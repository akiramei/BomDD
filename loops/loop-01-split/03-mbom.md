# ③ M-BOM — 区間分割(Split)スライス

E-BOM の論理部品を**製造単位(AIが生成・ビルド・検査できる成果物)**へ展開する。
技術スタックは原版固定。**この文書 + 工程([04-routing.md](04-routing.md))のみが製造装置への入力**(原版ソース非開示)。

## 製造単位

| 製造品コード | 成果物 | 対応E-BOM | 種別 |
|---|---|---|---|
| M-DOMAIN | C#ライブラリ `MoviePad.SplitSlice`(TimeMath.cs / RegionData.cs / DocumentState.cs) | EB-EDIT-DOC, EB-REGION, EB-SPLIT, EB-TIMEQ, EB-SELECT | generate |
| M-HISTORY | `History.cs`(汎用 undo/redo スタック) | EB-HISTORY | generate |
| M-CONTROLLER | `SplitController.cs`(UIフレームワーク非依存の分割統合) | EB-SPLIT-CMD, EB-IDGEN | generate |
| M-PROJ | `MoviePad.SplitSlice.csproj`(net10.0, nullable enable) | — | generate |

## 調達部品(procurement)
- `System.Collections.Immutable`(.NET 10 BCL 同梱。`ImmutableList<T>`)。
- 外部 NuGet 不要。**MVVM フレームワーク(CommunityToolkit.Mvvm)はこのスライスでは使わない** —
  プロパティ変更通知/コマンドの UI バインドは Loop1 の客観検査外(UI 関心、C4)。統合ロジックは素の POCO として製造し検査可能にする。

## 実行環境(M-BOM 技術選定)
- ターゲット: `net10.0`、言語 C# 13、`<Nullable>enable</Nullable>`、`<ImplicitUsings>enable</ImplicitUsings>`。
- OS 非依存(純粋ロジック。LibVLC/ffmpeg/Avalonia には依存しない)。

## 公開インターフェース契約(製造装置はこの形を厳守)
> 契約はBOMの「接続面」。実装本体(アルゴリズム)は受入基準から導出すること。原版実装は与えない。

```csharp
namespace MoviePad.Models;

public static class TimeMath {
    public const double MinLen = 0.5;
    public const double DefaultFps = 30.0;
    public static double Clamp(double v, double a, double b);
    public static double SnapFrame(double t, double fps);   // fps<=0 は DefaultFps を使う
}

public sealed record RegionData(int Id, double Start, double End, double Speed,
                                bool PreservePitch, bool Excluded = false, double Volume = 1.0) {
    public double Duration { get; }          // End - Start
}

public sealed record DocumentState(double TrimStart, double TrimEnd,
                                   System.Collections.Immutable.ImmutableList<RegionData> Regions) {
    public static DocumentState ForClip(double duration, int firstId = 1);
    public RegionData? RegionAt(double t);
    public RegionData? FindById(int id);
    public int IndexOfId(int id);
    public bool CanSplitAt(double playhead);
    public DocumentState? SplitAt(double playhead, int newId, double fps);
    public int? ResolveSelection(int? current, double playhead);
}
```
```csharp
namespace MoviePad.Services;
public sealed class History<T> where T : class {
    public History(int max = 50);
    public bool CanUndo { get; }
    public bool CanRedo { get; }
    public void Snapshot(T current);                 // 上限超過は古い順に破棄、redoはクリア
    public bool TryUndo(T current, out T previous);
    public bool TryRedo(T current, out T next);
    public void Clear();
}
```
```csharp
namespace MoviePad.Slice;
public sealed class SplitController {
    public SplitController(DocumentState initial, double fps);
    public DocumentState State { get; }
    public double Playhead { get; set; }
    public int? SelectedId { get; }
    public double Fps { get; }
    public bool CanSplit { get; }                    // State.CanSplitAt(Playhead)
    public bool CanUndo { get; }
    public bool CanRedo { get; }
    public void Split();
    public void Undo();
    public void Redo();
}
```

## 受入基準(behavioral — 製造装置はこれを満たす実装を導く。検査は隠しオラクルで別途)
**ドメイン不変条件**
- 区間は隙間なく順序付き(`region[i].End == region[i+1].Start`)。record は不変、全操作が新インスタンスを返す。
- 時刻は半開区間 [Start,End)。**境界時刻は後続区間に属し、最終区間のみ終端を含む**。

| AC | 受入条件 | 由来REQ |
|---|---|---|
| AC-1 | `ForClip(d)` は trim=[0,d]、1区間[0,d] speed=1 pitch=true | REQ-SPLIT-8 |
| AC-2 | `RegionAt`: 境界→後続、最終区間は終端含む、trim外は null | 前提制約 |
| AC-3 | `SplitAt` 有効内点: 区間数+1、左=[start,ph]、右=[ph,end] に新ID、右が speed/pitch/**volume** 継承 | REQ-SPLIT-1,4 |
| AC-4 | `SplitAt` が端から MinLen 以内 / 区間外 / trim外 → `null`(無変化) | REQ-SPLIT-5 |
| AC-5 | `SplitAt` は分割前に playhead を `SnapFrame` する | REQ-SPLIT-6 |
| AC-6 | `SplitAt` 後も元 `DocumentState` は不変 | REQ-SPLIT-8 |
| AC-7 | `CanSplitAt`: 直下区間が在り `Start+MinLen < ph < End-MinLen` のときだけ真 | REQ-SPLIT-5 |
| AC-8 | `ResolveSelection`: 直下が在ればそのID/無ければcurrent生存なら維持/それも無効なら先頭 | REQ-SPLIT-3 |
| AC-9 | Controller `Split()` 成功時: 後半の新IDが `SelectedId`、`CanUndo` 真、区間数+1 | REQ-SPLIT-1,3,7 |
| AC-10 | Controller `Split()` 失敗時(`!CanSplit`): State 不変・履歴に積まない | REQ-SPLIT-5,7 |
| AC-11 | Controller `Undo()` で分割前へ復帰し選択再解決、`Redo()` で再適用 | REQ-SPLIT-7 |
| AC-12 | 新IDは既存最大ID+1から単調増加(初期化時も最大+1) | NFR-SPLIT-2 |

## 非機能(NFR)
- NFR-SPLIT-1: 分割は不変リストの O(n) コピー、副作用なし(同期・即時)。
- NFR-SPLIT-2: ID 衝突なし(AC-12)。

## 曖昧点の解決
- **U1(履歴)**: 上限50・古い順破棄・新規 Snapshot で redo クリア(`History<T>` 契約に反映済み)。
- **U2(ツールバー活性同期)**: UI バインド関心。Loop1 客観検査外。`CanSplit` の公開のみ製造する。→ C4 候補。
- **U3(テキスト入力中は S 無効)**: View 層(`FocusManager`)責務=EB-KEYMAP。Loop1 では製造・検査せず不足記録。→ C4 候補。
