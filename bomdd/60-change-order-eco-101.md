# Change Order — ECO-101(ViewTube の復元経路の弧の記帳 — M-BOM の文の誤りが実行で確かめられた・書き戻し前の突き合わせの初の実使用・検査設備の固定の上限が検査一式に追いつかれる 2 例目〔記録のみ・draft〕)

> 裁定: user DECIDE「A」(2026-10-06・ViewTube ECO-VT-228/229 の受け入れ報告への応答)= ①ECO-VT-227 が持ち越した決め D4 を要求へ書く ViewTube の ECO を起票・書き戻し ②BomDD 側に、OBS-20261006-01 が実行で確かめられたことを記帳する。本 ECO は ②。
> 出典: ViewTube ECO-VT-228(applied `737b7252`)・ECO-VT-229(applied `9c9d6ad8`)・ECO-VT-230(staged `4b51151b`)・ECO-VT-231(implemented `562076d9`)。[ECO-100](60-change-order-eco-100.md)が「次に数える機会」と書いた ViewTube ECO-VT-228 の赤くなる検査。
> **本 ECO は記録のみ**。playbook・テンプレ・ツールは変えない(ECO-100 の candidate の訂正は本 ECO の実測より前に閉じている— 実測が candidate を支持するか反証するかを記録し、改訂は別途)。

## 担当設備(equipment)

- 起票・記録: requested/resolved `claude-fable-5-1`・Claude Code(Claude Agent SDK)・来歴 **self-reported**
- producer: EQ-001
- 独立検査: なし(記録のみ・製造者較正)。ViewTube 側の各 ECO は、担当の文脈を持たない読み手(同系統・新しい文脈)のレビューを受けている。

## 0. 根拠(起票・2026-10-06)

ViewTube の commit は origin へ push されていない。根拠の 8 文書を `562076d99281d9bd0807df450c63410191064879` から写して置く: [viewtube-snapshot/](reports/eco-101-viewtube-restore-arc/viewtube-snapshot/)。

```
947ef95423a915ad8205121a7f610013a0be2805625ed297d7ea895af9005ad7 *ECO-VT-228.md
8c45b594fc01d7e498d4c1fb576515d1eca2a4a41cfb01e2b24e62ec022133ca *ECO-VT-228-independent-review.md
e75ca16d711a8a40dff1da2707e0d41a8448960c1c8468e0abd67b3849825fd1 *ECO-VT-229.md
a6726dddbff4fda12baa98c6c1407cba9bb37e2c9587d478089bf6fa56031f5d *ECO-VT-229-independent-review.md
aa43fb11bc22c0537eeb7b71c630328f5db7fd52fe8fe745fee4b20999880e53 *ECO-VT-231.md
e5a56116046f8f43dc768c6a1871a9419d4810529bcc8cdf1f444eac4db742ae *ECO-VT-231-independent-review.md
4ef2e149b14e75cdfb4aa0b1f1b7a70bfd4b99339eecf8ae39d9cadbd289a748 *eco-vt-228-probe-before.txt
8818280949370b1b573090b26c758f58e251fcbd03cdec12894a2d9e58bdc133 *eco-vt-229-probe-before.txt
```

### 0.1 M-BOM の文の誤り(OBS-20261006-01)が、実行で確かめられた

- ECO-100 の時点では、D4(M-BOM「復元したバックアップは open で変換される」)がコードと合わないことは**読み**だけだった(2 人の読み手が一致・実行なし)。
- ViewTube ECO-VT-228 は、最初の仕事として赤くなる検査を作り、写しの中で復元の経路を**実行**した(`eco-vt-228-probe-before.txt`・基準点 `b908a46c`): 復元して起動し直さずに読むと 5 つの条件がすべて「条件なし」(赤)/ 復元→ビューを 1 回保存→起動で、旧い条件の行は 0 行になり条件は戻らない(赤・**条件が失われる**)/ 保存せずに起動すると変換される(緑)/ 起動で開く対照は変換される(緑)。
- 同じ 4 件を受入の検査にし、修理の前は 4 件のうち 2 件が赤。修理(版の移行の後の手当て 4 つを 1 つの並びにし、起動と復元が呼ぶ・user 裁定 B)の後は緑。独立レビューの 5 件目(手当てが何も無いバックアップ)を足して、修理の前 3/5 赤・修理の後 5/5 緑。全体の検査 1076 件・失敗 0。監督つきの実行の通過。applied `737b7252`(user「承認・2 は a・3 は a」)。
- **OBS-20261006-01 の 1 例目は、読みから実行に格上げ**された。2 例目の条件(別の製品または別の単位)には当たらない— 同じ単位・同じ文。カウンタは 1/3 のまま。

### 0.2 playbook §4.5(ECO-100)の「書き戻しの前に別の文脈の読み手が突き合わせとコードの読みを行う」の、初の実使用

- ViewTube ECO-VT-231(D4 の書き戻し・implemented `562076d9`)は、ECO-100 で訂正した手順どおりに進めた: 書き戻す文の句を先に固定した赤くなる検査(2 件赤)→ 書き戻し → 担当の文脈を持たない読み手が、足した 15 句を M-BOM の 2 行と句ごとに突き合わせ(全句 SAME・強くも弱くもない)、修理後のコードを読んで確かめた(復元は自分のトランザクションの中で並びを呼び、コミットしてから成功を返す)。
- レビューの所見は 6 件(すべて軽微): 本文の行番号と引用の不正確・仕様の付記の帰属(ECO-VT-228 は修理であって書き戻しではない)・根拠の欄に除外した作り方の語が入っていた・「条件の意味を保つ」は読めない数値の条件について文字どおりには偽(規則によって捨てられ知らされる)→「規則が与える条件を保つ」・REQ-064 と仕様のバックアップの項に REQ-032 を指す参照が無い。**忠実さ(M-BOM より強い・弱い・無い)の所見は 0**。
- 読み取り: 手順は、文の内容の誤りではなく、**言い回しの過不足と置き場**を拾った。ECO-VT-227(手順の前)では同じ読み手が文の内容の誤り(D4)と担当の言い換えの誤り(D2)を拾った。1 回ずつの比較で、効果の主張はしない。

### 0.3 検査設備の固定の上限が、検査一式の成長に追いつかれる(2 例目)

- ViewTube ECO-VT-215(2026-10-02): 監督つきの実行の全体の上限 180 秒が、検査一式の所要(178.3 秒)に追いつかれ、最後まで走った実行を打ち切った → 「動いていない時間」の見張りに変え、全体は 900 秒の backstop に。管理計画に読み替え「検査の道具の見張り・上限すべて: 道具自身の出力が示す進みの印で決め、壁時計は backstop、打ち切る側も対照で確かめる」。
- ViewTube ECO-VT-229(2026-10-06・`eco-vt-229-probe-before.txt`): その前段、検査の一覧を取る制限時間 15 秒(判定の道具の既定値・監督は渡していない)が、検査 1076 件の一覧の取得(15.4〜16.5 秒・前回 10-05 は 11.9 秒)に追いつかれ、ECO-VT-228 の受入の監督つきの実行が 2 回続けて検査を 1 件も走らせずに止まった(1 回目・user 裁定の exact retest の 2 回目とも)。ViewTube の規律(Stabilization-first: 道具の失敗で作業者は道具を直さず・再試行せず・証拠を残して人に問う)どおりに停止し、user 裁定 A で設備 ECO を起票・修理(監督に引数・既定 120 秒)。独立レビューは「ECO-VT-215 の読み替え(進みの印の形)を採らず壁時計の形だけ・打ち切る側の対照が無い」を major として指摘 → 規則から外れていることを本文に記し、打ち切る側の対照(制限 1 秒で準備が止まる)を足した。
- 同じ製品・同じ設備の系統で、別の上限。2 例とも「道具の中の固定の既定値が、一式の成長に追いつかれる」。

### 0.4 ほかに記録すること

- **道具の既定の書き先が、別の号の証拠を上書きした**(ECO-VT-229 R229a-F1): 監督の自己検査を `--result` なしで走らせ、既定の書き先である ECO-VT-061 の証拠ファイルを上書きした。独立レビューが見つけ、HEAD から戻した。BomDD では ECO-078 で playbook §3 に昇格済み(Codex `-o` の上書き機序・「座標の書き手を 1 つにする」)の同型 — 昇格済みのため加算しない。実例として記す。
- **利用者のアプリが起動中だと検査 12 件が赤になる**(環境・修理の有無と無関係・同じ 12 件): 書き込みを断る作りのため。再現して分離し、user にアプリを閉じてもらった。観測として記す(BomDD 側の規則の対象ではない)。
- **範囲の外の発見 2 件**(ViewTube 側で起票・利用者へ): デモ用のツールが初期化を通さずにカタログを開く(ECO-VT-230・staged)/ REQ-064 の「失敗時は byte-for-byte 不変」が置換後の失敗に成り立たない(ECO-VT-231 R231a-F10・未起票)。

## 1. 変更要求(記録のみ・凍結)

1. `method/improvements.md` に本節: OBS-20261006-01 の 1 例目を読みから実行へ格上げ(カウンタ不変)/ playbook §4.5(ECO-100)の初の実使用の記録 / 新規 OBS-20261006-02(検査設備の固定の上限が一式の成長に追いつかれる・2 例)/ §0.4 の実例と観測。
2. `bomdd/reports/eco-101-viewtube-restore-arc/viewtube-snapshot/` に根拠の写し(sha256 つき)。
3. `bomdd/60-change-register.yaml` に本 ECO を登録。

**採らない**: playbook・テンプレ・ツールの改訂(§4.5 の candidate は訂正したばかり・本 ECO の実測はそれを反証していない)/ 効果の主張 / ViewTube への書き込み / OBS-20261006-01 の加算(同じ単位)/ ECO-VT-230・R231a-F10 の BomDD 側での扱い。

## 2. 影響なし予測(起票時点・凍結)

本リポの diff= 台帳系(order・register・improvements.md・reports/eco-101-viewtube-restore-arc/)のみ。playbook・templates・schemas・tools・hooks・.github diff 0。ViewTube は読むだけ(`git show`)。

## 3. 受入条件(製造前に凍結・二部形・ECO-080)

- V1(条件): 写しの sha256 が ViewTube の `562076d9` の `git show` の出力と一致すること — 検査法: 本 order §0 の値と `sha256sum`。
- V2(条件): improvements.md の記帳の数値(赤/緑の件数・1076/0・15.4〜16.5 秒・レビュー所見の件数)が写しの値と一致すること — 検査法: 製造者の突合(写しを開いて 1 件ずつ)。
- V3(条件): OBS-20261006-01 のカウンタが 1/3 のままで、「実行で確認」が本文に書かれていること。新規 OBS-20261006-02 が `source:`/`evidence:` 行を持つこと — 検査法: grep・worklist.py の警告 0。
- V4(条件): diff が allowed_paths のみ・self-conformance 全 PASS(exit 0 観測後に commit)・CI success。較正 receipt(trigger ①)。

## /preflight receipt(起動経路: **自発** — 既裁定の適用の開始時)

- 分類= 既裁定の適用(user「A」の ②)。baseline `6edfb16`= **confirmed**(HEAD・clean・CI success)/ current-work-state= ECO-100 verified・ViewTube ECO-VT-228/229 applied・230 staged・231 implemented= **confirmed**(ViewTube `git log`)/
  unresolved-items= ECO-100 の「次に数える機会」= **confirmed**(improvements.md 2026-10-06 節)/ handoff-state= ECO-100 order と ViewTube の各 ECO 本文から再構成= **confirmed** / acceptance-target= **missing** → §3 で定義。次番 101= **confirmed**。
- discovered(契約外): ViewTube は未 push → 写しを sha256 つきで置く(ECO-100 と同じ)。
- 開始判定: **PROCEED**・override なし(0 件)。

## 4. 記録(2026-10-06)

- 写し 8 文書を §0 の sha256 で置いた。improvements.md に本節と OBS-20261006-02 を記帳した(起票と同じ commit)。
