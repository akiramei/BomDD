# BomDD-Plm ECO-009 r1 IA-01 是正の前後の突合(実在リポ 7 本・2 ゲート)

- 測定日: 2026-10-01・旧= BomDD-Plm b48a95d(製造 commit・作業を一時退避して実行)・新= 同 b48a95d の作業木(IA-01 の是正= ファイル名の右端からの候補定義の取り出し)
- 比較の単位は compare-real-repos.md と同じ(区分の欄を除いた所見と終了コード)。
- 読み: 増えたのは R-005(孤立定義の info)だけ — ファイル名から取り出した候補の定義が索引に入り、どこからも参照されていない分。error・warn と終了コードは全構成で不変。

| リポ-ゲート | exit 旧→新 | 区分以外の所見 | 新の区分の件数 | 新の measurement |
|---|---|---|---|---|
| BomDD-LibraryLending-Sample-acceptance.json | exit 1→1 | 差 0 件消失 / 5 件出現({'R-005:info': 5}) | {'MEASUREMENT_FAILURE': 45, '-': 63, 'RED': 50} | /CP/unreadable-input@always; /E/unreadable-input@always; /K/unreadable-input@always; R-011/E/unreadable-input@G3; R-014/CP/unreadable-input@freeze |
| BomDD-LibraryLending-Sample-always.json | exit 1→1 | 差 0 件消失 / 5 件出現({'R-005:info': 5}) | {'MEASUREMENT_FAILURE': 45, '-': 63, 'RED': 50} | /CP/unreadable-input@always; /E/unreadable-input@always; /K/unreadable-input@always; R-011/E/unreadable-input@G3; R-014/CP/unreadable-input@freeze |
| BomDD-Plm-acceptance.json | exit 0→0 | 同一 | {'-': 201} | — |
| BomDD-Plm-always.json | exit 0→0 | 同一 | {'-': 201} | — |
| BomDD-Transfer03-acceptance.json | exit 1→1 | 差 0 件消失 / 1 件出現({'R-005:info': 1}) | {'MEASUREMENT_FAILURE': 86, 'RED': 24, '-': 27} | /FMEA/selector-miss@always; /K/unreadable-input@always; /REQ/unreadable-input@always |
| BomDD-Transfer03-always.json | exit 1→1 | 差 0 件消失 / 1 件出現({'R-005:info': 1}) | {'MEASUREMENT_FAILURE': 86, 'RED': 24, '-': 27} | /FMEA/selector-miss@always; /K/unreadable-input@always; /REQ/unreadable-input@always |
| BomDD-UnitConv-Sample-acceptance.json | exit 1→1 | 同一 | {'MEASUREMENT_FAILURE': 99, 'RED': 219, '-': 109} | /CP/unreadable-input@always; /FMEA/unreadable-input@always; /K/unreadable-input@always; /REQ/unreadable-input@always; R-014/CP/unreadable-input@freeze |
| BomDD-UnitConv-Sample-always.json | exit 1→1 | 同一 | {'MEASUREMENT_FAILURE': 99, 'RED': 219, '-': 109} | /CP/unreadable-input@always; /FMEA/unreadable-input@always; /K/unreadable-input@always; /REQ/unreadable-input@always; R-014/CP/unreadable-input@freeze |
| TimetableAdv-acceptance.json | exit 1→1 | 同一 | {'RED': 4010, 'MEASUREMENT_FAILURE': 124, '-': 754} | /DE/empty-required-source@always; /FMEA/selector-miss@always; /ROUTE/selector-miss@always |
| TimetableAdv-always.json | exit 1→1 | 同一 | {'RED': 4010, 'MEASUREMENT_FAILURE': 124, '-': 754} | /DE/empty-required-source@always; /FMEA/selector-miss@always; /ROUTE/selector-miss@always |
| ViewPrism2-acceptance.json | exit 1→1 | 同一 | {'RED': 15, '-': 499, 'MEASUREMENT_FAILURE': 73} | — |
| ViewPrism2-always.json | exit 0→0 | 同一 | {'RED': 15, '-': 499, 'MEASUREMENT_FAILURE': 73} | — |
| ViewTube-acceptance.json | exit 1→1 | 同一 | {'RED': 575, '-': 124, 'MEASUREMENT_FAILURE': 13} | /CAPA/empty-required-source@always; /ECO/empty-required-source@always |
| ViewTube-always.json | exit 1→1 | 同一 | {'RED': 575, '-': 124, 'MEASUREMENT_FAILURE': 13} | /CAPA/empty-required-source@always; /ECO/empty-required-source@always |
