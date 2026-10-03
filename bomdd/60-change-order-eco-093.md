# Change Order — ECO-093(製造パッケージの条件付き定義の一本化・playbook 冒頭ステータスの正本化・phase3 の粒度規準に candidate 留保を戻す〔文書のみ〕)

> 裁定: user 2026-10-03 DECIDE「2:A」(外部レビュー 2026-10-02 論点 4・P3・論点 2 の文面部分)。
> 出典: [外部レビュー](reports/external-review-20261002/review.md) 論点 4 / P3 / 論点 2 — 照合= [verification.md](reports/external-review-20261002/verification.md)。
> 文書のみ・製造者較正のみ(前例= ECO-086 / ECO-088)。方針(E/S の上流裁定・粒度の第一基準)は本 ECO で決めない — ECO-094(試行)の領分。

## 担当設備(equipment)

- 起票・製造: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**
- producer: EQ-001
- 独立検査: なし(文書のみ・製造者較正のみ。inspector 行は置かない)

## 0. 実測(起票根拠・2026-10-03)

- **論点 4(製造パッケージの列挙)**: `method/` 配下で製造パッケージを列挙する箇所は grep で 15 箇所。うち **35-design-system-bom の条件(UI-CAD 案件で必須)を持つのは
  40-work-order(L17・L21)・templates/README(L38・L51)・onboarding/developer-navigation(L91)のみ**。playbook §4.6 G3(L336〜343)・phase3-design(L23)・phase4-manufacture(L8)・
  34-routing(L10)・product-profile/skills/bomdd-next(L16)は `20/30〜34/40` のみで 35 を欠く。定義の正本は無く、各所が一覧を複製している(playbook §13 原則⑥「列挙の腐敗」の自リポ実例)。
  実製品で 35 の欠落が発生した記録は無い(canonical な factory-delegate は実 work order を渡すため緩和される — レビューと同じ評価)。
- **P3(playbook 冒頭ステータス)**: README L16 は「現行の方法論の正本は playbook に一本化(2026-09-02 裁定)」と明記。playbook L3〜5 は「単一題材検証済み・一般化は未検証・method-v1 とは
  まだ統合しない」のまま(forward-01 当時の文)。README L18 はその後の実証(forward-01〜04・scale-01・transfer-01〜03・N=3)を記す。正本の所在と実証状況が冒頭で分離されていない。
- **論点 2(文面部分)**: playbook §4.1 L114 は「**粒度規準(candidate)**: M-BOM unit は…E-BOM 品目はその設計版」と candidate を明示。phase3-design L6 は「**粒度規準**: 部品は『独立に再製造・
  交換でき、単独で受入できる最小単位』で切る」と、留保なしに E-BOM の切り分けへ使う。contracts/bom-granularity-guide L7〜30 は E-BOM を「仕様責任者に理解できる機能・責務」とし、
  クラス・ファイル・DOM の一覧を否定する — phase3 の文は playbook と guide の双方から逸脱している。

## 1. 変更要求(製造対象・凍結)

1. **製造パッケージの定義を playbook §4.6 に一本化**: §4.6 の一覧に「Design System BOM(35)— UI-CAD 案件のみ必須」を加え、「本節が製造パッケージの定義の正本。他の文書は本節を参照し、
   一覧を複製しない」を明記。
2. **複製箇所を参照へ**(列挙を残す場合は 35 の条件を同梱): phase3-design L23(G3)・phase4-manufacture L8・34-routing L10・bomdd-next L16。40-work-order の列挙は製品側に配布される
   「実装開始条件」として残し、定義の正本(playbook §4.6)への参照を 1 行添える。templates/README・developer-navigation は条件を既に持つため不変。
   example-session-log(過去のセッション記録)・00-charter(同期タイミングの時点指定)・plm-ready-contract(必須成果物の検査)は列挙の目的が別なので不変。
3. **playbook 冒頭ステータスの改訂**: 「正本であること(README・2026-09-02 裁定)」と「実証状況(forward-01〜04・scale-01・transfer-01〜03・FINDINGS §7/9/11)」を分けて書き、
   method-v1 は凍結スナップショット(現行規範ではない)と README と同じ語で揃える。各節の candidate 表示は不変(正本化を理由に candidate を実証済みへ格上げしない)。
4. **phase3-design L6 の粒度規準に candidate 留保を戻す**: playbook §4.1 と同じ「粒度規準(candidate)」の語を置き、E-BOM 品目の基準は bom-granularity-guide(機能・責務・受入観点が閉じる単位)を
   参照する形にする。M-BOM unit の「独立に再製造・交換でき、単独で受入できる最小単位」は M-BOM 側の規準として残す。
5. **採らない**: パッケージ生成器や新しい機械検査の追加(生成器は存在せず、一覧の複製は本 ECO で参照に置き換えるため)/ E/S の上流裁定・粒度の第一基準の方針変更(ECO-094)/
   §4.6 以外の節の改訂 / 過去のセッション記録の書き換え。

## 2. 影響なし予測(製造前・凍結)

diff= playbook(§冒頭ステータス・§4.6)・phase3-design・phase4-manufacture・34-routing・40-work-order・product-profile/skills/bomdd-next+台帳系のみ。
tools・hooks・.github・schemas・contracts は diff 0。C7(README)・C13(リンク)・C15(deprecated 参照)の判定不変。bomdd-init が配布する templates の内容が変わる(34・40・bomdd-next)が
C4/C11 の煙試験は内容を検査しない(判定不変)。製品リポへは次回配布時に波及(既存製品の work order は不変)。

## 3. 受入条件(製造前に凍結・二部形・ECO-080)

- V1(条件): `method/` 配下で製造パッケージを列挙する箇所のうち、35 の条件も §4.6 への参照も持たないものが 0 件であること — 検査法: §0 の grep(`30[〜–-]34|20/30`)を再実行し、該当行を 1 行ずつ読む。
- V2(条件): playbook §4.6 に「35・UI-CAD 案件のみ必須」と「定義の正本」の文があること — 検査法: grep。
- V3(条件): playbook 冒頭に「正本(README・2026-09-02 裁定)」と実証状況(forward-01〜04・scale-01・transfer-01〜03)の文があり、「method-v1 とはまだ統合しない」の文が無いこと — 検査法: 実読+grep。
- V4(条件): phase3-design L6 に「粒度規準(candidate)」と bom-granularity-guide への参照があること — 検査法: grep。
- V5(条件): diff が allowed_paths のみ・self-conformance 全 PASS(exit 0 観測後に commit)・CI success であること。
- V6(条件): 製造者較正のみ・較正 receipt(trigger ①)があること。

## /preflight receipt(起動経路: **自発** — 既裁定の適用の開始時)

- 分類= 既裁定の適用(user 2026-10-03「2:A」)。baseline `069e0d5`= **confirmed** / 次番 093= **confirmed** / 列挙箇所 15 件と 35 条件の有無= **confirmed**(grep+実読)/
  playbook 冒頭と README の不一致= **confirmed**(実読)/ phase3 L6 と playbook L114・guide の不一致= **confirmed**(実読)/ 同一ファイルへの進行中 ECO= **confirmed**(なし)。
- 開始判定: **PROCEED**・override 0。

## /converge receipt(起動経路: 自発 — 定義の正本の置き場の設計)

- **判定: 収束**(round 軌跡: 3→1→0)。
- DoD: ✔ 条件付きの定義が 1 か所にある / ✔ 複製箇所は参照か条件同梱 / ✔ 製品側に配布される自己完結文書(40-work-order)は列挙を保つ / ✔ 方針(E/S・粒度)を先取りしない。
- round 1(新規 3 件): ①正本は playbook §4.6(規範)か 40-work-order(配布物)か → §4.6(規範が定義・配布物は参照つきで列挙を保つ)②bomdd-next は配布スキル → 書き換えると製品側へ
  次回配布で波及(C14 は kit 鮮度の計器の較正であり内容は見ない)→ 波及は意図どおり ③過去のセッション記録(example-session-log)は書き換えない(記録の改竄になる)。
- round 2(新規 1 件): ④phase3 L6 の修正で E-BOM の第一基準を「利用者に意味のある機能」と書くと ECO-094 の方針を先取りする → guide の既存の語(機能・責務)への参照に留める。round 3: 0 件。
- 検証した主張: 列挙 15 箇所と条件の有無(grep+実読)/ README と playbook の文(実読)/ guide の文(L7〜30 実読)。
- 敵対自問: 「参照に置き換えると読み手が §4.6 まで飛ぶ手間が増える」— 一覧を残す箇所は 35 の条件を同梱するので飛ばなくても足りる。参照は「正本がどこか」を示すため。
- 未収束事項: なし。

## 4. 製造(2026-10-03・製造者 EQ-001)

- 製造物(7 ファイル・+14/-11 行): playbook 冒頭ステータス(正本・実証状況・candidate 不格上げの 3 文に分離)/ playbook §4.6(定義の正本の宣言+35 の条件付き品目)/
  phase3-design L6(粒度規準(candidate・playbook §4.1)・E-BOM は guide の機能・責務・M-BOM unit の規準を分離)・L23(G3 の参照)/ phase4-manufacture L8 / 34-routing L10 / 40-work-order L17(正本参照の注記)/
  bomdd-next L16 / **templates/README L13**(製造中の追加: 「工場へ渡す場合は 20/30–34 へ昇格後」の列挙 1 箇所 — §0 の 15 箇所の数え上げで L38・L51 の条件を持つ同一ファイルとして見落としていた。
  V1 の厳密化のため同梱し、register の affected_refs / allowed_paths に追加)。
- 製造中の発見: ①templates/README L13 の見落とし(上記)②残る列挙 7 行(plm-ready-contract L269 必須成果物の検査・example-session-log L174 過去記録・phase5-accept L13 補正先・
  s-bom-template L54 層別出現・00-charter L76 同期タイミング・36-ui-dictionary L14 と templates/README L22 canonical 名の反映先)は製造パッケージの定義ではなく、§1-2 の宣言どおり不変。

## 5. 受入の実測(2026-10-03・製造者)

- **V1**= PASS(観測: `grep -rnE '30[〜–-]34|20/30' method/` から improvements.md を除き、`35` も `§4.6` も持たない行は上記 7 行のみで、いずれも製造パッケージの列挙ではない。
  製造パッケージを列挙する 8 箇所〔playbook §4.6・phase3 L23・phase4 L8・34-routing L10・40-work-order L17/L21・bomdd-next L16・templates/README L13/L38/L51・developer-navigation L91〕は全て 35 の条件か §4.6 参照を持つ)。
- **V2**= PASS(観測: playbook L339「本節が製造パッケージの定義の正本」・L343「Design System BOM(35)… UI-CAD 案件のみ必須」)。
- **V3**= PASS(観測: playbook L3〜7 に「現行の方法論の正本(README・2026-09-02 裁定で一本化)」「実証状況(正本であることとは別に読む)… forward-01〜04・scale-01・transfer-01〜03」
  「candidate を実証済みへ格上げしない」。`grep -c 'まだ統合しない'`= 0)。
- **V4**= PASS(観測: phase3-design L6 に「粒度規準(candidate・playbook §4.1)」と `method/contracts/bom-granularity-guide.md` の参照)。
- **V5**・**V6**= §6(クローズ時)。

## 6. クローズ(クローズ時に追記)
