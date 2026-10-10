"""ViewTube の検査の時間の実測(README.md の事前登録どおり)。読み取りだけ。

使い方: python measure.py <transcripts_dir> <acceptance_runs_dir> [since_iso]
出力は標準出力(呼び出し側が measure-output.txt に保存する)。
"""
import collections
import datetime
import json
import os
import re
import sys

SINCE_DEFAULT = '2026-10-07T00:00:00Z'
HUMAN_WAIT_S = 3600

RULES = [
    ('commit', re.compile(r'\bgit\s+(?:-c\s+\S+\s+)*commit\b')),
    ('supervised', re.compile(r'run-supervised-tests')),
    ('sweep', re.compile(r'sweep-capture-plans')),
    ('capture', re.compile(r'CaptureHarness|capture\d+|all-plans|tiers\d+|--plan\b', re.I)),
    ('mutation', re.compile(r'mutat', re.I)),
    ('targeted_test', re.compile(r'dotnet\s+test|run-class|--filter')),
    ('validate', re.compile(r'validate_\w+\.py|selftest_')),
    ('build', re.compile(r'dotnet\s+build')),
]
SWEEP_YES = 'capture-plan sweep: a path that can strand a plan is staged'
SWEEP_NO = 'capture-plan sweep: no path'
BLOCKED = 'commit blocked'
# 逸脱 1(数えた後に追加・README §6): 再開・分岐したセッションのファイルが同じ呼び出しを重複して持つため、
# tool_use の id で 1 回だけ数える。最初に読んだファイル(パスの辞書順)の側に帰属させる。
SEEN = set()
REPO = os.environ.get('VIEWTUBE_REPO') or (sys.argv[4] if len(sys.argv) > 4 else None)


def ts(s):
    return datetime.datetime.fromisoformat(s.replace('Z', '+00:00'))


def classify(text):
    for name, rx in RULES:
        if rx.search(text):
            return name
    return 'other'


def result_text(c):
    v = c.get('content')
    if isinstance(v, str):
        return v
    if isinstance(v, list):
        return '\n'.join(x.get('text', '') for x in v if isinstance(x, dict))
    return ''


def scan(path, since, acc):
    uses = {}
    with open(path, encoding='utf-8') as f:
        for line in f:
            try:
                o = json.loads(line)
            except Exception:
                continue
            t = o.get('timestamp')
            if not t or t < since:
                continue
            msg = o.get('message')
            content = msg.get('content') if isinstance(msg, dict) else None
            if not isinstance(content, list):
                continue
            for c in content:
                if not isinstance(c, dict):
                    continue
                if c.get('type') == 'tool_use' and c.get('name') in ('Bash', 'PowerShell', 'Monitor'):
                    uses[c['id']] = (t, c.get('name'), c.get('input') or {})
                elif c.get('type') == 'tool_result' and c.get('tool_use_id') in uses:
                    if c['tool_use_id'] in SEEN:
                        uses.pop(c['tool_use_id'])
                        continue
                    SEEN.add(c['tool_use_id'])
                    t0, name, inp = uses.pop(c['tool_use_id'])
                    el = (ts(t) - ts(t0)).total_seconds()
                    text = inp.get('command') or json.dumps(inp, ensure_ascii=False)
                    out = result_text(c)
                    acc.append({
                        'file': path, 'start': t0, 'elapsed': el, 'tool': name,
                        'bg': bool(inp.get('run_in_background')),
                        'cat': classify(text), 'cmd': text, 'out': out,
                    })


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    tdir, rdir = sys.argv[1], sys.argv[2]
    since = sys.argv[3] if len(sys.argv) > 3 else SINCE_DEFAULT
    files = []
    for root, _, names in os.walk(tdir):
        for n in names:
            if n.endswith('.jsonl'):
                files.append(os.path.join(root, n))
    acc = []
    for p in sorted(files):
        scan(p, since, acc)
    main_files = {p for p in files if os.path.dirname(p) == tdir.rstrip('/\\') or os.path.dirname(p) == os.path.normpath(tdir)}
    print(f'window since {since}; transcript files {len(files)}; tool calls in window {len(acc)}')

    # Q1
    print('\n== Q1 待ち時間(分)— 分類ごと・本体/サブエージェント ==')
    human = [r for r in acc if r['elapsed'] > HUMAN_WAIT_S]
    rest = [r for r in acc if r['elapsed'] <= HUMAN_WAIT_S]
    table = collections.defaultdict(lambda: [0, 0.0, 0, 0.0])
    for r in rest:
        key = ('wait:' if r['tool'] == 'Monitor' else '') + r['cat']
        side = 0 if os.path.normpath(r['file']) in {os.path.normpath(m) for m in main_files} else 2
        table[key][side] += 1
        table[key][side + 1] += r['elapsed']
    total = sum(v[1] + v[3] for v in table.values())
    print(f'{"category":<22}{"main n":>8}{"main min":>10}{"sub n":>8}{"sub min":>10}{"share":>8}')
    for k, v in sorted(table.items(), key=lambda kv: -(kv[1][1] + kv[1][3])):
        print(f'{k:<22}{v[0]:>8}{v[1] / 60:>10.1f}{v[2]:>8}{v[3] / 60:>10.1f}{(v[1] + v[3]) / total * 100 if total else 0:>7.1f}%')
    print(f'total (<= {HUMAN_WAIT_S}s) {total / 60:.1f} min; human_wait excluded: {len(human)} calls, {sum(r["elapsed"] for r in human) / 60:.1f} min')

    # Q2
    print('\n== Q2 commit とフックの全計画 ==')
    commits = [r for r in rest if r['cat'] == 'commit']
    kinds = collections.Counter()
    secs = collections.defaultdict(list)
    for r in commits:
        k = 'sweep' if SWEEP_YES in r['out'] else ('no_sweep' if SWEEP_NO in r['out'] else 'unknown')
        kinds[k] += 1
        secs[k].append(r['elapsed'])
    for k in ('sweep', 'no_sweep', 'unknown'):
        v = sorted(secs[k])
        med = v[len(v) // 2] if v else 0
        print(f'{k:<10} n={kinds[k]:<4} sum_min={sum(v) / 60:7.1f} median_s={med:6.0f}')

    # Q2b(逸脱 2・README §6): 出力が切られて「不明」が多いため、着地した commit の変更ファイルに
    # フックと同じパターン(bomdd/hooks/pre-commit の SWEEP_PATTERN)を当てて数える。読み取りだけ。
    if REPO:
        import subprocess
        sweep_rx = re.compile(r'^(src/|tools/ViewTube\.CaptureHarness/|tools/sweep-capture-plans\.py$|bomdd/hooks/pre-commit$|bomdd/ui/captures/[^/]+/fixture-manifest\.json$|bomdd/ui/fixtures/|Directory\.Build\.props$|Directory\.Packages\.props$|global\.json$|\.editorconfig$|Directory\.Build\.targets$|NuGet\.config$|Directory\.Build\.rsp$)')
        log = subprocess.run(['git', '-C', REPO, 'log', f'--since={since}', '--format=@@%h %s', '--name-only'],
                             capture_output=True, text=True, encoding='utf-8').stdout
        landed, swept, kinds_s = 0, 0, collections.Counter()
        cur, files_ = None, []
        def flush():
            nonlocal landed, swept
            if cur is None:
                return
            landed += 1
            hit = any(sweep_rx.search(p) for p in files_)
            swept += hit
            kinds_s[(cur.split(' ', 1)[1].split('(')[0].split(':')[0], hit)] += 1
        for line in log.splitlines():
            if line.startswith('@@'):
                flush(); cur, files_ = line[2:], []
            elif line.strip():
                files_.append(line.strip())
        flush()
        print(f'Q2b landed commits since {since}: {landed}; matching the sweep pattern: {swept}')
        for (k, hit), n in sorted(kinds_s.items()):
            print(f'   {k:<10} sweep={hit!s:<5} {n}')

    # Q3
    print('\n== Q3 門が止めた呼び出し ==')
    reasons = collections.Counter()
    for r in acc:
        if BLOCKED in r['out']:
            for line in r['out'].splitlines():
                if BLOCKED in line:
                    reasons[re.sub(r'\s+', ' ', line.strip())[:160]] += 1
    blocked_calls = sum(1 for r in acc if BLOCKED in r['out'])
    print(f'calls whose output contains "{BLOCKED}": {blocked_calls}')
    for k, n in reasons.most_common(25):
        print(f'{n:>4}  {k}')

    # Q4
    print('\n== Q4 全体の受け入れテスト(acceptance-runs)==')
    since_compact = since[:10].replace('-', '')
    runs = []
    for name in sorted(os.listdir(rdir)):
        m = re.match(r'run-(\d{8})T', name)
        if not m or m.group(1) < since_compact:
            continue
        p = os.path.join(rdir, name, 'supervisor-report.json')
        if not os.path.exists(p):
            runs.append((name, None, None, None)); continue
        d = json.load(open(p, encoding='utf-8-sig'))
        runs.append((name, d.get('discovered'), d.get('failed'), d.get('skipped')))
    print(f'runs in window: {len(runs)}; with failed>0: {sum(1 for r in runs if (r[2] or 0) > 0)}')
    for r in runs:
        print('  ', *r)

    # top long calls for reading
    print('\n== 参考: 待ちの長い呼び出し 上位 25(human_wait を除く)==')
    for r in sorted(rest, key=lambda r: -r['elapsed'])[:25]:
        side = 'main' if os.path.normpath(r['file']) in {os.path.normpath(m) for m in main_files} else 'sub'
        print(f"{r['start'][:19]} {r['elapsed']:>6.0f}s {side:<4} {('wait:' if r['tool'] == 'Monitor' else '') + r['cat']:<16} {r['cmd'][:150].replace(chr(10), ' | ')}")


if __name__ == '__main__':
    main()
