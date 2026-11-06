"""EXP-20261107-01 preparation (definitions.md sections 3, 5, 6).

    python prepare.py archive <staging>                      # git archive of MoviePad 126eae9 into <staging>/authority
    python prepare.py start-runs <runs.json>                 # one run with no presses (the start screen)
    python prepare.py start-screen <observed.json> <out>     # start-screen.json from that run's step 0
    python prepare.py package <staging>                      # the four writer folders K1 K2 C1 C2 (+ package-sha256.txt)
    python prepare.py verify <staging>                       # every packaged file still matches package-sha256.txt
    python prepare.py runs <examples.json> <runs.json>       # an examples.json as harness runs (one run per example)

Reads MoviePad and MoviePad-Remake by `git show` only; copies BehaviorForge's files, never writes there.
"""
import hashlib
import io
import json
import pathlib
import shutil
import subprocess
import sys
import tarfile

HERE = pathlib.Path(__file__).resolve().parent
REPOS = HERE.parents[3]
AUTHORITY = REPOS / "MoviePad"
AUTHORITY_COMMIT = "126eae9"
REMAKE = REPOS / "MoviePad-Remake"
REMAKE_COMMIT = "a2ca41e"
KIT = REPOS / "BehaviorForge"
ACTIONS = HERE.parent / "exp-20261030-05" / "writer" / "actions.json"
ACTIONS_SHA = "2351e73b40320b1bc2534e0ec4e6a66994cdf00fa5d1a7f6e341c431c7203e20"
KIT_FILES = [".gitignore", "AGENTS.md", "README.md", "docs/ai-onboarding.md", "docs/artifact-contract.md",
             "docs/publication.md", "docs/runbook.md", "docs/status.md", "examples/video-export.md", "prompts/review.md",
             "prompts/start.md", "templates/behavior-contract.md", "templates/domain-model.md", "templates/input-index.md",
             "templates/iteration-report.md", "templates/requirements.md", "templates/review-and-decisions.md",
             "templates/software-cad.md"]
WRITERS = {"K1": "k", "K2": "k", "C1": "c", "C2": "c"}
SETUP = [{"set": "ShowFfmpegSetup", "value": False}, {"set": "Playhead", "value": 20}]

# observation -> (view-model path, meaning shown to the writer). The paths are never given to a writer.
OBSERVATIONS = {
    "undo_enabled": ("CanUndo", "ツールバーの「Undo」(元に戻す)ボタンが使える"),
    "redo_enabled": ("CanRedo", "ツールバーの「Redo」(やり直す)ボタンが使える"),
    "split_enabled": ("CanSplit", "ツールバーの分割ボタン(再生ヘッドで区間を分割)が使える"),
    "merge_enabled": ("CanDeleteBoundary", "ツールバーの結合ボタン(選択中の区間を 1 つ前の区間と結合)が使える"),
    "trim_in_enabled": ("CanSetTrimIn", "ツールバーの In ボタン(トリム開始を再生ヘッドへ)が使える"),
    "trim_out_enabled": ("CanSetTrimOut", "ツールバーの Out ボタン(トリム終了を再生ヘッドへ)が使える"),
    "region_count": ("RegionCount", "タイムラインの区間の数"),
    "trim_start": ("TrimStart", "トリム開始(秒)"),
    "trim_end": ("TrimEnd", "トリム終了(秒)"),
    "output_length": ("OutputLength", "出力の長さ(秒・速度と除外を反映)"),
    "playhead": ("Playhead", "再生ヘッドの位置(秒)"),
    "selected_start": ("SelectedRegion.Start", "選択中の区間の開始(秒)"),
    "selected_end": ("SelectedRegion.End", "選択中の区間の終了(秒)"),
    "selected_speed": ("SelectedRegion.Speed", "選択中の区間の速度(倍)"),
    "selected_volume_percent": ("VolumeText", "選択中の区間の音量(%)"),
    "out_fps": ("OutFps", "出力フレームレート(fps)"),
    "out_width": ("OutW", "出力の幅(px)"),
    "out_height": ("OutH", "出力の高さ(px)"),
    "unsaved": ("Edited", "タイトル近くの状態表示が「未保存の変更」(false なら「保存済み」)"),
}
PATHS = [p for p, _ in OBSERVATIONS.values()]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def git_show(repo, commit, path):
    return subprocess.run(["git", "-C", str(repo), "show", f"{commit}:{path}"], capture_output=True, check=True).stdout


def write(p, b):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b)


def archive(staging):
    dest = pathlib.Path(staging) / "authority"
    if dest.exists():
        sys.exit(f"{dest} exists")
    tar = subprocess.run(["git", "-C", str(AUTHORITY), "archive", "--format=tar", AUTHORITY_COMMIT],
                         capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(tar)) as t:
        t.extractall(dest, filter="data")
    print("authority", dest, "files", sum(1 for _ in dest.rglob("*") if _.is_file()))


def start_runs(out):
    write(pathlib.Path(out), json.dumps({"paths": PATHS, "runs": [{"id": "START", "setup": SETUP, "actions": []}]},
                                        indent=1).encode())


def parse_value(name, s):
    if s is None or s == "":
        return None
    if name in ("undo_enabled", "redo_enabled", "split_enabled", "merge_enabled", "trim_in_enabled", "trim_out_enabled",
                "unsaved"):
        return {"True": True, "False": False}[s]
    v = float(s)
    return int(v) if v == int(v) else round(v, 3)


def start_screen(observed, out):
    obs = json.loads(pathlib.Path(observed).read_text(encoding="utf-8"))
    run = obs["runs"][0]
    if run["stopped"] or len(run["steps"]) != 1:
        sys.exit(f"start run did not complete: {run['stopped']}")
    vals = run["steps"][0]["values"]
    screen = {name: parse_value(name, vals[path]) for name, (path, _) in OBSERVATIONS.items()}
    write(pathlib.Path(out), (json.dumps({"note": "起動直後(サンプル動画・ffmpeg の案内を閉じ・再生ヘッド 20 秒)に観測した値",
                                          "values": screen}, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
    print(json.dumps(screen, ensure_ascii=False))


def package(staging):
    staging = pathlib.Path(staging)
    start = staging / "start-screen.json"
    if not start.is_file():
        sys.exit("start-screen.json first (definitions section 10 step 4)")
    actions = ACTIONS.read_bytes()
    if sha(actions) != ACTIONS_SHA:
        sys.exit("actions.json changed")
    observations = (json.dumps([{"name": n, "meaning": m} for n, (_, m) in OBSERVATIONS.items()], ensure_ascii=False,
                               indent=1) + "\n").encode("utf-8")
    common = (HERE / "prompts" / "common.md").read_bytes()
    files = {
        "sources/README.md": git_show(AUTHORITY, AUTHORITY_COMMIT, "README.md"),
        "sources/README.ja.md": git_show(AUTHORITY, AUTHORITY_COMMIT, "README.ja.md"),
        "sources/10-requirements.yaml": git_show(REMAKE, REMAKE_COMMIT, "bomdd/10-requirements.yaml"),
        "cad/actions.json": actions,
        "cad/observations.json": observations,
        "cad/start-screen.json": start.read_bytes(),
        "check_examples.py": (HERE / "check_examples.py").read_bytes(),
    }
    kit = {f"kit/{f}": (KIT / f).read_bytes() for f in KIT_FILES}
    lines = []
    for w, arm in WRITERS.items():
        d = staging / w
        if d.exists():
            sys.exit(f"{d} exists")
        prompt = (HERE / "prompts" / f"head-{arm}.md").read_bytes() + common
        mine = dict(files, **(kit if arm == "k" else {}))
        for rel, b in mine.items():
            write(d / rel, b)
            lines.append(f"{sha(b)}  {w}/{rel}")
        (d / "out").mkdir()
        write(staging / f"prompt-{w}.md", prompt)
        lines.append(f"{sha(prompt)}  prompt-{w}.md")
    write(staging / "package-sha256.txt", ("\n".join(lines) + "\n").encode())
    print("packaged", len(WRITERS), "writers,", len(lines), "hashed files; kit files", len(kit))


def verify(staging):
    staging = pathlib.Path(staging)
    bad = 0
    for line in (staging / "package-sha256.txt").read_text().splitlines():
        h, rel = line.split("  ", 1)
        p = staging / rel
        if not p.is_file() or sha(p.read_bytes()) != h:
            print("CHANGED", rel)
            bad += 1
    print("verify:", "OK" if not bad else f"{bad} changed")
    return 1 if bad else 0


def runs(examples, out):
    doc = json.loads(pathlib.Path(examples).read_text(encoding="utf-8"))
    rs = [{"id": ex["id"], "setup": SETUP, "actions": [s["action"] for s in ex["steps"] if s.get("action")]}
          for ex in doc["examples"]]
    write(pathlib.Path(out), json.dumps({"paths": PATHS, "runs": rs}, indent=1).encode())
    print("runs", len(rs))


if __name__ == "__main__":
    cmd, args = sys.argv[1], sys.argv[2:]
    sys.exit({"archive": archive, "start-runs": start_runs, "start-screen": start_screen, "package": package,
              "verify": verify, "runs": runs}[cmd](*args) or 0)
