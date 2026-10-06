#!/usr/bin/env bash
# ECO-102: the measurements the order's §0.2 rests on, taken on the ViewTube and ViewPrism2 working trees (both unpushed, so the
# independent inspector cannot read them). r2 (after independent inspection r1 IA-01..03): the M-BOM is counted PER INVARIANT ENTRY
# (a multi-line YAML scalar), not per physical line as r1 did; every copy placed beside this file is complete (all physical lines of
# every entry) and its sha256 is recorded here; the K-BOM lines that carry the word 'measured' are copied so that the reading
# "they are knowledge sentences, not records of a measurement" can be checked. Run from the BomDD repository root.
set -u
VT=C:/Users/akira/source/repos/ViewTube
VP=C:/Users/akira/source/repos/ViewPrism2
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
run() { echo; echo "\$ $*"; eval "$@" 2>&1; echo "[exit $?]"; }
{
echo "date: $(date +%Y-%m-%dT%H:%M:%S%z)"
echo "ViewTube HEAD: $(git -C "$VT" rev-parse HEAD) (working tree: $(git -C "$VT" status --short -- bomdd | wc -l) modified paths under bomdd/)"
echo "ViewPrism2 HEAD: $(git -C "$VP" rev-parse HEAD) (working tree: $(git -C "$VP" status --short -- bomdd | wc -l) modified paths under bomdd/)"
echo
echo "== sha256 of the measured files (in their repositories)"
(cd "$VT" && sha256sum bomdd/32-mbom.yaml bomdd/33-control-plan.yaml bomdd/50-as-built.yaml bomdd/52-metrics.yaml bomdd/31-kbom.yaml)
(cd "$VP" && sha256sum bomdd/32-mbom.yaml)
(cd "$REPO" && sha256sum method/templates/33-control-plan.yaml)
echo
echo "== M1-M5: ViewTube M-BOM invariant ENTRIES (each entry = one list item under invariants:, all its physical lines), counted by python"
python "$HERE/count_entries.py" "$VT/bomdd/32-mbom.yaml" "$HERE/viewtube-32-mbom-invariant-entries.txt"
echo "[exit $?]"
echo "== M6: ViewTube As-Built and Metrics - size, entries, last change"
run "wc -l $VT/bomdd/50-as-built.yaml $VT/bomdd/52-metrics.yaml"
run "grep -c '^  - id: ' $VT/bomdd/50-as-built.yaml"
run "git -C $VT log --format='%h %ad' --date=short -1 -- bomdd/50-as-built.yaml"
echo "== M7: ViewTube Control Plan - rows carrying learned_acceptance_characteristics, the characteristics, and known_limits"
run "grep -c 'learned_acceptance_characteristics' $VT/bomdd/33-control-plan.yaml"
run "grep -c '^    - id: ECO-VT-' $VT/bomdd/33-control-plan.yaml"
run "grep -c 'known_limits' $VT/bomdd/33-control-plan.yaml"
echo "== M8: the 33 template had no known_limits field before the manufacture (measured at 37c4f82; at HEAD after the manufacture the field exists)"
run "git -C $REPO show 37c4f82:method/templates/33-control-plan.yaml | grep -c known_limits"
echo "== M9: ViewPrism2 M-BOM - the word 'measured' and ECO references (physical lines)"
run "grep -ci measured $VP/bomdd/32-mbom.yaml"
run "grep -c 'ECO-' $VP/bomdd/32-mbom.yaml"
echo "== M10: K-BOM - the lines carrying the word 'measured' (copied in full below); the reading: knowledge sentences, no date, value or revision of a measurement"
run "grep -n -i measured $VT/bomdd/31-kbom.yaml"
grep -n -i measured "$VT/bomdd/31-kbom.yaml" > "$HERE/viewtube-31-kbom-measured-lines.txt"
echo "== copies: the Control Plan's learned characteristic ids and known_limits lines (with line numbers)"
grep -n "known_limits\|^    - id: ECO-VT-" "$VT/bomdd/33-control-plan.yaml" > "$HERE/viewtube-33-known-limits-lines.txt"
echo
echo "== sha256 of the copies beside this file (compute and compare: cd bomdd/reports/eco-102-record-clause-home && sha256sum <file>)"
(cd "$HERE" && sha256sum viewtube-32-mbom-invariant-entries.txt viewtube-33-known-limits-lines.txt viewtube-31-kbom-measured-lines.txt)
} > "$HERE/measurements.txt" 2>&1
cat "$HERE/measurements.txt"
