using MoviePad.Models;
using MoviePad.Services;

namespace MoviePad.Slice;

/// <summary>
/// 分割編集の状態機械。<see cref="DocumentState"/> と再生ヘッド・選択・履歴を束ね、
/// Split/Undo/Redo を提供する。
/// </summary>
public sealed class SplitController
{
    private readonly History<DocumentState> _history = new();

    private DocumentState _state;
    private double _playhead;
    private int? _selectedId;

    // 永続的な単調増加カウンタ。Undo/Redo では巻き戻さない(AC-12)。
    private int _nextId;

    /// <summary>
    /// 初期状態と fps からコントローラを生成する。
    /// nextId は初期 State の全区間の最大 Id + 1 に初期化する。
    /// </summary>
    public SplitController(DocumentState initial, double fps)
    {
        _state = initial;
        Fps = fps;

        int maxId = 0;
        bool any = false;
        foreach (var r in initial.Regions)
        {
            if (!any || r.Id > maxId) maxId = r.Id;
            any = true;
        }
        _nextId = (any ? maxId : 0) + 1;

        // 初期選択を解決(直下区間→先頭区間)。
        _selectedId = _state.ResolveSelection(null, _playhead);
    }

    /// <summary>現在のドキュメント状態。</summary>
    public DocumentState State => _state;

    /// <summary>再生ヘッド位置(秒)。</summary>
    public double Playhead
    {
        get => _playhead;
        set => _playhead = value;
    }

    /// <summary>現在選択中の区間 Id。</summary>
    public int? SelectedId => _selectedId;

    /// <summary>フレームレート。</summary>
    public double Fps { get; }

    /// <summary>現在の再生ヘッドで分割可能か。</summary>
    public bool CanSplit => _state.CanSplitAt(TimeMath.SnapFrame(_playhead, Fps));

    /// <summary>undo 可能か。</summary>
    public bool CanUndo => _history.CanUndo;

    /// <summary>redo 可能か。</summary>
    public bool CanRedo => _history.CanRedo;

    /// <summary>
    /// 現在の再生ヘッドで分割を実行する。成功時、生成された後半(新 Id)区間を選択し、
    /// 履歴へ分割直前の状態を積む。!CanSplit のときは State も履歴も一切変化しない(AC-10)。
    /// </summary>
    public void Split()
    {
        if (!CanSplit) return;

        int newId = _nextId;
        var next = _state.SplitAt(_playhead, newId, Fps);
        if (next is null) return; // 念のため(CanSplit と整合)。

        _history.Snapshot(_state);
        _state = next;
        _selectedId = newId;      // 後半(新 Id)区間を選択(AC-9)。
        _nextId++;                // 払い出し後に前進(AC-12)。
    }

    /// <summary>
    /// 分割直前の状態へ復帰する。選択は <see cref="DocumentState.ResolveSelection"/> で再同期する。
    /// nextId は変更しない(AC-12)。
    /// </summary>
    public void Undo()
    {
        if (_history.TryUndo(_state, out var previous))
        {
            _state = previous;
            _selectedId = _state.ResolveSelection(_selectedId, _playhead);
        }
    }

    /// <summary>
    /// 直前に undo した分割を再適用する。選択は <see cref="DocumentState.ResolveSelection"/> で再同期する。
    /// nextId は変更しない(AC-12)。
    /// </summary>
    public void Redo()
    {
        if (_history.TryRedo(_state, out var next))
        {
            _state = next;
            _selectedId = _state.ResolveSelection(_selectedId, _playhead);
        }
    }
}
