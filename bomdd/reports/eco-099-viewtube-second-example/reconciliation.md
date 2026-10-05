# 突合と結果 — ECO-099(ViewTube fe0250ef・3 単位 15 行)

統括 AI の分類([classification-producer.md](classification-producer.md))と、検査官の盲検の分類([inspection-report-r2.md](inspection-report-r2.md))の突合。事前登録 T1〜T5 の読み方による。
検査官 r1 は UNMEASURABLE([inspection-report-r1-unmeasurable.md](inspection-report-r1-unmeasurable.md): 検査官の sandbox から対象 commit の `31-kbom.yaml` が `fatal: bad object` で読めなかった。依頼者の環境では 613 行が読める)。
r2 は対象 commit の 5 ファイルの写し(sha256 を依頼者が git show の出力と照合・検査官も再計算して一致)を読んだ。統括 AI は自分の分類を保存してから検査官の報告を開いた。

## T1 区分の分布

| | 句数 | 参照化 | 人へ戻す | 製造手段 | 記録 | 分類不能 |
|---|---|---|---|---|---|---|
| 統括 AI | 42 | 20 | 7(内容 5 件) | 8 | 7 | 0 |
| 検査官 | 63 | 24 | 5(内容 4 件) | 19 | 15 | 0 |

句の切り方が違うため句数は比べられない(検査官は ECO 番号の由来と関数名を独立の句にした)。**両者とも「人へ戻す」が 1 句以上** — ViewPrism2(6 行= 参照化 5・製造手段 1・人へ戻す 0)と向きが違う。

## 「人へ戻す」の内容の突合(1 件 1 行)

| # | 内容 | 統括 AI | 検査官 | 突合の結果 |
|---|---|---|---|---|
| H3 | node condition を持つ pack は必須機能 `node-condition-v1` を宣言する・以前の読み手はその pack を拒否する(pack の形式の版の取り決め) | 人へ戻す(PERSISTENCE 4-4・VIEW-PACK 5-1) | 人へ戻す(PERSISTENCE 4-8・VIEW-PACK 5-7) | **一致**。同種の `music-scope-v1` は仕様(20:L1021)にあるが、こちらは 4 ファイルで 0 件 |
| H4 | 取り込みは music の定義を受け手の music scope に置く(collection を指定した場合を除く) | 人へ戻す(VIEW-PACK 4-3) | 人へ戻す(VIEW-PACK 4-5) | **一致** |
| H5 | 数として読めない numeric restriction を持つ旧い pack は、pack ごと拒否する(保存済みの同じ状況は「捨てて警告」と裁定済み= 別の決め) | 人へ戻す(VIEW-PACK 5-3) | 人へ戻す(VIEW-PACK 5-4) | **一致**(理由も同じ) |
| H2 | 旧い restriction の変換は schema version を上げない・以前のバックアップは復元後の最初の open で変換される | 人へ戻す(PERSISTENCE 4-3) | 製造手段(PERSISTENCE 4-6・4-7) | **不一致**。どちらも裁定層の所在は示せない。争点= これは「どう作るか」(移行の起動時期)か、「何を守るか」(以前のバックアップが復元できて変換されるという互換の約束)か |
| H6 | Condition と Restriction の両方を持つ placement は拒否する | 参照化(20:L1047 の「malformed な入力は変更の前に拒否」に含まれる) | 人へ戻す(一般則より具体的) | **不一致**。一般則を「同じ内容」と読むかの差 |
| H1 | どの外部の失敗もユーザー作成データを消さない | 人へ戻す(全称の保証は裁定層のどの文より強い) | 参照化(10:L108〜115 REQ-004・L139〜146 REQ-005) | **参照化を採る**(事前登録の読み方: どちらかが所在を示せれば参照化)。統括 AI は 10:L146 の rationale と E-BOM の 1 行だけを見て「弱い」と判断し、REQ-004 / REQ-005 の statement を引いていなかった。ただし M の文(全称)は 2 つの要求の合成より強い読みもできる |

**一致して「人へ戻す」= 3 件(H3・H4・H5)。不一致 2 件(H2・H6)。** 3 件とも View Pack(ファイルの形式・取り込み)の取り決めで、未見の腕(M-VIEW-PACK-001)に 3 件、既見の腕に 1 件(H3 が PERSISTENCE にも現れる)。

出所の確認(統括 AI・突合の後・対象 commit の `bomdd/eco/ECO-VT-212.md` 150 行を grep): 利用者の裁定として記録されているのは Q1 (a) と Q2 (i) の 2 つ(L112〜118)で、`node-condition`・`unreadable`・`schema`・`backup` の語は ECO 本文に現れない。
→ H3・H5(と H2)は、**利用者が裁定した記録が見つからず、M-BOM にだけ書かれている設計の決め**。H4(ECO-VT-195)は、ECO 本文を英語の語(forced・target・lands)で検索して 0 件 — 本文は日本語のため**未確認**(M の行は「the user's ruling of 2026-09-27, E」を行の冒頭に掲げる)。

## T2 3 分類の十分さ

「記録」= 統括 AI 7 句・検査官 15 句。分類不能 0。**playbook §4.5 の 3 分類(参照化・人へ戻す・製造手段)では ViewTube の M の行を分けきれない** — 実測値(MEASURED 2026-10-04 …)・レビューの所見(R8 round 2 (BLOCKING))・検査していないことの注記(NOT exercised by any automated case)・ECO と裁定の由来、が 4 つ目の区分として要る。
これらは設計の内容でも作り方でもなく、置き場は M-BOM 以外(K-BOM の実測の知識・As-Built・Control Plan の検査なしの注記・変更記録)が候補だが、本計測は置き場を決めない。

## T3 混在

2 つ以上の区分の句を含む行= 統括 AI 6/15・検査官 8/15。共通の 2 行(各単位の先頭 2 行)と VIEW-PACK の短い 3 行を除くと、**ECO ごとに書き足された長い行はほぼすべて混在**(統括 AI 6/8・検査官 8/8)。行単位の分類(ViewPrism2 の試行のやり方)は ViewTube では使えない。

## T4 盲検の一致(行ごとの区分の集合)

| 単位 | 行 | 統括 AI | 検査官 | 一致 | 差の内容 |
|---|---|---|---|---|---|
| PERSISTENCE | 1 | {参} | {参} | ○ | |
| PERSISTENCE | 2 | {人} | {参} | × | H1 |
| PERSISTENCE | 3 | {参, 製} | {参, 製, 記} | × | 検査官は「ECO-VT-195 (REQ-092 … ruling (b))」を由来の記録として分けた(統括 AI は参照化の句に含めた) |
| PERSISTENCE | 4 | {記, 製, 人} | {参, 人, 製, 記} | × | H2(人 / 製)。検査官は「DroppedRestriction を書く」を参照化として分けた |
| YOUTUBE | 1 | {参} | {参} | ○ | |
| YOUTUBE | 2 | {人} | {参} | × | H1 |
| YOUTUBE | 3 | {製} | {製, 記} | × | 由来の記録(ECO-VT-209)の分け方だけ |
| YOUTUBE | 4 | {製, 記} | {製, 記} | ○ | |
| YOUTUBE | 5 | {記, 製} | {製, 記} | ○ | |
| VIEW-PACK | 1 | {参} | {参} | ○ | |
| VIEW-PACK | 2 | {参} | {参} | ○ | |
| VIEW-PACK | 3 | {参} | {参} | ○ | |
| VIEW-PACK | 4 | {参, 人} | {参, 人, 記} | × | 由来の記録の分け方だけ(人へ戻す の内容 H4 は一致) |
| VIEW-PACK | 5 | {人, 製, 参} | {参, 人, 製, 記} | × | 由来の記録の分け方。人へ戻す の内訳は H3・H5 が一致・H6 が不一致 |
| VIEW-PACK | 6 | {参} | {参, 製, 記} | × | 由来の記録と「through ViewHierarchyService」の分け方だけ |

- **集合の一致= 7/15 行**。不一致 8 行のうち、差が「ECO 番号・裁定の由来を独立の記録の句に分けたか」「関数名 1 つを独立の製造手段の句に分けたか」だけの行が 4 行(PERSISTENCE 3・YOUTUBE 3・VIEW-PACK 4・VIEW-PACK 6)— 句の切り方の粒度の差で、内容の判断の差ではない。
  内容の判断が割れたのは 4 行(PERSISTENCE 2・YOUTUBE 2= H1 / PERSISTENCE 4= H2 / VIEW-PACK 5= H6)= 3 件。
- 読み方(事前登録): 閾値は置かない。「人へ戻す」の不一致は 1 件ずつ上の表に書いた。

## T5 腕の差

既見の腕(PERSISTENCE・YOUTUBE)= 一致した「人へ戻す」1 件(H3)・不一致 1 件(H2)。未見の腕(VIEW-PACK)= 一致 3 件(H3・H4・H5)・不一致 1 件(H6)。**向きは同じ(どちらの腕にも人へ戻す がある)**。件数は未見の腕の方が多い。
単位の性質の差もある: YOUTUBE(外部のプレーヤーとの接続)は製造手段と記録がほとんどで、人へ戻す は 0(H1 を参照化とした後)。VIEW-PACK(ファイルの形式と取り込み)に集中する。

## 観察(指標の外)

- **ViewTube の裁定層は、仕組みを M-BOM に委ねると明文で書いている**: REQ-095(10:L3714〜3715)「THE MECHANISM IS NOT SAID HERE, as in REQ-093: the ended signal, the seek and the mute are implementation judgements recorded in the M-BOM」。両分類者ともこれを根拠に YOUTUBE の行 4 を製造手段とした。
  「E 側は人が裁定し、M は AI が判断する」分担は、ViewTube では要求の本文に既に現れている。
- **設計の内容の正本は E-BOM ではなく要求と仕様の本文**: 参照化の所在は、統括 AI の 20 句・検査官の 24 句とも、ほぼすべて 10-requirements と 20-spec(E-BOM を所在に挙げた句は 0。K-BOM は 1 句)。OBS-20261005-02(裁定層は E-BOM だけでない)の 2 例目の条件(別の製品で、M の記述が E-BOM に無いが仕様・要求にある)に当たる。
- **「人へ戻す」は、ファイルの形式・版の違う読み手との取り決め・取り込みの既定に集中した**。利用者から直接は見えにくいが、後から変えにくい(出回った pack と以前の版の読み手が相手)決めである。
- **統括 AI の H1 の誤り**は ECO-097 の起票時と同じ型(裁定層を読み切らずに「無い」と判断)— 今回は rationale と E-BOM を見て statement を引かなかった。盲検の検査官が所在を示して訂正した。
