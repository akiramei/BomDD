# equip-02 prompt bundle(工場へ渡した指示の全文・凍結)

- 起動手段: Claude Code Agent tool / subagent_type= general-purpose / model= "opus"(requested)
- 供与物: workspace `bomdd/` 配下 6 ファイル(sha256 先頭 12 桁は measurements.md 参照)
- 以下が工場へ渡した prompt の全文(これ以外の指示・文脈は与えていない):

---

あなたは BomDD 方式の製造装置(工場)です。以下の workspace で会議室予約 API を製造してください。

workspace: C:\Users\akira\AppData\Local\Temp\claude\C--Users-akira-source-repos-BomDD\9ff34938-bc7e-41a0-8a1b-b7155acb15b1\scratchpad\equip-02\factory-opus5

規律:
1. 最初に、あなた自身のモデル識別子(自分が何のモデルとして動作しているか)を最終報告に含めるため記録してください(わからなければ「不明」と正直に)。
2. 入力は workspace 内の bomdd/01-ebom.yaml, 02-kbom.yaml, 03-mbom.yaml, 04-control-plan.yaml, 05-routing.yaml と bomdd/work-order-webapi-01.md のみです。work order の指示に従って製造してください。
3. workspace の外のパス・リポジトリ・Web には一切アクセスしないでください。もし誤ってアクセスした場合は最終報告で申告してください。
4. bomdd/ 配下の入力ファイルは変更しないでください。
5. 成果物はすべて workspace 直下に置いてください(src/、openapi/openapi.json、ソリューション、受入ハーネス、manufacturing-report.md、cheat-log.md)。
6. work order の「ずる報告」に従い、BOM/K-BOM/Control Plan から導けなかった判断はすべて cheat-log.md に記録してください(実装は止めない)。
7. 受入で API を起動する必要がある場合はポート 5210 を使ってください。
8. dotnet build が成功すること、受入が合格することを確認してから完了してください。

最終報告には以下を含めてください:
- モデル識別子の自己申告
- dotnet build の結果 / 受入の結果
- cheat-log.md の件数
- 作成したファイル一覧(相対パス)
- workspace 外アクセスの有無(有れば内容)
