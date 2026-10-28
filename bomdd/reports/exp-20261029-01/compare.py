"""EXP-20261029-01: compare the two classifications and map the defects. Writes summary.json and prints the tables.

usage: python compare.py
"""
import json
import os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
CLASSES = ['R', 'C', 'C+', 'J', 'U']


def load(name):
    with open(os.path.join(HERE, name), encoding='utf-8') as f:
        return json.load(f)


def main():
    items = load('items.json')['items']
    kind = {i['id']: i['kind'] for i in items}
    c1 = {e['id']: e for e in load('classifier-1.json')['items']}
    c2 = {e['id']: e for e in load('classifier-2.json')['items']}
    ids = [i['id'] for i in items]
    assert set(c1) == set(ids) == set(c2), 'id sets differ'

    out = {'n': len(ids), 'overall': {}, 'by_kind': {}, 'disagreements': [], 'defects': [], 'missing_fields': {}}
    for tag, c in (('1', c1), ('2', c2)):
        out['overall'][tag] = dict(Counter(c[i]['class'] for i in ids))
    agree = sum(c1[i]['class'] == c2[i]['class'] for i in ids)
    out['overall']['exact_agreement'] = agree
    island1 = sum(c1[i]['class'] in ('R', 'C') for i in ids)
    island2 = sum(c2[i]['class'] in ('R', 'C') for i in ids)
    island_both = sum(c1[i]['class'] in ('R', 'C') and c2[i]['class'] in ('R', 'C') for i in ids)
    out['overall']['island_R_or_C'] = {'1': island1, '2': island2, 'both': island_both}

    by_kind = defaultdict(list)
    for i in ids:
        by_kind[kind[i]].append(i)
    print(f"{'kind':26} {'n':>3}  {'cls 1 (R/C/C+/J/U)':>20}  {'cls 2 (R/C/C+/J/U)':>20}  agree  R|C both")
    for k, members in by_kind.items():
        n = len(members)
        cnt1 = Counter(c1[i]['class'] for i in members)
        cnt2 = Counter(c2[i]['class'] for i in members)
        ag = sum(c1[i]['class'] == c2[i]['class'] for i in members)
        rc_both = sum(c1[i]['class'] in ('R', 'C') and c2[i]['class'] in ('R', 'C') for i in members)
        out['by_kind'][k] = {'n': n, '1': dict(cnt1), '2': dict(cnt2), 'agree': ag, 'rc_both': rc_both,
                             'no_claim': (n - ag) * 3 > n}
        f = lambda cnt: '/'.join(str(cnt.get(x, 0)) for x in CLASSES)
        flag = '  no claim (>1/3 disagree)' if (n - ag) * 3 > n else ''
        print(f'{k:26} {n:>3}  {f(cnt1):>20}  {f(cnt2):>20}  {ag:>5}  {rc_both:>8}{flag}')
    print(f"overall: n={len(ids)} cls1={out['overall']['1']} cls2={out['overall']['2']} exact agreement {agree}/{len(ids)}; "
          f"R or C: cls1 {island1}, cls2 {island2}, both {island_both}")

    for i in ids:
        if c1[i]['class'] != c2[i]['class']:
            out['disagreements'].append({'id': i, '1': c1[i]['class'], '2': c2[i]['class'],
                                         'reason_1': c1[i]['reason'], 'reason_2': c2[i]['reason']})
    for tag, c in (('1', c1), ('2', c2)):
        fields = [c[i].get('missing_field') for i in ids if c[i]['class'] == 'C+']
        out['missing_fields'][tag] = dict(Counter(fields))

    defects = load('defects.json')['findings']
    hits = {'1': Counter(), '2': Counter()}
    for d in defects:
        row = {'id': d['id'], 'found_by': d['found_by'], 'items': d['items'],
               'class_1': [c1[i]['class'] for i in d['items']], 'class_2': [c2[i]['class'] for i in d['items']]}
        out['defects'].append(row)
        for i in d['items']:
            hits['1'][c1[i]['class']] += 1
            hits['2'][c2[i]['class']] += 1
    out['defect_item_hits_by_class'] = {k: dict(v) for k, v in hits.items()}
    mapped = [d for d in defects if d['items']]
    print(f"findings: {len(defects)} ({len(mapped)} mapped to items); item hits by class: cls1 {dict(hits['1'])}, cls2 {dict(hits['2'])}")
    print('disagreements:', len(out['disagreements']))

    with open(os.path.join(HERE, 'summary.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write('\n')


if __name__ == '__main__':
    main()
