#!/usr/bin/env bash
# ECO-102: the measurements the order's §0.2 rests on, one command and its output each, taken on the ViewTube and ViewPrism2
# working trees (both unpushed, so the independent inspector cannot read them: the sha256 of each measured file is recorded here,
# and the matched lines themselves are copied beside this file). Run from the BomDD repository root.
set -u
VT=C:/Users/akira/source/repos/ViewTube
VP=C:/Users/akira/source/repos/ViewPrism2
HERE="$(cd "$(dirname "$0")" && pwd)"
run() { echo; echo "\$ $*"; eval "$@" 2>&1; echo "[exit $?]"; }
{
echo "date: $(date +%Y-%m-%dT%H:%M:%S%z)"
echo "ViewTube HEAD: $(git -C "$VT" rev-parse HEAD) (working tree: $(git -C "$VT" status --short -- bomdd | wc -l) modified paths under bomdd/)"
echo "ViewPrism2 HEAD: $(git -C "$VP" rev-parse HEAD) (working tree: $(git -C "$VP" status --short -- bomdd | wc -l) modified paths under bomdd/)"
echo
echo "== sha256 of the measured files"
(cd "$VT" && sha256sum bomdd/32-mbom.yaml bomdd/33-control-plan.yaml bomdd/50-as-built.yaml bomdd/52-metrics.yaml bomdd/31-kbom.yaml)
(cd "$VP" && sha256sum bomdd/32-mbom.yaml)
(cd "$HERE/../../.." && sha256sum method/templates/33-control-plan.yaml)
echo
echo "== M1: ViewTube M-BOM invariant lines, and how many begin with an ECO id"
run "grep -c \"^    - '\" $VT/bomdd/32-mbom.yaml"
run "grep -c \"^    - 'ECO-VT-\" $VT/bomdd/32-mbom.yaml"
echo "== M2: lines mentioning a measurement"
run "grep -ci measured $VT/bomdd/32-mbom.yaml"
echo "== M3: lines mentioning a review, a round or a finding id"
run "grep -cE 'review|R[0-9]+[a-z]-F[0-9]+|round' $VT/bomdd/32-mbom.yaml"
echo "== M4: lines with a not-exercised / not-covered note"
run "grep -ciE 'not exercised|not covered|not measured|unmeasured|no case|not captured|not yet' $VT/bomdd/32-mbom.yaml"
echo "== M5: lines mentioning a ruling"
run "grep -ci ruling $VT/bomdd/32-mbom.yaml"
echo "== M6: ViewTube As-Built and Metrics - size, entries, last change"
run "wc -l $VT/bomdd/50-as-built.yaml $VT/bomdd/52-metrics.yaml"
run "grep -c '^  - id: ' $VT/bomdd/50-as-built.yaml"
run "git -C $VT log --format='%h %ad' --date=short -1 -- bomdd/50-as-built.yaml"
echo "== M7: ViewTube Control Plan - learned acceptance characteristics and known_limits"
run "grep -c 'learned_acceptance_characteristics' $VT/bomdd/33-control-plan.yaml"
run "grep -c '^    - id: ECO-VT-' $VT/bomdd/33-control-plan.yaml"
run "grep -c 'known_limits' $VT/bomdd/33-control-plan.yaml"
echo "== M8: the 33 template has no known_limits field (before the manufacture)"
run "grep -c known_limits $HERE/../../../method/templates/33-control-plan.yaml"
echo "== M9: ViewPrism2 M-BOM - measurements and ECO references"
run "grep -ci measured $VP/bomdd/32-mbom.yaml"
run "grep -c 'ECO-' $VP/bomdd/32-mbom.yaml"
echo "== M10: K-BOM - no measured record (the word 'measured' and 'MEASURED' in the knowledge items)"
run "grep -ci measured $VT/bomdd/31-kbom.yaml"
echo "== copies of the matched lines (ViewTube 32-mbom: the invariant lines; 33: the known_limits lines)"
grep "^    - '" "$VT/bomdd/32-mbom.yaml" > "$HERE/viewtube-32-mbom-invariant-lines.txt"
grep -n "known_limits\|^    - id: ECO-VT-" "$VT/bomdd/33-control-plan.yaml" > "$HERE/viewtube-33-known-limits-lines.txt"
echo "written: viewtube-32-mbom-invariant-lines.txt ($(wc -l < "$HERE/viewtube-32-mbom-invariant-lines.txt") lines), viewtube-33-known-limits-lines.txt ($(wc -l < "$HERE/viewtube-33-known-limits-lines.txt") lines)"
} > "$HERE/measurements.txt" 2>&1
cat "$HERE/measurements.txt"
