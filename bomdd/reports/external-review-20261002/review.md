# 外部レビュー(2026-10-02・原文の写し — pandoc で .docx から変換・内容は無改変)

> 出典: BomDD_repository_review_20261002.docx(user 持ち込み 2026-10-03)。照合と裁定は [verification.md](verification.md)。

レビュー日　2026年10月2日 UTC

対象　akiramei/BomDD main　[069e0d5ab55d893cb8c84bfe8edf39631441ee89](https://github.com/akiramei/BomDD/tree/069e0d5ab55d893cb8c84bfe8edf39631441ee89)

# 結論

最優先は、上流のE-BOMとS-BOMを人が裁定し、その確定版から統括AIがM-BOMとControl Planを導出する境界を明確にすることである。現在の方法にはGUI設計の裁定、隔離製造、固定オラクル、保守の逆引きなどの基盤がある。一方、S-BOMの工程上の位置とE-BOMの分割基準には、今回の目標モデルとの距離が残る。

実装面では、テスト実行全体の異常を見落とすC9と、特殊なGitインデックス状態で測定対象と異なる木を証明するwitnessを、限定した合成入力で再現した。これらの修正と製造パッケージの記載統一は、コンテキスト最適化の一般化より先に進める価値がある。

# 今回の判断基準

CAD-BOMはGUIモックとUI-IRに加え、非GUIのユースケースや観測可能な契約を設計入力にする。E-BOMは利用者にとって意味のある機能部品、S-BOMは上流の保守性要求を担う。人がE/Sの意味と方針を裁定し、統括AIがM-BOM・Control Planと製造委譲を担当し、工場AIが実装する。この目標を、現行リポジトリがすでに約束済みの契約とは区別して評価した。

# 指摘の読み方

• 論点1〜3は目標モデルに照らした不足である。現行の統制が全く存在しないという指摘ではない。

• 論点4は文書とプロンプト間の具体的な矛盾、論点5と7は既知の未完了課題、論点6は試行の評価設計に対する追加指摘である。

• 論点8と9は限定条件で再現した実装上の証拠不整合である。実運用での発生や全体ゲートの通過は確認していない。

優先度は、P1を設計方針または受入の信頼性に直結する課題、P2を次の限定的な修正・実験で扱う課題、P3を文書整理とする。コンテキストの範囲と寿命の最適化は、効果がまだ確定していない研究仮説として扱う。

# 上流の設計と裁定の境界

論点 1　P1　目標モデルとの不整合

## 保守性要求を上流の S BOM として確定する

現行のService BOMはPhase 6でAs-Builtとともに作られ、故障・更新時の影響範囲、再検査、交換判断を支える。PLMの追跡経路もAs-Builtの後にService BOMを置く。このため、交換可能性、復旧・移行、サービス継続、許容する保守境界を、E/Mの構造決定前に承認する入力が不足している。

既存のS-BOMはOSS依存一覧より広いことが明示されており、調達方針、substitutable、実測交換コストの扱いもある。これらを捨てず、上流のサービス設計基準と、下流のAs-Built・As-Maintained記録を別のライフサイクル表現として結ぶべきである。As-Maintainedやeffectivityの既知課題だけでは、この上流の不足は埋まらない。

**次の一手は、**1件の機能について保守上の約束を人が裁定し、E/Sのリビジョンを一つの設計リリースとして固定すること。その要求からM/Control Planへ導出した交換・復旧の検査を追跡できればよい。DIやadapterは必要な交換性を満たす手段として選び、全製品に一律強制しない。

根拠　[工程上の位置 L24-L33](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/method/bomdd-playbook-v1.md#L24-L33) ／ [Service BOMテンプレート L14-L26](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/method/templates/53-service-bom.yaml#L14-L26) ／ [交換コストの扱い L51-L69](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/method/s-bom-template.md#L51-L69)

論点 2　P1　現行記述の緊張と裁定境界の不足

## E BOM の機能部品と M BOM の製造単位を分ける

粒度ガイドは、E-BOMを仕様責任者に理解できる機能・責務として説明し、クラス・ファイル・DOMの一覧を否定している。一方、playbookは独立再製造可能性による粒度をcandidateとして示し、phase3の実行プロンプトはその留保なくE-BOMの切り分けに使う。機能の分解を確定する前に、工場・モジュールの境界を選ばせるおそれがある。

Eの第一基準を利用者に意味のある機能と観測可能な受入条件、Mの基準を製造・検査可能性とする。EからMへの実現は多対多を許し、ソースファイル参照は実現との対応付けとして残す。人による一般的な裁定とGUI裁定は既存の強みだが、E/Sの承認済み版から統括AIがM/CPを導出する責任境界は、まだ独立したリリース契約になっていない。

**確認は、**Mの再編だけを行ったときにEの機能IDと人の承認済みの約束を維持できるかで行う。新たな機能・保守上の約束や導出できない判断が必要になった場合だけ、人へ裁定を戻す。機械的な派生作業まで毎回承認対象にしない。

根拠　[機能粒度 L7-L30](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/method/contracts/bom-granularity-guide.md#L7-L30) ／ [候補の製造粒度 L110-L114](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/method/bomdd-playbook-v1.md#L110-L114) ／ [phase3指示 L3-L6](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/method/prompts/phase3-design.md#L3-L6) ／ [裁定済みの意味 L12-L25](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/method/templates/37-ui-rulings.yaml#L12-L25)

# CAD の入力契約と製造への引渡し

論点 3　P2　既知の拡張課題

## 媒体をまたぐ CAD 入力の最小契約を定める

GUIでは、実行可能なHTML・JavaScript・CSSモック、意味を持つUI-IR/UI-BOM、人の裁定、E-BOMへの昇格が具体化されている。TMP-UI系の仮番号も存在する。非GUIについても、読み取り専用・非対話CLIでの転移が実証されており、非GUIの取組がないという評価は誤りになる。

不足は、この成果を異なる媒体の設計入力へ適用する共通の入口である。CLI実験自体が、対話型CUI/TUI、副作用を持つCLI、API・event・data CADへの一般化を留保している。既存のWeb/APIやSagaのBOM実験も、API-CADからの入力工程をそのまま保証するものではない。

**次の一手は、**出典リビジョン、媒体、ユースケースと観測可能な契約、状態・異常経路、裁定、Eへの昇格参照だけを持つ小さな共通枠を置くこと。GUIと実証済みCLIをprofileとして維持し、API・batchなどは未検証profileと明記する。実例1件で、GUIの表面構造を強制せずに仕様の意味と昇格根拠を引き渡せるかを確認する。

根拠　[GUI設計の契約 L8-L45](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/method/ui-ir-ui-bom.md#L8-L45) ／ [CLI実証の範囲 L15-L16](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/loops/cli-cad-01/report.md#L15-L16) ／ [EのGUI入力欄 L13-L18](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/method/templates/30-ebom.yaml#L13-L18)

論点 4　P2　新たに確認した文書間の矛盾

## 条件付きの製造パッケージ一覧を一本化する

playbookのG3、phase3、phase4は20・30〜34・40を排他的な入力パッケージとして列挙する。一方、40-work-orderはUI-CADの場合に35-design-system-bomを必須としている。必要な35を除いた一覧に従う経路と、35を渡す経路が並存している。

canonicalなfactory-delegateは実際のwork orderを渡すため、この矛盾を緩和する。ただしECO向けの委譲手順だけでは、通常のG3や初回製造の列挙までは統一されない。今回確認したのは記述上の矛盾であり、実製品で35の欠落が発生したことではない。

**修正は、**GUIなどの条件を含むパッケージ定義を一か所に置き、G3と製造の双方が同じ定義を参照する形が小さい。UI-CADあり・なしの2ケースで生成した入力集合を比較し、35の包含条件が一致することを確認する。新しい一覧の手作業コピーを増やさない。

根拠　[G3の列挙 L336-L343](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/method/bomdd-playbook-v1.md#L336-L343) ／ [phase3の列挙 L22-L26](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/method/prompts/phase3-design.md#L22-L26) ／ [phase4の列挙 L5-L17](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/method/prompts/phase4-manufacture.md#L5-L17) ／ [35の条件付き必須化 L17-L23](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/method/templates/40-work-order.md#L17-L23)

## 設計の原典と実装の観測を混同しない

コードが現在どう動くかは事実の観測であり、何を正しいとするかの根拠は承認済みの上流契約である。差が見つかったら実装修正か上流変更の裁定へ進む。現在の挙動を採用する場合も、人が上流の変更を承認してから固定オラクルの新しい版へ反映する。

根拠　[仕様由来と凍結の原則 L6-L15](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/method/templates/41-fixed-oracle.yaml#L6-L15) ／ [凍結物と変更時の裁定 L57-L64](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/method/templates/product-profile/skills/factory-delegate.md#L57-L64)

# Control Plan を受入判断につなぐ

論点 5　P1　既知の設計課題と進行中の試行

## 規範から実行証拠までのつながりを確かめる

固定オラクルを仕様から作り、製造前に凍結し、変更はECOで扱う方針は明確である。ただし参照が存在することと、その期待値が承認済み契約から導かれ、実行されたassertionに対応し、今回の受入で使われたことは別である。R-030/031は参照・凍結の宣言を要求し、R-050は証拠内容や現物hash、受入経路への参加確認を対象外と明示している。これを新発見のvalidator違反とは呼べない。

ECO-086、ECO-090はこの接続不足をすでに認識している。ViewPrism2のECO-143ではCP行別の結果を承認依頼へ出す試行が始まり、最初の出力で検査なし4行と未登録CP ID 2件が表面化した。新しい表を重ねて提案するより、既存のcollectorと受入経路が判断を変えたかを評価すべきである。

**次の一手は、**1製品で承認済み契約版・INV → E → M → CP → 安定したtest/assertion ID → 実行証拠・検査対象digestを追跡すること。構造上の到達性と期待値の意味の妥当性は別に審査する。Routingの既存CP参照から検査時点を導き、失敗行と測定失敗がそれぞれ製品修正・測定系復旧へ振り分けられることを確認する。既に撤回されたCPのwhen欄は再提案しない。

根拠　[既存試行 L36-L57](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/bomdd/60-change-order-eco-090.md#L36-L57) ／ [参照検査の範囲 L490-L499](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/method/schemas/draft/ref-edges.draft.yaml#L490-L499) ／ [証拠検査の明示的限界 L542-L547](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/method/schemas/draft/ref-edges.draft.yaml#L542-L547) ／ [when欄案の撤回 L8224-L8227](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/method/improvements.md#L8224-L8227)

論点 6　P2　試行への追加的な評価設計指摘

## 行動が起きなかった理由を区別する

現在の試行は、次の3回の承認でCP結果が人の行動を生んだ回数を主指標にする。この0/3を、そのまま表が承認判断に使われなかった証拠とすることはできない。是正すべき例外がなければ行動ゼロは正常であり、例外を読んだうえで明示的に受容する判断もあり得る。逆に、表への言及だけでは判断への寄与を証明しない。

事前登録した主指標は維持する。同じ3件に補助注記として、対処可能な例外の有無、提示されたCP行と結果、実際の行動または行動しない裁定、その証拠を加える。結果を見てから主指標の意味や成功条件を置き換えない。

**確認は、**欠測・未知のCP IDを含む依頼をリハーサルし、例外が人に届くかを見ること。必要なら古い結果の取り違えも追加する。3件から言えるのは情報が意思決定に使われたかまでであり、不具合流出が減ったという効果までは主張しない。人の判断を補助する試行を、自動拒否ゲートへ無断で変えない。

根拠　[3回の承認と主指標 L8245-L8247](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/method/improvements.md#L8245-L8247) ／ [現在の受入経路の分類 L15-L52](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/bomdd/reports/eco-090-redesign-baseline/acceptance-paths.md#L15-L52)

# コンテキストを資源として評価する

論点 7　P2　既知の未完了仮説

## 範囲と寿命を観測してから分割を比較する

RoutingはBOM一式を読むところから始まり、Work Orderも共通の全体パッケージを要求する。M5はE/K/依存への直接参照数とinterface key数を数える代理指標であり、実際の入力量、追加検索、重複読込、保持される期間を測っていない。M単位を独立製造可能に切ることだけでは、最小のコンテキストや最適な工程順は決まらない。

一方、G3のfresh AIによる不足質問、役割別の手順範囲、読んだファイルの報告、As-Builtの出典固定、作業時間の計測は既にある。これらを再利用し、細かなschemaや一律token上限を先に増やさない。工場隔離は実験の妥当性とオラクル秘匿を守るためのものであり、作業コンテキストの縮小による効率改善とは目的を分ける。

根拠　[全体読込のRouting L10-L36](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/method/templates/34-routing.yaml#L10-L36) ／ [M5の定義 L31-L34](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/bomdd/reports/eco-090-redesign-baseline/preregistration.md#L31-L34) ／ [既知の前提条件 L8242-L8244](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/method/improvements.md#L8242-L8244)

## 最初の観測で残すもの

関連する複数の製造単位を持つ1ジョブで、統括AIの次の分割・工程判断に必要な証拠だけを残す。読む権限のあるコーパスと、モデルが実際に保持している注意・記憶を同一視しない。

• 配布した契約の節と版、実際に読んだ節、追加で必要だった参照、工場間での再読込

• その情報が必要になる最初と最後の工程、引渡し時点、G3質問と不足報告

• 既存の品質結果と総作業時間。tokenは実ログがある場合に用い、bytesや節数なら代理指標と明記する

## 縮小案の比較と破損試験

記録済みのECO-090の前提条件を満たしてから、同一の凍結課題・モデル・受入集合で、現行の全体パッケージと一つの範囲限定案を比較する。配布物の準備、統括、引渡し、再読込も総コストに含める。密結合の2単位を同じ工場セッションで扱う余地を残し、MのIDとコンテキストの寿命を一対一に固定しない。

実在するproducer–consumer接続と横断不変条件を一つずつ選び、既存のCP・INV参照から組立検査を割り当てる。必要な不変条件の欠落と、配布後の上流改訂を意図的に作り、不足・旧版として検出して統括AIへ戻るかを確認する。必要な原典が変わったときはパッケージを再発行し、下流の新しいコンテキストへ切り替える。既読tokenを選択的に消せるとは仮定しない。

**採否は、**必要な契約の欠落、検査不良、説明不能な判断を増やさず、総工数または維持する文脈を減らせたかで決める。分割で引渡し・再読込が増えるなら再統合する。初回比較は実行可能性の確認であり、狭い文脈が常に優位という一般則にはしない。

根拠　[不足時の停止と報告 L45-L67](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/method/templates/40-work-order.md#L45-L67) ／ [実行中の失効は対象外 L21-L30](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/method/templates/product-profile/skills/preflight.md#L21-L30) ／ [M6の観測範囲 L36-L44](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/bomdd/reports/eco-090-redesign-baseline/preregistration.md#L36-L44)

# 限定条件で再現した実装上の欠陥

論点 8　P2　合成入力で再現

## C9 が実行全体の異常を合格にする

C9はout.trxがあれば個々のUnitTestResultを判定し、以後はプロセス終了コードもResultSummaryやrun-level Errorも見ない。期待件数の行が揃うと、中断や実行基盤の異常が明示されていてもPASSになる。未変更のvalidatorに合成subprocess/TRX入力を与え、次を確認した。

| **入力条件**                              | **C9の結果**   |
|-------------------------------------------|----------------|
| Passed行・Completed・終了0                | PASS　正常対照 |
| 予期しないFailed行・終了1                 | FAIL　異常対照 |
| Passed行・Aborted・run-level Error・終了2 | PASS　誤受入   |
| Passed行・Failed・run-level Error・終了1  | PASS　誤受入   |

件数、空出力、expected-failure集合、suite構成、内部較正の既存チェックでは、この実行単位の異常を補えない。これは.NETの自然なクラッシュを再現した結果ではなく、プロセスとTRXの境界で宣言した入力に対する結果である。

**修正は、**完了した実行であること、中断・run-level Errorがないこと、終了状態とレポートが整合することを別に要求する。expected-failure suiteは正当に終了1を返せるため、一律の終了0要求にはしない。正常完了・期待通りの失敗・行出力後の中断・実行エラーを対にした回帰試験を追加する。

根拠　[TRX取得後の処理 L1164-L1181](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/method/tools/self-conformance.py#L1164-L1181) ／ [行単位の判定 L1092-L1118](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/method/tools/self-conformance.py#L1092-L1118)

論点 9　P2　特殊な状態の合成再現

## witness が測定していない Git の木を証明する

witnessの生成は実インデックスを一時インデックスへ複製してgit add -Aを行う。skip-worktreeが付いたentryも引き継ぐため、作業ツリーの測定済みbytesが取り込まれず、異なるindexのbytesが証明される場合がある。通常のstaged/unstaged不一致は既存処理で保護される。

隔離した小さなGitリポジトリで、不正YAMLをindexに置きskip-worktreeを設定し、作業ツリーを正しいYAMLへ変えた。C1は作業ツリーを読んでPASSになったが、生成witnessは不正YAMLを含むindexの木と一致した。フラグを外した正常対照では正しい作業ツリーが入り、実インデックスは変わらなかった。

**修正は、**証明前にこの未対応状態を拒否するか、一時インデックスのフラグを正規化して検査したtracked fileを確実に取り込むこと。git addの成否も確認する。回帰試験ではbytesの不一致とskip-worktreeを組み合わせ、実インデックスを保全する。確認範囲はC1とwitness関数の結び付きまでで、全体self-conformanceのPASSやpush成功、自然発生例は示していない。CIも別の防御として残る。

根拠　[witnessの契約と生成 L1672-L1705](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/method/tools/self-conformance.py#L1672-L1705) ／ [C1の作業ツリー読込 L239-L245](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/method/tools/self-conformance.py#L239-L245)

# 実施順序と判断の条件

## 最初に決めること

まず、上流S-BOMを保守性の設計入力とすること、E-BOMを利用者に意味のある機能で区切ること、承認済みE/S版から統括AIがM/CPを導出することを裁定する。既存の裁定記録とlineageを再利用し、並行する承認台帳を増やさない。この方針が確定してから、phase3と各テンプレートの記述を合わせる。

## 次に実装と引渡しの矛盾を直す

C9の実行全体の異常とwitnessの測定bytes不一致は、それぞれ独立した小さな回帰試験を先に用意して修正する。製造パッケージは条件付きの正本を一本化し、G3・phase3・phase4・work orderが同じ集合を使うことを確認する。これらはコンテキスト効率の研究結果を待つ必要がない。

## 既存の受入試行を評価する

ECO-143のCP行別結果を使う試行を継続し、事前登録した主指標を保ったまま、行動機会と明示的な裁定を補助記録する。規範から実行証拠への追跡は1製品で検証する。M6の「両端点へのCP参照がない」という観測を、結合テスト自体がないという主張へ広げない。Routingの参照の存在も、実行可能なゲートの存在と同一視しない。

## 観測結果が出てから一般化を判断する

コンテキストはまず実際の読込と寿命を観測し、既知の前提条件を満たした限定比較へ進む。非GUI CADも媒体ごとの未検証範囲を残し、一つずつ実例で確かめる。新しい記録は、誰がどの判断に使うかを示せるものに限る。消費者のいない記録や、導出できる情報の静的コピーを増やさない。

根拠　[記録の経済性 L1110-L1123](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/method/bomdd-playbook-v1.md#L1110-L1123)

## P3 正本の案内と冒頭のステータスを揃える

READMEはplaybookを現行方法論の正本と明記するが、playbook冒頭には単一題材検証済み・旧method-v1とは未統合という説明が残る。正本の所在と、どの主張がどこまで実証されたかを分けて更新する。正本化を理由に未検証の一般化を実証済みへ格上げする必要はない。

根拠　[正本の案内 L16-L20](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/README.md#L16-L20) ／ [旧ステータスの残存 L3-L5](https://github.com/akiramei/BomDD/blob/069e0d5ab55d893cb8c84bfe8edf39631441ee89/method/bomdd-playbook-v1.md#L3-L5)

## 検証範囲と残る不確実性

本レビューは固定コミットの文書・テンプレート・代表的なゲート実装を読み、2種類の小さな隔離合成試験を行った結果である。リポジトリ本体は変更していない。全テストスイート、実際の.NET実行、下流製品の現在のruntime、別リポジトリのPLM実装、CIやpushの成否は検証対象に含まない。

ECO-090の製品観測は記録済みの結果に基づく。少数・同一の作者と方法・一時点の観測から因果的優位性や効果量は推定しない。提案の採用可否は、承認済みの設計意図を守ったまま、受入の証拠が信頼でき、実際の製造判断に使われるかで決める。
