# r050-arms — 受入証拠検査(R-050)の対照腕を組み立てて実行する測定スクリプト(ECO-085)
#
# 目的: 「R-050 の所見なし」がどの検体で成立するかを、合否値だけを変えた検体で実測する。
# 判定器ではない — 期待との突合は --expect を与えたときだけ行う(pre= 是正前の基準 / post= ref-v0.11 の規則)。
#
# 検体の出所: BomDD-Plm の固定オラクル fixture `oracle/fixtures/clean/repo`(M unit 1・受入 CP 1= CP-CORE-001)を
# 一時ディレクトリへ複製し、bomdd/50-as-built.yaml だけを腕ごとに差し替える。対象リポには書き込まない。
# 実在標本(--specimen): 製品リポの 32-mbom / 33-control-plan と、50-as-built の指定エントリ 1 本だけを
# 実行時に読んで一時ディレクトリへ組む(製品リポの内容を本リポへ複写しない)。
#
# 使い方:
#   python r050-arms.py --plm <BomDD-Plm のパス> [--expect pre|post] [--specimen <製品リポ> --entry <AB id>]
#
# 終了コード: 0= 実行できた(--expect なし)/ 期待どおり(--expect あり)・1= 期待と不一致・2= 測定不能。
# 検出力の限界(宣言):
#   (1) 測るのは CLI の終了コードと R-050 所見(severity 別)の対象 ID 集合まで — 所見の文言・行番号は見ない。
#   (2) 合成検体は M unit 1・CP 1 の最小形。複数 unit・workspace・retired unit・抑止(suppress)は腕に無い。
#   (3) CLI の個体(どの commit の dist か)は呼び出し側が記録する — 本スクリプトは HEAD と dist の sha256 を出すだけ。
#   (4) 測定不能の所見(規則 (c))と適用外の所見(規則 (d))は対象 ID を実装が決めるため、件数 1 以上だけを見る。

import argparse
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

CP = "CP-CORE-001"
OTHER = "CP-OTHER-001"
ANY = "<1 件以上>"   # 対象 ID を問わず 1 件以上


def row(cp, result=None, eid="TE-x-001"):
    r = {"evidence_id": eid, "cp_ref": cp}
    if result is not None:
        r["result"] = result
    return r


def entry(rows):
    return {"as_built": [{"id": "AB-x-factory-01", "lifecycle_state": "as-built", "test_evidence_refs": rows}]}


# 腕: name / ab(50-as-built の内容・None= ファイルを置かない)/ keep_m(M-BOM を残すか)/ gate / desc
# 期待: pre・post それぞれ (error の対象 ID 集合 or ANY, info の対象 ID 集合 or ANY)
def arm(name, ab, desc, pre, post, keep_m=True, gate="acceptance"):
    return {"name": name, "ab": ab, "desc": desc, "pre": pre, "post": post, "keep_m": keep_m, "gate": gate}


NONE = (set(), set())
ARMS = [
    arm("good", entry([row(CP, "pass")]), "正常陰性対照: 合格", NONE, NONE),
    arm("fail", entry([row(CP, "fail")]), "違反陽性対照: 不合格", NONE, ({CP}, set())),
    arm("notrun", entry([row(CP, "not-run")]), "違反陽性対照: 未実行", NONE, ({CP}, set())),
    arm("blocked", entry([row(CP, "blocked")]), "違反陽性対照: 保留", NONE, ({CP}, set())),
    arm("nofield", entry([row(CP)]), "違反陽性対照: 合否値の欄なし", NONE, ({CP}, set())),
    arm("unknown", entry([row(CP, "expected-fail")]), "違反陽性対照: 語彙外の値", NONE, ({CP}, set())),
    arm("mixed", entry([row(CP, "pass"), row(CP, "fail", "TE-x-002")]),
        "違反陽性対照: 同一 CP に合格と不合格", NONE, ({CP}, set())),
    arm("extra", entry([row(CP, "pass"), row(OTHER, "fail", "TE-x-002")]),
        "違反陽性対照: 受入対象外の CP に不合格行", NONE, ({OTHER}, set())),
    arm("missing", entry([]), "既存の陽性対照: 証拠行が空", ({CP}, set()), ({CP}, set())),
    arm("noab", None, "対象欠落チャレンジ: 製造記録ファイルなし", NONE, (ANY, set())),
    arm("emptylist", {"as_built": []}, "対象欠落チャレンジ: as_built が空リスト", NONE, (ANY, set())),
    arm("docdialect", {"as_built": {"golden_approvals": []}}, "対象欠落チャレンジ: 文書方言(mapping)",
        NONE, (ANY, set())),
    arm("noab-G3", None, "ゲートの対照: 製造記録なしを G3 で実行(製造前は正常な状態)", NONE, NONE, gate="G3"),
    arm("notarget", None, "適用外の対照: 受入対象の M unit なし", NONE, (set(), ANY), keep_m=False),
]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run_cli(cli: Path, repo: Path, out: Path, gate: str = "acceptance"):
    p = subprocess.run(
        ["node", str(cli), str(repo), "--gate", gate, "--format", "json", "--out", str(out)],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    try:
        diag = json.loads(p.stdout)
    except json.JSONDecodeError:
        return p.returncode, None, None, None
    fs = list(diag.get("findings", [])) + list(diag.get("infos", []))
    r050 = [f for f in fs if f.get("rule") == "R-050"]
    err = [f for f in r050 if f.get("severity") == "error"]
    info = [f for f in r050 if f.get("severity") != "error"]
    others = [f for f in fs if f.get("rule") != "R-050" and f.get("severity") == "error"]
    return p.returncode, err, info, others


def match(expect, found):
    got = {str(f.get("targetId")) for f in found}
    if expect == ANY:
        return len(found) >= 1, got
    return got == expect, got


def show(s):
    return ", ".join(sorted(s)) if s else "なし"


def add_other_cp(repo: Path):
    """受入対象外の CP を Control Plan に定義する(参照切れ R-003 の赤で R-050 の判定を覆い隠さない)。"""
    cpf = repo / "bomdd" / "33-control-plan.yaml"
    cpd = yaml.safe_load(cpf.read_text(encoding="utf-8"))
    cpd["control_plan"]["characteristics"].append({
        "id": OTHER, "characteristic": "sample (no M unit refers to this row)",
        "verifies": ["E-CORE-001"], "requirement_refs": ["REQ-001"], "depth": "unit",
        "test_vectors": ["boundary"]})
    cpf.write_text(yaml.safe_dump(cpd, allow_unicode=True, sort_keys=False), encoding="utf-8")


def drop_m_units(repo: Path):
    (repo / "bomdd" / "32-mbom.yaml").write_text("mbom:\n  manufacturing_units: []\n", encoding="utf-8")
    cpf = repo / "bomdd" / "33-control-plan.yaml"
    cpd = yaml.safe_load(cpf.read_text(encoding="utf-8"))
    for c in cpd["control_plan"]["characteristics"]:
        c["verifies"] = [v for v in c.get("verifies", []) if not str(v).startswith("M-")]
    cpf.write_text(yaml.safe_dump(cpd, allow_unicode=True, sort_keys=False), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plm", required=True)
    ap.add_argument("--expect", choices=("pre", "post"))
    ap.add_argument("--specimen")
    ap.add_argument("--entry")
    a = ap.parse_args()

    plm = Path(a.plm)
    cli = plm / "packages" / "cli" / "dist" / "main.js"
    ev = plm / "packages" / "core" / "dist" / "rules" / "evaluate.js"
    src = plm / "oracle" / "fixtures" / "clean" / "repo"
    if not (cli.is_file() and ev.is_file() and src.is_dir()):
        print("UNMEASURABLE: CLI・evaluate.js・clean fixture のいずれかが無い")
        return 2
    head = subprocess.run(["git", "-C", str(plm), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", str(plm), "status", "--porcelain"], capture_output=True, text=True).stdout.strip()
    print(f"CLI の個体: BomDD-Plm HEAD {head}・作業木 {'clean' if not dirty else 'dirty'}"
          f"・evaluate.js sha256 {sha256(ev)[:12]}")
    print(f"期待: {a.expect or 'なし(測定のみ)'}")
    print()
    print("| 腕 | 説明 | ゲート | exit | R-050 error の対象 | R-050 info の対象 | R-050 以外の error | 期待との一致 |")
    print("|---|---|---|---|---|---|---|---|")

    bad = 0
    with tempfile.TemporaryDirectory(prefix="r050-arms-") as td:
        for m in ARMS:
            repo = Path(td) / m["name"] / "repo"
            shutil.copytree(src, repo)
            if not m["keep_m"]:
                drop_m_units(repo)
            if m["name"] == "extra":
                add_other_cp(repo)
            if m["ab"] is not None:
                (repo / "bomdd" / "50-as-built.yaml").write_text(
                    yaml.safe_dump(m["ab"], allow_unicode=True, sort_keys=False), encoding="utf-8")
            rc, err, info, others = run_cli(cli, repo, Path(td) / m["name"] / "out", m["gate"])
            if err is None:
                print(f"| {m['name']} | {m['desc']} | {m['gate']} | {rc} | (出力を読めない) | - | - | 測定不能 |")
                bad += 1
                continue
            ge, gi = {str(f.get("targetId")) for f in err}, {str(f.get("targetId")) for f in info}
            verdict = "-"
            if a.expect:
                ok_e, _ = match(m[a.expect][0], err)
                ok_i, _ = match(m[a.expect][1], info)
                verdict = "一致" if (ok_e and ok_i) else "不一致"
                bad += 0 if (ok_e and ok_i) else 1
            print(f"| {m['name']} | {m['desc']} | {m['gate']} | {rc} | {show(ge)} | {show(gi)} | {len(others)} | {verdict} |")

        if a.specimen:
            sp = Path(a.specimen)
            repo = Path(td) / "specimen" / sp.name
            (repo / "bomdd").mkdir(parents=True)
            for f in ("32-mbom.yaml", "33-control-plan.yaml"):
                shutil.copy2(sp / "bomdd" / f, repo / "bomdd" / f)
            doc = yaml.safe_load((sp / "bomdd" / "50-as-built.yaml").read_text(encoding="utf-8"))
            ent = [e for e in doc.get("as_built", []) if e.get("id") == a.entry]
            if len(ent) != 1:
                print(f"UNMEASURABLE: 標本のエントリ {a.entry} を一意に特定できない({len(ent)} 件)")
                return 2
            rows = ent[0].get("test_evidence_refs") or []
            (repo / "bomdd" / "50-as-built.yaml").write_text(
                yaml.safe_dump({"as_built": ent}, allow_unicode=True, sort_keys=False), encoding="utf-8")
            rc, err, info, others = run_cli(cli, repo, Path(td) / "specimen" / "out")
            got = {str(f.get("targetId")) for f in (err or [])}
            nonpass = sorted({str(r.get("cp_ref")) for r in rows if r.get("result") != "pass"})
            hit = [c for c in nonpass if c in got]
            sp_head = subprocess.run(["git", "-C", str(sp), "rev-parse", "--short=7", "HEAD"],
                                     capture_output=True, text=True).stdout.strip()
            print()
            print(f"実在標本: {sp.name}({sp_head})の製造記録エントリ 1 本・証拠行 {len(rows)}"
                  f"・合格以外の行を持つ CP {len(nonpass)} 件")
            print(f"  exit {rc}・R-050 error {len(err or [])} 件・合格以外の行を持つ CP のうち所見に出たもの {len(hit)} 件")
            if a.expect == "post":
                ok = set(hit) == set(nonpass)
                print(f"  期待(合格以外の行を持つ CP がすべて所見に出る)との一致: {'一致' if ok else '不一致'}")
                bad += 0 if ok else 1
            elif a.expect == "pre":
                ok = len(hit) == 0
                print(f"  期待(是正前の基準: 合格以外の行は所見にならない)との一致: {'一致' if ok else '不一致'}")
                bad += 0 if ok else 1

    return 1 if (a.expect and bad) else (2 if bad else 0)


if __name__ == "__main__":
    sys.exit(main())
