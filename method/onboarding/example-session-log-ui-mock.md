# 作業ログ実例(通し読み用・UI モック編) — BookLog のモックを受入検査して CAD 化する

> これは**模擬ログ**である([example-session-log.md](example-session-log.md) の BookLog を題材に、
> Phase 2 のモック提出直後〜UI-BOM 化までを拡大した続編。実在の適用 prospective-01 の実測出力を圧縮)。
> 👤 = 人間の入力(**全文掲載**)。🤖 = 設計者 AI の応答(**要点のみ抜粋**)。💻 = 治具の出力(実形式)。
> 読みどころ: 人間の入力は全部で **7 回**。AI が先へ進めない場所はすべて**治具の exit code**
> (順序違反の拒否・hearing の exit 3「戻れ」・gate-cad の施錠)。「1 に戻る」ループは
> 台帳が収束させるので、回るたびに安くなる。

対応する正典: [ui-ir-ui-bom.md](../ui-ir-ui-bom.md) §17(受入検査)/§17.1(参照モデル)/§17.2(コマンド化)。
コマンドは bomdd-init が製品リポへ設置する(`/bomdd-refmodel` → `/bomdd-mock-lint` → `/bomdd-ui-cad`)。

```text
1. モック作成(人間・自由)
2. /bomdd-refmodel  … 一般概念モデルとの gap → ①〜④ヒアリング(skip 可・理由必須)
   ②検討漏れ → 1 に戻る(治具 exit 3)
3. /bomdd-mock-lint … 矛盾検査+カバレッジ+隣接質問+復唱
   実在矛盾・blocking → 1 に戻る
4. /bomdd-ui-cad    … 決定的抽出→候補→裁定→UI-BOM(lint 合格まで治具が施錠)
```

---

## 0. 前提

BookLog(example-session-log.md §3)の続き。モック(一覧+編集モーダル)は `BookLogUI/資料/` にあり、
§12.1 のスナップショット治具で状態ごとの snapshot 化と `ui-extract.py` の raw IR 抽出が済んでいる。

**👤 akira:**
```
/bomdd-refmodel
```

**🤖 AI:**
> 検査ワークスペースを初期化します(manifest+隔離ステージング)。

```
💻 python {BomDD}/method/tools/ui-mock-inspect.py init --dir bomdd/ui/book-v1 \
     --mock design-notes.md snapshot-list.html snapshot-edit.html ui-ir.raw.list.json ui-ir.raw.edit.json
[ok] manifest 5 files / staging: ...\bomdd\ui\book-v1\staging
💻 ... emit-prompt --dir bomdd/ui/book-v1 --stage refmodel
[ok] prompt-refmodel.md を合成しました(正典 ui-mock-refmodel.md / sha256 4524fc35746e…)
```

> 合成プロンプトで**隔離サブエージェント**を起動しました(読めるのはステージング 5 ファイルのみ。
> 実装・台帳・git は不可視)。……報告書を受領、機械検査にかけます。

```
💻 ... check --dir bomdd/ui/book-v1 --stage refmodel --report refmodel-report.md
[pass] refmodel: 違反 0(警告 0)
```

> 製品クラス較正: 「個人用・ローカル完結の記録台帳アプリ(単一ユーザー・SQLite)」。
> 参照モデル 12 カテゴリとの差分 = **gap 6 件**。ヒアリングをお願いします
> (①意図的な非採用 / ②検討漏れ / ③スコープ外 / ④フェーズ計画):
>
> | # | gap | コスト | 要点 |
> |---|---|---|---|
> | 1 | 空状態(蔵書 0 冊・初回起動) | high | 起動直後は必ず通るのに snapshot が無い |
> | 2 | エラー提示(DB 書込失敗・破損) | high | ローカル DB を持つ以上、異常系は標準 |
> | 3 | 検索 0 件の表示 | medium | 検索がある以上、0 件は日常の状態 |
> | 4 | バックアップ/エクスポート | medium | 一人の記録資産の保全は同クラスの標準 |
> | 5 | アプリ定型設備(About・設定) | medium | デスクトップ慣習 |
> | 6 | ウィンドウサイズ・位置の記憶 | low | 常用ツールの定型 |

## 1. ヒアリング → ループ発動(治具が「戻れ」と言う)

**👤 akira:**
```
1.② 3.② は確かに忘れてた。2.④ 5.④ は後のバージョンで。4.③ 6.③ はスコープ外。
```

**🤖 AI:**
> 回答を台帳へ原子記入します(ruling+status+decided_at がセット。negative 側も自動で残る)。

```
💻 ... hearing --answers hearing-r1.yaml --rulings bomdd/ui/book-v1/37-ui-rulings.yaml
[ok] 台帳へ 6 件を原子記入(0→6件・UQ-0006 まで)
[flow] ②検討漏れ あり → モック改訂へ戻ってください(1 に戻る)
(exit 3)
```

> **exit 3 = ループ発動**です。UQ-0001(空状態)と UQ-0003(検索 0 件)の実装として
> モックの改訂をお願いします。①③④の 4 件は台帳資産になったので**二度と質問されません**。

## 2. 寄り道: 順序を飛ばそうとすると治具が拒否する

**👤 akira:**
```
モック直すのは明日にして、先に CAD 化を見てみたい。/bomdd-ui-cad
```

**🤖 AI:**
> 起動条件を検査します。

```
💻 ... gate-cad --dir bomdd/ui/book-v1
[NG]   lint が未合格(/bomdd-mock-lint を実行)
[fail] CAD 工程は施錠中(exit 1)
```

> **施錠中のため停止します**。lint 合格が解錠条件です(これはセッションの裁量では緩められません)。
> 明日、モック改訂 → /bomdd-mock-lint の順でお願いします。

## 3. モック改訂 → 2 周目は skip が効く

**👤 akira:**
```
直した。空状態は「最初の1冊を登録しましょう」+登録ボタン、検索0件は「見つかりませんでした」。
snapshot を2枚追加してある。
```

**🤖 AI:**
> manifest を作り直し(7 files)、refmodel は **skip** します(R1 で 6 裁定済み・本改訂はその実装。
> スキップも理由付きで来歴に残ります)。

```
💻 ... init --force --dir bomdd/ui/book-v1 --mock ...(7 files)
💻 ... skip --stage refmodel --reason "R1 で 6 裁定済み(UQ-0001〜0006)。本改訂はその実装でありスコープ変化なし"
[ok] refmodel を skipped として記録
```

## 4. /bomdd-mock-lint — 矛盾と質問(自分では気づかない型)

**👤 akira:**
```
/bomdd-mock-lint
```

**🤖 AI:**
> 合成プロンプトで隔離サブエージェントを起動 → 報告書受領 → 機械検査:

```
💻 ... check --dir bomdd/ui/book-v1 --stage lint --report lint-report.md
[pass] lint: 違反 0(警告 0)
[ok]  CAD 工程を解錠しました(/bomdd-ui-cad が実行可能)
```

> 書式・予算は合格(**解錠は書式合格であって内容決着ではありません** — 内容は次の裁定と、
> CAD 段の GU3 が止めます)。内容の要点:
>
> **矛盾候補 2 件**(注記 vs DOM):
> - C1: 注記「行をクリックすると編集モーダル」なのに、一覧の行に**操作可能の痕跡が無い**
>   (cursor 注記なし・raw IR の interactable 0 件)。このまま製造すると行クリックが翻訳から漏れる
> - C2: 空状態の登録ボタンは「登録する」、ツールバーは「+」— 同一操作の文言不一致
>
> **隣接質問 3 件**(抜粋・コスト順):
> - Q1 [high] 検索と並び替えは直交か(検索中に並び替えを変えたら両方効くか)
> - Q2 [high] 編集モーダルの閉鎖経路(キャンセル/Esc/スクリムクリック)
> - Q3 [medium] 評価の未入力は許すか(0 扱いか「未評価」か)
>
> **復唱文**(抜粋 — Yes/No で答えられます):
> 「削除は確認ダイアログの後、即時に行が消え、取り消せない」
> 「検索対象はタイトルと著者の両方である」…

**👤 akira:**
```
C1 はモックの落ち度なので行に pointer を付けた。C2 は「+」に統一した。
Q1 は直交(両方効く)。Q2 はキャンセルと Esc。スクリムでは閉じない。Q3 は未評価を許す(表示は —)。
```

**🤖 AI:**
> 裁定 5 件を 37 台帳へ記録。モック改訂分は `ui-extract.py` を再実行(決定的なので差分は
> cursor 痕跡の 1 箇所だけ)。裁定済みの質問は台帳にあるので、以後どの工程が再質問しても
> **人間に届く前に台帳突合で消えます**(prospective-01 実測: 18 問中 6 問が自動決着)。

## 5. /bomdd-ui-cad — 施錠が解けているので §12 パイプラインへ

**👤 akira:**
```
/bomdd-ui-cad
```

```
💻 ... gate-cad --dir bomdd/ui/book-v1
[pass] CAD 工程は解錠済み(lint 合格+refmodel 決着)
```

**🤖 AI:**
> §12 パイプラインを実行します:
> 1. **決定的抽出**(再抽出 — バイト同一を確認)
> 2. **AI 意味候補**: raw に無いノードは作らない・final 確定はしない。曖昧 2 件のうち 1 件は
>    **辞書ヒットで自動解決**(「登録する」=「+」と同一コマンド — さっきの C2 裁定が資産になった)。
>    残 1 件だけ質問します: 「読了日」クリアの意味(未読に戻す?)→ 裁定待ち
> 3. 裁定反映 → `ui-bom.json`+`ui-trace-map.json` 生成
> 4. ゲート:

```
💻 python {BomDD}/method/tools/ui-cad-gate.py --mock snapshot-list.html
GU1 raw会計 ok / GU2 会計 ok / GU3 裁定 ok / GU4 来歴 ok / GU5 追跡 ok / GU6 id揺れ ok
exit 0
```

> **GU 全 PASS — E-BOM / M-BOM へ昇格可能**です。以降は本編ログの Phase 3(BOM・工程設計)へ続きます。

---

## 読みどころの再掲(このログで治具が止めた場所)

| 場所 | 止め方 | 意味 |
|---|---|---|
| hearing 後 | **exit 3** | ②検討漏れ → モック改訂へ「戻れ」(ループはコマンドの正式な出口) |
| CAD 先回り | **gate-cad exit 1** | lint 未合格では CAD 化できない(セッション裁量で緩められない) |
| 報告書の書式・予算 | **check exit 1** | 質問 ≤20・gap ≤15・コスト降順・①〜④形式を機械強制 |
| blocking 未裁定 | **GU3** | 内容の決着は CAD 段のゲートが最終防衛線 |

人間がしたことは、**モックを自由に作る・①〜④で答える・矛盾の側を直す・裁定する**の 4 種類だけである。
検査の実測値(検出率・ノイズ率・台帳収束)は FINDINGS §10.1〜10.3 を参照。
