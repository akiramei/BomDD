---
name: bomdd-ui-cad
description: モック受入検査 手順4: UI-IR 作成・CAD 化。決定的抽出→意味候補→裁定→UI-BOM の §12 パイプラインを実行する。/bomdd-mock-lint 合格まで治具が施錠(gate-cad が起動条件)。
---

# /bomdd-ui-cad — UI-IR 作成・CAD 化(モック受入検査 手順4)

正典: `{{METHOD}}/method/ui-ir-ui-bom.md` §12(工程分離)+
`{{METHOD}}/method/prompts/ui-raw-to-candidates.md`(第1段)+
`{{METHOD}}/method/prompts/ui-apply-rulings-to-bom.md`(第2段)。
治具: ui-mock-inspect.py(施錠)/ ui-extract.py(決定的抽出)/ ui-cad-gate.py(GU1–GU6)。

## 起動条件(最初に必ず実行)

```
python {{METHOD}}/method/tools/ui-mock-inspect.py gate-cad --dir bomdd/ui/<pkg>
```

**exit 1 なら停止**し、不足(refmodel 未決着 / lint 未合格)を伝えて該当スキルへ誘導する。
このチェックを飛ばして CAD 化を始めない(モック検査をすり抜けた欠陥は下流で高くつく — 実測: PR 手戻り)。

## 手順(§12 パイプライン)

1. **決定的抽出**: `python {{METHOD}}/method/tools/ui-extract.py <snapshot> -o ui-ir.raw.json`
   (runtime 描画モックは §12.1 の snapshot 治具を先に。`--verify` で id 揺れ検査)
2. **第1段(AI 意味候補)**: ui-raw-to-candidates.md に従い `ui-ir.json` を生成
   — raw に無いノード禁止・final 確定禁止・曖昧は未裁定質問へ。
3. **裁定/辞書解決**: 質問を人間へ。裁定は 37 台帳・辞書は 36(scope 拡大=裁定)。
4. **第2段(昇格)**: ui-apply-rulings-to-bom.md に従い `ui-bom.json`+`ui-trace-map.json` を生成
   — ruled のみ昇格。
5. **ゲート**: `python {{METHOD}}/method/tools/ui-cad-gate.py --mock <snapshot>` で GU1–GU6。
   exit 0 で E-BOM/M-BOM 昇格可。

## 規律

- 機械で決まる事実は AI に推測させない/AI は候補と質問のみ/最終事実は辞書ヒットか裁定のみ(§12)。
- blocking の open が残る限り昇格禁止(GU3)。status 更新漏れは GU3/GU4 が拾う。
- 失敗の還流は §14 の X1/X2/X3 経路へ。メガプロンプトへの知見追記は禁止。
