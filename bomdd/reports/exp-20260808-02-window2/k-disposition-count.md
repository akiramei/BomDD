# K(記録層)所見 91 件の処置分類(read-only 集計・2026-09-29)

入力: bomdd/reports/exp-20260808-02-window2/classified.tsv layer==K(91 行・README の 記録 45+46 と一致)
処置の出典: ViewTube bomdd/eco/ECO-VT-NNN-independent-review.md(-ir と略)/ test-results/eco-vt-{186,189}-*/r8-round-N.yaml / bomdd/eco/ECO-VT-{210,211}.md / change-register.yaml

## 1. ECO 別

| ECO | 種別 | K | CORRECTED | CARRIED | SHRUNK | REJECTED | UNKNOWN |
|---|---|---|---|---|---|---|---|
| 186 | 工程 | 4 | 2 | 2 | 0 | 0 | 0 |
| 187 | 工程 | 9 | 3 | 6 | 0 | 0 | 0 |
| 189 | 工程 | 6 | 6 | 0 | 0 | 0 | 0 |
| 191 | 工程 | 5 | 1 | 4 | 0 | 0 | 0 |
| 192 | 工程 | 17 | 9 | 8 | 0 | 0 | 0 |
| 193 | 製品 | 3 | 3 | 0 | 0 | 0 | 0 |
| 194 | 製品 | 2 | 1 | 1 | 0 | 0 | 0 |
| 195 | 製品 | 7 | 4 | 3 | 0 | 0 | 0 |
| 196 | 製品 | 1 | 1 | 0 | 0 | 0 | 0 |
| 197 | 製品 | 4 | 1 | 3 | 0 | 0 | 0 |
| 198 | 製品 | 4 | 3 | 1 | 0 | 0 | 0 |
| 199 | 製品 | 4 | 2 | 2 | 0 | 0 | 0 |
| 200 | 製品 | 3 | 3 | 0 | 0 | 0 | 0 |
| 201 | 製品 | 2 | 1 | 1 | 0 | 0 | 0 |
| 202 | 製品 | 3 | 2 | 1 | 0 | 0 | 0 |
| 203 | 製品 | 1 | 1 | 0 | 0 | 0 | 0 |
| 204 | 製品 | 2 | 1 | 1 | 0 | 0 | 0 |
| 205 | 製品 | 1 | 1 | 0 | 0 | 0 | 0 |
| 206 | 製品 | 2 | 1 | 1 | 0 | 0 | 0 |
| 207 | 製品 | 2 | 2 | 0 | 0 | 0 | 0 |
| 208 | 工程 | 4 | 2 | 2 | 0 | 0 | 0 |
| 209 | 製品 | 2 | 1 | 1 | 0 | 0 | 0 |
| 210 | 製品 | 2 | 2 | 0 | 0 | 0 | 0 |
| 211 | 製品 | 1 | 1 | 0 | 0 | 0 | 0 |
| **計** | | **91** | **54** | **37** | **0** | **0** | **0** |

## 2. 合計と分割

| 区分 | K | CORRECTED | CARRIED |
|---|---|---|---|
| 全体 | 91 | 54 (59%) | 37 (41%) |
| (a) 非最終回 計 | 62 | 49 (79%) | 13 (21%) |
| (a-1) 多ラウンド ECO の第 1 回 | 38 | 32 | 6 |
| (a-2) 停止条件以前(186・189、2026-09-23) | 10 | 8 | 2 |
| (a-3) 単一ラウンド ECO(194/203/204/205/207/208/209・第 1 回 PASS で終了) | 14 | 9 | 5 |
| (b) 停止条件下の最終回(第 2 回) | 29 | 5 (17%) | 24 (83%) |

| 区分 | K | CORRECTED | CARRIED |
|---|---|---|---|
| 工程 ECO(186/187/189/191/192/208) 計 | 45 | 23 | 22 |
| 工程・非最終回 | 30 | 23 | 7 |
| 工程・最終回(187/191/192 第 2 回) | 15 | 0 | 15 |
| 製品 ECO(193〜207/209〜211) 計 | 46 | 31 | 15 |
| 製品・非最終回 | 32 | 26 | 6 |
| 製品・最終回 | 14 | 5 | 9 |

SHRUNK・REJECTED・UNKNOWN は 0(全 91 件に処置を確認)。主張縮小の処置は本窓では E/V 層(I192b-F1・R198b-F1・R200b-F1・R206b-F1)にのみ現れ、K 層には無い。

最終回でも記録訂正が流れた 5 件: R193b-F3(新 ECO 起票)・R195b-F1・R198b-F3・R206b-F4・R210b-F1 — いずれも「製品は変えない」宣言の下で本文の後節・登録簿に訂正を追記。工程 ECO の最終回は 15/15 CARRIED。

## 3. 所見別(eco, id, round, final?, disposition, 出典 file:line)

186-R186-F1 r1 n CORRECTED — test-results/eco-vt-186-*/r8-round-1.yaml:91(別 ECO-VT-189 起票 → ECO-VT-189.md §5 で修理)
186-R186-F2 r1 n CORRECTED — r8-round-1.yaml:92 → r8-round-2.yaml:16(ECO-VT-188 で closed)
186-R186-F4 r1 n CARRIED — r8-round-1.yaml:95 "stay as recorded"
186-R186-F6 r1 n CARRIED — r8-round-1.yaml:95
187-I187a-F1 r1 n CORRECTED — ECO-VT-187-ir.md:108(本文 §6 に主張文を逐語で追加・carrier 宣言)
187-R187a-F1 r1 n CORRECTED — ECO-VT-187-ir.md:108
187-R187a-F6 r1 n CARRIED — ECO-VT-187-ir.md:134(「主張文として読む」・記録本文は不変)
187-R187a-F7 r1 n CORRECTED — ECO-VT-187-ir.md:136(register に key 追記)
187-R187a-F8 r1 n CARRIED — ECO-VT-187-ir.md:137(ECO-VT-190 R190b-F6 として持ち越し)
187-R187b-F1 r2 y CARRIED — ECO-VT-187-ir.md:220-223
187-R187b-F2 r2 y CARRIED — ECO-VT-187-ir.md:224-226
187-R187b-F4 r2 y CARRIED — ECO-VT-187-ir.md:227
187-R187b-F5 r2 y CARRIED — ECO-VT-187-ir.md:227
189-R189-F1 r1 n CORRECTED — test-results/eco-vt-189-*/r8-round-1.yaml:85(ECO-VT-189.md §6 追記)
189-R189-F2 r1 n CORRECTED — r8-round-1.yaml:86
189-R189-F3 r1 n CORRECTED — r8-round-1.yaml:87(§6 に処置を記録)
189-R189-F4 r1 n CORRECTED — r8-round-1.yaml:88 "corrected by appending"
189-R189-F5 r1 n CORRECTED — r8-round-1.yaml:88
189-R189-F6 r1 n CORRECTED — r8-round-1.yaml:88
191-I191a-F5 r1 n CARRIED — ECO-VT-191-ir.md:134
191-R191a-F5 r1 n CORRECTED — ECO-VT-191-ir.md:136((a)(d) repaired・(b) carried・(c) closed)
191-R191b-F5 r2 y CARRIED — ECO-VT-191-ir.md:229
191-I191b-F3 r2 y CARRIED — ECO-VT-191-ir.md:230
191-I191b-F4 r2 y CARRIED — ECO-VT-191-ir.md:231
192-I192a-F6 r1 n CORRECTED — ECO-VT-192-ir.md:206
192-I192a-F7 r1 n CORRECTED — ECO-VT-192-ir.md:207
192-R192a-F11 r1 n CORRECTED — ECO-VT-192-ir.md:205
192-R192a-F12 r1 n CORRECTED — ECO-VT-192-ir.md:208
192-R192a-F2 r1 n CORRECTED — ECO-VT-192-ir.md:193
192-R192a-F4 r1 n CORRECTED — ECO-VT-192-ir.md:198
192-R192a-F6 r1 n CORRECTED — ECO-VT-192-ir.md:200
192-R192a-F7 r1 n CORRECTED — ECO-VT-192-ir.md:201
192-R192a-F8 r1 n CORRECTED — ECO-VT-192-ir.md:202
192-R192b-F11 r2 y CARRIED — ECO-VT-192-ir.md:355
192-R192b-F2 r2 y CARRIED — ECO-VT-192-ir.md:342(material と読み替え・carried)
192-R192b-F3 r2 y CARRIED — ECO-VT-192-ir.md:346
192-R192b-F4 r2 y CARRIED — ECO-VT-192-ir.md:348
192-R192b-F5 r2 y CARRIED — ECO-VT-192-ir.md:349
192-R192b-F6 r2 y CARRIED — ECO-VT-192-ir.md:350
192-R192b-F8 r2 y CARRIED — ECO-VT-192-ir.md:352
192-R192b-F9 r2 y CARRIED — ECO-VT-192-ir.md:353
193-R193a-F5 r1 n CORRECTED — ECO-VT-193-ir.md:250(manifest correction key)
193-R193a-F7 r1 n CORRECTED — ECO-VT-193-ir.md:252(本文 §7・register title note)
193-R193b-F3 r2 y CORRECTED — ECO-VT-193-ir.md:425 "the new ECO is filed next" → ECO-VT-195.md:5 が R193a-F1/F2 を起票根拠に
194-R194a-F3 r1 n CORRECTED — ECO-VT-194-ir.md:174
194-R194a-F7 r1 n CARRIED — ECO-VT-194-ir.md:178(コメントは直さず本文 §9 に記録)
195-R195a-F1 r1 n CORRECTED — ECO-VT-195-ir.md:396
195-R195a-F6 r1 n CORRECTED — ECO-VT-195-ir.md:401
195-R195a-F7 r1 n CARRIED — ECO-VT-195-ir.md:402
195-R195a-F8 r1 n CORRECTED — ECO-VT-195-ir.md:403(件数訂正・残りは carried)
195-R195b-F1 r2 y CORRECTED — ECO-VT-195-ir.md:701(本文 §10 が §9 を訂正)
195-R195b-F4 r2 y CARRIED — ECO-VT-195-ir.md:704
195-R195b-F5 r2 y CARRIED — ECO-VT-195-ir.md:705
196-R196a-F5 r1 n CORRECTED — ECO-VT-196-ir.md:217
197-R197a-F8 r1 n CORRECTED — ECO-VT-197-ir.md:239 → ECO-VT-197.md:73(§7 に訂正文)
197-R197b-F3 r2 y CARRIED — ECO-VT-197-ir.md:416
197-R197b-F4 r2 y CARRIED — ECO-VT-197-ir.md:417
197-R197b-F5 r2 y CARRIED — ECO-VT-197-ir.md:418
198-R198a-F5 r1 n CORRECTED — ECO-VT-198-ir.md:291 → ECO-VT-198.md:68
198-R198a-F7 r1 n CARRIED — ECO-VT-198-ir.md:293 → ECO-VT-198.md:75
198-R198a-F8 r1 n CORRECTED — ECO-VT-198-ir.md:294 → ECO-VT-198.md:69(§7 に訂正文)
198-R198b-F3 r2 y CORRECTED — ECO-VT-198-ir.md:556(§8 が §7 を訂正)
199-R199a-F6 r1 n CORRECTED — ECO-VT-199-ir.md:179(M-BOM 不変条件を M-APP-SHELL-001 へ移動)
199-R199a-F7 r1 n CORRECTED — ECO-VT-199-ir.md:180
199-R199b-F2 r2 y CARRIED — ECO-VT-199-ir.md:316("carried; read … as")
199-R199b-F3 r2 y CARRIED — ECO-VT-199-ir.md:317
200-R200a-F2 r1 n CORRECTED — ECO-VT-200-ir.md:201(REQ-037 本文を裁定どおり書き換え)
200-R200a-F3 r1 n CORRECTED — ECO-VT-200-ir.md:202
200-R200a-F4 r1 n CORRECTED — ECO-VT-200-ir.md:203
201-R201a-F2 r1 n CORRECTED — ECO-VT-201-ir.md:131
201-R201b-F4 r2 y CARRIED — ECO-VT-201-ir.md:331
202-R202a-F5 r1 n CORRECTED — ECO-VT-202-ir.md:100
202-R202a-F6 r1 n CORRECTED — ECO-VT-202-ir.md:101(見出し欠陥は ECO-VT-203 起票・M-BOM 文言訂正)
202-R202b-F1 r2 y CARRIED — ECO-VT-202-ir.md:214
203-R203a-F2 r1 n CORRECTED — ECO-VT-203-ir.md:149(frames-note.md と本文 §7 に読み替えを記録)
204-R204a-F2 r1 n CORRECTED — ECO-VT-204-ir.md:249
204-R204a-F4 r1 n CARRIED — ECO-VT-204-ir.md:251
205-R205a-F5 r1 n CORRECTED — ECO-VT-205-ir.md:297
206-R206a-F4 r1 n CARRIED — ECO-VT-206-ir.md:258
206-R206b-F4 r2 y CORRECTED — ECO-VT-206-ir.md:486(§8 が文言訂正)
207-R207a-F2 r1 n CORRECTED — ECO-VT-207-ir.md:248
207-R207a-F3 r1 n CORRECTED — ECO-VT-207-ir.md:249
208-R208a-F2 r1 n CORRECTED — ECO-VT-208-ir.md:248
208-R208a-F3 r1 n CARRIED — ECO-VT-208-ir.md:249
208-R208a-F4 r1 n CARRIED — ECO-VT-208-ir.md:250
208-R208a-F6 r1 n CORRECTED — ECO-VT-208-ir.md:252
209-R209a-F1 r1 n CORRECTED — ECO-VT-209-ir.md:244
209-R209a-F3 r1 n CARRIED — ECO-VT-209-ir.md:246
210-R210a-F7 r1 n CORRECTED — ECO-VT-210.md:101-107(4 点中 3 点訂正・register measured_by_the_probe は残り → R210b-F1)
210-R210b-F1 r2 y CORRECTED — ECO-VT-210.md:122-125・change-register.yaml:37341-37342
211-R211a-F5 r1 n CORRECTED — ECO-VT-211.md:131(§7 に一行追記)

## 4. 判断

- 分類規則: 処置行に carried/持ち越し とあれば CARRIED(「carried, recorded in body section N」を含む — 本文注記は持ち越しの記録であって対象の訂正ではない)。処置ブロックの外の記録(本文の後節・manifest/register key・M-BOM/REQ/requirement-amendments・inventory・別 ECO 起票)を変えたと書かれていれば CORRECTED。
- 「read X as Y」で本文不変(R187a-F6・R199b-F2・R199b-F3)は REJECTED でなく CARRIED(所見を争わず読み方を裁定)。R203a-F2 は読み替えを frames-note.md と本文 §7 に書いたので CORRECTED。
- 別 ECO へ回した件: その ECO が記録を直したなら CORRECTED(R186-F1→189・R186-F2→188・R193b-F3→195 起票・R202a-F6→203)、別 ECO の記録に持ち越しただけなら CARRIED(R187a-F8→R190b-F6)。
- 複数部分の所見(R191a-F5・R195a-F8・R210a-F7)は一部でも訂正されれば CORRECTED(問いが「是正へ流れたか」のため)。
- R200a-F2 は REQ-037 本文の書き換えなので SHRUNK でなく CORRECTED(記録そのものが変わった)。
- final? は「停止条件下で最後と宣言された回」のみ y。186・189(2026-09-23)は stop_condition_2026_09_25 以前で n。単一ラウンド ECO(194/203/204/205/207/208/209)は第 1 回 PASS で終了し停止条件は発動していないため n(分割 (a-3) として別掲)。196 は第 2 回が最終宣言の後に例外第 3 回があるが、K 所見は第 1 回のみ。
- 193 第 2 回は「指示された処置の実行ミスの復元」を新規修理と見なさない basis で処置(ir.md:421)。K 所見 R193b-F3 の新 ECO 起票はそれとは別に実行された。
- 191 第 1 回はエントリ 9 件・totals 10(README 既知)。K 分類は classified.tsv の行のまま。
