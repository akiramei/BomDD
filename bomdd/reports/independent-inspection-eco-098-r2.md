[INFORM / COMPLETE]

REJECT IA-01 / IA-02

- range: 是正確認+回帰
- inspector: EQ-002 / Codex CLI / gpt-5.6-sol
- 対象 revision: 8d84edb86c85bbd01c94dfb5a3181004c6de602a
- commit: 0
- 外部 API: 呼出しなし
- 読んだファイル一覧: `bomdd/60-change-order-eco-098.md`、`bomdd/60-change-register.yaml`、`bomdd/reports/independent-inspection-eco-098.md`、`method/bomdd-playbook-v1.md`。加えて `method/templates/32-mbom.yaml`・`method/templates/33-control-plan.yaml` の revision 間および作業ツリー差分を確認。
- 開始時 `git status --short`: `M bomdd/60-change-order-eco-098.md`、`M bomdd/60-change-register.yaml`、`M method/bomdd-playbook-v1.md`、`?? bomdd/reports/independent-inspection-eco-098.md`
- 終了時: 開始時と同一

## 判定概要

| 項目 | 判定 | 観測 |
|---|---|---|
| 1. IA-01 の是正確認 | **FAIL** | 対象 revision の §9 見出しは依然 `candidate・ECO-097 試行 N=1・ECO-098` で、「2 製造単位・1 製品」がない。V1 は不成立。意図された是正は未コミットの作業ツリーにのみ存在する。 |
| 2. 是正の範囲 | **FAIL** | `8d84edb` と指定された完全 SHA は同一コミットに解決される。このため指定の `git diff 8d84edb 8d84edb86c85bbd01c94dfb5a3181004c6de602a` は空で、「1 行の変更だけ」という条件を満たさない。作業ツリー上の playbook 差分自体は意図どおりの 1 行で、観測された全変更パスは `allowed_paths` 内。 |
| 3. 回帰 | PASS | r1 で PASS の項目 2・4・5・6を覆す変更は対象 revision にない。未コミットの是正 1 行も規模句の追加だけで、新しい不一致・矛盾・参照誤りは認めない。指定の revision 間および作業ツリーで 32・33 テンプレ差分は空。 |

## 所見

### IA-01 — blocking — 対象 revision では是正されていない

対象 revision の `method/bomdd-playbook-v1.md` §9 は r1 と同じ文面であり、ECO-098 §3 V1 が要求する「N=1・2 製造単位・1 製品」の完全な規模表示を満たさない。

作業ツリーには期待された見出しへの是正が存在するが、対象 revision の内容ではないため適合根拠にできない。

### IA-02 — blocking — 是正差分の revision 窓がゼロ幅

短縮 SHA `8d84edb` は対象 SHAそのものに解決される。指定された revision 間差分は空であり、是正の 1 行を対象 revision の差分として観測できない。

## 範囲外の観察(判定に含めない)

開始時から未コミットの変更が存在した。そこには §9 の意図された 1 行是正、r1 報告、order/register の更新が含まれ、いずれも ECO-098 の `allowed_paths` 内だった。