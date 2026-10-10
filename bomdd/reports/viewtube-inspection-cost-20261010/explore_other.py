"""探索(事前登録の外・README §6 逸脱 3): 分類 other の中身を、待ちの長い順に見る。読み取りだけ。
measure.py の scan と同じ重複除去を使う。"""
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import measure  # noqa: E402

sys.stdout.reconfigure(encoding='utf-8')
tdir = sys.argv[1]
since = sys.argv[2] if len(sys.argv) > 2 else measure.SINCE_DEFAULT
files = sorted(os.path.join(r, n) for r, _, ns in os.walk(tdir) for n in ns if n.endswith('.jsonl'))
acc = []
for p in files:
    measure.scan(p, since, acc)
other = [r for r in acc if r['cat'] == 'other' and r['tool'] != 'Monitor' and r['elapsed'] <= measure.HUMAN_WAIT_S]
buckets = collections.defaultdict(lambda: [0, 0.0])
for r in other:
    c = r['cmd']
    if re.search(r'until .*sleep|while .*sleep|Start-Sleep|\bsleep\b', c):
        k = 'poll_wait (until/sleep loops)'
    elif re.search(r'Remove-Item|rm -rf|worktree remove', c):
        k = 'cleanup (delete/worktree remove)'
    elif re.search(r'git worktree add|git stash|git checkout', c):
        k = 'worktree/checkout'
    elif re.search(r'\.ps1|\.sh\b|python\s+\S+\.py', c):
        k = 'script (other .ps1/.sh/.py)'
    elif re.search(r'\bgit\b', c):
        k = 'git (non-commit)'
    else:
        k = 'misc'
    buckets[k][0] += 1
    buckets[k][1] += r['elapsed']
for k, (n, s) in sorted(buckets.items(), key=lambda kv: -kv[1][1]):
    print(f'{k:<36} n={n:<5} min={s / 60:7.1f}')
print('\n-- other: 待ちの長い順 30 件 --')
for r in sorted(other, key=lambda r: -r['elapsed'])[:30]:
    print(f"{r['start'][:19]} {r['elapsed']:>5.0f}s {r['cmd'][:170].replace(chr(10), ' | ')}")
