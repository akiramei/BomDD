# BomDD-Plm ECO-009 の変更前後の突合(実在リポ 7 本・2 ゲート)

- 測定日: 2026-10-01・旧= BomDD-Plm 7c1e157(作業を一時退避して実行)・新= 同 7c1e157 の作業木(ECO-009 の実装・X-GIT 修正前の build — 本突合は --eco なしのため X-GIT の所見を含まない)
- 比較の単位= 所見の (rule, severity, gate, file, line, targetId, message) と終了コード。outcome・measurement・stats.outcomes・schemaVersion は新しい版で足した欄として比較から外し、新の件数を別に示す。
- 測定スクリプト= compare-real-repos.py。限界= 1 時点・各 1 回。TimetableAdv と ViewTube の作業木は dirty。新の測定不能(連鎖)の帰属が正しいかは人の確認が要る(ECO-009 §1A.4 未収束事項 ⑤)。

| リポ-ゲート | exit 旧→新 | 区分以外の所見 | 新の区分の件数 | 新の measurement |
|---|---|---|---|---|
| BomDD-LibraryLending-Sample-acceptance.json | exit 1→1 | 同一 | {'MEASUREMENT_FAILURE': 45, '-': 58, 'RED': 50} | /CP/unreadable-input@always; /E/unreadable-input@always; /K/unreadable-input@always; R-011/E/unreadable-input@G3; R-014/CP/unreadable-input@freeze |
| BomDD-LibraryLending-Sample-always.json | exit 1→1 | 同一 | {'MEASUREMENT_FAILURE': 45, '-': 58, 'RED': 50} | /CP/unreadable-input@always; /E/unreadable-input@always; /K/unreadable-input@always; R-011/E/unreadable-input@G3; R-014/CP/unreadable-input@freeze |
| BomDD-Plm-acceptance.json | exit 0→0 | 同一 | {'-': 201} | — |
| BomDD-Plm-always.json | exit 0→0 | 同一 | {'-': 201} | — |
| BomDD-Transfer03-acceptance.json | exit 1→1 | 同一 | {'MEASUREMENT_FAILURE': 86, 'RED': 24, '-': 26} | /FMEA/selector-miss@always; /K/unreadable-input@always; /REQ/unreadable-input@always |
| BomDD-Transfer03-always.json | exit 1→1 | 同一 | {'MEASUREMENT_FAILURE': 86, 'RED': 24, '-': 26} | /FMEA/selector-miss@always; /K/unreadable-input@always; /REQ/unreadable-input@always |
| BomDD-UnitConv-Sample-acceptance.json | exit 1→1 | 同一 | {'MEASUREMENT_FAILURE': 99, 'RED': 219, '-': 109} | /CP/unreadable-input@always; /FMEA/unreadable-input@always; /K/unreadable-input@always; /REQ/unreadable-input@always; R-014/CP/unreadable-input@freeze |
| BomDD-UnitConv-Sample-always.json | exit 1→1 | 同一 | {'MEASUREMENT_FAILURE': 99, 'RED': 219, '-': 109} | /CP/unreadable-input@always; /FMEA/unreadable-input@always; /K/unreadable-input@always; /REQ/unreadable-input@always; R-014/CP/unreadable-input@freeze |
| TimetableAdv-acceptance.json | exit 1→1 | 同一 | {'RED': 4010, 'MEASUREMENT_FAILURE': 124, '-': 754} | /DE/empty-required-source@always; /FMEA/selector-miss@always; /ROUTE/selector-miss@always |
| TimetableAdv-always.json | exit 1→1 | 同一 | {'RED': 4010, 'MEASUREMENT_FAILURE': 124, '-': 754} | /DE/empty-required-source@always; /FMEA/selector-miss@always; /ROUTE/selector-miss@always |
| ViewPrism2-acceptance.json | exit 1→1 | 同一 | {'RED': 15, '-': 499, 'MEASUREMENT_FAILURE': 73} | — |
| ViewPrism2-always.json | exit 0→0 | 同一 | {'RED': 15, '-': 499, 'MEASUREMENT_FAILURE': 73} | — |
| ViewTube-acceptance.json | exit 1→1 | 同一 | {'RED': 575, '-': 124, 'MEASUREMENT_FAILURE': 13} | /CAPA/empty-required-source@always; /ECO/empty-required-source@always |
| ViewTube-always.json | exit 1→1 | 同一 | {'RED': 575, '-': 124, 'MEASUREMENT_FAILURE': 13} | /CAPA/empty-required-source@always; /ECO/empty-required-source@always |
