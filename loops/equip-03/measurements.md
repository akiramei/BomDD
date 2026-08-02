# equip-03 measurements(実行記録 — 進行中)

## 0. 起票前検証 — fail-closed 停止と題材の再裁定(2026-08-02)

protocol §3 手順 1 の実在確認で **凍結題材の消滅を検出**し、製造に入らず停止した(逸脱ではなく
fail-closed の正常動作。工場起動・介入・製造は一切発生していない)。

- 実測: 候補「repo: 形の repo 不在= X-XREPO skip へ」は **Plm ECO-002(2026-07-03)で解消済み**。
  証拠= 20-spec §2.4(rev3・受理形3 の repo 不在= X-XREPO-001 skip)/オラクル S-24
  (change_ref: ECO-002・「ViewPrism2 pre-commit 実害の再現形」)/packages/core/src/resolve/
  model.ts(「rev3/ECO-002 CH-3」注記つき実装)。
- 根因: 52-metrics の候補行に解消マーカーが無く(他候補は「→ 解消(ECO-00N)」を持つ)、
  現存候補に見えていた — **台帳の記帳漏れ**。protocol 凍結(93b1be9)と gate ① 裁定 1 は
  この誤った在庫認識に基づいていた。
- 処置: 解消マーカーを追記(Plm 076f6c3・歴史記述は非改竄・追記のみ)。
- 教訓候補: 「候補台帳の解消マーカーは人手 — 起票前の実在検証(spec/oracle/src 突合)が
  最後の防壁」。equip-02 レビュー採択の入力検証(EXP-20260802-06 系)が**題材の存在**にも
  適用されるべき実例 1 件。

## 0.1 代替在庫の実測(再裁定の材料・2026-08-02)

| リポ | 実測結果 |
|---|---|
| Plm | 現存候補は **M-BOM 写像被覆ギャップのみ**(unmapped 76 files・受入= unmapped 0 が機械判定可。ただし「単独 ECO は過剰・次回 32-mbom 改訂時に便乗」と記録済み= 昇格には再裁定が要る)。宣言中心で src 製造は僅少 |
| ViewPrism2 | ECO-141 まで**全クローズ**・未起票候補なし |
| ViewGrid | 宣言系債務 4 件(catch-all ペア写像・csproj/sln 所有・tests unit・CP 接続)— いずれも「ECO 運用開始時」預り。60-register 未設= 測定系 bootstrap 込みになる |
| MoviePad | line ready・ECO-001 済み・未起票候補なし(W1〜W5 は製品是正不要と決着済み) |

= **src 変更を伴う実在の未起票 ECO 候補は現在ゼロ**。gate ① 再裁定へ(選択肢: Plm M-BOM
ギャップの単独昇格/ViewGrid 初 ECO/実需発生待ち)。

## 0.2 gate ① 再裁定(2026-08-02 maintainer)

**題材= Plm M-BOM 被覆ギャップの単独昇格で確定**(推奨案採択)。既存判断「単独 ECO は過剰」は
①測定価値 ②在庫ゼロの新事実 により更新。protocol 凍結文の題材条項(§ gate ① 裁定 1)は本再裁定で
差し替え — その他の凍結条項(工場スコープ/独立検査/入力固定/二車線/採らないもの)は不変。
比較セルの正直記載: eco_001/002 は src 変更 ECO・本 ECO は宣言 ECO のため**同格比較は成立しない**
(工程指標の参考併記に格下げ)。測定 4 次元のうち直接測定できるのは ①影響抽出 ③BOM 同期
④証拠クローズ+回帰非破壊(②の対象実体変更は無い)。

## 1. 起票・入力固定(EXP-20260802-06 初適用・2026-08-02)

- 起票: Plm ECO-006(order= bomdd/60-change-order-eco-006.md・register open・c6f9d2d push 済み)。
  起票時の self-hosting lint= exit 0(error/warn 0・info のみ)。
- **入力固定(凍結)**:
  - tag: `eco-006-input` / expected_commit: `c6f9d2d75301bb1fc664c9877917a18343b377d6`
  - **input_tree_hash**: `cc91fe5ec2aa2bbef6ace7adcdebdf3ae366269b`
  - 採点器: BomDD method/tools/impact-retrospective.py
    sha256= `614AB9ABFB1F12789613550C0EA6363ACC8BF317F4C551027098EE7FECF17526`
    (BomDD commit 941941a 時点・workspace へ凍結複写して工場に供与)
  - prompt bundle: [prompt-bundle.md](prompt-bundle.md)(sha256 は §2 で記録)
- **fail-closed 検査 PASS**: workspace clone の HEAD・tree・tag 解決値が期待値と全一致
  (不一致なら開始しない — 実測で一致)。
- **較正(V2・変更前個体の赤)**: 入力 commit c6f9d2d で
  `unmapped_files = 76`・`real_under_files = 111` を実測(受入 V1= unmapped 0 かつ
  real_under 111 不変、が現状不成立であることの凍結)。

## 2. 設備構成の記録(ECO-028 様式)

| 欄 | 値 | 来歴 |
|---|---|---|
| 製造 requested | Agent tool `model: "opus"` | observed(呼び出しパラメータ) |
| 製造 resolved | **claude-opus-5[1m]** | **self-reported**(equip-02 と同一申告値・証明ではない) |
| ハーネス | Claude Code Agent tool subagent(親= claude-fable-5) | observed |
| 主観察者(起票・採点・commit) | claude-fable-5 | observed |
| 独立検査官 | Codex fresh(別ベンダー・read-only・§5 に記録) | observed |
| prompt bundle | sha256= 32D263D1792C9DFA01FBC88A041727CE882D5AC6FA3BEDB6B4FB621B02DDE68B | observed |

## 3. 時間分解・原価・カウンタ(プロスペクティブ実測)

- 工場起動 2026-08-02T20:50:21+09:00 / **製造(工場壁時計)= 1,000,971 ms ≈ 16 分 41 秒**・
  tool 呼び出し 48 回 / トークン= **154,693**(ハーネス計測)/ 費用(通貨)= **unknown**(推定禁止)。
- **介入 0・差戻 0・範囲外 1**(軽微・自己申告: lint 出力先の相対パス誤りで指定 3 パス外
  〔同一 scratchpad 内〕へ 1 回出力 → 即削除・是正。実害なし)。
- 生成物の一時変更 1 件を自己申告(較正 build の tsbuildinfo 更新 → git restore 復元・dist 変化ゼロ)。

## 4. 結果 — 必須製造車線(合否・OBS-20260802-07 二車線)

**全 PASS(一発・機械受入)**:

| 検査 | 実測 |
|---|---|
| V1 採点器(設計者独立再実行) | **unmapped 76 → 0・real_under 111 不変・mapped 111** |
| V3 build / tests / オラクル | 0 エラー / **118/118** / **34/34** |
| V3 self-hosting `--eco --fail-on error` | **error 0 / warn 0**(info 176→180→176: +4 は新 unit の R-005 孤立= register 影響集合更新で解消 — 予測どおり) |
| V3 ViewPrism2 workspace 回帰 | **差分 0**(変更前個体との対照実測で error 0/warn 12/info 502 が完全同値 — warn 12 は ViewPrism2 側の既存 drift・本 ECO 非起因の帰属証明) |
| V5 diff 閉包 | bomdd/ のみ(3 ファイル・126 行純増・削除 0) |
| Plm CI | fix 8a874ea = **success**(両 OS 緑) |

製造内容: 32-mbom へ所有 unit 5 件(M-ORACLE-009/M-BUILD-CORE-010/M-BUILD-VIEWER-011/
M-CI-012/M-SCHEMA-013)。裁定 1= 生成物専用 unit(帰属規則「生成物を一意に生む製造手順を持つ
最小の unit」の一般化)/裁定 2= 治具様式整合・oracle/ 併合否の根拠= **供与境界が逆**
(34-routing factory_isolation と突合した論証)。

## 5. 自主改善車線(別枠観測 — 合否に算入しない)

- 較正の赤(unmapped 76)を工場が独立再実測し凍結値と一致確認(要求外の検証行動)。
- 帰属規則の一般化(1 package=1 unit なら源 unit・N unit なら専用 unit+depends_on)を
  ルール文として明文化 — 将来 ECO の判断基準になりうる提案。
- **F003= 設計者側 order の欠陥検出**: §3 の起草先記述の誤記(workspace 直下 vs bomdd/61)を
  検出し「実物が正+受入証拠+diff_audit 整合」の 3 点論証で正しく解決(order §5 で訂正済み)。
  equip-02 の「受入の自主拡張」に続く自発的検査規律の 2 例目(装置差の候補観測・n=2)。
- 影響なし予測の外れ 1 件(multi_unit_ecos 5 予測→実測 4)を自己申告 — 正直記載の転移。
- ずる報告 4 件(F001 生成物由来欄の語彙未規定/F002 artifact.type 語彙/F003 上記/
  F004 R-005 info 増の許容基準不在 — 検査を黙らせるために 34-routing を歪めない判断を明記)。

## 6. 独立検査(Codex fresh・別ベンダー・read-only)

> **訂正(正直記載)**: protocol §4 と本書初版は本検査を「EXP-20260726-01 の 2 回目を兼ねる」と
> 記したが、これは**誤り** — EXP-20260726-01 は「**非 GPT 系**検査官での検査転移の再現」であり、
> Codex(GPT 系)による本検査は対象外。本検査が延伸するのは transfer-04 系列(GPT 系検査官・
> 通算実績への加算)であって、EXP-20260726-01 は未回収のまま残る。凍結 protocol の当該記述は
> 逸脱として本欄で訂正する(protocol 本文は非改竄)。

- 検査官: OpenAI Codex(model family GPT-5・**resolved= unknown と自己申告 — 推定補完せず**=
  unknown 規律の横断成立)。セッション 019fc264…(rollout jsonl 保存・報告全文=
  [independent-inspection-eco-006.md](independent-inspection-eco-006.md))。
- 実施上の実測: read-only 制約で build/test/oracle の再実行は mkdtemp EPERM —
  「製品 FAIL でなく**独立再測定不能**」と正しく分類(4 値判定の規律を独立に適用)。
  数値受入は書込みなし経路で独立再現(unmapped 76→0・real_under 111 不変・既存写像の帰属変更 0・
  最終 lint 176/新 unit 所見 0・diff 5 ファイル bomdd/ 閉包)。採点器も独立再実行。
  スレッドが最終報告前に停止し **resume 1 回で報告回収**(中断→resume は測定系イベントとして記録)。
- **判定 REJECT・所見 5 件(high 0/medium 4/low 1)— 当方突合で 5/5 CONFIRMED・誤検出 0**:

| ID | 深刻度 | 要旨 | 帰属 |
|---|---|---|---|
| IA-01 | medium | 生成物 unit の path 過広 — 著述物(package.json/tsconfig.json)を吸収し「鋳造物・人手編集禁止」契約と矛盾 | 工場 |
| IA-02 | medium | M-SCHEMA-013 が供与入力(ref-v0)と製造出力(plm-*)を混載= 粒度原則不適合 | 工場 |
| IA-03 | medium | depends_on 不完全(viewer→core 欠落・CI→build unit 欠落)+意味論未裁定 | 工場 |
| IA-04 | low | oracle/ 非併合の結論は妥当だが根拠「test/ は工場へ渡る」が routing 実文言と不一致 | 工場 |
| IA-05 | medium | 受入記録 §5 が工場段階と最終段階の証拠を混在・ViewPrism2 回帰の revision/コマンド未記録= 再現不能 | **設計者(fable)** |

- IA-05 の追実測: 同一 revision(ViewPrism2 6fe3706/ViewPrismUI 204723b)+記録コマンドで
  warn 12 を 3 回再現 — 検査官の 15 は実行条件差とみられ、欠陥の本体は「記録の未固定」で確定。
  是正= order §5 追記(設計者・即日)。
- **差戻 1 回目**(2026-08-02T21:44:33+09:00): IA-01〜04 を同一工場個体(文脈保持)へ発行。
- 検出構造の観測: 機械受入(V1〜V5)が全 PASS の個体から、意味品質(帰属の来歴・宣言の過広・
  依存の完全性・論拠の事実整合)の真正所見を別ベンダー検査が摘出 — **「数値 PASS は意味 PASS を
  含意しない」の直接実測**。transfer-04 4 類型の「存在 vs 完全性」と同族。H-e3-3 **成立**。

## 7. 差戻ループの実測(差戻 1〜3・検査 3 ラウンド)

| 段 | 工場実測 | 結果 |
|---|---|---|
| 差戻 1(IA-01〜04)| 12 分 56 秒・全所見受諾・provenance 分離規則 (A) 一般化・新 unit 3(014/015/016)・残余 1 正直記載(tsbuildinfo= パス機構の限界)・ずる +3 | fix2= e876e81(CI 緑)。再検査= 4 CLOSED+**境界受理 1**(宣言済み残余を現物一致で受理)・IA-03 PARTIAL・NEW-01(設計者帰属) |
| 差戻 2(IA-03 完全化)| 7 分 19 秒・9 エッジ追加(**証拠等級 A/B を自発定義**・A6/B3・張らない側 5 クラスも検算記録・削除 0 機械証明)・ずる +2(F008 B 等級の構造的弱点/F009 不在宣言の再検証不能性) | fix3= 677b43e(CI 緑・NEW-01 は設計者是正を同梱)。第 3 回検査= NEW-01 CLOSED・new 0・IA-03 PARTIAL 継続(基準の自己閉包未達= 欠落 2 エッジ+B 例外未明文化) |
| 差戻 3(基準の閉包)| 7 分 51 秒・欠落 2 エッジ追加(計 11)+**例外規則を妥当性条件 (C) 非循環へ一般化**(等級 A/B= 証拠の強さ・採否= (C))+**閉性の機械検査を自作**(DAG+B 候補全数処理・治具はリポ外)・ずる +1(F010 CP→ファイル写像の非機械可読性= 設計者側債務の指摘)= 累計 10 | fix4= 6ef20f7(CI 緑)。第 4 回検査= **IA-03 CLOSED**(検査官独立 DAG 解析: 16 unit/29 edge/循環 0/B 残余 0)・new= NEW-IA03-01(low・61 の段階ラベル欠落= 工場側記録)→ 設計者追記で条件充足(fix5= d31b835・第 5 回は比例原則で不実施) |

- **独立検査シリーズ確定**: 4 ラウンド・提起 8・**8/8 CONFIRMED・誤検出 0**・境界受理 1・
  残 open 0。収束 5 → 2 → 1 → 0(単調)。
  第 4 報告= [independent-closure-eco-006.md](independent-closure-eco-006.md)。
- **段階混在クラス 3 例**(IA-05 設計者/NEW-01 設計者/NEW-IA03-01 工場)— workspace 段階と
  最終統合個体の測定値を段階ラベルなしで記録する誤りが両系統に再現= 還元候補(記録様式に
  「個体= どの revision か」の欄)。

## 8. 時間・原価の合算(equip-03 全体)

| 項目 | 実測 |
|---|---|
| 工場(claude-opus-5)壁時計 | 初回 16m41s+差戻1 12m56s+差戻2 7m19s+差戻3 7m51s= **44m47s** |
| 工場トークン(ハーネス計測・累積) | **292,075**(内訳: 初回 154,693/差戻1 ≈64,126/差戻2 ≈35,342/差戻3 ≈37,914) |
| 工場 tool 呼び出し | 48+25+17+19= 109 |
| 独立検査(Codex)| 4 ラウンド(初回はスレッド中断→ resume 1 回で回収)。トークンは第 3 回のみ観測 87,895・他 unknown(CLI 非表示) |
| 費用(通貨) | **unknown**(推定禁止) |
| カウンタ(最終) | **介入 0・差戻 3・範囲外 1(軽微・自己申告・即是正)** |
| Plm CI | 起票 c6f9d2d・fix 8a874ea・fix3 677b43e・fix4 6ef20f7・fix5 d31b835 = **全 5 push 緑(実測)** |

## 9. 事前予測 H-e3-1〜3 の判定

- **H-e3-1(機械受入一発到達)= 成立** — rev1 が V1〜V5 一発 PASS(eco_001/002 の opus-4.8/
  sonnet-4.5 と同値)。ただし**意味品質は機械受入の外**にあり独立検査で差戻 3(протокол の
  検査体制がなければ見えなかった — 検査条件込みの値、の再確認)。
- **H-e3-2(ビルドキャッシュ系 under 3 例目)= 対象外(前提消滅)** — 題材が宣言 ECO に
  変わり src 変更が無いため発火面なし。類縁事象 1 件は観測(較正 build の tsbuildinfo 変化を
  工場が自己申告・復元)。
- **H-e3-3(機械受入通過後の独立検査の真正所見)= 成立** — 3 ラウンド連続で新真正所見
  (5/1/1)・4 回目で残余 0。

## 10. 集計 — claude-opus-5 の ECO 適用製造セル(equip 表への追加行)

- **セル値(検査体制込み)**: P-ECO(宣言 ECO・M-BOM 改訂)×1 — 機械受入**一発**(V1〜V5)・
  **意味品質の差戻 3(単調収束・全所見受諾・反論 0)**・介入 0・範囲外 1(軽微)・ずる 10
  (全て高粒度・うち 2 件は設計者側債務の指摘)。
- **測定 4 次元**: ①影響抽出= under 0/over 0(hub_concentration 内訳予測まで的中・予測外れ
  1 件は自己申告)②非破壊= 全回帰差分 0(ViewPrism2 は変更前個体との対照で帰属証明)
  ③BOM 同期= unmapped 76→0+**provenance 帰属規則・depends_on 意味論・(C) 非循環の一般規則化**
  (宣言の意味設計まで到達)④証拠クローズ= 全段 diff 閉包・追加のみ・記録系欠陥 3 は検出後即固定。
- **質的観測(装置差候補・n 小につき記録のみ)**: (a) 差戻への応答様式 — 全所見受諾+指摘の
  一段先まで一般化(規則 (A)/(C)・証拠等級・閉性検査の自作)が 3 回連続 (b) 自主検査規律
  (equip-02 の変異検査に続き 3 例目) (c) 「張らない側」の検算記録= 不在の証明への自発的関心。
- **拘束(再掲)**: 本セルは webapi-02 P2 とも Plm eco_001/002(src ECO)とも直接比較不能
  (クラス・検査体制が異なる)。率の統計判定・routing への使用禁止。n=1。

## 11. 残(maintainer 裁定待ち)

- **verified 裁定+golden**(maintainer)→ verified 時: diff_audit へ head:(受入タグ)追記で
  窓閉鎖・52-metrics 記帳(eco_006 節+候補行解消マーカー)・as-built 追記。
- 還元候補(lesson-promote 入口・裁定後): 段階混在クラス(3 例)/F010(test_vectors の
  機械可読化)/証拠等級 A/B・妥当性条件 (C) の一般化可能性/題材消滅を fail-closed が検出した
  実例(EXP-20260802-06 の初適用実測)。

- 残件の単調減少: 5 → 2 → 1。検査官は前進を PARTIAL として認めつつ**工場自身の基準の自己適用**で
  残件を特定 — 検査 3 ラウンドの提起は通算 7・**7/7 CONFIRMED・誤検出 0**。
- 設計者側欠陥も 2 件検出された(IA-05 記録精密性/NEW-01 宣言未履行)— 検査は工場だけでなく
  **測定系(設計者)にも効いた**。両件とも即日是正。
- 報告全文: [independent-inspection-eco-006.md](independent-inspection-eco-006.md) /
  [independent-reinspection-eco-006.md](independent-reinspection-eco-006.md) /
  [independent-reinspection-2-eco-006.md](independent-reinspection-2-eco-006.md)。

