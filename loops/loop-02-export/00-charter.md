# Loop 2 憲章 — 書き出し(外部プロセスIO)スライス

## 目的
純粋ロジックでない領域(ffmpeg 連携)で、C2(暗黙知)と C3(工程欠落)/C4(受入)がどう増えるかを測る。
Loop 1.5 で妥当性確認したループ手法 + 改善(E-BOMグラフ・モダリティ列・完全性・無矛盾)を継続適用。技術は原版固定。

## スコープ(2ユニット)
- **Unit A `ExportPlan.Analyze`** — ストリームコピー可否の純粋判定(規則ベース)。Split 同様 industrializable と予想。
- **Unit B `BuildFilterGraph` / `BuildFilterArgs` / `BuildCopyArgs`** — ffmpeg コマンド文字列構築。外部ツール文法。

実プロセス起動(`ExportAsync`/`ProcessRunner`)は Loop2 では対象外(IO実行・進捗解析は別ループ)。

## 仮説
- **H4**: Unit A は規則から再生産可能。ただし「コーデック白名簿(H.264/H.265, AAC/MP3/AC-3)」「VFRはコピー可だが再エンコードでは要CFR」等は**要求から導けない外部/業務知識**。BOM に明記が要る数を数える。
- **H5**: Unit B は綺麗に industrialize できない。受入オラクルが要求する正確文字列(`[cv]null[vout]` 等)は実装の任意様式。behavioral M-BOM では装置は別文字列を生成 → 正確文字列オラクルは部分失敗。
  分岐: ffmpeg を M-BOM へ転記(BOM=コード崩壊) or 実行+メディア差分受入(C4)。
- **H6**: 標準 ffmpeg 慣用は C2 でタダで出る / 実装固有最適化(seekBase 2入力・`[cv]null`透過・lanczos)は出ない。

## 実験変数(意図的設計)
- Unit A の M-BOM: **規則を完全列挙**(industrializable 側の対照)。
- Unit B の M-BOM: **挙動のみ記述、内部ラベル名/透過様式/最適化は manufacturer に委ねる**(外部文法ギャップを露出させる)。
  ただし `[vout]`/`[aout]` 出力パッド名のみ固定(`BuildFilterArgs` の `-map` 接続面=ハード契約)。

## 測定
Unit A: オラクル合格率 + 「導けない規則」件数。Unit B: オラクル合格率の内訳(通る=タダのC2慣用 / 落ちる=実装固有)。
→ [../loop-02-report.md](../loop-02-report.md)。
