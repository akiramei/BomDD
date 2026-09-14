# Change Order — ECO-076(handoff 実装規則の「読み手規則」— 結論先行・内部語の言い換え・証拠は付録か記録へ・裁定の単一化/契約 v0.4 不変〔verified〕)

> 裁定: user 2026-09-14「handoff スキルについて、プロトコル自体は問題ない。問題は応答内容」+第三者コメント(user 転送)を読んで対処せよ、という指示。
> 契約 §1 は変えない(user の判定)。変えるのは §2 実装規則(交換可能・default)と §3 例。**起票と製造を同一 commit で行う**(文書のみ・ECO-071 の型)・受入は製造者較正のみ。
> verified 昇格は self-conformance PASS と CI 結論を観測した後の受入 commit で(観測前に転記しない)。

## 担当設備(equipment)

- 起票・製造: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**
- producer: EQ-001
- 独立検査: なし(文書のみ・製造者較正のみ。inspector 行は置かない)

## 0. 実測(起票根拠)

- **対象となった応答**: OBS-20260914-01 の DISCUSS(工程設計レビューへの応答・2026-09-14・commit b2b4540 の元メッセージ)。第三者コメントの指摘(要旨):
  1. 内部用語が説明なしに連続する(「r1」「昇格循環」「selftest 腕」「self-conformance C 群」「job 射影」「order」「陽性対照」)。
  2. 主張は 4 点と単純なのに、実測・例外・過去 ECO・補足が本文に入り結論が埋もれる。冒頭「半分はすでに満たされ・残り半分が未測定」は「半分」が何か次を読まないと分からない。
  3. 造語「探索収率」は分母・分子が不明。測りたいのは「未知の問題をどれだけ見つけているか」で、普通の言葉で言える。
  4. 「r1 所見 → ツールの selftest 腕」より「見つかった問題は、そのツールの回帰テストとして追加されている」の方が明確。
  5. 提案 1〜4 への賛否を求めているが、裁定が要るのは「今は起票せず OBS 記帳だけでよいか」の 1 点。2〜4 は付随する設計方針。
  6. 総評: **「監査証跡としては良いが、人間との議論文としては悪い」。証拠を全部本文に載せる癖がある。本文は判断に必要な事実だけにし、詳細は「根拠」節か別表へ**。
- **既存規則との照合(実読)**: §2.2 共通に「パケット本体は 15 行程度・詳細な証拠は system of record に置き、handoff はそれを参照して再現しない」は**既にある**。
  しかし §2.3 validate に対応する検査項目がない(structural H/F/M・semantic P1〜P4 はいずれも mode と必須要素の検査)。生成規則にあって検査にない項目は違反しても観測されない —
  EXP-20260912-01 の指標(mode 訂正・reply_format 順守・許容表)は読み手の負荷を測っていないので、確定 5/5 のまま本件が起きた。
- **コメント自身の観測(記録)**: 圧縮例のヘッダは `[DISCUSS / COMPLETE]` で、契約 §1 の許容表では無効な組合せ(DISCUSS は COMPLETE を取らない)。プロトコルの問題ではなく
  例示の書き方の問題であり、§3 の例では `[DISCUSS / PAUSED]` で示す。指摘の本体(読み手規則)には影響しない。

## 1. 変更要求(凍結・文書のみ)

1. `method/templates/product-profile/skills/handoff.md` §2.2 共通に **読み手規則** 4 点を追加(handoff は議論文であって監査証跡ではない):
   (1) 結論先行 — ヘッダの次の 1 文が結論。抽象語(半分・一部・概ね)で先送りせず対象を数えて列挙する
   (2) 語彙 — 本文だけで意味が取れない内部語は初出で言い換える。造語を導入しない
   (3) 証拠の配置 — 本文は判断に必要な事実だけ。列挙は `付録(根拠・返答不要)` か system of record へ。数値は結論を変えるものだけ
   (4) 裁定の単一化 — DECIDE / DISCUSS は実際に裁定が要る点だけを問う。付随方針は前提として述べ、承認項目に並べない。
2. §2.3 semantic に **P5〜P8**(各読み手規則に 1 対 1)。semantic に置く理由: 機械判定できない(語彙の内外・結論性・必要十分性は読解)。較正は既存 P と同じく人間の訂正回数で外から測る。
3. §3 に読み手規則を適用した **DISCUSS の例**(環境非依存・付録「根拠」つき・`[DISCUSS / PAUSED]`)。
4. adapter A3 に出自 1 行(ECO-076)。`.claude/skills/handoff/SKILL.md` は正本から再生成(既知 3 hunk)。
5. `method/improvements.md` に本節+EXP-20260914-02(効果の計測: 次の handoff で user の読みにくさ指摘の回数)。

**採らない**: 契約 §1 の変更(user 判定: プロトコルは問題ない)/ 本文行数の structural 上限(15 行「程度」のまま — 硬い上限は待機形・REQUEST 様式と衝突し、
証明のための複雑性になる)/ 語彙の機械検査(内外の判定は環境依存で core に置けない)/ 第 5 の mode / bomdd-init・README・AGENTS.md の変更(本数・所在は不変)。

## 2. 影響なし予測(製造前・凍結)

diff= skills 正本・写し・improvements.md+台帳系(order・register)のみ。契約 §1 の本文は不変(sha256 で確認)・core 固有語 0 を維持(ECO-075 V1 の 13 語)・写しの diff= 既知 3 hunk・
C7 13 本不変・C12/C13 リンク先不変・tools/templates(60-change-order)/hooks/.github diff 0・worklist 新規 ID 1(EXP-20260914-02)・警告 0。

## 3. 受入

- **V1**: 正本 §2.2 に `読み手規則`・§2.3 に `P5`〜`P8`・§3 に `付録(根拠・返答不要)` の例・A3 に `ECO-076`(grep)。
- **V2**: 契約 §1 の sha256 が変更前後で一致 / core(adapter 区画より前)の固有語 0(13 語)/ 写しの diff= 既知 3 hunk のみ。
- **V3**: self-conformance 全 PASS(exit 0 観測後に commit)・CI 緑・窓= 3 文書+台帳系。
- **V4**: 製造者較正のみ。**V5(クローズ条件でない)**: EXP-20260914-02 で効果を測る。

## /preflight receipt(起動経路: **job 経由** — `bomdd-job.py ECO-076` の出力を開始 artifact として読んだ)

- 分類= 既裁定の適用実装(user 指示: コメントを読んで対処・契約は不変)。baseline `b2b4540`= **confirmed** / 次番 076= **confirmed**(grep 0)/ §2.2 の既存規則(15 行・system of record)=
  **confirmed**(実読)/ §2.3 に読み手側の検査項目なし= **confirmed**(実読)/ 同一ファイルへの進行中 ECO なし(ECO-075 は verified)= **confirmed**。
- job ビュー(register 追記後・order 生成前): required_skills= `["calibrate", "preflight"]`・stop_type= MISSING_INPUT(order 不在 — 本ファイル生成で解消)・required_capability= null(配員欄は order 生成後に解決)。
- 開始判定: **PROCEED**・override 0。

## 4. 製造と受入の実測(2026-09-14・同一 commit)

- 製造物: 正本 §2.2 読み手規則 4 点・§2.3 P5〜P8・§3 DISCUSS 例(付録「根拠」つき)・A3 出自 1 行 / 写し(正本から再生成)/ improvements.md 節+EXP-20260914-02。
- **V1**= PASS(grep: `読み手規則` 7・`P5 `〜`P8 ` 各 1・`付録(根拠・返答不要)` 2・`ECO-076` 1〔adapter のみ〕)。
- **V2**= PASS(契約 §1 の sha256 `4326a0467cae` が変更前後で一致・63 行 / core 固有語 13 語すべて 0 / 写しの diff= 3 hunk〔8c8,12 冒頭注記・A2/A3 の `{{METHOD}}` 解決 2 行〕)。
- **V3**= §5 で記録(観測後)。

## 5. クローズ(2026-09-14・verified・製造者較正のみ)

- **V3**= PASS(self-conformance: 1 回目 **exit=1・C13 FAIL**〔新規 order が未追跡で git ls-files の母集団に入らず「リンク不在」— ECO-070 で既知の手順欠陥の再演〕→ stage 後 2 回目 **exit=0 全 PASS**
  〔C7 13 本・C13 不在 0〕→ witness(tree 87a13ee882a7・gates 1)→ 入口 dry ADVANCE → 製造 commit cea4b41 → push → CI run 34842179743 **success**)。
  diff 監査の窓: baseline `b2b4540` → head `cea4b41`(**窓閉鎖**・受入 commit は台帳系のみ)。窓内= allowed_paths のみ。
- **V1/V2**= §4(PASS)。**V4**= 製造者較正のみ(独立検査なし)。register: `implemented → verified`・head 凍結。
- **V5(非クローズ条件)**: EXP-20260914-02 で次の 20 通の読みにくさ指摘を数える。本 ECO の handoff(製造報告)自体が最初の適用個体。
- 実測(正直記載): self-conformance の 1 回目 FAIL は製造物の欠陥ではなく実行手順(stage 前実行)。ECO-070/071 で同じ手順欠陥が記録済みで、本件で 3 例目 — 「stage してから実行」は
  手順書に書かれているが機構化されていない(bomdd-run 入口は self-conformance を起動しない)。今回は記録のみ。

### 較正 receipt(/calibrate 自己適用 — trigger ①: verified 昇格。文書のみの変更)

- 査定した主張と判定:
  1. 「正本 §2.2 に読み手規則 4 点・§2.3 に P5〜P8・§3 に付録「根拠」つき例・A3 に出自がある」— **observed / 適格**(grep 7/1・1・1・1/2/1・V1)。
  2. 「契約 §1 は不変」— **observed / 適格**(契約ブロックの sha256 `4326a0467cae` が変更前後で一致・63 行)。
  3. 「core は環境非依存のまま」— **observed / 適格**(ECO-075 V1 と同じ 13 語で 0。ただし検査官の 24 語+読解は今回なし)。
  4. 「写しは正本と同期」— **observed / 適格**(diff 3 hunk= ECO-075 の既知 hunk と同一位置種別)。
  5. 「読み手規則は指摘の型を消す」— **unknown(未測定・EXP-20260914-02)**。semantic 検査(P5〜P8)は自己申告であり、較正は人間の指摘回数で外から測る。
- 検出した計器欠陥(帰属つき): 製造物 0 件。受理側 1 件(手順・stage 前実行で C13 が偽 FAIL — 計器は正しく「母集団に無い」と言っており計器欠陥ではなく手順欠陥。3 例目・記録のみ)。
- 検出力の限界: 読み手規則の効果は未測定。第三者(コメント執筆者)の再評価は未実施。独立検査なし。P5〜P8 は機械判定できず、違反は人間の指摘でしか観測されない
  (本 ECO の機序そのもの — 生成規則にあって検査にない項目は違反が観測されない — は semantic 検査を足しても「自己申告の検査」にしかならず、外部計測 EXP で補う)。
- battery 行別記録:

  | Q | asked/NA | 判定 | 実測 or 読解 | 所見 |
  |---|---|---|---|---|
  | Q1 | asked | observed/適格 | 実測 | grep・sha256・diff(V1/V2) |
  | Q2 | asked | NA 相当 | — | 文書変更に known-bad 対照なし(宣言)。固有語 grep の陽性対照は ECO-075 の 44 件を流用せず今回なし |
  | Q3 | asked | observed/適格 | 実測 | 変更前(§2.2 に 15 行規則のみ・§2.3 に読み手項目なし)→ 変更後(4 点+P5〜P8) |
  | Q4 | asked | 読解 | 読解 | 「生成規則にあって検査にない項目は違反しても観測されない」は本件 1 例からの読解 |
  | Q5 | asked | observed/適格 | 実測 | 未測定(効果・第三者再評価・独立検査なし)を宣言 |
  | Q6 | asked | observed/適格 | 実測 | 検査 exit 観測(1 回目 FAIL → 2 回目 PASS)→ witness → 入口 dry → commit → push → CI success |
  | Q7 | asked | NA | — | 陽性対照なし(文書) |
  | Q8 | NA | — | — | 免除機構なし |
  | Q9 | asked | observed/適格 | 実測 | witness(ECO-076.json)・register・commit cea4b41・run 台帳(ECO-076.jsonl) |
  | Q10 | asked | 宣言 | 読解 | 上記「検出力の限界」 |
  | Q11 | asked | observed/適格 | 読解 | 入力クラス= 正本/写し/記帳の 3 文書・規則 4 点と検査 4 項の対応 |

- このクローズが支持しないもの: 読み手規則の効果(EXP-20260914-02)/ 第三者による再評価 / 契約の変更(していない)/ 製品リポでの適用結果。
