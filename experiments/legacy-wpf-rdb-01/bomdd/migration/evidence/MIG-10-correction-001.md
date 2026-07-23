# MIG-10 Post-Accept Correction 001

Date: 2026-07-19  
Owner: Migration Owner / UI Approver

## Observation

当時 `OBS-UI-003-timesheet-calendar.png` と呼んでいた画像はカレンダーの固定高さ scroll region の上部だけを示し、11:46 の event 自体は viewport 外だった。取得時の accessible DOM には `project:experiment START` が存在したが、その証跡ファイルが保存されていなかった。IMP-006 で実体が JPEG と判明し、`.jpg` へ訂正した。

## Correction

- `evidence/current-ui/OBS-UI-003-calendar-dom.txt` を追加した。
- `current-observation-index.md` は、PNG を layout evidence、DOM extract を event-presence evidence として区別した。
- `current-baseline.md` の表現を同じ区別へ修正した。

## Boundary and decision

- product、fixture、schema、screenshot bytes は変更していない。
- accepted artifact の根拠を弱める誤記だったため、正確性を優先して correction と再 Gate check を残す。
- Classification: evidence clarification; no product difference and no blocker after correction.
