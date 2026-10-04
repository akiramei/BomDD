[INFORM / COMPLETE]

REJECT IA-01

- inspector: EQ-002 / Codex CLI / gpt-5.6-sol
- 対象: HEAD `9f239a83ff48f5412b8a7d626661beafc119d9fd` + 作業ツリー
- commit: 0 / ファイル変更: 0
- 開始時 git status --short: `M .claude/skills/eco-fix/SKILL.md`; `M bomdd/32-mbom.yaml`; `M bomdd/33-control-plan.yaml`; `M bomdd/cp_results.py`; `M tests/ViewPrism2.Tests/CpDb006Tests.cs`; `M tests/ViewPrism2.Tests/CpThumb007Tests.cs`; `M tests/ViewPrism2.Tests/CpThumb049ExifTests.cs`; `M tests/ViewPrism2.Tests/CpThumb144VersionPinTests.cs`
- 終了時 git status --short: 開始時と同一
- 読んだファイル一覧: `bomdd/10-requirements.yaml`, `bomdd/20-spec.md`, `bomdd/30-ebom.yaml`, `bomdd/31-kbom.yaml`, `bomdd/32-mbom.yaml`, `bomdd/33-control-plan.yaml`, `bomdd/cp_results.py`, `tests/ViewPrism2.Tests/CpThumb007Tests.cs`, `CpThumb049ExifTests.cs`, `CpThumb144VersionPinTests.cs`, `CpDb006Tests.cs`, および指定ファイルの `git diff`
- 禁止対象の変更命令書・変更台帳・`.claude/`・`AGENTS.md`・`CLAUDE.md`・BomDD リポは読んでいない

## A. ID ごとの判定

| ID | 判定 | 検査している内容 | statement のうち検査していない部分 |
|---|---|---|---|
| REQ-003 | 合 | 新規 DB の `journal_mode=wal` と `foreign_keys=1` を実照会している（`CpDb006Tests.cs:137-151`） | なし |
| REQ-004 | 条件付き | 新規 DB の全 migration ID 記録、v0→最新スキーマ同値、未適用 ID 昇順、再実行時の冪等性（`:155-227`） | `migrations` の列定義 `id TEXT PK, executed_at` の独立オラクル、各 migration がトランザクション内で実行されること |
| REQ-010 | 条件付き | フォルダ削除 API の成立と配下 images/image_tags の連鎖消滅、path の大文字小文字違いの明示拒否と DB UNIQUE 実動（`:287-331`） | 登録・編集・無効化、各フィールドと既定値、exclude_patterns の意味、name 重複許可。フォルダ削除時 CASCADE は statement 本文ではなく rationale にある |
| REQ-028 | 合 | タグ削除後の image_tags、view_conditions、階層ノード、子タグ parent_id の4規則すべて（`:231-285`） | なし |
| REQ-040 | 条件付き | 寸法・比率・拡大禁止、PNG/非PNG形式、キャッシュヒット、パス大小文字同一キー、生成失敗時 null/記録なし、破損キャッシュ再生成（`CpThumb007Tests.cs:51-201`） | JPEG 品質80、実際の `%APPDATA%` 保存先、ファイル名が正しい MD5 値であること、プレースホルダ表示、元画像修復後の次回成功。絶対パス化そのものも直接は検査していない |
| REQ-085 | 条件付き | Orientation 6 の正立サムネ・実効寸法・向き付きピクセル、TopLeft 回帰、`-v2` と旧キャッシュ非参照（`CpThumb049ExifTests.cs:37-135`） | Orientation 2〜5・7・8、実ビューアのフルサイズ表示、pHash/SHA-256/スキャンへの非適用、旧ファイルが削除されず孤児として残ること |
| REQ-104 | 条件付き | 三実ファイルから版を抽出でき、三者が一致し、各文字列が `x.y.z` exact 形式であること（`CpThumb144VersionPinTests.cs:27-58`） | 値が指定版 `3.119.4` であること、交換不可という境界、更新を DEG として受理すること、CP-THUMB-007 と CP-DUPQUALITY-030 全 fixture の再検査・採用ゲート |
| REQ-105 | 条件付き | 同一構成でのキャッシュヒット時 mtime 不変、新世代 `-v2` が旧世代名を参照せず生成されること（`CpThumb007Tests.cs:132-149`; `CpThumb049ExifTests.cs:81-106`） | 実際の部品交換・更新後にも既存キャッシュを継続利用できること、世代更新時の新旧共存（旧ファイルの残存）の明示確認 |
| REQ-106 | 否 | 壊れた JPG が null・キャッシュなし・例外なしになる部分は検査する（`CpThumb007Tests.cs:165-180`） | スキャンと一覧の継続、他画像の処理・表示継続、読めない画像。加えて破損キャッシュ再生成テストの REQ-106 trait は statement と対応しない（IA-01） |

条件付きは「検査している部分には意味対応があるが、statement 全体は覆わない」の意であり、それ自体は reject 理由ではない。

## A-3・A-4 / B / C / D

### 3. trait のない2テスト

- `解像度取得はフルデコードなしで寸法を返す`（`CpThumb007Tests.cs:203-214`）:
  - 非 EXIF の寸法取得と壊れた入力で null を検査する。
  - 生きている要求の statement に、通常画像の GetDimensions 実装方式や「フルデコードなし」を直接要求する ID はない。REQ-085 は Orientation 5〜8 の実効寸法、REQ-106 はサムネイルとスキャン／一覧の継続を述べるため、このテスト全体へ付けるべき req trait はない。
- `COLLATE_NOCASEが主要列に付与されている`（`CpDb006Tests.cs:334-349`）:
  - `sync_folders.path` 部分は REQ-010、`images.relative_path` 部分は REQ-014 に対応する（`10-requirements.yaml:71-77`, `119-122`）。
  - したがって分割するか、少なくとも REQ-010 と REQ-014 の対応を表現すべきである。ただし現状でも同じ CP 内の重複拒否テストが REQ-010 の外部挙動を検査しており、trait 欠落だけを blocking とはしない。

### 4. 付けるべきでない trait

- `破損キャッシュは削除して再生成する` の REQ-106 trait（`CpThumb007Tests.cs:182-200`）は不適切。
- このテストが検査するのは、REQ-040 statement の「読み取り不能なキャッシュファイルは削除して再生成する」（`10-requirements.yaml:377-382`）。
- REQ-106 statement は「壊れた画像・読めない画像」「その画像のサムネイルだけ null」「スキャンと一覧・他画像が続く」（`:1527-1532`）であり、正常な元画像に対する壊れたキャッシュの再生成は述べていない。REQ-106 rationale の受入記載だけでは、今回指定された statement 基準での対応にならない。

### 5. refs にあるが行のテストが検査していない ID

- CP-DB-006: なし。REQ-003/004/010/028 はいずれも少なくとも statement の一部を検査する。
- CP-THUMB-007:
  - INV-009 は指定どおり「検査なし」。
  - REQ-040/085/104/105 は少なくとも一部を検査する。
  - REQ-106 は壊れた JPG の null・キャッシュなし・例外なし部分を検査するため、ID 全体として「検査なし」ではない。ただし破損キャッシュテストの trait は誤対応（IA-01）。

### 6. 行のテストが検査しているのに refs にない裁定層 ID

- CP-DB-006 の trait なしテストは REQ-014 の `images.relative_path` case-insensitive を検査しているため、REQ-014 が refs にない。
- 同テストの `sync_folders.path` 部分は既存 ref の REQ-010 に含まれる。
- CP-THUMB-007 について追加すべき裁定層 ID は認めない。

### 7. `when` / `on_fail`

- 両行の `when: acceptance` は、受入用 L2 fixture の実態と矛盾しない（`33-control-plan.yaml:264,285`）。
- `red: product-fix` と `unmeasurable: instrument-recovery` も検査の実態と整合する。
- CP-THUMB-007 の `dependency-update: human-approval` は REQ-104 の DEG／再検査採用経路と整合する。ただし通常の版不一致は人の承認ではなく製品修正であり、行の記述もその区別をしている（`:282-307`）。

## C. M-BOM の行の分類

削除された6行はいずれも裁定層に同内容が存在し、削除による意味の喪失や明白な狭化・広化は認めない。

1. M-DB-007「単一共有+SemaphoreSlim シリアル化」
   - 同内容: `bomdd/31-kbom.yaml:14`
   - 新 `manufacturing_decisions`: `bomdd/32-mbom.yaml:131-132`
2. M-DB-007「migrations テーブル契約は REQ-004 のとおり」
   - 同内容: `bomdd/10-requirements.yaml:48-52`
   - 仕様展開: `bomdd/20-spec.md:41-43`
   - E-BOM: `bomdd/30-ebom.yaml:169,175-179`
3. M-DB-007「スキャンバッチ失敗時は全ロールバック、部分適用なし」
   - 同内容: `bomdd/30-ebom.yaml:179`
4. M-THUMB-008「INV-009 元画像へ書き込まない」
   - 同内容: `bomdd/20-spec.md:1435`
   - E-BOM: `bomdd/30-ebom.yaml:413-414`
5. M-THUMB-008「読み取り不能キャッシュは削除して再生成」
   - 同内容: `bomdd/10-requirements.yaml:378`
   - 仕様: `bomdd/20-spec.md:345-346`
6. M-THUMB-008「EXIF は表示系のみ、pHash 入力には適用しない」
   - 同内容: `bomdd/10-requirements.yaml:1095`
   - 仕様: `bomdd/20-spec.md:347-352`
   - K-BOM: `bomdd/31-kbom.yaml:36`

### 9. `manufacturing_decisions`

- `接続戦略は K-SQLITE(ADR-0003)のとおり(単一共有+SemaphoreSlim シリアル化)`（`32-mbom.yaml:131-132`）は、K-BOM の「アプリ全体で単一の SqliteConnection を共有し、SemaphoreSlim(1,1) でシリアル化」（`31-kbom.yaml:14`）と一致する。
- M-BOM 側は型引数 `(1,1)` と接続型名を省略した参照形だが、K-SQLITE を明示参照しており意味の変更ではない。

## D. `cp_results.py`

### 10. selftest と区分

- `python bomdd/cp_results.py --selftest` は実行していない。selftest は一時ディレクトリへ YAML/XML を作成・変更・削除する実装であり、今回の「ファイルの作成・変更・削除 0」を優先した。
- 読解上、`classify_ruled` は以下を正しく区別する:
  - Fail が1件でもあれば違反
  - Pass があれば合格
  - trait はあるが Pass/Fail 以外だけなら測定不能
  - trait がなく、参照元がすべて human-only depth なら「未実行(人の承認で検査)」
  - それ以外は「未実行(検査なし)」
- 完全に検査が届かない L2 ID が「合格」になる直接経路は認めない。
- ただし同一 ID に Pass と Skip/NotRun が混在すると `n_pass` により「合格」になる。ID 内の一部 vector が測定不能でも ID 全体が合格表示される経路である。
- また、本件 IA-01 のように trait の意味対応が誤っていても、スクリプトは文字列一致だけを見るため、その誤ったテストが Pass すれば REQ-106 を合格表示できる。これは表の機械的限界であり、今回の意味審査が必要な理由に当たる。
- 「人の承認で検査」への経路は、ID が参照される全 CP 行の depth が human-only の場合に限定される。今回追加された CP-DB-006/CP-THUMB-007 は L2 のため、その誤分類経路はない。

## 所見

### IA-01 — blocking

- 内容: `破損キャッシュは削除して再生成する` に REQ-106 trait が付いているが、REQ-106 statement を検査していない。
- テスト根拠: `tests/ViewPrism2.Tests/CpThumb007Tests.cs:182-200`
- 裁定層根拠:
  - REQ-106 statement: `bomdd/10-requirements.yaml:1527-1528`
  - 実際に対応する REQ-040 statement: `bomdd/10-requirements.yaml:377-378`
- 影響: 誤った trait により、`cp_results.py` は破損キャッシュ再生成の Pass を REQ-106 の検査結果として数える。判定条件の「付けるべきでない trait」に該当するため blocking。
- 是正方向: 当該テストから REQ-106 trait を外し、REQ-040 のみとする。REQ-106 のスキャン／一覧／他画像継続を測るなら別テストが必要。

## 範囲外の観察（判定に含めない）

- CP-DB-006 の `characteristic` は依然として「REQ-003〜005 と一致する」と書く一方、REQ-005 は意図的に refs から除外され、fixture も DB 配置場所を検査しない（`33-control-plan.yaml:262-270`）。refs の意味審査とは別の記述整合性所見として記録する。
