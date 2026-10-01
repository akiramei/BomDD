# M-BOM / CP 再設計 — 基準計数(2026-10-01)

定義と読み方は preregistration.md(実行前に固定)。字面と YAML 構造のみ。届く ≠ 検査されている。

| リポ | 区分 | HEAD | 作業木 | 30 | 32 | 33 | 34 | M unit | CP 行 |
|---|---|---|---|---|---|---|---|---|---|
| ViewPrism2 | 主 | e8edbbb | clean | ok | ok | ok | ok | 44 | 65 |
| ViewTube | 主 | 6917d6c9 | dirty(4) | ok | ok | ok | ok | 12 | 41 |
| BomDD-Plm | ツール | 0d98371 | clean | ok | ok | ok | ok | 16 | 21 |
| TimetableAdv | ゲーム | 73b79d47 | dirty(2149) | ok | ok | ok | ok | 48 | 471 |
| BomDD-LibraryLending-Sample | サンプル | f7bfc24 | clean | 読めない(ScannerError) | ok | 読めない(ScannerError) | ok | 3 | 0 |
| BomDD-Transfer03 | サンプル | (git なし) | - | ok | ok | ok | ok | 4 | 10 |
| BomDD-UnitConv-Sample | サンプル | bb6c090 | clean | ok | ok | 読めない(ScannerError) | ok | 2 | 0 |

## M1 M-BOM が設計の中身を持つか

| リポ | invariants を持つ unit | 参照のみ | ID+本文 | 本文のみ | E 品目と完全一致(写し) | display_contract を持つ unit |
|---|---|---|---|---|---|---|
| ViewPrism2 | 22/44 | 0 | 16 | 53 | 1 | 0 |
| ViewTube | 12/12 | 0 | 0 | 90 | 0 | 12 |
| BomDD-Plm | 6/16 | 9 | 0 | 4 | 0 | 1 |
| TimetableAdv | 44/48 | 0 | 0 | 83 | 70 | 1 |
| BomDD-LibraryLending-Sample | 2/3 | 0 | 0 | 5 | 測定不能(30 読めない(ScannerError)) | 0 |
| BomDD-Transfer03 | 4/4 | 9 | 0 | 6 | 4 | 4 |
| BomDD-UnitConv-Sample | 1/2 | 0 | 1 | 1 | 0 | 1 |

## M2 FMEA の置き場所

| リポ | 32 の fmea | 33 の control_plan.fmea |
|---|---|---|
| ViewPrism2 | 41 | 0 |
| ViewTube | 12 | 0 |
| BomDD-Plm | 0 | 10 |
| TimetableAdv | 72 | 0 |
| BomDD-LibraryLending-Sample | 6 | 読めない(ScannerError) |
| BomDD-Transfer03 | 10 | 0 |
| BomDD-UnitConv-Sample | 7 | 読めない(ScannerError) |

## M3 CP 行の「いつ測るか」「落ちたら何をするか」

**計器の点検(実行後)**: キー名の一致で数えたため、意味が違うキーも拾う。ViewTube の `sampling` は「何件測るか」(例 all fixed cases)で「いつ」ではなく、`stop_condition` は「何を不合格とするか」(例 any mismatch, unobserved required field/state, or fixture failure)で「落ちたら何をするか」ではない。下表の ViewTube 41/41 はこの読み替えを前提に読む。

| リポ | いつ の欄を持つ行 | 処置 の欄を持つ行 | 使われたキー | 別ファイル・別節の代替 |
|---|---|---|---|---|
| ViewPrism2 | 0/65 | 0/65 | - | 33:part_kind_gates(1)×1, 34:routing_eco022.gate_g3_dryrun×1, 34:routing_v2.gate_g3_dryrun×1, 34:routing_v3.gate_g3_dryrun×1, 34:routing_v4.gate_g3_dryrun×1 |
| ViewTube | 41/41 | 41/41 | sampling, stop_condition | 34:routing.hold_points×1, 34:routing.steps.quality_gate×18 |
| BomDD-Plm | 0/21 | 0/21 | - | 34:routing.steps.gate×1 |
| TimetableAdv | 0/471 | 0/471 | - | 33:station_gate_semantics(1)×1, 33:station_gates(11)×1, 34:routing.stations×1, 34:routing.unit_routes.stations×47 |
| BomDD-LibraryLending-Sample | 測定不能(33 読めない(ScannerError)) | 測定不能 | - | - |
| BomDD-Transfer03 | 0/10 | 0/10 | - | 34:routing.steps.gate×1 |
| BomDD-UnitConv-Sample | 測定不能(33 読めない(ScannerError)) | 測定不能 | - | 34:routing.steps.gate×1 |

## CP 行の層(結びつく M unit の数)

| リポ | 要求直結(0) | 単位(1) | またぐ(2+) | またぐ(治具の unit を除く・事後の感度確認) |
|---|---|---|---|---|
| ViewPrism2 | 16 | 41 | 8 | 8 |
| ViewTube | 13 | 4 | 24 | 13 |
| BomDD-Plm | 4 | 17 | 0 | 0 |
| TimetableAdv | 111 | 339 | 21 | 16 |
| BomDD-LibraryLending-Sample | 測定不能(33 読めない(ScannerError)) | - | - | - |
| BomDD-Transfer03 | 0 | 5 | 5 | 5 |
| BomDD-UnitConv-Sample | 測定不能(33 読めない(ScannerError)) | - | - | - |

## M4 不変条件がどの層の検査行へ届くか(INV 単位・1 つの INV が複数層に届けば各層で数える)

| リポ | 仕様の INV | 届かない | 要求直結(0) | 単位(1) | またぐ(2+) |
|---|---|---|---|---|---|
| ViewPrism2 | 15 | 12 | 2 | 1 | 2 |
| ViewTube | 17 | 17 | 0 | 0 | 0 |
| BomDD-Plm | 10 | 9 | 0 | 1 | 0 |
| TimetableAdv | 0 | INV 定義なし | - | - | - |
| BomDD-LibraryLending-Sample | 0 | INV 定義なし | - | - | - |
| BomDD-Transfer03 | 8 | 8 | 0 | 0 | 0 |
| BomDD-UnitConv-Sample | 7 | CP 読めない(ScannerError) | - | - | - |

## M5 単位ごとの参照数(E 参照+K 参照+依存+インターフェース契約の項目数)

| リポ | 中央値 | 最大 | 最大の unit |
|---|---|---|---|
| ViewPrism2 | 5.0 | 14 | M-UI-018 |
| ViewTube | 8.0 | 15 | M-VIEW-PACK-001 |
| BomDD-Plm | 5.5 | 15 | M-VIEWER-UI-007 |
| TimetableAdv | 11.0 | 41 | M-UI-INTERACTION-EPISODE-SHELL-001 |
| BomDD-LibraryLending-Sample | 7 | 12 | M-API-SQLITE-001 |
| BomDD-Transfer03 | 9.5 | 11 | M-DOMAIN-001 |
| BomDD-UnitConv-Sample | 5.0 | 8 | M-CORE-001 |

## M6 単位間の接続(depends_on)に、両端に結びつく検査行があるか

| リポ | depends_on を持つ unit | 接続 | 両端を検査する行がある接続 |
|---|---|---|---|
| ViewPrism2 | 0/44 | 0 | 測定不能(M unit に depends_on の欄が無い) |
| ViewTube | 2/12 | 11 | 0/11 |
| BomDD-Plm | 10/16 | 29 | 0/29 |
| TimetableAdv | 27/48 | 81 | 16/81 |
| BomDD-LibraryLending-Sample | 0/3 | 0 | CP 読めない(ScannerError) |
| BomDD-Transfer03 | 3/4 | 4 | 3/4 |
| BomDD-UnitConv-Sample | 1/2 | 1 | CP 読めない(ScannerError) |
