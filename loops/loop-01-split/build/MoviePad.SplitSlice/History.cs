namespace MoviePad.Services;

/// <summary>
/// A bounded undo/redo history of reference-typed snapshots.
/// </summary>
public sealed class History<T> where T : class
{
    private readonly int _max;
    private readonly LinkedList<T> _undo = new();
    private readonly Stack<T> _redo = new();

    /// <summary>Creates a history that retains at most <paramref name="max"/> undo snapshots.</summary>
    public History(int max = 50)
    {
        _max = max < 1 ? 1 : max;
    }

    /// <summary>True when there is at least one snapshot to undo to.</summary>
    public bool CanUndo => _undo.Count > 0;

    /// <summary>True when there is at least one snapshot to redo to.</summary>
    public bool CanRedo => _redo.Count > 0;

    /// <summary>
    /// Records <paramref name="current"/> as the latest undo point.
    /// Oldest entries beyond the cap are discarded; the redo stack is cleared.
    /// </summary>
    public void Snapshot(T current)
    {
        _undo.AddLast(current);
        while (_undo.Count > _max)
        {
            _undo.RemoveFirst();
        }
        _redo.Clear();
    }

    /// <summary>
    /// Moves one step back: pushes <paramref name="current"/> onto the redo stack and
    /// yields the previous snapshot. Returns false when there is nothing to undo.
    /// </summary>
    public bool TryUndo(T current, out T previous)
    {
        if (_undo.Count == 0)
        {
            previous = current;
            return false;
        }

        previous = _undo.Last!.Value;
        _undo.RemoveLast();
        _redo.Push(current);
        return true;
    }

    /// <summary>
    /// Moves one step forward: pushes <paramref name="current"/> onto the undo history and
    /// yields the next snapshot. Returns false when there is nothing to redo.
    /// </summary>
    public bool TryRedo(T current, out T next)
    {
        if (_redo.Count == 0)
        {
            next = current;
            return false;
        }

        next = _redo.Pop();
        _undo.AddLast(current);
        while (_undo.Count > _max)
        {
            _undo.RemoveFirst();
        }
        return true;
    }

    /// <summary>Drops all undo and redo state.</summary>
    public void Clear()
    {
        _undo.Clear();
        _redo.Clear();
    }
}
