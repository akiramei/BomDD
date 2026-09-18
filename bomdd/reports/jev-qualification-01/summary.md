records=78 answered=78 errors=0 models=['jev-1.13.0']
tokens in=42738 out=1794

## 腕別指標

| 腕 | N | negative 正答(感度: known-bad を弾く) | positive 正答(特異度: 実在を通す) | 拮抗帯 0.4〜0.6 | 誤り検体 |
|---|---|---|---|---|---|
| ja | 36 | 26/29 | 4/7 | 6 | C17-F1(P 0.38), C17-F2(n 0.72), C17-F9(P 0.35), C17-F17(P 0.42), C16-F11(n 0.50), C16-F12(n 0.74) |
| en | 35 | 24/28 | 4/7 | 0 | C17-F1(P 0.25), C17-F2(n 0.66), C17-F9(P 0.27), C17-F17(P 0.27), C16-F10(n 0.70), C16-F11(n 0.67), C16-F12(n 0.83) |
| real | 7 | 1/3 | 4/4 | 0 | R5(n 0.70), R6(n 0.82) |

## ja と en の差(同一 fixture)

対応 35 本・|Δp|≥0.3= 0・判定反転= 1
  反転 C16-F10 (n): ja=0.48 en=0.70

## 検体別(ja/en/real)

| id | 腕 | ラベル | P | 判定 | 帯 | 説明 |
|---|---|---|---|---|---|---|
| C17-F1 | ja | POS | 0.380 | **MISS** | clear | verified + receipt(旧 scope) |
| C17-F1 | en | POS | 0.250 | **MISS** | clear | verified + receipt(旧 scope) |
| C17-F2 | ja | neg | 0.720 | **MISS** | clear | verified + receipt なし |
| C17-F2 | en | neg | 0.660 | **MISS** | clear | verified + receipt なし |
| C17-F3 | ja | neg | 0.040 | ok | clear | filed + なし(verified のみ対象) |
| C17-F3 | en | neg | 0.040 | ok | clear | filed + なし(verified のみ対象) |
| C17-F4 | ja | neg | 0.060 | ok | clear | verified + 根拠つき免除(宣言者表示) |
| C17-F4 | en | neg | 0.050 | ok | clear | verified + 根拠つき免除(宣言者表示) |
| C17-F5 | ja | neg | 0.050 | ok | clear | フェンス内の免除宣言は無効(過剰免除の遮断) |
| C17-F5 | en | neg | 0.050 | ok | clear | フェンス内の免除宣言は無効(過剰免除の遮断) |
| C17-F6 | ja | neg | 0.060 | ok | clear | 空の reason は却下(欄の存在でなく中身) |
| C17-F6 | en | neg | 0.060 | ok | clear | 空の reason は却下(欄の存在でなく中身) |
| C17-F7 | ja | neg | 0.070 | ok | clear | backtick フェンス内の様式例は receipt ではない(known-bad) |
| C17-F7 | en | neg | 0.050 | ok | clear | backtick フェンス内の様式例は receipt ではない(known-bad) |
| C17-F8 | ja | neg | 0.120 | ok | clear | 平文の言及・否定文は receipt ではない(known-bad) |
| C17-F8 | en | neg | 0.140 | ok | clear | 平文の言及・否定文は receipt ではない(known-bad) |
| C17-F9 | ja | POS | 0.350 | **MISS** | clear | 見出しとして存在する receipt(known-good・旧 scope) |
| C17-F9 | en | POS | 0.270 | **MISS** | clear | 見出しとして存在する receipt(known-good・旧 scope) |
| C17-F10 | ja | neg | 0.280 | ok | clear | チルダ fence 内の見出しは receipt ではない(独立検査官 S4-1) |
| C17-F10 | en | neg | 0.140 | ok | clear | チルダ fence 内の見出しは receipt ではない(独立検査官 S4-1) |
| C17-F11 | ja | neg | 0.050 | ok | clear | インデントされたコード例内の免除宣言は無効(独立検査官 S4-2) |
| C17-F11 | en | neg | 0.050 | ok | clear | インデントされたコード例内の免除宣言は無効(独立検査官 S4-2) |
| C17-F12 | ja | neg | 0.040 | ok | clear | 見出し内の否定+本体なし(独立検査官 S4-3a) |
| C17-F12 | en | neg | 0.040 | ok | clear | 見出し内の否定+本体なし(独立検査官 S4-3a) |
| C17-F13 | ja | neg | 0.480 | ok | ambiguous | `##較正`(空白なし)は見出しではない(独立検査官 S4-3b) |
| C17-F13 | en | neg | 0.320 | ok | clear | `##較正`(空白なし)は見出しではない(独立検査官 S4-3b) |
| C17-F14 | ja | neg | 0.400 | ok | ambiguous | `#` 7 個は見出しではない(独立検査官 S4-3c) |
| C17-F14 | en | neg | 0.300 | ok | clear | `#` 7 個は見出しではない(独立検査官 S4-3c) |
| C17-F15 | ja | neg | 0.320 | ok | clear | receiptless は receipt ではない(独立検査官 S4-3d) |
| C17-F15 | en | neg | 0.260 | ok | clear | receiptless は receipt ではない(独立検査官 S4-3d) |
| C17-F16 | ja | neg | 0.110 | ok | clear | 見出しのみ・本体空は新 scope では receipt ではない(旧 P4 境界の縮小) |
| C17-F16 | en | neg | 0.100 | ok | clear | 見出しのみ・本体空は新 scope では receipt ではない(旧 P4 境界の縮小) |
| C17-F17 | ja | POS | 0.420 | **MISS** | ambiguous | 見出し+本体 4 項目(known-good・新 scope) |
| C17-F17 | en | POS | 0.270 | **MISS** | clear | 見出し+本体 4 項目(known-good・新 scope) |
| C17-F18 | ja | neg | 0.130 | ok | clear | status 'verifiedness' は対象外(厳密一致 — 独立検査官 S4-4 の偽陽性) |
| C17-F18 | en | neg | 0.120 | ok | clear | status 'verifiedness' は対象外(厳密一致 — 独立検査官 S4-4 の偽陽性) |
| C16-F1 | ja | neg | 0.050 | ok | clear | required + receipt なし |
| C16-F1 | en | neg | 0.050 | ok | clear | required + receipt なし |
| C16-F2 | ja | POS | 0.760 | ok | clear | required + receipt あり(正常系) |
| C16-F2 | en | POS | 0.790 | ok | clear | required + receipt あり(正常系) |
| C16-F3 | ja | neg | 0.030 | ok | clear | not-required + receipt なし |
| C16-F3 | en | neg | 0.030 | ok | clear | not-required + receipt なし |
| C16-F4 | ja | neg | 0.460 | ok | ambiguous | mixed-task 陽性(事実照会で始まり裁定候補を生成) |
| C16-F4 | en | neg | 0.330 | ok | clear | mixed-task 陽性(事実照会で始まり裁定候補を生成) |
| C16-F5 | ja | neg | 0.070 | ok | clear | hard-positive 実在 かつ 根拠なし not-required 宣言 |
| C16-F5 | en | neg | 0.060 | ok | clear | hard-positive 実在 かつ 根拠なし not-required 宣言 |
| C16-F6 | ja | neg | 0.070 | ok | clear | not-required + reason のみ(decided-by なし) |
| C16-F6 | en | neg | 0.070 | ok | clear | not-required + reason のみ(decided-by なし) |
| C16-F7 | ja | neg | 0.090 | ok | clear | not-required + reason + decided-by(根拠つき受理) |
| C16-F7 | en | neg | 0.070 | ok | clear | not-required + reason + decided-by(根拠つき受理) |
| C16-F8 | ja | neg | 0.090 | ok | clear | not-required + 空の reason(欄の存在でなく中身を測る) |
| C16-F8 | en | neg | 0.070 | ok | clear | not-required + 空の reason(欄の存在でなく中身を測る) |
| C16-F9 | ja | neg | 0.080 | ok | clear | コードフェンス内の宣言は免除を与えない(構文を説明する文書の自己免除を防ぐ) |
| C16-F9 | en | neg | 0.060 | ok | clear | コードフェンス内の宣言は免除を与えない(構文を説明する文書の自己免除を防ぐ) |
| C16-F10 | ja | neg | 0.480 | ok | ambiguous | フェンス内の様式例は receipt ではない(遺産規則でも) |
| C16-F10 | en | neg | 0.700 | **MISS** | clear | フェンス内の様式例は receipt ではない(遺産規則でも) |
| C16-F11 | ja | neg | 0.500 | **MISS** | ambiguous | 未閉鎖 fence 内の様式例は receipt ではない |
| C16-F11 | en | neg | 0.670 | **MISS** | clear | 未閉鎖 fence 内の様式例は receipt ではない |
| C16-F12 | ja | neg | 0.740 | **MISS** | clear | チルダ fence 内(新規則) |
| C16-F12 | en | neg | 0.830 | **MISS** | clear | チルダ fence 内(新規則) |
| C16-F13 | ja | neg | 0.050 | ok | clear | 平文の言及(省略宣言)は receipt ではない(新規則) |
| C16-F13 | en | neg | 0.060 | ok | clear | 平文の言及(省略宣言)は receipt ではない(新規則) |
| C16-F14 | ja | POS | 0.830 | ok | clear | 見出しはあるが判定・DoD のない receipt(ECO-036/053 様式違反) |
| C16-F14 | en | POS | 0.860 | ok | clear | 見出しはあるが判定・DoD のない receipt(ECO-036/053 様式違反) |
| C16-F15 | ja | neg | 0.090 | ok | clear | インデントされたコード例内の免除宣言は無効 |
| C16-F15 | en | neg | 0.080 | ok | clear | インデントされたコード例内の免除宣言は無効 |
| C16-F16 | ja | POS | 0.870 | ok | clear | 「round 軌跡」様式だけの正当 receipt を遮断しない(偽陽性の除去・遺産規則) |
| C16-F16 | en | POS | 0.880 | ok | clear | 「round 軌跡」様式だけの正当 receipt を遮断しない(偽陽性の除去・遺産規則) |
| C16-F17 | ja | POS | 0.900 | ok | clear | 5 ラベル完備の receipt(known-good・新規則) |
| C16-F17 | en | POS | 0.900 | ok | clear | 5 ラベル完備の receipt(known-good・新規則) |
| P1 | ja | neg | 0.040 | ok | clear | 見出し内の否定+本体ラベル完備(C17 限界 (5)・機械は通す) |
| R1 | real | POS | 0.950 | ok | clear | ECO-071 較正 receipt(実施済み) |
| R2 | real | POS | 0.960 | ok | clear | ECO-075 較正 receipt(実施済み) |
| R3 | real | POS | 0.960 | ok | clear | ECO-076 較正 receipt(実施済み) |
| R4 | real | POS | 0.930 | ok | clear | ECO-076 §4 製造と受入の実測(実測結果・receipt 様式ではない) |
| R5 | real | neg | 0.700 | **MISS** | clear | ECO-076 §3 受入(計画) |
| R6 | real | neg | 0.820 | **MISS** | clear | ECO-075 §3 受入(候補・計画) |
| R7 | real | neg | 0.040 | ok | clear | ECO-076 §5 製造 commit 時点(未記入の placeholder) |
