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

- ViewTube `bomdd/32-mbom.yaml`: 不変条件の項目 128(1 項目= `invariants:` の 1 要素。PyYAML で読み、写し `viewtube-32-mbom-invariant-entries.txt`・計数は `count_records.py`・語彙は英日: measured/実測/測った/測定、review/round/所見 ID/レビュー/所見、not exercised 等/測っていない/未検査/未測定、ruling/裁定/利用者の判断)。**87 件が ECO 番号で始まる**(由来の記録)。実測値の語を含む項目 17。レビューの所見の語を含む項目 54。未検査の注記の語を含む項目 5。裁定の語を含む項目 14。
  (r2 の訂正: 起票時はファイルの物理行で数えて 21 / 95 / 6 / 15 と書いた。独立検査 r1〔IA-02〕が、先頭行だけの写しからは再計数できないと指摘し、項目の数に改めた。DECIDE で示した「21 行が実測値・6 行が未検査の注記」も物理行の数である。
  r3 の訂正: r2 の「60 件・全件が ECO 番号で始まる」は、引用符つきで ECO 番号から始まる項目だけを正規表現で拾った数だった。`invariants:` には引用符の無い項目(設計時からの不変条件)もあり、PyYAML で読むと 128 件・ECO 番号で始まるのは 87 件。語彙も英語だけだったので、英日の語彙で数え直した。)
- ViewTube `bomdd/50-as-built.yaml`: 244 行・エントリ 8 件(工場ごとの派生製造・現場是正・CAPA)。**最終更新は `a9b71406`・2026-07-25** — ECO ごとには書かれていない。`52-metrics.yaml` 176 行、同様。
- ViewTube `bomdd/33-control-plan.yaml`: 受入の特性(`learned_acceptance_characteristics`)42 件が 15 の検査行に付き、うち `known_limits` を持つもの 7 件(ECO-VT-192 の様式。受入のときに「何を測っていないか」を書く欄)。33 テンプレには `known_limits` の欄が無い(grep 0 件)。
- ViewTube の ECO 本文と台帳(60 番台): M-BOM の記録句の由来(ECO 番号で始まる 87 項目の先頭の番号)は 26 号で、**26 号すべてに本文と台帳の項がある**(`viewtube-eco-ids-of-the-entries.txt`)。26 本の本文のうち、実測値の語を含むもの 26・レビューの所見の語 26・未検査の注記の語 13・裁定の語 20(`count_records.py`)。例として ECO-VT-232 の本文と台帳の項を写した(`viewtube-eco-vt-232-body.md`・`viewtube-register-eco-vt-232.yaml`: 本文 §7〜§10 と台帳の `probe_2026_10_06` / `r8_rounds` / `acceptance` が 4 種を持つ)。
  (r3 の訂正: 起票時は「4 種すべてを毎回持つ」と書いた— 独立検査 r2〔IA-05〕のとおり記録が無かった。上は計数と写しに置き換えた文である。)
- ViewPrism2 `bomdd/32-mbom.yaml`: 不変条件の項目 63(写し `viewprism2-32-mbom-invariant-entries.txt`・同じ語彙)。ECO 番号で始まる項目 0・ECO 番号を含む項目 15。実測値の語 0・レビューの所見の語 0・未検査の注記の語 0・裁定の語 1。「記録」は長い ECO 弧を持つ製品で現れる(OBS-20261005-03 の観察と一致)。
  (r3 の訂正: r2 までの「`measured` 0 件・`ECO-` の参照 138 件〔物理行〕— 由来の参照だけ」は、独立検査 r2〔IA-06〕のとおり 2 語の grep では「だけ」を支えない。項目の単位と同じ語彙で数え直した。)
- K-BOM(ViewTube `31-kbom.yaml`): 知識(出典つきの判断・`managed_knowledge`・`source`)の層。`measured` の語を持つ行は 2(K の名「ViewPrism2 measured responsive grid …」と知識の文「Responsive decisions use measured toolbar content width …」。写し `viewtube-31-kbom-measured-lines.txt`)で、日付・値・版を持つ実測の記録ではない(r2 で写しを足した。独立検査 r1〔IA-03〕)。

### 0.3 候補の評価(DECIDE で示した得失)

- A(採用): 記録句の由来 26 号はすべて ECO 本文と台帳の項を持ち、本文 26 本すべてが実測値と所見の語を含む(§0.2)— 正本をそこに置いても新しい記録の義務は生まれない(正本が一つ・§13 の転写値禁止と整合)。個々の記録が本文と台帳の両方に漏れなく載っているかは測っていない。未検査の注記は「検査の層が何を見ていないか」であり、検査の責任層(33)に置けば読み手が探さずに済む。
  (r4 の訂正: 「実測値・所見・由来の正本は今でも ECO 本文と台帳が完全に持つ」は独立検査 r3〔IA-05〕のとおり記録より強い。計数の文に置き換えた。)
- B: 番号体系(50 番台= 記録)に最も忠実だが、As-Built を ECO ごとに書く新しい義務が生まれる(ViewTube では現状書かれておらず、ECO 本文との二重化になる— 推定・未測定)。
- C: 移行は最も安いが、導出層が設計でも作り方でもない内容を持ち続ける(OBS-20261005-03 が指摘したことそのもの)。
- 「K-BOM へ」: 実例 0 のため候補から外した。

## 1. 変更要求(user 裁定 A・凍結)

1. playbook §4.5 の④を、置き場の決定として書き換える: 記録句の正本= 変更記録(60 番台: ECO 本文と台帳)。M-BOM の行には由来の ECO 番号だけを残す。検査していないことの注記は Control Plan の `known_limits` へ。局所名=「M-BOM の記録句」(ECO-100 IA-01)。根拠の規模(1 製品の実測・ViewPrism2 は実測値・所見・未検査の語 0・ECO 参照 15・裁定の語 1)と未測定を併記。candidate のまま。(r4 の訂正: 凍結した文の「ViewPrism2 は由来のみ」は独立検査 r3〔IA-06〕のとおり裁定の語 1 件と矛盾する排他の表現で、計数に限定した。要求の内容は変えていない。)
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

## 4. 製造(2026-10-07・製造者 EQ-001)

- 起票 commit `37c4f82` の後に製造した(文案は起票の前に台本〔mfg102.py〕として作り、起票 commit の作業木には入れず、起票の後に適用)。
- 製造物(3 ファイル・追加 10 行・削除 3 行): playbook §4.5 の candidate の項の 2 か所(④の文〔1 行を 4 行に: 局所名・正本・参照・known_limits・根拠・選ばれなかった道〕/ 未測定の列挙の 1 句〔「記録」の置き場 → 記録句をこの置き場で書いた製品 0〕)。
  templates/32 の `invariants` のコメント(1 行を 2 行に)。templates/33 の検査行に `known_limits: []` とコメント(3 行)。§4.4・§9・§13 の項・他のテンプレは変えていない。
- 測定の記録(§0.2 の根拠): `reports/eco-102-record-clause-home/measurements.txt`(measure102.sh r3 の出力・測定したファイルの sha256・ViewTube / ViewPrism2 の HEAD・写しの sha256)と、`count_records.py`(PyYAML・両製品・英日の語彙)、写し 7 本(`viewtube-32-mbom-invariant-entries.txt`・`viewprism2-32-mbom-invariant-entries.txt`・`viewtube-eco-ids-of-the-entries.txt`・`viewtube-eco-vt-232-body.md`・`viewtube-register-eco-vt-232.yaml`・`viewtube-33-known-limits-lines.txt`・`viewtube-31-kbom-measured-lines.txt`)。
  (r4 の訂正: この行は r1 の写し 2 本〔`viewtube-32-mbom-invariant-lines.txt` 60 行・現存せず〕のままだった— 独立検査 r3〔IA-07〕。r1 → r2 → r3 の変遷は §6 にある。)
  測定で起票の文の数値を 2 か所訂正した(起票 commit の前): As-Built のエントリは 5 件でなく 8 件 / Control Plan の「15 件のうち 7 件」は、受入の特性 42 件(15 の検査行に付く)のうち 7 件。DECIDE で示した「15 件のうち 7 件」は後者の誤りで、order・register・improvements・playbook の文は訂正後の値である。

## 5. 受入の実測(2026-10-07・製造者)

- **V1**= PASS(観測: playbook への grep、1 句ずつ — `変更記録(60 番台: ECO 本文と台帳)` 1 件・`ECO 番号の参照だけを残す` 1 件・`known_limits` 3 件〔④の文・根拠・未測定〕・`M-BOM の記録句` 1 件・`ECO-102` 1 件・`**未測定**` 1 件・`置き場は**未決**` 0 件。
  `git diff -U0` の playbook の hunk は 2 つ〔L348 → L348〜351・L356 → L359〕で、どちらも §4.5 の項の中。項は candidate の表示のまま)。
- **V2**= PASS(観測: 32 テンプレに `置き場は未決` 0 件・`変更記録` / `known_limits` 2 件。33 テンプレの L47 に `known_limits: []`(検査行 `CP-<NAME>-001` の `test_vectors` の次)。PyYAML の `safe_load` で 2 本とも読めた。`git diff` の追加・削除行のうち、コメントでも `known_limits: []` の欄でもない行は 0)。
- **V4** のうち機械で測れる部分= PASS(観測: 上の hunk の位置。§4.4 の candidate の項〔L170〕・§9〔L825 → 製造後 L828〕・§13〔L911 → L914〕に差分なし)。
- **V8**= PASS(観測: improvements.md の OBS-20261005-03 の本文末尾に回収の追記〔`置き場は ECO-102 で決定`〕・カウンタ `[watch 1/3]` 不変・`python method/tools/worklist.py` の validation_warnings 0)。
- **V3**・**V4** の実読・**V6**= 独立検査(§6)。**V5**・**V7**= クローズ節。

## 6. 独立検査(異系統・EQ-002 Codex gpt-5.6-sol)

### 6.1 r1(2026-10-07・境界探索・対象 78f96509)— **REJECT**(blocking 3・証拠の連鎖)

- 報告= [independent-inspection-r1.md](reports/eco-102-record-clause-home/independent-inspection-r1.md)。項目 1(範囲)・2(V1 の句)・4(既存の本文との整合)・5(テンプレの健全性)・6(言い回し)= PASS。項目 3(記録との一致)= FAIL。IA-04(non-blocking): 製造物は order §4 のとおりで、所見は設計の内容でなく受入用の証拠の欠落に帰属する。
- **IA-01(blocking)**: order は写しを「sha256 つき」と書いたが、measurements.txt に写し 2 本の sha256 が無い(元ファイルの sha256 だけ)。
- **IA-02(blocking)**: 写しは不変条件の先頭行だけ(`grep "^    - '"`)で、計数(21 / 95 / 6 / 15)は物理行の全部に対するもの— 写しからは再計数できない(検査官の再計数: 0 / 26 / 0 / 14)。
- **IA-03(blocking)**: 「K-BOM に実測の記録を入れた例は無い」は、`measured` 2 件の存在までしか記録になく、その 2 件を実測の記録でないと分類する根拠行の写しが無い。
- **処置(r2・本 commit)**: 測定の台本を改め(`measure102.sh` r2・`count_entries.py`)、不変条件を**項目**(複数行の 1 要素)の単位で数え、全項目の全行の写し(`viewtube-32-mbom-invariant-entries.txt`・422 行)と K-BOM の該当 2 行の写しを置き、写し 3 本の sha256 を measurements.txt に記録した。
  数値を項目の数に訂正した(60 / 60 / 11 / 36 / 2 / 14): order §0.2・register の source・improvements.md の節・playbook §4.5 ④の根拠。K-BOM の主張は「`measured` の語を持つ 2 行は知識の文で、実測の記録ではない」に限定した。起票 commit のメッセージの数値(21・6)は訂正できないので、ここに記す。
  r2 の検査は本 commit を対象に、同じブリーフ(対象の版と IA-01〜03 の処置の確認を加える)で行う。

### 6.2 r2(2026-10-07・境界探索・対象 9212e719)— **REJECT**(blocking 2・証拠の連鎖)

- 報告= [independent-inspection-r2.md](reports/eco-102-record-clause-home/independent-inspection-r2.md)。写し 3 本の sha256 一致。IA-01・02・03 は **CLOSED**。項目 1・2・4・5・6 PASS、項目 3 FAIL。
- **IA-05(blocking)**: 「ECO 本文と台帳が実測値・レビューの所見の正本を既に持つ」「4 種すべてを毎回持つ」は置き場の決定を直接支える事実なのに、measurements.txt と写しに照合できる根拠行が無い。
- **IA-06(blocking)**: 「ViewPrism2 は由来の参照だけ」は排他の主張で、`measured` 0 と `ECO-` 138 の 2 語の grep では立証できない。
- **処置(r3・本 commit)**: 測定の台本を r3 に(`count_records.py`: 両製品の M-BOM を PyYAML で読み、`invariants` の全要素を英日の語彙で数え、全要素の写しを置く。ViewTube の記録句の由来 26 号の本文と台帳の有無と語彙を数え、ECO-VT-232 の本文と台帳の項を写す。写し 7 本の sha256 を記録)。
  r3 で分かった r2 の誤り: r2 の「60 件・全件が ECO 番号で始まる」は引用符つきの項目だけの数で、`invariants` は 128 要素(ECO 番号で始まるのは 87)。数値を order §0.2・register・improvements・playbook §4.5 ④で訂正し、
  ECO 本文の主張を計数(26 号すべてに本文と台帳・本文 26 本中 実測値 26・所見 26・未検査の注記 13・裁定 20)に、ViewPrism2 の主張を計数(63 件中 ECO 番号を含む 15・裁定 1・実測値/所見/未検査 0)に置き換えた。製造物の形は不変。r3 の検査は本 commit を対象に行う。

### 6.3 r3(2026-10-07・境界探索・対象 b5592120)— **REJECT**(blocking 3・order の文だけ)

- 報告= [independent-inspection-r3.md](reports/eco-102-record-clause-home/independent-inspection-r3.md)。写し 7 本の sha256 一致・全要素の写しからの再計数が両製品とも一致(128/87/87/17/54/5/14・63/0/15/0/0/0/1)・26 号の本文と台帳の有無が一致。IA-01〜04 CLOSED。項目 1・2・4・5・6 PASS、項目 3 FAIL。
- **IA-05(open・blocking)**: order §0.3 の「実測値・所見・由来の正本は今でも ECO 本文と台帳が完全に持つ」は、記録(本文 26 本が語を含む・台帳の項がある)より強い。
- **IA-06(open・blocking)**: order §1 の「ViewPrism2 は由来のみ」は、裁定の語 1 件と矛盾する排他の表現。
- **IA-07(blocking)**: order §4 の測定の記録の行が r1 の写し 2 本(現存せず)のままで、r3 の 7 本と食い違う。
- **処置(r4・本 commit)**: order の 3 文を計数の文に置き換え、または現状に合わせた(§0.3 の A・§1 の 1・§4 の測定の記録の行)。凍結した §1 の文は訂正の注記つきで直し、要求の内容は変えていない。playbook・テンプレ・register・improvements は r3 のまま(r3 で既に計数の文)。r4 の検査は本 commit を対象に行う。

### 6.4 r4(2026-10-07・境界探索・対象 ee5eec62)— **ACCEPT**

- 報告= [independent-inspection-r4.md](reports/eco-102-record-clause-home/independent-inspection-r4.md)。項目 1(範囲)・2(V1 の句)・3(記録との一致)・4(既存の本文との整合)・5(テンプレの健全性)・6(言い回し)= すべて PASS。写し 7 本の sha256 一致・両製品の再計数一致・26 号の本文と台帳の存在と語彙の計数が一致。blocking 所見なし。
- 所見: IA-01〜IA-07 すべて CLOSED(IA-05: §0.3 を計数と未測定の明記に縮小 / IA-06: §1 の排他を計数に置換 / IA-07: §4 が現存する写し 7 本を列挙)。新しい所見なし。

## 7. クローズ(2026-10-07・verified・異系統の独立検査 r4 ACCEPT)

- **V1**= PASS(観測: §5 の grep〔各句 1 件以上・「未決」0 件〕。検査官 r1〜r4 項目 2 も各 round で同じ件数・見出しに candidate)。
- **V2**= PASS(観測: §5 のとおり。検査官 r1〜r4 項目 5 — PyYAML `safe_load` 成功・変更行はコメントと `known_limits: []` の欄だけ)。
- **V3**= PASS(観測: 検査官 r4 項目 3 — order・playbook・improvements の事実の主張が r3 の記録〔measurements.txt・写し 7 本・count_records.py〕と一致し、記録より強い主張が無い。r1〜r3 は FAIL で、写しの sha256・写しの被覆・物理行と項目の取り違え・引用符つき項目だけの計数・ECO 本文の主張の根拠・排他の表現・古い記述の 7 件を直した〔§6.1〜§6.3〕)。
- **V4**= PASS(観測: 検査官 r1〜r4 項目 1・4 — hunk は §4.5 の項の中だけ・§4.4・§9・§13 と他のテンプレは差分 0・§13 の転写値禁止と同じ形・§4.4 の結線〔`invariant_refs`〕と役割が異なる・50 テンプレの `test_evidence_refs` と重ならない)。
- **V5**= PASS(観測: 窓 `aec11da` → `ee5eec6`= allowed_paths のみ〔検査官 r4 項目 1〕。起票 `37c4f82`・製造 `78f9650`・r2 `9212e71`・r3 `b559212`・r4 `ee5eec6` とも self-conformance exit 0 を観測してから commit。CI は 4 run とも success〔37487052377・37488769191・r3・r4〕。本クローズ commit は台帳系+r4 報告のみ)。
- **V6**= PASS(観測: r4 **ACCEPT**。r1〜r3 は REJECT で、所見はすべて受入用の証拠の連鎖と order の文に帰属し、製造物〔置き場の決定・テンプレの欄〕への blocking は 0〔r1 IA-04・r2・r3 の項目 4〜6〕)。
- **V7**= 下の較正 receipt。
- **V8**= PASS(観測: OBS-20261005-03 の本文末尾に回収の追記・`[watch 1/3]` 不変・worklist 警告 0)。register: `implemented → verified`。

### 較正 receipt(/calibrate 自己適用 — trigger ①: verified 昇格・receipt_author_role= producer。文書とテンプレのみの変更・異系統の独立検査 4 round)

- 査定した主張と判定:
  1. 「§4.5 ④の決定と 32 / 33 テンプレの変更は、裁定 A のとおりで、記録より強い主張を含まない」— **observed / 適格**(検査官 r4 項目 3・6。r1〜r3 の所見で記録と文を揃えた)。
  2. 「置き場の根拠の数値は両製品の M-BOM と ECO 本文の実測である」— **observed / 適格**(count_records.py・写し 7 本・検査官 r3/r4 の再計数が一致)。ただし計数は語彙の有無で、記録句の意味の分類ではない(ECO-099 の句ごとの分類とは別の計器)。
  3. 「As-Built は ECO ごとに書かれていない」— **observed / 適格**(git log の最終更新・エントリ 8 件)。
  4. 「K-BOM の `measured` 2 行は実測の記録ではない」— **observed / 適格**(写しと検査官 r2〜r4 の読み)。
  5. 「変更記録を正本にしても新しい記録の義務は生まれない」— **条件付き**(26 号の本文と台帳の存在と語の有無まで。個々の記録が両方に漏れなく載っているかは未測定)。
  6. 「この置き場で、次の製品の M-BOM から記録句が消え、導出が正確になる」— **unknown(本文も主張しない)**。この置き場で書いた製品は 0。
  7. 「B は二重化になる」— **unknown**(推定・未測定と明記)。
- 検出した計器欠陥(帰属つき): 製造物 0 件。製造者の記録 7 件(r1〜r3)= 写しの sha256 を記録しなかった / 写しが先頭行だけ / 物理行の数を項目の数のように書いた / 引用符つき項目だけを正規表現で数えた / ECO 本文の主張に根拠を置かなかった / 排他の表現 2 件 / §4 の記述の更新漏れ。
  いずれも「測定を記録に残す前に数字を書いた」同じ型で、検査官(異系統)が各 round で 1 段ずつ掘った。製造者の自己査定は 3 回とも見落とした(playbook §9 の昇格済み原則の実例・加算しない)。
- 検出力の限界: 文書とテンプレのみ。検査官は 1 系統・読解中心(実行は PyYAML の読み込みだけ)。根拠の ViewTube / ViewPrism2 側は写し(未 push)。計数は語彙の有無で、句の意味の分類ではない。1 製品の実測(ViewPrism2 は語 0)。
- battery 行別記録:

  | Q | asked/NA | 判定 | 実測 or 読解 | 所見 |
  |---|---|---|---|---|
  | Q1 | asked | observed/適格 | 読解 | 受入条件は句の存在・記録との一致・矛盾なし・健全性・回収の追記までで、効果を条件にしていない。主張 5〜7 を分離 |
  | Q2 | asked | observed/適格 | 実測 | 本 ECO の陰性の実演= r1〜r3 の REJECT(blocking 8 件・すべて製造者の記録の欠陥)を検査官が検出した |
  | Q3 | asked | observed/適格 | 実測 | 製造者の grep・PyYAML・self-conformance と、検査官の再計数(全要素の写しから)を別々に行った |
  | Q4 | asked | observed/適格 | 実測 | 実ファイル・実 commit(5 つ)・CI 4 run。製品側は写しと sha256(主張 2) |
  | Q5 | asked | observed/適格 | 実測 | 語彙の計数と意味の分類の違い・未測定の製品・推定の B を限界として分離 |
  | Q6 | asked | observed/適格 | 実測 | 各 commit は単独で実行して exit を観測し、その後に witness → push → CI → 検査の起動(ブリーフの SHA は commit の後に埋めた)。r1 の起動は作業ツリーの不一致で道具が止め、ブリーフをリポの外に置いて再起動した |
  | Q7 | asked | NA 相当 | — | 陽性対照は置いていない(Q2 の陰性の実演を参照) |
  | Q8 | NA | — | — | 免除機構なし |
  | Q9 | asked | observed/適格 | 実測 | 検査の対象 revision の完全 SHA をブリーフに埋め、検査官が開始時・終了時の HEAD と照合(4 round とも一致)。写し 7 本の sha256 も検査官が計算 |
  | Q10 | asked | 宣言 | 読解 | 上記「検出力の限界」+主張 5〜7 |
  | Q11 | asked | observed/適格 | 読解 | 入力クラス(playbook の項 / テンプレ 2 本 / order の事実 / improvements の記帳 / 既存節との照合 / 言い回し)を分けて検査させた |

- このクローズが支持しないもの: 置き場の決定の効果(M-BOM が読みやすくなる・導出が正確になる)/ 他の製品への一般化 / B の二重化の実在 / 既存の M-BOM の記録句を実際に動かすこと(次にその単位へ触れる変更で)/ candidate の実証済みへの格上げ。
