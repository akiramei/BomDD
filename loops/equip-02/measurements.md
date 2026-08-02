# equip-02 measurements — claude-opus-5 P2 セル(webapi-02 行追加)実測記録

- 測定日: 2026-08-02
- protocol: [protocol.md](protocol.md)(凍結 f80a2e8)・逸脱 0
- prompt bundle: [prompt-bundle.md](prompt-bundle.md)
  (sha256= 4C1EA88762ADC7F593EAAF87545E525773B3FD47F5B2BE2DA64ECE95994CECB4)

## 1. 設備構成の記録(ECO-028 欄様式)

| 欄 | 値 | 来歴 |
|---|---|---|
| 製造 requested | Agent tool `model: "opus"`(ハーネス別名) | observed(呼び出しパラメータ) |
| 製造 resolved | **claude-opus-5[1m]** | **self-reported**(工場の自己申告・証明ではない) |
| ハーネス | Claude Code Agent tool subagent(親= claude-fable-5 セッション) | observed |
| 主観察者(採点・記帳) | claude-fable-5 | observed(本セッション) |
| 検査官 | 機械オラクル(blackbox-oracle.ps1 16 シナリオ)+主観察者突合 | observed |
| git trailer | 本リポ commit は Fable 5(親セッション)— 製造設備の証拠にしない(事前宣言どおり) | observed |

供与物 sha256(先頭 12 桁): 01-ebom= DC9F0D12AF46 / 02-kbom= FEDB0593CAB7 /
03-mbom= 38229D43239E / 04-control-plan= F384BE0F51A4 / 05-routing= 7931223DDB70 /
work-order= 7830AEB640A5(tag `webapi-02-input-bom` = commit 4eed25f から抽出)。

## 2. 時間分解・原価(プロスペクティブ実測)

| 区間 | 実測 |
|---|---|
| V0 ヤードスティック健全性(原版 16/16 一致) | 製造前に実施・不一致 0 |
| 供与物固定 | 2026-08-02T16:46:10+09:00 |
| prompt 凍結・工場起動 | 16:46:48 |
| 製造(工場の壁時計) | **1,057,548 ms ≈ 17 分 38 秒**(ハーネス計測)・tool 呼び出し 42 回 |
| 採点完了(固定オラクル+探索プローブ) | 17:05:15 |
| 全体(供与固定→採点完了) | **約 19 分 05 秒**・人間待ち 0 |
| トークン | subagent_tokens= **147,623**(ハーネス計測・observed) |
| 費用(通貨) | **unknown**(取得手段なし — 推定で埋めない) |

## 3. カウンタ

- **介入: 0**(工場起動後、主観察者は一切介入していない)
- **差戻: 0**(一発で受入到達)
- **範囲外: 0**(工場の自己申告「workspace 外アクセスなし・bomdd/ 無変更」+成果物確認。
  隔離は指示ベース= protocol §4 の宣言済み限界)

## 4. 結果 — 固定オラクル層(合否)

**claude-opus-5 = 0/16(差分ゼロ)** — 事前予測 H-e2-1 的中。帰属= capable factory transfer。

| 工場(as-built 記載機種) | 固定オラクル差分 | 帰属 |
|---|---|---|
| Claude Opus 4.8(webapi-02) | 0/16 | capable factory transfer |
| Claude Sonnet 4.5(webapi-02) | 1/16 | unspecified BOM residue(not_found 名) |
| Claude Haiku 4.5(webapi-02) | 3/16 | specified contract miss(能力) |
| **claude-opus-5(本ラウンド)** | **0/16** | **capable factory transfer** |

- build: 成功(0 warn/0 err)。自己受入: 工場が受入ハーネスを自作し 43 検査 PASS
  (unit 21 / L2 6 / L1 1 / L3 15)。
- 採点結果 JSON: [result-opus5.json](result-opus5.json)(原版突合の生値)。

## 5. 結果 — 探索プローブ層(観測のみ・合否非混在)

| 次元 | original | opus 4.8 | sonnet 4.5 | haiku 4.5 | **opus 5** |
|---|---|---|---|---|---|
| 予約ID 形式 | bk_+16hex | bk_+24hex | bk_+16hex | bk_+12hex | **bk_+24hex** |
| 同内容・別 key で同 ID | False | True(内容のみ) | False | True(内容のみ) | **False(衝突しない)** |
| startUtc エコー | +00:00 | Z | Z | Z | **Z** |
| createdAtUtc | 7桁小数+00:00 | なし | 秒精度 Z | 7桁小数 Z | **なし** |
| cancelledAtUtc | あり | なし | なし | なし | **なし**(cancel 応答= status のみ変化) |

生値: [probe-opus5.json](probe-opus5.json)。

## 6. cheat 報告(工場の自己申告)

**16 件**(CHEAT-OPUS5-001〜016。opus 4.8= 14 / sonnet= 7 / haiku= 4)。
特記: 導出済み項目(header 名・UTC 扱い・fingerprint 対象・status code 主要分)を
「ずるではない」と根拠つきで区別した上で残余の空白のみ起票 — 報告の粒度が高い。
正本: [factory-opus5/cheat-log.md](factory-opus5/cheat-log.md)。

## 7. 観測(予測外・事前登録外 — 記録のみ)

1. **タグ記録の不一致(既存記録側)**: 現タグ `webapi-02-input-bom` の指示先= 4eed25f(git 実測)
   に対し、既存 as-built.yaml / report.md は `abfd667` と記載。本ラウンドはタグ現指示先を正と
   した。歴史記録は改竄しない(要因は未特定 — 観測のみ)。
2. **同一ベンダー系列でも探索層署名は版で変わる**: opus 4.8 と opus 5 は固定オラクル層では
   同値(0/16)だが、ID 一意性が content-only(衝突あり)→ 非衝突へ変化。「探索層の署名」は
   設備識別の傍証になりうる一方、版間で不変とは限らない、の実測 1 例。
3. **受入の自主拡張**: 工場は Control Plan の `status: planned` 2 件(認証表面・並行性)を
   HTTP 実測へ自力昇格し、さらに変異検査 1 件(literal Z 要件の除去→ FAIL 確認→撤回)で
   自作受入の検出力を確認した。前 3 工場の記録には無い行動(検査体制は同一供与物なので、
   設備差の候補観測。n=1 につき記録のみ)。cheat-016 として「L3 を測るか否か」自体を
   分岐リスクと申告している点も含め、検査規律の自発適用が観測された。

## 8. 判定と拘束

- **P2 セルへ claude-opus-5 の行を追加: 0/16・介入 0・差戻 0・一発**。
- equip-01 の暫定能力表 alpha の claude-opus-5 行は「#1 P5×3・n 不足で判定不能」に
  **P2×1(識別つき・プロスペクティブ)が加わる**。依然 n 小 — 率の統計判定はしない
  (protocol §1 の採らない裁定を継承)。
- セル値は検査体制込み(V0 済み固定オラクル 16 シナリオ被覆)の値であり設備単体の能力値では
  ない。routing 根拠への使用禁止(equip-01 と同じ拘束)。
- EXP-20260802-03 の適用実測 1 回目: 記録欄仕様(識別 requested/resolved・来歴・prompt bundle・
  時間分解・3 カウンタ・費用)を protocol へ最初から適用 — **識別・時間の欠落 0**
  (遡及値: 識別 100%/原価 97% 欠落)。費用(通貨)のみ unknown のまま(ハーネスが露出しない)。
