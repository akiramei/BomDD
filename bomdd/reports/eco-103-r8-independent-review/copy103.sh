#!/usr/bin/env bash
# ECO-103 の起票の根拠の写しと測定(読み取りだけ・ViewTube / ViewPrism2 には書き込まない)。
# 使い方: bash copy103.sh > measurements.txt   (BomDD のリポ直下から)
set -u
OUT=bomdd/reports/eco-103-r8-independent-review
VT=../ViewTube
VP=../ViewPrism2

echo "# ECO-103 measurements — $(date -Iseconds)"
echo "BomDD HEAD: $(git rev-parse HEAD)"
echo "ViewTube HEAD: $(git -C $VT rev-parse HEAD)  status: $(git -C $VT status -sb | head -1)"
echo "ViewPrism2 HEAD: $(git -C $VP rev-parse HEAD)  status: $(git -C $VP status -sb | head -1)"
echo

echo "## M1 ViewTube の R8(写し: viewtube-r8.txt)"
{
  echo "### ViewTube bomdd/process/change-management.md:103-117"
  sed -n 103,117p $VT/bomdd/process/change-management.md
  echo
  echo "### ViewTube AGENTS.md:23"
  sed -n 23p $VT/AGENTS.md
} > $OUT/viewtube-r8.txt
echo "source sha256: $(sha256sum $VT/bomdd/process/change-management.md | cut -c1-64)  change-management.md"
echo "source sha256: $(sha256sum $VT/AGENTS.md | cut -c1-64)  AGENTS.md"
echo

echo "## M2 ViewPrism2 の R8(写し: viewprism2-r8.txt)"
{
  echo "### ViewPrism2 .claude/skills/eco-fix/SKILL.md:55-66"
  sed -n 55,66p $VP/.claude/skills/eco-fix/SKILL.md
  echo
  echo "### ViewPrism2 で R8 の段を入れた commit"
  git -C $VP log --format='%h %ad %s' --date=short -S'セルフレビュー(R8' -- .claude/skills/eco-fix/SKILL.md | tail -1
} > $OUT/viewprism2-r8.txt
echo "source sha256: $(sha256sum $VP/.claude/skills/eco-fix/SKILL.md | cut -c1-64)  eco-fix/SKILL.md"
echo

echo "## M3 配布キットの現状(BomDD・grep)"
echo "kit eco-fix.md の R8|独立|fresh|異系統|セルフレビュー: $(grep -c -E 'R8|独立|fresh|異系統|セルフレビュー' method/templates/product-profile/skills/eco-fix.md)"
echo "kit change-management.md の 独立|independent|R8: $(grep -c -E '独立|independent|R8' method/templates/product-profile/change-management.md)"
echo "  (内訳: 該当行)"
grep -n -E '独立|independent|R8' method/templates/product-profile/change-management.md
echo "kit operator-layer.md:109 = $(sed -n 109p method/templates/product-profile/operator-layer.md)"
echo "kit operator-layer.md §4 不成立の条件 2 = $(sed -n 94p method/templates/product-profile/operator-layer.md)"
echo

echo "## M4 BomDD 自己適用の配員(register)"
echo "inspector: EQ- の行数: $(grep -c 'inspector: EQ' bomdd/60-change-register.yaml)"
echo "receipt_author_role の値: $(grep -o 'receipt_author_role: *[a-z]*' bomdd/60-change-register.yaml | sort | uniq -c | tr '\n' ' ')"
echo

echo "## 写しの sha256"
sha256sum $OUT/viewtube-r8.txt $OUT/viewprism2-r8.txt
