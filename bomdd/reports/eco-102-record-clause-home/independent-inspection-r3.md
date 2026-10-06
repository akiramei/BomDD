[INFORM / COMPLETE]

REJECT

- inspector: EQ-002 / Codex CLI / gpt-5.6-sol
- HEAD at start / at end: b5592120c3785f116e0b89a96ac6d2a9d42c3e89 / b5592120c3785f116e0b89a96ac6d2a9d42c3e89
- commit: 0 / ファイル変更: 0（終了時 `git status --short` 出力なし）
- 写しの sha256 の照合: 7本すべて一致
  - `viewtube-32-mbom-invariant-entries.txt`: `7e78a63bfe1d1b7cf241478ca13d3ebbccee3dd2bd03213c2e9610c003ba5456`
  - `viewprism2-32-mbom-invariant-entries.txt`: `6daf9821646e22207b80c1a7be5a6ac2a9d80585b8ecd1c7cae73ebfd206bf6d`
  - `viewtube-eco-ids-of-the-entries.txt`: `222e7980ec4c88b24f455d384b7b4a51ca1e62581e8e25654b60b0082e48d08c`
  - `viewtube-eco-vt-232-body.md`: `57a637b4295c60f8cc752f8671d192d2886ff38a74a288e94af93e00ecff8c57`
  - `viewtube-register-eco-vt-232.yaml`: `9b80df3b7c63a466e986cc38702d19e95ac0812b812a7d540bf81678a2d56543`
  - `viewtube-33-known-limits-lines.txt`: `53e08aacfc864bd77acb220eb06c5fecb1b6b8d61876b3d88286d3ebcecb4bb0`
  - `viewtube-31-kbom-measured-lines.txt`: `ea5429c6982d6b125a55268a4ff19f2336618694208ca299639f491df732f413`

## 項目ごとの判定

| # | 項目 | 判定 | 根拠(file:line・コマンドと出力の要点) |
|---|---|---|---|
| 1 | 範囲 | PASS | `git diff --stat/name-only 37c4f82…b559212` は register の `allowed_paths`（`bomdd/60-change-register.yaml:3249`）内の18パスのみ。playbook の `git diff -U0` は旧348行と356行の2 hunkだけで、ともに §4.5 内。§4.4・§9・§13 に差分なし。 |
| 2 | V1 の句 | PASS | `Select-String -SimpleMatch` の結果: `変更記録…` 1件(L348)、`ECO 番号の参照だけを残す` 1件(L348)、`known_limits` 3件(L349,352,360)、`M-BOM の記録句` 1件(L348)、`ECO-102` 1件(L349)、`**未測定**` 1件(L360)、`置き場は**未決**` 0件。見出しL344は candidate のまま。 |
| 3 | 記録との一致 | FAIL — blocking | 全要素写しの独立再計数は ViewTube `128/87/87/17/54/5/14`、ViewPrism2 `63/0/15/0/0/0/1` で `measurements.txt:16-34` と一致。26 IDの body/register=yes も一致。しかし order `:36` の「ECO 本文と台帳が完全に持つ」は、記録が示す「本文の語彙計数＋台帳項の存在」より強い。order `:43` の「ViewPrism2 は由来のみ」も裁定語1件という同 order `:30`・測定記録`:29`と両立しない。さらに order `:94` は削除済み写し名・2本という旧状態を現在の製造記録として残す。 |
| 4 | 既存本文との整合 | PASS | `known_limits` は検査行内(`33-control-plan.yaml:47-49`)で、検査対象との結線を担う `invariant_refs`(`:34-36`)を置換しない。§13 の記録の経済(`playbook:1143-1149`)と「正本一つ・参照」の形は両立。As-Built の `test_evidence_refs`(`50-as-built.yaml:32-40`)は個体ごとの再測定結果であり、検査行自身の未測定範囲とは役割が異なる。ECO-086/098/100 の candidate と正面衝突なし。 |
| 5 | テンプレの健全性 | PASS | 指定の `python -c` で32・33とも `yaml.safe_load` 成功。差分は32のコメント2行、33の `known_limits: []` とコメント3行だけ。欄は主検査行の要素内(`33-control-plan.yaml:47`)。表示パリティ行は別の簡略例で、既に `when/on_fail/invariant_refs/test_vectors` も省略しているため、新欄がないことはスキーマ否定を意味しない。 |
| 6 | 言い回し | PASS | §4.5 L348で対象範囲と四種の具体例を伴い「局所名= M-BOM の記録句」と定義。ECO-100 IA-01の同語問題を回収しており、通常の変更記録や§13の一般的な「記録」と区別して一意に読める。 |

## 所見(IA-01, IA-02, …)

- IA-01 — CLOSED。7写しすべてについて、独立計算した sha256 が `measurements.txt:79-85` と一致。
- IA-02 — CLOSED。全要素写しから項目単位で再計数でき、ViewTube の `128 / 87 / 17 / 54 / 5 / 14` と一致。
- IA-03 — CLOSED。K-BOM の該当2行が写され、いずれも知識の名称・文であり、日付・値・版を持つ実測記録ではない。
- IA-04 — CLOSED。製造物自体の配置・テンプレ構造には blocking 不整合なし。
- IA-05 — OPEN / blocking。`bomdd/60-change-order-eco-102.md:36` の「実測値・所見・由来の正本は今でも ECO 本文と台帳が完全に持つ」は過大。記録が示すのは、26本文すべてが実測・所見の語を含むことと、26台帳項が存在することまで。個々の記録内容が本文と台帳の双方に完全収載されることは測っていない。
- IA-06 — OPEN / blocking。`bomdd/60-change-order-eco-102.md:43` の「ViewPrism2 は由来のみ」は、同ファイル`:30`および `measurements.txt:23-29` の「裁定の語1件」と矛盾する排他表現。「実測値・所見・未検査の語は0、ECO参照15、裁定語1」に限定する必要がある。
- IA-07 — blocking。`bomdd/60-change-order-eco-102.md:94` は測定の写しを旧 `viewtube-32-mbom-invariant-lines.txt`（現存せず）等2本と記述する。r3の実体は7本で、同 order `:123-125` および `measurements.txt:78-85` と不一致。製造・受入の事実記録として更新されていない。

## 較正 receipt

- 査定した主張: 「r3 の記録は §0.2・§4.5④および order の事実主張を支え、IA-05/06を閉じる」
- 判定: **observed / 不適格**。数値再計数と写しの同一性は適格だが、order に記録より強い主張と旧写し記述が残るため、全体の昇格根拠には使用不可。
- 計器欠陥: 集計コードの出力と全要素写しの再計数に不一致なし。欠陥帰属は製造物本文ではなく order の主張・記録更新。
- battery: Q1 asked / Q2 NA / Q3 asked / Q4 asked / Q5 asked / Q6 NA / Q7 NA / Q8 NA / Q9 asked / Q10 asked / Q11 asked。

## 検査しなかったこと(限界)

- ViewTube / ViewPrism2 のリポ本体は読んでいない。写しと BomDD 内の測定記録だけを検査した。
- `self-conformance`、worklist、CI、ビルド、テスト、外部 API は実行していない。
- 26本のECO本文すべては写されていないため、本文語彙の集計は `measurements.txt` と計数コードの読解まで。独立再計数できたのはM-BOM全要素写し、26 IDの存在一覧、Control Plan/K-BOMの写し、およびECO-VT-232の例。
- 語彙出現数は記録内容の意味的完全性を証明しない。

human_action: none。execution: COMPLETE — 指定範囲の独立検査を終了し、blocking 3件により REJECT。