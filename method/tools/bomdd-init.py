#!/usr/bin/env python3
"""bomdd-init — 新規 BomDD プロジェクトのブートストラップ。

まっさらな環境で、プロダクトリポ(+GUI の場合は CAD リポ)を生成し、
テンプレ一式と運用プロファイル(CLAUDE.md / スキル / 変更管理手順)を配置する。

使い方:
    python method/tools/bomdd-init.py MyProduct --dir C:/repos [--gui|--no-gui] [--cad-name MyProductUI] [--no-git]

生成後にやることは画面表示とオンボーディング文書(method/onboarding/)を参照。

版固定(harness ECO-004・2026-07-10 外部レビュー所見2):
    生成物は方法論リポへの絶対パスで結合しない。方法論(method/ 全体)を
    同梱 kit(bomdd-kit/)として製品リポへ凍結コピーし、{{METHOD}} はその相対パスに
    置換する。kit の出自(方法論リポの commit・dirty)と内容ハッシュは bomdd.lock に
    記録する — 方法論リポの更新が既存製品の手順を無記録で変えない(凍結・来歴・再現性)。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

METHOD_ROOT = Path(__file__).resolve().parents[2]  # <BomDD リポ root>
TEMPLATES = METHOD_ROOT / "method" / "templates"
PROFILE = TEMPLATES / "product-profile"
ONBOARDING = METHOD_ROOT / "method" / "onboarding"

KIT_DIRNAME = "bomdd-kit"  # 生成先リポ内の方法論同梱先({{METHOD}} の置換値)

# 製品リポ bomdd/ へコピーするフェーズ成果物テンプレ(単一正本は method/templates/)
PHASE_TEMPLATE_GLOBS = ["[0-9][0-9]-*.md", "[0-9][0-9]-*.yaml", "README.md"]

SKILLS = ["bomdd-next", "eco-file", "eco-fix", "eco-accept", "sec-advisory",
          "bomdd-refmodel", "bomdd-mock-lint", "bomdd-ui-cad"]


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


def _method_provenance() -> dict[str, object]:
    """方法論リポの版来歴。git 不在でも止めず not-computed を正直記録(t3 様式)"""
    def g(*args: str) -> str | None:
        try:  # ECO-009 #1: git 実行ファイル不在(OSError)も「失敗」= None — 約束どおり止めない
            p = subprocess.run(["git", "-C", str(METHOD_ROOT), *args],
                               capture_output=True, text=True, encoding="utf-8")
        except OSError:
            return None
        return p.stdout.strip() if p.returncode == 0 else None
    commit = g("rev-parse", "HEAD")
    if commit is None:
        return {"commit": "not-computed(git unavailable or not a git checkout)", "dirty": "unknown"}
    st = g("status", "--porcelain")
    # ECO-009 #3: status 失敗(None)は clean(False)と区別して unknown を正直記録
    return {"commit": commit, "dirty": bool(st) if st is not None else "unknown"}


def _skills_table(skills: list[str]) -> str:
    """AGENTS.md 用のスキル表(実設置分のみ — ECO-009 #4 と同族の正直記録。ECO-010)"""
    if not skills:
        return "(このリポに入口スキルは設置されていない)"
    rows = "\n".join(f"| `/{s}` | [.claude/skills/{s}/SKILL.md](.claude/skills/{s}/SKILL.md) |"
                     for s in skills)
    return "| コマンド | 手順書(正本) |\n|---|---|\n" + rows


def install_agents(root: Path, template: str, repl: dict[str, str], skills: list[str]) -> None:
    """ハーネス中立の入口 AGENTS.md を生成(ECO-010)。既存は保持(kit と同じ fail-safe)"""
    dst = root / "AGENTS.md"
    if dst.exists():
        print(f"[agents] {dst} は既存のため保持")
        return
    render(PROFILE / template, dst, {**repl, "SKILLS_TABLE": _skills_table(skills)})


def _kit_integrity_problems(root: Path, kit: Path) -> list[str]:
    """既存 kit の完全性検査(ECO-009 #2)。問題を列挙(空リスト=健全)"""
    problems: list[str] = []
    manifest_path = kit / "kit-manifest.json"
    lock_path = root / "bomdd.lock"
    manifest = None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except OSError:
        problems.append("kit-manifest.json がない/読めない")
    except json.JSONDecodeError:
        problems.append("kit-manifest.json がパース不能")
    try:
        m = re.search(r"^\s*files:\s*(\d+)\s*$", lock_path.read_text(encoding="utf-8"), re.M)
        if not m:
            problems.append("bomdd.lock に kit files 数がない")
        elif manifest is not None and int(m.group(1)) != len(manifest.get("files") or {}):
            problems.append(f"lock の files={m.group(1)} と manifest の実数 {len(manifest.get('files') or {})} が不一致")
    except OSError:
        problems.append("bomdd.lock がない/読めない")
    return problems


def install_kit(root: Path, created: str, skills: list[str]) -> None:
    """method/ 全体を凍結コピーし、per-file sha256 manifest と bomdd.lock を書く"""
    kit = root / KIT_DIRNAME
    if kit.exists():
        # ECO-009 #2: 存在でなく完全性を検査 — 中断の残骸(manifest/lock 欠落)の黙認は fail-open
        problems = _kit_integrity_problems(root, kit)
        if problems:
            sys.exit(f"エラー: 既存の {kit} が不完全({'・'.join(problems)})。"
                     f"復旧するには {KIT_DIRNAME}/ と bomdd.lock を削除して再実行してください")
        print(f"[kit] {kit} は既存のため保持(方法論の版を更新する場合は {KIT_DIRNAME}/ と bomdd.lock を削除して再実行)")
        return
    shutil.copytree(METHOD_ROOT / "method", kit / "method",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    manifest: dict[str, str] = {}
    for f in sorted(kit.rglob("*")):
        if f.is_file():
            manifest[f.relative_to(kit).as_posix()] = hashlib.sha256(f.read_bytes()).hexdigest()
    prov = _method_provenance()
    manifest_path = kit / "kit-manifest.json"
    manifest_path.write_text(
        json.dumps({"created": created, "method_commit": prov["commit"], "files": manifest},
                   ensure_ascii=False, indent=1),
        encoding="utf-8", newline="\n")
    dirty = prov["dirty"]
    dirty_yaml = str(dirty).lower() if isinstance(dirty, bool) else f'"{dirty}"'
    commit = str(prov["commit"])
    lock = (
        "# bomdd.lock — 方法論の版固定(harness ECO-004)\n"
        f"# 実行時に参照する方法論は同梱 kit({KIT_DIRNAME}/)のみ — 方法論リポの更新は本製品に波及しない。\n"
        "# origin_path は来歴(教訓の一般形昇格の送り先)であって実行時依存ではない。\n"
        "bomdd_lock:\n"
        f"  created: \"{created}\"\n"
        "  method:\n"
        f"    origin_path: \"{METHOD_ROOT.as_posix()}\"\n"
        f"    commit: \"{commit}\"\n"
        f"    dirty: {dirty_yaml}\n"
        "  kit:\n"
        f"    root: {KIT_DIRNAME}\n"
        f"    files: {len(manifest)}\n"
        f"    manifest: {KIT_DIRNAME}/kit-manifest.json\n"
        f"    manifest_sha256: \"{hashlib.sha256(manifest_path.read_bytes()).hexdigest()}\"\n"
        "  adapter:\n"
        f"    skills: [{', '.join(skills)}]\n"  # ECO-009 #4: 実設置スキル(全 SKILLS 固定は --skills 部分集合・CAD で嘘になる)
        "  runtime:\n"
        f"    python: \"{sys.version.split()[0]}\"\n"
    )
    (root / "bomdd.lock").write_text(lock, encoding="utf-8", newline="\n")
    if dirty is True:
        print("[warn] 方法論リポに未コミット変更あり — kit は dirty スナップショット(bomdd.lock に記録済み)")
    print(f"[kit] 方法論 kit を同梱しました({len(manifest)} files・method commit {commit[:9]})")


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
    install_agents(root, "AGENTS.product.md", repl, SKILLS)
    install_kit(root, repl["DATE"], SKILLS)


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
    install_agents(root, "AGENTS.cad.md", repl, [])  # CAD 用内容(スキルなし・裁定台帳参照。ECO-010)
    install_kit(root, repl["DATE"], [])  # CAD リポにスキルは設置しない — lock も空を正直記録(ECO-009 #4)


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
    ap.add_argument("--skills-only", action="store_true",
                    help="既存の製品リポへ運用スキルのみ設置(scaffold しない。name は既存ディレクトリ)")
    ap.add_argument("--skills", default=None,
                    help="--skills-only で設置するスキルをカンマ区切りで限定(既定: 全部)")
    args = ap.parse_args()

    if args.skills_only:
        root = (Path(args.dir).resolve() / args.name)
        if not root.is_dir():
            print(f"エラー: {root} が存在しません(--skills-only は既存リポ向け)", file=sys.stderr)
            return 1
        selected = [s.strip() for s in args.skills.split(",")] if args.skills else SKILLS
        unknown = [s for s in selected if s not in SKILLS]
        if unknown:
            print(f"エラー: 未知のスキル: {unknown}(候補: {SKILLS})", file=sys.stderr)
            return 1
        repl = {"PRODUCT": args.name, "CAD": args.cad_name or f"{args.name}UI",
                "METHOD": KIT_DIRNAME, "DATE": date.today().isoformat()}
        for skill in selected:
            render(PROFILE / "skills" / f"{skill}.md",
                   root / ".claude" / "skills" / skill / "SKILL.md", repl)
        install_agents(root, "AGENTS.product.md", repl, selected)
        install_kit(root, repl["DATE"], selected)
        print(f"[ok] {root} へスキル {len(selected)} 本を設置しました(コミットは手動で)")
        return 0

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
        "METHOD": KIT_DIRNAME,
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
    w(f"   {KIT_DIRNAME}/method/onboarding/working-with-ai.md")  # ECO-009 #5: 兄弟行と同じ kit 相対
    w()
    w("== 完全な手順(すべて製品リポ同梱の kit 内 — 版は bomdd.lock)" + "=" * 12)
    w(f" チェックリスト: {KIT_DIRNAME}/method/onboarding/new-project-checklist.md")
    w(f" フェーズ手順:   {KIT_DIRNAME}/method/prompts/  (phase0-charter.md 〜 phase7-change-order.md)")
    w(f" playbook:       {KIT_DIRNAME}/method/bomdd-playbook-v1.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
