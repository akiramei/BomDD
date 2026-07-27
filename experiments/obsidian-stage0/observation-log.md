# Obsidian stage 0 — 観測記録

1 探索セッション = 1 エントリ。様式(全項目必須・「なし」も記入する — 未記入と区別するため):

```markdown
## YYYY-MM-DD-NN
- 目的: <何を知りたくて開いたか>
- 経路: <使ったもの: 検索 / バックリンク / グラフ / ファイルツリー / アウトライン>
- 到達: <目的の情報に Obsidian 内で到達したか。途中で grep / エディタへ脱出したなら、どの時点で何のために>
- 不足: <欲しかったが無かった機能・見えなかった情報(なければ「なし」)— stage 1 の起票根拠になる>
- 逸脱: <Obsidian による正本ファイルの書き換え(git status で確認。なければ「なし」)>
```

記入例(様式説明用・実セッションではない):

```markdown
## 2026-07-27-00(例)
- 目的: OBS-20260726-02 の 3 例の出典 ECO を辿る
- 経路: 検索 → improvements.md → ファイルツリーで bomdd/60-change-order-eco-015.md
- 到達: 部分的 — YAML 台帳(60-change-register.yaml)はプレビューできず外部エディタへ脱出
- 不足: worklist ID から出典節への逆リンク(バックリンクは md 間しか張れない)
- 逸脱: なし
```

---

## 2026-07-27-01(初回オープン — 設置確認・実機)

- 目的: vault として開けるか+開いた直後に Obsidian が何を書き換えるかの確認(README 規則 3 の初回実測)
- 経路: ファイルツリーのみ(探索セッションではない)
- 到達: 該当なし(設置確認)。ツリーにフォルダ+ルート md 4 件を表示。tmp/ output/ plm-out/ は
  エクスプローラには出る(`userIgnoreFilters` が効くのは検索・グラフのみ — 仕様どおり・許容)
- 不足: なし(未探索)
- 逸脱: **正本への書き換え 0 件**。書き換えは `.obsidian/` 内 2 ファイルのみ —
  ①追跡 2 ファイルの末尾改行を除去(Obsidian の書式) ②`core-plugins.json` へ既定キー 4 件を
  マージ(footnotes / slash-command / webviewer = false、**bases = true**)。
  `appearance.json` / `workspace.json` が生成されたが .gitignore どおり未追跡
- 対応(規則 5: 設定変更の diff+理由): **`bases` を false へ変更** — bases は .base ファイルを
  生成する read-model 機能(性格は Dataview と同じ)で、既定 on のままだと測定③
  (read-model への欲求を記録で取る)が濁る。生成系 core plugin off の方針とも整合。
  欲しくなったらその欲求を本ログへ記録する(規則 4 と同じ扱い)。
  末尾改行なしは Obsidian の正規形として受け入れ、追跡ファイルはその書式で固定
  (逆らうと開くたびに diff ノイズが出る)。**設定を反映するには Obsidian の再起動が必要**
