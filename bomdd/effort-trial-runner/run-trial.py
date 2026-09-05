#!/usr/bin/env python3
"""effort trial 実行器(ET-002 以降・ET-001 rubric/run-trial.py の一般化)。

測定器 method/tools/effort-calibration.py の**記録を作る側**。判定はしない。treatment は plan ファイルで与え、
trial 定義(input/rubric/語彙/反復/盲検)とは分離する(trial/treatment 分離 — ECO-058)。

コマンド:
  init     <trial_dir> --input TASK.md --rubric rubric.md --vocab a,b,c --repetitions N [--title ...]
           trial.yaml を封印(input_hash / rubric_hash / trial_hash)。既存 trial.yaml があれば拒否。
  dry-run  <trial_dir> --plan plan.yaml [--scratch DIR]
           prompt と codex コマンドを組み立てて表示するだけ(codex を呼ばない)。
  probe    --plan plan.yaml [--scratch DIR]
           各腕を 1 行プロンプトで 1 回ずつ呼び、応答と usage を確認(到達モデルは確認できない)。
  execute  <trial_dir> --plan plan.yaml --scratch DIR
           全腕 × 反復を並列実行 → runs/<run>.execution.yaml + outputs/。execution receipt が既にあれば拒否。
  evaluate <trial_dir> --evaluator SCRIPT
           outputs/<run>.RESULT.md を SCRIPT に渡し(引数は出力ファイルだけ — treatment を渡す経路なし)、
           JSON {result, observed_failures, ...} を evaluation receipt へ。
  recover-outputs <trial_dir>
           RESULT.md が空の run を events.jsonl の最終 agent_message から復元(evaluation receipt が 1 件でもあれば拒否)。
  --selftest
           codex を呼ばずに init → 合成 execution → evaluate → effort-calibration validate まで通す陽性対照。

plan.yaml:
  arms:
    - {tag: LN, model: gpt-5.6-luna, effort: none,   converge: false}
    - {tag: LM, model: gpt-5.6-luna, effort: medium, converge: false}
    - {tag: LH, model: gpt-5.6-luna, effort: high,   converge: false}
    - {tag: SM, model: gpt-5.6-sol,  effort: medium, converge: false}
  harness: {name: codex-cli, version: "0.144.1"}     # 実行時に `codex --version` と突合(不一致は停止)
  sandbox: read-only

ET-001 からの是正(実測): `-o` は cwd 基準で解決される → 絶対パス / Windows は `codex.cmd` → shutil.which /
書き込みは newline="\\n" 明示(hash 結合された記録の byte 規律・playbook §13)/ RESULT.md 空は events から復元。

限界: 到達モデル・到達 effort は観測不能(resolved= unknown 固定)。execution receipt のアンカーは未結線
(本実行器を人が起動する散文契約)。effort 序数に none / max が無い間、Luna none を含む対は
effort-calibration の投影で `unordered-effort` になる(序数の追加は method/tools の変更= ECO 起票)。
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, shutil, subprocess, sys, tempfile, threading
from pathlib import Path
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.stdout.reconfigure(encoding="utf-8")
EC: dict = {}
exec((ROOT / "method" / "tools" / "effort-calibration.py").read_text(encoding="utf-8")
     .split("# ---------------------------------------------------------------- validate")[0], EC)
canonical_hash, file_hash, treatment_hash, trial_hash_fn = (EC["canonical_hash"], EC["file_hash"],
                                                             EC["treatment_hash"], EC["trial_hash"])
CONVERGE_SRC = ROOT / "method" / "templates" / "product-profile" / "skills" / "converge.md"


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_text(p: Path, s: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)


def dump_yaml(p: Path, obj) -> None:
    write_text(p, yaml.safe_dump(obj, allow_unicode=True, sort_keys=False, width=120))


def load_yaml(p: Path):
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def codex_bin() -> str:
    b = shutil.which("codex") or shutil.which("codex.cmd")
    if not b:
        raise SystemExit("codex CLI が PATH に無い(実行不能は結果ではない)")
    return b


def codex_version() -> str:
    out = subprocess.run([codex_bin(), "--version"], capture_output=True, text=True, encoding="utf-8")
    return out.stdout.strip().split()[-1] if out.stdout.strip() else "unknown"


def last_agent_message(events: Path) -> str:
    msgs = []
    if not events.is_file():
        return ""
    for line in events.read_text(encoding="utf-8").splitlines():
        try:
            j = json.loads(line)
        except json.JSONDecodeError:
            continue
        if j.get("type") == "item.completed" and (j.get("item") or {}).get("type") == "agent_message":
            msgs.append(j["item"].get("text", ""))
    return msgs[-1] if msgs else ""


def usage_from_events(events: Path) -> dict:
    usage = {"input": 0, "output": 0}
    if not events.is_file():
        return usage
    for line in events.read_text(encoding="utf-8").splitlines():
        try:
            j = json.loads(line)
        except json.JSONDecodeError:
            continue
        if j.get("type") == "turn.completed" and "usage" in j:
            u = j["usage"]
            usage = {"input": int(u.get("input_tokens", 0)), "output": int(u.get("output_tokens", 0)),
                     "reasoning_output": int(u.get("reasoning_output_tokens", 0)),
                     "cached_input": int(u.get("cached_input_tokens", 0))}
    return usage


# ---------------------------------------------------------------- plan / treatment
def load_plan(p: Path) -> dict:
    plan = load_yaml(p)
    arms = plan.get("arms") or []
    if not arms:
        raise SystemExit("plan に arms が無い")
    tags = [a["tag"] for a in arms]
    if len(set(tags)) != len(tags):
        raise SystemExit(f"plan の tag が重複: {tags}")
    for a in arms:
        for k in ("tag", "model", "effort"):
            if k not in a:
                raise SystemExit(f"arm に {k} が無い: {a}")
    plan.setdefault("harness", {"name": "codex-cli", "version": "unknown"})
    plan.setdefault("sandbox", "read-only")
    return plan


def requested(arm: dict, plan: dict, harness_version: str) -> dict:
    stack = ([{"name": "converge.md(method/templates/product-profile/skills)", "hash": file_hash(CONVERGE_SRC)}]
             if arm.get("converge") else [])
    return {"model": arm["model"], "effort": arm["effort"], "method_stack": stack,
            "harness": {"name": plan["harness"]["name"], "hash": harness_version},
            "tool_permissions": [f"sandbox:{plan['sandbox']}"],
            "runtime_config": {"prompt_via": "stdin", "output": "-o <abs>/RESULT.md",
                               "flags": "--json --skip-git-repo-check"}}


def build_prompt(trial_dir: Path, trial: dict, arm: dict) -> str:
    prompt = (trial_dir / trial["input_file"]).read_text(encoding="utf-8")
    if arm.get("converge"):
        add = trial_dir / "input" / "converge-addendum.md"
        if not add.is_file():
            raise SystemExit(f"converge 腕には {add} が要る(ET-001 の様式)")
        prompt = add.read_text(encoding="utf-8") + "\n\n---\n\n" + prompt
    return prompt


def codex_cmd(arm: dict, plan: dict, run_dir: Path) -> list[str]:
    return [codex_bin(), "exec", "-m", arm["model"], "-s", plan["sandbox"], "--skip-git-repo-check",
            "-C", str(run_dir), "--json", "-c", f"model_reasoning_effort={arm['effort']}",
            "-o", str(run_dir / "RESULT.md"), "-"]


# ---------------------------------------------------------------- init(封印)
def cmd_init(a) -> int:
    td = Path(a.trial_dir).resolve()
    tf = td / "trial.yaml"
    if tf.exists():
        raise SystemExit(f"{tf} が既にある(封印済み定義は書き換えない)")
    inp, rub = td / a.input, td / a.rubric
    for p in (inp, rub):
        if not p.is_file():
            raise SystemExit(f"無い: {p}")
    vocab = [v.strip() for v in a.vocab.split(",") if v.strip()]
    if not vocab:
        raise SystemExit("--vocab が空")
    t = {"trial_id": td.name, "input_hash": file_hash(inp), "rubric_hash": file_hash(rub),
         "symptom_vocabulary": vocab, "repetitions": int(a.repetitions),
         "evaluator_policy": {"blind": True, "evaluator": a.evaluator_note, "sealed_at": now()}}
    t["trial_hash"] = trial_hash_fn(t)
    t.update({"title": a.title or "", "input_file": a.input, "rubric_file": a.rubric,
              "notes": "treatment は execution receipt に記録する(trial 定義は treatment を含まない)"})
    dump_yaml(tf, t)
    print(f"[sealed] {tf} trial_hash={t['trial_hash'][:12]} input={t['input_hash'][:12]} rubric={t['rubric_hash'][:12]}")
    return 0


# ---------------------------------------------------------------- dry-run / probe
def cmd_dry_run(a) -> int:
    td = Path(a.trial_dir).resolve(); trial = load_yaml(td / "trial.yaml"); plan = load_plan(Path(a.plan))
    scratch = Path(a.scratch) if a.scratch else Path(tempfile.gettempdir()) / "effort-trial-dry"
    for arm in plan["arms"]:
        for i in range(1, int(trial["repetitions"]) + 1):
            rid = f"{td.name}-{arm['tag']}-{i:02d}"
            d = scratch / rid
            prompt = build_prompt(td, trial, arm)
            req = requested(arm, plan, plan["harness"].get("version", "unknown"))
            print(f"{rid}: treatment_hash={treatment_hash(req)[:12]} prompt={len(prompt)}B")
            print("  " + " ".join(codex_cmd(arm, plan, d)))
    return 0


def cmd_probe(a) -> int:
    plan = load_plan(Path(a.plan))
    scratch = Path(a.scratch) if a.scratch else Path(tempfile.mkdtemp(prefix="effort-probe-"))
    ver = codex_version()
    print(f"codex version: {ver} (plan: {plan['harness'].get('version')})")
    for arm in plan["arms"]:
        d = scratch / f"probe-{arm['tag']}"; d.mkdir(parents=True, exist_ok=True)
        with open(d / "events.jsonl", "w", encoding="utf-8") as ev, open(d / "stderr.txt", "w", encoding="utf-8") as er:
            p = subprocess.run(codex_cmd(arm, plan, d), input="Reply with exactly: OK", text=True,
                               encoding="utf-8", stdout=ev, stderr=er, timeout=300)
        msg = last_agent_message(d / "events.jsonl")
        err = ""
        if p.returncode != 0:
            errs = [l.split("ERROR", 1)[1].strip()[:110] for l in (d / "stderr.txt").read_text(encoding="utf-8").splitlines()
                    if "ERROR" in l and "system skills" not in l]
            err = f" error={errs[0]!r}" if errs else " error=(stderr に ERROR なし)"
            err += " — 実行不能は結果ではない(UNKNOWN)"
        print(f"{arm['tag']} {arm['model']}/{arm['effort']}: exit={p.returncode} reply={msg.strip()[:20]!r} usage={usage_from_events(d / 'events.jsonl')}{err}")
    return 0


# ---------------------------------------------------------------- execute
def one_run(rid: str, arm: dict, plan: dict, td: Path, trial: dict, scratch: Path, ver: str, results: dict,
            package: Path | None = None):
    d = scratch / rid; d.mkdir(parents=True, exist_ok=True)
    if package is not None:  # 許可ファイル集合(履歴なし)を run dir へ複製 — 課題文は同ディレクトリのファイルだけを読む契約
        shutil.copytree(package, d, dirs_exist_ok=True)
    prompt = build_prompt(td, trial, arm)
    write_text(d / "PROMPT.md", prompt)
    started = now()
    with open(d / "events.jsonl", "w", encoding="utf-8") as ev, open(d / "stderr.txt", "w", encoding="utf-8") as er:
        p = subprocess.run(codex_cmd(arm, plan, d), input=prompt, text=True, encoding="utf-8",
                           stdout=ev, stderr=er, timeout=3600)
    completed = now()
    res = d / "RESULT.md"
    out_text = res.read_text(encoding="utf-8") if res.is_file() else ""
    recovered = False
    if not out_text:
        out_text = last_agent_message(d / "events.jsonl"); recovered = bool(out_text)
    out_dir = td / "outputs"
    write_text(out_dir / f"{rid}.RESULT.md", out_text)
    shutil.copyfile(d / "events.jsonl", out_dir / f"{rid}.events.jsonl")
    req = requested(arm, plan, ver)
    rec = {"run_id": rid, "trial_id": trial["trial_id"], "trial_hash": trial["trial_hash"],
           "treatment": {"requested": req, "resolved": {"model": "unknown", "effort": "unknown"}},
           "treatment_hash": treatment_hash(req), "started_at": started, "completed_at": completed,
           "exit_code": p.returncode, "token_usage": usage_from_events(d / "events.jsonl"),
           "output_hash": hashlib.sha256(out_text.encode("utf-8")).hexdigest(),
           "output_file": f"outputs/{rid}.RESULT.md",
           "prompt_hash": hashlib.sha256(prompt.encode("utf-8")).hexdigest()}
    if recovered:
        rec["output_recovered_from"] = f"outputs/{rid}.events.jsonl (item.completed/agent_message 最終)"
    dump_yaml(td / "runs" / f"{rid}.execution.yaml", rec)
    results[rid] = {"exit": p.returncode, "tokens": rec["token_usage"], "out_bytes": len(out_text)}
    print(f"[done] {rid} exit={p.returncode} tokens={rec['token_usage']} out={len(out_text)}B", flush=True)


def cmd_execute(a) -> int:
    td = Path(a.trial_dir).resolve(); trial = load_yaml(td / "trial.yaml"); plan = load_plan(Path(a.plan))
    if trial["input_hash"] != file_hash(td / trial["input_file"]):
        raise SystemExit("input が trial 定義と不一致(封印後の改変)")
    if trial["rubric_hash"] != file_hash(td / trial["rubric_file"]):
        raise SystemExit("rubric が trial 定義と不一致(封印後の改変)")
    if any((td / "runs").glob("*.execution.yaml")):
        raise SystemExit("runs/ に既存の execution receipt がある(追記のみ — 上書きしない)")
    ver = codex_version()
    want = str(plan["harness"].get("version", "unknown"))
    if want != "unknown" and ver != want:
        raise SystemExit(f"codex version 不一致: 実測 {ver} / plan {want}(plan を更新してから実行)")
    scratch = Path(a.scratch).resolve()
    package = Path(a.package).resolve() if getattr(a, "package", None) else None
    if package is not None and not package.is_dir():
        raise SystemExit(f"package が無い: {package}")
    threads, results = [], {}
    for arm in plan["arms"]:
        for i in range(1, int(trial["repetitions"]) + 1):
            rid = f"{td.name}-{arm['tag']}-{i:02d}"
            t = threading.Thread(target=one_run, args=(rid, arm, plan, td, trial, scratch, ver, results, package))
            t.start(); threads.append(t)
    for t in threads:
        t.join()
    print(json.dumps(results, ensure_ascii=False, indent=1))
    return 0


# ---------------------------------------------------------------- evaluate / recover
def cmd_evaluate(a) -> int:
    td = Path(a.trial_dir).resolve(); trial = load_yaml(td / "trial.yaml")
    evaluator = Path(a.evaluator).resolve()
    spec_hash = file_hash(evaluator)
    runs = td / "runs"
    n = 0
    for ef in sorted(runs.glob("*.execution.yaml")):
        rid = ef.name[: -len(".execution.yaml")]
        vf = runs / f"{rid}.evaluation.yaml"
        if vf.is_file():
            print(f"[skip] {rid}: evaluation exists"); continue
        out = subprocess.run([sys.executable, str(evaluator), str(td / "outputs" / f"{rid}.RESULT.md")],
                             capture_output=True, text=True, encoding="utf-8")
        if out.returncode != 0:
            raise SystemExit(f"{rid}: evaluator failed: {out.stderr}")
        j = json.loads(out.stdout)
        if j.get("result") not in ("pass", "fail"):
            raise SystemExit(f"{rid}: evaluator の result が pass|fail でない: {j.get('result')}")
        rec = {"run_id": rid, "execution_receipt_hash": file_hash(ef),
               "evaluator": {"id": f"oracle-script:{evaluator.relative_to(ROOT) if evaluator.is_relative_to(ROOT) else evaluator.name}",
                             "spec_hash": spec_hash},
               "rubric_hash": trial["rubric_hash"], "rubric_sealed_before_run": True,
               "result": j["result"], "observed_failures": list(j.get("observed_failures") or []),
               "evaluated_at": now()}
        for k in ("correct", "expected", "details"):
            if k in j:
                rec[f"evaluator_{k}"] = j[k]
        dump_yaml(vf, rec); n += 1
        print(f"[eval] {rid}: {j['result']} {j.get('correct', '?')}/{j.get('expected', '?')} {rec['observed_failures']}")
    print(f"evaluated {n}")
    return 0


def cmd_recover(a) -> int:
    td = Path(a.trial_dir).resolve()
    if any((td / "runs").glob("*.evaluation.yaml")):
        raise SystemExit("評価済み — execution receipt は改変しない")
    for ef in sorted((td / "runs").glob("*.execution.yaml")):
        rec = load_yaml(ef); rid = rec["run_id"]
        cur = td / "outputs" / f"{rid}.RESULT.md"
        if cur.is_file() and cur.stat().st_size > 0:
            continue
        text = last_agent_message(td / "outputs" / f"{rid}.events.jsonl")
        write_text(cur, text)
        rec["output_hash"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
        rec["output_recovered_from"] = f"outputs/{rid}.events.jsonl (item.completed/agent_message 最終) — 評価前の復元"
        dump_yaml(ef, rec)
        print(f"[recovered] {rid} {len(text)}B")
    return 0


# ---------------------------------------------------------------- selftest(codex を呼ばない陽性対照)
def selftest() -> int:
    bad = []
    base = Path(tempfile.mkdtemp(prefix="effort-runner-st-"))
    try:
        td = base / "root" / "ST-001"; (td / "input").mkdir(parents=True); (td / "rubric").mkdir()
        write_text(td / "input" / "TASK.md", "Q: 1+1?\n")
        write_text(td / "rubric" / "rubric.md", "expected: 2\n")
        ev = td / "rubric" / "evaluate.py"
        write_text(ev, "import json,sys\nt=open(sys.argv[1],encoding='utf-8').read()\n"
                       "ok='2' in t\nprint(json.dumps({'result':'pass' if ok else 'fail',"
                       "'observed_failures':[] if ok else ['wrong-answer'],'correct':int(ok),'expected':1}))\n")
        plan = base / "plan.yaml"
        dump_yaml(plan, {"arms": [{"tag": "LN", "model": "m-cheap", "effort": "none"},
                                  {"tag": "LH", "model": "m-cheap", "effort": "high"},
                                  {"tag": "SM", "model": "m-big", "effort": "medium"}],
                         "harness": {"name": "codex-cli", "version": "unknown"}, "sandbox": "read-only"})
        rc = main(["init", str(td), "--input", "input/TASK.md", "--rubric", "rubric/rubric.md",
                   "--vocab", "wrong-answer,missing", "--repetitions", "2"])
        if rc != 0 or not (td / "trial.yaml").is_file():
            bad.append("init が trial.yaml を作らない")
        try:
            main(["init", str(td), "--input", "input/TASK.md", "--rubric", "rubric/rubric.md",
                  "--vocab", "x", "--repetitions", "1"]); bad.append("init が封印済み trial.yaml を上書きした")
        except SystemExit as e:
            if "書き換えない" not in str(e):
                bad.append(f"init の拒否理由が違う: {e}")
        # dry-run は codex 不要
        if main(["dry-run", str(td), "--plan", str(plan)]) != 0:
            bad.append("dry-run が失敗")
        # 合成 execution(codex を呼ばずに receipt だけ作る)— LN fail / LH pass / SM pass
        trial = load_yaml(td / "trial.yaml"); p = load_plan(plan)
        answers = {"LN": "3", "LH": "2", "SM": "2"}
        for arm in p["arms"]:
            for i in (1, 2):
                rid = f"ST-001-{arm['tag']}-{i:02d}"
                text = f"A: {answers[arm['tag']]}\n"
                write_text(td / "outputs" / f"{rid}.RESULT.md", text)
                req = requested(arm, p, "unknown")
                dump_yaml(td / "runs" / f"{rid}.execution.yaml", {
                    "run_id": rid, "trial_id": "ST-001", "trial_hash": trial["trial_hash"],
                    "treatment": {"requested": req, "resolved": {"model": "unknown", "effort": "unknown"}},
                    "treatment_hash": treatment_hash(req), "started_at": now(), "completed_at": now(),
                    "token_usage": {"input": 10, "output": 2},
                    "output_hash": hashlib.sha256(text.encode("utf-8")).hexdigest()})
        if main(["evaluate", str(td), "--evaluator", str(ev)]) != 0:
            bad.append("evaluate が失敗")
        pr = EC_validate(td.parent)
        if pr:
            bad.append(f"effort-calibration validate が落ちた: {pr[:2]}")
        vals = {load_yaml(f)["run_id"]: load_yaml(f)["result"] for f in (td / "runs").glob("*.evaluation.yaml")}
        if not (vals.get("ST-001-LN-01") == "fail" and vals.get("ST-001-LH-01") == "pass" and vals.get("ST-001-SM-01") == "pass"):
            bad.append(f"評価結果が想定と違う: {vals}")
        # evaluation 後の recover は拒否される
        try:
            main(["recover-outputs", str(td)]); bad.append("評価後の recover-outputs を通した")
        except SystemExit as e:
            if "改変しない" not in str(e):
                bad.append(f"recover-outputs の拒否理由が違う: {e}")
        # execute は既存 receipt があれば拒否(codex を呼ぶ前に止まる)
        try:
            main(["execute", str(td), "--plan", str(plan), "--scratch", str(base / "s")]); bad.append("既存 receipt があるのに execute が進んだ")
        except SystemExit as e:
            if "上書きしない" not in str(e):
                bad.append(f"execute の拒否理由が違う: {e}")
    finally:
        shutil.rmtree(base, ignore_errors=True)
    for b in bad:
        print(f"[FAIL] {b}")
    print("selftest:", "PASS" if not bad else f"FAIL {len(bad)}")
    return 0 if not bad else 1


def EC_validate(root: Path) -> list:
    ns: dict = {}
    exec((ROOT / "method" / "tools" / "effort-calibration.py").read_text(encoding="utf-8")
         .split("# ---------------------------------------------------------------- project")[0], ns)
    return ns["validate"](root)


# ---------------------------------------------------------------- main
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("init"); s.add_argument("trial_dir"); s.add_argument("--input", required=True)
    s.add_argument("--rubric", required=True); s.add_argument("--vocab", required=True)
    s.add_argument("--repetitions", required=True); s.add_argument("--title", default="")
    s.add_argument("--evaluator-note", default="oracle-script — treatment を受け取る引数を持たない")
    s = sub.add_parser("dry-run"); s.add_argument("trial_dir"); s.add_argument("--plan", required=True); s.add_argument("--scratch")
    s = sub.add_parser("probe"); s.add_argument("--plan", required=True); s.add_argument("--scratch")
    s = sub.add_parser("execute"); s.add_argument("trial_dir"); s.add_argument("--plan", required=True); s.add_argument("--scratch", required=True)
    s.add_argument("--package", help="run dir へ複製する許可ファイル集合(履歴なし)のディレクトリ")
    s = sub.add_parser("evaluate"); s.add_argument("trial_dir"); s.add_argument("--evaluator", required=True)
    s = sub.add_parser("recover-outputs"); s.add_argument("trial_dir")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    return {"init": cmd_init, "dry-run": cmd_dry_run, "probe": cmd_probe, "execute": cmd_execute,
            "evaluate": cmd_evaluate, "recover-outputs": cmd_recover}.get(a.cmd, lambda _: (ap.print_help(), 2)[1])(a)


if __name__ == "__main__":
    sys.exit(main())
