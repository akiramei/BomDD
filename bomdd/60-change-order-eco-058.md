# Change Order — ECO-058(effort 較正の測定器 — trial/execution/evaluation receipt の検証と導出投影)

> 裁定: user 2026-09-03「打ち切り採用で。補強 4 点と境界宣言を含めて進めて」— Effort レベルの過不足を
> 計測する設計の converge(外部案 → 当方 3 修正 → 外部 3 修正 → 当方 4 補強+境界 1・4→1→0 で
> 打ち切り採用)。裁定が gate ① を兼ねる。**新規 skill 0・skill 本文変更 0**。

## 担当設備(equipment)

- 製造: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**
- 設計の出所: 外部 AI の案(calibrate 統合・capability table・treatment 比較)+当方の修正
  (calibrate 不変・表は導出物・採点独立/反復/コスト)+外部の再修正(receipt 分離・解釈の導出化・
  treatment identity)+当方の補強(trial/treatment 分離・requested/resolved・評価統制の凍結・投影の来歴)。

## 0. 実測(起票根拠)

- Effort レベル(内部推論量)は回答テキストから直接観測できない。観測可能なのは要求負荷・投入の痕跡・
  下流の帰結であり、「不足」は帰結に、「過剰」は無寄与作業にしか現れない(非対称)。
- 症状から原因へ飛ぶ判定器(「制約を 3 件落とした → Effort 不足 → High」)は較正前の仮説を設備へ
  焼き込む。本リポの既裁定(散文の実施要求≠実施証明・mutable 台帳を正本にしない・observed/unknown の
  分離・rubric の事前封印・到達モデルは unknown)に照らし、**測定器は観測記録の検証と導出投影に徹する**。

## 1. 変更要求(製造対象)

`method/tools/effort-calibration.py` を新設:
1. **正本= 3 種の immutable 記録**: trial 定義(input_hash・rubric_hash・症状語彙・反復数・盲検方針・
   trial_hash)/ execution receipt(treatment requested/resolved・treatment_hash・時刻・token・output_hash)/
   evaluation receipt(execution_receipt_hash・evaluator id+spec_hash・rubric_hash・封印フラグ・result・
   observed_failures ⊆ 語彙)。**execution と evaluation は別ファイル**(実行完了と評価完了は別イベント)。
2. **禁止キー**: execution に result/observed_failures/candidate_reason/response_class(観測に評価・解釈を
   混ぜない)/ evaluation に treatment/effort/model/candidate_reason/response_class(盲検・解釈の分離)。
3. **同一性**: trial_hash= 定義 5 項の canonical JSON / treatment_hash= requested(model・effort・
   method_stack{name,hash}・harness{name,hash}・tool_permissions・runtime_config)の canonical JSON。
   **resolved(到達モデル・適用 effort)は unknown を許容して別欄**(観測不能なものを推定で埋めない)。
4. **validate**(fail-closed): 必須キー・禁止キー・ハッシュ整合(trial/treatment/execution_receipt_hash=
   ファイル bytes)・語彙・盲検方針・対象 0 件の FAIL。
5. **project**(導出・read-only): trial × treatment_hash の n / pass / 率(反復数未達は `insufficient-n` —
   率を出さない)/ mean tokens、effort だけが異なる対の **effort 感度= supported / unsupported /
   insufficient-n**、**来歴**(源 receipt の sha256 一覧+本ツールの sha256)。不整合な記録からは投影しない。
6. **--selftest**: known-good 1(M fail×2 / H pass×2 → supported)・known-bad 7(execution なし / hash 改変 /
   盲検の破れ / 解釈の混入 / 反復不足 / 語彙外+座標不一致 / 空 root)。
7. **限界宣言 6 点**(docstring): (1) execution receipt のアンカーは現ハーネスで**未結線 — 手動記帳の
   散文契約・被覆不能な境界** (2) resolved は観測不能 (3) 盲検は構造でしか担保しない (4) 導出分類は
   仮説の支持であり policy 自動化はしない (5) 反復数は凍結・不足は率を出さない (6) immutability は
   単一実行では検査不能。

**採らない**: 新規 skill / calibrate・converge 本文の変更(凍結・converge は独立した treatment)/
capability table の手保守(正本にしない)/ E→High 規則の自動化 / self-conformance への組込み
(必要が実測されてから)/ 実 trial の実施(本 ECO は測定器のみ — 初回 trial は別途)。

## 2. 影響なし予測(反証可能・製造前に凍結)

diff は新規ファイル 1 本+台帳系。既存検査の判定不変(C7 の SKILLS 本数は不変・C13 は新規リンクなし・
C1 は bomdd/ 配下に新規 yaml を置かないため不変)。記録の置場 `bomdd/effort-trials/` は本 ECO では
作らない(実 trial 時に作る — 空ディレクトリを正本にしない)。

## 3. 受入

- **V1**: `--selftest` PASS(known-good 1・known-bad 7)。**V2**: 空 root の validate が FAIL・不整合記録で
  project が投影しない。**V3**: self-conformance 全 PASS。**V4**: CI 緑。**V5**: diff 窓。

## /preflight receipt(起動経路: 自発 — 既裁定の適用実装)

- 分類= 既裁定の適用実装(厳しい側= continuation)。状態: baseline `c935ac9` → rebase 後 `6b1a549`= **confirmed**(別セッションが
  ECO-055〜057 を進行中のため clean linked worktree で作業 — 主作業木のステージ済み変更には非接触)/
  次番 058= **confirmed**(HEAD の register 末尾= 057)/ 設計の裁定内容= **confirmed**(打ち切り採用の実文)/
  PyYAML 可用= **confirmed**(既存ツールが使用)。
- 開始判定: **PROCEED**・override 0。

## /converge receipt(起動経路: 人間呼び出し — 打ち切り採用)

- **判定: 未収束のまま打ち切り採用**(round 軌跡: 4→1→0 — 上限到達・開いた論点なし・user 裁定で採用)。
  起動経路: 人間呼び出し。
- round 1(4 件)= trial と treatment の分離 / requested と resolved の分離(到達モデル unknown の実測)/
  評価統制 3 点の凍結(盲検・evaluator spec hash・反復数)/ 投影の来歴。round 2(1 件)= execution receipt の
  アンカー未結線を被覆不能な境界として宣言。round 3= 0。
- **DoD**: 分類(製品欠陥/観測限界/評価方法)✔ / アンカー ✔(評価完了)・✘→宣言(実行完了は未結線)/
  実装先 ✔(effort-calibration.py 1 本)/ 赤 fixture ✔(known-bad 7 腕)/ 複雑性 ✔(skill 新設 0・
  本文変更 0・投影は導出物)/ 選択肢 ✔(A〜D+D′+受入れた 3 修正)。
- 検証した主張: 到達モデル unknown(盲検試験の設備刻印)/ §13 記録規約(hash 結合・座標同一性)/
  Instrument Registry 節(mutable 台帳を正本にしない)/ 盲検試験の rubric 封印。
- 未収束事項: なし。

## 4. 製造と受入の実測(2026-09-03)

- diff 監査の窓: baseline `6b1a549`(rebase 後の起票直前 HEAD — 起票時は c935ac9・別セッションの ECO-057 accept を
  跨いだため push 前に rebase・窓は同一)→ head は受入時に確定。
- `method/tools/effort-calibration.py` を新設(validate / project / hash-treatment / --selftest・限界 6 点)。
- **製造中の自己捕捉(計器欠陥)**: 初回の `--selftest` で **known-good 腕が FAIL** — project の effort 順序を
  文字列比較していたため `"high" < "medium"` となり低/高が反転(M fail / H pass の known-good を
  unsupported と分類)。序数 `EFFORT_ORDER` を導入し、序数外のラベルは順序を仮定せず `unordered-effort` と
  出す形へ是正・known-bad 8 腕目(序数外 effort)を追加。**陽性対照が計器を先に疑わせた実例**(OBS-20260828-05
  の予防面)。
- **V1 実測**: `--selftest` **PASS(known-good 1・known-bad 8)**。**V2 実測**: 存在しない root の validate=
  FAIL・exit 1 / treatment_hash 改変を含む記録での project= 「投影しない」・exit 1 / known-good の投影=
  effort_sensitivity supported(low medium 0.0 → high 1.0)・sources 8 件・tool_hash あり。**V1/V2 PASS**。
- V3 以降は §5 で確定。

### 較正 receipt(/calibrate 自己適用 — trigger ③: 検査器の新設直後。二軸)

- 査定した主張と判定:
  1. 「validate は禁止キー・ハッシュ不整合・語彙外・空集合を fail-closed で遮断する」— **observed / 適格**
     (known-bad 8 腕が各々独立に FAIL・空 root FAIL)。
  2. 「project は反復不足で率を出さず、来歴を持つ」— **observed / 適格**(insufficient-n 腕・sources と
     tool_hash の存在を実測)。
  3. 「本測定器で Effort の過不足が測れる」— **unknown(理由コード: 未実行)** — 実 trial は 0 件。
     本 ECO が示すのは記録の構造検証と導出の再現性まで。
- 検出した計器欠陥: **1 件(製造中・自己捕捉)** — effort 順序の文字列比較による低/高反転。known-good 腕で
  検出・序数化で是正・known-bad 腕を追加。
- 検出力の限界: docstring の 6 点。特に (1) アンカー未結線は、記録が「書かれなかった」ことを本ツールが
  検出できないことを意味する(空 root の FAIL は「何も無い」ときだけ効く)。
- battery 行別記録:

  | Q | asked/NA | 判定 | 実測 or 読解 | 所見 |
  |---|---|---|---|---|
  | Q1 | asked | observed/適格 | 読解 | docstring の主張とコードの一致(判定器ではなく測定器) |
  | Q2 | asked | observed/適格 | 実測 | known-good 1・known-bad 7(ラベルは設計裁定の要件から) |
  | Q3 | asked | observed/適格 | 実測 | 各 known-bad が独立に落ちる |
  | Q4 | asked | observed/適格 | 実測 | selftest は本体関数を合成記録で実行 |
  | Q5 | asked | observed/適格 | 実測 | 空 root・反復不足を PASS/率にしない |
  | Q6 | asked | observed/適格 | 実測 | exit code 経由 |
  | Q7 | asked | observed/適格 | 実測 | --selftest が常設陽性対照 |
  | Q8 | NA | — | — | 免除機構なし(測定器) |
  | Q9 | asked | observed/適格 | 実測 | 投影が tool_hash と源 receipt の sha256 を持つ |
  | Q10 | asked | observed/適格 | 読解 | 限界 6 点 |
  | Q11 | asked | observed/適格 | 実測 | 禁止キー/ハッシュ/語彙/反復/空集合をクラス別に |

## 5. CI 実測(V4)

- 対象 revision: `937d1d7`(**origin/main と一致を確認**)
- run 識別子: 33716957974 — 結論: **PASS**(completed/success・headSha 照合済み)
- V3 = self-conformance 全 PASS を **clean な linked worktree で独立観測してから** push(初回 push は
  別セッションの ECO-057 accept により non-fast-forward で拒否 → rebase → register の競合を「上流全採用+
  ECO-058 追記」で解消 → baseline を 6b1a549 へ更新して amend → 再検査 → push)。

## 6. クローズ

- diff 監査の窓: baseline `6b1a549` → head `937d1d7`(**窓閉鎖**)。窓内は effort-calibration.py+台帳系
  (order・register・improvements.md)のみ — 影響なし予測が的中(C7/C13/C1 判定不変)。
- 受入: V1(selftest known-good 1・known-bad 8)/ V2(空 root FAIL・不整合記録は投影せず・投影に来歴)/
  V3(全検査緑・clean worktree)/ V4(CI 緑)/ V5(窓)成立。較正 receipt は §4(行別 asked/NA つき)。
- 製造中の自己捕捉= known-good 腕が計器欠陥(effort 順序の文字列比較)を捕捉し是正(§4)。
- このクローズが支持しないもの: **本測定器で Effort の過不足が実際に測れること**(実 trial 0 件 —
  EXP-20260903-03 が初回実使用を測る)/ execution receipt の記帳が起きること(アンカー未結線・散文契約)/
  到達モデル・適用 effort の同一性(観測不能)/ 評価者の行動上の盲検 / policy(E→High)への昇格。
