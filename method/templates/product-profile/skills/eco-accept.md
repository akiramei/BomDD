---
name: eco-accept
description: golden 合格後の ECO クローズ。クローズ 3 点セット(検査観点明記=再発防止・register applied 化+golden 承認記録・ECO 本文クローズ節+教訓)→必要なら台帳同期(M4)→accept コミット→完了報告まで行う。golden 合格の報告を受けてから使う。
---

# /eco-accept — golden 合格後のクローズ 3 点セット

典拠: [bomdd/change-management.md](../../../bomdd/change-management.md) §3.3/§4。
引数: ECO 番号+golden 結果(合格/所見)。

## 前提確認

- fix コミット済みで register が「golden 待ち」であること。
- **golden 不合格(所見あり)の場合はこのスキルを使わない**: 所見を GF-* として ECO 本文へ
  記録し、/eco-fix(同一欠陥)か /eco-file(別欠陥の分離起票 — R3)へ。

## 手順(クローズ 3 点セット)

1. **受入証拠と再発防止の記録**: 該当golden CPをsurfaceのacceptance_refsから特定する。
   固定製造証拠へは書き戻さない。独立append-only受入証拠レイヤーを導入済みの製品では、
   `{{METHOD}}/method/acceptance-evidence.md`と製品の適用プロファイルに従って記録する。
   対象CPの固定版・candidate・passed attempt/verdictへ束縛し、今回の観点を**潜伏実績つきで**残す。
   訂正も新記録とし、旧記録を編集・削除しない。CPの拡張・合成、製造条件の上書きは行わない。
   必須読取検査を通し、受入前とapplied遷移で同じ固定記録集合を確認する。
   未導入の場合、従来のCP.characteristic追記は製造証拠の固定を破らない場合に限る。
   固定を破る場合や新層の検査器が未配備の場合は停止し、導入ECOまたは通常の新製造版へ戻す。
   過去の受入記録を新形式に書き換えず、既存検査・golden・receiptの要件を免除しない。
2. **register 更新**: `status: applied`+承認記録(日付・approver・確認内容)。
   golden フィールドを `approved(<日付> <承認者> 実機: <確認内容>)` に書き換える。
3. **ECO 本文クローズ節**: タイトルの (staged)→(applied)、クローズ節に
   実機確認内容・再発防止・**教訓**(一般化できる形で 1 段落。既存教訓との関係=read-across を明記)。
4. **台帳同期(M4)の要否判定**: 仕様・E-BOM・M-BOM に as-built 乖離が生じた ECO
   (surface 新設・挙動仕様変更)は同期まで行う。内部欠陥是正のみなら不要。
5. **検証+コミット**: 台帳整合検査 → `accept(eco-NNN): golden 合格 — <要約>`。
6. **残課題の再掲**: ECO 中に R3 で送付したスコープ外事項があれば完了報告に再掲する。

## 完了報告

コミットハッシュ(起票/fix/accept)・機械受入サマリ・再発防止の場所・教訓・
残った後続事項を 1 つの報告にまとめる。

## 教訓の昇格

教訓がプロダクト固有でなく一般形(方法論レベル)なら、方法論リポ(`{{METHOD}}`)への
昇格候補として完了報告に明記する(昇格自体は方法論側の変更 = 別リポ・別オーダー)。
