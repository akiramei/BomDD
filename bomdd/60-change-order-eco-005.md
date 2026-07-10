# ECO-005 — ui-cad-gate の理由なし rejected 黙殺(GU4 の来歴穴)

## 起票(2026-07-10)

- 出典: メンバー外部レビュー所見5(P2)。「`ruled` と `superseded` しか内容検査せず、
  GU2 では任意の active ruling が action を被覆する。したがって `status: rejected`、
  根拠・否定裁定なしでも action を落として合格できる。`rejected` には理由・evidence・
  決定者を必須にすべき」。
- 再現(是正前・実測): 最小 fixture(action 1 件+理由なし rejected 裁定 1 件)で
  **全ゲート PASS・「昇格可」・exit 0** — 黙殺が通ることをコードパスで確認。
- 位置づけ: 37-ui-rulings テンプレの規律 3「裁定には否定側(negative_rulings)と
  根拠(evidence)を残す」は散文規律のままで、機械検査(GU4)が
  ruled/superseded にしか及んでいなかった — **手順の成熟度ラダー②→④の未昇格**(playbook §13)。

## 裁定

- ユーザー承認(2026-07-10)「進めてOK」。
- 是正方針: レビュー提案どおり rejected の内容必須化。却下根拠= `evidence` **または**
  `negative_rulings`(却下は「負の裁定」であり、否定側の言明が根拠になる場合がある)+
  `decided_by` 必須。**rejected が GU2 の被覆に入ること自体は正しい**(根拠つきの
  却下は action を落とす正規の経路)— 塞ぐのは「来歴なし」の方。
- スコープ外(観測のみ): ruled への decided_by 必須化は既存台帳への遡及影響があるため
  見送り(rule of three 待ち — 今回の穴は rejected 固有)。

## 影響分析(製造前凍結)

- 影響なし予測: `ui-cad-gate.py` 以外は diff ゼロ。既存の正規台帳は判定不変
  (反証可能: MoviePad retro-01 実台帳で前後比較)。

## 是正

- GU4 の台帳形式検査に追加: `status == "rejected"` のとき
  (a) `evidence` も `negative_rulings` も空 → FAIL「却下根拠が空(理由なき黙殺の禁止)」
  (b) `decided_by` 空 → FAIL「誰が却下したか」。

## 検証(2026-07-10)

- **陽性対照**: 理由なし rejected(fixture)→ **GU4 FAIL 2 件・昇格禁止・exit 1**(是正前 exit 0)。
- **陰性対照**: 同 fixture に negative_rulings+evidence+decided_by を与える → 全ゲート PASS。
- **回帰**: MoviePad retro-01 実台帳(ruled 15+superseded 4・rejected 0)で全ゲート PASS — 判定不変。
- 影響なし予測: 的中。

## 教訓(還元候補 — lesson-promote 経由)

- ゲートの被覆規則(GU2「active が被覆する」)と内容規則(GU4「status ごとの必須項目」)が
  別々に育つと、**新しい status が被覆側にだけ算入されて内容側で漏れる** — status を追加・
  流用するときは「被覆に入るなら来歴必須」の対で検査を書く(1 例目)。
- fixture ペア(黙殺が通る/根拠つきが通る)= mutation matrix の最小形として self-conformance
  (ECO-006)へ収載する。
