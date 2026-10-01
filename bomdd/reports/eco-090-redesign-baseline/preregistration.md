# M-BOM / CP 再設計 — 基準計数の事前登録(2026-10-01・実行前に記入)

読み取りのみ・7 リポ・各 1 回・HEAD の作業木(dirty は dirty のまま)。字面と YAML 構造だけを見る(意味は読まない)。
解析できないファイルは「測定不能(読めない)」と記録し、0 件として数えない。

重み付け(user 指示 2026-10-01): 一般的なアプリに近い = ViewPrism2・ViewTube(主の根拠)。
TimetableAdv = ゲーム(別枠)。Plm = 開発ツール。LibraryLending・Transfer03・UnitConv = 小さなサンプル(参考)。

## 項目と定義

M1 M-BOM が設計の中身を持つか
- M unit の `invariants` 各行を 3 分類: 参照のみ(行が INV-NNN だけ)/ ID+本文 / 本文のみ(ID なし)。
- 写し判定: M unit の invariants 行の本文(空白正規化)が、その unit の ebom_refs 先の E 品目の invariants 行と完全一致 → 写し。
- `display_contract` を持つ M unit の数(テンプレートは E からの転記を指示)。
- 仮説: 主の 2 本で「本文のみ」または「ID+本文」が多数(= 参照でなく内容を持つ)。完全一致の写しは少ない(言い換えて持つ)。

M2 FMEA の置き場所: 32 のトップ `fmea` / 33 の `control_plan.fmea` / 両方 / なし。件数つき。

M3 CP 行の「いつ測るか」「落ちたら何をするか」
- CP 行のキーで判定。いつ= gate|station|sampling|when|frequency|quality_gate を含むキー。処置= stop_condition|reaction|on_fail|on_red を含むキー。
- 別ファイルでの代替も記録: 34-routing の工程にある gate / quality_gate / hold_points、33 の station_gates。
- 仮説: CP 行に処置の欄を持つリポは 0〜1 本。

M4 不変条件がどの層の検査行へ届くか
- INV の定義= ECO-086 と同じ(20-spec.md の表の先頭列)。
- CP 行の層= その行に結びつく M unit の数。結びつき= CP 行の verifies に現れる M-* ∪ M unit の acceptance_refs に CP 行 ID がある unit。
  0 = 単位に結びつかない(要求直結)/ 1 = 単位 / 2 以上 = 単位をまたぐ。
- 各 INV について、その ID を字面で含む CP 行の層を数える。
- 仮説: 届く INV は少なく(ECO-086 と同じ 0〜3 割)、届く先は「単位」の行が多い。

M5 単位ごとの参照数(文脈面積の代理)
- 参照数= len(ebom_refs)+len(kbom_refs)+len(depends_on)+interface_contract のキー数(dict のとき)/行数(list のとき)。
- 各リポで中央値・最大・最大の unit ID。
- 仮説なし(基準線として採るだけ)。

M6 単位間の接続に検査行があるか
- 接続= M unit の depends_on にある M-* の組。
- 被覆= 両端の unit の両方に結びつく CP 行(M4 の結びつき)が 1 本以上ある。
- 仮説: 被覆率は低い(単位をまたぐ行が少ない)。

## 読み方(先に決める)
- 測定不能は 0 と書かない。リポ単位で「読めない」と記す。
- 主の根拠は ViewPrism2・ViewTube。2 本で向きが揃わなければ「揃わない」と書き、他のリポで補わない。
- 字面の一致は検査の実態ではない(届く ≠ 検査されている)。
