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

## 1. 変更要求(設計判断を含む — gate ① で方式ごと裁定する)

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

### 1.1 推奨方式(たたき台 — gate ① で採否)

- 製品リポ直下に **最小既定のみ**を設置する: `* text=auto eol=lf` + 既知バイナリ宣言。
  証拠クラスの `-text` は**設置先の裁定**(列挙は腐る・§13 原則⑥)。
- **既存ファイルがある場合は触れず、`bomdd-init` の出力に「既存の .gitattributes を検出。
  表現規約の宣言状況を確認してください」と表示して続行**(停止しない)。
  - 根拠: 測定不能・判断不能を理由に**作業を止めない**(§13「止めるのは作業でなく
    信頼済み状態への昇格」)。設置は開発着手であって昇格ではない。
- 設置したか否かを `bomdd.lock` / `kit-manifest.json` の来歴へ記録する
  (`gitattributes: installed | preexisting | skipped`)。**沈黙と健全を区別する**。

## スコープ外(宣言済み境界)

- **BomDD 側 6 件の CRLF 正規化**: ECO-030 の製造対象。本 ECO では扱わない。
- **既設製品リポへの適用**: 各製品リポの裁定。本 ECO は `bomdd-init` の配布仕様のみ。
- **`self-conformance` への設置検査(④)の追加**: 本 ECO では採らない
  (playbook §8.5 — 様式化・validator 強制は実測後に判断)。

## 2. 影響なし予測(製造前 — gate ① 承認後に凍結する)

*本 ECO は方式が未決のため、影響なし予測は gate ① で方式が確定してから凍結する。*
*(未決のまま予測を書くと反証不能になる — 予測は方式に対して立てるものであるため。)*

## 3. 較正と受入(gate ① 承認後に凍結する)

*方式確定後に凍結。最低限、以下は方式によらず必要になる見込み:*

- 較正(赤): 現行 `bomdd-init` で scaffold した製品リポに `.gitattributes` が**存在しない**こと。
- V1: scaffold 後の製品リポで `git check-attr text eol -- <任意のテキストファイル>` が
  `text: auto` / `eol: lf` を返す。
- V2: 既存 `.gitattributes` を置いた設置先で、衝突規則が宣言どおりに動く(上書きしない等)。
- V3: `self-conformance` 全 PASS(C4 scaffold 煙試験込み)。
- V4: push 後 CI 緑(4 値判定)。

## 4. CI 実測(push 後に追記)

- 対象 revision:
- run 識別子:
- 結論(PASS / FAIL / UNKNOWN / OVERRIDDEN):
- 観測日時 / 観測主体:
