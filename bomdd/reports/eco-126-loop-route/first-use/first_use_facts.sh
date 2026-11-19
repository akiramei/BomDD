#!/usr/bin/env bash
# ECO-126 section 10: facts of the first use of the route in a product (MoviePad ECO-007 / ECO-008).
# Read-only on both repositories. Writes three text files beside this script.
# usage: bash first_use_facts.sh <BomDD checkout> <MoviePad checkout>
set -u
BD="$1"; MP="$2"
HERE="$(cd "$(dirname "$0")" && pwd)"
export PYTHONIOENCODING=utf-8 PYTHONDONTWRITEBYTECODE=1
KIT=7943c6403297cb05a6a19b75596fd770e8c387da

{
  echo "== MoviePad HEAD"
  git -C "$MP" rev-parse HEAD
  git -C "$MP" rev-parse --abbrev-ref HEAD
  echo "== MoviePad: tracked files modified (expected: none)"
  git -C "$MP" status --porcelain --untracked-files=no
  echo "== MoviePad main, first parent"
  git -C "$MP" log --format='%H %cI %s' --first-parent -2 HEAD
  echo "== accept commits (by trailer)"
  git -C "$MP" log --format='%H %cI' --grep='BomDD-ECO-Accept: ECO-007' -1 HEAD
  git -C "$MP" log --format='%H %cI' --grep='BomDD-ECO-Accept: ECO-008' -1 HEAD
  echo "== ECO-008 window 68f565c..c2da245: commits, and the round candidates"
  git -C "$MP" rev-list --count 68f565c..c2da245
  git -C "$MP" log --format='%h %cI' --grep='^fix(eco-008): ' 68f565c..c2da245
  echo "== blobs at HEAD"
  for f in bomdd/60-change-order-eco-007.md bomdd/60-change-order-eco-008.md bomdd/loops/eco-008.yaml bomdd.lock; do
    echo "$f $(git -C "$MP" rev-parse "HEAD:$f")"
  done
  echo "== the lock's method commit"
  git -C "$MP" show HEAD:bomdd.lock | grep -E 'commit:|dirty:|files:'
  echo "== kit tools: blob in BomDD at $KIT / blob in MoviePad at HEAD"
  for f in loop-count.py handover-stamp.py ui-cad-gate.py; do
    a=$(git -C "$BD" rev-parse "$KIT:method/tools/$f")
    b=$(git -C "$MP" rev-parse "HEAD:bomdd-kit/method/tools/$f")
    if [ "$a" = "$b" ]; then s=same; else s=DIFFERENT; fi
    echo "$f $a $b $s"
  done
  for f in skills/eco-turn.md change-management.md; do
    a=$(git -C "$BD" rev-parse "$KIT:method/templates/product-profile/$f")
    b=$(git -C "$MP" rev-parse "HEAD:bomdd-kit/method/templates/product-profile/$f")
    if [ "$a" = "$b" ]; then s=same; else s=DIFFERENT; fi
    echo "product-profile/$f $a $b $s"
  done
} > "$HERE/moviepad-identity.txt" 2>&1

cd "$MP" || exit 2
{
  python bomdd-kit/method/tools/loop-count.py --check bomdd/loops/eco-008.yaml
  echo "exit=$?"
} > "$HERE/moviepad-eco-008-loop-count.txt" 2>&1
{
  python bomdd-kit/method/tools/ui-cad-gate.py --ui-dir bomdd/ui --mock bomdd/ui/snapshot-main.html
  echo "exit=$?"
} > "$HERE/moviepad-eco-008-ui-cad-gate.txt" 2>&1
echo "== MoviePad after (expected: unchanged)"
git -C "$MP" status -sb
wc -l "$HERE"/moviepad-*.txt
