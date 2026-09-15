# Change Order — ECO-079: immutable製造証拠と独立append-only受入証拠の分離

状態: implemented（文書契約の是正・ローカル検査済み、未コミット・CI未確認）。製品実装・配布・正式受入とは別工程。

## 2026-09-15 公開再開のpreflight receipt

ユーザー原文「pushして」を、直前に確認したBomDD/mainの候補commit・push・CI確認（先行ECO078受入commitを含む）の明示許可として受領した。以下の「push未許可」は過去の停止時点の記録であり、現在の権限待ちは解消。
分類=continuation。baseline b46359f92d4c20dca7917e2b1101974140437743、current-work-state=本件5ファイルだけの未コミット差分、既存indexは空、未解決事項=最終tree検査・commit/push・固定CI、handoff-state=公開許可待ちから再開、acceptance-target=最終treeのself-conformance exit0＋push確認＋対象commitのCI結論。以上を実読・Gitでconfirmed。
開始判定=PROCEED、有効overrideなし。方法論の実装契約3件は変えず、許可・再開記録を検査前に揃える。検査結果はcommit本文と製品側の公開receiptに記録し、検査後に方法論の作業ツリーを編集しない。push先はorigin/main、force push・製品リポのpush・kit導入・製品受入を含めない。CI確認前にverifiedへ昇格しない。

## 担当設備

起票・文書是正: requested=既存タスク設定、resolved=unknown（実到達モデルの証拠なし）。
ハーネス=Codex desktop、版unknown、来歴self-reported。独立検査なし。
方法論の文書修正のみであり、製品の工場再製造を実施したとは主張しない。

## 0. baselineと権限

方法論HEAD=7e060c920db1bc3b07e838ab905420db03200b5a。
依頼元TimetableAdv ECO-113。2026-09-15ユーザー原文:
採用してよい。ただし「Control Planを拡張する機能」ではなく、「immutableな製造証拠とは別のappend-only受入証拠レイヤー」として導入すること。
製品側原文の正本=artifacts/acceptance/eco-113/approval/layer-amendment.json。
旧option-1の「合成CP」はこの裁定で撤回された。上流是正と検証済み配布の許可であり、全面kit更新・push・検査免除は含めない。

## 1. 帰属と実測

spec_omission。eco-accept手順1のCP.characteristic直接追記は、固定製造CPに後発の受入事実を書き込む要求になっている。
TimetableAdvの既存probeでは6台帳そのままなら成功、メモリ内characteristic追加はshared-dependency:control-delta。
qualificationもCP全ファイルhashを固定しており、旧検査を削ることは是正ではない。
方法論の変更前eco-accept SHA256=2da19777f0fc1810cc6ef0a573a2713e8ed711f2777e901155f7a6f1deff29c3。
検査成功、性能改善、全製品へ実装済みであることは未主張。

## 2. 設計前DoDと影響なし予測

1. CPを拡張・合成しない。新層はimmutableな製造証拠の参照と後発受入証拠のみを所有する。
2. 受入事実/潜伏事実/再発防止/責任者/日時を記録し、CP固定版・candidate・attempt・verdictへ束縛する。
3. append-onlyを履歴単位で保証する。訂正は新イベント、基準変更は通常ECOへ戻す。
4. 製品へ適用するには検証済み読取経路が必要。文書を置いただけで受入済みとしない。
5. 不変製造証拠・既存passed・既存強制検査・製品固有の適用範囲を維持する。

allowed_paths=本order、60-change-register.yaml（ECO079追加だけ）、method/acceptance-evidence.md（新規）、
method/templates/product-profile/skills/eco-accept.md、method/templates/product-profile/change-management.md。
工具・検査器・hooks・CI・他templates・playbook・ECO078の3つの既存staged差分は不変。
製品kit/lock/CP/src/tests・CAD画面は本上流変更に含めない。初期製品適用はECO113で別検証する。

## 3. 受入計画（修正前固定）

- V1: 正本の条文をDoD1〜5と照合。旧直接追記規則が固定製造版にも適用されることをRED根拠とする。
- V2: 文書の経路対照。正常な既合格候補への受入事実追加は製造原本を変更しない。閾値上書き、旧記録削除、候補違い、未passed、読取経路欠落は受入不可。生成表示をCP正本として再投入しない。
- V3: 単一入口python method/tools/self-conformance.pyの終了コードを観測。非0/測定不能をPASSにしない。
- V4: stagedのECO078差分を保全し、上記allowed_paths以外に本作業の差分なしを確認。
- V5: 固定版のCIを観測するまでverified/適格配布版としない。文書の経路対照は製品validatorの動作検査を代用しない。

## preflight receipt

起動経路: 自発（上流規範の変更開始）。分類=既裁定の適用実装。
confirmed: 対象条文と固定CPの衝突、次番079未使用、上流変更の明示許可、対象手順全文。
confirmed: ECO078のorder/register/improvementsに別担当のstaged変更あり。
開始判定=PROCEED_WITH_LIMITS。既存indexの3blobを保全し、registerは作業ツリー末尾へ079だけ追加する。
既存staged変更のcommit・unstage・取り消しはしない。配布/commitの混入を防げない段階は停止する。
index baseline: order078=a3b622c96d57fd72d6fe339aa4b5ce965b663a30、register=9c03106ddd2a778e6952d990f49434cded2204ae、improvements=38349410b8fb2e2ee5f35c4ad2f3ca1c0b4e9782。

## converge receipt

起動経路: 自発（裁定追補による方式変更）。設計前DoDは§2。
round1: 新規1。旧案の合成CPを否定するだけでは参照検査の責任が曖昧なため、読取器の出力は受入証拠整合性のみと明記する。
round2: 新規0。訂正イベント、candidate変更、未passed、実行条件変更、未導入製品の境界を点検。
round3: 新規0。自己署名hashとGit固定参照、製造検査のAND維持、歴史非遡及、配布出自を点検。
判定: 収束（文書設計のみ）。DoD1〜5 ✔。未収束事項なし。実装強制力・転移効果は別検証であり未測定。

## 実施記録

上記計画の凍結後に文書3件を修正した。固定製造CPへ追記せず、別の受入証拠を検証する契約を新設。CP合成出力は明示禁止。旧経路は未移行かつ製造証拠の固定を破らない場合に限って残す。

V1: 修正前の条文/hashを実読し、製品closure-control-plan-probe.pyを再実行（exit0、診断成立）。無変更6台帳は成功、メモリ内追記はcontrol-delta、現物CP hash不変。これは新層の機械検査成功ではない。
V2: 文書の経路対照を実施。既合格候補の事実追加→原本不変（§1/2）、閾値変更→通常ECO（§1）、旧記録削除→不可（§2/3）、候補違い/未passed→不可（§3）、読取器欠落→正式受入停止（§4）、合成CP再投入→禁止（§1/3）。機械的な弁別試験ではなく、実装の有効性は未測定。
skill-creatorのquick_validate.pyはSKILL.md名の一時写しに対してexit0。frontmatter等の形式確認であり、手順の意味・製品動作の証明ではない。

### V3: 第1回 — FAIL（環境帰属）

CodexSandboxOfflineで単一入口self-conformance.pyを実行。C14のREALだけ失敗（6/7）、全体exit1。C1〜C13/C15〜C18はPASS。約10分、工程設備の既定/非既定構成の各35対照・2回決定性を含む。固定版の全合格とはしない。
追加の非破壊診断でkit-freshness._clean_git_envがGIT_CONFIG_COUNTを除去し、origin照会がGit exit128のdubious ownershipになることを実測。所有者akiraと実行主体CodexSandboxOfflineが異なる。判定基準の欠陥と断定せず、正常な所有者環境での再実行へ戻す。グローバルsafe.directoryや検査条件は変更しない。

### 並行変更と再開条件

検査中、別担当がECO078のorderのindexを更新し、b46359f92d4c20dca7917e2b1101974140437743へcommitしたことを観測。ECO079は混入せず、indexは空、本件の差分だけが残った。当方は相手のindex・commitを操作していない。検査開始時点の全体版固定は成立していないため、第1回を固定配布の証拠にしない。
以降の比較基準はb46359f92d4c20dca7917e2b1101974140437743（ECO079の文書3件は初回実行後未変更）。正しい実行主体で全検査を再実行し、結果観測まではcommit/push/製品配布しない。

## calibrate receipt

第2回追補: リポジトリ所有者の実行環境で同じ単一入口を再実行し、exit0・全検査PASSを観測。C14 REALを含む7/7、C11/C11bの各35対照・2回決定性もPASS。方法論の文書3ソースは第1回と同一hash、検査器/グローバルGit設定は未変更。HEADは実行前後ともb46359f92d4c20dca7917e2b1101974140437743。証拠=製品artifacts/acceptance/eco-113/upstream/run-02.json（失敗したrun-01も保存）。
このローカル結果は記録した文書ソースの自己適合に条件付き適格。新受入層の機械的強制・製品検査・固定CIは依然unknown。以下の第1回査定は履歴として保持する。

ここから先は候補commit/pushとCI確認が必要。pushは未許可のため実行しない。現origin/main参照は7e060c9、ローカルmainはb46359fなので、mainの公開には先行ECO078の受入commitも含まれる。これは当方が作ったcommitではない。今回の測定後に本order/registerへ結果を記録したため、push前には最終treeに一致する必須検査/witnessが必要。旧witnessで通過させない。製品kit/lock・検査器は未変更。

査定した主張と判定: 文書に所有境界と停止経路を定義したこと=observed・条件付き適格（V1/V2の実読）。形式検査成功=observed・形式に限り適格。全体検査第1回FAIL=observed・環境失敗の記録として適格。新層の機械的強制と固定CI=unknown、未実装/未実行で資格なし。
計器欠陥: 未確定。Git環境隔離でtrust設定が失われることを診断した。安全機構を緩めず実行主体を正す。
検出力の限界: 文書の正しさ/新層の製品上の強制/転移効果は既存self-conformanceから導かない。製造者の自己査定で独立検査なし。
行別記録: Q1 asked（主張は文書/形式へ限定）、Q2 asked（旧CPプローブの独立した原本/改変腕。新層のgood/bad実装試験は未測定）、Q3 asked（実装被覆は未測定）、Q4 NA（本上流差分にfixture宣言なし）、Q5 asked（FAIL/unknownを保存）、Q6 asked（終了観測後に再開判断）、Q7 NA（新計器なし）、Q8 asked（停止出口は通常ECO/検査器配備）、Q9 asked（主体とbaseline変化を記録）、Q10 asked（限界を上記宣言）、Q11 asked（正常追加/条件変更/訂正/参照違い/未配備を区別。機械実行は未測定）。
