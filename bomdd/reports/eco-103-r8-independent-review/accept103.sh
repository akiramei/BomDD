#!/usr/bin/env bash
# ECO-103 受入の実測 V1〜V3・V6(製造者)。使い方: bash accept103.sh <baseline> > accept-output.txt(BomDD のリポ直下から)
set -u
BASE=${1:-c41838a}
K=method/templates/product-profile
CM=$K/change-management.md
EF=$K/skills/eco-fix.md
OL=$K/operator-layer.md
echo "# ECO-103 accept measurements — $(date -Iseconds) — base $BASE — HEAD $(git rev-parse --short HEAD)"

echo "## V1 change-management の R8"
for p in 'R8' '文脈の独立' '設備の独立' 'R8 対象外' 'inspector' 'ECO-103' '未測定'; do
  echo "  [$p] lines in R8 item: $(awk '/^- \*\*R8 /{f=1} f&&/^## /{f=0} f' $CM | grep -c -F "$p")"
done
echo "  hunks in change-management.md:"; git diff -U0 $BASE -- $CM | grep '^@@'
echo "  removed lines (-): $(git diff -U0 $BASE -- $CM | grep -c '^-[^-]')"

echo "## V2 eco-fix の 3.6"
for p in 'R8' '停止点に進まない' 'R8 対象外'; do
  echo "  [$p] lines in 3.6: $(awk '/^3\.6\. /{f=1} /^4\. /{f=0} f' $EF | grep -c -F "$p")"
done
echo "  hunks in eco-fix.md:"; git diff -U0 $BASE -- $EF | grep '^@@'
python -c "import sys,yaml;t=open(sys.argv[1],encoding='utf-8').read().split('---')[1];d=yaml.safe_load(t);print('  frontmatter parse OK:',sorted(d), 'R8 in description:', 'R8' in d['description'])" $EF

echo "## V3 operator-layer"
echo "  hunks:"; git diff -U0 $BASE -- $OL | grep '^@@'
echo "  §4 (89-99) unchanged: $(diff <(git show $BASE:$OL | sed -n 89,99p) <(sed -n 89,99p $OL) >/dev/null && echo yes || echo NO)"

echo "## V6 diff window"
git diff --name-only $BASE
echo "## sha256 of the three files"
sha256sum $CM $EF $OL
