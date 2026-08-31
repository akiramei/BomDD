# Change Order — ECO-040(CI/ローカル環境前提の宣言・環境個体の刻印・ubuntu C9 の 1 回実測)

> 裁定: user 2026-09-01「③を calibrate の第 2 回題材として開始してください。主張を宣言面・
> 実行面・OS 間再現性・将来ドリフトに分解し…」+ 掃引結果への gate 裁定
> 「X+Y+Z を採択します」(6 条件つき — 下記 gate ① 節)。
> EXP-20260831-04(calibrate 効果測定)の第 2 回観測。

## 担当設備(equipment)

- 査定・製造:
  - requested: `claude-fable-5`
  - resolved: `claude-fable-5`
  - ハーネス: Claude Code(Claude Agent SDK)
  - 来歴: **self-reported**
- 検査官: 外部レビュア(匿名・user 経由)— 題材 ③ の先行を推奨・裁定権限なし

## 0. 実測(掃引 ③ の要旨・2026-08-31〜09-01)

主張「CI 緑 = self-conformance がローカルと同じ意味で成立」を 4 面へ分解して査定:

- **S1 宣言面 = observed/適格**: 単一入口が CI(workflow:24)とローカル(AGENTS 規律 2)で同一。
- **S2 実行面 = observed/条件付き適格**: git identity は計器が内在化(ECO-020・
  `self-conformance.py:257-266` 理由コメントつき)。測っていない次元= 版の非対称
  (CI= Python 3.12.14〔run 33403694106 ログ採取〕/ ローカル= 3.13.1・PyYAML は CI unpinned)。
- **S3 OS 間 = fast: observed/条件付き適格(両 OS 毎 push 緑・ただし OS 間で判定が分かれる
  known-bad の較正なし)/ dotnet: unknown(理由コード: 未実行 — C9 は ubuntu で一度も測定なし)**。
  windows-only は ECO-006 order 裁定 (c) に**構成として宣言済み**(`60-change-order-eco-006.md:23`)
  だが**原裁定に理由の記録がない** — 無宣言境界ではなく「宣言済み・根拠未記録」。
- **S4 将来ドリフト = unknown(理由コード: 観測手段なし)**: runner image(`*-latest`)・
  PyYAML・python patch・dotnet minor がすべて floating。赤化するドリフトは検出されるが、
  沈黙的な判定意味論の変化には検出手段がない(版の刻印なし)。

所見分類(欠陥件数へ統合しない): **capability defect 0 / boundary 2(B1 版非対称・
B2 刻印なし)/ declaration 2(D1 dotnet=windows 根拠未記録・D2 shallow 一般則未宣言)/
unknown 3(C9 非 windows= 未実行・沈黙的ドリフト= 観測手段なし・OS/版間弁別= 未較正)**。

## gate ①(製造承認)

**承認 2026-09-01 maintainer「X+Y+Z を採択します」** — 6 条件:

1. **X**: D1/D2 の宣言を追加。ただし ECO-006 に記録されていない windows-only の歴史的理由を
   **推測で補完しない** — 「構成は裁定済みだが原裁定の理由は記録されていない」という事実を
   そのまま残す。
2. **Y**: pin ではなく**環境個体の刻印** — Python/PyYAML/.NET SDK/runner 等、判定に関係する
   実版を証拠から追跡可能に。目的はドリフト防止でなく**ドリフトの観測可能化**。
3. **Z**: ubuntu で dotnet/C9 を **1 回実測**。結果は当該 revision・当該 runner 個体についてのみ
   有効とし、1 回の緑を OS 横断再現性の一般証明へ**昇格させない**。常設化は実測後の別裁定。
4. **B1 は修理しない**: 現在両環境緑という観測と、版間判定同値性が未較正であることを併記。
5. **EXP-20260831-04 は capability defect= 0 をそのまま記録** — boundary/declaration/unknown を
   欠陥件数へ統合しない。
6. **unknown は「未実行」と「観測手段なし」を理由コード上で区別して保持**。

## 1. 変更要求(製造対象)

- **(X)** workflow 冒頭へ境界宣言 2 点(D1= 構成裁定済み・理由未記録の事実記録 / D2= shallow
  前提と「履歴依存検査は fetch-depth 裁定を先に」)+ self-conformance docstring へ
  「環境前提の宣言」節(identity 内在化・shallow・版非前提と B1 併記・刻印の目的)。
- **(Y)** `env_imprint()` 新設 — `[env]` 行に python/PyYAML/os/runner(ImageOS/ImageVersion・
  ローカルは `runner local`)/ dotnet-sdk(--dotnet 時のみ・測定不能は明示)を毎回刻印。
- **(Z)** dotnet job を一時的に matrix(windows+ubuntu)へ変異し、本 ECO の fix push の CI で
  ubuntu C9 を 1 回実測。**accept コミットで windows のみへ復帰**(常設化しない)。
  runner 個体の証拠は (Y) の刻印が CI ログに残す。

## 2. 影響なし予測(反証可能・製造前に凍結)

- diff は `.github/workflows/self-conformance.yml` / `method/tools/self-conformance.py` /
  `method/improvements.md`(gate 裁定 5・6 の記帳)+台帳系のみ。
- 全 16 検査+C9 の**判定ロジックは不変**(追加は出力行 `[env]` と宣言のみ)。
- fix push の CI は一時的に 4 job(fast×2+dotnet×2)。**ubuntu dotnet の結論は未知** —
  緑でも赤でも当該 revision の実測として §5 に記録する(赤なら持ち越さず accept の復帰で解消し、
  結果は所見として残す)。
- C16 は本 order を required と判定する見込み — receipt を下記に埋め込む。

## 3. 受入(起票時凍結)

- **V1**: `[env]` 刻印がローカル(runner local)と CI(ImageOS/ImageVersion)の両方の証拠に
  出現し、判定に関係する実版が追跡可能。
- **V2**: fast 全検査 PASS・既存判定不変(ローカル+CI)。
- **V3(Z)**: ubuntu dotnet job が 1 回実行され、結論(緑/赤とも)と runner 個体が記録される。
- **V4**: accept で dotnet job が windows のみへ復帰し、復帰後 CI 緑。
- **V5**: diff 窓が §2 の範囲に収まる。
- **V6**: 較正 receipt(二軸・unknown の理由コード区別)を埋め込む。

## /converge receipt(本製造の設計に適用 — 起動経路: 人間裁定〔題材指定+X/Y/Z 採択〕)

- **判定: 収束**(round 軌跡: 2→0→0)。
- 周回数と新規指摘: round 1 = 2 件(Z の実装方式を workflow_dispatch 別経路でなく
  「一時 matrix 変異+accept 復帰」に確定 — 当該 revision 限定の測定として最も自然で、
  Y の刻印が runner 個体の証拠を兼ねる / runner 識別は hosted runner の ImageOS/ImageVersion
  環境変数で取得可能なことを確認)/ round 2 = 0 / round 3 = 0。
- 検証した主張(要点): workflow 実文・ECO-006 order:23 実文 / CI 実版= run 33403694106 ログ /
  ローカル実版= 直接実測(Python 3.13.1・PyYAML 6.0.3・SDK 10.0.400・global.json 不在)/
  identity 内在化= `self-conformance.py:257-266` 実読。
- 未収束事項: なし。

## 4. 製造の実測(2026-09-01)

- diff 監査の窓: baseline `a4e9322`(起票直前 HEAD・起票+製造は同一窓)→ head は受入時に確定。
- (X)(Y)(Z) を §1 のとおり適用。EXP-20260831-04 第 2 回観測を improvements.md へ記帳
  (裁定 5・6 の様式 — capability defect 0 のまま・unknown の理由コード区別)。
- 実測結果は §5 に追記する。

## 5. CI 実測(V1〜V4)

- fix push 対象 revision: `b56dbd6`(**ローカル HEAD と一致を確認**)
- run 識別子: 33413482874 — **全 4 job success**(fast ubuntu / fast windows /
  dotnet windows / **dotnet ubuntu**)
- **V1 PASS(刻印)**: ローカル= `[env] python 3.13.1・PyYAML 6.0.3・os Windows-11・
  runner local` / CI ubuntu dotnet= `[env] python 3.12.14・PyYAML 6.0.3・
  os Linux-6.17.0-1022-azure・runner ubuntu24/20260823.283.1・dotnet-sdk 10.0.400` —
  判定に関係する実版が証拠(CI ログ・ローカル出力)から追跡可能。
- **V3 PASS(Z の 1 回実測)**: ubuntu の C9 = **全行 PASS**(計器較正 5 腕成立・
  母集団突合 4⇔4・4 スイート全て manifest 一致・期待赤 4 件一致・**identity 突合 4 件** —
  xunit の失敗 Message は Linux でも同一 identity に構造化された)。
  **本結果の有効範囲(gate 裁定 3)**: revision `b56dbd6`・runner 個体
  `ubuntu24/20260823.283.1`・SDK 10.0.400 についてのみ。**1 回の緑を OS 横断再現性の
  一般証明へ昇格させない**。掃引 ③ の unknown「C9 の非 windows 再現性(未実行)」は
  observed / **条件付き適格**〔範囲= 当該 revision・当該個体〕へ遷移。
- **V2 PASS**: fast 全検査は両 OS・ローカルとも PASS・既存判定不変。
- V4(復帰後 CI)は §6 で確定。

## 6. クローズ

- **V4 PASS**: matrix 復帰後の CI(run 33415086488 @`c7ac101`)= 3 job 構成(dotnet= windows
  のみ)へ戻って全緑。headSha 照合済み。
- diff 監査の窓: baseline `a4e9322` → head `c7ac101`(**窓閉鎖** — Z の一時変異と復帰を含む)。
  窓内は workflow / self-conformance.py / improvements.md+台帳系のみ — 影響なし予測が的中。
- 受入: V1(刻印・両環境)/ V2(fast 全 PASS)/ V3(Z 実測・範囲限定つき)/ V4(復帰後緑)/
  V5(diff 窓)すべて成立。
- **掃引 ③ 所見の最終処置**: D1/D2= 宣言で閉鎖(理由の推測補完なし)/ B2= 刻印で観測可能化
  (pin なし)/ B1= 修理しない(裁定 4 — 併記のみ)/ unknown「C9 非 windows」= observed/
  条件付き適格へ遷移(範囲= revision `b56dbd6`・runner `ubuntu24/20260823.283.1`・SDK 10.0.400)。
- このクローズが支持しないもの: OS 横断再現性の**一般証明**(1 回の緑 — 裁定 3)/ 沈黙的
  ドリフトの非発生(unknown・理由コード= 観測手段なし。刻印により事後突合のみ可能)/
  版間判定同値性(unknown・理由コード= 未較正 — B1)/ dotnet ubuntu の常設化(別裁定)。

### V6 — 較正 receipt(二軸・unknown 理由コード区別 — gate 裁定 6)

- 査定した主張と判定:
  1. 「判定に関係する環境個体は証拠から追跡可能」— **observed / 適格**(V1・両環境の刻印実物)。
  2. 「C9 は ubuntu でも同一判定」— **observed / 条件付き適格**〔範囲= 当該 revision・当該
     runner 個体・N=1。一般証明ではない — 裁定 3〕。
  3. 「沈黙的ドリフトは起きていない」— **unknown(理由コード: 観測手段なし)** — 刻印は
     事後突合の手段であり非発生の証明ではない。資格判定なし・昇格根拠に使用不可。
  4. 「版非対称でも判定は同値」— **unknown(理由コード: 未較正)** — 両環境緑の一致観測のみ
     (B1・修理しない裁定)。
- 検出した計器欠陥と帰属: なし(本製造弧の所見なし)。
- 検出力の限界: 刻印は判定時点のスナップショットであり依存の推移的版(pip 依存ツリー)までは
  刻印しない / runner 実体の直接観測は不可(リポ外アンカー)。
