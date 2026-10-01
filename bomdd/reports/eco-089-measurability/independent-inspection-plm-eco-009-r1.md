独立検査を完了しました。判定は `REJECT IA-01` です。

報告書: [independent-inspection-ECO-009-r1.md](C:/Users/akira/AppData/Local/Temp/bomdd-ia-b0439b3337a340acb928a4229aff1115/independent-inspection-ECO-009-r1.md)

blocking 所見は、candidate filename 定義だけが存在する場合に定義が解決索引へ入らず、R-003 / MEASUREMENT_FAILURE が誤発火する問題です。これは比較基準にも存在する既存挙動ですが、対象 revision も正本の candidate fallback 意味論を満たしていません。

必須再現結果:

- build: 警告 0
- tests: 152/152 PASS
- 固定オラクル: 49/49 PASS
- self-hosting: exit 0、error/warn 0
- 旧個体較正: 15件中14件 FAIL、exit 1
- 開始・終了時の対象リポ: clean
- 検査中 commit: 0
- 製品リポへの変更: なし