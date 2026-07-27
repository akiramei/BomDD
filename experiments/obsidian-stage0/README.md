# Obsidian workbench — stage 0(観測のみ・正本不変)

裁定(2026-07-27・improvements.md「外部提案裁定 — Obsidian workbench」節): Obsidian は
**閲覧・探索・起案の面**であり、正本(Git)と統制エンジン(lifecycle validator・hook・
self-conformance・CI)は既存のまま。stage 0 では**何も作らず**、既存リポをそのまま vault として
開き、「実際にどんな探索をしたか・何が足りなかったか」を実測する。stage 1(派生 vault 生成 /
正本形式の変更)の起票要否は、この実測を根拠に**保存形式レビュー三層化提案と合同で**裁定する。

## stage 0 の運用規則

1. **Obsidian から正本を変更しない** — 編集・rename・移動・削除は禁止。使ってよいのは閲覧・
   検索・バックリンク・グラフ・アウトラインのみ。
2. **起案・メモは本フォルダ(`experiments/obsidian-stage0/`)配下のみ**に書く。正本への反映は
   従来どおり ECO / 還元手順を通す。
3. **Obsidian が正本ファイルを書き換えた事象**(自動整形・frontmatter 正規化・リンク書き換え)は
   **逸脱**として observation-log へ記録する(`git status` が検出器)。
4. **community plugin は入れない**。欲しくなったら、その欲求自体を observation-log へ記録する —
   それが stage 1 の起票根拠になる(Dataview / SQLite / MCP も同じ扱い: 必要の実測が先)。
5. vault 設定の変更は `.obsidian/app.json` の diff としてコミットし、理由を observation-log に残す。

## 保守的設定の内訳(`.obsidian/app.json`)

| 設定 | 値 | 理由 |
|---|---|---|
| `alwaysUpdateLinks` | false | rename 時の全 vault リンク書き換え(最大の正本汚染経路)を遮断 |
| `useMarkdownLinks` / `newLinkFormat` | true / relative | 新規リンクを GitHub 互換の相対 markdown にする(wikilink を正本形式にしない) |
| `propertiesInDocument` | source | Properties UI の YAML 正規化(並び替え・引用符変更)を避け frontmatter を生表示 |
| `defaultViewMode` / `livePreview` | preview / false | 既定を閲覧モードにし、編集時も生 markdown(閲覧が主用途であることの物理化) |
| `strictLineBreaks` | true | GitHub と同じ改行解釈で表示(表示差を「直したくなる」誘因を消す) |
| `attachmentFolderPath` | 本フォルダ配下 | 貼り付け画像が正本ツリーへ散らばらない |
| `showUnsupportedFiles` | true | .yaml / .py もエクスプローラに見せる(台帳の存在を隠さない) |
| `userIgnoreFilters` | tmp/ output/ plm-out/ | 生成物を検索・グラフのノイズにしない |
| core plugins | daily-notes / templates / note-composer / canvas 等 off | ファイルを新規作成・改変する系を落とす(検索・バックリンク・グラフ系のみ有効) |

`.obsidian/` は `app.json` と `core-plugins.json` のみ追跡(実行時状態は .gitignore)。

## 測定(EXP-20260727-15)

1 探索セッション = 1 エントリを [observation-log.md](observation-log.md) に記録する。

**stage 1 判定点**: 実セッション 5 回、または実プロジェクト立ち上げ(EXP-20260725-03)の完了の
早い方。蓄積エントリを根拠に、①stage 1 起票の要否 ②起票するなら派生 vault 生成か正本形式変更か
(三層化裁定と合同)③grep で足りなかったクエリの有無(SQLite/MCP の要否)を裁定する。
