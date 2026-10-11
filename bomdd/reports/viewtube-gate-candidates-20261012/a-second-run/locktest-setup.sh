#!/bin/sh
# Builds a tiny repository and checks, for three commit modes, whether the index can change
# between the pre-commit hook and the commit-msg hook (a "foreign" git add from the editor step).
set -u
BASE="$(cd "$(dirname "$0")" && pwd)"
R="$BASE/repo"
rm -rf "$R"
mkdir -p "$R"
cd "$R" || exit 1
git init -q
git config user.name t
git config user.email t@t.invalid
git config core.autocrlf false
mkdir hooks
cat >hooks/pre-commit <<'EOF'
#!/bin/sh
echo "  [pre-commit] GIT_INDEX_FILE=${GIT_INDEX_FILE:-unset} lock=$( [ -f .git/index.lock ] && echo held || echo free ) staged=$(git diff --cached --name-only | tr '\n' ' ')"
EOF
cat >hooks/prepare-commit-msg <<'EOF'
#!/bin/sh
echo "  [prepare-commit-msg] lock=$( [ -f .git/index.lock ] && echo held || echo free )"
EOF
cat >hooks/commit-msg <<'EOF'
#!/bin/sh
echo "  [commit-msg] GIT_INDEX_FILE=${GIT_INDEX_FILE:-unset} lock=$( [ -f .git/index.lock ] && echo held || echo free ) staged=$(git diff --cached --name-only | tr '\n' ' ')"
EOF
cat >editor.sh <<'EOF'
#!/bin/sh
# A foreign process: no GIT_INDEX_FILE inherited, stages b.txt into the real index.
( unset GIT_INDEX_FILE; cd "$(git rev-parse --show-toplevel)" && git add b.txt ) >/dev/null 2>"$1.err"
echo "  [editor] foreign 'git add b.txt' exit=$? $(head -c 120 "$1.err" | tr '\n' ' ')"
echo "msg" >"$1"
EOF
chmod +x hooks/* editor.sh
git config core.hooksPath hooks
echo a >a.txt
echo base >b.txt
git add a.txt b.txt hooks editor.sh
git commit -q -m init --no-verify
run() {
  mode="$1"; shift
  echo "== $mode"
  echo "x$mode" >>a.txt
  echo "y$mode" >>b.txt
  git add a.txt
  GIT_EDITOR="$R/editor.sh" git commit -q "$@"
  echo "  committed tree contains b.txt change: $(git show --stat --format= HEAD | grep -c 'b.txt')"
  echo "  real index after commit, b.txt staged vs HEAD: $(git diff --cached --name-only | tr '\n' ' ')"
  git reset -q --hard HEAD
}
run plain
run all -a
run pathspec a.txt
