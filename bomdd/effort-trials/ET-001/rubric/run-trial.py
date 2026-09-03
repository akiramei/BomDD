#!/usr/bin/env python3
"""ET-001 実行器 — codex exec を treatment ごとに起動し execution receipt を書く(評価はしない)。

  python run-trial.py execute  <scratch_root>   # 8 run を並列実行 → runs/*.execution.yaml + outputs/
  python run-trial.py evaluate                  # outputs/ を evaluate.py で採点 → runs/*.evaluation.yaml

execution と evaluation は別コマンド(実行完了と評価完了は別イベント — ECO-058 §1)。
evaluate は evaluate.py に出力ファイルだけを渡す(treatment を渡す経路が無い)。
"""
from __future__ import annotations
import datetime as dt, hashlib, json, os, shutil, subprocess, sys, threading
from pathlib import Path
import yaml

HERE = Path(__file__).resolve().parent
TRIAL = HERE.parent
ROOT = TRIAL.parents[2]
sys.path.insert(0, str(ROOT / "method" / "tools"))
sys.stdout.reconfigure(encoding="utf-8")
EC = {}
exec((ROOT / "method" / "tools" / "effort-calibration.py").read_text(encoding="utf-8")
     .split("# ---------------------------------------------------------------- validate")[0], EC)
canonical_hash, file_hash, treatment_hash = EC["canonical_hash"], EC["file_hash"], EC["treatment_hash"]

TRIAL_ID = "ET-001"
TASK = TRIAL / "input" / "TASK.md"
ADDENDUM = TRIAL / "input" / "converge-addendum.md"
CONVERGE_SRC = ROOT / "method" / "templates" / "product-profile" / "skills" / "converge.md"
RUNS = TRIAL / "runs"
OUT = TRIAL / "outputs"
REPS = 2
TREATMENTS = [("M", "medium", False), ("H", "high", False), ("MC", "medium", True), ("HC", "high", True)]


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def last_agent_message(events: Path) -> str:
    msgs = []
    for line in events.read_text(encoding="utf-8").splitlines():
        try:
            j = json.loads(line)
        except json.JSONDecodeError:
            continue
        if j.get("type") == "item.completed" and (j.get("item") or {}).get("type") == "agent_message":
            msgs.append(j["item"].get("text", ""))
    return msgs[-1] if msgs else ""


def recover_outputs():
    """初回実行の復元(1 回限り): outputs/*.events.jsonl の最終 agent_message を RESULT.md へ書き、
    execution receipt の output_hash を再計算する。evaluation receipt が 1 件でもあれば拒否(評価後の改変禁止)。"""
    if any(RUNS.glob("*.evaluation.yaml")):
        raise SystemExit("評価済み — execution receipt は改変しない")
    for ef in sorted(RUNS.glob("*.execution.yaml")):
        rec = yaml.safe_load(ef.read_text(encoding="utf-8"))
        rid = rec["run_id"]
        text = last_agent_message(OUT / f"{rid}.events.jsonl")
        (OUT / f"{rid}.RESULT.md").write_text(text, encoding="utf-8")
        rec["output_hash"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
        rec["output_recovered_from"] = f"outputs/{rid}.events.jsonl (item.completed/agent_message 最終) — 実行器欠陥の復元・評価前"
        ef.write_text(yaml.safe_dump(rec, allow_unicode=True, sort_keys=False), encoding="utf-8")
        print(f"[recovered] {rid} {len(text)}B {rec['output_hash'][:12]}")


def requested(effort: str, with_converge: bool) -> dict:
    stack = [{"name": "converge.md(method/templates/product-profile/skills)", "hash": file_hash(CONVERGE_SRC)}] \
        if with_converge else []
    return {"model": "gpt-5.6-sol", "effort": effort, "method_stack": stack,
            "harness": {"name": "codex-cli", "hash": "0.144.1"},
            "tool_permissions": ["sandbox:read-only"],
            "runtime_config": {"service_tier": "default", "prompt_via": "stdin", "output": "-o RESULT.md",
                               "flags": "--json --skip-git-repo-check"}}


def one_run(run_id: str, effort: str, with_converge: bool, scratch: Path, trial: dict, results: dict):
    d = scratch / run_id; d.mkdir(parents=True, exist_ok=True)
    prompt = TASK.read_text(encoding="utf-8")
    if with_converge:
        prompt = ADDENDUM.read_text(encoding="utf-8") + "\n\n---\n\n" + prompt
    (d / "PROMPT.md").write_text(prompt, encoding="utf-8")
    codex = shutil.which("codex") or shutil.which("codex.cmd")
    if not codex:
        raise SystemExit("codex CLI が PATH に無い(実行不能は結果ではない)")
    cmd = [codex, "exec", "-s", "read-only", "--skip-git-repo-check", "-C", str(d), "--json",
           "-c", f"model_reasoning_effort={effort}", "-o", str(d / "RESULT.md"), "-"]
    # 初回実行の実行器欠陥(自己捕捉・評価前): `-o RESULT.md` は -C ではなく本プロセスの cwd 基準で解決され
    # 8 run が同一ファイルを上書き → RESULT.md が全 run で空。最終メッセージは events.jsonl の
    # item.completed(agent_message)にも残るため、そこから復元して output_hash を再計算した(receipt は
    # 未評価・未コミットの段階で再導出)。以後は絶対パスで渡し、events からの抽出を正本の照合に使う。
    started = now()
    with open(d / "events.jsonl", "w", encoding="utf-8") as ev, open(d / "stderr.txt", "w", encoding="utf-8") as er:
        p = subprocess.run(cmd, input=prompt, text=True, encoding="utf-8", stdout=ev, stderr=er, timeout=1800)
    completed = now()
    usage = {"input": 0, "output": 0}
    for line in (d / "events.jsonl").read_text(encoding="utf-8").splitlines():
        try:
            j = json.loads(line)
        except json.JSONDecodeError:
            continue
        if j.get("type") == "turn.completed" and "usage" in j:
            u = j["usage"]; usage = {"input": int(u.get("input_tokens", 0)), "output": int(u.get("output_tokens", 0)),
                                     "reasoning_output": int(u.get("reasoning_output_tokens", 0)),
                                     "cached_input": int(u.get("cached_input_tokens", 0))}
    res = d / "RESULT.md"
    out_text = res.read_text(encoding="utf-8") if res.is_file() else ""
    if not out_text:
        out_text = last_agent_message(d / "events.jsonl")
    OUT.mkdir(exist_ok=True)
    (OUT / f"{run_id}.RESULT.md").write_text(out_text, encoding="utf-8")
    (OUT / f"{run_id}.events.jsonl").write_bytes((d / "events.jsonl").read_bytes())
    req = requested(effort, with_converge)
    rec = {"run_id": run_id, "trial_id": TRIAL_ID, "trial_hash": trial["trial_hash"],
           "treatment": {"requested": req, "resolved": {"model": "unknown", "effort": "unknown"}},
           "treatment_hash": treatment_hash(req), "started_at": started, "completed_at": completed,
           "exit_code": p.returncode, "token_usage": usage,
           "output_hash": hashlib.sha256(out_text.encode("utf-8")).hexdigest(),
           "output_file": f"outputs/{run_id}.RESULT.md", "prompt_hash": hashlib.sha256(prompt.encode("utf-8")).hexdigest()}
    RUNS.mkdir(exist_ok=True)
    (RUNS / f"{run_id}.execution.yaml").write_text(yaml.safe_dump(rec, allow_unicode=True, sort_keys=False), encoding="utf-8")
    results[run_id] = (p.returncode, usage, len(out_text))
    print(f"[done] {run_id} exit={p.returncode} tokens={usage} out={len(out_text)}B", flush=True)


def execute(scratch: Path):
    trial = yaml.safe_load((TRIAL / "trial.yaml").read_text(encoding="utf-8"))
    assert trial["input_hash"] == file_hash(TASK), "TASK.md が trial 定義と不一致(封印後の改変)"
    assert trial["rubric_hash"] == file_hash(HERE / "rubric.md"), "rubric.md が trial 定義と不一致"
    if any(RUNS.glob("*.execution.yaml")):
        raise SystemExit("runs/ に既存の execution receipt がある(追記のみ — 上書きしない)")
    threads, results = [], {}
    for tag, effort, wc in TREATMENTS:
        for i in range(1, trial["repetitions"] + 1):
            rid = f"{TRIAL_ID}-{tag}-{i:02d}"
            t = threading.Thread(target=one_run, args=(rid, effort, wc, scratch, trial, results)); t.start(); threads.append(t)
    for t in threads:
        t.join()
    print(json.dumps(results, ensure_ascii=False, indent=1))


def evaluate():
    trial = yaml.safe_load((TRIAL / "trial.yaml").read_text(encoding="utf-8"))
    spec_hash = file_hash(HERE / "evaluate.py")
    for ef in sorted(RUNS.glob("*.execution.yaml")):
        run_id = ef.name[: -len(".execution.yaml")]
        vf = RUNS / f"{run_id}.evaluation.yaml"
        if vf.is_file():
            print(f"[skip] {run_id}: evaluation exists"); continue
        out = subprocess.run([sys.executable, str(HERE / "evaluate.py"), str(OUT / f"{run_id}.RESULT.md")],
                             capture_output=True, text=True, encoding="utf-8")
        if out.returncode != 0:
            raise SystemExit(f"{run_id}: evaluator failed: {out.stderr}")
        j = json.loads(out.stdout)
        rec = {"run_id": run_id, "execution_receipt_hash": file_hash(ef),
               "evaluator": {"id": "oracle-script:ET-001/rubric/evaluate.py", "spec_hash": spec_hash},
               "rubric_hash": trial["rubric_hash"], "rubric_sealed_before_run": True,
               "result": j["result"], "observed_failures": j["observed_failures"],
               "correct_count": f"{j['correct']}/{j['expected']}", "evaluated_at": now(), "details": j["details"]}
        vf.write_text(yaml.safe_dump(rec, allow_unicode=True, sort_keys=False), encoding="utf-8")
        print(f"[eval] {run_id}: {j['result']} {j['correct']}/{j['expected']} {j['observed_failures']}")


if __name__ == "__main__":
    if sys.argv[1:2] == ["execute"]:
        execute(Path(sys.argv[2]))
    elif sys.argv[1:2] == ["evaluate"]:
        evaluate()
    elif sys.argv[1:2] == ["recover-outputs"]:
        recover_outputs()
    else:
        print(__doc__)
