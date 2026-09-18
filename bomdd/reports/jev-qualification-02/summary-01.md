
## 軸スコア(3 回平均・0〜3)と主因(3 回の最頻値)

| 検体 | referent | jargon | density | fact_eval | metaphor | buried_conclusion | evidence_overload | primary(最頻値) | 修正方向 |
|---|---|---|---|---|---|---|---|---|---|
| A_bad | 2.79 | 2.66 | 2.67 | 1.98 | 1.76 | 1.72 | 0.23 | JARGON | DEFINE_OR_REPLACE_TERM |
| A_good | 2.04 | 2.21 | 1.92 | 1.52 | 0.12 | 1.13 | 0.32 | JARGON | DEFINE_OR_REPLACE_TERM |
| B_bad | 2.55 | 2.67 | 2.76 | 0.92 | 0.64 | 0.15 | 2.11 | JARGON | DEFINE_OR_REPLACE_TERM |
| B_good | 1.50 | 1.92 | 2.23 | 0.49 | 0.89 | 0.04 | 1.37 | JARGON | DEFINE_OR_REPLACE_TERM |
| C_bad | 1.95 | 1.17 | 1.28 | 1.44 | 0.11 | 0.45 | 0.18 | JARGON | DEFINE_OR_REPLACE_TERM |
| C_good | 1.89 | 1.31 | 1.14 | 1.43 | 0.53 | 1.02 | 0.18 | JARGON | DEFINE_OR_REPLACE_TERM |
| obs_fix_msg | 2.80 | 2.71 | 2.90 | 1.62 | 1.01 | 1.63 | 2.25 | JARGON | DEFINE_OR_REPLACE_TERM |
| obs_handoff_example | 1.83 | 1.21 | 2.32 | 0.49 | 0.60 | 0.66 | 0.66 | JARGON | DEFINE_OR_REPLACE_TERM |

## 認定条件

① 方向(名指し軸 9 セルで bad−good ≥ 0.5): **5/9**(条件 ≥ 8) → FAIL
   - A:jargon bad 2.66 − good 2.21 = +0.45 MISS
   - A:referent bad 2.79 − good 2.04 = +0.75 OK
   - A:fact_eval bad 1.98 − good 1.52 = +0.46 MISS
   - A:metaphor bad 1.76 − good 0.12 = +1.63 OK
   - A:density bad 2.67 − good 1.92 = +0.75 OK
   - B:jargon bad 2.67 − good 1.92 = +0.75 OK
   - B:buried_conclusion bad 0.15 − good 0.04 = +0.11 MISS
   - B:evidence_overload bad 2.11 − good 1.37 = +0.74 OK
   - C:buried_conclusion bad 0.45 − good 1.02 = -0.56 MISS
   - A_bad primary= JARGON(期待 TOO_DENSE) MISS
   - B_bad primary= JARGON(期待 JARGON) OK
   - C_bad primary= JARGON(期待 AMBIGUOUS_REFERENCE/BURIED_CONCLUSION) MISS
② 主因(bad 側の最頻値が第三者の主因と一致): **1/3**(条件 ≥ 2) → FAIL
③ good 側の偽陽性(good 3 本 × 7 軸で平均 < 2.0): **18/21**(条件 21/21) → FAIL — 違反: A_good:referent=2.04, A_good:jargon=2.21, B_good:density=2.23
④ 再現性(56 セルで 3 回の範囲 ≤ 0.5): **56/56**(条件 ≥ 50) → PASS — 最大範囲: C_bad:referent=0.24, C_good:fact_eval=0.14, B_bad:metaphor=0.13, obs_fix_msg:buried_conclusion=0.13, C_good:referent=0.12

**判定: 未達 → この質問設計では採らない**

requests=24 tokens in=65139 out=5064 model=['jev-1.13.0']
