[DECIDE / PAUSED]

**裁定してほしい点は 1 つ**: 運転層配布 第 2 弾の範囲を、契約と台帳の文書配布に絞るか、製品側の機械検査まで含めるか、ツールごと移植するか。

preflight の結論: 開始条件は「範囲の裁定」だけが欠けています。開始点(HEAD 95a1d9c・作業木 clean)、現在状態(ECO-062 §7 の現在地= 第 2 弾は user 裁定待ち・ECO-075 verified)、残課題(EXP-20260914-01 の 4 項目= bomdd-job の self-conformance 非依存化・配員欄の機械検査・run 台帳の配置と hook・設備台帳テンプレート)は正本で確認できました。何が通れば完了かは未定義なので、起票の前にここで決めます。

実測で分かった前提が 2 つあります。第一に、製品リポの変更管理は process-core(profile が register の場所と状態語彙を決め、hooks と process-validator が強制)で動いており、運転層 3 ツール(job/witness/run・約 2,500 行)は BomDD 自リポの台帳配置と状態語彙(filed/in-progress/implemented/verified)に結合しています。製品側は staged/applied または ViewTube 型の 3 状態で、ECO 本文は自由形式、配員欄はありません。第二に、ViewTube は独自に「装置パスを staged にする commit は ECO を名乗る」検査を持っています(ECO-VT-164/165)。設備の概念は製品側で既に芽生えていて、配布はそれと整合させる必要があります。

| 案 | 得るもの | 失うもの | 戻せるか | 採ると次に起きること |
|---|---|---|---|---|
| **A 契約と台帳の文書配布(推奨)** | 運転層の契約(job/receipt/ruling は台帳の射影・停止語彙・設備台帳の 3 軸と独立性規則・配員は register 側の欄)を product-profile に core/adapter 形で正本化し、設備台帳テンプレートを kit に追加。製品側で配員と設備を書き始められ、後の機械化が読む対象が固定される | 製品側の機械強制はまだない | はい(文書とテンプレのみ) | ECO-081 起票(文書+テンプレ・製造者較正+Codex 境界探索 1 round) |
| B 機械検査を process-core に載せる | A に加え、設備台帳がある製品リポでだけ process-validator が配員の実在と独立性(producer≠inspector・3 軸)を検査する | process-core は 6 製品リポに設置済みの核で、変更は全製品へ波及し qualification の再実行が要る。ViewTube の独自検査との整合が別課題になる | ECO 経由でのみ | instrument-change クラス・異系統検査・kit 再設置 |
| C ツールごと移植 | BomDD 自リポと同じ運転層(job/witness/run)を製品で使える | 3 ツールを process-core の profile に合わせて再設計(状態語彙 2 系統の写像)。process-validator との二重統治 | 難しい | 設計の収束(converge)が先で、弧 1 本に収まらない |

recommendation: **A**。B が劣る理由は、製品側で配員取り違えの実害がまだ 1 件も観測されていない段階で全製品に波及する検査を足すことになり、converge 凍結時の裁定(証明のための複雑性を足さない)に反するからです。C が劣る理由は、process-core と運転層の二重統治(ECO-025 で自リポ側に退けた構図の裏返し)になるからです。A は B・C の前提になる部分だけを先に固定するので、後で B に進む道は残ります。

reply_format: `A / B / C`。A なら、対象製品を ViewTube に置いて設備台帳の初期値(EQ-001〜003 相当)を用意してよいかも一言ください(なければ雛形のみ・値は空欄)。
