"""EXP-20261028-01 outcome baseline: derive per-ECO outcome counts from change records and git.

Read-only in every repository. Rules: definitions.md in this folder (frozen before counting).
Writes baseline.json and baseline.md next to this script. Python 3 + PyYAML.
Never reads or lists ViewTube/product/ (every file path is under bomdd/ or a register-named test-results/ review file).
"""
import json
import os
import re
import statistics
import subprocess
import sys
import unicodedata
from datetime import datetime

import yaml

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = r'C:\Users\akira\source\repos'
WINDOW_START = '2026-10-01'

REPOS = [
    dict(name='BomDD', root=os.path.join(BASE, 'BomDD'), kind='bomdd',
         register='bomdd/60-change-register.yaml', prefix='ECO-'),
    dict(name='ViewTube', root=os.path.join(BASE, 'ViewTube'), kind='vt',
         register='bomdd/process/change-register.yaml', prefix='ECO-VT-'),
    dict(name='ViewPrism2', root=os.path.join(BASE, 'ViewPrism2'), kind='vp',
         register='bomdd/60-change-register.yaml', prefix='ECO-'),
    dict(name='MoviePad-Remake', root=os.path.join(BASE, 'MoviePad-Remake'), kind='mp',
         register='bomdd/60-change-register.yaml', prefix='ECO-'),
]
RECEIVING = {('ViewPrism2', 'ECO-148'), ('ViewTube', 'ECO-VT-270'), ('ViewTube', 'ECO-VT-271'),
             ('MoviePad-Remake', 'ECO-004')}
PRODUCT_NAMES = {'ViewTube': 'ViewTube', 'ViewPrism2': 'ViewPrism2', 'MoviePad-Remake': 'MoviePad-Remake'}


def U(code):
    return {'unknown': code}


def is_unknown(v):
    return isinstance(v, dict) and 'unknown' in v


# ---------------------------------------------------------------- git

def git(root, *args):
    r = subprocess.run(['git', '-C', root, *args], capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    if r.returncode != 0:
        raise RuntimeError('git failed: %s %s: %s' % (root, args, r.stderr))
    return r.stdout


def load_commits(root):
    out = git(root, 'log', 'HEAD', '--format=%H%x1f%cI%x1f%B%x1e')
    commits = []
    for rec in out.split('\x1e'):
        rec = rec.strip('\n')
        if not rec.strip():
            continue
        h, date, body = rec.split('\x1f', 2)
        body = body.strip()
        subject = body.split('\n', 1)[0]
        trailers = re.findall(r'^BomDD-ECO-(\w+):\s*(\S.*?)\s*$', body, re.M)
        commits.append(dict(sha=h.strip(), date=date.strip(), subject=subject, body=body,
                            trailers=[(k, v.upper()) for k, v in trailers]))
    commits.reverse()  # oldest first
    return commits


def first_add(root, relpath):
    out = git(root, 'log', '--diff-filter=A', '--format=%H%x1f%cI', '--', relpath)
    lines = [l for l in out.splitlines() if l.strip()]
    if not lines:
        return None
    h, d = lines[-1].split('\x1f')
    return dict(sha=h, date=d)


def parse_dt(s):
    return datetime.fromisoformat(s)


# ---------------------------------------------------------------- ids and attribution

def norm_id(repo, num):
    return '%s%03d' % (repo['prefix'], int(num))


def subject_ids(repo, subject):
    """ECO ids named by a commit subject's scope (definitions.md, Scope)."""
    ids = set()
    if repo['kind'] == 'vt':
        m = re.match(r'^[^\s(:]+\(([^)]*)\)', subject)
        if m:
            for n in re.findall(r'eco-vt-(\d+)', m.group(1), re.I):
                ids.add(norm_id(repo, n))
        return ids
    m = re.match(r'^([^\s(:]+)\(([^)]*)\)', subject)
    if m:
        typ, scope = m.group(1), m.group(2)
        for n in re.findall(r'eco-(\d+)', scope, re.I):
            ids.add(norm_id(repo, n))
        if typ.lower() == 'eco':
            for a, b in re.findall(r'(\d{2,3})\s*-\s*(\d{2,3})', scope):
                for n in range(int(a), int(b) + 1):
                    ids.add(norm_id(repo, n))
            for n in re.findall(r'\d{2,3}', scope):
                ids.add(norm_id(repo, n))
    m = re.match(r'^eco-(\d+):', subject, re.I)
    if m:
        ids.add(norm_id(repo, m.group(1)))
    return ids


def attributed(repo, c, eid):
    if eid in subject_ids(repo, c['subject']):
        return True
    return any(v == eid for _, v in c['trailers'])


def subject_type(subject):
    m = re.match(r'^([^\s(:]+)\(', subject)
    return m.group(1).lower() if m else None


def id_regex(eid):
    return re.compile(r'(?<![\w-])' + re.escape(eid) + r'(?![\d])', re.I)


# ---------------------------------------------------------------- text helpers

HEAD_RE = re.compile(r'^\s*(#{1,6})\s')
BOLD_RE = re.compile(r'^\s*(?:[-*]|\d+\.)?\s*\*\*')
RECEIPT_HEAD = re.compile(r'収束 receipt|[Cc]onverge receipt|[Cc]onvergence receipt')


def heading_level(line):
    m = HEAD_RE.match(line)
    return len(m.group(1)) if m else None


def split_receipts(text):
    """Return (text without converge receipts, list of receipt texts)."""
    lines = text.split('\n')
    keep, receipts, cur, cur_level = [], [], None, None
    for line in lines:
        lvl = heading_level(line)
        if cur is not None:
            if lvl is not None and lvl <= cur_level:
                receipts.append('\n'.join(cur))
                cur = None
            else:
                cur.append(line)
                continue
        if lvl is not None and RECEIPT_HEAD.search(line):
            cur, cur_level = [line], lvl
            continue
        keep.append(line)
    if cur is not None:
        receipts.append('\n'.join(cur))
    return '\n'.join(keep), receipts


# ---------------------------------------------------------------- metric 1: review rounds

ROUND_RE = re.compile(r'\b[Rr]ound\s+(\d+)\b|\binspection\s+r(\d+)\b')
SUBSEC_R = re.compile(r'^\s*#{3,4}\s+\d+\.\d+\s+r(\d+)[(（]')
INLINE_R = re.compile(r'\br(\d+)\s*\*\*(ACCEPT|REJECT)')
VERDICT_RE = re.compile(r'PASS WITH FINDINGS|NOT FIT|ACCEPT|REJECT|不合格|合格|PASS|FAIL')
VERDICT_LINE = re.compile(r'verdict|Verdict|VERDICT|Result|判定')
COUNT_RE = re.compile(r'\b(\d+)\s+(?:new\s+)?findings?\b')
SER_RE = re.compile(r'substance\s+(\d+),\s*evidence\s+(\d+),\s*record\s+(\d+)')
JPCOUNT_RE = re.compile(r'(?:ブロッキング|重大|軽微|blocking|material|minor|major)\s*(\d+)')
ZERO_RE = re.compile(r'no (?:substance |new |blocking |in-scope )?findings?\b|[Ff]indings?:? none|所見なし|No substance finding', re.I)
FID_PREFIXED = re.compile(r'\b(IA-\d+|R\d{3}[a-z]-F\d+|R\d{3}-\d+-\d+|R\d{3}-[A-Z]\d+|R8-\d+-\d+|VP\d+-[A-Z]\d+|R\d-\d+)\b')
TABLE_ROW = re.compile(r'^\s*\|\s*`?(IA-\d+|R\d{3}[a-z]?-[A-Z]?\d+(?:-\d+)?|R8-\d+-\d+)`?\s*\|')  # Departure D3
FID_BARE = re.compile(r'^\s*#{2,6}\s+(F\d+)\b')
RANGE_RE = re.compile(r'IA-(\d+) to IA-(\d+)')


def map_verdict(tok):
    if tok is None:
        return None
    if tok in ('ACCEPT', 'PASS', 'PASS WITH FINDINGS', '合格'):
        return 'ACCEPT'
    return 'REJECT'


HEAD_ROUND = re.compile(r'(?<![Ll]oop )(?<![Ll]oop \d )\b[Rr]ound\s+(\d+)\b|\binspection\s+r(\d+)\b')
BOLD_ROUND = re.compile(r'^\s*(?:[-*]|\d+\.)?\s*\*\*([^*]{0,25}?)\b[Rr]ound\s+(\d+)\b')


def marker(line):
    """Round number if the line opens a round marker, and whether it is a heading.

    Departure D1 (definitions.md): a bold lead counts only when the round phrase is inside the bold text
    (within 40 characters of its start, no 'loop'/'converge' before it); a heading counts when the phrase
    is not 'loop N round M'."""
    m = SUBSEC_R.match(line)
    if m:
        return int(m.group(1)), True
    if heading_level(line) is not None:
        m = HEAD_ROUND.search(line)
        if m and not re.search(r'[Ll]oop\s+\d+\s*,?\s*round', line):
            return int(m.group(1) or m.group(2)), True
        m = re.search(r'第\s*(\d+)\s*回', line)  # Departure D4: ViewTube's Japanese round headings
        if m:
            return int(m.group(1)), True
    m = BOLD_ROUND.match(line)
    if m and not re.search(r'loop|converge', m.group(1), re.I):
        return int(m.group(2)), False
    m = INLINE_R.search(line)
    if m:
        return int(m.group(1)), False
    return None, None


def chunk_rounds(text, whole_file):
    lines = text.split('\n')
    pre, chunks, cur = [], [], None
    for line in lines:
        n, is_head = marker(line)
        lvl = heading_level(line)
        if n is not None and (cur is None or n > cur['n']):
            cur = dict(n=n, lines=[line], closed=False, level=lvl, head=is_head)
            chunks.append(cur)
            continue
        if cur is None:
            pre.append(line)
            continue
        if not whole_file and not cur['closed'] and lvl is not None and n is None:
            if (not cur['head']) or lvl <= cur['level']:
                cur['closed'] = True
        if cur['closed']:
            continue  # text after a round's end in an order file is not the round's
        cur['lines'].append(line)
    return pre, [(c['n'], c['lines']) for c in chunks]


def findings_of(lines, seen, verdict_line_idx):
    marker_line = lines[0]
    cand = [marker_line]
    if verdict_line_idx is not None:
        cand.append(lines[verdict_line_idx])
    for l in cand:
        m = SER_RE.search(l)
        if m:
            return sum(int(x) for x in m.groups()), 'explicit_layers'
        m = COUNT_RE.search(l)
        if m:
            return int(m.group(1)), 'explicit_count'
        m = re.search(r'所見[がは]?\s*(\d+)\s*件', l)  # Departure D5: the Japanese count form
        if m:
            return int(m.group(1)), 'explicit_count_ja'
    ids = set()
    for a, b in RANGE_RE.findall(marker_line):
        for k in range(int(a), int(b) + 1):
            ids.add('IA-%02d' % k)
    for i, l in enumerate(lines):
        if i == 0 or heading_level(l) is not None or BOLD_RE.match(l):
            ids.update(FID_PREFIXED.findall(l))
        t = TABLE_ROW.match(l)
        if t:
            ids.add(t.group(1))
        t = re.match(r'^\s*\|\s*(F\d+)\s*\|', l)
        if t:
            ids.add('#' + t.group(1))
        m = FID_BARE.match(l)
        if m:
            ids.add('#' + m.group(1))
    new = {i for i in ids if i.startswith('#') or i not in seen}
    seen.update(i for i in ids if not i.startswith('#'))
    if new:
        return len(new), 'ids'
    if any(ZERO_RE.search(l) for l in lines):
        return 0, 'zero_phrase'
    return U('NO_FINDING_COUNT'), None


def rounds_from_text(text, whole_file):
    pre, chunks = chunk_rounds(text, whole_file)
    if whole_file:
        pre_txt = '\n'.join(pre)
        pre_has_verdict = any(VERDICT_LINE.search(l) and VERDICT_RE.search(l) for l in pre)
        if not chunks:
            chunks = [(1, pre)] if pre else []
        elif pre_has_verdict and chunks[0][0] != 1:
            chunks = [(1, pre)] + chunks
        elif pre_has_verdict and chunks[0][0] == 1:
            pass
    result, seen = [], set()
    for n, lines in chunks:
        tok = None
        m = VERDICT_RE.search(lines[0])
        vidx = None
        if m:
            tok = m.group(0)
        else:
            for i, l in enumerate(lines[1:], 1):
                if VERDICT_LINE.search(l):
                    m = VERDICT_RE.search(l)
                    if m:
                        tok, vidx = m.group(0), i
                        break
                    if heading_level(l) is not None:
                        # Departure D2: a 'Verdict' heading's token is on the next non-empty line
                        for j in range(i + 1, min(i + 4, len(lines))):
                            if lines[j].strip():
                                m = VERDICT_RE.search(lines[j])
                                if m:
                                    tok, vidx = m.group(0), j
                                break
                        if tok:
                            break
        f, basis = findings_of(lines, seen, vidx)
        result.append(dict(round=n, verdict=map_verdict(tok) if tok else U('NO_VERDICT_TOKEN'),
                           verdict_token=tok, findings=f, findings_basis=basis,
                           marker=lines[0].strip()[:160]))
    return result


SUBJ_ROUND = re.compile(r'r(\d+)(?:\s*→\s*r(\d+))?[^r\n]{0,12}?[\s(（〔]*\**(ACCEPT|REJECT)')


def rounds_from_subjects(repo, commits, eid):
    found = {}
    for c in commits:
        if not attributed(repo, c, eid):
            continue
        s = c['subject']
        if subject_ids(repo, s) != {eid}:
            continue  # a subject naming several ECOs (eco(091/093/094)) cannot say whose round it is
        if not re.search(r'独立検査|inspection', s):
            continue
        for a, b, v in SUBJ_ROUND.findall(s):
            n = int(b or a)
            found.setdefault(n, v)
    return [dict(round=n, verdict=found[n], verdict_token=found[n], findings=U('NO_FINDING_COUNT'),
                 findings_basis=None, marker='commit subject') for n in sorted(found)]


def vt_register_rounds(repo, entry, num):
    ev = entry.get('evidence') or {}
    blocks = sorted((int(m.group(1)), v) for k, v in ev.items()
                    for m in [re.match(r'review_round_(\d+)$', k)] if m and isinstance(v, dict) and 'verdict' in v)
    if blocks:
        out = []
        for n, v in blocks:
            tok_m = VERDICT_RE.search(str(v.get('verdict', '')))
            tok = tok_m.group(0) if tok_m else None
            fs = JPCOUNT_RE.findall(str(v.get('findings', '')))
            f = sum(int(x) for x in fs) if fs else U('NO_FINDING_COUNT')
            out.append(dict(round=n, verdict=map_verdict(tok) if tok else U('NO_VERDICT_TOKEN'),
                            verdict_token=tok, findings=f, findings_basis='register_block' if fs else None,
                            marker='register evidence.review_round_%d' % n))
        return out, 'register_blocks'
    text = yaml.safe_dump(entry, allow_unicode=True, width=100000)
    paths = sorted(set(re.findall(r'(test-results/[^\s\'"]*?/review%dr\d+[^\s\'"/]*\.md)' % num, text)))
    paths = [p for p in paths if not p.startswith('product/')]
    if paths:
        def key(p):
            m = re.search(r'review%dr(\d+)([^/]*)\.md$' % num, p)
            return (int(m.group(1)), m.group(2))
        paths.sort(key=key)
        out, seen = [], set()
        for i, p in enumerate(paths, 1):
            full = os.path.join(repo['root'], p)
            if not os.path.isfile(full):
                out.append(dict(round=i, verdict=U('NO_R8_RECORD'), verdict_token=None,
                                findings=U('NO_R8_RECORD'), findings_basis=None, marker=p))
                continue
            t = open(full, encoding='utf-8', errors='replace').read()
            sub = rounds_from_text(t, whole_file=True)
            r0 = sub[0] if sub else dict(verdict=U('NO_VERDICT_TOKEN'), verdict_token=None,
                                         findings=U('NO_FINDING_COUNT'), findings_basis=None)
            out.append(dict(round=i, verdict=r0['verdict'], verdict_token=r0['verdict_token'],
                            findings=r0['findings'], findings_basis=r0['findings_basis'], marker=p))
        return out, 'register_named_files'
    return None, None


# ---------------------------------------------------------------- metric 2: converge

CHAIN = re.compile(r'\d+\s*(?:→|->)\s*\d+(?:\s*(?:→|->)\s*\d+)*')
TRAJ_CTX = re.compile(r'軌跡|trajectory|round|findings', re.I)
JUDGE = re.compile(r'(?:判定|[Vv]erdict|[Jj]udgement|[Oo]utcome|ended)[^\n]{0,20}?(未収束|unconverged|not converged|収束|converged)')


def converge(receipts):
    if not receipts:
        return dict(loops=[], outcome='none')
    # Departure D10: per loop (a heading inside the receipt), the chain on a 軌跡/trajectory line wins,
    # else the longest qualifying chain - the first chain on a line could be a partial ("of round 1's 15 → 7").
    loops, final = [], None
    for rt in receipts:
        best = {}
        loop_key = 0
        for line in rt.split('\n'):
            if heading_level(line) is not None:
                loop_key += 1
            if TRAJ_CTX.search(line):
                for m in CHAIN.finditer(line):
                    ch = re.sub(r'\s+', '', m.group(0)).replace('->', '→')
                    pri = 1 if re.search(r'軌跡|trajectory', line, re.I) else 0
                    cand = (pri, ch.count('→'), ch)
                    if loop_key not in best or cand[:2] > best[loop_key][:2]:
                        best[loop_key] = cand
            for j in JUDGE.finditer(line):
                final = j.group(1)
        loops.extend(best[k][2] for k in sorted(best))
    if final is None:
        return dict(loops=loops, outcome=U('NO_CONVERGE_VERDICT'))
    outcome = 'cutoff' if final in ('未収束', 'unconverged', 'not converged') else 'converged'
    return dict(loops=loops, outcome=outcome, final_token=final)


# ---------------------------------------------------------------- metric 4: rulings and golden

ATTR = r"(?:\buser(?:'s)?|利用者|\bmaintainer(?:'s)?|\bDECIDE)"
QUOTE = re.compile(ATTR + r"[^\"「\n]{0,40}?(?:\"([^\"\n]{1,60})\"|「([^」\n]{1,80})」)")
UNQ = re.compile(r"(?:user|利用者)\s*(?:裁定|ruling|DECIDE)\s*((?:\d+\s*[:：]\s*[A-Za-z]'?\s*)+)")
GOLD = re.compile(r'golden|gate ?②|gate 2|application golden|real-machine|実機', re.I)
REJ = re.compile(r'差し戻|returned|sent back|rejected|REJECT|不合格|not approved|did not approve|invalidated|やり直')
GOLD_NA = re.compile(r'golden n/a|no golden gate|There is no golden|No golden', re.I)


def norm_q(s):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', s))


def register_words(obj, acc):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ('words', 'instruction_words', 'answers'):
                if isinstance(v, dict):
                    acc.extend(str(x) for x in v.values())
                elif isinstance(v, list):
                    acc.extend(str(x) for x in v)
                else:
                    acc.append(str(v))
            else:
                register_words(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            register_words(v, acc)


QUOTE_G = re.compile(ATTR + r"([^\"「\n]{0,40}?)(?:\"([^\"\n]{1,60})\"|「([^」\n]{1,80})」)")
GAP_BAD = re.compile(r'ECO-|says|typically|e\.g\.|for a |such as', re.I)
NX = re.compile(r"\d+:[A-Za-z]'?")


def rulings(texts, reg_entry):
    """Departure D9: a quote whose gap after the attribution names another ECO or reads as content
    ('says', 'typically', 'e.g.', 'for a', 'such as') is not a ruling."""
    found = set()
    for t in texts:
        for gap, a, b in QUOTE_G.findall(t):
            if GAP_BAD.search(gap):
                continue
            found.add(norm_q(a or b))
        for s in UNQ.findall(t):
            found.add(norm_q(s))
    if reg_entry is not None:
        acc = []
        register_words(reg_entry.get('evidence') or {}, acc)
        for w in acc:
            found.add(norm_q(w))
    found.discard('')
    # A fragment rule ('3:A' inside '1:A 2:A 3:A' is a reference) was tried and withdrawn: in ECO-115 the
    # fragment '2:A' is a ruling of its own (spot-check.md), so references to part of an answer stay counted.
    return sorted(found)


REJ2 = re.compile(r'差し戻|sent back|was returned|returned it|returned the|golden (?:failed|failure|was rejected|rejected|returned)'
                  r'|rejected (?:at|the) golden|not approved|did not approve|承認しな|やり直し')
WHO = re.compile(r'user|利用者|maintainer', re.I)


def golden_returns(texts, kind):
    """Departure D7: BomDD n/a; the rejection words narrowed (no 'invalidated', no inspection 'REJECT');
    the line must also name the user / maintainer."""
    if kind == 'bomdd':
        return 'n/a', []
    joined = '\n'.join(texts)
    if GOLD_NA.search(joined) or not GOLD.search(joined):
        return 'n/a', []
    lines = [l.strip()[:200] for l in joined.split('\n') if GOLD.search(l) and REJ2.search(l) and WHO.search(l)]
    return len(lines), lines


# ---------------------------------------------------------------- metric 5: known defects

NUMWORD = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8,
           'nine': 9, 'ten': 10, 'eleven': 11, 'twelve': 12}
NUMKD = re.compile(r'\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s+'
                   r'(?:(?:low|minor|open|named)\s+)?known defects?\b', re.I)
ZEROKD = re.compile(r'\b[Nn]o known defects?\b')


def known_defects(repo, num, status, texts, accept_msg):
    if status not in ('applied', 'verified'):
        return 'n/a', 'NOT_ACCEPTED'
    joined = '\n'.join(texts + [accept_msg or ''])
    ids = set(re.findall(r'\bKD-%d-\d+\b' % num, joined))
    for l in joined.split('\n'):  # Departure D8b: VP ids are finding ids, so they count only on known-defect lines
        if re.search(r'known defect', l, re.I):
            ids.update(re.findall(r'\bVP%d-[A-Z]\d+\b' % num, l))
    if ids:
        return len(ids), 'own_ids:' + ','.join(sorted(ids))
    # Departure D8: the accept commit's number phrase comes before R8 ids on lines, and R8 id ranges are expanded
    m = NUMKD.search(accept_msg or '')
    if m:
        w = m.group(1).lower()
        return (int(w) if w.isdigit() else NUMWORD[w]), 'accept_number_phrase:' + m.group(0)
    r8 = set()
    for l in joined.split('\n'):
        if re.search(r'known defect', l, re.I):
            for a, b, c in re.findall(r'\bR8-(\d+)-(\d+) to R8-\1-(\d+)\b', l):
                for k in range(int(b), int(c) + 1):
                    r8.add('R8-%s-%02d' % (a, k))
            r8.update(re.findall(r'\bR8-\d+-\d+\b', l))
    if r8:
        return len(r8), 'r8_ids_on_kd_lines:' + ','.join(sorted(r8))
    for t in texts:
        m = NUMKD.search(t)
        if m:
            w = m.group(1).lower()
            return (int(w) if w.isdigit() else NUMWORD[w]), 'number_phrase:' + m.group(0)
    if ZEROKD.search(joined):
        return 0, 'no_known_defect_phrase'
    return U('NO_KD_STATEMENT'), None


# ---------------------------------------------------------------- metric 6: escapes

ESC = re.compile(r'origin|caused|introduced|regression|escaped|due to|起因|由来|混入|退行|回帰', re.I)
def esc_match(line, eid):
    """Departure D6: the escape word must point at the id (definitions.md, Departures)."""
    i = re.escape(eid)
    pats = [
        r'\b(?:introduced|caused|broken|broke|regressed|regression|escaped|originated|origin)\s+(?:by|in|at|since|from|with|of)\b[^\n]{0,40}?' + i + r'(?!\d)',
        r'\bsince\s+(?:\S+\s+){0,2}?' + i + r"(?!\d)(?:'s)?\s+(?:acceptance|application|fix|repair|change|manufacture)",
        i + r"(?!\d)(?:'s)?\s+(?:\S+\s+){0,3}?(?:introduced|caused|broke|regressed)\b",
        i + r'(?!\d)[^\n]{0,15}?(?:起因|混入|退行|で壊|が壊|由来の欠陥)',
        # added after the spot-check of ECO-098 (ECO-100 corrects "ECO-098 の記載の誤り"): correction wording
        i + r'(?!\d)\s*の(?:記載の)?誤り',
        i + r'(?!\d)\s*(?:の記載)?(?:を訂正|の訂正)',
        r'\b(?:corrects|correcting|an error in|the error in|a defect (?:of|in))\s+(?:\S+\s+){0,2}?' + i + r'(?!\d)',
    ]
    return any(re.search(p, line, re.I) for p in pats)


PRODUCT_BEFORE = re.compile(r'(ViewTube|ViewPrism2|MoviePad|TimetableAdv|Plm|BomDD-Plm)[^\n]{0,15}$')


def escape_corpus(repo, ecos_all, improvements_text):
    """List of (kind, number_or_None, path_label, text)."""
    corpus = []
    for num, path in ecos_all:
        corpus.append(('eco', num, path, open(os.path.join(repo['root'], path), encoding='utf-8', errors='replace').read()))
        if repo['kind'] == 'vt':
            rp = 'bomdd/eco/ECO-VT-%03d-independent-review.md' % num
            fp = os.path.join(repo['root'], rp)
            if os.path.isfile(fp):
                corpus.append(('eco', num, rp, open(fp, encoding='utf-8', errors='replace').read()))
    cl = os.path.join(repo['root'], 'bomdd/51-cheat-log.md')
    if os.path.isfile(cl):
        corpus.append(('cheat', None, 'bomdd/51-cheat-log.md', open(cl, encoding='utf-8', errors='replace').read()))
    corpus.append(('obs', None, 'BomDD/method/improvements.md', improvements_text))
    return corpus


def escapes(repo, eid, num, corpus, register_entries):
    rx = id_regex(eid)
    cites = {}
    lines_out = []
    for kind, cnum, path, text in corpus:
        if kind == 'eco' and (cnum is None or cnum <= num):
            continue
        section = None
        for ln, line in enumerate(text.split('\n'), 1):
            if kind == 'cheat':
                m = re.match(r'^#{1,4}\s+(CHEAT-[\w-]+)', line)
                if m:
                    section = m.group(1)
            m = rx.search(line)
            if not m or not esc_match(line, eid):
                continue
            if kind == 'obs':
                if repo['kind'] == 'bomdd':
                    if PRODUCT_BEFORE.search(line[:m.start()]):
                        continue
                elif PRODUCT_NAMES[repo['name']] not in line:
                    continue
            if kind == 'eco':
                key = norm_id(repo, cnum)
            elif kind == 'cheat':
                key = section or '%s:L%d' % (path, ln)
            else:
                o = re.search(r'OBS-\d{8}-\d+', line)
                key = o.group(0) if o else '%s:L%d' % (path, ln)
            cites.setdefault(key, 0)
            cites[key] += 1
            lines_out.append(dict(record=key, path=path, line=ln, text=line.strip()[:240]))
    for e in register_entries:
        co = e.get('corrective_of')
        if co and e.get('id') != eid:
            vals = co if isinstance(co, list) else [co]
            if any(str(v).strip().upper() == eid for v in vals):
                cites.setdefault(e['id'], 0)
                cites[e['id']] += 1
                lines_out.append(dict(record=e['id'], path=repo['register'], line=None, text='corrective_of: %s' % eid))
    return len(cites), sorted(cites), lines_out


# ---------------------------------------------------------------- metric 7: close commit

def close_commit(repo, commits, eid):
    low = eid.lower()
    for c in commits:
        if any(k == 'Accept' and v == eid for k, v in c['trailers']):
            return c, 'accept_trailer'
        if not attributed(repo, c, eid):
            continue
        s = c['subject']
        t = subject_type(s)
        if t == 'accept':
            return c, 'accept_subject'
        if t == 'eco' and re.match(r'^eco\([^)]*\):\s*accept', s, re.I):
            return c, 'eco_accept_subject'
        if t == 'record' and re.match(r'^record\([^)]*\):\s*(verified|applied)', s, re.I):
            return c, 'record_verified_subject'
    rx = id_regex(eid)
    for c in commits:
        if rx.search(c['subject']) and re.search(r'\bverified\b|\bapplied\b', c['subject']):
            return c, 'CLOSE_BY_SUBJECT_FALLBACK'
    return None, None


# ---------------------------------------------------------------- metric 3: fix commits

def fix_commits(repo, commits, eid):
    out = []
    rx = id_regex(eid)
    for c in commits:
        tr = any(k == 'Fix' and v == eid for k, v in c['trailers'])
        att = eid in subject_ids(repo, c['subject'])
        t = subject_type(c['subject'])
        ok = tr
        if not ok and att and t in ('fix', 'file+fix'):
            ok = True
        if not ok and t == 'manufacture' and rx.search(c['body']):
            ok = True
        if not ok and repo['kind'] == 'bomdd' and att and t == 'eco':
            head = c['subject'].split(' — ', 1)[0]
            if re.search(r'製造|是正|処置', head):
                ok = True
        if ok:
            out.append(c['sha'][:8])
    return out


# ---------------------------------------------------------------- metric 8: receiving

def receiving(repo, eid, commits):
    p = os.path.join(repo['root'], 'bomdd/50-as-built.yaml')
    if not os.path.isfile(p):
        return 0, []
    d = yaml.safe_load(open(p, encoding='utf-8'))
    entries = []
    def walk(o):
        if isinstance(o, dict):
            if o.get('work_ref') == eid and str(o.get('id', '')).startswith('AB-'):
                entries.append(o)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(d)
    out = []
    for e in entries:
        aid = e['id']
        t = None
        for c in commits:
            if subject_type(c['subject']) == 'receive' and aid in c['subject'] and attributed(repo, c, eid):
                t = dict(time=c['date'], source='receive commit ' + c['sha'][:8])
                break
        if t is None:
            rd = str(((e.get('measurement') or {}).get('run_dir')) or '')
            m = re.search(r'run-(\d{8}T\d{6})', rd)
            if m:
                t = dict(time=m.group(1) + 'Z', source='run_dir')
        out.append(dict(id=aid, **(t or {'time': U('NO_TIMESTAMP'), 'source': None})))
    return len(out), out


# ---------------------------------------------------------------- per repository

def order_path(repo, num):
    if repo['kind'] == 'vt':
        return 'bomdd/eco/ECO-VT-%03d.md' % num
    return 'bomdd/60-change-order-eco-%03d.md' % num


def run_repo(repo, improvements_text):
    reg = yaml.safe_load(open(os.path.join(repo['root'], repo['register']), encoding='utf-8'))
    entries = reg['changes']
    by_id = {e['id']: e for e in entries}
    commits = load_commits(repo['root'])
    nums = []
    for e in entries:
        m = re.match(re.escape(repo['prefix']) + r'(\d+)$', e['id'])
        if m:
            nums.append(int(m.group(1)))
    nums.sort()
    all_orders = [(n, order_path(repo, n)) for n in nums if os.path.isfile(os.path.join(repo['root'], order_path(repo, n)))]
    corpus = escape_corpus(repo, all_orders, improvements_text)
    rows = []
    for n in nums:
        eid = norm_id(repo, n)
        e = by_id[eid]
        op = order_path(repo, n)
        if not os.path.isfile(os.path.join(repo['root'], op)):
            continue
        fa = first_add(repo['root'], op)
        if repo['kind'] in ('bomdd', 'mp'):
            fdate = str(e.get('date'))
            date_src = 'register.date'
        else:
            fdate = fa['date'][:10] if fa else None
            date_src = 'first commit adding the order file (+09:00)'
        if not fdate or fdate < WINDOW_START:
            continue
        status = str(e.get('status'))
        text = open(os.path.join(repo['root'], op), encoding='utf-8', errors='replace').read()
        body_no_receipt, receipts = split_receipts(text)
        reg_text = yaml.safe_dump(e, allow_unicode=True, width=100000) if repo['kind'] == 'vt' else ''
        close, close_basis = close_commit(repo, commits, eid)
        accept_msg = close['body'] if close else ''
        row = dict(repo=repo['name'], id=eid, status=status, filed=fdate, filed_source=date_src,
                   filing_commit=fa['sha'][:8] if fa else None)

        # 1 review rounds
        rounds, rsrc = None, None
        if repo['kind'] == 'vt':
            rp = os.path.join(repo['root'], 'bomdd/eco/ECO-VT-%03d-independent-review.md' % n)
            if os.path.isfile(rp):
                rounds = rounds_from_text(open(rp, encoding='utf-8', errors='replace').read(), whole_file=True)
                rsrc = 'review_file'
            else:
                rounds, rsrc = vt_register_rounds(repo, e, n)
        else:
            rounds = rounds_from_text(body_no_receipt, whole_file=False)
            rsrc = 'order_file'
            if not rounds and repo['kind'] == 'bomdd':
                rounds = rounds_from_subjects(repo, commits, eid)
                rsrc = 'commit_subjects'
                if not rounds and str(e.get('inspector', 'none')) in ('none', 'None'):
                    rounds, rsrc = [], 'none_declared'
        if rounds is None or (not rounds and rsrc != 'none_declared'):
            row['review_rounds'] = U('NO_R8_RECORD')
            row['review'] = []
        else:
            row['review_rounds'] = len(rounds)
            row['review'] = rounds
        row['review_source'] = rsrc

        # 2 converge
        conv_src = receipts
        if repo['kind'] == 'vt':
            _, conv_src = split_receipts(text)
        row['converge'] = converge(conv_src)

        # 3 fix commits
        fx = fix_commits(repo, commits, eid)
        row['fix_commits'] = len(fx)
        row['fix_shas'] = fx
        row['rework_fixes'] = max(len(fx) - 1, 0)

        # 4 rulings, golden
        texts = [text] + ([accept_msg] if accept_msg else [])
        rl = rulings(texts, e if repo['kind'] == 'vt' else None)
        row['human_rulings'] = len(rl)
        row['ruling_strings'] = rl
        gtexts = texts + ([reg_text] if reg_text else [])
        g, glines = golden_returns(gtexts, repo['kind'])
        row['golden_returns'] = g
        row['golden_lines'] = glines

        # 5 known defects
        kd, kdb = known_defects(repo, n, status, [text] + ([reg_text] if reg_text else []), accept_msg)
        row['known_defects'] = kd
        row['known_defects_basis'] = kdb

        # 6 escapes
        ec, ecr, ecl = escapes(repo, eid, n, corpus, entries)
        row['escapes'] = ec
        row['escape_records'] = ecr
        row['escape_lines'] = ecl

        # 7 elapsed
        if status == 'superseded':
            row['elapsed_h'] = U('SUPERSEDED')
        elif status not in ('applied', 'verified'):
            row['elapsed_h'] = U('NOT_CLOSED')
        elif not fa:
            row['elapsed_h'] = U('NO_FILING_COMMIT')
        elif not close:
            row['elapsed_h'] = U('NOT_CLOSED')
        else:
            row['elapsed_h'] = round((parse_dt(close['date']) - parse_dt(fa['date'])).total_seconds() / 3600, 1)
        row['close_commit'] = close['sha'][:8] if close else None
        row['close_basis'] = close_basis

        # 8 receiving
        if (repo['name'], eid) in RECEIVING:
            cnt, recs = receiving(repo, eid, commits)
            row['receiving_runs'] = cnt
            row['receiving'] = recs
        else:
            row['receiving_runs'] = 'n/a'
            row['receiving'] = []
        rows.append(row)
    return rows


# ---------------------------------------------------------------- output

def cell(v):
    if is_unknown(v):
        return 'unknown:' + v['unknown']
    return str(v)


def median_of(vals):
    nums = [v for v in vals if isinstance(v, (int, float)) and not isinstance(v, bool)]
    if not nums:
        return 'n/a', 0
    return round(statistics.median(nums), 2), len(nums)


def main():
    imp = open(os.path.join(BASE, 'BomDD', 'method', 'improvements.md'), encoding='utf-8', errors='replace').read()
    all_rows = []
    for repo in REPOS:
        all_rows.extend(run_repo(repo, imp))
    for r in all_rows:
        rv = r['review']
        r['review_verdicts'] = '-'.join(cell(x['verdict']) if is_unknown(x['verdict']) else x['verdict'][0] for x in rv) if rv else ''
        r['review_findings'] = [x['findings'] for x in rv]
        r['last_verdict'] = (rv[-1]['verdict'] if rv else ('none' if r['review_rounds'] == 0 else U('NO_R8_RECORD')))
    json.dump(dict(generated=datetime.now().astimezone().isoformat(timespec='seconds'),
                   window_start=WINDOW_START, rows=all_rows),
              open(os.path.join(HERE, 'baseline.json'), 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)

    metrics = ['review_rounds', 'fix_commits', 'rework_fixes', 'human_rulings', 'golden_returns', 'known_defects',
               'escapes', 'elapsed_h', 'receiving_runs']
    md = ['# EXP-20261028-01 outcome baseline (generated by baseline.py; do not edit by hand)', '',
          'Rules: `definitions.md`. Window: ECOs filed on or after %s. `unknown:<code>` = not derivable; '
          '`n/a` / `none` = the metric does not apply or nothing exists. Verdicts: A = ACCEPT, R = REJECT.' % WINDOW_START, '']
    for repo in REPOS:
        rows = [r for r in all_rows if r['repo'] == repo['name']]
        md.append('## %s (%d ECOs)' % (repo['name'], len(rows)))
        md.append('')
        md.append('| ECO | status | filed | R8 rounds | verdicts | findings/round | converge | outcome | fixes | rulings | golden ret. | KD | escapes | elapsed h | receiving |')
        md.append('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
        for r in rows:
            cv = r['converge']
            md.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                r['id'], r['status'], r['filed'], cell(r['review_rounds']), r['review_verdicts'] or '-',
                ', '.join(cell(f) for f in r['review_findings']) or '-',
                ' ; '.join(cv['loops']) or '-', cell(cv['outcome']), r['fix_commits'], r['human_rulings'],
                cell(r['golden_returns']), cell(r['known_defects']), r['escapes'], cell(r['elapsed_h']),
                cell(r['receiving_runs'])))
        md.append('')
    md.append('## Medians per repository (numeric cells only; n = cells counted)')
    md.append('')
    md.append('| repository | ' + ' | '.join(metrics) + ' |')
    md.append('|---|' + '---|' * len(metrics))
    med_json = {}
    for repo in REPOS:
        rows = [r for r in all_rows if r['repo'] == repo['name']]
        cells = []
        med_json[repo['name']] = {}
        for m in metrics:
            v, k = median_of([r[m] for r in rows])
            med_json[repo['name']][m] = dict(median=v, n=k)
            cells.append('%s (n=%d)' % (v, k))
        md.append('| %s | %s |' % (repo['name'], ' | '.join(cells)))
    md.append('')
    md.append('## Unknown cells by metric')
    md.append('')
    unk = {}
    def tally(metric, v):
        if is_unknown(v):
            unk.setdefault(metric, {}).setdefault(v['unknown'], 0)
            unk[metric][v['unknown']] += 1
    for r in all_rows:
        for m in metrics:
            tally(m, r[m])
        tally('converge_outcome', r['converge']['outcome'])
        for x in r['review']:
            tally('review_verdict(per round)', x['verdict'])
            tally('review_findings(per round)', x['findings'])
        for x in r['receiving']:
            tally('receiving_time(per run)', x['time'])
    md.append('| metric | unknown cells | by reason |')
    md.append('|---|---|---|')
    for m in sorted(unk):
        md.append('| %s | %d | %s |' % (m, sum(unk[m].values()), ', '.join('%s %d' % kv for kv in sorted(unk[m].items()))))
    md.append('')
    md.append('## Converge outcomes')
    md.append('')
    for repo in REPOS:
        rows = [r for r in all_rows if r['repo'] == repo['name']]
        oc = {}
        for r in rows:
            k = cell(r['converge']['outcome'])
            oc[k] = oc.get(k, 0) + 1
        md.append('- %s: %s' % (repo['name'], ', '.join('%s %d' % kv for kv in sorted(oc.items()))))
    md.append('')
    open(os.path.join(HERE, 'baseline.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(md) + '\n')
    json.dump(dict(medians=med_json, unknown=unk), open(os.path.join(HERE, 'baseline-summary.json'), 'w', encoding='utf-8', newline='\n'),
              ensure_ascii=False, indent=1)
    print('rows', len(all_rows), {repo['name']: len([r for r in all_rows if r['repo'] == repo['name']]) for repo in REPOS})
    print(json.dumps(unk, ensure_ascii=False))


if __name__ == '__main__':
    main()
