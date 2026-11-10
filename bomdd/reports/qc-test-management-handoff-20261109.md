# 承認済み試験値の訂正実験から BomDD に持ち帰る観察

`qc-test-management` は、REQ-QC-001 の承認済み試験値を訂正する機能を、品質管理部1部門の水分試験で具体化した製品リポジトリです。この記録の対象は、裁定と製造入力の固定から `ROUTE-QC-BUILD-READ` までです。

最優先の持ち帰りは、**状態遷移を検査するとき、誰が、どの操作の直後に、何を観測するかを固定すること**です。特に、依存する処理が止まることと、独立した処理が進むことを対にすると、一律に止める実装を不合格にする検査行を書けます。そうした実装を実際に走らせて落とすことは、まだ確かめていません(検出力は未測定)。BomDD の Control Plan と Routing の記入例として再利用できます。

## 持ち帰る観察

### 1a 確定前後と競合時を別接続から観測する

訂正コアの自己検査は、製品コードの `CorrectionService` と PostgreSQL を使います。判定・証拠照合には検査用の実装を渡しています。許可と保留開始、正式版の切替と保留解除を、別の PostgreSQL 接続からコミット前後に観測しました。意図的にコミットを失敗させたケースでは、操作履歴や承認記録を含めて更新が戻りました。取下げと再承認を競合させたケースでは、どちらを先に確定しても、後発の操作は行ロックを待った後、古い状態として拒否されました。PostgreSQL の遅延トリガーで確定の順序を制御しました。 [コアの検査コード](../../../qc-test-management/tests/acceptance/CoreSelfTest.cs) · [コミットを制御する治具](../../../qc-test-management/tests/acceptance/CoreTestEnvironment.cs)

### 1b 依存する処理の保留と独立した処理の継続を対にする

正式参照の自己検査は、製品コードの `OfficialReadService` と PostgreSQL を使います。水分試料1に依存する集約判定・帳票・受け渡し・次工程について、必要な正式入力を照合する判定が `OnHold` を返しました。試料2と外観の正式参照は続き、それらだけを使う処理では `ConfirmAsync` を通じて検査用テーブルに確定を記録できました。保留開始と確定が競合した場合は、確定側が保留を認識し、解除後も古い版や不足した入力の組を拒否しました。承認済・完了の依頼では、取下げ・回復版の再承認や未登録時の取りやめを経ても、依頼の進捗と完了日時が維持されました。 [正式参照の検査コード](../../../qc-test-management/tests/acceptance/ReadSelfTest.cs)

Control Plan に転用するなら、各行に初期状態、観測する接続または利用者、確定前後の期待、失敗時に残る状態を置きます。影響範囲が重要な機能では、同じ依頼内で続けられる処理も対照に含めます。CP-QC-11 には一律に保留する実装を不合格とする期待があります。今回の自己検査では現行実装を観測し、一律に保留する欠陥を入れた実装での検出力は測定していません。 [CP-QC-11 の反例](../../../qc-test-management/bomdd/33-control-plan.yaml#L602) [Routing と自己検査への参照](../../../qc-test-management/bomdd/34-routing.yaml)

### 2 禁止条件と成立すべき状態を同じ検査に書く

CP-QC-03 のレビューでは、「旧値を返さない」という条件だけだと、空欄や一般エラーでも合格し得ると分かりました。合格条件に、正式参照で明示的に保留を返すこと、再承認者に訂正版が承認待ちとして見えること、履歴閲覧権限のある人に旧版が見えることを入れました。保留の対象と理由も確認します。機械検査が測る状態と、利用者が表示から何を判断できるかは、それぞれ Control Plan と Phase 5 に置きました。 [CP-QC-03](../../../qc-test-management/bomdd/33-control-plan.yaml#L110) · [Phase 5 の観測事項](../../../qc-test-management/bomdd/evidence/qc-001/baseline.yaml#L90)

治具の自己検査は、合成した正例1件を通し、旧値・訂正値の漏出、空欄、一般エラー、版や保留理由の欠落などの不適合例9件を落としました。これは検査器が用意した応答を区別できるという観測です。試作では旧値が正式表示に残る不一致があり、修正後も登録直後の中間画面は直接観測していません。製品でこの行を測るときは、その中間状態の実際の画面を取得します。 [治具の検査コード](../../../qc-test-management/tests/acceptance/SelfTest.cs) · [試作の観測結果](../../../qc-test-management/bomdd/sources/req-qc-001/run-01/trial-record.md#trial-results)

### 3 業務裁定と検査入力を結び付けて版を固定する

業務上の裁定、実運用で登録する任命・規格・装置等、検査用の架空データを分けて記録しました。Control Plan の21行から Routing の実行入口と `QC-MOISTURE-FX-v1` のケースを引けます。治具はマニフェストと入力20ファイルのハッシュを照合し、79ケースを PostgreSQL に投入して読み戻しました。この79件は入力を読み戻した件数です。 [製造入力の裁定](../../../qc-test-management/bomdd/decisions/DEC-QC-003.md) · [初期データのマニフェスト](../../../qc-test-management/bomdd/fixtures/qc-moisture-v1/manifest.yaml)

判定の自己検査では、規格上限と丸め規則を別々に改訂した場合を比較しました。改訂前の規則では `12.24%` が `12.2%・適合` になり、当時の版を確認できないケースでは再承認が保留されました。固定資料のハッシュと結果版からの参照を併用することで、どの版に基づく判定かを追える事例です。 [判定・証拠照合の検査コード](../../../qc-test-management/tests/acceptance/RulesSelfTest.cs)

## BomDD での扱い

- 観察1aと2は、BomDD担当者のレビューで watch の候補になった。観察1aは実DBでの部品自己検査、観察2は検査行のレビューと合成応答での弁別を根拠にする。本文への昇格を判断するための製品経路での観測は未実施。 [トランザクション境界と同時更新の競合](../../method/silence-checklist.md#L156)
- 観察1bと3は既存規定の記入例。1b は依存する対象と独立した対象を分け、3 は固定した入力と規則の効力を追える形にした。転用時の検出力を測る場合は、保留を無視する実装、一律に保留する実装、古い入力で確定する実装を、検査ケースを見ていない別の担当者が用意する。 [Control Plan の規定](../../method/bomdd-playbook-v1.md#L147) · [較正](../../method/bomdd-playbook-v1.md#L370) · [自己受入](../../method/bomdd-playbook-v1.md#L667) · [規則改訂の効力](../../method/bomdd-playbook-v1.md#L748)
- 事前裁定は、製造入力に落とした事例として扱う。今回の製品開発では裁定時期を変えた比較や工数計測をしていないため、`OBS-20261108-01` の手戻り・工数に関する追加の効果測定には数えない。BehaviorForge や自由実装に対する優位性も比較していない。 [既存観察と追試条件](../../method/improvements.md#L10571) · [BehaviorForge の先行パイロット](../../method/improvements.md#L10512)

## 対象版と再実行

製品リポジトリは `C:\Users\akira\source\repos\qc-test-management`。以下のソース版を使う。

| 対象 | 識別子 |
|---|---|
| 製品ソースのコミット | `1b4216a7bdc3d0562862d391d2531adc1a482eaf` |
| Git ツリー | `4973936ac4d03608f4bab64ae03bb4dc435de8ac` |
| `QC-MOISTURE-FX-v1` のマニフェスト SHA-256 | `676c7ec0f5f41545689b1a99a7c72211cb8b1cefa4c9b5621d32ae5a0dff5d75` |

Windows の PowerShell、.NET SDK 10.0.403、稼働中の Podman マシンを使う。起動手順はダイジェストで固定した PostgreSQL 18.6 の検査用コンテナを使い、ホスト側の `127.0.0.1:55438` に公開する。上記のコミットをチェックアウトしたクリーンな作業ツリーのルートで実行する。現在の作業ツリーが別の版を指す場合は、追試用のチェックアウトを別に用意する。 [治具の実行手順](../../../qc-test-management/tests/acceptance/README.md) · [PostgreSQL の固定と起動](../../../qc-test-management/tests/acceptance/postgres.ps1)

```powershell
$revision = '1b4216a7bdc3d0562862d391d2531adc1a482eaf'
$observed = git rev-parse HEAD
if ($LASTEXITCODE -ne 0 -or $observed -ne $revision) { throw 'Unexpected checkout' }
$dirty = git status --porcelain=v1
if ($LASTEXITCODE -ne 0 -or $dirty) { throw 'Use a clean checkout' }

pwsh -NoProfile -File tests/acceptance/postgres.ps1 -Action Start
if ($LASTEXITCODE -ne 0) { throw 'PostgreSQL startup failed' }
dotnet restore tests/acceptance/Qc.Acceptance.csproj --locked-mode --source https://api.nuget.org/v3/index.json
if ($LASTEXITCODE -ne 0) { throw 'Restore failed' }
dotnet build tests/acceptance/Qc.Acceptance.csproj --no-restore
if ($LASTEXITCODE -ne 0) { throw 'Build failed' }

$run = 'bomdd-replay-' + [DateTime]::UtcNow.ToString('yyyyMMddHHmmssfff')
foreach ($step in @('self-test', 'core-self-test', 'rules-self-test', 'read-self-test')) {
    dotnet run --no-build --project tests/acceptance/Qc.Acceptance.csproj -- $step --run-id "$run-$step"
    if ($LASTEXITCODE -ne 0) { throw "Self-test failed for $step" }
}
```

## 既存の実行記録

実行記録は製品リポジトリの `.qc-acceptance/` にローカル保存される。以下は既存記録を識別するハッシュ。追試で生じる記録は別の実行IDと時刻を持つため、比較するのはケース別の判定と入力のマニフェストである。

| 記録 | 観測 | 記録ファイルの SHA-256 |
|---|---|---|
| [治具マニフェスト](../../../qc-test-management/.qc-acceptance/harness/build-read-harness-01/manifest.json) | PostgreSQL で入力79ケースを読み戻し | `69663327b7d61e57307e3dcd6798ef1c62da71a72e7577aa3694f7089a6f8c91` |
| [CP-QC-03 の模擬観測](../../../qc-test-management/.qc-acceptance/harness/build-read-harness-01/CP-QC-03.json) | 正例1件が合格、不適合例9件が不合格 | `abfc0806010201eef23295dc4fa5a7b9f38d33af8647b6d02d92e17315488fc9` |
| [訂正コア](../../../qc-test-management/.qc-acceptance/core/build-read-core-01/report.json) | PostgreSQL の自己検査8件が合格。判定・証拠照合は検査用実装 | `0134d81d792b9b4a7d041da74a8693acec7f36b169f312352de2c31f20ec425e` |
| [判定と証拠照合](../../../qc-test-management/.qc-acceptance/rules/build-read-rules-01/report.json) | PostgreSQL の自己検査7件が合格。規則と証拠は固定した架空資料 | `29d970a1fda2e3978242fd3ff10f331fd28e885995708b10b4888971360e1ff3` |
| [正式参照と依存判定](../../../qc-test-management/.qc-acceptance/read/build-read-01/report.json) | PostgreSQL の自己検査6件が合格。後続処理の確定は検査用テーブルで観測 | `11924e416070348da1e3a59bd26bf0ee1796d62c9707a43b131e31a17c2ac8be` |

製品検査21件と Phase 5 はすべて `NOT_RUN`。画面・帳票・実機・製造連携での振る舞いと、利用者が保留を理解して待てるかは未測定。自己検査の実行記録は上記のソースコミットとは別に、実行したアセンブリのハッシュで個体を識別している。 [製品検査の証拠台帳](../../../qc-test-management/bomdd/evidence/qc-001/baseline.yaml)

## 作業確認と証拠の資格

- `/preflight` は `continuation`。前回の観察を担当者が追試できる形で渡す。基準版は上記の Git コミットとツリー、現在の工程と残項目は Routing と証拠台帳、引き渡す内容と完了条件は観察・限界・根拠・再実行手順を1ファイルから参照できること。いずれも `confirmed`。リポジトリ固有の確認先は BomDD の AGENTS.md と自己適用台帳。追加で、ローカルの証拠が残っていることを確認した。開始判定は `PROCEED`、override はなし。
- `/calibrate` は模擬応答の弁別、固定入力のDB読み戻し、隔離DBでの各部品の動作について `observed × 条件付き適格`。記録のアセンブリハッシュとローカルの実体、入力ハッシュと Routing の固定値を照合した。模擬応答は凍結した期待に対する合成対照で、実際の製品経路を通していない。一律に保留する欠陥を仕込んだ実装での検出力は `unknown`（理由は欠陥を入れた個体の未実行）。製品検査と Phase 5 も `unknown`（理由 `NOT_RUN`）。計器欠陥の新規検出はなし。Q1〜Q5・Q9〜Q11 は `asked`、Q6〜Q8 は `NA`（工程の前進判定や常設ゲートは査定外）。
