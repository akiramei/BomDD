# Change Order — ECO-102(「記録」の置き場の決定 — M-BOM の記録句は変更記録を正本とし、行には ECO 番号の参照だけを残し、検査していないことの注記は Control Plan の `known_limits` へ〔文書とテンプレのみ・candidate〕)

> 裁定: user DECIDE「A」(2026-10-06・本 ECO の起票の直前)= 変更記録(60 番台: ECO 本文と台帳)が正本。M-BOM の行は ECO 番号の参照だけを残す。検査していないことの注記だけは Control Plan の `known_limits` へ。
> 示した選択肢: A(上記)/ B(種類ごとに 50 番台へ分ける: 実測値→As-Built・所見→60・注記→CP・由来→参照)/ C(M-BOM に残して別の欄に分離)。推奨は A と添えた。
> 出典: playbook §4.5 ④(ECO-100 で「置き場は未決」と明記)/ OBS-20261005-03(候補= K-BOM・As-Built・Control Plan・変更記録)/ ECO-100 IA-01(区分の名「記録」は他の節の語と同じ— 置き場を決めるときに名を決める)。

## 担当設備(equipment)

- 起票・設計・製造: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**
- producer: EQ-001
- 独立検査: EQ-002(Codex CLI / gpt-5.6-sol・異系統)— method 本文とテンプレの改訂のため受ける。

## 0. 根拠(起票・2026-10-07・裁定は 2026-10-06)

### 0.1 未決のまま残したもの

- playbook §4.5 の④: 「記録(実測値・レビューの所見・検査していないことの注記・ECO と裁定の由来)は設計の内容でも作り方でもない。置き場は**未決**で(候補= K-BOM・As-Built・Control Plan・変更記録・OBS-20261005-03)、決まるまでは①〜③と区別できる形で残す」(ECO-100・L348)。
- 32 テンプレの `invariants` のコメント: 「記録(…)は設計の内容でも作り方でもない— 置き場は未決(playbook §4.5)」(L39)。
- ECO-100 の独立検査の non-blocking 所見 IA-01: 区分の名「記録」は playbook の別の話題の「記録」(§13 記録の経済・レビュー所見の処置区分)と同じ語。置き場を決める改訂のときに局所名を与える。

### 0.2 実測(2026-10-06・製造者・ViewTube と ViewPrism2 の作業木を読んだだけ。書き込みなし)

- ViewTube `bomdd/32-mbom.yaml`: 不変条件の行 60。**60 行すべてが ECO 番号で始まる**(由来の記録は全行)。`measured` を含む行 21。`review` / `round` / 所見 ID を含む行 95(重複あり)。「検査していない」の注記(not exercised / not covered / not captured 等)を含む行 6。`ruling` を含む行 15。
- ViewTube `bomdd/50-as-built.yaml`: 244 行・エントリ 8 件(工場ごとの派生製造・現場是正・CAPA)。**最終更新は `a9b71406`・2026-07-25** — ECO ごとには書かれていない。`52-metrics.yaml` 176 行、同様。
- ViewTube `bomdd/33-control-plan.yaml`: 受入の特性(`learned_acceptance_characteristics`)42 件が 15 の検査行に付き、うち `known_limits` を持つもの 7 件(ECO-VT-192 の様式。受入のときに「何を測っていないか」を書く欄)。33 テンプレには `known_limits` の欄が無い(grep 0 件)。
- ViewTube の ECO 本文と台帳(60 番台): 実測値・レビューの所見・未検査の注記・由来の 4 種すべてを毎回持つ(例: ECO-VT-232 本文 §7〜§10、台帳の `probe_2026_10_06` / `r8_rounds` / `acceptance`)。
- ViewPrism2 `bomdd/32-mbom.yaml`: `measured` 0 件・`ECO-` の参照 138 件 — 由来の参照はあるが実測値は無い。「記録」は長い ECO 弧を持つ製品で現れる(OBS-20261005-03 の観察と一致)。
- K-BOM(ViewTube `31-kbom.yaml`): 知識(出典つきの判断・`managed_knowledge`・`source`)の層で、実測の記録を入れた例は無い。

### 0.3 候補の評価(DECIDE で示した得失)

- A(採用): 実測値・所見・由来の正本は今でも ECO 本文と台帳が完全に持つ(正本が一つ・§13 の転写値禁止と整合)。未検査の注記は「検査の層が何を見ていないか」であり、検査の責任層(33)に置けば読み手が探さずに済む。
- B: 番号体系(50 番台= 記録)に最も忠実だが、As-Built を ECO ごとに書く新しい義務が生まれる(ViewTube では現状書かれておらず、ECO 本文との二重化になる— 推定・未測定)。
- C: 移行は最も安いが、導出層が設計でも作り方でもない内容を持ち続ける(OBS-20261005-03 が指摘したことそのもの)。
- 「K-BOM へ」: 実例 0 のため候補から外した。

## 1. 変更要求(user 裁定 A・凍結)

1. playbook §4.5 の④を、置き場の決定として書き換える: 記録句の正本= 変更記録(60 番台: ECO 本文と台帳)。M-BOM の行には由来の ECO 番号だけを残す。検査していないことの注記は Control Plan の `known_limits` へ。局所名=「M-BOM の記録句」(ECO-100 IA-01)。根拠の規模(1 製品の実測・ViewPrism2 は由来のみ)と未測定を併記。candidate のまま。
2. 32 テンプレの `invariants` のコメントの「置き場は未決」を、決定の内容に書き換える。
3. 33 テンプレの検査行に `known_limits: []`(candidate・ECO-102)を足す(コメントで用途を書く)。
4. `method/improvements.md` に本節(記帳)と、OBS-20261005-03 の回収の追記(置き場は決まった。2 例目の条件〔別の製品の M-BOM に記録句が混ざる実測〕はそのまま)。

**採らない**: 実証済みへの格上げ(candidate のまま)/ 効果の主張 / 既存の BOM の一括の直し(§4.5 の既存の規則「次にその単位へ触れる変更で直す」のまま)/ 既存製品(ViewTube・ViewPrism2)への書き込み / As-Built・Metrics・K-BOM テンプレの変更 / §4.4・§9・§13 の項の変更 / schemas・ツール・検査器・プロンプトの変更 / OBS-20261005-03 の加算(2 例目の条件に当たる実測は無い)。

## 2. 影響なし予測(製造前・凍結)

diff= playbook(§4.5 の④の文と、その項の実測・未測定の列挙だけ)・templates/32(`invariants` のコメント 1 行)・templates/33(検査行に 1 欄+コメント)+台帳系+reports/eco-102-record-clause-home/ のみ。playbook の他の節・templates の他のファイル・tools・hooks・.github・schemas・contracts・prompts diff 0。
C1(YAML 厳格パース)PASS のまま(33 の新しい欄は空のリスト)・C4(bomdd-init 生成物の parse)PASS のまま・C7 / C13 / C14 / C15 判定不変。配布テンプレは次回配布時に波及・既存製品は不変。

## 3. 受入条件(製造前に凍結・二部形・ECO-080)

- V1(条件): playbook §4.5 の項が次の句をすべて含み、`置き場は**未決**` を含まないこと — 検査法: 各句の grep(1 件ずつ)と実読。
  `変更記録(60 番台: ECO 本文と台帳)` / `ECO 番号の参照だけを残す` / `known_limits` / `M-BOM の記録句` / `ECO-102` / `**未測定**`。項が candidate のままで、§4.4・§9・§13 の項は 1 字も変わっていないこと。
- V2(条件): 32 テンプレの `invariants` のコメントが `置き場は未決` を含まず `変更記録` と `known_limits` を含むこと。33 テンプレの検査行に `known_limits` の欄があり、テンプレ 2 本が厳格 YAML パースを通ること(C1・C4) — 検査法: grep・PyYAML・self-conformance。
- V3(条件): 本文の事実の主張(§0.2 の数値を含む)が、ViewTube・ViewPrism2 の作業木と BomDD の記録(ECO-100 order・improvements.md)の値に一致し、記録に無い主張・記録より強い主張(効果・一般化)を含まないこと — 検査法: 独立検査(異系統)。ViewTube・ViewPrism2 は未 push のため、検査官には測定の対象の写し(各ファイルの該当の計数の根拠= grep の対象行)を sha256 つきで置く。
- V4(条件): 改訂後の項が、playbook の他の節(特に §13 の転写値禁止・記録の経済、§4.4 の Control Plan の項)・ECO-086 / 098 / 100 の他の candidate・31 / 32 / 33 / 50 テンプレの他のコメントと矛盾しないこと — 検査法: `git diff`・実読・独立検査。
- V5(条件): diff が allowed_paths のみ・self-conformance 全 PASS(exit 0 観測後に commit)・CI success であること。
- V6(条件): 異系統の独立検査が ACCEPT であること(境界探索)。
- V7(条件): 較正 receipt(trigger ①)があること。
- V8(条件): OBS-20261005-03 に回収の追記があり、カウンタは 1/3 のままで、worklist の検証警告が 0 であること — 検査法: `python method/tools/worklist.py`・実読。

## /preflight receipt(起動経路: **自発** — 既裁定の適用の開始時)

- 分類= 既裁定の適用(user「A」)。根拠= 裁定が置き場を名指ししており、設計の空白は文言・欄の形・局所名だけ。
- 最小契約(continuation): baseline `aec11da`= **confirmed**(HEAD・clean・CI success〔ECO-101 クローズ時に確認〕)/ current-work-state= ECO-100・101 verified・§4.5 ④未決・OBS-20261005-03 1/3= **confirmed**(playbook L348・improvements.md L8373・register)/
  unresolved-items= §4.5 の未測定の列挙「『記録』の置き場」・ECO-100 IA-01= **confirmed** / handoff-state= ECO-100 order と improvements.md から再構成= **confirmed** / acceptance-target= **missing** → 本 order §3 で定義。
- discovered(契約外): ViewTube・ViewPrism2 の作業木は未 push(ViewTube は origin より 101 先行)→ 検査官が辿れない(ECO-099 r1 の実績)→ 計数の根拠行の写しを sha256 つきで置く(V3)。
- 同一ファイルへの進行中 ECO= なし(register に draft / implemented の ECO なし)。次番 102= **confirmed**。
- 開始判定: **PROCEED**・override なし(0 件)。

## /converge receipt(起動経路: 自発 — 置き場の候補の設計と提示)

- **判定: 収束**(round 軌跡: 1→0→0)。提示は DECIDE 1 回(2026-10-06)。
- DoD(着手前に固定): ✔ 正本が一意(記録の種類ごとに置き場が一つ・M-BOM は参照だけ)/ ✔ 凍結行の実文(§4.5 ④・OBS-20261005-03 の候補の列挙・ECO-100 IA-01)と突合 / ✔ 影響が行単位(§4.5 の 1 項・32 の 1 行・33 の 1 欄)/ ✔ 既存製品へ遡及を求めない / ✔ candidate 止まりで効果を主張しない / ✔ 選択肢を落とさない(候補 4 つ+「残す」)。
- round 1(新規 1 件): 「K-BOM へ」を候補に残すか → ViewTube・ViewPrism2 の K-BOM に実測の記録を入れた例が 0(実測)で、知識の層の定義(出典つきの判断)にも合わない → 候補から外し、提示では理由を添えて外したと書く。
  round 2: 0 件(§0.2 の数値を ViewTube・ViewPrism2 の作業木で取り直し)。round 3: 0 件(敵対自問・失敗型 ①〜⑧ の照合)。
- 検証した主張(実測): §0.2 の各行(`grep -c` / `git log -1 -- 50-as-built.yaml` / テンプレの grep)。「B は二重化になる」は推定(未測定)と明記して提示。
- 敵対自問: 「正本が ECO 本文なら、ECO 本文を持たない小さな製品(§11 テーラリング)ではどうなるか」— 台帳のエントリが記録になる(60 番台には台帳もある)。本文の文は「ECO 本文と台帳」と書く。
  「M-BOM に ECO 番号だけ残すと、後の読み手が『なぜ』を失わないか」— ECO 本文はリポにあり番号で辿れる。§13 の転写値禁止と同じ形(正本は一つ、他は参照)。
  「未検査の注記を 33 に置くと、§4.4 の『検査行と裁定層の結線』の項と衝突しないか」— 衝突しない。`known_limits` は検査行が自分の被覆の限界を言う欄で、結線(どの不変条件を検査するか)は `invariant_refs` のまま。
  「効果の予測」— 「記録句を動かすと M-BOM が読みやすくなる・導出が正確になる」は主張しない。
- 未収束事項: なし。
