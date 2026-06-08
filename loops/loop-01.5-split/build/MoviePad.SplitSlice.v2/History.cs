namespace MoviePad.Services;

/// <summary>
/// undo/redo 履歴。参照型のスナップショットを保持する汎用スタック。
/// </summary>
/// <typeparam name="T">スナップショットの型(参照型)。</typeparam>
public sealed class History<T> where T : class
{
    private readonly int _max;
    // 末尾が最新。古い順に破棄するため List で先頭から落とす。
    private readonly List<T> _undo = new();
    private readonly List<T> _redo = new();

    /// <summary>
    /// 履歴を生成する。
    /// </summary>
    /// <param name="max">undo スタックに保持する最大件数。</param>
    public History(int max = 50)
    {
        _max = max < 0 ? 0 : max;
    }

    /// <summary>undo 可能か。</summary>
    public bool CanUndo => _undo.Count > 0;

    /// <summary>redo 可能か。</summary>
    public bool CanRedo => _redo.Count > 0;

    /// <summary>
    /// 現在状態 <paramref name="current"/> を undo スタックに積む。
    /// 上限超過は古い順に破棄。redo スタックはクリアする。
    /// </summary>
    public void Snapshot(T current)
    {
        _undo.Add(current);
        while (_undo.Count > _max)
        {
            _undo.RemoveAt(0);
        }
        _redo.Clear();
    }

    /// <summary>
    /// undo を実行。直前のスナップショットを <paramref name="previous"/> に返し、
    /// <paramref name="current"/> を redo スタックへ退避する。
    /// </summary>
    public bool TryUndo(T current, out T previous)
    {
        if (_undo.Count == 0)
        {
            previous = current;
            return false;
        }

        int last = _undo.Count - 1;
        previous = _undo[last];
        _undo.RemoveAt(last);
        _redo.Add(current);
        return true;
    }

    /// <summary>
    /// redo を実行。次のスナップショットを <paramref name="next"/> に返し、
    /// <paramref name="current"/> を undo スタックへ戻す。
    /// </summary>
    public bool TryRedo(T current, out T next)
    {
        if (_redo.Count == 0)
        {
            next = current;
            return false;
        }

        int last = _redo.Count - 1;
        next = _redo[last];
        _redo.RemoveAt(last);
        _undo.Add(current);
        return true;
    }

    /// <summary>履歴を全消去する。</summary>
    public void Clear()
    {
        _undo.Clear();
        _redo.Clear();
    }
}
