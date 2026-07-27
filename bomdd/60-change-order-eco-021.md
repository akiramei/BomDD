# ECO-021 — process-qualification のプローブパスが既定 profile を暗黙前提(adapt 初適用で 3 FAIL+2 無音弱化)

> 状態: **verified(2026-07-27)**。fix= 742be89(CI 緑 run 30244546377)・クローズ実測=
> MoviePad 再適格 PASS(line ready・設置 93ca904・実パス E01 負例 PASS・push 33e416e)。
> 窓は accept で閉鎖(baseline bdb6391 → head 742be89)。

## 製造中の発見(観測 — 本 ECO では是正しない)

**kit 再配布は既存設備を同期しない(仕様)**: bomdd-init は完全な既存設備を検出すると保持する
(「動いている工程設備を上書きしない。更新は手動で」— ECO-017 REV-07 の不完全設備 FAIL と対の
設計)。影響予測の「kit 再配布で同期」は**部分不的中(正直記載)** — 実際の更新経路は
〈正本から byte-identical 複写 → kit/lock 削除・再生成 → 再適格性確認〉の手動 3 手順で、
MoviePad intake の update_note に記録した。**設備更新の装置化**(bomdd-init --update 等)の要否は
観測として還元へ送る — 手動経路の実測 1 例(手数・誤りやすさ)を得たが、rule of three 前に
装置を作らない。

## 裁定(gate ① — 2026-07-27)

- **製造承認(2026-07-27・maintainer — 「製造承認します、裁定 2 点は推奨どおりで」)**。
  baseline を起票コミット bdb6391 とする。
- 裁定 2 点は**推奨案を採択**:
  1. 導出規則= 先頭ディレクトリ型エントリ配下に合成・無ければ先頭エントリ(ファイル型)・
     空/不在なら明示 FAIL。単一関数 `_probe_rel()` を 5 対照が共有。
  2. MoviePad DL-01(protected_paths 15 エントリ・states 既定 2 状態)承認。

## 起票(2026-07-27)

### 発見経緯(実運用初回 — EXP-20260725-03 のトリガー中)

MoviePad を題材とする process-core **実運用初回**の設置中に発見。経過:

1. `bomdd-init --skills-only MoviePad` で設置 → 初回 IQ/OQ **全 PASS**(30 対照+DET)。
   このとき profile は**既定のまま**(`protected_paths: [src/, test/, tests/]`)。
2. MoviePad の実装は**ルート直下配置**(ViewModels/ Views/ Services/ 等・src/ 不在)のため、
   既定の保護パスは実質空 — adapt(差分注入・DL-01)として protected_paths を実レイアウトへ
   差し替え。**profile adapt の実運用初適用**。
3. 再適格性確認 → **FAIL 3 件+無音弱化 2 面**(下記)。適格性ゲートは
   「process-qualification: FAIL — 製造を開始しない」で**正しく製造を止めた**。

### 事実(実測 — adapt 後の全出力)

`src/` がハードコードされたプローブが **5 箇所**(process-qualification.py
L293 POS / L301 N1 / L341 N6 / L407 N11 / L487 N18)。installed profile(src/ 非保護)では:

- **N1 FAIL(素通り・fail-open 方向の表示)**: `src/a.txt` への ECO なし commit が保護外のため
  E01 が発火せず「想定外の通過」— 「E01 が効くこと」の負例検査が機能していない。
- **N11 FAIL(理由不一致)**: 既定 profile では E01/E08 の**二重遮断**で E01 が先に報告されて
  いた。adapt 後は E01 側が消え **E08(設備変更)単独遮断**になり期待と不一致。遮断自体は正しい。
- **N18 FAIL(理由不一致)**: 同様に E01 が消え、N17 で無力化した hooks の **E11 が先**に出る。
- **POS(無音の弱化 — 最も重い)**: 「起票→**保護変更**→accept」の保護変更脚が保護外パスを
  書いており、**E01 経路を実は検査せずに PASS**(silence §16(c) 存在 vs 完全性の類型)。
- **N6(弱化)**: `slipped=True` が「hook 無効だから素通り」でなく「保護外だから素通り」でも
  真になる — 判定の意味が消えている。

### 見逃しの構造

1. **治具は installed assets(対象リポの実 profile)を検査対象とする設計**(正しい —
   「qualification は installed assets を対象とする」)なのに、**プローブのパスだけが既定
   profile の値を暗黙前提**にしていた。既定と一致するリポ(scaffold・本リポの C11)でしか
   実行されたことがなく、**adapt という主要分岐を一度も踏んでいない**(silence §16(b):
   説明が約束する全分岐を通るテストがあるか — profile は「差分注入の場」と宣言しながら、
   差分が入った状態の検査が無い)。
2. 既定値の暗黙前提が「最初の実 adapt」で発現 — EXP-20260727-09(依存の既定値が影響分析に
   載るか)の同族。ECO-015 受入(V2 負例 7 種)・独立検査 3 ラウンドも既定 profile 上で
   実行されたため到達せず。
3. **fail-closed の勝ち(対照)**: 治具レベルでも「期待した遮断が起きない/理由が違う」を
   FAIL として表面化させ、ゲートが製造開始を止めた。誤りは設置者の眼前・是正コスト最小点で
   顕在化(OBS-20260726-03 の 3 例目候補 — 同族= ECO-017 V8(a) IQ-02 初版誤 FAIL)。

## 是正方針案(製造前・凍結前の草案)

1. **プローブパスを installed profile から導出する単一関数**を新設し、5 箇所(POS/N1/N6/N11/
   N18)が共有する(silence §16(e) — 同一契約「保護パスとは何か」の解釈を 1 実装に集約)。
   導出規則(裁定点 1): protected_paths の最初のディレクトリ型エントリ(末尾 `/`)配下に
   プローブファイルを合成。ディレクトリ型が無ければ最初のエントリ(ファイル型)をそのまま使用。
   **protected_paths が空/不在なら適格性 FAIL**(保護対象ゼロの line を ready と言わない —
   vacuous 化の遮断)。
2. N11 の期待は E01 のまま(導出関数適用で E01 が復活し二重遮断に戻る)。ただし「複数違反時の
   報告順序」への依存は脆さとして注記し、判定を「E01 **を含む**」で書く(順序非依存)。

## 裁定を要する設計点(gate ①)

1. **導出規則**: 上記案(最初のディレクトリ型エントリ優先・空なら FAIL)でよいか。
2. **MoviePad の profile adapt(DL-01)の内容承認**: protected_paths を実レイアウト
   (App.axaml / App.axaml.cs / Program.cs / MoviePad.csproj / Controls/ / Converters/ /
   Markup/ / Models/ / Services/ / Styles/ / Util/ / ViewModels/ / Views/ / Resources/ /
   Assets/)へ差し替え。states は既定 2 状態のまま。

## 受入基準(事前登録 — 製造前に凍結する)

- **回帰**: 既定 profile の scaffold で全対照 PASS(現行に同じ)。
- **陽性対照(今回の見逃しを直接塞ぐ)**: src/ を含まない adapt profile(MoviePad 実物)で
  全対照 PASS — 特に N1 が E01 遮断・POS の保護変更脚が実際に保護パスを書くこと。
- **負例**: protected_paths が空の profile で適格性が明示 FAIL(無音 PASS しない)。
- **決定性**: DET(2 回実行一致)維持。
- **クローズ条件**: kit 再配布後、MoviePad 実機で再適格性確認 PASS = line ready。
  本リポ self-conformance 全 PASS+**push 後 CI 緑の実測**(ECO-020 規律)。

## 影響分析(製造前予測 — 未凍結)

- 変更は `method/templates/process-core/tools/process-qualification.py` のみ
  (+MoviePad への kit 再配布で同ファイルの設置側同期)。validator・hooks・profile スキーマ・
  製品挙動(bomdd-init)は不変。C11(self-conformance)は既定 profile scaffold を使うため
  判定不変の予測。
- 依存の既定値の観点(EXP-20260714-04/EXP-20260727-09 の予防適用): 導出規則が新たに持つ
  暗黙前提は「protected_paths の並び順」— 先頭エントリ選択を仕様として order に明記し、
  並び替えで挙動が変わることを宣言する。

## スコープ外(明示)

- MoviePad の設置コミット(ECO-021 verified 後・line ready 実測後に実施)。
- MoviePad 側 bomdd/tools/process-qualification.py の直接パッチ(kit 再配布で同期する —
  設置物の手直しは正本と派生の乖離を作る)。
- profile スキーマへの「レイアウト自動検出」等の機能追加(必要が実測されてから)。

## 是正(2026-07-27)

1. `_probe_rel(root)` を新設(installed profile から導出・裁定 1 の規則・並び順依存を仕様として
   docstring に明記)。**OQ-00** を新設し導出結果を記録 — 導出不能(空/不在)は明示 FAIL で
   以降の OQ を実行しない。
2. 5 対照(POS/N1/N6/N11/N18)の `src/` ハードコードを `probe` 共有へ置換。ヘッダ対照表へ
   OQ-00 を追記。変更は process-qualification.py の 1 ファイルのみ(影響予測どおり)。

## 検証(2026-07-27・受入基準=起票時凍結分)

- **V1(回帰・既定 profile)**: fresh scaffold(bomdd-init 経由=実配布経路)で全対照 PASS・
  probe=`src/oq-probe.txt`・line ready。
- **V2(陽性対照・今回の見逃しを直接塞ぐ)**: MoviePad 実機(adapt 済み 15 エントリ)で
  全対照 PASS・probe=`Controls/oq-probe.txt`・**line ready**。N1 が E01 遮断・POS 保護変更脚が
  実保護パスを書くことを含む。
- **V2b(§16(b) 予防適用 — 凍結外・追加)**: ファイル型のみの protected_paths(`[Program.cs]`)で
  全対照 PASS・probe=`Program.cs` — 導出関数が約束する fallback 分岐を実測(約束した分岐を
  未実測のまま出荷しない — 本 ECO の欠陥型を是正自身に適用)。
- **V3(負例)**: `protected_paths: []` で **OQ-00 明示 FAIL・exit 1・「製造を開始しない」**
  (無音 PASS しない)。
- **V4(DET)**: 決定性 PASS(V1/V2/V2b 各実行に含む)。
- self-conformance 全 PASS(C4 scaffold 煙試験+C11 が新治具経由)。
- クローズ条件(kit 再配布 → MoviePad 再適格 PASS・CI 緑)は accept 節に記録する。

## 教訓(還元候補 — クローズ後に lesson-promote 経由)

- **設定を「差分注入の場」と宣言したら、検査は差分が入った状態を対照に含める** — 既定値と
  一致する構成だけで検査すると、adapt 分岐は最初の実運用で初めて踏まれる。
- fail-closed 適格性ゲートは治具自身の欠陥も表面化させる(誤 FAIL・理由不一致を FAIL に
  倒す設計が、治具の前提崩れを設置者の眼前へ出した)。
