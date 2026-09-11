---
name: handoff
description: AI→人間のハンドオフ・プロトコル。ターンを終えて人間へ制御を渡すメッセージごとに、interaction(INFORM/DECIDE/DISCUSS/REQUEST)と execution(CONTINUING/BLOCKED/COMPLETE/PAUSED)を先頭 1 行で宣言し、mode ごとの必須要素を満たしてから送る。人間が「報告か・質問か・議論か・AI は止まっているか」を逆推論しなくて済むようにする通信契約。長い報告・裁定要求・設計議論・完了報告・中断報告のすべてが対象。
---

# /handoff — AI→人間の制御移譲プロトコル

> 出自: 2026-09-11 BomDD ECO-062 Phase 5 run-01 の報告に対する user 批評 —「裁定に必要な入力」と「実験報告」が混ざり、
> 人間の仕事が裁定でなく再分析になった(REPORT としては良いが RULING REQUEST として弱い)。改善は文章術ではなく
> **応答の型付け**で行う。本スキルは BomDD の方法論ではなく **ハーネス側の通信規約**(所在は `.claude/skills/` のみ・
> user 裁定 2026-09-11 1:A・product-profile 非接触・計測後に正本化を判断)。
>
> 構造: **§1 契約(normative・小さく固定)**と **§2 実装規則(交換可能)**を分離する。契約は「何を宣言し何を含むか」だけを
> 決め、書き方・個数・順序は実装側に置く。モデルや用途が変わっても契約は変えない。

## 1. 契約(HANDOFF CONTRACT v0.2・normative)

> v0.1 → v0.2(2026-09-11・user DECIDE「A」): 第 4 の mode **REQUEST**(人間に作業を依頼し成果物を待つ)を追加。契機= run-02 の運転員依頼を INFORM で送り
> user が訂正(INFORM は人間のアクションなしの型)— EXP-20260911-01 の mode 訂正 1 件目。

```text
HANDOFF CONTRACT v0.2

Scope:
  A handoff is the message that ends the AI's turn and returns control to the human.
  Intermediate progress lines within a turn are not handoffs.

Every handoff starts with:
  [INFORM|DECIDE|DISCUSS|REQUEST / CONTINUING|BLOCKED|COMPLETE|PAUSED]

Single mode:
  One handoff declares exactly one interaction mode.
  Content belonging to another mode goes to a separate handoff, or to an
  explicitly delimited appendix after the packet. The appendix must not
  contain questions or decisions.

INFORM requires:  information being handed off / human_action: none / execution state explanation
DECIDE requires:  decision_question / options / recommendation / reply_format / execution state explanation
DISCUSS requires: discussion_question / thesis / reasoning / counterpoint /
                  what_would_change_thesis / explicit non-decision status
REQUEST requires: request (what the human is asked to do) / deliverable (what to return, in what form) /
                  why_human (why the AI cannot do it itself) / execution state explanation
                  The reply to a REQUEST is the deliverable itself. INFORM never asks for human action.

Execution states:
  CONTINUING = the AI keeps working after this handoff
  BLOCKED    = an input or ruling required to proceed with the current request is missing
  COMPLETE   = the requested scope is finished (verified or explicitly not)
  PAUSED     = work is intentionally suspended, independent of whether it could proceed

Before sending:
  1. validate header combination
  2. validate required fields exist                        (structural check)
  3. validate message purpose agrees with declared mode    (semantic self-check)
  4. validate single mode (no undeclared-mode content outside the appendix)
  5. rewrite if invalid
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

ガード: 慣例・コード・台帳で確かめられる判断を DECIDE にしない(自律の範囲)。逆に、人間の裁定事項を DISCUSS に逃がさない
(コミット回避の動機を疑う)。「〜しますか?」「必要なら言ってください」で終わる末尾付加は、隠れた DECIDE か隠れた DISCUSS —
本体に昇格させるか削る。

### 2.2 生成(generate)— mode ごとの default

- 共通: パケット本体は 15 行程度。監査記録(実験結果・ログ・全所見)は **リポのファイルに置きパスで参照**する — メッセージは
  記録の射影であって記録ではない。数値には限定子を付ける(機構の性能か・人間や運転員の判断込みか・N・未測定の failure class)。
  人間や運転員の判断で救われた例は機構の成功に数えない。
- INFORM: 分かったこと → 意味・示唆(必要なら)→ `human_action: none` → execution の 1 行(次の一手 / 未実施項目 / 再開条件)。
- DECIDE: decision_question は 1 文で、回答により状態が確定する形。options は 2〜4 個を default とし、相互排他・各 1 行の帰結つき。
  独立した裁定を 1 つの options に混ぜない(複数なら依存順に並べ、番号を振る)。recommendation は options の 1 つを名指しし、理由は
  観測の羅列でなく「何が示せて何が示せないか」。reply_format は人間の返答コストを固定する(例: `A` / `1:A 2:B` / `OTHER: 理由` / `MODIFY: 条件`)。
- DISCUSS: discussion_question は範囲が一意に分かる問い(A/B 形に限定しない)。thesis はその問いへの現在の回答 1 文。reasoning は 3 点以内。
  counterpoint は自分の thesis への最強の反論 1 点。what_would_change_thesis を 1 行。末尾に「裁定要求ではない」と、返答の形(`AGREE` /
  `DISAGREE: 理由` / 自由記述)。
- REQUEST: request は 1 段落(何を・どこで・どの手順書で)。deliverable は返答の形をそのまま示す(貼れる書式)。why_human は 1 行
  (例: 「運転員= 人間という実験設計」「私の権限外」「私が触ると測定が汚れる」)。作業の所要目安を添える。
- 付録: 主モード以外の内容を同じメッセージに残す場合は、パケットの後に `---` と `付録(INFORM・返答不要)` の見出しで区切る。
  付録に疑問文・裁定・「〜しますか」を置かない。

### 2.3 検査(validate)— 構造検査と意味自己検査は別計器

```text
structural(lint・機械的に判定できる)
  H1 先頭行が [mode / execution] の形で、語彙内
  H2 組合せが有効(INFORM/BLOCKED は無効 — 人間の返答を待つなら DECIDE か DISCUSS へ)
  F1 mode の必須要素がすべて存在する(見出し・ラベル・または明瞭な 1 文)
  F2 DECIDE: options が列挙され、reply_format がある
  F3 DISCUSS: discussion_question と thesis が両方ある
  F4 REQUEST: request・deliverable・why_human がある。INFORM に human_action あり(依頼・疑問文)は F1 違反= REQUEST か DECIDE へ再分類
  M1 付録の外に、宣言外モードの内容(疑問文・裁定・議題・依頼)がない

semantic(self-review・自己申告 — 較正は人間の mode 訂正回数で外から測る)
  P1 メッセージの目的が宣言した mode と一致する(読み手が「私は何をすれば?」と問わずに済むか)
  P2 DECIDE: recommendation が evidence から従い、限定子が主張を実際に絞っている
  P3 DISCUSS: thesis が discussion_question への回答になっている・counterpoint が thesis を実際に脅かす
  P4 execution が本文と矛盾しない(BLOCKED なのに作業継続を書いていない・COMPLETE なのに未実施が隠れていない)
```

### 2.4 書き直し(rewrite)

FAIL があれば送る前に書き直す。default 上限 2 回。上限で残る FAIL は末尾に `self-check: FAIL <id>(理由)` を 1 行で自己申告する
(未収束を収束と報告しない — converge と同じ形)。structural PASS / semantic self-check PASS は将来別々に較正できるよう、申告時は id で区別する。

### 2.5 DISCUSS の収束(default)

同じ discussion_question で 3 往復して thesis が動かないなら、DECIDE に切り替えて人間に確定を求める(裁定点へ写す)。
BLOCKED の DISCUSS に返答がない間、AI は既定の thesis で進んではいけない。

### 2.6 BomDD の停止語彙との対応(参考)

NORMATIVE_RULING / CONVERGENCE_LIMIT → DECIDE/BLOCKED。PREFLIGHT_HOLD → DECIDE/BLOCKED(入力が要る)か INFORM/PAUSED(待つだけ)。
VERIFICATION_FAIL → 是正中なら INFORM/CONTINUING、是正方針が分岐するなら DECIDE。LEDGER_INCONSISTENT → 裁定材料を DECIDE で提示
(原文パス提示・要約しない)。

### 2.7 適用外

ターン途中の進捗の一行(バックグラウンド待ちの呟き等)。user が「形式なし」を指示したメッセージ。

## 3. 例(最小形)

```text
[INFORM / COMPLETE]
ECO-065 verified(CI 34516211684 success・register verified・窓閉鎖)。詳細= bomdd/60-change-order-eco-065.md §7。
human_action: none。未実施= なし。次の裁定材料は別 handoff で出す。
```

```text
[DECIDE / BLOCKED]
decision_question: Phase 6(狭い自動起動)を今開くか。
options: A 開く(帰結: 自動起動 job で witness 再検証が機構として効くかを次に測る)/ B 保留し run-02 を先に(帰結: operator rescue 依存を切り分けてから)
recommendation: B。fail-open 0/7 は運転員+検証器の性能で、2 件は運転員の仕様外行動に依存し、dirty 腕は狙った failure class を未測定。
reply_format: A / B / OTHER: 理由
execution: BLOCKED — Phase 6 の作業は回答まで着手しない。
```

```text
[DISCUSS / PAUSED]
discussion_question: 契約 v0 に「handoff の定義」と「1 パケット 1 主モード」を契約側として足すか。
thesis: 足す。どちらも実装規則でなく通信契約の側の制約。
reasoning: (3 点以内)
counterpoint: 分割でメッセージ数が増える。
what_would_change_thesis: 付録方式で裁定の再分析が起きなければ分割は実装の選択に落とす。
裁定要求ではない。返答: AGREE / DISAGREE: 理由 / 自由記述。
```

```text
[REQUEST / BLOCKED]
request: run-02 の R1〜R8 を bomdd/reports/phase5-run-02-brief.md の手順 v2 で実施してください(所要 20〜30 分)。
deliverable: run ごとに `R1 | decision= | code= | 1 行目=` の 1 行+R7 の裁定材料+手順の欠落(なければ「なし」)。
why_human: 運転員= 人間という実験設計(裁定 A)。私が実行すると運転員≠製造者が崩れる。
execution: BLOCKED — 台帳が届くまで採点・R9 に進まない。
```

## 4. 計測(試行・user 裁定 2026-09-11 2:A)

- 単位: handoff 20 回(うち DECIDE 5 回以上)で評価。EXP-20260911-01(improvements.md)。
- 指標: ①人間が mode を訂正した回数 ②「で、私は何をすれば」型の再質問回数 ③DECIDE への返答が reply_format どおり 1 語(またはラベル列)で済んだ比率。
- 基準線(契約前・Phase 5 run-01 報告): 訂正 1・再分析 1・1 語返答 0/1。
- 試行中の記録(契約後): 2026-09-11 mode 訂正 1(run-02 依頼を INFORM で送信・self-check FAIL H2 を申告しつつ送った → user 訂正 → v0.2 REQUEST 追加)。
- 評価後の分岐: 指標が改善しなければ §2 の細則の一部を §1 へ昇格させて再試行。改善すれば product-profile への正本化を ECO で判断する。
