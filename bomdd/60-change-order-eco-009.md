# ECO-009 — bomdd-init の版来歴の正直記録+kit 完全性(独立検査が検出した5件)

## 起票(2026-07-11)

- 出典: **transfer-04(検査の転移)パイロット N=3**。独立受入検査官(Codex gpt-5.5・
  read-only 敵対レビュー)が `bomdd-init.py`(ECO-004)に5件を指摘。当方の実コード検証で
  **5/5 CONFIRMED・全件現 HEAD 4dd025b に残存**(bomdd-init.py は ECO-004 以降未変更)。
- 再現(実測 2026-07-11):
  1. **[med-high] git 不在で正直記録が破綻**: `_method_provenance` 内の `g()` が
     `subprocess.run(["git", ...])` を try 無しで呼ぶため、git 実行ファイル不在で
     `FileNotFoundError`(OSError)が送出され、`install_kit` が **copytree 後に中断**する。
     docstring「git 不在でも止めず not-computed を正直記録(t3 様式)」を**直接反証**。
     上位の `git()` は `except (OSError, CalledProcessError)` で守っているのに、内側 `g()`
     だけ非対称に無防備。
  2. **[med] 不完全 kit の fail-open**: `install_kit` は `if kit.exists(): return` で
     ディレクトリの存在のみを見るため、**manifest / bomdd.lock 欠落の壊れた kit も
     「保持」= 成功扱い**になる。fail-safe(無断上書きしない)を意図した所が fail-open。
     **#1 と連鎖**: #1 の中断で copytree 済み・manifest/lock 未生成の不完全 kit が残り、
     再実行時に #2 がそれを黙認する。
  3. **[low-med] dirty の誤記録**: `bool(g("status", "--porcelain"))` は、rev-parse 成功後に
     `git status` が失敗(returncode≠0 → None)した場合 `bool(None)=False` となり、
     **status 失敗を「clean」と混同**する。commit は not-computed/実値を区別するのに
     dirty は失敗と clean を区別しない — 正直記録の非対称。
  4. **[low-med] lock の adapter.skills 不正確**: bomdd.lock は常に全 `SKILLS` を記録する
     (`skills: [{', '.join(SKILLS)}]`)。`--skills-only --skills <subset>` で部分集合を
     設置した場合、**実際に設置したスキル集合と lock 記録が不一致**になる。`install_kit`
     が `selected` を受け取らないため構造的に記録できない。
  5. **[low] 協働ガイド参照の絶対パス**: 画面案内の working-with-ai.md 参照が
     `{product_root}/bomdd-kit/...`(絶対)のまま。兄弟の checklist/prompts/playbook は
     `{KIT_DIRNAME}/...`(kit 相対)。ECO-004 是正4「案内を kit 相対へ」の逸脱。
     ※ 画面出力のみで生成ファイルへの絶対パス漏れではない(C4 の検査対象外)。

## 裁定

- ユーザー承認(2026-07-11)「進めて」— ECO-008 と同一裁定・是正順序 2 番。
- 是正方針: 起票時の草案どおり(1〜5)。kit 完全性の検査は bomdd-init の
  **PyYAML 非依存を維持**するため lock は regex(`files: N` 行)で読む。

## 影響分析(製造前凍結)

- 影響なし予測: `method/tools/bomdd-init.py` 以外 diff ゼロ。正常系(git あり・完全 kit・
  全スキル設置)の生成物は不変。#4 は lock の adapter.skills の値が部分集合時のみ変わる。

## 是正(2026-07-11)

1. `g()` を `except OSError` で保護(git 実行ファイル不在も None → not-computed 経路)。
   not-computed の文言を `git unavailable or not a git checkout` へ(不在も含む正直記載)。
2. `_kit_integrity_problems()` 新設 — 既存 kit は存在でなく完全性(manifest の存在+パース・
   lock の存在+files 数一致)を検査し、不完全なら問題列挙つき明示エラーで停止
   (無断上書きしない設計は維持 — 復旧手順を案内)。
3. `dirty: bool(st) if st is not None else "unknown"` — status 失敗を clean と区別。
4. `install_kit(root, created, skills)` へ拡張し実設置スキルを記録。3 経路=
   scaffold_product→SKILLS / --skills-only→selected / **scaffold_cad→[]**(CAD にスキルは
   設置しない — 従来は全 8 本を偽記録)。
5. working-with-ai の画面案内を兄弟行と同じ `bomdd-kit/` 相対へ。

## 検証(2026-07-11・検証治具 13 項目全 PASS)

- **V1(正常系回帰)**: scaffold exit 0・lock skills=実設置 8 本・working-with-ai 案内が
  kit 相対(絶対パスなし)。
- **V2(#1 陽性対照)**: PATH から git を除去した環境で scaffold → **exit 0**
  (是正前は FileNotFoundError で copytree 後に中断)・lock `commit: not-computed…`・
  `dirty: "unknown"` を正直記録。
- **V3(#2 陽性対照)**: kit-manifest.json 削除後の --skills-only 再実行 → 「既存の kit が
  不完全」で **exit 1**(是正前は黙認)。lock の files 数改ざん(不一致)も検出し exit 1。
- **V4(#4 副経路)**: `--skills-only --skills bomdd-next,eco-file` → lock skills=
  **実設置 2 本のみ**(是正前は全 8 本を偽記録)。
- **V5(#4 CAD 経路)**: --gui 生成の CAD リポ lock= `skills: []`(正直記録)・製品リポは 8 本。
- self-conformance fast 全 PASS(C4 scaffold 煙試験の回帰含む)。
- **影響なし予測: 部分不的中(1 項目・正直記載)** — 予測「#4 は --skills 部分集合時のみ
  変わる」に対し、実装は **CAD リポの lock も変わる**(全 8 本の偽記録→空の正直記録)。
  起票時に CAD 経路の #4 同族を見落とした — 是正対象そのものと同じ**副経路の見落とし
  (silence §16(d))を影響分析自身が再演**した実例。diff ゼロ範囲の予測(bomdd-init.py 以外)は的中。

## 教訓(還元候補 — lesson-promote 経由・transfer-04 系列)

- 自己検証が張り損なう類型のうち3つを本 ECO が体現: **(a) 約束した挙動の未検枝**
  (docstring は「git 不在でも止めず」と約束するが、その枝は自己検証で一度も踏まれていない)・
  **(b) 存在 vs 完全性**(kit.exists() は存在を見て完全性を見ない)・**(c) 副経路の正確性**
  (--skills 部分集合という主経路でない枝で lock が嘘をつく)。独立×別ベンダー検査が
  高精度に突いた(transfer-04)。
- **影響分析も副経路を見落とす**(本 ECO の製造で追加観測): 「#4 は部分集合時のみ」の凍結予測が
  CAD 経路(同じ嘘の別経路)を落としていた。影響分析の被覆と欠陥の被覆は同じ盲点を共有する —
  影響予測を書くときも silence §16 の 4 観点(特に (d))を当てる(1 例目・rule of three 待ち)。
