# 統括 AI の分類 — ECO-099(ViewTube fe0250ef・3 単位 15 行・句ごと)

- 分類者: 統括 AI(EQ-001・claude-fable-5-1)。2026-10-05。**検査官の報告(inspection-report.md)を開く前に書いた**(検査官の実行は先に終わっていたが、本ファイルを保存してから読む)。
- 読んだもの: 対象 commit の `bomdd/32-mbom.yaml`・`10-requirements.yaml`・`20-spec.md`・`30-ebom.yaml`・`31-kbom.yaml`(`git show fe0250ef…:<path>` を scratchpad に写して読んだ。ViewTube の作業ツリーは読んでいない)。
- 所在の表記: `10:L3409`= 10-requirements.yaml の 3409 行(対象 commit)。検索は 4 ファイルに対する grep(語は各行に記す)。

## 分類表

| 単位 | 行 | 句 | 句(原文の該当部分) | 区分 | 所在 / 検索した語と結果 / 理由 |
|---|---|---|---|---|---|
| PERSISTENCE | 1 | 1 | Core has no Avalonia/SQLite/HTTP/OS dependency. | 参照化 | 20:L673「Core は Avalonia/SQLite/HTTP/OS を参照しない」・10:L2185 |
| PERSISTENCE | 2 | 1 | No external failure deletes user-authored data. | **人へ戻す** | 検索「user-authored」「ユーザー作成」「failure … preserv / leaves」「must not delete」→ 近い文= 10:L146 rationale「Remote data is mutable and disposable; user-authored organization is the durable product value」・30:L811「ユーザー作成データを外部応答や表示状態から分離する」・個別の失敗の保全(10:L795・L2091)。**「どの外部の失敗もユーザー作成データを消さない」という全称の保証は裁定層に無い**(句の方が強い) |
| PERSISTENCE | 3 | 1 | ECO-VT-195 (REQ-092: a scope is fixed at creation, everywhere - the user's ruling (b)) | 参照化 | 10:L3409「A DEFINITION'S SCOPE IS FIXED WHEN IT IS CREATED, here as everywhere」・L3451(裁定の日付つき) |
| PERSISTENCE | 3 | 2 | SaveTagAsync and SaveViewAsync refuse an update whose scope differs from the stored scope_key (DefinitionScopeIsFixed), after ECO-VT-193's origin guard. | 製造手段 | どの関数がどの順で拒否するか |
| PERSISTENCE | 3 | 3 | The store refuses a music-scope assignment. | 参照化 | 20:L1019〜1020「Music … owns Tags and Views but no assignments」・10:L3395〜3397「WHAT THE SCOPE OWNS IS DEFINITIONS AND NOT VALUES」 |
| PERSISTENCE | 3 | 4 | The MCP save_tag and save_view keep an existing definition's scope when no scopeCollectionId is given | 参照化 | 10:L3409〜3410「A definition that already exists does not become one of this scope's by being edited」から読める(引数の名前は作り方)。検索「scopeCollectionId」→ 0 件 |
| PERSISTENCE | 3 | 5 | assign_tag / unassign_tag record a music-owned tag Global when none is given | 参照化 | 10:L3395〜3397「A tag assignment made through a definition this scope owns is recorded globally」 |
| PERSISTENCE | 3 | 6 | Import compares scopes (DefinitionScope), not collection ids, so a music definition is never matched, shadowed or collided with as a global one. | 参照化 | 20:L1023「Tag/View uniqueness is (scope, Ordinal name)」・L1019(Music は別の scope)。「DefinitionScope で比べる」は作り方だが、句の主旨(music の定義が global と混ざらない)は裁定層にある |
| PERSISTENCE | 4 | 1 | ECO-VT-212: a view's hierarchy is one JSON blob, so a node's Restriction - a property the model no longer has - would be dropped by the serializer without a word. | 記録 | なぜこの処理が要るかの経緯(実装の事情) |
| PERSISTENCE | 4 | 2 | CarryNodeRestrictionsAsync runs on every open inside the initialising transaction: it reads each view's raw JSON, removes Restriction, writes Condition by NodeCondition.FromLegacyRestriction …, and writes DroppedRestriction where the text could not be carried. | 製造手段 | いつ・どの関数が変換するか。変換の意味(結果を保つ・運べないものは捨てて知らせる)は 10:L986〜992・20:L276〜280 にある |
| PERSISTENCE | 4 | 3 | It is not a schema version bump (the restore path compares a backup against SchemaVersion); a restored backup is converted on its open, and a second open finds nothing. | **人へ戻す** | 検索「schema version」「SchemaVersion」「restored backup」「on its open」→ 20:L636(schema version を 1 ずつ migration)・31:L248・L355(restore は schema version を確かめる)。**「この変換は schema version を上げない・以前のバックアップは復元後の最初の open で変換される」というデータ互換の決めは裁定層に無い** |
| PERSISTENCE | 4 | 4 | View Pack export writes Condition and declares node-condition-v1 when any exported node has one. | **人へ戻す** | 検索「node-condition」→ 4 ファイルで 0 件。同種の `music-scope-v1` は 20:L1021 にある。**pack の形式の必須機能フラグ(版の違う読み手との取り決め)が裁定層に無い** |
| YOUTUBE | 1 | 1 | Core has no Avalonia/SQLite/HTTP/OS dependency. | 参照化 | PERSISTENCE 行 1 と同文 |
| YOUTUBE | 2 | 1 | No external failure deletes user-authored data. | **人へ戻す** | PERSISTENCE 行 2 と同文(同じ 1 件) |
| YOUTUBE | 3 | 1 | ECO-VT-209: EmbedPageHost.Start hands its accept loop the listener and the cancellation token as values taken before the work is queued, never the fields, so a Stop at any moment leaves no failed task behind. | 製造手段 | 検索「EmbedPageHost」→ 0 件。内部の受け渡しの守り |
| YOUTUBE | 4 | 1 | ECO-VT-225 (REQ-095). The player page is not changed for the ended signal: window.__q already answers the YouTube state, and 0 is ended. | 製造手段 | 10:L3714〜3715 が明示: 「THE MECHANISM IS NOT SAID HERE … the ended signal, the seek and the mute are implementation judgements recorded in the M-BOM」 |
| YOUTUBE | 4 | 2 | Seek and mute go through window.__cmd as pause and stop do: seekTo(seconds), mute() and unMute(). | 製造手段 | 同上 |
| YOUTUBE | 4 | 3 | MEASURED 2026-10-04 (spike, WebView2 154.0.4258.53, the product's own page, muted): seekTo(60) … at 62.5 after 2.5 s and seekTo('120') … at 122.5 …; isMuted() followed mute() and unMute(). | 記録 | 実測値(日付・版・観測) |
| YOUTUBE | 4 | 4 | so CommandAsync needs no overload and the seek is passed as its other arguments are | 製造手段 | 実測からの作り方の帰結 |
| YOUTUBE | 4 | 5 | The measurement is of the page alone: the product's surface was not driven. | 記録 | 実測の限界の注記 |
| YOUTUBE | 5 | 1 | ECO-VT-225, R8 round 2 (BLOCKING). | 記録 | レビューの所見の由来 |
| YOUTUBE | 5 | 2 | EmbeddedPlayerSurface.OpenAsync RETURNS WITHOUT loadVideoById WHEN ITS STATE IS NO LONGER LOADING after the page is ready. | 製造手段 | 実装の守り(迷った句— 下) |
| YOUTUBE | 5 | 3 | StopAsync skips the script call before the page is ready … and only sets Stopped, so an open that went on to load the video played it under a state that said Stopped, with nobody owning the sound; the shell cannot see that from the state. | 記録 | 見つかった欠陥の説明 |
| YOUTUBE | 5 | 4 | The guard is one line and is NOT exercised by any automated case: no case drives a real WebView2, and the spy models the rule (…). | 記録 | 検査していないことの注記 |
| YOUTUBE | 5 | 5 | Its check is the real-machine step in the body's section 20. | 記録 | どこで確かめるかの参照 |
| VIEW-PACK | 1 | 1 | Product manufacture follows the preregistered formal-red probe without weakening its observations. | 参照化 | 20:L1056〜1058「The preregistered formal-red detector … must fail before product correction and is not weakened after manufacture」 |
| VIEW-PACK | 2 | 1 | Export, preview, Apply, and scoped delete have explicit transaction and cancellation ownership. | 参照化 | 20:L1035〜1046(6 Planning and mutation・7 Collection deletion・8 File and data boundary)・31:L531 |
| VIEW-PACK | 3 | 1 | Existing global Tag/View/assignment and complete-result selection behavior remains a regression yardstick. | 参照化 | 20:L1052〜1054「Existing Videos result ownership … and complete-result batch selection remain authoritative」 |
| VIEW-PACK | 4 | 1 | ECO-VT-195 (the user's ruling of 2026-09-27, E): the pack format carries Music as a third owner; a pack with a music definition lists music-scope-v1, and the reader supports it. | 参照化 | 20:L1019〜1022 |
| VIEW-PACK | 4 | 2 | A music tag may shadow a global one (collection-local rules). | 参照化 | 20:L1023〜1024 |
| VIEW-PACK | 4 | 3 | Import lands music definitions in the receiver's music scope unless a target collection is forced. | **人へ戻す** | 検索「target collection」「forced」「receiver's music」「import … music」→ 0 件(20:L1080 は別の文脈)。取り込み先の決め方(既定は受け手の music scope・collection を指定すればそちら)は裁定層に無い |
| VIEW-PACK | 4 | 4 | A collection's export drops music-owned tags' assignments (REQ-092 as amended) | 参照化 | 10:L3406〜3408「A collection's export does not carry this scope's tags or their values」 |
| VIEW-PACK | 4 | 5 | an export from the music scope (ruling (a)) carries its own views and their tags only. | 参照化 | 10:L3405〜3406 |
| VIEW-PACK | 5 | 1 | ECO-VT-212: ViewPackHierarchyPlacement carries Condition; its Restriction is read-only, never written (omitted when null). | **人へ戻す** | pack の形式(書くのは Condition・Restriction は読むだけ)。検索「node-condition」「Restriction」→ 形式の取り決めは 0 件(10:L986 は保存済みの restriction の意味)。PERSISTENCE 行 4 句 4 と同じ 1 件(node condition の pack 形式) |
| VIEW-PACK | 5 | 2 | ViewPackJsonTransfer.CarryLegacyRestrictions converts a pack from before ECO-VT-212 on read, with the pack's own tag types, by FromLegacyRestriction | 製造手段 | どの関数が読み取り時に変換するか。変換の意味は 10:L986〜992 |
| VIEW-PACK | 5 | 3 | a numeric restriction that does not read as a number refuses the pack (ViewPackLegacyRestrictionUnreadable) rather than importing it with the condition gone | **人へ戻す** | 保存済みの同じ状況は「捨てて、その View が警告で知らせる」(10:L989〜992・20:L278〜280)。**pack では拒否する、という別の決めは裁定層に無い**(検索「unreadable」「refuses the pack」→ 0 件。一般則 20:L1047「malformed … reject before mutation」に含めるかは迷った句— 下) |
| VIEW-PACK | 5 | 4 | a placement carrying both forms refuses as ViewPackNodeConditionAmbiguous | 参照化 | 20:L1047「malformed/truncated/duplicate/cyclic inputs reject before mutation」(両方の形を持つ= 不正な入力) |
| VIEW-PACK | 5 | 5 | Import validates each view's conditions for form (R8 round 1: a candidate is not held to the definition - see below). | 参照化 | 10:L979〜985・20:L272〜275 |
| VIEW-PACK | 5 | 6 | The reader supports node-condition-v1; a reader from before it refuses such a pack before mutation. | 参照化 | 拒否の規則は 20:L1047「Unknown required features … reject before mutation」。フラグの名前と存在は行 5 句 1 の件に含める |
| VIEW-PACK | 6 | 1 | ECO-VT-212 R8 round 1, the user's ruling Q2 (i): a pack carries a selection as it is stored. | 参照化 | 10:L983〜985・20:L274〜275 |
| VIEW-PACK | 6 | 2 | Import still refuses a condition out of form, but does not hold a candidate to the pack's tag definition, so a view keeping a candidate its tag dropped is exported, and lands with that candidate selected and shown as no longer a candidate (R212a-F1, F3). | 参照化 | 同上 |
| VIEW-PACK | 6 | 3 | The candidate must be predefined only where it is newly chosen - the editor and MCP, through ViewHierarchyService. | 参照化 | 10:L982。「through ViewHierarchyService」は作り方(句を分けず、主旨で参照化) |

## 集計

| 単位 | 行数 | 句数 | 参照化 | 人へ戻す | 製造手段 | 記録 | 分類不能 | 2 つ以上の区分を含む行 |
|---|---|---|---|---|---|---|---|---|
| M-INFRA-PERSISTENCE-001(既見) | 4 | 12 | 6 | 3 | 2 | 1 | 0 | 2(行 3・行 4) |
| M-INFRA-YOUTUBE-001(既見) | 5 | 13 | 1 | 1 | 5 | 6 | 0 | 2(行 4・行 5) |
| M-VIEW-PACK-001(未見) | 6 | 17 | 13 | 3 | 1 | 0 | 0 | 2(行 4・行 5) |
| 合計 | 15 | 42 | 20 | 7 | 8 | 7 | 0 | 6 |

「人へ戻す」7 句は、内容では **5 件**(同文・同件をまとめる):

| # | 内容 | 現れる句 | 裁定層に書くとしたら |
|---|---|---|---|
| H1 | どの外部の失敗もユーザー作成データを消さない(全称の保証) | PERSISTENCE 2-1・YOUTUBE 2-1 | 20-spec の不変条件(INV)か、10 の横断の要求 |
| H2 | 旧い restriction の変換は schema version を上げず、以前のバックアップは復元後の最初の open で変換される | PERSISTENCE 4-3 | REQ(node condition の移行)の statement か、バックアップの要求(REQ-064)の互換の句 |
| H3 | node condition を持つ pack は必須機能 `node-condition-v1` を宣言し、pack が書くのは Condition で Restriction は読むだけ | PERSISTENCE 4-4・VIEW-PACK 5-1 | 20-spec の View Pack の節(music-scope-v1 と同じ場所) |
| H4 | 取り込みは music の定義を受け手の music scope に置く(collection を指定した場合を除く) | VIEW-PACK 4-3 | 20-spec の View Pack の節 3(Definition scope) |
| H5 | 数として読めない numeric restriction を持つ旧い pack は、条件を落として取り込まずに pack ごと拒否する | VIEW-PACK 5-3 | REQ(node condition)の「旧い restriction」の句に pack の場合を足す |

## 行ごとの区分の集合

| 単位 | 行 | 区分の集合 |
|---|---|---|
| PERSISTENCE | 1 | {参照化} |
| PERSISTENCE | 2 | {人へ戻す} |
| PERSISTENCE | 3 | {参照化, 製造手段} |
| PERSISTENCE | 4 | {記録, 製造手段, 人へ戻す} |
| YOUTUBE | 1 | {参照化} |
| YOUTUBE | 2 | {人へ戻す} |
| YOUTUBE | 3 | {製造手段} |
| YOUTUBE | 4 | {製造手段, 記録} |
| YOUTUBE | 5 | {記録, 製造手段} |
| VIEW-PACK | 1 | {参照化} |
| VIEW-PACK | 2 | {参照化} |
| VIEW-PACK | 3 | {参照化} |
| VIEW-PACK | 4 | {参照化, 人へ戻す} |
| VIEW-PACK | 5 | {人へ戻す, 製造手段, 参照化} |
| VIEW-PACK | 6 | {参照化} |

## 迷った句と決め方

- **PERSISTENCE 2-1 / YOUTUBE 2-1(H1)**: 裁定層には「ユーザー作成の整理が製品の価値」「外部応答から分離する」と、個別の失敗での保全(バッチの失敗は割り当てを変えない・復元の失敗は現行のカタログを変えない)がある。句は「どの外部の失敗も」という全称で、裁定層のどの文よりも強い → 人へ戻す。
  E-BOM の 1 行(分離する)を「同じ内容」と読めば参照化になる — 検査官と割れる可能性が高い句。
- **YOUTUBE 5-2**: 「止めた後に遅れて開いた動画が鳴らない」は利用者から観測できるふるまいとも読めるが、句が述べているのは守りの置き場所(OpenAsync が状態を見て戻る)。REQ-095 は仕組みを M-BOM に委ねると明示している(10:L3714)→ 製造手段。
  観測できるふるまいの側(停止の後に音が鳴らない)が裁定層にあるかは、検索語「Stopped」「owning the sound」「stop … while loading」では当たらなかった(REQ-095 の「can be paused or stopped」まで)。
- **VIEW-PACK 5-3(H5)と 5-4**: どちらも「不正な pack は拒否」の一般則(20:L1047)に入るとも読める。5-4(両方の形を持つ)は入力の形の不正なので参照化。5-3 は、保存済みの同じデータなら「捨てて知らせる」と裁定されている状況で、pack では拒否を選ぶ**別の決め**なので人へ戻す。
- **PERSISTENCE 3-4**: MCP の引数を省いたときの既定は外から見える取り決めだが、「既存の定義の scope は編集で変わらない」(10:L3409〜3410)から読める → 参照化。

## 観察(分類の外・記録)

- **裁定層が M-BOM への委任を明文で持つ**: REQ-095(10:L3714〜3715)「THE MECHANISM IS NOT SAID HERE, as in REQ-093: the ended signal, the seek and the mute are implementation judgements recorded in the M-BOM」。ViewTube は、要求の側で「仕組みは M-BOM の判断」と書いている。
- **E-BOM の不変条件は一般的な 1 行**(E-PERSISTENCE-001「仕様で定義した識別子・状態遷移・境界を保持する。」)で、設計の内容は要求(10・3854 行)と仕様(20・1087 行)の本文にある。M の行が指す裁定層の所在は、42 句中 E-BOM が 1 句(H1 の近い文)だけで、残りは 10 と 20。
- **既見の腕で grep した 5 語**(起票前)は、いずれも本分類の所在と矛盾しなかった。
