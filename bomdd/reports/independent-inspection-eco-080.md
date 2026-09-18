[INFORM / COMPLETE]

REJECT IA-01・IA-02・IA-03・IA-04

- range: 境界探索
- inspector: EQ-002 / Codex CLI / gpt-5.6-sol
- 対象 revision: `79cdcf74c69b89a255cc950d8ceae85bc152b153`
- commit: 0（開始時・終了時とも HEAD は対象 revision）
- 外部 API: 呼び出しなし
- リポ内ファイル書込み: 0

開始時 `git status --short`（exit 0）:

```text
（出力なし）
```

終了時 `git status --short`（exit 0）:

```text
（出力なし）
```

## 判定要約

- V1 の文字列上の要件と kit 配布: 満足。
- V2 の記録上の数値: 満足（orig 9/9 performed、new 9/9 planned）。
- ただし、新書式の Markdown 構造、内容保存、newh0 の腕定義、および実験で使った「新書式」とテンプレ書式の一致に不適合があるため REJECT。
- 自己適用 §3/§4: 検査官が測れる V1・V2 について整合。起票時 §3 からの変更なし。

## 所見

### IA-01 — テンプレの失敗分類表が Markdown の表として成立しない

- 再現:
  - `git show 79cdcf...:method/templates/60-change-order.md`
  - 対象 §5 を `pandoc -f gfm -t native` で解析（exit 0）。
- 観測:
  - 二部形の第3箇条書き直後に空行がない。
  - `| 観測 | 分類 |` 以下は `Table` ではなく、第3箇条書き内の `SoftBreak` を含む通常テキストとして解析された。
- 期待との差:
  - 既存の失敗5分類表が独立した表として維持されるべきところ、二部形5行の挿入により表示構造が壊れている。
- 帰属: 製造物 `method/templates/60-change-order.md`。

### IA-02 — ECO-077 の新書式は内容を保存していない

- 読解箇所:
  - 原文 `bomdd/60-change-order-eco-077.md` §3 V1
  - `jev_qual_03.py` の `NEW_BODY["077"]`
- 観測:
  - 原文は `known-bad(実測)` と明記し、「実 map の1 classから roles を外した」「復元後 PASS」という実施済み記録を含む。
  - 新文はこれを将来検査する条件へ変え、さらに検査法を「temp map での再実行」としている。
- 期待との差:
  - 文形だけの変更ではない。実施済みという証拠属性を落とし、fixture も実 map から temp map へ変更している。
- 帰属: 製造物 `jev_qual_03.py`。README §4 が認識している原文の混在を、内容保存のまま条件化することはできない。

### IA-03 — newh0 の「原文見出し」説明と実装が2件で不一致

- 再現箇所:
  - README §5 の newh0 定義
  - `jev_qual_03.py`: `OLD_HEAD = "## 3. 受入"` および `build()`
  - ECO-068/075 の原文 §3
- 観測:
  - ECO-068 の原文見出しは `## 3. 受入(製造時の候補)`。
  - ECO-075 の原文見出しは `## 3. 受入(候補)`。
  - newh0 は両方とも固定値 `## 3. 受入` に置換する。
- 期待との差:
  - README の「新書式の本文＋原文の見出し」ではない。
  - したがって newh0 9/9 から「見出しを変えず本文だけで効いた」とする説明は、少なくとも2/9では実験定義どおりに成立しない。
- 帰属: 製造物 README §5・§6 と `jev_qual_03.py`。

### IA-04 — 実験の NEW_BODY が宣言した新書式を一貫して実装していない

- 読解箇所:
  - README §5: `V<n>(条件): …であること — 検査法: …`
  - `jev_qual_03.py` の各 `NEW_BODY`
- 観測:
  - 多数の条件に `— 検査法:` がない。例: ECO-070 V3/V4、ECO-075 V3/V4/V5、ECO-076 V3/V4、ECO-078 V4。
- 期待との差:
  - 第3回はテンプレが規定する二部形そのものではなく、より緩い「条件語を加えた文」の集合を測っている。
  - 9/9 planned は条件文形の効果を支持するが、テンプレの完全な書式を検証したとはいえない。
- 帰属: 製造物 `jev_qual_03.py` と README §5 の設計記述。

### IA-05 — UNMEASURABLE の記録要件が曖昧

- 読解箇所: `method/templates/60-change-order.md` §5 結果行。
- 観測:
  - `UNMEASURABLE(観測: <座標= ログ / commit / run id>)` は、測定不能の理由・失敗した計器・不足した権限等を必須にしていない。
- 期待との差:
  - 状態選択自体は明確だが、何を記録すれば UNMEASURABLE の根拠になるかは一意でない。
- 帰属: 凍結要求および製造物の双方。実装は order §1 の指定を忠実に写しているため、主として要求側の未規定。
- 判定への扱い: 境界所見。IA-01〜IA-04とは独立。

### IA-06 — `state_sha256` は完全な SHA-256 値ではない

- 再現箇所: `jev_qual_03.py` の `.hexdigest()[:16]` と `results-03.jsonl`。
- 観測:
  - 全27行にフィールドは存在するが、値はすべて16文字（64 bit 相当）で、64文字の SHA-256 全値ではない。
- 期待との差:
  - フィールド名から完全な SHA-256 座標と読む余地がある。短縮値なら命名または短縮規則の明記が必要。
- 帰属: 製造物。
- 判定への扱い: 境界所見。

## 9節の第三者読解

| id | 原文を結果と読み違える余地 | 新書式を未実施条件と一意に読めるか | 内容保存 |
|---|---|---|---|
| ECO-063 | あり。`全 PASS`、`CI 緑`、件数が結果文形 | はい | はい。検査コマンドの明示化のみ |
| ECO-068 | あり。候補見出しはあるが具体的出力・exit値が結果状 | はい | 一部不一致。V2 に「台帳の cell 行」を追加 |
| ECO-069 | あり。`差分…のみ`、`全 PASS`、`CI 緑` | はい | はい。grep等の明示化 |
| ECO-070 | あり。存在・PASSを断定する文形 | はい | はい |
| ECO-071 | あり。存在・PASSを断定する文形 | はい | はい |
| ECO-075 | あり。候補見出しはあるが `0`、`全 PASS` 等が結果状 | はい | はい |
| ECO-076 | あり。hash一致・差分のみ・全PASSの結果文形 | はい | はい |
| ECO-077 | あり。加えて `known-bad(実測)` は実際に結果 | はい。ただし実測来歴を条件へ変換している | いいえ。IA-02 |
| ECO-078 | あり。件数・差分・全PASSの結果文形 | はい | はい |

総括: 文形変更による planned/performed の弁別効果自体は第三者読解でも認める。ただし ECO-077 は内容保存を満たさない。

## テンプレ文言

- §3 の「変更分の受入を先に追加」「治具の凍結条件」と二部形の規律は矛盾しない。
- §5 の失敗5分類とも意味上は矛盾しないが、IA-01 により Markdown 構造上は表が壊れる。
- 二部形5行に機械 lint/enforcement の存在を主張する文言はない。
- テンプレ内の既存説明には、製品リポでは「機械的な導出・検証・強制は存在しない」と明記されている。
- 条件行と PASS/FAIL 結果行の区別は明確。
- UNMEASURABLE の証拠内容は IA-05 のとおり未規定。

## 自己適用の整合

- §3 V1〜V5 はいずれも `…であること` を用いた条件で、受入結果を書いていない。
- §4 は条件行を変更せず、V1/V2 を別の `Vn= PASS(観測: …)` 行として記録している。
- §3 の V1〜V5 と §4 の V1〜V5 参照は対応する。V3〜V5 は後続節への参照であり、本 round の測定対象外。
- `git diff --unified=0 0e50b2f 79cdcf... -- bomdd/60-change-order-eco-080.md` に §3 の hunk はない。起票時から条件行は不変。
- §5・§6 は禁止に従い検査していない。

## 第3回記録

ローカル集計:

```text
LINE_COUNT=27
MISSING_STATE_SHA256=0
MISSING_MODEL=0
MISSING_CHOICE=0
MISSING_PROBABILITIES=0
orig:  N=9 planned=0 performed=9
new:   N=9 planned=9 performed=0
newh0: N=9 planned=9 performed=0
model=jev-1.13.0
```

- README §6、`summary-03.md`、JSONL 集計は数値上一致。
- probabilities は全27行に4 choice のキーを持つ。
- README §5 とスクリプトは、対象 ECO、3腕、new/orig の認定閾値について一致。
- newh0 の見出し定義は IA-03 のとおり不一致。
- 「結果受領前に固定」は、設計と結果が同一 commit に入っているため検査官には検証できなかった。これは所見ではなく証拠資格の限界。

## kit 非破壊 smoke

実行:

```text
python method/tools/bomdd-init.py Smoke --dir C:\Users\akira\AppData\Local\Temp\bomdd-eco080-inspection-20260918-a7f93c2e --no-gui --no-git
BOMDD_INIT_EXIT_CODE=0
```

- 生成された製品側 `bomdd/60-change-order.md` と同梱 kit 側 `bomdd-kit/method/templates/60-change-order.md` の双方に、二部形5行を確認。
- 一時生成物は OS temp 内で、リポの status には影響なし。

## 意図と実装の乖離

`git diff --stat 0e50b2f 79cdcf...` は8ファイル、275 insertions / 4 deletions。

- 差分は ECO-080 order/register、Jev 第3回記録、improvements、テンプレに限定され、ブリーフ記載の窓内。
- 既存 order の差分はなく、order 差分は ECO-080 のみ。
- `method/bomdd-playbook-v1.md`、`change-management.md`、`acceptance-evidence.md` は diff 0。
- 機械 lint の追加なし。
- ECO-079 対象ファイルへの変更なし。

## 較正 receipt

### 査定した主張と判定

- V1 二部形の存在・kit 配布: PASS。ただし Markdown 表構造は FAIL（IA-01）。
- V2 数値記録: PASS。
- 「内容保存・文形だけ変更」: FAIL（IA-02）。
- 「newh0 は原文見出しを保持」: FAIL（IA-03）。
- 「実験は宣言した完全な新書式を測った」: FAIL（IA-04）。
- 自己適用条件不変・V番号対応: PASS。

### 計器欠陥

- Pandoc/GFM 構文解析で表崩れを検出。計器自体の欠陥は認めない。
- 初回 kit smoke 要求は temp の再帰削除を同一要求に含めたため実行ポリシーが起動前拒否した。削除を除いた再実行は exit 0。製造物への帰属なし。
- Jev は再実行していないため、その計器の再較正はしていない。

### 検出力の限界

- README §5 が結果受領前に固定された時系列は検証不能。
- JSONL が外部 API の原応答を完全に表すか、署名・外部ログによる検証はしていない。
- Jev の設備認定全体、工程組み込み、他の書き手への一般化は測っていない。
- §5・§6、register の内容は禁止により読んでいない。
- Markdown は Pandoc の GFM parser で測定し、GitHub 実環境への外部送信・表示確認はしていない。

### battery

| 問い | 記録 |
|---|---|
| Q1 | asked — README/コード/報告の主張差を検査し IA-02〜IA-04 |
| Q2 | asked — orig/new の対照記録を確認。事前固定時系列は測定不能 |
| Q3 | asked — 3腕を分離集計 |
| Q4 | asked — README の宣言入力と実装を照合し IA-03 |
| Q5 | asked — 欠損・エラー行なし。UNKNOWN を PASS に算入した形跡なし |
| Q6 | asked — 結果受領前固定の順序は同一 commit のため測定不能 |
| Q7 | asked — orig 対照は9/9 performed を再現 |
| Q8 | NA — 予防ゲートと免除は本検査対象外 |
| Q9 | asked — revision、HEAD、model、state fingerprint を照合。短縮hashは IA-06 |
| Q10 | asked — 上記「検出力の限界」に記録 |
| Q11 | asked — orig/new/newh0 を別入力クラスとして確認。newh0 の2件に交絡あり |

## 範囲外の観察

- Jev の工程組み込み、設備認定全体の合否、playbook 織り込み案の採否は判定していない。
