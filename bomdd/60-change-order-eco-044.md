# Change Order — ECO-044(process-core 治具の検出力限界 — 一次記録への参照面の追加)

> 裁定: user 2026-09-01(Q10 横断ミニ掃引への 7 点裁定)の 2「案 X は限定採択する。既に限界が
> 一次記録へ実在する計器については、コード/docstring からその記録へ辿れる参照面を追加してよい。
> 特に process-validator は、ECO-015/ECO-018 等へ分散している既存限界を新しく作り直さず、
> 参照・要約によってコード側から到達可能にする。まだ限界が一次記録として確定していない旧計器に
> ついて、新しい限界を今回の Q10 単問掃引だけから推測して書かない」— 裁定が gate ① を兼ねる。

## 担当設備(equipment)

- 製造:
  - requested: `claude-fable-5`
  - resolved: `claude-fable-5`
  - ハーネス: Claude Code(Claude Agent SDK)
  - 来歴: **self-reported**

## 0. 実測(起票根拠)

Q10 横断ミニ掃引(EXP-20260831-04 第 5 回・母集団 27 単位)の所見: process-validator の
検出力限界は**一次記録に実在する**(ECO-018 order §残余の限界 / ECO-019 order §是正しない
範囲〔IA-02/03 の境界文書化〕/ ECO-019 独立検査 BOUNDARY-DUP-04 の帰着裁定)が、
**コードから辿れない** — 証拠は在るが参照面がない弱形。process-qualification も同様
(IQ-04 の POSIX 限定= ECO-017 order / 据え置き所見= register ECO-017 追記)。

## 1. 変更要求(製造対象 — 裁定の文言どおり)

- `process-validator.py` docstring 直後へ「検出力の限界(一次記録からの集約参照)」ブロック
  3 項 — **新しい限界の創作なし**・各項に一次記録座標(BomDD ECO-018/019)を付す。
- `process-qualification.py` へ同様 2 項(BomDD ECO-017・register ECO-017 追記)。
- 判定ロジック・selftest・出力は**一切変更しない**(コメント挿入のみ)。
- **書かないもの(裁定 2 の否定側)**: ui-cad-gate・worklist・self-conformance 旧検査等、
  限界が一次記録として未確定の計器への新規宣言(それぞれのフル掃引時に確定 — 裁定 3/5/6)。

## 2. 影響なし予測(反証可能・製造前に凍結)

- diff は process-core tools 2 ファイルの**挿入のみ**(削除 0)+台帳系。判定不変の機械根拠=
  コメント行のみ・py_compile 成立・C11(validator selftest+IQ/OQ+決定性)判定不変の予測。
- 配布物につき既設リポへは kit 再設置まで非波及。C16 は本 order を required と判定する見込み。

## 3. 受入

- **V1**: 追記が参照・要約のみ(各項に一次記録座標・新規限界の創作なし — 実文突合)。
- **V2**: diff が挿入のみ(削除 0)・py_compile 両ファイル成立。
- **V3**: self-conformance 全 PASS(C11 判定不変)。
- **V4**: CI 緑(headSha 照合)。**V5**: diff 窓。

## /converge receipt(起動経路: 人間裁定〔案 X 限定採択〕)

- **判定: 収束**(round 軌跡: 1→0→0)。round 1 = 1 件(qualification の据え置き所見の引用は
  「NEW-05 が据え置かれた」という**裁定の来歴**として書く — 所見自体を限界として新作しない
  形に文言を固定)。
- 検証した主張: 一次記録の実在= ECO-018 order:171・ECO-019 order:55・ECO-017 order:29 実読 /
  挿入位置= 両ファイル docstring 終端直後(parse 確認)。
- 未収束事項: なし。

## 4. 製造と受入の実測(2026-09-01)

- 挿入 18 行(validator 11・qualification 7)・削除 0・py_compile 両成立(V2 前半)。
- V1= 各項の座標: validator (1)= ECO-018 §残余の限界(order:171)/(2)= ECO-019 §是正しない
  範囲(order:55)/(3)= ECO-019 BOUNDARY-DUP-04。qualification (1)= ECO-017 order:29 /
  (2)= register ECO-017 追記の実文 — いずれも転記・要約であり新規限界なし。
- V3〜V5 は §5 で確定。

### 較正 receipt(/calibrate 自己適用 — trigger ③: 検査文の変更。二軸)

- 査定した主張と判定:
  1. 「追記は検査文の過大主張を作らない」— **observed / 適格**(追記は全て**限界**=
     主張の縮小方向であり、かつ各項が一次記録の転記 — Q1 の逆方向)。
  2. 「判定ロジックは不変」— **observed / 適格**(挿入のみの diff+py_compile+V3 の
     C11 判定不変で三重確認)。
  3. 「参照面の追加で限界が読者に到達する」— **unknown(理由コード: 未実行 — 到達の実効は
     次にこの治具を扱う者の行動で観測される)**。
- 検出した計器欠陥: なし。検出力の限界: 本査定はコメント変更の妥当性のみ — 治具本体の
  battery 査定は独立検査 4 巡+将来のフル掃引の領分。

## 5. CI 実測

(push 後に追記)

## 6. クローズ

(受入後に追記)
