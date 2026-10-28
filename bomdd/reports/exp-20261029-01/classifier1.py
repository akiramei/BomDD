"""Classifier 1 (the designer, this session) for EXP-20261029-01. Writes classifier-1.json.

Written before classifier 2's file was read. Each entry: class, missing field (C+), check, check_by, reason.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
A1 = 'kit playbook 4.6 G3 A1 (rules 1-6; no tool runs it - a1_check.py was written for this experiment)'
C1 = 'kit playbook 4.5 C1 (no tool runs it)'
SELFTEST = 'compare.py --selftest and the sealed mutant sets measure the rows detection, not the value itself'

E = {}


def put(iid, cls, reason, check='none', by=None, missing=None):
    E[iid] = {'id': iid, 'class': cls, 'missing_field': missing, 'check': check, 'check_by': by, 'reason': reason}


# unit partition
put('UNIT/M-SOLUTION-001', 'C', 'A build-skeleton unit with no E item is the practice of every .NET product here; paths are the dotnet defaults. Statable as a K-BOM rule.', 'prose', 'kit playbook 4.5 P4 (units without ebom_refs provide statements only)')
for u in ['DOCUMENT', 'HISTORY', 'MEDIA-TOOLS', 'PROBE', 'OUTPUT-SETTINGS', 'EXPORT']:
    put(f'UNIT/M-{u}-001', 'C', 'One unit per E item, the artifact path is the E item\'s planned_output_artifact_ref; file names are one file per public type of the form. No written rule maps E items to units 1:1.', 'prose', 'kit playbook 4.6 A1 rules 2-3')
put('UNIT/M-SELF-ACCEPTANCE-001', 'C', 'The factory test project as its own unit follows the routing\'s self-acceptance step; statable as a rule.', 'prose', 'kit playbook 4.5 P4')

# dependencies
put('DEP/M-SOLUTION-001', 'C', 'platform:dotnet-sdk-10.0 from K-DOTNET-001; statable (a unit requires the platform its K item names).', 'prose', A1)
for u in ['DOCUMENT', 'HISTORY', 'MEDIA-TOOLS']:
    put(f'DEP/M-{u}-001', 'R', 'The E item requires nothing; A1 rules 5-6 give empty requires and depends_on.', 'prose', A1)
put('DEP/M-PROBE-001', 'R', 'A1 rule 5 gives a requires targeting IF-MEDIA-TOOLS-01 (the E item requires it). The written value targets PS-M-MEDIA-TOOLS-001-P01, which A1 rule 4 forbids (a1_check.py).', 'prose', A1)
put('DEP/M-OUTPUT-SETTINGS-001', 'J', 'The PROBE part is A1 rule 5; the DOCUMENT part comes from MD/M-OUTPUT-SETTINGS-001/1 (reuse Even() from TimeMath), a judged reuse that adds an E-to-E dependency the E-BOM does not have (E-OUTPUT-SETTINGS-001 requires IF-PROBE-01 only) - playbook 4.5 P3 would return it to the human. Both targets fail A1 rule 4.', 'prose', A1)
put('DEP/M-EXPORT-001', 'C', 'The IF part is A1 rule 5 (four IFs); the ffmpeg procurement target needs a stated rule (a unit whose K item names a procured tool requires it). The written value omits IF-OUTPUT-SETTINGS-01 (the form passes width/height/fps) and targets PS- items (A1 rules 4 and 5 fail).', 'prose', A1)
put('DEP/M-SELF-ACCEPTANCE-001', 'C', 'The test project requires the solution skeleton; statable.', 'prose', A1)

# acceptance refs
for u in ['DOCUMENT', 'HISTORY', 'MEDIA-TOOLS', 'PROBE', 'OUTPUT-SETTINGS']:
    put(f'ACC/M-{u}-001', 'C', 'Equal to the E item\'s acceptance_refs (a copy). The E-BOM already names the rows; no written rule says the M unit copies them (playbook 4.5 lists E-BOM acceptance_refs as unmeasured).', 'prose', C1)
put('ACC/M-EXPORT-001', 'C', 'The E item\'s acceptance_refs minus the rows listed in mbom.assembly (CP-EXPORT-VFR-001); statable.', 'prose', C1)
put('ACC/M-SOLUTION-001', 'C', 'The build row for the build unit; statable.', 'prose', C1)
put('ACC/M-SELF-ACCEPTANCE-001', 'C', 'The self-acceptance row for the test unit; statable.', 'prose', C1)

# provides
put('PROVIDES/PS-M-SOLUTION-001-P01', 'C', 'Target framework, nullable and packages come from K-DOTNET-001 and procurement; InternalsVisibleTo and "no package in the core" are the product\'s practice.', 'prose', C1)
put('PROVIDES/PS-M-DOCUMENT-001-P01', 'J', 'The signatures would follow from a typed operation model of SPEC-DOCUMENT/EDIT, but the form adds behaviour the spec does not state (SplitAt accepts a newId in use; "no change" returns the same instance) - read from the authority or chosen.', 'prose', A1 + '; ' + C1, 'a typed operation model per IF- (operations, inputs, outputs, refusals)')
put('PROVIDES/PS-M-HISTORY-001-P01', 'C+', 'Signatures only; the behaviour is SPEC-HISTORY-001. A typed operation model would give them; the Try-pattern and class/record style need a stated style rule.', 'prose', A1 + '; ' + C1, 'a typed operation model for IF-HISTORY-01')
put('PROVIDES/PS-M-MEDIA-TOOLS-001-P01', 'J', 'Adds behaviour the spec does not state (paths cached per instance, Started=false and ExitCode -1 instead of an exception, no normalisation, a double quote in a path unsupported).', 'prose', A1 + '; ' + C1, 'a typed operation model for IF-MEDIA-TOOLS-01')
put('PROVIDES/PS-M-PROBE-001-P01', 'J', 'Adds behaviour the spec does not state (AspectRatio 16/9 when Height is 0; a cancelled probe returns null).', 'prose', A1 + '; ' + C1, 'a typed operation model for IF-PROBE-01')
put('PROVIDES/PS-M-OUTPUT-SETTINGS-001-P01', 'J', 'Allocation and edge behaviour chosen (Scale applies to any s and leaves KeepAspect; ratios in double).', 'prose', A1 + '; ' + C1, 'a typed operation model for IF-OUTPUT-SETTINGS-01')
put('PROVIDES/PS-M-EXPORT-001-P01', 'C+', 'Types and members restate SPEC-EXPORT-001 (formats, errors, progress) as C#; a typed operation model plus a style rule would give them.', 'prose', A1 + '; ' + C1, 'a typed operation model for IF-EXPORT-01 (operations, error kinds, progress record)')
put('PROVIDES/PS-M-EXPORT-001-P02', 'C', 'Restates 20-spec 2.6-2.9 and INV-008 by reference (P4 statement form).', 'prose', C1)
put('PROVIDES/PS-M-EXPORT-CLOCK-001-P01', 'J', 'Mostly spec 2.7 quantities, but the split of the formula between ExportClock and the exporter (the 1.0 s threshold is the exporter\'s), BigInteger rationals and the null cases are chosen.', 'prose', A1 + '; ' + C1, 'a typed operation model for IF-EXPORT-CLOCK-01')
put('PROVIDES/PS-M-EXPORT-COPY-001-P01', 'J', 'Definitions follow spec 2.9, but the lookup\'s failure behaviour is "as the authority" (knowledge outside the ruled input) and Analyze\'s parameter shape is chosen.', 'prose', A1 + '; ' + C1, 'a typed operation model for IF-EXPORT-COPY-01')
put('PROVIDES/PS-M-SELF-ACCEPTANCE-001-P01', 'J', 'How the factory tests get media (lavfi in a temporary directory, nothing outside the repository) is a chosen method.', 'prose', C1)

# manufacturing decisions
put('MD/M-SOLUTION-001/1', 'J', 'One library vs a project per unit: both reasonable; a trade-off.')
put('MD/M-SOLUTION-001/2', 'J', '.sln vs .slnx: taste and tool compatibility.')
put('MD/M-DOCUMENT-001/1', 'C', 'Follows from the spec\'s clamp semantics with lo > hi plus K knowledge that Math.Clamp throws; a K-BOM rule would carry it.')
put('MD/M-MEDIA-TOOLS-001/1', 'J', 'One argument string vs ArgumentList: both reasonable.')
put('MD/M-PROBE-001/1', 'J', 'JsonDocument vs a serializer is a choice; the invariant-culture part is a general K rule.')
put('MD/M-OUTPUT-SETTINGS-001/1', 'J', 'Reuse across units vs a local copy; the choice adds an E-to-E dependency (see DEP/M-OUTPUT-SETTINGS-001).')
put('MD/M-EXPORT-001/1', 'J', 'One of many filter graphs that give the specified output; knowledge of ffmpeg and of the authority.')
put('MD/M-EXPORT-001/2', 'J', 'Responsibility allocation between the exporter and its caller.')
put('MD/M-EXPORT-001/3', 'J', 'Argument order and the mov muxer options: ffmpeg knowledge and choice beyond the spec.')
put('MD/M-EXPORT-001/4', 'J', 'A filter graph among alternatives.')
put('MD/M-EXPORT-001/5', 'J', 'Edge behaviour (empty env var, a token already cancelled) chosen; arguably spec content.')
put('MD/M-EXPORT-001/6', 'J', 'A null policy for result fields chosen.')
put('MD/M-EXPORT-001/7', 'J', 'Progress parsing details beyond the spec.')
put('MD/M-EXPORT-001/8', 'C', 'Same fixed arguments for copy as for re-encode: a consistency rule.')
put('MD/M-EXPORT-001/9', 'J', 'Pass a missing directory through vs create it vs refuse: chosen.')
put('MD/M-EXPORT-001/10', 'J', 'BigInteger vs long with overflow checks vs a package: chosen.')
put('MD/M-EXPORT-001/11', 'C', 'Keep a public form unchanged across a unit merge: a statable change rule.')
put('MD/M-EXPORT-001/12', 'J', 'The ffprobe command and keyframe reading: knowledge of ffprobe and of the authority.')

put('ASSEMBLY', 'C', 'The rows that measure several units end to end at L3 (kit playbook 4.5 A2 states the kind; selecting by depth is statable).', 'prose', 'kit playbook 4.5 A2')

# control plan
SECTION = 'One row per spec section 2.x, split by E item, plus the standard build / self-acceptance / harness rows; the E-BOM already names the row ids.'
for r in ['BUILD', 'DOCUMENT', 'EDIT', 'HISTORY', 'OUTPUT-SETTINGS', 'MEDIA-TOOLS', 'PROBE', 'EXPORT-CLOCK', 'EXPORT-COPY', 'EXPORT', 'EXPORT-VFR', 'SELF-ACCEPTANCE', 'HARNESS-SELFTEST']:
    put(f'CPROW/CP-{r}-001', 'C', SECTION)
put('CPROW/CP-EXPORT-OUTPUT-001', 'J', 'A separate row for stream properties apart from the content rows: a choice of how to cut export\'s measurement.')
put('CPROW/CP-ASSEMBLY-EXPORT-001', 'J', 'An end-to-end content row across requirements 015-017: a choice of how to cut export\'s measurement.')

for r in ['BUILD', 'HISTORY', 'OUTPUT-SETTINGS', 'MEDIA-TOOLS', 'PROBE', 'EXPORT-CLOCK', 'EXPORT-COPY', 'EXPORT', 'EXPORT-OUTPUT', 'ASSEMBLY-EXPORT', 'EXPORT-VFR', 'SELF-ACCEPTANCE', 'HARNESS-SELFTEST']:
    put(f'CPLINK/CP-{r}-001', 'C', 'verifies = the E item and its unit; part_standard_refs = the provides the row\'s section covers; invariants from the E item. A join.', 'prose', C1)
for r in ['DOCUMENT', 'EDIT']:
    put(f'CPLINK/CP-{r}-001', 'C+', 'The join as above, but which of E-DOCUMENT-001\'s invariants each row checks needs a map from invariant to operation.', 'prose', C1, 'per invariant, the operations or spec section it constrains')

for r in ['DOCUMENT', 'EDIT', 'HISTORY', 'OUTPUT-SETTINGS', 'MEDIA-TOOLS', 'PROBE', 'EXPORT-CLOCK', 'EXPORT-COPY', 'EXPORT', 'EXPORT-OUTPUT', 'ASSEMBLY-EXPORT', 'EXPORT-VFR']:
    put(f'CPMETHOD/CP-{r}-001', 'J', 'Depth follows the ladder, but test vectors, tolerances, fixtures and the mutants to catch are chosen (the FMEA names some failure modes; the boundary values and cases are designed).', 'machine', SELFTEST)
put('CPMETHOD/CP-BUILD-001', 'C', 'Build and compare package references with procurement; the known limits record what the instrument reads.', 'none')
put('CPMETHOD/CP-SELF-ACCEPTANCE-001', 'J', 'A test class per unit and the search of test sources are chosen criteria.', 'none')
put('CPMETHOD/CP-HARNESS-SELFTEST-001', 'J', 'The known-bad alterations and the sealed-set design are chosen.', 'none')

WHEN_RULE = 'classification from the E item; on_fail and approver the same in every product row; when by a statable rule (unit with no depends_on -> part-change; with -> connection-change; L3 -> acceptance; instruments -> instrument-change).'
for r in ['BUILD', 'DOCUMENT', 'EDIT', 'HISTORY', 'MEDIA-TOOLS', 'PROBE', 'EXPORT-COPY', 'EXPORT', 'EXPORT-VFR', 'SELF-ACCEPTANCE', 'HARNESS-SELFTEST']:
    put(f'CPPOLICY/CP-{r}-001', 'C', WHEN_RULE, 'machine', 'test-plan/check_test_plan.py (when against the stages that judged the row)')
for r, why in [('OUTPUT-SETTINGS', 'part-change although its unit depends on PROBE and DOCUMENT (the fixture feeds values directly)'),
               ('EXPORT-CLOCK', 'part-change although M-EXPORT-001 has providers (the clock is pure arithmetic)'),
               ('EXPORT-OUTPUT', 'acceptance only at depth L2'),
               ('ASSEMBLY-EXPORT', 'classification core while the verified E item is surface')]:
    put(f'CPPOLICY/CP-{r}-001', 'J', f'Departs from the statable rule: {why}; the choice rests on the row\'s fixture.', 'machine', 'test-plan/check_test_plan.py (when only)')

# routing
put('ROUTE/ROUTE-ECO', 'R', 'process-core refuses a commit under src/ or test/ without an open ECO (E01), so the ECO precedes the work order.', 'machine', 'process-core hook (E01)')
put('ROUTE/ROUTE-READ', 'R', 'The template routing\'s read step; the package is kit playbook 4.6\'s list.', 'none')
put('ROUTE/ROUTE-MANUFACTURE-001', 'C', 'Every unit and K item in one step (the template separates core and surface); statable.', 'none')
put('ROUTE/ROUTE-SELF-ACCEPTANCE', 'R', 'The template\'s self-acceptance step with the K-DOTNET commands.', 'none')
put('ROUTE/ROUTE-DELIVERY-COMMIT', 'J', 'An answer to the factory sandbox not writing .git (delivery 1); equipment knowledge outside the ruled input.', 'none')
put('ROUTE/ROUTE-INSPECT', 'R', 'The test plan\'s events decide the stages (written in 33 test_plan and test-plan.md).', 'none')

items = json.load(open(os.path.join(HERE, 'items.json'), encoding='utf-8'))['items']
ids = [i['id'] for i in items]
missing = [i for i in ids if i not in E]
extra = [i for i in E if i not in ids]
assert not missing and not extra, (missing, extra)
with open(os.path.join(HERE, 'classifier-1.json'), 'w', encoding='utf-8', newline='\n') as f:
    json.dump({'classifier': '1 (designer, this session)', 'items': [E[i] for i in ids]}, f, ensure_ascii=False, indent=1)
    f.write('\n')
counts = {}
for i in ids:
    counts[E[i]['class']] = counts.get(E[i]['class'], 0) + 1
print(len(ids), counts)
