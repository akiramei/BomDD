# OSS 選定記録

選定日: 2026-07-19

## 候補比較

| 候補 | RDB | 規模の目安 | UI/業務の検証幅 | ライセンス | 初回実証への判断 |
|---|---|---:|---|---|---|
| `traggo/server` | SQLite、MySQL、PostgreSQL | 約 272 tracked files、GitHub 表示約 1.4 MB | 時間記録、タグ、一覧、カレンダー、dashboard、利用者 | GPL-3.0 | 採用。全機能を追える境界の明瞭さを優先 |
| `go-shiori/shiori` | SQLite、PostgreSQL、MariaDB/MySQL | GitHub 表示約 49 MB | bookmark、検索、archive、import/export、CLI | MIT | 次点。外部 Web archive が初回の変数を増やす |
| `sissbruecker/linkding` | SQLite 系の Django 配置 | GitHub 表示約 6.7 MB | bookmark、tag、共有、REST API、archive | 選定時未確定 | テストは充実するが Python/Node の再現負荷が高い |
| `grocy/grocy` | SQLite | GitHub 表示約 24 MB | stock、shopping、meal、chores | MIT | 大きく、既存 desktop wrapper が比較を偏らせる |

## 採用理由

`traggo/server` は小さな CRUD サンプルではなく、時間・集計・カレンダー・複数テーブル・認証を含む。一方、対象 commit の tracked file は 272 で、手引きの問題と製品固有の複雑さを分離しやすい。SQLite の単一ファイルを基準 fixture として固定でき、既存 RDB 流用の成否を hash、schema、canonical query で検査できる。

GPL-3.0 は配布条件を増やすが、ライセンス遵守も移行成果物の外部依存・配布検査として扱えるため、除外理由とはしなかった。

## 一次情報

- https://github.com/traggo/server
- https://github.com/traggo/server/blob/master/README.md
- https://github.com/traggo/server/blob/master/LICENSE
- https://traggo.net/install/
- https://github.com/go-shiori/shiori
- https://github.com/sissbruecker/linkding
- https://github.com/grocy/grocy

