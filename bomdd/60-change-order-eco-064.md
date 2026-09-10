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
