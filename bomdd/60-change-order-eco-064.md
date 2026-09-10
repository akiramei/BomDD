# Change Order — ECO-064(ECO-062 第 2 弾 F1 — job ビューの `required_skills` を事前宣言する: activation-map(参照付き対応表)+ receipt 突合〔起票のみ〕)

> 裁定: user 2026-09-10「F1 を第 2 弾として起票して」— ECO-062 §5.1 F1(required_skills の事前宣言欄がない)と Phase 4 の実測
> (ECO-063: job の `required_skills` が null のため EXP-20260910-01 の中心量= 明示起動の効果が測れない)の帰結。**起票のみ**(製造着手は別裁定)。
> 本 ECO は起票工程自体を **job 経由**で起動した(§0.4)— Phase 4 の 2 本目候補。

## 担当設備(equipment)

- 起票: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**

## 0. 実測(起票根拠)

### 0.1 欠落 F1 の現状

- `bomdd-job.py` は `required_skills` を null+`source: none(F1)` で出す(ECO-062 §1-1・§5.1)。register/order に事前宣言欄がなく、receipt 見出しは
  事後記録のため転写しない、と判定した。
- Phase 4 の 1 本目(ECO-063 §6)で、job 経由でも明示起動は起きず自発起動に依存 → EXP-20260910-01 の next trigger を「F1 実装後の初 job」へ更新済み。

### 0.2 出所となる契約(実読・転写しない)

- **preflight**: 自発起動契約= 既存状態依存タスク(continuation・bug fix・既裁定の適用実装)を**開始するとき**。機械アンカー候補= 作業開始
  (タスク受領・起票 commit)。task contract 最小表は 2 クラス(continuation / bug-fix)・**行の追加統制**(欠落事故 1 件の実測または裁定のみ)。
- **converge**: 設計合成タスク(裁定候補・対策仕様・スキーマ・アーキテクチャ案)を認識したら。機械アンカー= C16 の hard-positive
  (`CONVERGE_HARD_POSITIVES`: 裁定を求め / gate ① / 裁定対象 / 残ゲート / 推奨)— self-conformance.py が正本。
- **calibrate**: ①verification・受入・較正の節を書くとき(verified 昇格)②既存の緑の引用 ③検査器の新設・変更直後 ④計器インシデント後。
  機械アンカー= ①③(verification artifact・検査器の変更)— C17 の適用範囲(verified)が正本。②④は認識依存(機械では出せない)。
- receipt 検出の正本= self-conformance の `CONVERGE_RECEIPT_HEAD_RE` / `C17_RECEIPT_RE`(fence 除去つき)。preflight receipt は
  「/preflight receipt」見出し(ECO-042 様式)— 機械検出は未整備。

### 0.3 二重正本の回避(設計上の制約)

- 対応表を job に固定値で持つと(F5 と同型)、契約が変わったとき job が腐る。契約文を YAML に写すと転写値になる。
  → 対応表は**参照付き**(各行が契約の所在= ファイル+節を `source` に持ち、判定は機械アンカーだけで行う)にする。
- converge 要否・receipt 検出の正規表現は self-conformance.py から **import**(同一ディレクトリ・正本 1 つ)。import 不能なら該当欄を unknown にする
  (測定不能を合格にしない)。

### 0.4 起票工程の job 経由起動(Phase 4 の 2 本目・起票のみ)

- register 追記直後に `python method/tools/bomdd-job.py ECO-064` を実行し、その出力(state=filed・stop_type=NONE・write_scope)を開始 artifact として
  preflight を行った(receipt 下記)。`required_skills` は本 ECO 自身が対象の欄のため null(F1)。

## 1. 変更要求(製造対象の候補 — 製造裁定時に凍結)

1. **activation-map**(新規・`method/templates/product-profile/skills/activation-map.yaml`): task class ごとの `required_skills` と、各行の
   `anchor`(機械判定に使う台帳側の事実)と `source`(契約の所在)。初期行= 
   - `start`(status ∈ {filed, decided} の ECO の開始)→ `preflight` / source= preflight.md 自発起動契約
   - `design-synthesis`(order が C16 hard-positive に該当)→ `converge` / source= converge.md 自発起動契約+self-conformance C16
   - `verified-promotion`(status → verified)→ `calibrate` / source= calibrate.md 自発起動契約 ①+C17
   - `instrument-change`(affected_refs が計器パス〔method/tools/*.py・bomdd/hooks/*・.github/workflows/*〕に触れる)→ `calibrate` / source= calibrate.md ③
     (**パス集合は列挙であり腐る** — 宣言つきの限界。§13 原則⑥)
   - 行の追加統制= preflight 最小表と同じ(欠落事故 1 件の実測または裁定・出典必須)。
2. **bomdd-job.py**: `required_skills` を activation-map から導出(`source`= map の行 ID)。`skills_observed` を order の receipt 見出し(C16/C17 と共通の
   正規表現を import・preflight は「/preflight receipt」見出し)から導出。`skills_missing`= required − observed(**情報欄のみ・停止語彙は不変・gate 化しない** —
   §8.5「必要が実測されてから」)。map 不在・import 不能= 該当欄 unknown(source に理由コード)。
3. **selftest**: map の全スキル名が skills/ に実在・全行に source・4 class の陽性対照(該当/非該当)・observed の検出(fence 内は無視)・map 不在→unknown。
4. **EXP-20260910-01 の測定器化**: job ビューの `skills_missing` が空か否かを、job 経由で回した ECO ごとに記帳できる(自己申告でなく order の receipt 見出しから導出)。

**採らない**: skills_missing を停止種別や機械ゲートにすること(必要が実測されてから)/ 契約文の YAML への転写 / preflight 最小表への行追加 /
required_capability(F2)・forbidden(F3)・expected_outputs(F4)・independent_inspection(F6)の同時実装(別弾)/ 認識依存トリガー(calibrate ②④)の機械化。

## 2. 影響なし予測(起票段階・反証可能)

起票の diff は台帳系(本 order・register・ECO-062 order §7 の現在地 1 行)のみ。製造時の予測(製造裁定時に凍結): bomdd-job.py の既存欄・停止語彙・exit 契約は不変
(既存 selftest 全腕が PASS のまま)/ activation-map は kit(method/ 全体コピー)に入るが `SKILLS` 定数・README 本数・C7 は不変 / self-conformance の判定不変
(job は import するだけで self-conformance を変更しない)/ C13 は新規 YAML にリンクなし。

## 3. 受入(製造時の候補)

- **V1**: 既存 selftest 全腕 PASS+新規腕(§1-3)PASS。**V2**: ECO-062/063 に対する job ビューで `required_skills` が map どおり(062= start+design-synthesis+
  verified-promotion+instrument-change / 063= start+verified-promotion)・`skills_observed` が実 receipt と一致・`skills_missing` 空。**V3**: map の各行の source が
  実在(ファイル+節)。**V4**: self-conformance・CI・diff 窓。
- 独立検査: 機械挙動(導出規則)を含むため**異系統独立検査必須**(ECO-062 §4 裁定 3 の型・Codex・CLI 直接経路を既定にする〔ECO-063 工程 2〕)。

## /preflight receipt(起動経路: **job 経由** — `bomdd-job.py ECO-064` の出力を開始 artifact として読んだ〔§0.4〕)

- 分類= 既裁定の適用実装(user 裁定 2026-09-10「起票して」)。baseline `7e90025`= **confirmed**(HEAD・作業木 clean)/ 次番 064= **confirmed**(register 末尾= 063)/
  出所契約の実在= **confirmed**(preflight/converge/calibrate の自発起動契約と C16/C17 の正規表現を実読)/ 凍結の非該当= **confirmed**(converge・calibrate の
  **本文は触れない** — map は参照するだけ)/ 同一ファイルへの進行中 ECO なし= **confirmed**(ECO-062/063 は verified)。
- 開始判定: **PROCEED**(起票まで)・override 0。製造は別裁定。

## /converge receipt(起動経路: 自発 — F1 の設計)

- **判定: 収束**(round 軌跡: 4→1→0→0)。
- DoD: ✔ 契約文を転写しない(参照付き対応表)/ ✔ 判定は台帳側の機械アンカーのみ / ✔ 正規表現の正本を 1 つにする(import)/ ✔ 停止語彙・exit 契約・既存欄は不変 /
  ✔ gate 化しない(情報欄)/ ✔ 列挙(計器パス集合)は限界を宣言する。
- round 1(新規 4 件): ①固定値(F5 型)は契約変更で腐る → YAML+source 参照へ ②C16 hard-positive を job に再実装すると二重正本 → import ③calibrate ②④は認識依存で
  機械化不能 → 対象外と宣言 ④preflight receipt の機械検出が未整備 → 見出し検出を job 側に置く(C 検査には昇格しない)。
- round 2(新規 1 件): 計器パス集合の列挙は腐る → 宣言つき限界+行の追加統制で縛る。round 3: 0 件。round 4: 0 件。
- 検証した主張: 3 契約の所在と文言(実読)/ C16 hard-positive と receipt 正規表現(self-conformance.py:1173-1176・1285・1439)/ preflight 最小表の追加統制(実読)/
  kit が method/ 全体をコピーすること(bomdd-init.py install_kit)。
- 敵対自問: 「対応表自体が第二の契約(正本)になっていないか」— 判定規則は持つが契約の意味は持たない(各行は所在参照のみ)。契約が変われば行の source が
  腐る → selftest V3 で所在の実在を測る(意味の一致は測れない= 限界)。「gate 化を先回りしていないか」— 情報欄に留める。「F2〜F6 を混ぜていないか」— 採らないに明記。
- 未収束事項: なし(製造範囲の凍結は製造裁定の入力)。

## 4. 製造裁定と製造(2026-09-11・user「ECO-064 の製造まで進めて」)

- 製造範囲(凍結)= §1 候補 1〜3(activation-map 新設・bomdd-job.py の導出 3 欄・selftest)。候補 4(EXP-20260910-01 の測定器化)は 1〜3 の帰結として
  同時に成立(追加実装なし)。allowed_paths= `method/tools/bomdd-job.py`・`method/templates/product-profile/skills/activation-map.yaml`+台帳系+検査報告。
- 起動: **job 経由**(`bomdd-job.py ECO-064` → state=filed・stop_type=NONE・write_scope=台帳系・`required_skills: null`〔製造前の第 1 弾 job〕)。
  preflight(製造着手): baseline `da41238`= confirmed(HEAD・clean)/ 出所契約の実在= confirmed(§0.2)/ self-conformance の正規表現名= confirmed
  (`CONVERGE_HARD_POSITIVES`・`CONVERGE_RECEIPT_HEAD_RE`・`C17_RECEIPT_RE`・`_strip_fences_all` を実読)/ 凍結の非該当= confirmed。PROCEED。

## 5. 製造物

- [`activation-map.yaml`](../method/templates/product-profile/skills/activation-map.yaml)(新規・43 行): `classes` 4 行(start= always → preflight /
  design-synthesis= order-hard-positive → converge / verified-promotion= ledger-status[verified] → calibrate / instrument-change= affected-refs-glob
  〔method/tools/*.py・bomdd/hooks/*・.github/workflows/*〕→ calibrate)。各行= `anchor_kind`・`anchor`・`source`(契約の所在参照)。`addition_control`(preflight
  最小表と同じ統制)・`limitation`(列挙は腐る)を宣言。kit(method/ 全体コピー)に入る。
- [`bomdd-job.py`](../method/tools/bomdd-job.py)(+174/-8 行): `MAP_PATH`(ツール自身の位置から解決= kit でも動く)/ `_load_selfconf()`(self-conformance.py を
  importlib で読み正規表現 4 つを借りる・失敗= None)/ `load_map()` / `_class_matches()`(anchor_kind 4 種・判定不能= None)/ `observed_skills()`(fence 除去後の
  receipt 見出し・preflight は `PREFLIGHT_RECEIPT_RE`)/ `project()` に `required_skills`(source= map の該当 class 列挙+判定不能 class の明示)・`skills_observed`・
  `skills_missing`(情報欄)。map 不在= `unknown(MAP_MISSING)`・import 不能= observed unknown+design-synthesis 判定不能・order 不在= observed unknown。
  既存欄・停止語彙・exit 契約・`select()` の引数処理は不変(`select()` は map と sc を 1 回だけ読む)。
- selftest 追加腕: 実 map の読取・全 class の必須キー・required_skills のスキル実在・source の所在実在(V3)/ 陽性 class(残ゲート+verified+method/tools/x.py →
  required [preflight, converge, calibrate]・observed 3・missing [])/ 陰性(fence 内 receipt 無視・start のみ → missing [preflight])/ map 不在・sc 不能・order 不在= unknown。

## 6. 受入の実測(製造者)

- **V1**= PASS(job selftest 全腕 PASS〔既存+F1〕・witness selftest PASS〔不変〕)。製造中の実測: 旧 F1 腕(「required_skills は null であるべき」)が新仕様と衝突し
  初回 FAIL → 腕を「map なし project は unknown(MAP_MISSING)」へ更新(仕様変更に伴う selftest の更新・欠陥ではない)。
- **V2**= PASS(`bomdd-job.py ECO-062 ECO-063 ECO-064 --json`):

  | ECO | state | required(source= class) | observed | missing |
  |---|---|---|---|---|
  | ECO-062 | verified | preflight・converge・calibrate(start / design-synthesis / verified-promotion / instrument-change) | 3 | [] |
  | ECO-063 | verified | preflight・calibrate(start / verified-promotion / instrument-change)| 3(converge は要求外だが起動済み)| [] |
  | ECO-064 | filed(製造前) | preflight・converge・calibrate(start / design-synthesis / instrument-change)| preflight・converge | [calibrate] |

  ECO-064 の `missing [calibrate]` は instrument-change(affected_refs に bomdd-job.py)の要求で、verified 昇格時の較正 receipt で埋まる(§7 で再測)— 情報欄が
  「これから要るもの」を先に示した初例。
- **V3**= PASS(selftest が map の 4 class の source〔preflight.md / converge.md / calibrate.md / self-conformance.py〕と required_skills の 3 スキルの実在を確認)。
- **V4**: self-conformance・CI・diff 窓・witness → §7。**独立検査**(§3・異系統必須)→ §8。

## 8. 独立検査

### 8.1 r1(2026-09-11・Codex・CLI 直接 `codex exec -s workspace-write -m gpt-5.6-sol`)= **REJECT**・所見 4+環境 1・受理側 **4/4 CONFIRMED**

- 報告: [bomdd/reports/independent-inspection-eco-064.md](reports/independent-inspection-eco-064.md)(CLI `-o` で書出し・無編集。58〜59 行目に検査官出力の文字化け
  2 行があるが該当箇所は 60〜61 行目で正しく示されている)。V1 PASS・**V2 は検査官が order を独立に読んで導出した期待値と 3 ECO とも一致**(ECO-063 に hard-positive
  なし・ECO-064 の missing [calibrate] は instrument-change 由来)・二重正本なし(import 4 つを確認・再実装なし)・unknown 5 条件で exit 0 維持・receipt 境界 9 腕期待どおり・
  停止語彙/引数処理/既存欄は d9fe305 から不変・diff 窓 PASS・案超過なし。
- 所見と受理側判定・是正(r1b):

  | 所見 | severity | 内容 | 受理側判定 | 是正 |
  |---|---|---|---|---|
  | IA-01 | high | `statuses` の型不正(int → TypeError・exit 1 / str → 文字反復で silently false / dict → キー反復で true)— exit 0 契約違反 | **CONFIRMED**(HEAD コピーで 3 型とも再現) | `validate_map()`: class の型(id・required_skills・anchor_kind・statuses・instrument_paths・anchor・source)を検査し、不正な map は `MAP_INVALID` として unknown(exit 0)。`_class_matches` も型不正= None(防御) |
  | IA-02 | medium | `fnmatch` が区切りを跨ぐ(`method/tools/sub/x.py` が一致)・`\` が OS 依存 | **CONFIRMED**(再現) | `_glob_match()`: `*` は 1 階層・`**` は複数階層・`\` を `/` に正規化(OS 非依存)。map に規約を明記 |
  | IA-03 | medium | anchor の括弧内に契約の意味(「verification 節を書くイベント」「検査器の新設・変更」)が転写されている | **CONFIRMED**(map 実読) | anchor を台帳側の事実だけに書き直し(v1.1)。契約の箇条番号は `contract_item`(注記・検査しない)へ分離 |
  | IA-04 | medium | selftest の V3 は source の `#` 断片を検査せず、断片を「不存在」にしても PASS(陰性対照なし) | **CONFIRMED**(コード読解: `split("#")[0]` のみ) | `validate_map()` が断片の literal 実在(.md= 見出し行に含む / .py= 本文に含む)を検査。source を literal 断片(`#自発起動契約`・`#CONVERGE_HARD_POSITIVES`・`#C17_SCOPE_MIN`)へ改訂。selftest に断片改変の陰性対照 |
  | IA-05 | 環境 | 検査官環境で self-conformance C14 が Git ownership 制約により UNKNOWN | 検査官環境帰属(製造者環境では C14 7/7 PASS) | 是正なし |

- 是正の陽性対照(selftest・r1): 型不正 3 型 → 判定 None+MAP_INVALID / glob 5 腕(通常・sub 不一致・`\` 正規化・docs 不一致・hooks 一致)+`**`/`*` の階層意味 /
  断片不存在 map → validate 問題あり・実 map → 0 / anchor_kind 不正・スキル不在 → MAP_INVALID。selftest PASS・V2(ECO-062/063/064)不変。
- 受理側の付随発見(製造物外): self-conformance の C14 が OS temp に `bomdd-selfconf-c14-*` を **281 件(2026-08-02 以降・約 13 MB/件)** 残置していた —
  `shutil.rmtree(ignore_errors=True)` が Windows の read-only な git object を消せず無音(fail-silent)。ECO-064 の範囲外 → improvements.md に OBS 記帳・別 ECO 候補。
  残置は当方が削除(sandbox 所有の 2 件は権限で不可・報告)。
- **r2 の受入**: r1b の selftest PASS・V4・witness→commit・CI・**独立検査 r2**(IA-01〜04 の再実測+V1〜V3 の回帰・新規所見)。

### 8.2 r2(2026-09-11・Codex・CLI 直接 workspace-write)= **REJECT**・IA-01〜04 **resolved 4/4**・新規 3(high 1 / medium 2)・受理側 **3/3 CONFIRMED**

- 引き渡しの実測: 初回実行は OS のハングで中断(ログ 2,414 行・V2 まで進行・報告未出力・リポ内変更なし・OS temp 残置なし)。r1b commit の CI(run 34499173239)は
  ハング後に確認= success。同一ブリーフで再実行し成立(所要 約 25 分)。
- 報告: [bomdd/reports/independent-inspection-eco-064-r2.md](reports/independent-inspection-eco-064-r2.md)(CLI `-o`・無編集)。IA-01〜04 は検査官が r1 の再現手順を
  再実行して全て resolved(3 型の statuses・glob 5 腕+`**`/`?` 境界・anchor の ablation〔`contract_item` を任意 object に置換しても判定不変〕・断片の literal 実在と
  陰性対照)。V1 PASS・V2 一致・unknown 5 条件 exit 0・停止語彙/引数処理を **AST で独立抽出**して d9fe305 と同一・diff 窓 PASS。
- 新規所見と受理側判定・是正(r2b):

  | 所見 | severity | 内容 | 受理側判定 | 是正 |
  |---|---|---|---|---|
  | IA-06 | medium | `source` の `;` 区切り空要素を `continue` で黙って通す | **CONFIRMED**(HEAD コピー・validate_map → []) | 空要素を問題として列挙(MAP_INVALID) |
  | IA-07 | high | unhashable な `id`(list/dict)で `seen.add` が TypeError → 通常 CLI が exit 1(r1 IA-01 と同型の契約違反) | **CONFIRMED**(TypeError 再現) | 文字列 id のみ `seen` に入れる。加えて `load_map` が `validate_map` 自体の例外を捕捉して MAP_INVALID(最終防御) |
  | IA-08 | medium | 空配列の `statuses` / `instrument_paths` が validate を通り、class を無言で無効化(fail-open) | **CONFIRMED**(validate → []・match → False) | 非空を要求(MAP_INVALID)。`_class_matches` も空配列= None(防御) |

- 陽性対照(selftest・r2): 空要素 2 形 → 問題あり / id= list・dict・None・int → 問題あり(例外なし)・list id の map → MAP_INVALID / 空配列 2 種 → 問題あり・判定 None。
  selftest PASS・V2 不変。改変 map(id=[start])を temp 複製で `load_map` → MAP_INVALID を実測。
- 検査官環境の残置: self-conformance C14 の temp 2 件(`bomdd-selfconf-c14-4e7i9d9b` / `-rhz89wcj`)は sandbox 所有で当方も削除不可(権限)— 利用者の削除に委ねる。
  C14 の temp 残置自体は製造物外の欠陥(§8.1 付随発見・OBS 記帳予定)。
- 検査官が独立に落とした枝の型(r1〜r2): 型不正・区切り・意味転写・断片検査・空要素・unhashable・空配列 — いずれも validator の**入力クラスの網羅**の穴。
  製造者 selftest は「正しい map」と「明らかに壊れた map」の 2 極しか持たず、境界(空・型違い・非文字列キー)を測っていなかった。
- **r3 の受入**: r2b の selftest PASS・V4・witness→commit・CI・**独立検査 r3**(IA-06〜08 の再実測+r1/r2 の回帰+境界クラスの追加探索)。

### 8.3 r3(2026-09-11・Codex・CLI 直接 workspace-write)= **REJECT**・IA-06〜08 **resolved 3/3**・新規 1(IA-09 medium)・受理側 **1/1 CONFIRMED**

- 報告: [bomdd/reports/independent-inspection-eco-064-r3.md](reports/independent-inspection-eco-064-r3.md)(CLI `-o`・無編集)。IA-06(空要素 3 位置)・IA-07(id 5 型+
  `validate_map` の monkeypatch で最終防御を実証)・IA-08(空配列・空文字・空白)は全て resolved。境界探索 8 腕(重複・大小文字・`../`・大文字 anchor_kind・`#` 2 つ・
  YAML alias・classes が dict・1,000 class 0.49 秒)のうち不適合は IA-09 のみ。V1 PASS・V2 同一・unknown 5 条件・停止語彙/引数処理(AST)不変・diff 窓 PASS・
  activation-map.yaml に diff なし・temp 残置 0。`self-conformance.py` はブリーフの指示どおり検査官は未実行(環境制約で C14 が測定不能・temp 残置のため)。
- 所見と受理側判定・是正(r3b):

  | 所見 | severity | 内容 | 受理側判定 | 是正 |
  |---|---|---|---|---|
  | IA-09 | medium | `required_skills` が canonical な skill ID に制限されない — `Preflight`(Windows の大小文字非区別 FS で実在判定を通過し、observed と不一致の偽 missing を生成)・`../README`(skills/ 外の実在ファイル)・重複を受理 | **CONFIRMED**(HEAD コピーで 3 形とも validate → []) | ID 文法 `[a-z0-9][a-z0-9-]*`+skills/ 直下の実ファイル名(`iterdir` の stem)との**大小文字込みの完全一致**+重複拒否(MAP_INVALID) |

- 陽性対照(selftest・r3): `Preflight`・`../README`・`../x`・重複・空白入り・`.md` 付き・空文字 → 問題あり / `preflight`・`factory-delegate` → 0。selftest PASS・V2 不変。
- 検査官が落とした枝の系譜(r1〜r3): 型不正 → 区切り → 意味転写 → 断片 → 空要素 → unhashable → 空配列 → **識別子の正規化**。すべて validator の入力クラス。
  製造者 selftest は各 round で検査官の腕を取り込み、round ごとに 1 クラス縮小している(r1: 4 → r2: 3 → r3: 1)。
- **r4 の受入**: r3b の selftest PASS・V4・witness→commit・CI・**独立検査 r4**(IA-09 の再実測+回帰・境界探索の続き)。

### 8.4 r4(2026-09-11・Codex・CLI 直接 workspace-write)= **REJECT**・IA-09 **resolved**・新規 3(medium 2 / low 1)・受理側 **3/3 CONFIRMED**

- 報告: [bomdd/reports/independent-inspection-eco-064-r4.md](reports/independent-inspection-eco-064-r4.md)(CLI `-o`・無編集)。IA-09 は 14 腕(Unicode 2 種を含む)で
  resolved・canonical 3 名は受理。境界探索 9 腕のうち不適合 3(IA-10〜12)。V1 PASS・V2 同一・unknown 5 条件・停止語彙/引数処理(AST)不変・diff 窓 PASS・temp 残置 0。
- 所見と受理側判定・是正(r4b):

  | 所見 | severity | 内容 | 受理側判定 | 是正 |
  |---|---|---|---|---|
  | IA-10 | medium | `instrument_paths` の非正規値(絶対パス・前後空白)が validate を通り class を無言で無効化。`**` 単独は全一致 | **CONFIRMED**(3 形とも再現) | 正規形の文法(リポ相対・`/` 区切り・`..` 禁止・前後空白なし・`\` 不可)+ literal 区間のない全一致 pattern を拒否(MAP_INVALID) |
  | IA-11 | medium | `statuses` の大小文字・前後空白違い(`Verified`・` verified`)が validate を通り verified class を無言で無効化 | **CONFIRMED**(2 形とも再現) | statuses を register の状態語彙(proposed/filed/decided/in-progress/implemented/applied/verified/rejected/superseded・完全一致)に限定 |
  | IA-12 | low | class の宣言順が `required_skills` の配列順に漏れる(逆順 map で順序が変わる) | **CONFIRMED**(再現) | required・該当 class 列挙・判定不能 class を辞書順で固定(配列は集合・順序に意味なしと宣言) |

- 陽性対照(selftest・r4): instrument_paths 非正規 8 形 → 拒否・正規 4 形 → 受理 / statuses 語彙外 4 形 → 拒否・語彙内 → 受理 / 逆順 map で required が同一かつ辞書順。
  selftest PASS。**V2 の値は集合として不変・配列順のみ辞書順へ変化**(ECO-062: [calibrate, converge, preflight])。
- 検査官が「新規 IA にしない」と判定した境界: `id` の文法(表示と重複検出のみに使用・誤射影を再現できず)/ `contract_item`・`limitation` の型(注記・判定入力でない)。
- **r5 の受入と範囲の限定**: r1〜r4 の各 round で「境界探索の続き」を求めた結果、round ごとに新しい入力クラス(型→区切り→意味→断片→空→unhashable→空配列→識別子→
  パス正規形→語彙→順序)が 1〜4 件ずつ出ている。**r5 は IA-10〜12 の再実測と r1〜r4 の全所見の回帰に範囲を限定し、新規クラスの探索は求めない**(探索の打ち切りは
  受理側の判断— 未探索クラスは §9 で「この受入が支持しないもの」として宣言する)。

### 8.5 r5(2026-09-11・Codex・CLI 直接 workspace-write・範囲限定= 回帰のみ)= **ACCEPT**・IA-10〜12 **resolved**・IA-01〜09 回帰 9/9・新規所見 **0**

- 報告: [bomdd/reports/independent-inspection-eco-064-r5.md](reports/independent-inspection-eco-064-r5.md)(CLI `-o`・無編集)。V1 PASS・V2(required は辞書順・
  observed/missing は集合として同一)・unknown 5 条件 exit 0・停止語彙/引数処理(AST)不変・diff 窓 PASS・activation-map.yaml 不変・temp 残置 0・新規クラス探索は
  §8.4 の限定どおり未実施。

## 9. クローズ(2026-09-11・verified)

- **受入**: V1= PASS(job selftest= 既存+F1+r1〜r4 腕・witness selftest 不変)/ V2= PASS(ECO-062: required 3= observed 3・missing [] / ECO-063: required 2・
  observed 3・missing [] / ECO-064: implemented 時点で missing [calibrate]= instrument-change の要求 — verified 昇格後は §9 末尾の再測で [])/ V3= PASS(validate_map が
  map の 4 class の source 断片と skill の実在を検査・r2 以降は検査官が独立確認)/ V4= PASS(self-conformance 全 PASS ×6・各 commit 前に exit 0 を観測・CI 6 run success:
  34495672945 / 34499173239 / 34503637641 / 34505764145 / 34508102476 +本クローズ)/ diff 窓= allowed_paths のみ(検査官 r1〜r5 各回 PASS)。
- **独立検査**: 5 round(r1 REJECT 4 → r2 REJECT 3 → r3 REJECT 1 → r4 REJECT 3 → r5 ACCEPT)。所見 12 件= **全件 CONFIRMED・全件是正・全件に陽性対照**。受理側で拒否 0。
  環境帰属 1(IA-05: 検査官環境の C14 不能)。**r5 は範囲限定**(新規クラス探索なし — 受理側の判断・§8.4)。
- diff 監査の窓: baseline `7e90025` → head `ef88211`(**窓閉鎖**)。窓内= 製造物 2 ファイル+台帳系(order・register・ECO-062 order・improvements.md)+検査報告 r1〜r4
  (r5 報告は本クローズ commit)。既存ファイル(self-conformance.py・skills/*.md・README・hooks)の diff= 0 — 影響なし予測(§4)が的中。
- **製造物の最終形**: `activation-map.yaml` v1.1(4 class・anchor は台帳側の事実のみ・source は literal 断片・contract_item は注記)/ `bomdd-job.py`(validate_map= 型・
  canonical skill ID・statuses 語彙・instrument_paths 正規形・source 断片実在・空要素/unhashable/空配列/重複の拒否・validator 自身の例外も MAP_INVALID / `_glob_match`=
  区切りを跨がない・`\` 正規化 / required・class 列挙は辞書順 / 停止語彙・exit 契約・既存欄は第 1 弾から不変)。
- **register**: `implemented → verified`・head 凍結。
- **EXP-20260910-01 の測定器**: job ビューの `skills_missing` が order の receipt 見出しから機械導出される(§1-4)。本 ECO 自身が初の測定対象: implemented 時点
  `[calibrate]`(要求は instrument-change 由来・receipt 未記入)→ 本 §9 の較正 receipt 記入後の再測= `[]`(§9 末尾)。

### 較正 receipt(/calibrate 自己適用 — trigger ①: verified 昇格+③: 計器〔validate_map・job 射影〕の新設・変更。二軸)

- 査定した主張と判定:
  1. 「独立検査の所見 12 件は全て是正された」— **observed / 適格**(r5 ACCEPT: IA-10〜12 resolved+IA-01〜09 回帰 9/9。受理側でも全件を HEAD コピーで再現→是正後の消失を selftest で実測)。
  2. 「required_skills は契約を転写せず台帳側の機械アンカーだけで導出される」— **observed / 適格**(map の anchor 4 行を検査官が r2/r3/r5 で実読・IA-03 是正後は契約語なし)。
     ただし「anchor が契約の**意味**と一致している」は読解であり機械では測れない(source の literal 実在まで)。
  3. 「validate_map は fail-closed(不正 map は unknown・exit 0)」— **observed / 条件付き適格**(r1〜r4 で検査官が 12 クラスの不正入力を落とし全て是正。**未探索クラスは残る**
     — r5 で探索を打ち切った・下記「支持しないもの」)。
  4. 「skills_observed は receipt 見出しから正しく導出される」— **observed / 適格**(3 ECO で検査官が order を独立に読んで一致・fence 内偽見出し 9 腕)。
  5. 「V4 self-conformance 全 PASS・CI 緑」— **observed / 適格**(製造者・各 commit 前 exit 0・CI headSha 照合 ×6)。検査官は環境制約(C14・ネットワーク)で unknown。
  6. 「明示起動(job の required_skills)が自発起動不発を消す」— **unknown(理由コード: 未測定 — 本 ECO は測定器を作ったのみ)**。Phase 4 の残り(EXP-20260910-01)で測る。
  7. 「skills_missing を gate 化しても安全」— **unknown(設計上対象外・検査官も r1〜r5 で「支持しない」と宣言)**。
- 検出した計器欠陥(帰属つき): **製造物 12 件**(IA-01〜04・06〜12。全て validator/射影の入力クラスの穴= 型・区切り・意味転写・断片・空要素・unhashable・空配列・識別子・
  パス正規形・語彙・順序)。**検査設備 1 件**(IA-05・検査官環境の C14 不能)。**製造物外 1 件**(self-conformance C14 の temp 残置 281 件— OBS 記帳・別 ECO 候補)。
  受理側 0 件。
- 検出力の限界: 製造者 selftest は検査官が落とした 12 クラスを取り込んだが、未探索クラス(Linux/macOS・全 YAML 型・全 glob・alias graph・資源上限・`id` 文法)は
  測っていない。契約の意味一致・運転員の行動・明示起動の効果は未測定。CI は製造者のみ確認。
- battery 行別記録:

  | Q | asked/NA | 判定 | 実測 or 読解 | 所見 |
  |---|---|---|---|---|
  | Q1 | asked | observed/適格 | 実測 | validator の自己記述(fail-closed)より狭い実装を r1〜r4 が 12 件検出 → 全て是正・陽性対照化 |
  | Q2 | asked | observed/適格 | 実測 | 各 class で known-good(正規 map)と known-bad(改変 map)を対で持つ(selftest 40 腕超) |
  | Q3 | asked | observed/適格 | 実測 | 各所見を単独腕で落とした(受理側再現 12 件・是正後に消失) |
  | Q4 | asked | observed/適格 | 実測 | selftest は実 map・実 skills/・実 self-conformance 正規表現を入力・検査官も temp 複製で実 CLI |
  | Q5 | asked | observed/適格 | 実測 | 検査官の unknown(C14・CI)を PASS に数えず製造者側で実測・出所を分けた |
  | Q6 | asked | observed/適格 | 実測 | 6 commit すべて「検査 exit 観測 → witness produce/verify(条件結合)→ commit → push → CI 照合」 |
  | Q7 | asked | observed/適格 | 実測 | 陽性対照= selftest 各腕・r5 で検査官が独立に PASS |
  | Q8 | NA | — | — | 免除機構なし(skills_missing は情報欄・gate 化していない) |
  | Q9 | asked | observed/適格 | 実測 | witness(個体+tree)・register・commit で来歴化 |
  | Q10 | asked | 宣言 | 読解 | 上記「検出力の限界」+主張 6・7 の unknown |
  | Q11 | asked | observed/適格 | 読解 | 入力クラスを列挙(12 クラス+未探索の宣言)。検査官 r4 が「新規 IA にしない」とした `id` 文法・注記欄の型は宣言つき対象外 |

- このクローズが支持しないもの: 未探索の入力クラス(Linux/macOS・全 YAML 型・全 glob 表現・alias graph・資源上限・`id` 文法)に対する fail-closed 性 /
  skills_missing の gate 化 / 明示起動の効果(EXP-20260910-01・Phase 4 残り)/ 運転員の行動(Phase 5)/ F2〜F6 / activation-map への行追加の運用(追加統制の実効)。
