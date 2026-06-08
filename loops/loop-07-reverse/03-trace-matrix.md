# ③ 双方向トレース行列 — Export seek/audio 経路

`原版証拠 | 観測された振る舞い | REQ | 核/表面 | E-BOM部品 | K-BOM依存 | M-BOM AC | Control Plan深さ | FMEA故障モード | 治具`

| 証拠 | 振る舞い | REQ | 種別 | E-BOM | K-BOM | M-BOM AC | CP深さ | FMEA | 治具 |
|---|---|---|---|---|---|---|---|---|---|
| E1,E2 | 前トリム≥1sで映像入力を `-ss` シーク | REQ-SEEK-1: SpanStart≥1で映像をシーク | 表面 | Export-filter(seek) | FFMPEG-SEEK | `seekBase=SpanStart>=1?SpanStart:0` | L2(尺) | 閾値誤り→遅い/欠け | (perf計測) |
| E5 | 映像 trim=`s-seekBase`(相対) | REQ-SEEK-2: seek時 映像trimはseekBase相対 | 表面 | Export-filter(seek) | FFMPEG-SEEK | `[0:v]trim=start=s-seekBase:end=e-seekBase` | L3(内容) | オフセット引き忘れ→映像ずれ | loop-05 L3 |
| E3,E4,E6 | 音声=**絶対時刻** `s,e`、**未シーク入力1**から | REQ-SEEK-3: seek時 音声は2入力・絶対時刻 | 表面 | Export-filter(seek)+args | FFMPEG-SEEK | 2入力, `[1:a]atrim=start=s:end=e` 絶対 | **L3(音声同期)** | **座標系取り違え(CHEAT-008)** | **loop-05 L3 audio** |
| E7 | 音声非シークで **AACサンプルずれ回避・ビット完全一致** | REQ-SEEK-4: 音声は**サンプル精度**同期 | 表面 | (根拠) | FFMPEG-SEEK(精度) | 同期誤差 **±サンプル/数ms** | **L3 サンプル精度** | サブmsドリフト→微小音ズレ | **要精緻化(±ms相関)** ← 現L3治具は粗い |
| E8 | 非seek時は単一入力・絶対時刻 | REQ-SEEK-5: 非seekは単一入力絶対 | 表面 | Export-filter(非seek) | FFMPEG-GRAMMAR | `[0:v]trim=start=s:end=e` 単一入力 | L2 | — | loop-02.5 L2 |

## 双方向性
- **前方**(証拠→受入): 各行 左→右に辿れる。例: E6 → REQ-SEEK-3 → Export-filter → FFMPEG-SEEK → 2入力AC → L3 → CHEAT-008 → loop-05治具。
- **逆引き**(受入→証拠): 各治具/FMEA/AC から証拠へ戻れる。例: loop-05 L3治具 → REQ-SEEK-3 → E6/E3/E4。FMEA「座標系取り違え」→ E5/E6 の非対称。

## マルチファクトリ・リバースの所見(R30検証)
- 振る舞い行(E5,E6=REQ-SEEK-2/3)は **3リーダー全員一致**=自然に読める(強い)。
- **REQ-SEEK-4(根拠の精度)が弱点**: 3リーダーは根拠を「AV同期」と粗く読み、真の「AACサンプル精度・ビット完全一致」を取りこぼした。
  → これが **CP深さの許容差を過小設定**するリスク(粗いL3で十分と誤判断)。Loop6 の治具劣化発見と同根。
