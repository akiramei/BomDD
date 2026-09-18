r"""EXP-20260918-01 第 3 回(r1 是正版・03b)— ECO-080 V2: 受入節を二部形(条件形)に書き換えると Jev の弁別が回復するか。

設計(結果受領前に固定・README §5 と同一。r1 所見 IA-02/03/04/06 の是正を反映):
- 検体= 第 2 回で planned→performed と誤読された受入節 9 本(ECO-063/068/069/070/071/075/076/077/078)。
  腕 orig  = 原文(各 ECO の実際の見出し+本文原文)— 対照(第 2 回の再現・performed になる見込み)。
  腕 new   = 新書式(見出し「## 3. 受入条件(製造前に凍結)」+本文をテンプレの二部形「V<n>(条件): …であること — 検査法: …」に書き換え。**全条件に検査法**〔IA-04〕。
             内容は保存し文形だけ変える〔IA-02: ECO-077 の known-bad(実測) は実施済みの記録なので原文のまま残す= 混在検体として扱う〕。書き換えは当方)。
  腕 newh0 = 新書式の本文+**各 ECO の原文見出し**(「## 3. 受入」「## 3. 受入(製造時の候補)」「## 3. 受入(候補)」〔IA-03〕)。
- 質問・criteria・前処理= 第 2 回と同一(Choice 4 択・フェンス剥がし・status 非提示)。
- 認定条件(事前宣言・不変)= new で planned ≥ 8/9 かつ orig で performed ≥ 8/9。newh0 は別掲(条件外)。
- 記録= state_sha256 は完全な 64 桁〔IA-06〕。出力= results-03b.jsonl(r1 で REJECT された初版の記録は results-03.jsonl に残す)。
"""
import hashlib, json, re, sys, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve()
for p in ROOT.parents:
    if (p / "bomdd" / "60-change-register.yaml").is_file():
        ROOT = p
        break
else:
    ROOT = Path.cwd()
OUT = ROOT / "bomdd" / "reports" / "jev-qualification-01" / "results-03b.jsonl"
KEY_FILE = Path("C:/Users/akira/.typesafe/api_key")
MODEL = "jev-latest"
ECOS = ["063", "068", "069", "070", "071", "075", "076", "077", "078"]

INSTRUCTIONS = (
    "The `section` field is one section of a change-order document from a software methodology repository "
    "(Japanese, some English terms). Classify what kind of content the section is, judging only by what the text "
    "itself states — not by the heading number and not by whether it looks well written."
)
CRITERIA = {
    "performed": "Reports results of work or assessment that has already been carried out: measurements taken, checks run, "
                 "verdicts given, findings listed, receipts of an assessment recorded (things stated as done, with results).",
    "planned": "Describes what will be checked, verified, predicted, or decided later: acceptance criteria to be tested, "
               "predictions frozen before manufacturing, candidate decisions not yet executed (things stated as intended or expected).",
    "template": "A blank form or format example: generic instructions, angle-bracket placeholders, or field names to be "
                "filled in, not about one specific change.",
    "omitted": "States that the item was omitted, exempted, or is not yet written: an exemption declaration, a note that "
               "the receipt was skipped, or a placeholder saying it will be filled in later.",
}
FENCE_RE = re.compile(r"^(```|~~~)[^\n]*\n.*?(?:^\1[ \t]*$|\Z)", re.S | re.M)
NEW_HEAD = "## 3. 受入条件(製造前に凍結)"

# 新書式(テンプレの二部形・全条件に検査法。内容は原文を保存し文形だけ変える。当方の書き換え)
NEW_BODY = {
    "063": """
- V1(条件): self-conformance が全 PASS であること(C7 が 12/12・C4 scaffold に factory-delegate が配置されること)— 検査法: 単一入口 `python method/tools/self-conformance.py` の終了コードと C7/C4 行を観測。
- V2(条件): 正本と写しの差分が写し注記ブロック+`{{METHOD}}` 解決の 2 箇所のみであること(frontmatter 同一)— 検査法: `diff 正本 写し`。
- V3(条件): 旧写し(`~/.claude/skills/factory-delegate/SKILL.md`)と正本の本文差分が冒頭注記+工程 2 追記のみであること(手順本体の逸脱 0)— 検査法: `diff 旧写し 正本`。
- V4(条件): CI が success であること — 検査法: headSha 照合で run を特定し結論を読む。
- V5(条件): diff 窓が allowed_paths+台帳系のみであること — 検査法: `git diff --stat baseline..head`。
- witness(条件): 検査 exit 観測後に `bomdd-witness.py produce --eco ECO-063` → `verify --eco ECO-063` が ADVANCE のときだけ commit すること(ECO-062 の機構を実運用)— 検査法: verify の 1 行目と終了コード。
- 独立検査(条件): 製造者較正のみで受入とすること(散文の移設・機械挙動の変更= `SKILLS` 定数 1 名追加のみ・ECO-061 の先例)。user が異系統検査を求めれば §8 として追加する — 検査法: 較正 receipt の存在。
""",
    "068": """
- V1(条件・外部プローブ): 3 ツールそれぞれに `tempfile.tempdir=<不在パス>` の子プロセスで `--selftest` を実行したとき、1 行目が `UNMEASURABLE TREE_UNAVAILABLE(TEMP_UNAVAILABLE): …`・exit 2・traceback なしであること。
  `PATH=""` では `GIT_UNAVAILABLE` になること。通常環境では従来どおり `ADVANCE OK: selftest PASS…` exit 0 であること — 検査法: 子プロセスを起動し 1 行目と終了コードを観測。
- V2(条件・実環境): Phase 6 実 cell(Codex read-only)で `bomdd-run.py --selftest` を再実行したとき 1 行 UNMEASURABLE・exit 2 であること(織り込み案 C の効果測定)— 検査法: 実 cell で再実行し 1 行目と終了コードを観測。
- V3(条件): self-conformance が全 PASS・CI が success・窓が 3 ファイル+台帳系のみであること — 検査法: 単一入口の終了コード・`gh run list`・`git diff --stat`。
- V4(条件): 独立検査は製造者較正のみとすること(3 ファイル各 10 行の局所変更・本体経路非接触・ECO-065 A 案と同じ整理。異系統検査を要するなら製造裁定で指定する)— 検査法: 較正 receipt の存在。
""",
    "069": """
- V1(条件): 正本と写しの差分が ECO-063 の既知差分(注記ブロック+`{{METHOD}}` 解決)のみであること — 検査法: `diff` で実測。
- V2(条件): 60-change-order.md の検査官行に 2 欄が入っていること — 検査法: grep。
- V3(条件): self-conformance が全 PASS・CI が success・窓が 3 文書+台帳系のみであること — 検査法: 単一入口の終了コード・`gh run list`・`git diff --stat`。
- V4(条件): 製造者較正のみとすること — 検査法: 較正 receipt の存在。
""",
    "070": """
- V1(条件): SKILL.md §1 に許容表・DECIDE/REQUEST の必須要素追記・Scope の待機形があること / §2.3 に F5・§2.4 に送信停止規則があること — 検査法: grep。
- V2(条件): AGENTS.md のリンクが解決すること — 検査法: C12 の判定行。
- V3(条件): self-conformance が全 PASS・CI が success・窓が 3 文書+台帳系のみであること — 検査法: 単一入口の終了コード・`gh run list`・`git diff --stat`。
- V4(条件): 製造者較正のみとすること — 検査法: 較正 receipt の存在。
- V5(クローズ条件でない): EXP-20260912-01 を次の handoff 20 回で測る — 検査法: improvements.md の EXP 行。
""",
    "071": """
- V1(条件): SKILL.md §1 に `Free-style span` と `One-way ratchet`・§2.3 に F6・§2.7 に区間規則・§4 に ⑥⑦⑧があること — 検査法: grep。
- V2(条件): AGENTS.md のリンクが解決すること — 検査法: C12 の判定行。
- V3(条件): self-conformance が全 PASS・CI が success・窓が 3 文書+台帳系のみであること — 検査法: 単一入口の終了コード・`gh run list`・`git diff --stat`。
- V4(条件): 製造者較正のみとすること — 検査法: 較正 receipt の存在。
- V5(クローズ条件でない): 指標 ⑥⑦⑧を EXP-20260912-01 で測る — 検査法: improvements.md の EXP 行。
""",
    "075": """
- V1(条件): core(handoff.md の adapter 区画より前)に BomDD 固有語が 0 であること(grep 表: `ECO-`・`bomdd/`・`Phase`・`run-02`・`R1`・`Codex`・`NORMATIVE_RULING` 等)。adapter 区画に集約されていること — 検査法: grep 表の各語の件数。
- V2(条件): 写しの diff が既知 hunk(冒頭注記・`{{METHOD}}` 解決)のみであること — 検査法: `diff 正本 写し`。
- V3(条件): self-conformance が全 PASS(C7 13 本)・CI が success・窓が allowed_paths のみであること — 検査法: 単一入口の終了コード・`gh run list`・`git diff --stat`。
- V4(条件): 独立検査(製造裁定 A のとき: r1 境界探索「core に固有物が残っていないか・BomDD を知らない読者が契約を適用できるか」→ r2 是正確認+回帰・`--range` つきで起動・verified は inspection gate)を経ること — 検査法: run 台帳の cell 行と inspection gate。
- V5(条件): 較正 receipt があること — 検査法: order の較正 receipt 節(C17)。
- V6(条件): 60-change-order.md の配員欄に「機械的 enforcement が存在する」と読める語(解決・検証・止まる・STOP)が製品向け文言に残っていないこと — 検査法: grep。
""",
    "076": """
- V1(条件): 正本 §2.2 に `読み手規則`・§2.3 に `P5`〜`P8`・§3 に `付録(根拠・返答不要)` の例・A3 に `ECO-076` があること — 検査法: grep。
- V2(条件): 契約 §1 の sha256 が変更前後で一致すること / core(adapter 区画より前)の固有語が 0(13 語)であること / 写しの diff が既知 3 hunk のみであること — 検査法: sha256・grep・`diff`。
- V3(条件): self-conformance が全 PASS(exit 0 観測後に commit)・CI が success・窓が 3 文書+台帳系のみであること — 検査法: 単一入口の終了コード・`gh run list`・`git diff --stat`。
- V4(条件): 製造者較正のみとすること — 検査法: 較正 receipt の存在。
- V5(クローズ条件でない): EXP-20260914-02 で効果を測る — 検査法: improvements.md の EXP 行。
""",
    "077": """
- V1(条件・selftest): bomdd-job(F7 腕)・bomdd-run・bomdd-witness の selftest がすべて PASS であること — 検査法: 3 ツールの `--selftest` の終了コード。**known-bad(実測)**: 実 map の 1 class から roles を外すと job selftest が FAIL(復元後 PASS)。
- V2(条件・射影): 既存 ECO(ECO-076)の job ビューで `required_skills` が不変・`required_skills_by_role` が導出され・`receipt_author_role` が null であること。本 ECO の verified 行で `producer` が射影されること — 検査法: `bomdd-job.py --json` の出力。
- V3(条件・文書): 正本の工程 1 に役割欄・工程 5 に検査官の役割欄があること / 写しの diff が既知 2 hunk・`{{METHOD}}` 未解決 0 であること / テンプレに `receipt_author_role` のコメントがあること — 検査法: grep・`diff`。
- V4(条件): self-conformance が全 PASS(exit 0 観測後に commit)・CI が success・窓が allowed_paths のみであること — 検査法: 単一入口の終了コード・`gh run list`・`git diff --stat`。
- V5(条件): 異系統独立検査(EQ-002・range つき・検査官ブリーフに §1-2 の役割欄を適用)を経ること — 検査法: run 台帳の cell 行。
- V6(条件): 較正 receipt があること(著者役割を register に記す)— 検査法: order の較正 receipt 節と register の欄。
""",
    "078": """
- V1(条件): playbook §3 に `報告の正本経路`・factory-delegate 正本と写しに `報告の正本経路を 1 つ宣言する` が各 1 あること — 検査法: grep。
- V2(条件): 写しの diff が既知 2 hunk(8c8,12・10c14)のみで `{{METHOD}}` が 0 であること — 検査法: `diff`・grep。
- V3(条件): self-conformance が全 PASS(exit 0 観測後に commit)・CI が success・窓が allowed_paths のみであること — 検査法: 単一入口の終了コード・`gh run list`・`git diff --stat`。
- V4(条件): 製造者較正のみとすること — 検査法: 較正 receipt の存在。
- V5(非クローズ条件): 効果= 次の独立検査ブリーフで報告経路の読み違いが 0 であること — 検査法: OBS-20260915-01 のトリガー「同型 2 例目」で観測。
""",
}


def strip_fences(t):
    return FENCE_RE.sub("", t)


def orig_section(n):
    t = (ROOT / f"bomdd/60-change-order-eco-{n}.md").read_text(encoding="utf-8").splitlines()
    s = next(i for i, l in enumerate(t) if l.startswith("## 3. 受入"))
    e = next(i for i in range(s + 1, len(t)) if t[i].startswith("## "))
    return t[s], "\n".join(t[s + 1:e]) + "\n"


def build():
    specs = []
    for n in ECOS:
        head, body = orig_section(n)
        specs.append(dict(id=f"ECO-{n}", arm="orig", label="planned", head=head, text=strip_fences(head + "\n" + body)))
        specs.append(dict(id=f"ECO-{n}", arm="new", label="planned", head=NEW_HEAD, text=strip_fences(NEW_HEAD + "\n" + NEW_BODY[n])))
        specs.append(dict(id=f"ECO-{n}", arm="newh0", label="planned", head=head, text=strip_fences(head + "\n" + NEW_BODY[n])))
    return specs


def main():
    specs = build()
    if "--list" in sys.argv:
        for s in specs:
            print(s["id"], s["arm"], len(s["text"]), s["head"])
        print("total", len(specs)); return 0
    from typesafe_sdk import Choice, TypeSafeClient, TypeSafeAuthenticationError, TypeSafeError
    key = KEY_FILE.read_text(encoding="utf-8").strip()
    if not key:
        print("UNMEASURABLE: key file empty"); return 2
    q = {"kind": Choice(instructions=INSTRUCTIONS, criteria=CRITERIA)}
    n_ok = n_err = 0
    with TypeSafeClient(api_key=key, model=MODEL) as client, OUT.open("a", encoding="utf-8") as fh:
        for s in specs:
            state = {"section": s["text"]}
            sha = hashlib.sha256(json.dumps(state, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
            rec = dict(ts=datetime.now(timezone.utc).isoformat(timespec="seconds"), id=s["id"], arm=s["arm"], label=s["label"], head=s["head"], state_sha256=sha, chars=len(s["text"]))
            try:
                r = client.system_one(state=state, questions=q)
                a = r.answers["kind"]
                rec.update(model=r.model, choice=a.choice, confidence=a.confidence, probabilities=a.probabilities,
                           usage=dict(input_tokens=r.usage.input_tokens, output_tokens=r.usage.output_tokens))
                n_ok += 1
                print(f"{s['id']} {s['arm']:6} -> {a.choice:9} conf={a.confidence:.2f} p(planned)={a.probabilities.get('planned',0):.2f} p(performed)={a.probabilities.get('performed',0):.2f}")
            except TypeSafeAuthenticationError as e:
                rec.update(error="AUTH", error_class=type(e).__name__); n_err += 1; fh.write(json.dumps(rec, ensure_ascii=False) + "\n"); print("UNMEASURABLE AUTH"); break
            except TypeSafeError as e:
                rec.update(error="API", error_class=type(e).__name__, error_msg=str(e)[:200]); n_err += 1; print(f"{s['id']} UNMEASURABLE {type(e).__name__}")
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            time.sleep(0.2)
    rows = [json.loads(l) for l in OUT.read_text(encoding="utf-8").splitlines() if l.strip()]
    rows = [r for r in rows if "choice" in r]
    print("\n## 腕別\n\n| 腕 | N | planned | performed | template | omitted |\n|---|---|---|---|---|---|")
    for arm in ("orig", "new", "newh0"):
        rs = [r for r in rows if r["arm"] == arm]
        c = {k: sum(1 for r in rs if r["choice"] == k) for k in ("planned", "performed", "template", "omitted")}
        print(f"| {arm} | {len(rs)} | {c['planned']} | {c['performed']} | {c['template']} | {c['omitted']} |")
    print("\n| id | 原文見出し | orig→ | new→ | newh0→ |\n|---|---|---|---|---|")
    for n in ECOS:
        g = {r["arm"]: r for r in rows if r["id"] == f"ECO-{n}"}
        f = lambda a: f"{g[a]['choice']}({g[a]['probabilities'].get('planned',0):.2f})" if a in g else "—"
        print(f"| ECO-{n} | {g.get('orig',{}).get('head','—')} | {f('orig')} | {f('new')} | {f('newh0')} |")
    print(f"\ndone: ok={n_ok} err={n_err} tokens in={sum((r.get('usage') or {}).get('input_tokens') or 0 for r in rows)} out={sum((r.get('usage') or {}).get('output_tokens') or 0 for r in rows)} model={sorted({r['model'] for r in rows})}")
    return 0 if n_err == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
