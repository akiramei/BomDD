# equip-03 prompt bundle(工場へ渡した指示の全文・凍結)

- 起動手段: Claude Code Agent tool / subagent_type= general-purpose / model= "opus"(requested)
- 以下が工場へ渡した prompt の全文(これ以外の指示・文脈は与えていない):

---

あなたは BomDD 方式の製造装置(工場)です。以下の workspace で Plm リポの ECO-006 を適用製造してください。

workspace リポ: C:\Users\akira\AppData\Local\Temp\claude\C--Users-akira-source-repos-BomDD\9ff34938-bc7e-41a0-8a1b-b7155acb15b1\scratchpad\equip-03\plm-eco006(tag eco-006-input で検証済み)
採点器(凍結複写): C:\Users\akira\AppData\Local\Temp\claude\C--Users-akira-source-repos-BomDD\9ff34938-bc7e-41a0-8a1b-b7155acb15b1\scratchpad\equip-03\tools\impact-retrospective.py
lint 出力先: C:\Users\akira\AppData\Local\Temp\claude\C--Users-akira-source-repos-BomDD\9ff34938-bc7e-41a0-8a1b-b7155acb15b1\scratchpad\equip-03\out

規律:
1. 最初に、あなた自身のモデル識別子を記録し最終報告に含めてください(わからなければ「不明」と正直に)。
2. work order は workspace リポ内の bomdd/60-change-order-eco-006.md です。入力はこのリポの内容のみ。上記 3 パス(リポ・採点器・出力先)以外の場所・他リポ・Web へは一切アクセスしないでください。誤ってアクセスした場合は最終報告で申告してください。
3. リポ内で変更してよいのは bomdd/ 配下のみです(diff_audit allowed_paths= bomdd/)。src・test・oracle・schemas・.github の実体は変更しないでください。build/test の実行で生成物(dist 等)が変わった場合は git restore で復元し、報告に記載してください。
4. 手順:
   (a) work order §1〜§2 を読み、影響分析を bomdd/61-impact-analysis-eco-006.md へ起草する(既存の 61-impact-analysis-eco-001/002 の様式に整合させ、裁定点 2 点〔生成物の帰属方式・unit 粒度/命名〕の設計根拠を含める)。
   (b) bomdd/32-mbom.yaml へ所有宣言を実装する(M-BOM 冒頭の粒度原則との整合を 61 に明記)。
   (c) 自己受入を実測する: ①python <採点器> --repo . で summary.decomposition.unmapped_files = 0 かつ summary.real_under_files = 111 ②npm run build が 0 エラー ③npm test 全通過 ④node packages/cli/dist/main.js . --eco --out <lint 出力先>/self で error/warn 0 ⑤git status --porcelain で変更が bomdd/ のみ。
   (d) BOM/order から導けなかった判断は bomdd/51-cheat-log.md へ既存様式で追記する(実装は止めない)。
   (e) 製造報告を workspace 直下(リポ外)の factory-report.md へ書く。
5. git commit はしないでください(設計者側が行います)。
6. 最終報告には以下を含めてください: モデル識別子の自己申告/自己受入 5 点の実測値/変更・新規ファイル一覧/ずる報告件数/workspace 外アクセスの有無。
