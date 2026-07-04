#!/usr/bin/env python3
"""bomdd-init — 新規 BomDD プロジェクトのブートストラップ。

まっさらな環境で、プロダクトリポ(+GUI の場合は CAD リポ)を生成し、
テンプレ一式と運用プロファイル(CLAUDE.md / スキル / 変更管理手順)を配置する。

使い方:
    python method/tools/bomdd-init.py MyProduct --dir C:/repos [--gui|--no-gui] [--cad-name MyProductUI] [--no-git]

生成後にやることは画面表示とオンボーディング文書(method/onboarding/)を参照。
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

METHOD_ROOT = Path(__file__).resolve().parents[2]  # <BomDD リポ root>
TEMPLATES = METHOD_ROOT / "method" / "templates"
PROFILE = TEMPLATES / "product-profile"
ONBOARDING = METHOD_ROOT / "method" / "onboarding"

# 製品リポ bomdd/ へコピーするフェーズ成果物テンプレ(単一正本は method/templates/)
PHASE_TEMPLATE_GLOBS = ["[0-9][0-9]-*.md", "[0-9][0-9]-*.yaml", "README.md"]

SKILLS = ["bomdd-next", "eco-file", "eco-fix", "eco-accept", "sec-advisory"]


def render(src: Path, dst: Path, repl: dict[str, str]) -> None:
    text = src.read_text(encoding="utf-8")
    for key, val in repl.items():
        text = text.replace("{{" + key + "}}", val)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8", newline="\n")


def git(repo: Path, *args: str) -> bool:
    try:
        subprocess.run(["git", *args], cwd=repo, check=True,
                       capture_output=True, text=True)
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


def scaffold_product(root: Path, repl: dict[str, str]) -> None:
    bomdd = root / "bomdd"
    bomdd.mkdir(parents=True)
    for pattern in PHASE_TEMPLATE_GLOBS:
        for f in sorted(TEMPLATES.glob(pattern)):
            shutil.copy2(f, bomdd / f.name)
    # サブ配置(空ディレクトリは .gitkeep で保持)
    (bomdd / "db").mkdir()
    shutil.copy2(TEMPLATES / "db" / "schema-intent.md", bomdd / "db" / "schema-intent.md")
    for sub in ["plm-intake", "ui/mock", "reports"]:
        d = bomdd / sub
        d.mkdir(parents=True)
        (d / ".gitkeep").write_text("", encoding="utf-8")
    shutil.copy2(TEMPLATES / "ui" / "README.md", bomdd / "ui" / "README.md")
    # 運用プロファイル
    render(PROFILE / "CLAUDE.product.md", root / "CLAUDE.md", repl)
    render(PROFILE / "change-management.md", bomdd / "change-management.md", repl)
    for skill in SKILLS:
        render(PROFILE / "skills" / f"{skill}.md",
               root / ".claude" / "skills" / skill / "SKILL.md", repl)


def scaffold_cad(root: Path, repl: dict[str, str]) -> None:
    docs = root / "docs"
    for sub in ["screens", "decisions"]:
        d = docs / sub
        d.mkdir(parents=True)
        (d / ".gitkeep").write_text("", encoding="utf-8")
    mock_dir = root / "資料"
    mock_dir.mkdir()
    (mock_dir / ".gitkeep").write_text("", encoding="utf-8")
    render(PROFILE / "cad" / "02_mock_fidelity_policy.md",
           docs / "02_mock_fidelity_policy.md", repl)
    render(PROFILE / "cad" / "review_points.md", docs / "review_points.md", repl)
    render(PROFILE / "CLAUDE.cad.md", root / "CLAUDE.md", repl)


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    ap = argparse.ArgumentParser(description="BomDD 新規プロジェクト ブートストラップ")
    ap.add_argument("name", help="プロダクト名(リポジトリのディレクトリ名になる)")
    ap.add_argument("--dir", default=".", help="生成先の親ディレクトリ(既定: カレント)")
    gui = ap.add_mutually_exclusive_group()
    gui.add_argument("--gui", action="store_true", help="GUI アプリ(CAD リポも生成)")
    gui.add_argument("--no-gui", action="store_true", help="GUI なし(CAD リポを生成しない)")
    ap.add_argument("--cad-name", default=None, help="CAD リポ名(既定: <name>UI)")
    ap.add_argument("--no-git", action="store_true", help="git init/初回コミットを行わない")
    args = ap.parse_args()

    if args.gui or args.no_gui:
        is_gui = args.gui
    elif sys.stdin.isatty():
        is_gui = input("GUI アプリですか? (CAD リポも生成) [Y/n]: ").strip().lower() != "n"
    else:
        is_gui = True  # 非対話時の既定: GUI(不要なら --no-gui)

    parent = Path(args.dir).resolve()
    product_root = parent / args.name
    cad_name = args.cad_name or f"{args.name}UI"
    cad_root = parent / cad_name

    for target in [product_root] + ([cad_root] if is_gui else []):
        if target.exists():
            print(f"エラー: {target} は既に存在します(上書きしません)", file=sys.stderr)
            return 1
    if not PROFILE.is_dir():
        print(f"エラー: テンプレが見つかりません: {PROFILE}", file=sys.stderr)
        return 1

    repl = {
        "PRODUCT": args.name,
        "CAD": cad_name if is_gui else "(CAD なし — GUI 非対象)",
        "METHOD": str(METHOD_ROOT),
        "DATE": date.today().isoformat(),
    }

    scaffold_product(product_root, repl)
    if is_gui:
        scaffold_cad(cad_root, repl)

    committed = []
    if not args.no_git:
        for repo in [product_root] + ([cad_root] if is_gui else []):
            ok = git(repo, "init") and git(repo, "add", "-A") and git(
                repo, "commit", "-m", f"bomdd-init: scaffold ({date.today().isoformat()})")
            committed.append((repo.name, ok))

    w = print
    w()
    w(f"[ok] {product_root} を生成しました(bomdd/ テンプレ+運用プロファイル+スキル {len(SKILLS)} 本)")
    if is_gui:
        w(f"[ok] {cad_root} を生成しました(CAD: 権威宣言+裁定台帳+資料置き場)")
    for name, ok in committed:
        w(f"[git] {name}: {'初回コミット済み' if ok else 'git 初期化に失敗(手動で git init してください)'}")
    w()
    w("== 次にやること(人間) " + "=" * 40)
    w(f" 1. 仕様の種(既存メモ・チケット・議事録)を {product_root / 'bomdd' / 'plm-intake'} へ")
    if is_gui:
        w(f" 2. デザインツールで UI/UX を設計し、モックを {cad_root / '資料'} へ")
        w(f" 3. {product_root} を Claude Code 等で開き /bomdd-next を実行(Phase 0 から誘導されます)")
    else:
        w(f" 2. {product_root} を Claude Code 等で開き /bomdd-next を実行(Phase 0 から誘導されます)")
    w()
    w(" あなたの仕事は 2 つだけ: 裁定(選択肢から選ぶ)と golden(実機確認)。")
    w(" AI への頼み方は「症状・要求を書く。解決策を書かない」。詳細:")
    w(f"   {ONBOARDING / 'working-with-ai.md'}")
    w()
    w("== 完全な手順 " + "=" * 48)
    w(f" チェックリスト: {ONBOARDING / 'new-project-checklist.md'}")
    w(f" フェーズ手順:   {METHOD_ROOT / 'method' / 'prompts'}  (phase0-charter.md 〜 phase7-change-order.md)")
    w(f" playbook:       {METHOD_ROOT / 'method' / 'bomdd-playbook-v1.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
