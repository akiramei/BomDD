# Change Order — ECO-031(配布 kit へ表現規約〔.gitattributes〕を同梱するか)

> ECO-030 gate ①(2026-08-28)の裁定 b-2 により分離。**設計判断を含むため受入の性質が
> ECO-030(内容差ゼロの機械的正規化)と異なる**ことが分離理由。gate ① 承認待ち。

## 担当設備(equipment)

- 製造(設計者):
  - requested: `claude-opus-5`
  - resolved: `claude-opus-5`
  - ハーネス: Claude Code(Claude Agent SDK)
  - 来歴: **self-reported**
- 検査官: なし(独立検査なし)

## 0. 実測(起票根拠・2026-08-28)

- **製品リポは BomDD 側の `.gitattributes` を受け取らない。** `bomdd-init.py` は
  `shutil.copytree(METHOD_ROOT/"method", kit/"method")` で **method/ 配下のみ**を配布し、
  リポ直下の `.gitattributes`(4191538 で新設)は配布対象外。
- したがって**設置先リポでは system `core.autocrlf` の継承が防がれていない**。
  ViewTube ECO-VT-070 の実測(フレッシュクローンで 1,397/4,615 ファイルがバイト相違・
  validator が作業ツリーで通りクローンで落ちる)は、まさに**製品リポ側**で起きた事象である。
- BomDD 側の実測(ECO-030 §0)では、system=true / local=false という「ローカル設定だけで
  打ち消す」構成が実在した。同じ構成が設置先で再現しない保証はない。

### 追補実測(gate ① 前・2026-08-28)— 起票時の前提 3 件が崩れた

**① 製品リポに `.gitattributes` が無い、は誤り。** TimetableAdv は既に持っており、内容は
**BomDD と正反対**である:

```
* -text whitespace=cr-at-eol
```

導入は `c43bb5c fix(eco-002): preserve basecamp bytes across checkout`。方針は正当
(basecamp manifest がバイト厳密な成果物在庫)。CR を含む 152 blob(追跡 2129 中)は
**全件 `text=unset` で保護されており壊れていない**。
→ **上書きは ECO 裏付きの意図的方針の破壊にあたる。**

**② 宣言があれば継承は止まる、は誤り。** ViewTube は ECO-VT-070 の後に `.gitattributes` を
導入済みだが `*` の既定行を持たない(パス個別のみ)。実測:

```
.agents/skills/cad-mock/SKILL.md: text: unspecified / eol: unspecified
```

**大半のファイルが無宣言のまま**で継承は止まっていない。
→ **判定条件は「ファイルの存在」ではなく「`*` の既定行の有無」でなければならない。**

**③ 遡及の必要は小さい、は誤り。** 同一環境の BomDD 系リポの実態:

| リポ | 宣言 | 継承を止められるか |
|---|---|---|
| BomDD | `* text=auto eol=lf` + `loops/** -text` | ✔ |
| BomDD-Plm | `* text=auto eol=lf` + binary | ✔ |
| TimetableAdv | `* -text whitespace=cr-at-eol` | ✔ |
| MoviePad | `* text=auto`(**eol 未指定**) | ✘ checkout が core.eol/autocrlf 依存 |
| ViewTube | パス個別のみ(`*` なし) | ✘ 上記②の実測 |
| TimetableAdvUI / ViewPrism2 / ViewPrismUI / ViewGrid / 各 Sample | なし | ✘ |

**保護されているのは 10 リポ中 3 つ。** 2 つは不完全宣言、5 つ以上が無宣言。

**方針が 2 つ実在し、どちらも正当**であることも確定した — source 型(`* text=auto eol=lf`・
BomDD と Plm が独立に到達)と byte-exact artifact 型(`* -text`・TimetableAdv が ECO-002 で到達)。

## gate ①(製造承認)

- **承認 2026-08-28 maintainer**:「推奨で進めて。gate ① 承認、order へ反映して」
- 裁定 = §1.1 の推奨方式(下記に確定形を記す)を採択し製造へ。

## 1. 変更要求(**gate ① で方式確定済み**)

`bomdd-init` が製品リポへ表現規約を設置するか、するならどの方式か。

### 決めるべき論点(いずれも未決 — 推奨は §1.1)

1. **設置先**: 製品リポ直下 `.gitattributes` か、`bomdd/` 配下か、kit 内のみか。
   - リポ直下でなければ `core.autocrlf` 継承は防げない(gitattributes はディレクトリ単位で
     しか効かない)。目的から言えば**直下でなければ意味がない**。
2. **既存 `.gitattributes` との衝突規則**: 設置先に既存ファイルがある場合、
   上書き / 追記 / スキップして警告 / 停止 のどれか。
   - `bomdd-init` は既存 kit を**保持する**設計(冪等性・ECO-004 の凍結)。同じ思想なら
     既存ファイルには触れないのが整合するが、それでは目的(継承の遮断)が達成されない
     ケースが残る。**この矛盾が本 ECO の核心**。
3. **内容**: 製品リポには BomDD と異なる証拠クラス(`test-results/`・`bomdd/reports/`・
   capture 画像等)があり、`-text` 指定の対象が同一ではない。テンプレとして固定値を配るか、
   最小既定(`* text=auto eol=lf` + バイナリ宣言)のみ配って残りは設置先の裁定にするか。
4. **既設リポへの遡及**: 既に設置済みのリポへどう届けるか(kit 再設置は各製品リポの裁定)。

### 1.1 確定方式(gate ① 採択・2026-08-28)

**論点 1(設置先)= リポ直下**。`bomdd/` 配下では `*` がリポ全体に効かないため、目的
(system autocrlf の継承遮断)を達成できない。

**論点 2(衝突規則)= 既存があれば触れない。ただし判定条件は「`*` の既定行の有無」**。

- 既存ファイルを上書きしない — 追補実測①のとおり、上書きは ECO 裏付きの意図的方針の破壊に
  あたる(TimetableAdv の byte-exact 保護)。
- **「ファイルが存在するか」で判定しない**(追補実測②の精密化)。存在判定では MoviePad
  (`* text=auto` の eol 未指定)と ViewTube(`*` 行なし)が素通りする。
- 判定は 3 状態にして出力へ出す:
  - `installed` — 既存なし。既定を設置した。
  - `preexisting` — 既存に `*` の既定行があり `eol` または `-text` が定まっている。触れない。
  - `incomplete` — 既存はあるが `*` の既定行がない、または `*` はあるが eol/`-text` が
    未指定。**触れないが警告する**(「表現規約が不完全: `*` の既定行を確認してください」)。
- **停止はしない**(§13「止めるのは作業でなく信頼済み状態への昇格」— 設置は開発着手であって
  昇格ではない)。

**論点 3(内容)= `* text=auto eol=lf` + 既知バイナリ + 工程証拠パスの `-text` carve-out +
逃げ道の明記**。

- 既定は source 型。根拠: BomDD・BomDD-Plm の 2 リポが独立にこの形へ到達しており、
  新規プロジェクト開始時点で byte-exact 成果物の要求が判明していることは稀。
- **carve-out は `bomdd-init` 自身が作る工程証拠パスに限る**(BomDD の `loops/** -text` と同型)。
  製品固有の証拠クラスまで列挙しない — **列挙は腐る**(§13 原則⑥)。
- **逃げ道を設置ファイルのコメントへ明記する**: 「成果物がバイト厳密(取得物・在庫・capture 等)
  なら `* -text` へ切り替える。**切り替えは早いほど安い**(既に正規化されたバイトは戻せない)」。
  これは方針が 2 つ実在するという実測(追補実測③)への対応であり、**既定の誤りを不可逆に
  しないための出口**である。

**論点 4(既設リポへの遡及)= 各リポの裁定。ただし本 order の実測表を判断材料として残す**。

- `bomdd-init` は既存 kit を保持して return するため(`bomdd-init.py:144-150`)、配布仕様の
  変更は既設リポへ届かない。遡及は各リポの ECO で行う。
- 追補実測③の表(保護 3 / 不完全 2 / 無宣言 5+)を各リポの判断材料として本 order に残す。

**来歴の記録**: 設置判定(`installed` / `preexisting` / `incomplete`)を `bomdd.lock` の
adapter 節へ記録する。**沈黙と健全を区別する**ため。

## スコープ外(宣言済み境界)

- **BomDD 側 6 件の CRLF 正規化**: ECO-030 の製造対象。本 ECO では扱わない。
- **既設製品リポへの適用**: 各製品リポの裁定。本 ECO は `bomdd-init` の配布仕様のみ。
- **`self-conformance` への設置検査(④)の追加**: 本 ECO では採らない
  (playbook §8.5 — 様式化・validator 強制は実測後に判断)。

## 2. 影響なし予測(反証可能・gate ① で方式確定のため製造前に凍結・2026-08-28)

- diff は `method/tools/bomdd-init.py` + 台帳系のみ。**他ファイルは diff ゼロ**
  (設置内容は生成器が書き出すためテンプレファイルを新設しない — 新設する場合は本予測を修正する)。
- **C4 は判定不変**: `c4_scaffold()` の検査は絶対パス漏れ・lock/manifest 整合・AGENTS.md
  参照スキルの実在・生成 YAML の厳格パース。`.gitattributes` の追加はいずれにも触れない。
  ただし kit-manifest は生成物の増加を反映するため**件数は変わりうる**(整合判定は不変)。
- **C7 は判定不変**(`SKILLS` 実数に触れない)。**C13 は判定不変**(設置ファイルに
  markdown リンクを置かない)。
- **既存 8+1 スキル・既存テンプレの内容は不変**。
- **既設製品リポへは非波及**(`bomdd-init.py:144-150` により既存 kit は保持されて return)。
- **既存 `.gitattributes` を持つ設置先を破壊しない**(論点 2 の衝突規則)。

## 3. 較正と受入(起票時凍結・2026-08-28)

本 ECO は**予防ゲートの新設ではなく生成器の機能追加**であり、赤プローブが取れる
(現行 `bomdd-init` の生成物に `.gitattributes` が無い)。加えて衝突規則は分岐を持つため、
**分岐ごとに対照を置く**(§4.4「兼ねる統制は較正 2 系統」の適用形 — 分岐が複数なら対照も複数)。

- **較正(赤・是正面のプローブ)**:
  - **CAL-0**: 現行 `bomdd-init` で scaffold した製品リポに `.gitattributes` が**存在しない**
    ことを実測(是正前不合格)。
- **較正(陽性対照・衝突規則の 3 分岐がそれぞれ固有の理由で発火する)**:
  - **CAL-1** `installed`: 既存なしの設置先で設置され、`git check-attr` が `text: auto` /
    `eol: lf` を返す。
  - **CAL-2** `preexisting`: 既存に `* -text` を置いた設置先で**上書きされず**、判定が
    `preexisting` になる(TimetableAdv 型の保護)。
  - **CAL-3** `incomplete`: 既存に `* text=auto`(eol 未指定)だけを置いた設置先で
    **上書きされず**、判定が `incomplete` になり警告が出る(MoviePad 型)。加えて
    `*` 行を持たない既存(ViewTube 型)でも `incomplete` になる。
    **CAL-3 が `preexisting` になったら判定条件が存在判定へ退化している** — 追補実測②の再発。
- 受入:
  - **V1**: CAL-1〜CAL-3 の 3 分岐がすべて宣言どおりに動く。
  - **V2**: 設置判定が `bomdd.lock` の adapter 節へ記録される(3 値のいずれか)。
  - **V3**: `self-conformance` 全検査 PASS(C4 scaffold 煙試験込み)。
  - **V4**: push 後 CI 緑(4 値判定・対象 revision を照合する)。
  - **V5**: diff が影響なし予測の窓内。

## 4. CI 実測(push 後に追記)

- 対象 revision:
- run 識別子:
- 結論(PASS / FAIL / UNKNOWN / OVERRIDDEN):
- 観測日時 / 観測主体:
