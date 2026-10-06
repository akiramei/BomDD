#!/usr/bin/env bash
# ECO-102: the measurements the order's §0.2 rests on, taken on the ViewTube and ViewPrism2 working trees (both unpushed, so the
# independent inspector cannot read them). r3 (after independent inspection r2 IA-05 / IA-06, and r1 IA-01..03): the M-BOMs are
# parsed with PyYAML and counted per invariant ENTRY with a bilingual vocabulary (count_records.py); every counted text is copied
# beside this file in full; the ECO bodies and register entries behind the ViewTube entries are counted and one is copied as the
# example; the sha256 of every copy is recorded at the end. r2 counted only the quoted entries that begin with an ECO id (60) -
# the lists also hold unquoted entries. Run from the BomDD repository root.
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
(cd "$VT" && sha256sum bomdd/32-mbom.yaml bomdd/33-control-plan.yaml bomdd/50-as-built.yaml bomdd/52-metrics.yaml bomdd/31-kbom.yaml bomdd/process/change-register.yaml bomdd/eco/ECO-VT-232.md)
(cd "$VP" && sha256sum bomdd/32-mbom.yaml)
echo
echo "== M1-M5, M9, M11: the M-BOM invariant entries of both products (PyYAML), and the ECO bodies behind ViewTube's (count_records.py)"
python "$HERE/count_records.py" "$VT" "$VP" "$HERE"
echo "[exit $?]"
echo "== M6: ViewTube As-Built and Metrics - size, entries, last change"
run "wc -l $VT/bomdd/50-as-built.yaml $VT/bomdd/52-metrics.yaml"
run "grep -c '^  - id: ' $VT/bomdd/50-as-built.yaml"
run "git -C $VT log --format='%h %ad' --date=short -1 -- bomdd/50-as-built.yaml"
echo "== M7: ViewTube Control Plan - rows carrying learned_acceptance_characteristics, the characteristics, and known_limits"
run "grep -c 'learned_acceptance_characteristics' $VT/bomdd/33-control-plan.yaml"
run "grep -c '^    - id: ECO-VT-' $VT/bomdd/33-control-plan.yaml"
run "grep -c 'known_limits' $VT/bomdd/33-control-plan.yaml"
echo "== M8: the 33 template had no known_limits field before the manufacture (at the filing commit 37c4f82)"
run "git -C $REPO show 37c4f82:method/templates/33-control-plan.yaml | grep -c known_limits"
echo "== M10: K-BOM - the lines carrying the word 'measured' (copied in full); the reading: knowledge sentences, no date, value or revision of a measurement"
run "grep -n -i measured $VT/bomdd/31-kbom.yaml"
grep -n -i measured "$VT/bomdd/31-kbom.yaml" > "$HERE/viewtube-31-kbom-measured-lines.txt"
echo "== copies: the Control Plan's learned characteristic ids and known_limits lines (with line numbers)"
grep -n "known_limits\|^    - id: ECO-VT-" "$VT/bomdd/33-control-plan.yaml" > "$HERE/viewtube-33-known-limits-lines.txt"
echo
echo "== sha256 of the copies beside this file (compute and compare: cd bomdd/reports/eco-102-record-clause-home && sha256sum <file>)"
(cd "$HERE" && sha256sum viewtube-32-mbom-invariant-entries.txt viewprism2-32-mbom-invariant-entries.txt viewtube-eco-ids-of-the-entries.txt viewtube-eco-vt-232-body.md viewtube-register-eco-vt-232.yaml viewtube-33-known-limits-lines.txt viewtube-31-kbom-measured-lines.txt)
} > "$HERE/measurements.txt" 2>&1
cat "$HERE/measurements.txt"
