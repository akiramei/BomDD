[INFORM / COMPLETE]

DONE

- inspector: EQ-002 / Codex CLI / gpt-5.6-sol
- 対象: ViewTube `fe0250ef1c09fe3b642749b4636cdcdf17833d8a` の写し（sha256 の照合: 一致）
- sha256:
  - `10-requirements.yaml`: `cb5e3729dd68a819d9f67588a32671cda82d981de732d512e9adbe4f74283306`
  - `30-ebom.yaml`: `8b463d8e4aa39ffc49855f6c80bbe050ca0f3e953ce92b27bc1644859b62c4b2`
  - `31-kbom.yaml`: `577b8a6e1813a4e07081f663993ec7341850af8948c1689a117bcdef9e2013e6`
  - `32-mbom.yaml`: `44144eea3d836d8f78bedc40136f5c420be3bd9d3030c552e118552c049a7233`
  - `20-spec.md`: `02e31c6adbda9479a2b6a8257326f13eaaea468bf24157b2384698b905845203`
- commit: 0 / ファイル変更: 0
- ビルド・テスト: 実行せず
- 外部 API: 呼び出さず
- 読んだファイル一覧: `32-mbom.yaml`, `10-requirements.yaml`, `20-spec.md`, `30-ebom.yaml`, `31-kbom.yaml`

## 分類表

| 単位 | 行# | 句# | 句（原文の該当部分） | 区分 | 裁定層の所在 / 検索結果 / 理由 |
|---|---:|---:|---|---|---|
| M-INFRA-PERSISTENCE-001 | 1 | 1 | `Core has no Avalonia/SQLite/HTTP/OS dependency.` | 参照化 | `10-requirements.yaml:2181-2186` |
| M-INFRA-PERSISTENCE-001 | 2 | 1 | `No external failure deletes user-authored data.` | 参照化 | `10-requirements.yaml:110-115,141-146`。外部障害中もローカル組織を利用可能とし、remote refresh が tags/notes/views 等を変えてはならない。 |
| M-INFRA-PERSISTENCE-001 | 3 | 1 | `ECO-VT-195 (REQ-092 ... user's ruling (b))` | 記録 | ECO・要求・利用者裁定の由来。 |
| M-INFRA-PERSISTENCE-001 | 3 | 2 | `SaveTagAsync and SaveViewAsync` | 製造手段 | 固定スコープを実現する具体的関数名。 |
| M-INFRA-PERSISTENCE-001 | 3 | 3 | `refuse an update whose scope differs from the stored scope_key (DefinitionScopeIsFixed)` | 参照化 | `10-requirements.yaml:3409-3410,3451-3456`。作成済み定義のスコープは移動しない。 |
| M-INFRA-PERSISTENCE-001 | 3 | 4 | `after ECO-VT-193's origin guard` | 製造手段 | 内部検証の順序。 |
| M-INFRA-PERSISTENCE-001 | 3 | 5 | `The store refuses a music-scope assignment.` | 参照化 | `10-requirements.yaml:3396-3402`; `20-spec.md:1019-1021`。Music は定義を所有するが assignment は所有しない。 |
| M-INFRA-PERSISTENCE-001 | 3 | 6 | `MCP save_tag and save_view keep an existing definition's scope when no scopeCollectionId is given` | 参照化 | `10-requirements.yaml:3409-3410,3451-3456`。引数名は具体化だが、述べる製品契約は既存定義の固定スコープ。 |
| M-INFRA-PERSISTENCE-001 | 3 | 7 | `assign_tag / unassign_tag record a music-owned tag Global when none is given` | 参照化 | `10-requirements.yaml:3396-3402,3444-3450`。Music 所有タグ経由の値は global に記録され、第三の assignment branch は持たない。 |
| M-INFRA-PERSISTENCE-001 | 3 | 8 | `Import compares scopes (DefinitionScope), not collection ids` | 製造手段 | identity/scope 契約を実現する内部比較方法。 |
| M-INFRA-PERSISTENCE-001 | 3 | 9 | `a music definition is never matched, shadowed or collided with as a global one` | 参照化 | `10-requirements.yaml:2329-2334`; `20-spec.md:1023-1026`。一意性は scope 内で決まり、Music と Global は別スコープ。 |
| M-INFRA-PERSISTENCE-001 | 4 | 1 | `ECO-VT-212` | 記録 | 変更経緯。 |
| M-INFRA-PERSISTENCE-001 | 4 | 2 | `a view's hierarchy is one JSON blob ... Restriction ... would be dropped by the serializer` | 製造手段 | 永続化表現と旧プロパティ消失の実装上の事情。 |
| M-INFRA-PERSISTENCE-001 | 4 | 3 | `CarryNodeRestrictionsAsync runs on every open inside the initialising transaction` | 製造手段 | 移行関数、実行タイミング、transaction の具体策。 |
| M-INFRA-PERSISTENCE-001 | 4 | 4 | `reads ... raw JSON, removes Restriction, writes Condition by NodeCondition.FromLegacyRestriction ...` | 製造手段 | 具体的な読取・変換・書込方法。 |
| M-INFRA-PERSISTENCE-001 | 4 | 5 | `writes DroppedRestriction where the text could not be carried` | 参照化 | `10-requirements.yaml:986-992`; `20-spec.md:276-280`。変換不能な旧 restriction を捨て、保有 View が警告する契約。 |
| M-INFRA-PERSISTENCE-001 | 4 | 6 | `It is not a schema version bump ...` | 製造手段 | schema migration としない実装判断。 |
| M-INFRA-PERSISTENCE-001 | 4 | 7 | `a restored backup is converted on its open, and a second open finds nothing` | 製造手段 | 移行の起動時期と冪等化方法。 |
| M-INFRA-PERSISTENCE-001 | 4 | 8 | `View Pack export writes Condition and declares node-condition-v1 when any exported node has one` | 人へ戻す | 4ファイルで `node-condition-v1`, `export writes Condition`, `exported node has one` を検索したが該当なし。一般的な required-feature 規則は `20-spec.md:1045-1049` にあるが、正確な feature 名と宣言条件はそれより細かい。 |
| M-INFRA-YOUTUBE-001 | 1 | 1 | `Core has no Avalonia/SQLite/HTTP/OS dependency.` | 参照化 | `10-requirements.yaml:2181-2186` |
| M-INFRA-YOUTUBE-001 | 2 | 1 | `No external failure deletes user-authored data.` | 参照化 | `10-requirements.yaml:110-115,141-146` |
| M-INFRA-YOUTUBE-001 | 3 | 1 | `ECO-VT-209` | 記録 | ECO の由来。 |
| M-INFRA-YOUTUBE-001 | 3 | 2 | `EmbedPageHost.Start hands its accept loop the listener and the cancellation token as values ... never the fields` | 製造手段 | 関数名、値渡し、queue 前の capture という内部実装。 |
| M-INFRA-YOUTUBE-001 | 3 | 3 | `so a Stop at any moment leaves no failed task behind` | 製造手段 | 前句の非同期実装上の守りとその内部 task 結果。 |
| M-INFRA-YOUTUBE-001 | 4 | 1 | `ECO-VT-225 (REQ-095)` | 記録 | ECO・要求の由来。 |
| M-INFRA-YOUTUBE-001 | 4 | 2 | `The player page is not changed for the ended signal` | 製造手段 | REQ-095 は終了時の製品挙動を定めるが、信号取得方法は実装判断と明記される（`10-requirements.yaml:3688-3694,3714-3715`）。 |
| M-INFRA-YOUTUBE-001 | 4 | 3 | `window.__q already answers the YouTube state, and 0 is ended` | 製造手段 | page bridge と数値 state の利用方法。 |
| M-INFRA-YOUTUBE-001 | 4 | 4 | `Seek and mute go through window.__cmd ... seekTo(seconds), mute() and unMute()` | 製造手段 | bridge 関数と引数の渡し方。REQ-095 自身も mechanism を規定しない（`10-requirements.yaml:3714-3715`）。 |
| M-INFRA-YOUTUBE-001 | 4 | 5 | `MEASURED 2026-10-04 ... seekTo(60) ... 62.5 ... seekTo('120') ... 122.5` | 記録 | 日付、環境、操作、実測値。 |
| M-INFRA-YOUTUBE-001 | 4 | 6 | `so CommandAsync needs no overload and the seek is passed as its other arguments are` | 製造手段 | 実測から採用した overload・引数処理の実装判断。 |
| M-INFRA-YOUTUBE-001 | 4 | 7 | `isMuted() followed mute() and unMute()` | 記録 | spike の観測結果。 |
| M-INFRA-YOUTUBE-001 | 4 | 8 | `The measurement is of the page alone: the product's surface was not driven.` | 記録 | 未検査範囲の注記。 |
| M-INFRA-YOUTUBE-001 | 5 | 1 | `ECO-VT-225, R8 round 2 (BLOCKING)` | 記録 | ECO、レビュー回、blocking 判定。 |
| M-INFRA-YOUTUBE-001 | 5 | 2 | `EmbeddedPlayerSurface.OpenAsync RETURNS WITHOUT loadVideoById WHEN ITS STATE IS NO LONGER LOADING` | 製造手段 | 関数名・状態検査・呼出抑止という内部 guard。 |
| M-INFRA-YOUTUBE-001 | 5 | 3 | `StopAsync skips the script call before the page is ready ... and only sets Stopped` | 製造手段 | Stop の内部順序と状態更新方法。 |
| M-INFRA-YOUTUBE-001 | 5 | 4 | `an open ... played it under a state that said Stopped, with nobody owning the sound; the shell cannot see that` | 記録 | 不具合解析・レビュー所見。 |
| M-INFRA-YOUTUBE-001 | 5 | 5 | `The guard is one line` | 製造手段 | 実装修正の形。 |
| M-INFRA-YOUTUBE-001 | 5 | 6 | `NOT exercised by any automated case: no case drives a real WebView2` | 記録 | 未検査範囲。 |
| M-INFRA-YOUTUBE-001 | 5 | 7 | `the spy models the rule ... PageReady false until the first gate passes` | 記録 | test double が規則を仮定しているという検査所見。 |
| M-INFRA-YOUTUBE-001 | 5 | 8 | `Its check is the real-machine step in the body's section 20.` | 記録 | 検査手順の所在。 |
| M-VIEW-PACK-001 | 1 | 1 | `Product manufacture follows the preregistered formal-red probe without weakening its observations.` | 参照化 | `20-spec.md:1056-1059` |
| M-VIEW-PACK-001 | 2 | 1 | `Export, preview, Apply, and scoped delete have explicit transaction and cancellation ownership.` | 参照化 | `10-requirements.yaml:2427-2431,2459-2467`; `20-spec.md:1035-1044`; `31-kbom.yaml:531` |
| M-VIEW-PACK-001 | 3 | 1 | `Existing global Tag/View/assignment and complete-result selection behavior remains a regression yardstick.` | 参照化 | `20-spec.md:1050-1054`; `10-requirements.yaml:2503-2507`。既存 result ownership と complete-result selection を維持する。 |
| M-VIEW-PACK-001 | 4 | 1 | `ECO-VT-195 (the user's ruling of 2026-09-27, E)` | 記録 | ECO・日付・利用者裁定。 |
| M-VIEW-PACK-001 | 4 | 2 | `the pack format carries Music as a third owner` | 参照化 | `20-spec.md:1018-1026`; `10-requirements.yaml:3387-3391`。Music は Global/CollectionLocal と別の定義所有スコープ。 |
| M-VIEW-PACK-001 | 4 | 3 | `a pack with a music definition lists music-scope-v1, and the reader supports it` | 参照化 | `20-spec.md:1019-1022` |
| M-VIEW-PACK-001 | 4 | 4 | `A music tag may shadow a global one (collection-local rules).` | 参照化 | `10-requirements.yaml:2329-2334`; `20-spec.md:1023-1026` |
| M-VIEW-PACK-001 | 4 | 5 | `Import lands music definitions in the receiver's music scope unless a target collection is forced.` | 人へ戻す | 4ファイルで `target collection`, `forced`, `music definitions`, `music scope import` を検索。Music scope と import の一般規則はあるが、target collection 指定時に Music 定義を別 scope へ着地させる例外は見つからない。 |
| M-VIEW-PACK-001 | 4 | 6 | `A collection's export drops music-owned tags' assignments` | 参照化 | `10-requirements.yaml:3396-3408`。Music は assignment を所有せず、Collection export は Music の tag/value を運ばない。 |
| M-VIEW-PACK-001 | 4 | 7 | `an export from the music scope ... carries its own views and their tags only` | 参照化 | `10-requirements.yaml:3406-3408,3457-3462` |
| M-VIEW-PACK-001 | 5 | 1 | `ECO-VT-212` | 記録 | ECO の由来。 |
| M-VIEW-PACK-001 | 5 | 2 | `ViewPackHierarchyPlacement carries Condition; its Restriction is read-only, never written (omitted when null)` | 製造手段 | DTO/serializer の具体的な表現・書込方法。 |
| M-VIEW-PACK-001 | 5 | 3 | `CarryLegacyRestrictions converts a pack ... with the pack's own tag types, by FromLegacyRestriction` | 参照化 | `10-requirements.yaml:973-992`; `20-spec.md:269-280`。旧 restriction は tag type に従って結果を保つ condition へ移す。 |
| M-VIEW-PACK-001 | 5 | 4 | `a numeric restriction that does not read as a number refuses the pack (ViewPackLegacyRestrictionUnreadable)` | 人へ戻す | `numeric restriction`, `ViewPackLegacyRestrictionUnreadable`, `refuses the pack` を4ファイルで検索し一致なし。近い裁定は `10-requirements.yaml:986-992` / `20-spec.md:276-280` だが、そこでは変換不能 numeric を捨てて警告するため、本句の pack 全体拒否はより強い。 |
| M-VIEW-PACK-001 | 5 | 5 | `a placement carrying both forms refuses as ViewPackNodeConditionAmbiguous` | 人へ戻す | `both forms`, `ViewPackNodeConditionAmbiguous`, `ambiguous` を4ファイルで検索し、この二重表現拒否契約は見つからない。一般的な malformed input 拒否（`20-spec.md:1045-1049`）より具体的。 |
| M-VIEW-PACK-001 | 5 | 6 | `Import validates each view's conditions for form ... a candidate is not held to the definition` | 参照化 | `10-requirements.yaml:973-985`; `20-spec.md:269-275`。form は検証するが、保存済み selection の候補を現定義に限定しない。 |
| M-VIEW-PACK-001 | 5 | 7 | `The reader supports node-condition-v1; a reader from before it refuses such a pack before mutation.` | 人へ戻す | `node-condition-v1` を4ファイルで検索し一致なし。未知 required feature を mutation 前に拒否する一般則は `20-spec.md:1045-1049` にあるが、feature 名、導入条件、旧 reader の対象範囲は本句の方が細かい。 |
| M-VIEW-PACK-001 | 6 | 1 | `ECO-VT-212 R8 round 1, the user's ruling Q2 (i)` | 記録 | ECO、レビュー回、利用者裁定。 |
| M-VIEW-PACK-001 | 6 | 2 | `a pack carries a selection as it is stored` | 参照化 | `10-requirements.yaml:980-985`; `20-spec.md:273-275` |
| M-VIEW-PACK-001 | 6 | 3 | `Import still refuses a condition out of form, but does not hold a candidate to the pack's tag definition` | 参照化 | `10-requirements.yaml:973-985`; `20-spec.md:269-275` |
| M-VIEW-PACK-001 | 6 | 4 | `a view keeping a candidate its tag dropped is exported, and lands with that candidate selected and shown as no longer a candidate` | 参照化 | `10-requirements.yaml:980-985`; `20-spec.md:272-275` |
| M-VIEW-PACK-001 | 6 | 5 | `The candidate must be predefined only where it is newly chosen - the editor and MCP` | 参照化 | `10-requirements.yaml:982-985`; `20-spec.md:273-275` |
| M-VIEW-PACK-001 | 6 | 6 | `through ViewHierarchyService` | 製造手段 | 契約を実現する具体的 service の選択。 |

## 集計

| 単位 | 行数 | 句数 | 参照化 | 人へ戻す | 製造手段 | 記録 | 分類不能 | 2つ以上の区分を含む行の数 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| M-INFRA-PERSISTENCE-001 | 4 | 19 | 8 | 1 | 8 | 2 | 0 | 2 |
| M-INFRA-YOUTUBE-001 | 5 | 21 | 2 | 0 | 9 | 10 | 0 | 3 |
| M-VIEW-PACK-001 | 6 | 23 | 14 | 4 | 2 | 3 | 0 | 3 |
| **合計** | **15** | **63** | **24** | **5** | **19** | **15** | **0** | **8** |

## 行ごとの区分の集合

| 単位 | 行# | その行に現れる区分の集合 |
|---|---:|---|
| M-INFRA-PERSISTENCE-001 | 1 | {参照化} |
| M-INFRA-PERSISTENCE-001 | 2 | {参照化} |
| M-INFRA-PERSISTENCE-001 | 3 | {参照化, 製造手段, 記録} |
| M-INFRA-PERSISTENCE-001 | 4 | {参照化, 人へ戻す, 製造手段, 記録} |
| M-INFRA-YOUTUBE-001 | 1 | {参照化} |
| M-INFRA-YOUTUBE-001 | 2 | {参照化} |
| M-INFRA-YOUTUBE-001 | 3 | {製造手段, 記録} |
| M-INFRA-YOUTUBE-001 | 4 | {製造手段, 記録} |
| M-INFRA-YOUTUBE-001 | 5 | {製造手段, 記録} |
| M-VIEW-PACK-001 | 1 | {参照化} |
| M-VIEW-PACK-001 | 2 | {参照化} |
| M-VIEW-PACK-001 | 3 | {参照化} |
| M-VIEW-PACK-001 | 4 | {参照化, 人へ戻す, 記録} |
| M-VIEW-PACK-001 | 5 | {参照化, 人へ戻す, 製造手段, 記録} |
| M-VIEW-PACK-001 | 6 | {参照化, 製造手段, 記録} |

## 「人へ戻す」とした句の一覧

- M-INFRA-PERSISTENCE-001 行4句8 — `node-condition-v1` の宣言条件。近い節: `20-spec.md` の「ECO-VT-056 View Pack contract preregistration」§8（file/required-feature boundary）、または REQ-077。
- M-VIEW-PACK-001 行4句5 — target collection 指定時の Music 定義の着地先。近い節: REQ-071〜073 / `20-spec.md` §3 Definition scope・§5 Dependency and resolution。
- M-VIEW-PACK-001 行5句4 — 読めない numeric legacy restriction で pack 全体を拒否する契約。近い節: REQ-032 の legacy restriction migration、または REQ-077 の malformed-input policy。
- M-VIEW-PACK-001 行5句5 — `Condition` と `Restriction` の二重保持を ambiguous として拒否する契約。近い節: REQ-032 の condition form validation、または REQ-077。
- M-VIEW-PACK-001 行5句7 — `node-condition-v1` の reader compatibility 契約。近い節: REQ-077 / `20-spec.md` §8 file and data boundary。

## 迷った句と決め方

- `No external failure deletes user-authored data.` は裁定層に同一の一文はないが、REQ-004 の「remote failure 中もローカル組織を利用可能」と、`10-requirements.yaml:141-146` の「remote update は user-authored organization を変更しない」を合わせれば同じ制約を読み取れるため、参照化とした。
- `MCP ... keep an existing definition's scope when no scopeCollectionId is given` は引数省略時という細部を含む。ただし観測される契約は「既存定義の scope は作成後に変わらない」そのものであり、引数名だけを独立した要求とは扱わず参照化とした。
- `a numeric restriction ... refuses the pack` は、裁定層の旧 restriction 規則に近いが、裁定層は変換不能 numeric を drop＋warning としている。本句は pack 全体拒否へ強化しており同内容ではないため、人へ戻すとした。
- `node-condition-v1` の2句は、未知 required feature の拒否という一般則には近い。しかし正確な feature 名、いつ宣言するか、旧 reader が何を拒否するかは裁定層にないため、人へ戻すとした。
- YouTube の ended/seek/mute 句は製品機能に関係するが、REQ-095 自身がこれらの mechanism を M-BOM の実装判断と明記している（`10-requirements.yaml:3714-3715`）。したがって製造手段とした。