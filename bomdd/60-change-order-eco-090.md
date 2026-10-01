# Change Order — ECO-090(M-BOM / Control Plan 再設計の基準計数と、製品側の試行〔ViewPrism2 ECO-143〕の記録 / 記録のみ)

> 指示: user 2026-10-02「BomDD 側の記録を起票して」。経緯= ECO-089 verified の後、M-BOM / Control Plan の再設計について議論 →
> 7 リポの基準計数(user AGREE)→ 主 2 本の受入経路の調査(user「B」= 起票前に事実を確かめる)→ 方法論の文書より先に製品で試す(user「B」)→
> ViewPrism2 ECO-143 を起票・製造・受入(裁定 A・golden n/a 受理)。本 ECO はその記録を方法論リポへ残す。
> **起票と記録を同一 commit で行う**(記録のみ・ECO-088 の型)。受入は製造者較正のみ。verified 昇格は self-conformance PASS と CI 結論を観測した後の受入 commit で。

## 担当設備(equipment)

- 起票・記録: requested/resolved `claude-opus-5-5`・Claude Code・来歴 **self-reported**
- producer: EQ-004
- 独立検査: なし(記録のみ・製造者較正のみ。inspector 行は置かない)
- 設備の変化: ECO-089 の producer は EQ-005。途中でモデルを切り替えたため、本 ECO は EQ-004 で起票する。

## 0. 実測(起票根拠・2026-10-01〜02)

証拠の所在= [bomdd/reports/eco-090-redesign-baseline/](reports/eco-090-redesign-baseline/preregistration.md)。

### 0.1 7 リポの基準計数(数え方は実行前に固定 — preregistration.md)

主の根拠= ViewPrism2・ViewTube(一般的なアプリに近い)。TimetableAdv はゲームで別枠、サンプル 3 本は参考(user の位置づけ)。

- **不変条件は検査行にほぼ届かない**: ViewTube 0/17・ViewPrism2 3/15(ECO-086 の基準線と一致 — 計器の対照)。
  M-BOM は不変条件を自分の言葉で持つ(ViewTube 90 行・INV 番号 0・E-BOM と完全一致 0 / ViewPrism2 69 行・番号 16・一致 1)—
  写しの重複ではなく、E-BOM と機械で突き合わせられない並行の記述。
- **「いつ測るか」は CP の行に欄が無い(読めた 5 本とも 0)が、工程表の側から CP を指す形がある**: ViewTube 33/41・Plm 17/21・Transfer03 10/10、
  ViewPrism2 は 16/65(主 2 本で揃わない)。「落ちたら何をするか」は 0 本。ViewTube の `sampling`・`stop_condition` は件数と不合格の基準で、処置ではない。
- **CP の層は主 2 本で揃わない**: ViewPrism2 は単位の行が中心(65 中 41)、ViewTube は単位をまたぐ行(治具を除いて 13)と要求直結(13)が中心で単位は 4。
  どちらの形にも一般化しない(事前登録の読み方)。
- **単位間の接続を検査する行は無い**: ViewTube 0/11・Plm 0/29。ViewPrism2 は M-BOM に依存の欄が無く測定不能(依存は E-BOM 側に 44/44)。
- **文脈面積の代理(単位ごとの参照数の中央値)**: ViewPrism2 5・ViewTube 8・TimetableAdv 11(最大 41)。基準線として採るのみ。
- **製造単位の繰り返し(標準 M-BOM 案の効果の見積もり)**: 7/7 に出るのは受入治具だけ(テンプレートが配るコピー型)。永続化は 5/7 だがライブラリが揃わない。
  ログ・設定・入力検証は製造単位として 0/7(単位の中に埋もれる横断的関心事は ID では数えられない — 過小評価の側)。
- 測定の限界: 字面と YAML 構造のみ・各 1 回・作業木 dirty のリポあり(TimetableAdv 2149・ViewTube 1)。実行後の計器修正 3 点と追加計数 1 点は baseline.md と routing-cp.md に明記。

### 0.2 主 2 本で受入を実際に決めているもの([acceptance-paths.md](reports/eco-090-redesign-baseline/acceptance-paths.md))

- 2 本とも**人の承認**が決める。CI は無く、フックは記録の形式を見る。CP は受入の**出力**(観点の追記先)で、判定の入力として読まれない。
- ViewTube は、監督つき受入実行が毎回「合格なし・終了コード 9」を返し、件数と利用者の言葉で読み替えて受け入れている(原因未確認)。

### 0.3 製品側の試行 — ViewPrism2 ECO-143(applied 2026-10-02)

- 機械受入のテスト結果(xUnit XML・各テストの trait cp)を、CP の行ごとに 違反 / 合格 / 測定不能 / 未実行(人の承認で検査)/ 未実行(検査なし)で集計し、
  承認の依頼に添える。機械では止めない(ViewPrism2 の裁定 A)。区分は ECO-089(plm-diag/2)に対応させ、「検査なし」だけを意図した違いとして分けた。
- 初回の表は事前登録の予測と完全一致(検査なし 4・人の承認 3・retired 1・台帳外 ID 2・合格 57)。「974/974」の件数はこれらを見せていなかった。
- 製造中の発見: 呼び出し側の `-p:TestingPlatformCommandLineArguments` は既定引数を丸ごと置き換え、HangDump(fail-closed)が黙って外れる —
  起票前の技術確認の実行がその状態で走っていた。報告の引数は既定の側へ足した。
- 試行の評価は ViewPrism2 側で回収する(次の 3 件の ECO の承認で、表を見た処置が起きたか)。

## 1. 変更要求(凍結・記録のみ)

1. `bomdd/reports/eco-090-redesign-baseline/` に、事前登録・計数スクリプト 3 本(baseline-count.py・routing-cp.py・key-inventory.py)・結果 2 本・受入経路の調査を保存する。
2. `method/improvements.md` に本節と、OBS 3 件・EXP 1 件(CP が受入の出力として使われる/ViewTube の常に赤の計器/標準 M-BOM 案と文脈境界案の着手条件/ViewPrism2 試行の評価)。
3. `bomdd/60-change-register.yaml` に本 ECO を登録。

**採らない**: playbook・テンプレート・スキーマ・ツールの改訂(試行の評価の前に文書へ書かない — ViewPrism2 で試してから文書にする、という user の選択)/
ViewTube の常に赤の計器の是正(ViewTube 側の ECO の領分)/ 標準 M-BOM 案・文脈境界案の着手(着手条件つきの記帳のみ)/ EXP-20261001-01 の回収(再設計の前後比較はまだ無い)。

## 2. 影響なし予測(製造前・凍結)

diff= improvements.md+台帳系(order・register・reports)のみ。method/ の playbook・templates・schemas・tools、hooks・.github は diff 0。
C10 判定不変・C13 リンク不変・C16(本 order と improvements.md の節に裁定の語を置かない)・worklist 警告 0。製品リポへは非波及。

## 3. 受入条件(製造前に凍結・二部形)

- V1(条件): reports に 7 ファイル(preregistration.md・baseline-count.py・baseline.md・routing-cp.py・routing-cp.md・key-inventory.py・acceptance-paths.md)があり、
  baseline.md の M4 の値が ECO-086 の基準線(ViewPrism2 3/15・ViewTube 0/17・Plm 1/10・Transfer03 0/8)と一致すること — 検査法: ls と実読。
- V2(条件): improvements.md の本節に OBS 3 件・EXP 1 件があり、`python method/tools/worklist.py` の警告が 0 であること。
- V3(条件): diff が allowed_paths のみで、method/ の playbook・templates・schemas・tools と hooks・.github が diff 0 であること — 検査法: `git diff --stat baseline..head`。
- V4(条件): self-conformance 全 PASS(exit 0 観測後に commit)・CI success であること。
- V5(条件): 製造者較正のみ・較正 receipt(trigger ①)があること。

## /preflight receipt(起動経路: **自発** — 既裁定の記録)

- 分類= 既裁定の記録(user「BomDD 側の記録を起票して」)。baseline `efa9864`= **confirmed**(作業木 clean・push 済み)/ 次番 090= **confirmed**(register に id 0 件)/
  記録する計数が作業用の場所にある= **confirmed**(scratchpad/redesign の 6 ファイル)/ 同じファイルを窓に持つ進行中の ECO がない= **confirmed**(ECO-089 は verified・窓閉鎖)/
  EQ-004 が設備台帳にある= **confirmed**(70-equipment.yaml・status active)。
- discovered(推測・契約外): 計数のスクリプトは製品リポの場所を絶対パスで持つ(ECO-086 inv-reach.py と同じ型)— 再実行は同じ配置の環境に限る。
- 開始判定: **PROCEED**・override 0。
