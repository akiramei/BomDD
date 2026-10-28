"""Apply the kit playbook's G3 A1 structure resolution (rules 1-6) to MoviePad-Remake at a fixed commit.

EXP-20261029-01 found that A1 is written (playbook section 4.6) but no tool runs it. This script is a reading aid for the
experiment, not a validator of the product: it reads 30-ebom.yaml and 32-mbom.yaml with `git show` and prints each rule's
failures. Rule 7 (IF- exists and the provider connects to the consumer as section 4.1 says) is not implemented.
Retired E items (superseded_by set) and mbom.retired_units are left out, as I3a reads manufacturing_units only.

usage: python a1_check.py <path to MoviePad-Remake> [commit]   (exit 0 always; the output is the finding)
"""
import subprocess
import sys

import yaml


def show(repo, commit, path):
    out = subprocess.run(['git', '-C', repo, 'show', f'{commit}:{path}'], check=True, capture_output=True).stdout
    return yaml.safe_load(out.decode('utf-8'))


def main():
    repo = sys.argv[1]
    commit = sys.argv[2] if len(sys.argv) > 2 else 'd3683d6'
    ebom = show(repo, commit, 'bomdd/30-ebom.yaml')['ebom']
    mbom = show(repo, commit, 'bomdd/32-mbom.yaml')['mbom']

    items = {i['id']: i for i in ebom['items']
             if not ((i.get('lineage') or {}).get('superseded_by'))}
    units = {u['id']: u for u in mbom['manufacturing_units']}
    e_provides = {}   # IF -> E item providing it
    e_requires = {}   # E item -> IF list
    for iid, it in items.items():
        intf = it.get('interfaces') or {}
        for p in intf.get('provides') or []:
            e_provides.setdefault(p['id'], []).append(iid)
        e_requires[iid] = list(intf.get('requires') or [])
    ps_owner = {}
    for uid, u in units.items():
        ps = u.get('part_standard') or {}
        for p in (ps.get('provides') or []) + (ps.get('requires') or []):
            ps_owner[p['id']] = uid
    procurement = {p.get('id') or p.get('package') or p.get('name') for p in (mbom.get('procurement') or [])}

    def realiser(if_id):
        return [uid for uid, u in units.items()
                if set(u.get('ebom_refs') or []) & set(e_provides.get(if_id, []))
                and any(p.get('ruled_ref') == if_id for p in ((u.get('part_standard') or {}).get('provides') or []))]

    findings = []
    # rule 2
    for if_id in sorted(e_provides):
        r = realiser(if_id)
        if len(r) != 1:
            findings.append(('2', f'{if_id} is realised by {len(r)} units {r}'))
    for uid, u in units.items():
        ps = u.get('part_standard')
        if not ps:
            continue
        mine = set(u.get('ebom_refs') or [])
        # rule 3
        for p in ps.get('provides') or []:
            rr = p.get('ruled_ref')
            if rr and not (mine & set(e_provides.get(rr, []))):
                findings.append(('3', f'{uid} {p["id"]} ruled_ref {rr} is not an IF- of its E items'))
        resolved_units = set()
        for q in ps.get('requires') or []:
            t = q['target']
            if t.startswith('PS-'):
                owner = ps_owner.get(t)
                if owner is None:
                    findings.append(('1', f'{uid} {q["id"]} target {t} does not exist'))
                    continue
                resolved_units.add(owner)
                provider_e = set(units[owner].get('ebom_refs') or [])
                if not (mine & provider_e) and provider_e:
                    findings.append(('4', f'{uid} {q["id"]} targets {t} of {owner}: the units share no E item and the provider has ebom_refs {sorted(provider_e)} (an E-to-E boundary must be an IF-)'))
            elif t.startswith('IF-'):
                r = realiser(t)
                ok_side = (not mine) or any(t in e_requires.get(e, []) or t in [p['id'] for p in ((items.get(e) or {}).get('interfaces') or {}).get('provides') or []] for e in mine)
                if len(r) != 1 or not ok_side:
                    findings.append(('1', f'{uid} {q["id"]} target {t} does not resolve (realisers {r}, requiring side allowed {ok_side})'))
                else:
                    resolved_units.add(r[0])
            elif t.startswith('procurement:') or t.startswith('platform:'):
                pass
            else:
                findings.append(('1', f'{uid} {q["id"]} target {t} is of no known kind'))
        # rule 6
        dep = set(u.get('depends_on') or [])
        if dep and dep != resolved_units:
            findings.append(('6', f'{uid} depends_on {sorted(dep)} != units its requires resolve to {sorted(resolved_units)}'))
    # rule 5
    for consumer, ifs in e_requires.items():
        for if_id in ifs:
            consumer_units = [uid for uid, u in units.items() if consumer in (u.get('ebom_refs') or [])]
            provider_units = realiser(if_id)
            if any(c in provider_units for c in consumer_units):
                continue
            if not any((units[c].get('part_standard') or {}) for c in consumer_units):
                continue
            has = any(any(q['target'] == if_id for q in ((units[c].get('part_standard') or {}).get('requires') or []))
                      for c in consumer_units)
            if not has:
                findings.append(('5', f'E item {consumer} requires {if_id}; no unit realising {consumer} ({consumer_units}) has a requires targeting it'))

    print(f'MoviePad-Remake {commit}: {len(units)} units, {len(items)} live E items, {len(e_provides)} IF-')
    for rule in '123456':
        rows = [f for r, f in findings if r == rule]
        print(f'rule {rule}: {len(rows)} failure(s)')
        for f in rows:
            print('  ', f)


if __name__ == '__main__':
    main()
