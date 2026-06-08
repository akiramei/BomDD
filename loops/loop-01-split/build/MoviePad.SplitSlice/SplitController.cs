using MoviePad.Models;
using MoviePad.Services;

namespace MoviePad.Slice;

/// <summary>
/// Drives split editing over a <see cref="DocumentState"/>, tracking the playhead,
/// the current selection, and an undo/redo history. All state transitions go through
/// immutable <see cref="DocumentState"/> instances.
/// </summary>
public sealed class SplitController
{
    private readonly History<DocumentState> _history = new();
    private DocumentState _state;
    private int _nextId;

    /// <summary>
    /// Initializes the controller from an existing state. The next Id is seeded to
    /// (max existing region Id) + 1; the playhead starts at 0 and the selection is
    /// resolved against that playhead.
    /// </summary>
    public SplitController(DocumentState initial, double fps)
    {
        _state = initial;
        Fps = fps;
        _nextId = ComputeNextId(initial);
        Playhead = 0.0;
        SelectedId = _state.ResolveSelection(null, Playhead);
    }

    /// <summary>The current immutable document state.</summary>
    public DocumentState State => _state;

    /// <summary>The current playhead time in seconds.</summary>
    public double Playhead { get; set; }

    /// <summary>The currently selected region Id, or null.</summary>
    public int? SelectedId { get; private set; }

    /// <summary>Frames-per-second used when snapping split points.</summary>
    public double Fps { get; }

    /// <summary>Mirrors <see cref="DocumentState.CanSplitAt"/> at the current playhead.</summary>
    public bool CanSplit => _state.CanSplitAt(Playhead);

    /// <summary>True when an undo step is available.</summary>
    public bool CanUndo => _history.CanUndo;

    /// <summary>True when a redo step is available.</summary>
    public bool CanRedo => _history.CanRedo;

    /// <summary>
    /// Splits the region under the playhead. On success the newly created (right)
    /// region becomes the selection and the prior state is pushed onto the undo history.
    /// When the split is not possible, nothing changes.
    /// </summary>
    public void Split()
    {
        if (!CanSplit)
            return;

        int newId = _nextId;
        var next = _state.SplitAt(Playhead, newId, Fps);
        if (next is null)
            return;

        _history.Snapshot(_state);
        _state = next;
        _nextId++;                 // 単調増加: Undo を挟んでも巻き戻さない(原版準拠 / NFR-SPLIT-2)。CHEAT-004
        SelectedId = newId;
    }

    /// <summary>
    /// Reverts to the state before the most recent split, re-syncing the selection.
    /// </summary>
    public void Undo()
    {
        if (_history.TryUndo(_state, out var previous))
        {
            _state = previous;
            SelectedId = _state.ResolveSelection(SelectedId, Playhead);
        }
    }

    /// <summary>
    /// Re-applies the most recently undone split, re-syncing the selection.
    /// </summary>
    public void Redo()
    {
        if (_history.TryRedo(_state, out var next))
        {
            _state = next;
            SelectedId = _state.ResolveSelection(SelectedId, Playhead);
        }
    }

    private static int ComputeNextId(DocumentState state)
    {
        int max = 0;
        foreach (var r in state.Regions)
        {
            if (r.Id > max)
                max = r.Id;
        }
        return max + 1;
    }
}
