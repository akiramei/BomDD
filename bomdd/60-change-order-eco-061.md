# Change Order — ECO-061(停止規則に貼られた品質の語を工程上の扱いへ直す — preflight「receipt 不在= 非起動の証拠」/ eco-fix・change-management「プローブが不合格にならなければ診断が誤り」)

> 裁定: user 2026-09-06「preflight・eco-fix の文言修正を ECO として起票して」— 外部スキル棚卸レビュー
> (2 往復・improvements.md 2026-09-06 節)の帰結。**起票のみ**(製造着手は別裁定)。
> 変更は散文 4 箇所(正本 3+写し 1)。**行動指示は不変・凍結スキル(converge/calibrate)には触れない・
> playbook 本文は変更しない**。

## 担当設備(equipment)

- 起票: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**

## 0. 実測(起票根拠)

- 外部レビュー(2026-09-06)が 3 スキルに同型の断定を指摘し、当方が原文で一致を確認した
  (improvements.md 2026-09-06 節)。型= **運用上の停止規則に品質の語が貼られている**。playbook §9
  (自己査定 receipt は順守の記録であって弁別力の証明ではない・2026-09-03 昇格)の適用漏れであり、新原則ではない。
- **preflight**([正本:30](../method/templates/product-profile/skills/preflight.md) / [写し:36](../.claude/skills/preflight/SKILL.md)):
  「起動は preflight receipt で観測可能化する(receipt 不在= 非起動の**証拠**)」。確実に言えるのは規定の実施記録が
  ないことで、実行漏れと記録漏れは区別できない。意図は fail-closed の**扱い**(記録がなければ非起動として扱う —
  「空白は無報告のみが悪」と同じ規約)であり、帰結はどちらの漏れでも同じ(receipt を作ってやり直す)。
- **eco-fix**([正本:21](../method/templates/product-profile/skills/eco-fix.md)):「プローブが不合格にならない場合、
  **診断が誤り**。コードに触らず /eco-file の工程診断へ差し戻す」。プローブ感度不足・対象環境の違い・再現条件の
  欠落でも同じ結果になる。指示している行動(コードに触らず差し戻す)はいずれの原因でも正しい — 理由の断定だけが強すぎる。
- **change-management**([正本:38](../method/templates/product-profile/change-management.md)):R5 の同文
  「プローブが不合格にならなければ診断が誤り — R2 へ差し戻す」。eco-fix と同型・同一 profile 内の 2 正本。
- **playbook §8.3**(bomdd-playbook-v1.md:605)は既に「不合格にならない場合、黙って弱めずコードに触らず診断を
  精密化する(再現マトリクス → 機構特定 → より強いプローブ)」と**過大断定なしで書かれている** — 変更不要。
  かつ ECO-055(in-progress)の allowed_paths に含まれるため、本 ECO は playbook に触れない(diff 混濁回避)。
- 同型文の掃討(`grep -rn "診断が誤り|不合格にならない場合|receipt 不在= 非起動"`): 上記 4 箇所+playbook §8.3
  (適正)+improvements.md の歴史記述(書き換えない)。他になし。
- 他原因(感度不足・環境差・再現条件欠落)で「プローブが赤にならなかった」実例が本リポ・製品リポにあるかは
  **未確認**(本 ECO は論理の過大を直すもので、実例の有無は主張しない)。

## 1. 変更要求(製造対象)

散文の置換のみ。**行動指示・停止規則・自発起動契約・適用範囲は変えない。**

1. **preflight 正本:30**(+ 写し:36 を同期 — D-1):
   - 旧: `観測可能化する**(receipt 不在= 非起動の証拠)。`
   - 新: `観測可能化する**(receipt 不在は**非起動として扱う** — 規約。実行漏れと記録漏れは区別できないため「証拠」ではない。帰結はどちらも同じ= receipt を作ってやり直す)。`
2. **eco-fix 正本:21**:
   - 旧: `**プローブが不合格にならない場合、診断が誤り。コードに触らず /eco-file の工程診断へ差し戻す。**`
   - 新: `**プローブが不合格にならない場合、診断またはプローブが症状を捉えていない(真因の誤り・プローブ感度不足・環境差・再現条件の欠落のいずれか)。コードに触らず /eco-file の工程診断へ差し戻す(playbook §8.3: 黙って弱めず診断を精密化)。**`
3. **change-management 正本:38**:
   - 旧: `プローブが不合格にならなければ診断が誤り — R2 へ差し戻す。`
   - 新: `プローブが不合格にならなければ診断またはプローブが症状を捉えていない — コードに触らず R2 へ差し戻す(playbook §8.3)。`

**採らない**: converge「収束」の語の扱い(凍結・EXP-20260906-01/02 の測定結果か実運用の失敗観測が出てからの
別裁定)/ playbook §8.3 の改稿(適正・ECO-055 窓内)/ improvements.md の歴史記述(「receipt 不在= 非起動の証拠」
5 箇所)の書き換え(§13: 歴史は書き換えない)/ eco-fix に「他原因の切り分け手順」を新設すること(§8.3 の再現
マトリクスを参照するに留める — 散文を足さない)/ 機械ゲートの新設(文言の過大は機械検査の対象にしない)。

## 2. 影響なし予測(反証可能・製造前に凍結)

diff は上記 4 ファイル(各 1 行〜2 行)+台帳系(order・register・improvements.md)。self-conformance の判定は
不変(C7 スキル本数不変・C13 リンク不変〔新規リンクなし〕・C16/C17 は order/verified を対象とし本変更は
非対象・C4 scaffold は写しではなく正本を配布するため配布物の文言だけが変わる)。preflight の自発起動契約・
4 値判定・eco-fix の手順番号と R5〜R7 は不変。製品リポへは kit 再設置まで非波及。

## 3. 受入

- **V1**: 置換後の 4 ファイルに旧文が 0 件・新文が各 1 件(grep)。**V2**: 正本と写しの差分が「写し」注記と
  プレースホルダー解決の既知 2 箇所のみ(ECO-042 時点と同じ)。**V3**: self-conformance 全 PASS・判定不変。
  **V4**: CI 緑。**V5**: diff 窓= allowed_paths+台帳系のみ。
- 独立検査: 不要(散文 4 箇所・機械挙動の変更なし)— 製造者較正のみで受入する旨を verified 時に明記。

## /preflight receipt(起動経路: 自発 — 既裁定の適用実装〔起票〕)

- 分類= 既裁定の適用実装(user 裁定 2026-09-06)。baseline `509533f`= **confirmed**(HEAD・origin/main 一致・
  作業木 clean)/ 次番 061= **confirmed**(register 末尾= 060)/ 変更対象 4 箇所の実在= **confirmed**
  (preflight.md:30・SKILL.md:36・eco-fix.md:21・change-management.md:38 を実読)/ 凍結の非該当=
  **confirmed**(凍結は converge・calibrate のみ — improvements.md 2026-09-02 節)/ 同一ファイルへの進行中 ECO
  なし= **confirmed**(in-progress は ECO-055 のみ・refs= 52-metrics.yaml+playbook)。
- 開始判定: **PROCEED**(起票まで)・override 0。製造は別裁定。

## /converge receipt(起動経路: 自発 — 置換文の設計)

- **判定: 収束**(round 軌跡: 2→0→0)。
- DoD: ✔ 各文の主張が測れる範囲(記録の有無・症状の捕捉)に縮む / ✔ 行動指示は不変 / ✔ 同型文の全サイトを
  掃討し列挙 / ✔ 凍結スキル非接触 / ✔ 正本→写しの同期規則(D-1)に従う / ✔ 散文を足さず既存正本(§8.3)を参照。
- round 1(新規 2 件): ①change-management.md:38 に同文(grep で発見・対象へ追加)②playbook §8.3 は既に適正
  かつ ECO-055 窓内(対象から除外・理由を §0 に明記)。round 2: 0 件。round 3: 0 件。
- 検証した主張: 同型文の所在(grep 実行・§0)/ 凍結範囲(improvements.md:5753)/ ECO-055 の refs(register:2062)/
  正本と写しの差分が 2 箇所(diff 実行)。
- 敵対自問: 「選択肢を落としていないか」— eco-fix 側に切り分け手順を新設する案は§8.3 の重複(正本 2 つ)になるため
  採らない。「正本が 2 つになっていないか」— eco-fix と change-management の R5 文は元から 2 箇所にあり、本 ECO は
  両方を同じ意味へ揃える(統合は範囲外)。「自分の設計の帰結を構造的制約と読み替えていないか」— 「記録なし=
  非起動として扱う」は規約であって観測ではないと本文に明記する。
- 未収束事項: なし。
