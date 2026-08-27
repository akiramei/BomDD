# Change Order — ECO-030(kit へバイトコピーで配布される 6 ファイルが FULL-CRLF)

> playbook §13「記録規約 第 1 層」③(表現の規約は `.gitattributes` で宣言する)の自己適用で
> 新設した `.gitattributes`(4191538)が、宣言時点で既に不適合な追跡 blob を 6 件残している。
> 6 件はいずれも **kit 経由で製品リポへバイトコピーされる**ため、ハーネス(AGENTS.md 規律 1)に
> あたり起票なしに触れない。gate ① 承認待ち。

## 担当設備(equipment)

- 製造(設計者):
  - requested: `claude-opus-5`
  - resolved: `claude-opus-5`
  - ハーネス: Claude Code(Claude Agent SDK)
  - 来歴: **self-reported**(ハーネス表示。observed な機械記録は取得していない)
- 検査官: なし(独立検査なし・単独作業)
- 注意: 本 ECO の起票・実測は同一設備が実施している。独立検査は入っていない。

## 0. 実測(起票根拠・2026-08-28)

すべて `git grep -I -l -P '\r' HEAD`(テキスト復号を挟まないバイト検査)と
`git ls-files --eol` による。

- `core.autocrlf` は **system=true / local=false**。local 設定はクローンへ引き継がれないため、
  フレッシュクローンは system 既定を継承する(ViewTube ECO-VT-070 で 1,397/4,615 ファイルが
  バイト相違し validator が作業ツリーで通りクローンで落ちた構成と同じ)。
- CR を含む追跡 blob は **70 件**。内訳= `loops/` 配下の取得物 63 件(`.gitattributes` で
  `-text` 指定・保存対象)/ 素の欠陥 7 件。うち `docs/terminology.md` は是正済み(54e1209)。
- **残 6 件はすべて FULL-CRLF**(LF 数 = CRLF 数・lone CR ゼロ):

  | path | LF/CRLF | 配布経路 |
  |---|---|---|
  | `method/tools/ui-cad-gate.py` | 293/293 | kit copytree |
  | `method/tools/ui-extract.py` | 323/323 | kit copytree |
  | `method/templates/36-ui-dictionary.yaml` | 52/52 | kit copytree + `bomdd/` へ copy2 |
  | `method/templates/37-ui-rulings.yaml` | 100/100 | kit copytree + `bomdd/` へ copy2 |
  | `method/prompts/ui-apply-rulings-to-bom.md` | 34/34 | kit copytree |
  | `method/prompts/ui-raw-to-candidates.md` | 41/41 | kit copytree |

- **配布経路の実測**(`method/tools/bomdd-init.py`):
  - L152 `shutil.copytree(METHOD_ROOT/"method", kit/"method", ignore=("__pycache__","*.pyc"))`
    — **method/ 全体がバイトコピー**で kit に入る(`tools/` `prompts/` 込み)。
  - L155-157 直後に `manifest[path] = sha256(f.read_bytes())` — **CRLF のバイト列がそのまま
    製品リポの `kit-manifest.json` へ焼き付く**。
  - L247-249 `PHASE_TEMPLATE_GLOBS`(`[0-9][0-9]-*.yaml` を含む)→ `shutil.copy2` で
    製品リポの `bomdd/` へ。36/37 はこの経路にも乗る。
  - `render()`(`write_text(..., newline="\n")` で LF を明示)は**通らない** — 起票前の仮説
    「render 経由なので CRLF は落ちる」は**実測で反証**した。
- **副次実測**: `git add --renormalize` による決定的測定で `loops/metrics.csv` /
  `metrics-v2.csv` が index=LF・作業ツリー=CRLF に乖離していた(stat キャッシュに隠れ
  `git status` はクリーンを表示)。EOL のみの差であることをバイト比較で確認し復元済み
  (4191538)。**「作業ツリーで通りクローンで落ちる」(ECO-VT-070 D10-006)の同型が
  本リポにも実在していた。**

## 1. 変更要求

### (a) 6 件を LF へ正規化【是正】

バイト I/O(`read_bytes` → `replace(b"\r\n", b"\n")` → `write_bytes`)で行い、
**内容不変を assert で確認**する(改行除去後のバイト列が一致すること・lone CR ゼロ)。
`git add --renormalize` に委ねず明示的に書き換えるのは、作業ツリーと index の両方を
一致させるため(副次実測の乖離が再発しない形)。

各ファイルは**全行差分**になる。これは意図した表現正規化であり、
**内容変更と同一コミットに混ぜない**(harness ECO-024 の 756 行 CRLF 化が
diff 監査・窓監査を同時に無効化した失敗を、正規化する側で繰り返さない)。

### (b) kit への `.gitattributes` 同梱の要否【**ECO-031 へ分離** — 本 ECO のスコープ外】

製品リポ側にも表現規約を効かせるか。実施する場合 `bomdd-init.py` の変更を伴う。

- 採る理由: 製品リポは BomDD 側の `.gitattributes` を受け取らないため、設置先で同じ
  system autocrlf 継承が起きる。ECO-VT-070 は**製品リポ側**で起きた事象である。
- 採らない理由: 設置先リポの既存 `.gitattributes` との衝突・上書き規則を決める必要があり、
  `bomdd-init` の冪等性(既存 kit は保持する設計)と整合を取る設計が要る。
- **裁定(gate ①・2026-08-28 maintainer)= b-2「別 ECO に切る」を採択。**
  (b) は **ECO-031** へ分離し、本 ECO の製造対象は **(a) のみ**とする。
  理由: (a) は内容差ゼロの機械的正規化で受入が明快だが、(b) は `bomdd-init` の冪等性と
  設置先の既存 `.gitattributes` との衝突規則という**設計判断**を含み、受入の性質が違う。
  混ぜると diff 監査の窓が「表現正規化のみ」と言えなくなり V5 が成立しない。

## gate ①(製造承認)

- **承認 2026-08-28 maintainer**:「gate ① 承認。b-2 で別 ECO に切る。push して製造に進んで」
- 裁定 2 点 = ①製造承認(a: 6 件の LF 正規化)②(b) は ECO-031 へ分離。
- 本 order の受入 V1〜V5 は起票時に凍結済み・変更なし。

## スコープ外(宣言済み境界 — 本 ECO で明文化して残す)

- **(b) kit への `.gitattributes` 同梱**: gate ① 裁定により **ECO-031** へ分離。

- **`loops/` 配下の取得物 63 件**: `.gitattributes` の `loops/** -text` で保存対象。
  改行は観測データの一部であり正規化は事後復元不可(playbook §13「不可逆観測データの
  保存義務は rule of three を待たない」)。**是正しない**。
- **既設製品リポの kit 更新**: 各製品リポの裁定。本 ECO は BomDD 側正本のみを扱う。
  既設リポは自分の manifest と一致したままなので **TAMPERED にはならない**
  (`kit-freshness` の STALE は commit 距離で測り内容ハッシュでは測らない — advisory)。
- **`self-conformance` への `.gitattributes` 存在検査(④)の追加**: 本 ECO では採らない。
  playbook §8.5「様式化・validator 強制は採らない — 実測で効いたのは事前束縛そのもの」に従い、
  必要が実測されてから判断する。

## 2. 影響なし予測(反証可能・製造前に凍結)

- diff は上記 6 ファイル + 台帳系(register・本 order)のみ。**他ファイルは diff ゼロ**。
- 6 件はいずれも**内容差ゼロ**(EOL のみ)。全行差分になるが挙動は不変
  — Python の字句解析・PyYAML・Markdown いずれも CRLF/LF 非依存。
- **C1〜C15 の判定不変**。特に C4(scaffold 煙試験・lock/manifest 整合)は scaffold 時に
  manifest を再生成するため、ソース側のバイトが変わっても整合は保たれる。
- 既存製品リポへは **kit 再設置まで非波及**。
- `ui-cad-gate.py` / `ui-extract.py` の実行結果不変。

## 3. 較正と受入(起票時凍結)

- **較正(赤・2026-08-28 実測済み)**: 現 HEAD(54e1209)で
  `git grep -I -l -P '\r' HEAD -- method/` が **6 件**を返す。
- 受入:
  - **V1**: 是正後、同コマンドが **0 件**。
  - **V2**: 6 件それぞれについて、是正前 blob と是正後の内容が**改行除去後にバイト一致**
    (内容差ゼロ)。かつ `git ls-files --eol` が全件 `i/lf w/lf` を返す。
  - **V3**: `self-conformance` 全 PASS(C4 scaffold 煙試験込み・exit 0)。
  - **V4**: push 後 CI 緑(4 値判定 — 対象 revision と結論を本 order へ実測追記。ECO-020 規律)。
  - **V5**: 是正コミットが**表現正規化のみ**であることを diff 監査で確認
    (窓内が affected_refs + 台帳系のみ・内容行の変更ゼロ)。

## 4. 製造と受入実測(2026-08-28)

### 製造

- diff 監査の窓: baseline `b8ad483`(gate ① 記録コミット= 是正開始直前)→ head は本節末に追記。
- 方式: バイト I/O — blob を bytes で読み、CRLF を LF へ置換して bytes で書き戻す
  (テキスト復号を挟まない)。
  書き換え前に ①作業ツリーと `HEAD:` blob のバイト一致 ②lone CR ゼロ を assert し、
  いずれかが崩れたら中止する形で実行した。

| ファイル | CRLF | bytes 前 → 後 | 差 = CRLF 数 |
|---|---:|---|---|
| `method/tools/ui-cad-gate.py` | 293 | 13402 → 13109 | ✔ |
| `method/tools/ui-extract.py` | 323 | 12817 → 12494 | ✔ |
| `method/templates/36-ui-dictionary.yaml` | 52 | 2704 → 2652 | ✔ |
| `method/templates/37-ui-rulings.yaml` | 100 | 5634 → 5534 | ✔ |
| `method/prompts/ui-apply-rulings-to-bom.md` | 34 | 2154 → 2120 | ✔ |
| `method/prompts/ui-raw-to-candidates.md` | 41 | 3088 → 3047 | ✔ |

**バイト差が全件 CRLF 数と厳密一致** — 差が改行のみであることの機械的裏づけ。

### 受入

- **V1 PASS**: `method/` 配下で CR を含むファイル **0 件**(較正の赤 6 件 → 0 件)。
- **V2 PASS**: 全 6 件が `git ls-files --eol` で `i/lf w/lf`。内容不変は上表の
  バイト差一致 + 書き換え時の assert(改行除去後のバイト列一致)で確認。
- **V3 PASS**: `self-conformance` 全 17 検査 PASS・FAIL 0 件・exit 0。
  影響なし予測どおり **C4 は不変**:
  `[C4] PASS scaffold 煙試験(絶対パス漏れ 0 件・lock/manifest 整合 True・AGENTS.md 参照スキル 16 件・生成 YAML 厳格パース 全数)`
  — scaffold 時に manifest を再生成するため、ソース側バイトが変わっても整合が保たれることの実測。
- **V5 PASS**: 変更ファイルは affected_refs 6 件のみ、他は diff ゼロ
  (影響なし予測「他ファイルは diff ゼロ」が的中)。全行差分だが内容行の変更はゼロ。
- **V4**: 下記。

### 計器の運用欠陥(本 ECO 内で自己検出・記録)

受入証拠を取る実行を `| tail -8` でパイプしたため、**出力ファイルに C4 の行が残らなかった**
(集約判定 exit 0 は残ったが、order に「C4 込み」と書く根拠となる行単位の証拠が欠けた)。
全文キャプチャで再実行して取得。**同型が本セッション内で 2 度目** — `gh run watch` を
`tail` へ繋いで `$?` が tail の終了コードになり、CI の結論の証拠にならなかった件と同じ
(そちらは `gh run view --json conclusion` で取り直し)。
**証拠を取る実行はパイプしない**(切り詰めと終了コードの両方を失う)。

**3 例目(本 order 自身・commit 07e6db6 で混入 → 6e 系で是正)**: 本節の「方式」行に
改行の**エスケープ列を書いたつもりで実バイトの CR/LF を書いてしまい**、`.gitattributes` の
正規化(CRLF→LF)が 1 行を 3 行へ割った — **表現の正規化が、正規化について書いた文の内容を
壊した**。検出は `git add` の警告(`CRLF will be replaced by LF the next time Git touches it`)、
すなわち**本 ECO 系列で新設した宣言そのものが設置者の眼前で捕捉**した(§13 遮断方向の規則の
実測 — 誤りは是正コスト最小点で顕在化した)。是正= 当該行からエスケープ列を除去し散文で記述。
教訓: **改行について書く文書は、改行そのものを本文へ埋め込まない**(表示目的でも実バイトを
置かない)。本セッション内の同型 3 例(パイプ 2 件+本件)は、いずれも「計器・記録の側」で
起きており製造対象には及んでいない。

## 5. CI 実測(V4)

- 対象 revision: `4235be4c2c7c2398b910a57a948a077a4c6b0cd9`(**ローカル HEAD と一致を確認**)
- 規則版: workflow `self-conformance`(リポ内定義= 測定器。FINDINGS §11.6 の訂正どおり
  信頼アンカーではない)
- run 識別子: 33110813052 — https://github.com/akiramei/BomDD/actions/runs/33110813052
- 結論: **PASS**(`status: completed` / `conclusion: success`)
- 観測日時 / 観測主体: 2026-08-28 / 本 ECO の担当設備(§担当設備)
- UNKNOWN の理由コード: 該当なし(別 commit の結果でない・規則版一致・結果は当該 push のもの)

## 6. クローズ

- diff 監査の窓: baseline `b8ad483` → head `4235be4`(**窓閉鎖**)。
  窓内は affected_refs 6 件 + 台帳系(本 order・register)のみ — 影響なし予測が的中。
- 受入: V1 / V2 / V3 / V4 / V5 すべて PASS。
- **恒久回帰**: `.gitattributes` の `* text=auto eol=lf`(4191538)が本欠陥クラスの再発を
  checkout/add 経路で遮断する。本 ECO 内で**その遮断が実際に作動した実測**を得た
  (§4「計器の運用欠陥」3 例目 — 新設した宣言が order 自身の混入 CR を `git add` の
  警告として捕捉)。§13「ECO による是正は恒久回帰と、その検出器が実際に作動することを
  示す陽性対照を収載してからクローズする」の充足はこの実測をもって行う。
  **なお `self-conformance` への存在検査(④)追加は採らない**(§8.5 — 様式化・validator
  強制は実測後に判断。宣言済み境界のとおり)。
- 残: kit への `.gitattributes` 同梱は **ECO-031**(filed・方式未決)。
