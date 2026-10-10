"""探索(事前登録の外・README §6 逸脱 3): 撮影の全計画の門が止めた呼び出しの出力を読む。読み取りだけ。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import measure  # noqa: E402

sys.stdout.reconfigure(encoding='utf-8')
tdir = sys.argv[1]
files = sorted(os.path.join(r, n) for r, _, ns in os.walk(tdir) for n in ns if n.endswith('.jsonl'))
acc = []
for p in files:
    measure.scan(p, measure.SINCE_DEFAULT, acc)
for r in acc:
    if 'a capture plan does not run to its end' in r['out']:
        print('=' * 20, r['start'], round(r['elapsed']), 's', r['file'][-60:])
        print('CMD:', r['cmd'][:300].replace('\n', ' | '))
        print(r['out'][-2500:])
