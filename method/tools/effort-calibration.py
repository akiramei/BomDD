#!/usr/bin/env python3
"""effort-calibration — effort × 工程条件の較正記録(receipt)の検証と投影(ECO-058)。

目的: 「Effort レベルが不足/過剰である可能性」を**症状→仮説→介入→帰結→分類**の順で測るための
測定器。判定器ではない — 本ツールは観測記録の構造検証と、記録からの**導出投影**(read-only)だけを行う。

正本(immutable): trial 定義 / execution receipt / evaluation receipt(いずれも書き換えず追記のみ)。
導出物(再生成可能・正本ではない): 集計率・effort 感度の分類・capability projection(来歴つき)。

記録の置場(既定 root= bomdd/effort-trials/):
  <root>/<trial_id>/trial.yaml
  <root>/<trial_id>/runs/<run_id>.execution.yaml
  <root>/<trial_id>/runs/<run_id>.evaluation.yaml

スキーマ(必須キー):
  trial.yaml:
    trial_id, input_hash, rubric_hash, symptom_vocabulary[list], repetitions[int>0],
    evaluator_policy: {blind: true}, trial_hash(= 上記 5 項の canonical JSON の sha256)
  execution receipt:
    run_id, trial_id, trial_hash, treatment: {requested: {model, effort, method_stack[{name,hash}],
    harness{name,hash}, tool_permissions, runtime_config}, resolved: {model, effort}(観測不能なら
    "unknown")}, treatment_hash(= requested の canonical JSON の sha256), started_at, completed_at,
    token_usage{input,output}, output_hash
    禁止キー(観測でなく評価・解釈): result, observed_failures, candidate_reason, response_class
  evaluation receipt:
    run_id, execution_receipt_hash(= execution receipt ファイル bytes の sha256), evaluator{id,spec_hash},
    rubric_hash(= trial と一致), rubric_sealed_before_run: true, result: pass|fail,
    observed_failures[list ⊆ trial.symptom_vocabulary]
    禁止キー(盲検の破れ・解釈の混入): treatment, effort, model, candidate_reason, response_class

コマンド:
  validate [root]        記録の構造・ハッシュ整合・禁止キー・語彙を検査(fail-closed・exit 1)
  project  [root]        trial × treatment の n / pass 率 / コスト、effort 感度の導出分類、来歴を出力
  hash-treatment <yaml>  treatment_spec(requested)の treatment_hash を計算
  --selftest             陽性対照(known-good 1・known-bad 8)を合成して実測

検出力の限界(宣言 — 実施した検査が測っていない次元):
  (1) execution receipt のアンカー「model invocation completed」は現ハーネスで**未結線** — 当面は手動記帳
      であり「必ず起きる」ではなく散文契約(被覆不能な境界として明示。hook で結線できた時点で解消)。
  (2) resolved model / effort は観測不能(要求値のみ観測可)— treatment_hash は requested で計算し、
      resolved は unknown を許容して別欄に記録する。同一 treatment_hash の反復が実は別モデルだった
      場合を本ツールは検出できない。
  (3) 評価者の盲検は**構造**(evaluation receipt が treatment 欄を持たない)でしか担保しない — 評価者が
      別経路で treatment を知った場合は検出できない。
  (4) 導出分類「effort-sensitive: supported」は**仮説の支持**であって原因の証明ではない。policy の自動化
      (E→High 規則の焼き込み)は行わない。
  (5) 反復数は trial 定義で凍結し、不足時は率を出さず insufficient-n とする(任意停止の防止)。
  (6) 記録の immutability は単一実行では検査できない(git 履歴での改変検出は本ツールの外)。
"""
from __future__ import annotations
import argparse, hashlib, json, sys, tempfile, shutil
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML が必要です: pip install pyyaml")

DEFAULT_ROOT = Path("bomdd") / "effort-trials"
TRIAL_HASH_KEYS = ("input_hash", "rubric_hash", "symptom_vocabulary", "repetitions", "evaluator_policy")
EXEC_REQUIRED = ("run_id", "trial_id", "trial_hash", "treatment", "treatment_hash",
                 "started_at", "completed_at", "token_usage", "output_hash")
EXEC_FORBIDDEN = ("result", "observed_failures", "candidate_reason", "response_class")
EVAL_REQUIRED = ("run_id", "execution_receipt_hash", "evaluator", "rubric_hash",
                 "rubric_sealed_before_run", "result", "observed_failures")
EVAL_FORBIDDEN = ("treatment", "effort", "model", "candidate_reason", "response_class")
REQ_KEYS = ("model", "effort", "method_stack", "harness", "tool_permissions", "runtime_config")
# effort の序数(文字列比較は "high" < "medium" となり低/高が反転する — selftest の known-good 腕が捕捉)。
# 序数外のラベルは順序を仮定せず分類しない(unordered-effort)。
EFFORT_ORDER = {"low": 0, "medium": 1, "high": 2, "xhigh": 3}


def canonical_hash(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def file_hash(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def trial_hash(trial: dict) -> str:
    return canonical_hash({k: trial.get(k) for k in TRIAL_HASH_KEYS})


def treatment_hash(requested: dict) -> str:
    return canonical_hash({k: requested.get(k) for k in REQ_KEYS})


def load_yaml(p: Path):
    return yaml.safe_load(p.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- validate
def validate(root: Path) -> list[str]:
    """fail-closed: 問題を列挙して返す(空= 適合)。対象 0 件も問題(測定不能は合格ではない)。"""
    problems: list[str] = []
    if not root.is_dir():
        return [f"root が無い: {root}"]
    trials = sorted(p for p in root.iterdir() if p.is_dir())
    if not trials:
        return [f"trial が 0 件: {root}(空集合は合格ではない)"]
    for td in trials:
        tf = td / "trial.yaml"
        if not tf.is_file():
            problems.append(f"{td.name}: trial.yaml が無い"); continue
        trial = load_yaml(tf)
        if not isinstance(trial, dict):
            problems.append(f"{td.name}: trial.yaml が mapping でない"); continue
        for k in ("trial_id",) + TRIAL_HASH_KEYS + ("trial_hash",):
            if k not in trial:
                problems.append(f"{td.name}: trial.yaml に {k} が無い")
        if problems and problems[-1].startswith(td.name):
            continue
        if trial["trial_id"] != td.name:
            problems.append(f"{td.name}: trial_id 不一致({trial['trial_id']})")
        if not isinstance(trial["repetitions"], int) or trial["repetitions"] <= 0:
            problems.append(f"{td.name}: repetitions は正の整数")
        if not (isinstance(trial.get("evaluator_policy"), dict) and trial["evaluator_policy"].get("blind") is True):
            problems.append(f"{td.name}: evaluator_policy.blind は true 必須")
        if trial["trial_hash"] != trial_hash(trial):
            problems.append(f"{td.name}: trial_hash が再計算と不一致(定義の改変)")
        vocab = set(trial.get("symptom_vocabulary") or [])
        runs = td / "runs"
        execs = sorted(runs.glob("*.execution.yaml")) if runs.is_dir() else []
        evals = sorted(runs.glob("*.evaluation.yaml")) if runs.is_dir() else []
        if not execs:
            problems.append(f"{td.name}: execution receipt が 0 件")
        exec_by_run: dict[str, Path] = {}
        for ef in execs:
            e = load_yaml(ef)
            tag = f"{td.name}/{ef.name}"
            if not isinstance(e, dict):
                problems.append(f"{tag}: mapping でない"); continue
            miss = [k for k in EXEC_REQUIRED if k not in e]
            if miss:
                problems.append(f"{tag}: 必須キー欠落 {miss}"); continue
            bad = [k for k in EXEC_FORBIDDEN if k in e]
            if bad:
                problems.append(f"{tag}: 観測記録に評価/解釈キー {bad}(execution receipt には書かない)")
            if e["trial_id"] != trial["trial_id"] or e["trial_hash"] != trial["trial_hash"]:
                problems.append(f"{tag}: trial_id/trial_hash が trial と不一致")
            tr = e.get("treatment") or {}
            req = (tr.get("requested") or {}) if isinstance(tr, dict) else {}
            if [k for k in REQ_KEYS if k not in req]:
                problems.append(f"{tag}: treatment.requested に欠落 {[k for k in REQ_KEYS if k not in req]}")
            elif e["treatment_hash"] != treatment_hash(req):
                problems.append(f"{tag}: treatment_hash が requested の再計算と不一致")
            res = tr.get("resolved") if isinstance(tr, dict) else None
            if not (isinstance(res, dict) and "model" in res and "effort" in res):
                problems.append(f"{tag}: treatment.resolved に model/effort が無い(観測不能なら unknown と書く)")
            if e["run_id"] != ef.name[: -len(".execution.yaml")]:
                problems.append(f"{tag}: run_id とファイル名が不一致")
            exec_by_run[e["run_id"]] = ef
        for vf in evals:
            v = load_yaml(vf)
            tag = f"{td.name}/{vf.name}"
            if not isinstance(v, dict):
                problems.append(f"{tag}: mapping でない"); continue
            miss = [k for k in EVAL_REQUIRED if k not in v]
            if miss:
                problems.append(f"{tag}: 必須キー欠落 {miss}"); continue
            bad = [k for k in EVAL_FORBIDDEN if k in v]
            if bad:
                problems.append(f"{tag}: 盲検/解釈違反キー {bad}(evaluation receipt には書かない)")
            ef = exec_by_run.get(v["run_id"])
            if ef is None:
                problems.append(f"{tag}: 対応する execution receipt が無い(run_id={v['run_id']})"); continue
            if v["execution_receipt_hash"] != file_hash(ef):
                problems.append(f"{tag}: execution_receipt_hash が実ファイルと不一致(座標同一性の破れ)")
            if v["rubric_hash"] != trial["rubric_hash"]:
                problems.append(f"{tag}: rubric_hash が trial と不一致")
            if v["rubric_sealed_before_run"] is not True:
                problems.append(f"{tag}: rubric_sealed_before_run は true 必須")
            if v["result"] not in ("pass", "fail"):
                problems.append(f"{tag}: result は pass|fail")
            extra = [s for s in (v.get("observed_failures") or []) if s not in vocab]
            if extra:
                problems.append(f"{tag}: symptom_vocabulary 外の症状 {extra}(語彙は trial で封印)")
            ev = v.get("evaluator") or {}
            if not (isinstance(ev, dict) and ev.get("id") and ev.get("spec_hash")):
                problems.append(f"{tag}: evaluator.id / spec_hash が無い(評価者も計器)")
    return problems


# ---------------------------------------------------------------- project(導出・read-only)
def project(root: Path) -> dict:
    """記録から集計と effort 感度の導出分類を作る。来歴(源 receipt のハッシュ・本ツールのハッシュ)を持つ。"""
    out = {"tool_hash": file_hash(Path(__file__)), "trials": {}, "sources": []}
    for td in sorted(p for p in root.iterdir() if p.is_dir()):
        trial = load_yaml(td / "trial.yaml")
        runs = td / "runs"
        groups: dict[str, dict] = {}
        for ef in sorted(runs.glob("*.execution.yaml")):
            e = load_yaml(ef)
            vf = runs / f"{e['run_id']}.evaluation.yaml"
            out["sources"].append({"file": str(ef.relative_to(root)), "sha256": file_hash(ef)})
            g = groups.setdefault(e["treatment_hash"], {
                "requested": e["treatment"]["requested"], "n": 0, "pass": 0, "unevaluated": 0,
                "tokens": 0})
            tu = e.get("token_usage") or {}
            g["tokens"] += int(tu.get("input", 0)) + int(tu.get("output", 0))
            if not vf.is_file():
                g["unevaluated"] += 1
                continue
            v = load_yaml(vf)
            out["sources"].append({"file": str(vf.relative_to(root)), "sha256": file_hash(vf)})
            g["n"] += 1
            g["pass"] += 1 if v["result"] == "pass" else 0
        rep = int(trial["repetitions"])
        tsum = {}
        for th, g in groups.items():
            tsum[th] = {
                "requested": g["requested"], "n": g["n"], "pass": g["pass"],
                "unevaluated": g["unevaluated"],
                "pass_rate": (round(g["pass"] / g["n"], 3) if g["n"] >= rep else "insufficient-n"),
                "mean_tokens": (round(g["tokens"] / max(1, g["n"] + g["unevaluated"]))),
            }
        # effort 感度: effort だけが異なる対(他の requested 要素が同一)で比較する
        sens = []
        ths = list(tsum)
        for i in range(len(ths)):
            for j in range(i + 1, len(ths)):
                a, b = tsum[ths[i]], tsum[ths[j]]
                ra, rb = dict(a["requested"]), dict(b["requested"])
                ea, eb = ra.pop("effort"), rb.pop("effort")
                if ra != rb or ea == eb:
                    continue
                if ea not in EFFORT_ORDER or eb not in EFFORT_ORDER:
                    sens.append({"low": ea, "high": eb, "low_rate": a["pass_rate"], "high_rate": b["pass_rate"],
                                 "effort_sensitive": "unordered-effort"})
                    continue
                lo, hi = (a, b) if EFFORT_ORDER[ea] < EFFORT_ORDER[eb] else (b, a)
                if lo["pass_rate"] == "insufficient-n" or hi["pass_rate"] == "insufficient-n":
                    verdict = "insufficient-n"
                elif hi["pass_rate"] > lo["pass_rate"]:
                    verdict = "supported"
                else:
                    verdict = "unsupported"
                sens.append({"low": lo["requested"]["effort"], "high": hi["requested"]["effort"],
                             "low_rate": lo["pass_rate"], "high_rate": hi["pass_rate"],
                             "effort_sensitive": verdict})
        out["trials"][trial["trial_id"]] = {"repetitions": rep, "treatments": tsum,
                                            "effort_sensitivity": sens}
    return out


# ---------------------------------------------------------------- selftest(陽性対照)
def _write_trial(root: Path, tid: str, rep: int, vocab=("dependency_not_resolved", "constraint_miss")):
    t = {"trial_id": tid, "input_hash": "in" * 8, "rubric_hash": "rb" * 8,
         "symptom_vocabulary": list(vocab), "repetitions": rep, "evaluator_policy": {"blind": True}}
    t["trial_hash"] = trial_hash(t)
    d = root / tid; (d / "runs").mkdir(parents=True, exist_ok=True)
    (d / "trial.yaml").write_text(yaml.safe_dump(t, allow_unicode=True), encoding="utf-8")
    return t


def _write_run(root: Path, t: dict, run_id: str, effort: str, result: str, extra_exec=None,
               extra_eval=None, tamper_hash=False, no_eval=False, eval_exec_hash=None, symptoms=None):
    req = {"model": "m-1", "effort": effort, "method_stack": [], "harness": {"name": "h", "hash": "h1"},
           "tool_permissions": ["read"], "runtime_config": {}}
    e = {"run_id": run_id, "trial_id": t["trial_id"], "trial_hash": t["trial_hash"],
         "treatment": {"requested": req, "resolved": {"model": "unknown", "effort": "unknown"}},
         "treatment_hash": treatment_hash(req), "started_at": "2026-09-03T00:00:00Z",
         "completed_at": "2026-09-03T00:01:00Z", "token_usage": {"input": 100, "output": 50},
         "output_hash": "out" * 5}
    if tamper_hash:
        e["treatment_hash"] = "0" * 64
    e.update(extra_exec or {})
    ef = root / t["trial_id"] / "runs" / f"{run_id}.execution.yaml"
    ef.write_text(yaml.safe_dump(e, allow_unicode=True), encoding="utf-8")
    if no_eval:
        return
    v = {"run_id": run_id, "execution_receipt_hash": eval_exec_hash or file_hash(ef),
         "evaluator": {"id": "independent-A", "spec_hash": "ev1"}, "rubric_hash": t["rubric_hash"],
         "rubric_sealed_before_run": True, "result": result,
         "observed_failures": list(symptoms if symptoms is not None else ([] if result == "pass" else ["dependency_not_resolved"]))}
    v.update(extra_eval or {})
    (root / t["trial_id"] / "runs" / f"{run_id}.evaluation.yaml").write_text(
        yaml.safe_dump(v, allow_unicode=True), encoding="utf-8")


def selftest() -> int:
    bad: list[str] = []
    base = Path(tempfile.mkdtemp(prefix="effort-cal-st-"))
    try:
        # known-good: M fail×2 / H pass×2, repetitions=2 → validate OK・supported
        g = base / "good"; t = _write_trial(g, "T1", 2)
        _write_run(g, t, "T1-M-01", "medium", "fail"); _write_run(g, t, "T1-M-02", "medium", "fail")
        _write_run(g, t, "T1-H-01", "high", "pass"); _write_run(g, t, "T1-H-02", "high", "pass")
        pr = validate(g)
        if pr:
            bad.append(f"known-good が validate で落ちた: {pr[:2]}")
        pj = project(g)
        s = pj["trials"]["T1"]["effort_sensitivity"]
        if not (s and s[0]["effort_sensitive"] == "supported"):
            bad.append(f"known-good の導出分類が supported でない: {s}")
        if not pj["sources"] or not pj["tool_hash"]:
            bad.append("投影に来歴(sources/tool_hash)が無い")
        # known-bad 1: evaluation だけ(execution なし)
        b = base / "b1"; t = _write_trial(b, "T2", 1)
        _write_run(b, t, "T2-M-01", "medium", "fail")
        (b / "T2" / "runs" / "T2-M-01.execution.yaml").unlink()
        if not validate(b):
            bad.append("known-bad1: execution なしの evaluation を通した")
        # known-bad 2: treatment_hash 改変
        b = base / "b2"; t = _write_trial(b, "T3", 1)
        _write_run(b, t, "T3-M-01", "medium", "fail", tamper_hash=True)
        if not any("treatment_hash" in p for p in validate(b)):
            bad.append("known-bad2: treatment_hash 改変を通した")
        # known-bad 3: evaluation に treatment(盲検の破れ)
        b = base / "b3"; t = _write_trial(b, "T4", 1)
        _write_run(b, t, "T4-M-01", "medium", "fail", extra_eval={"treatment": {"effort": "medium"}})
        if not any("盲検" in p for p in validate(b)):
            bad.append("known-bad3: evaluation の treatment 欄を通した")
        # known-bad 4: execution に candidate_reason(解釈の混入)
        b = base / "b4"; t = _write_trial(b, "T5", 1)
        _write_run(b, t, "T5-M-01", "medium", "fail", extra_exec={"candidate_reason": "E3"})
        if not any("解釈" in p for p in validate(b)):
            bad.append("known-bad4: execution の candidate_reason を通した")
        # known-bad 5: 反復不足 → 率を出さない
        b = base / "b5"; t = _write_trial(b, "T6", 3)
        _write_run(b, t, "T6-M-01", "medium", "fail"); _write_run(b, t, "T6-H-01", "high", "pass")
        if validate(b):
            bad.append(f"known-bad5 の前提(構造は適合)が不成立: {validate(b)[:1]}")
        s = project(b)["trials"]["T6"]["effort_sensitivity"]
        if not (s and s[0]["effort_sensitive"] == "insufficient-n"):
            bad.append(f"known-bad5: 反復不足で率を出した: {s}")
        # known-bad 6: 語彙外の症状 / execution_receipt_hash 不一致
        b = base / "b6"; t = _write_trial(b, "T7", 1)
        _write_run(b, t, "T7-M-01", "medium", "fail", symptoms=["made_up_symptom"], eval_exec_hash="f" * 64)
        pr = validate(b)
        if not (any("語彙" in p for p in pr) and any("座標同一性" in p for p in pr)):
            bad.append(f"known-bad6: 語彙外/ハッシュ不一致を通した: {pr}")
        # known-bad 7: 空 root
        if not validate(base / "empty"):
            bad.append("known-bad7: 空 root を通した")
        # known-bad 8: 序数外の effort ラベルは順序を仮定して分類しない
        b = base / "b8"; t = _write_trial(b, "T8", 1)
        _write_run(b, t, "T8-A-01", "turbo", "fail"); _write_run(b, t, "T8-B-01", "medium", "pass")
        s = project(b)["trials"]["T8"]["effort_sensitivity"]
        if not (s and s[0]["effort_sensitive"] == "unordered-effort"):
            bad.append(f"known-bad8: 序数外の effort を順序づけて分類した: {s}")
    finally:
        shutil.rmtree(base, ignore_errors=True)
    if bad:
        print("selftest FAIL(計器を先に疑う): " + " / ".join(bad))
        return 1
    print("selftest PASS(known-good 1・known-bad 8)")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("command", nargs="?", choices=["validate", "project", "hash-treatment"])
    ap.add_argument("arg", nargs="?")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.command == "hash-treatment":
        spec = load_yaml(Path(a.arg))
        req = spec.get("requested", spec) if isinstance(spec, dict) else spec
        print(treatment_hash(req)); return 0
    root = Path(a.arg) if a.arg else DEFAULT_ROOT
    if a.command == "validate":
        pr = validate(root)
        for p in pr:
            print(f"[FAIL] {p}")
        print("validate:", "OK" if not pr else f"{len(pr)} 件の問題")
        return 0 if not pr else 1
    if a.command == "project":
        pr = validate(root)
        if pr:
            print(f"validate に {len(pr)} 件の問題 — 投影しない(不整合な記録から導出しない)")
            return 1
        print(yaml.safe_dump(project(root), allow_unicode=True, sort_keys=False))
        return 0
    ap.print_help(); return 2


if __name__ == "__main__":
    sys.exit(main())
