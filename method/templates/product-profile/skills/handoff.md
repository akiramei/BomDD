---
name: handoff
description: AI→人間のハンドオフ・プロトコル(通信契約)。ターンを終えて人間へ制御を渡すメッセージごとに、interaction(INFORM/DECIDE/DISCUSS/REQUEST)と execution(CONTINUING/BLOCKED/COMPLETE/PAUSED)を先頭 1 行で宣言し、mode ごとの必須要素を満たしてから送る。人間が「報告か・質問か・議論か・AI は止まっているか」を逆推論しなくて済むようにする。長い報告・裁定要求・設計議論・完了報告・中断報告のすべてが対象。フリースタイル区間(形式なし)は人間の宣言でのみ開始・終了し、区間内でも裁定・依頼・タスク終了の 1 通は契約に戻る。
---

# /handoff — AI→人間の制御移譲プロトコル(通信契約)

正典: `{{METHOD}}/method/templates/product-profile/skills/handoff.md`(本ファイルの配布元)。

> 本スキルは特定の方法論に属さない **ハーネス側の通信規約** である。AI が人間へ制御を渡すメッセージ(handoff)を
> 型付けし、人間の仕事が「再分析」でなく「裁定・確認・議論」になるようにする。改善は文章術ではなく応答の型付けで行う。
>
> 構造: **§1 契約(normative・小さく固定)** と **§2 実装規則(交換可能・default)** を分離する。契約は「何を宣言し何を含むか」
> だけを決め、書き方・個数・順序は実装側に置く。モデルや用途が変わっても契約は変えない。
> 運用環境に固有の対応(停止語彙との写像・記録の所在・出自)は末尾の **adapter 区画** に置く — core は環境を知らない。

## 1. 契約(HANDOFF CONTRACT v0.4・normative)

```text
HANDOFF CONTRACT v0.4

Scope:
  A handoff is the message that ends the AI's turn and returns control to the human.
  Intermediate progress lines within a turn are not handoffs.
  A turn that ends only to wait for a harness notification (background task,
  no human action, automatic resumption) is a handoff of mode INFORM / CONTINUING
  in the wait form: what is awaited and what depends on it, nothing else.

Free-style span:
  The contract applies by default. A free-style span begins and ends only by
  the human's declaration; inside it, messages carry no header and no required
  fields. The AI never enters a span by its own inference.
  One-way ratchet: if, inside a span, a message needs a decision, asks the
  human for work, or ends a task turn, that single message returns to the
  contract and says the span continues. Task -> conversation is the human's
  switch only; conversation -> task is automatic for that message.

Every handoff starts with:
  [INFORM|DECIDE|DISCUSS|REQUEST / CONTINUING|BLOCKED|COMPLETE|PAUSED]

Valid combinations (anything else is a structural FAIL and is not sent):
             CONTINUING  BLOCKED  COMPLETE  PAUSED
  INFORM        yes        no       yes      yes
  DECIDE        yes        yes      no       yes
  DISCUSS       yes        yes      no       yes
  REQUEST       yes        yes      no       no
  (INFORM never waits on the human, so INFORM/BLOCKED is invalid; a finished
   scope with a pending question is DECIDE/BLOCKED or /PAUSED, not /COMPLETE.)

Single mode:
  One handoff declares exactly one interaction mode.
  Content belonging to another mode goes to a separate handoff, or to an
  explicitly delimited appendix after the packet. The appendix must not
  contain questions or decisions.

INFORM requires:  information being handed off / human_action: none / execution state explanation
DECIDE requires:  decision_question / options, each with its consequence (gain, loss, reversibility) /
                  recommendation, including why the other options are worse / reply_format /
                  execution state explanation
                  Independently decidable items are numbered as separate decisions so each
                  can be adopted or rejected on its own.
DISCUSS requires: discussion_question / thesis / reasoning / counterpoint /
                  what_would_change_thesis / explicit non-decision status
REQUEST requires: request (what the human is asked to do) / deliverable, as a fill-in form the human
                  returns as is (every expected line with its fields) /
                  why_human (why the AI cannot do it itself) / execution state explanation
                  The reply to a REQUEST is the deliverable itself. INFORM never asks for human action.

Execution states:
  CONTINUING = the AI keeps working after this handoff
  BLOCKED    = an input or ruling required to proceed with the current request is missing
  COMPLETE   = the requested scope is finished (verified or explicitly not)
  PAUSED     = work is intentionally suspended, independent of whether it could proceed

Before sending:
  1. validate header combination against the table          (structural check)
  2. validate required fields exist                          (structural check)
  3. validate message purpose agrees with declared mode      (semantic self-check)
  4. validate single mode (no undeclared-mode content outside the appendix)
  5. rewrite if invalid. A structural FAIL is a hard stop: the handoff is not
     sent with a self-reported FAIL. Only an unresolved semantic self-check
     may be reported and sent.
```

契約が言わないこと: options の個数・reasoning の個数・行数・出現順・分類の手順・書き直し回数・DISCUSS の収束法。これらは §2。

## 2. 実装規則(交換可能・default)

### 2.1 分類(classify)— 決定木を上から当て、最初に yes になったところで決める

```text
Q0 人間にしかできない作業(私が代行できない・してはいけない)を頼み、その成果物を待つ必要があるか
     yes → REQUEST(成果物が返るまで BLOCKED。独立に進められる部分があれば CONTINUING で名指し)
Q1 私の次の行動が、人間にしか決められない選択で分岐するか
     yes → DECIDE。分岐に依存しない部分があれば CONTINUING(独立部分は進める・依存部分を名指し)、なければ BLOCKED
Q2 私に立場はあるが、コミットする前に人間の見解で変わりうる論点があるか
     yes → DISCUSS(execution は作業状態に従う。コミットを意図的に保留しているなら PAUSED)
Q3 それ以外 → INFORM(CONTINUING / COMPLETE / PAUSED のいずれか)
```

ガード: 慣例・コード・記録で確かめられる判断を DECIDE にしない(自律の範囲)。逆に、人間の裁定事項を DISCUSS に逃がさない
(コミット回避の動機を疑う)。「〜しますか?」「必要なら言ってください」で終わる末尾付加は、隠れた DECIDE か隠れた DISCUSS —
本体に昇格させるか削る。

待機: ターンがハーネス通知待ち(バックグラウンド処理の完了など)だけで終わるなら、決定木を通さず INFORM/CONTINUING の**待機形**(§2.2)。

区間: フリースタイル区間内(§1・人間が宣言済み)では決定木を Q0/Q1 の検出にだけ使う — yes ならその 1 通は契約に戻り「区間は継続」と書く・no なら形式なし。
区間に入るのは人間の宣言だけ(「会話だと思ったので形式を落とした」は違反)。区間の終了も人間の宣言(タスク指示が来たら、それを終了宣言とみなしてよいが、その旨を最初の handoff に書く)。

### 2.2 生成(generate)— mode ごとの default

- 共通: パケット本体は 15 行程度。**詳細な証拠(実験結果・ログ・全所見)は system of record に置き、handoff はそれを参照して再現しない** —
  メッセージは記録の射影であって記録ではない。system of record が何か(リポのファイル・課題管理・ドキュメント基盤・データベース・CI の成果物)は環境が決める(adapter)。
  数値には限定子を付ける(機構の性能か・人間や運転員の判断込みか・N・未測定の failure class)。人間や運転員の判断で救われた例は機構の成功に数えない。
- INFORM: 分かったこと → 意味・示唆(必要なら)→ `human_action: none` → execution の 1 行(次の一手 / 未実施項目 / 再開条件)。
  **待機形**(ハーネス通知待ちでターンが切れるとき): ヘッダ+「何を待つ・何がそれに依存する」の 1〜2 行のみ。同じ待機が続いても本文を増やさない
  (読み飛ばせることが価値 — 実運用では待機通知が handoff の過半を占める)。
- DECIDE: **decision_question を本文の先頭に置く**(1 文・回答により状態が確定する形。状態報告や経緯は末尾か付録へ — 人間が探すのは質問)。
  options は 2〜4 個を default とし相互排他。**各案を同じ形で並べる**: `得るもの / 失うもの / 戻せるか / 採ると次に何が起きる`(表または同順の 1 行)。
  独立に採否できる項目は 1 案に束ねず番号を分ける(人間が `1:A,A',C` のように部分採択できる形。依存があれば依存順に並べる)。recommendation は
  options の 1 つを名指しし、理由は観測の羅列でなく「何が示せて何が示せないか」+**非推奨案がなぜ劣るか 1 行**。reply_format は人間の返答コストを
  固定する(例: `A` / `1:A 2:B` / `OTHER: 理由` / `MODIFY: 条件`)。
- DISCUSS: discussion_question は範囲が一意に分かる問い(A/B 形に限定しない)。thesis はその問いへの現在の回答 1 文。reasoning は 3 点以内。
  counterpoint は自分の thesis への最強の反論 1 点。what_would_change_thesis を 1 行。末尾に「裁定要求ではない」と、返答の形(`AGREE` /
  `DISAGREE: 理由` / 自由記述)。
- REQUEST: request は 1 段落(何を・どこで・どの手順書で)。deliverable は**穴埋め様式**— 返してほしい行を欄名つきで全部並べ、記入例を 1 行添える。
  人間はそれを埋めて返す(様式なしで依頼すると回収に追加の往復が要る)。欄が埋まらずに返ったら再 REQUEST の前に様式の欠陥を疑う。why_human は 1 行
  (例: 「人間が実施するという実験設計」「私の権限外」「私が触ると測定が汚れる」)。作業の所要目安を添える。
- 付録: 主モード以外の内容を同じメッセージに残す場合は、パケットの後に `---` と `付録(INFORM・返答不要)` の見出しで区切る。
  付録に疑問文・裁定・「〜しますか」を置かない。

### 2.3 検査(validate)— 構造検査と意味自己検査は別計器

```text
structural(lint・機械的に判定できる)
  H1 先頭行が [mode / execution] の形で、語彙内
  H2 組合せが §1 の許容表にある(INFORM/BLOCKED は無効 — 人間の返答を待つなら DECIDE / DISCUSS / REQUEST へ)
  F1 mode の必須要素がすべて存在する(見出し・ラベル・または明瞭な 1 文)
  F2 DECIDE: decision_question が本文先頭にあり、options が各案同形の帰結(得る/失う/戻せるか)つきで列挙され、独立項目は番号が分かれ、reply_format がある
  F3 DISCUSS: discussion_question と thesis が両方ある
  F4 REQUEST: request・deliverable(穴埋め様式・記入例つき)・why_human がある。INFORM に human_action あり(依頼・疑問文)は F1 違反= REQUEST か DECIDE へ再分類
  F5 待機形: ヘッダ+2 行以内
  F6 区間: フリースタイル区間の開始に人間の宣言がある(AI 推定で形式なしにしない)/ 区間内で裁定・依頼・タスク終了を含む通にヘッダと「区間は継続」がある
  M1 付録の外に、宣言外モードの内容(疑問文・裁定・議題・依頼)がない

semantic(self-review・自己申告 — 較正は人間の mode 訂正回数で外から測る)
  P1 メッセージの目的が宣言した mode と一致する(読み手が「私は何をすれば?」と問わずに済むか)
  P2 DECIDE: recommendation が evidence から従い、限定子が主張を実際に絞っている
  P3 DISCUSS: thesis が discussion_question への回答になっている・counterpoint が thesis を実際に脅かす
  P4 execution が本文と矛盾しない(BLOCKED なのに作業継続を書いていない・COMPLETE なのに未実施が隠れていない)
```

### 2.4 書き直し(rewrite)

FAIL があれば送る前に書き直す。default 上限 2 回。**structural(H/F/M)の FAIL は送信停止**— 機械的に直せるものを申告付きで送らない
(申告は検査の代わりにならない)。上限で残る **semantic(P)の FAIL のみ** 末尾に `self-check: FAIL <id>(理由)` を 1 行で自己申告する
(未収束を収束と報告しない)。structural / semantic は将来別々に較正できるよう id で区別する。

### 2.5 DISCUSS の収束(default)

同じ discussion_question で 3 往復して thesis が動かないなら、DECIDE に切り替えて人間に確定を求める(裁定点へ写す)。
BLOCKED の DISCUSS に返答がない間、AI は既定の thesis で進んではいけない。

### 2.6 適用外

ターン途中の進捗の一行(ターンを終えないもの)。**フリースタイル区間**(§1): 人間の宣言で開始・終了し、区間内は形式なし。ただし裁定・依頼・タスクの
ターン終了を含む 1 通はその通だけ契約に戻り「区間は継続」と明記する(片方向ラチェット)。AI の推定で区間に入らない(既定は契約)。
**ターンを終える待機(バックグラウンド通知待ち)は適用外ではなく待機形 INFORM/CONTINUING**。

## 3. 例(最小形・環境非依存)

```text
[INFORM / COMPLETE]
変更 #123 を検証済みで閉じた(CI success・台帳 verified)。詳細= 記録の所在(system of record のパス)。
human_action: none。未実施= なし。次の裁定材料は別 handoff で出す。
```

```text
[INFORM / CONTINUING]
必須検査の終了コード観測待ち。以降(受領証の生成 → commit → push → CI)はすべてこれに依存する。
```

```text
(user: ここからはフリースタイルで)
(形式なしの会話が続く)

[DECIDE / PAUSED]  ← 区間内で裁定が必要になった 1 通だけ契約に戻る
decision_question: …
options: …
reply_format: A / B
execution: PAUSED — 区間は継続(返答後はフリースタイルに戻る)。
```

```text
[DECIDE / BLOCKED]
decision_question: 機能 X の自動起動を今開くか。
options:
  A 開く         — 得る: 自動起動の再検証を次に測れる / 失う: 切り分け前に機構を積む / 戻せる: 可(順序の入替) / 次: 起票
  B 試験を先行   — 得る: 人間の介入依存を切り分けてから開ける / 失う: 1 試験分の時間 / 戻せる: 可 / 次: 試験手順書
recommendation: B。合格 0/7 は運転員+検証器の性能で、2 件は運転員の仕様外行動に依存し、1 クラスは未測定。A が劣る理由: 未測定の failure class の上に自動起動を積む。
reply_format: A / B / OTHER: 理由
execution: BLOCKED — 機能 X の作業は回答まで着手しない。
---
付録(INFORM・返答不要): 試験の記録= <system of record のパス>
```

```text
[DISCUSS / PAUSED]
discussion_question: 契約に「handoff の定義」と「1 パケット 1 主モード」を契約側として足すか。
thesis: 足す。どちらも実装規則でなく通信契約の側の制約。
reasoning: (3 点以内)
counterpoint: 分割でメッセージ数が増える。
what_would_change_thesis: 付録方式で裁定の再分析が起きなければ分割は実装の選択に落とす。
裁定要求ではない。返答: AGREE / DISAGREE: 理由 / 自由記述。
```

```text
[REQUEST / BLOCKED]
request: 手順書 <パス> の手順 1〜8 を実施してください(所要 20〜30 分)。
deliverable(穴埋め・そのまま返す):
  手順1 | 判定= | code= | 1 行目=
  …(手順8 まで同形)
  手順7 issue= / options= / 手順の欠落=(なければ「なし」)
  例: 手順1 | 判定=ADVANCE | code=OK | 1 行目=ADVANCE OK: …
why_human: 人間が実施するという実験設計。私が実行すると独立性が崩れる。
execution: BLOCKED — 成果物が届くまで採点に進まない。
```

---

## BomDD adapter(環境固有の対応 — core は本区画を知らない)

> core(§1〜§3)は環境非依存。本区画は BomDD 方法論の運用環境に固有の写像・所在・出自を置く。他の環境へ配布するときは
> 本区画を差し替える(core は変えない)。

### A1. 停止語彙との対応(参考)

NORMATIVE_RULING / CONVERGENCE_LIMIT → DECIDE/BLOCKED。PREFLIGHT_HOLD → DECIDE/BLOCKED(入力が要る)か INFORM/PAUSED(待つだけ)。
VERIFICATION_FAIL → 是正中なら INFORM/CONTINUING、是正方針が分岐するなら DECIDE。LEDGER_INCONSISTENT → 裁定材料を DECIDE で提示
(原文パス提示・要約しない)。INDEPENDENCE_FAIL / INSPECTION_MISSING → REQUEST(配員のやり直し・独立検査の結果回収を人間に依頼)か DECIDE。

### A2. system of record(BomDD)

詳細な証拠の所在= 変更指示書 `bomdd/60-change-order-eco-NNN.md`・台帳 `bomdd/60-change-register.yaml`・報告 `bomdd/reports/`・改善の追跡 `{{METHOD}}/method/improvements.md`。
運転層の台帳(`.git/bomdd-run/`・witness)は非正本の機械記録で、handoff はその判定行を引用してよいが hash や判定語を転写して正本にしない。

### A3. 出自と計測(BomDD 方法論リポ)

契約 v0.1(2026-09-11・試行開始)→ v0.2(REQUEST 追加)→ v0.3(許容表・DECIDE の得失・REQUEST の穴埋め・待機形/ECO-070)→ v0.4(フリースタイル区間/ECO-071)→ 正本化(ECO-075)。
出自= Phase 5 報告への批評(裁定入力と実験報告の混在)。試行の評価= `{{METHOD}}/method/improvements.md` の 2026-09-11 節(EXP-20260911-01)と 2026-09-12 節(EXP-20260912-01・確定 2026-09-14)。
第三者到達の実測= 異系統ハーネス(Codex)の独立検査報告が契約ヘッダで始まった 6/6。
