#!/bin/sh
# 外部レビュー 論点 9 の再現(2026-10-03・製造者環境 Git Bash / Windows)。
# witness の生成経路(self-conformance.py _write_selfconf_witness: 実 index を一時 index へ複製 → git add -A → write-tree)を
# 隔離リポで模倣し、skip-worktree 付き entry では「検査した作業ツリーの bytes」でなく「index の bytes」が証明されることを示す。
# 使い方: sh witness-skip-worktree-repro.sh <空の作業ディレクトリ>
set -e
d=${1:?dir}
mkdir -p "$d" && cd "$d" && git init -q . && git config user.email t@t && git config user.name t
printf 'a: 1\n' > f.yaml && git add f.yaml && git commit -qm init
# index に不正 YAML(重複キー)を置き、skip-worktree を立て、作業ツリーを正しい YAML へ戻す
printf 'a: 1\na: 2\n' > f.yaml && git add f.yaml && git update-index --skip-worktree f.yaml && printf 'a: 1\n' > f.yaml
echo "--- worktree(C1 が読む側):"; cat f.yaml
echo "--- index blob:"; git cat-file -p "$(git ls-files -s f.yaml | awk '{print $2}')"
tmp=$(mktemp) && cp .git/index "$tmp"
GIT_INDEX_FILE=$tmp git add -A; echo "add exit=$?"
T=$(GIT_INDEX_FILE=$tmp git write-tree); echo "witness tree=$T"
echo "--- witness tree の blob(skip-worktree あり):"; git cat-file -p "$(git ls-tree "$T" | awk '{print $3}')"
echo "--- 対照(フラグなし):"
git update-index --no-skip-worktree f.yaml && tmp2=$(mktemp) && cp .git/index "$tmp2"
GIT_INDEX_FILE=$tmp2 git add -A && T2=$(GIT_INDEX_FILE=$tmp2 git write-tree)
git cat-file -p "$(git ls-tree "$T2" | awk '{print $3}')"
echo "--- 実 index は不変:"; git cat-file -p "$(git ls-files -s f.yaml | awk '{print $2}')"
rm -f "$tmp" "$tmp2"
# 実測 2026-10-03: skip-worktree あり → witness tree の blob= 'a: 1\na: 2'(index の不正 YAML)/ 対照 → 'a: 1'(作業ツリー)/ 実 index 不変。
