# handover-stamp — 渡した版のうち、どれが動いたかを跡で確かめる(candidate・BomDD ECO-126)
#
# 周で回す変更(製品の変更管理手順 §3.5)で、人に渡すビルドのフォルダに
#   - handover.json  … 印(label)・この stamp の番号(stamp_id)・名指したファイルと起動するファイルの sha256
#   - launch.cmd / launch.sh … 起動口。起動のたびに「時刻・stamp_id・主ファイル名・その時点の主ファイルの sha256」を
#                              launch-log.tsv に 1 行足してから、プログラムを起動する
# を置く。返事が来たら check で、この stamp の起動の回数と、渡した版(handover.json)と一致するかを読む。
#
# 使い方:
#   python handover-stamp.py stamp --dir <ビルドのフォルダ> --program <起動するファイル> --file <主ファイル> [--file ...] --label <印>
#   python handover-stamp.py check --dir <ビルドのフォルダ>
#   python handover-stamp.py --selftest
#
# check の終了コード: 0 = この stamp の起動が 1 回以上あり、全部が渡した版と一致し、今のファイルも印と同じ
#                     1 = 一致しない起動がある・今のファイルが印と違う・跡に読めない行がある
#                     2 = 測れない(フォルダや handover.json が無い・形が違う・跡が読めない・使えないファイル名 = [input]、
#                         想定外の例外 = [internal])。**合格でも不合格でもない**
#                     3 = この stamp の起動口からの起動が 0 回(**不明** — 合格ではない)
# check の最後の「record line」を、周の記録(bomdd/loops/eco-NNN.yaml)の launches に写す。
#
# これは**測る**道具で、止めない。限界(宣言):
#   - 起動口を通さない起動(実行ファイルを直接開く)は跡を残さない。1 回でも起動口から起動していれば、その後の直接の起動は
#     見えないまま exit 0 になる。起動口からの起動が 0 回のときだけ「不明」と言える。
#   - 跡は書き換えられる(同じフォルダの素のファイル)。うっかりの取り違えを見つけるためのもので、改ざんは範囲外。
#   - ファイル名は、フォルダからの相対で、英数字と . _ - / だけ(起動口のスクリプトを OS の文字コードや記号の解釈に依らせない
#     ため)。印(label)は handover.json にだけ書き、跡の行には stamp_id を書く。
#   - 起動のたびに測るのは主ファイル(最初の --file)だけ。ほかの --file と起動するファイルは、stamp の時と check の時に測る
#     (起動と check のあいだに差し替えて戻されたものは見えない)。
#   - 同じフォルダに stamp し直すと、前の stamp の起動は「前の stamp の行」として数え、今の stamp の起動には入れない。
#   - 起動するファイルは実行ファイルを想定する。Windows でスクリプト(.cmd / .bat)を指すと、start が窓を開いたままにする
#     (スクリプトが自分で exit しない限り)。
#   - selftest は、いまの OS の起動口だけを通す(Windows なら launch.cmd)。もう一方は BomDD ECO-126 の V3 の記録。
#   - ファイル名の各区切りは、英数字か _ で始める(`./main.bin`・`.hidden/m.bin`・`bin\app.bin` は使えない)。
#   - selftest の腕が覆う範囲(BomDD ECO-126 の証拠 mutants_tools.py・2026-11-17 に実測): 検査を 1 つずつ外した写しのうち、
#     別の文脈の読みが作った 25 の 24 と、後から足した検査の 3 のすべてで、selftest が赤になった。赤にならなかった 1 つは
#     `..` の検査(ファイル名の形の検査が同じ名前を先に拒むので、外しても結果が変わらない)。写しの一覧に無い検査については、
#     何も言えない。POSIX の起動口(launch.sh)は、この selftest を POSIX で走らせたときだけ通る。

import argparse
import contextlib
import hashlib
import io
import json
import os
import re
import secrets
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

MANIFEST, LOG = "handover.json", "launch-log.tsv"
SCHEMA = "handover-stamp/0.2-candidate"
NAME_RE = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9._-]*(/[A-Za-z0-9_][A-Za-z0-9._-]*)*$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class InputError(Exception):
    pass


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _safe(name):
    """フォルダからの相対で、英数字と . _ - / だけ。親へ出る・絶対・記号つきの名前は使わない。"""
    return isinstance(name, str) and bool(NAME_RE.match(name)) and ".." not in name.split("/")


CMD = """@echo off
rem BomDD handover-stamp: logs which build ran, then starts it. Do not edit.
setlocal
set "D=%~dp0"
set "H=unreadable"
for /f "usebackq delims=" %%H in (`powershell -NoProfile -Command "(Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $env:D '{main_win}')).Hash.ToLower()"`) do set "H=%%H"
for /f "usebackq delims=" %%T in (`powershell -NoProfile -Command "[DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')"`) do set "T=%%T"
>>"%D%{log}" echo %T%	{stamp}	{main}	%H%
if defined HANDOVER_NO_START exit /b 0
start "" "%D%{program_win}" %*
"""
SH = """#!/bin/sh
# BomDD handover-stamp: logs which build ran, then starts it. Do not edit.
D="$(cd "$(dirname "$0")" && pwd)"
H="$( (sha256sum "$D/{main}" 2>/dev/null || shasum -a 256 "$D/{main}" 2>/dev/null) | cut -d' ' -f1 | tr -d '\\\\')"
T="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
printf '%s\\t%s\\t%s\\t%s\\n' "$T" "{stamp}" "{main}" "${{H:-unreadable}}" >> "$D/{log}"
[ -n "$HANDOVER_NO_START" ] && exit 0
exec "$D/{program}" "$@"
"""


def stamp(d, program, files, label):
    d = Path(d)
    if not d.is_dir():
        raise InputError(f"フォルダが無い: {d}")
    if not files:
        raise InputError("--file を 1 つ以上(最初のものが、起動のたびに測る主ファイル)")
    names = list(dict.fromkeys([*files, program]))   # 起動するファイルも印に入れる
    for name in names:
        if not _safe(name):
            raise InputError(f"ファイル名は、フォルダからの相対で、英数字と . _ - / だけ: {name!r}")
        if not (d / name).is_file():
            raise InputError(f"ファイルが無い: {d / name}")
    stamp_id = secrets.token_hex(6)
    manifest = {"schema": SCHEMA, "label": label, "stamp_id": stamp_id, "program": program, "main": files[0],
                "files": {name: sha256(d / name) for name in names},
                "stamped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    (d / MANIFEST).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    (d / "launch.cmd").write_text(CMD.format(main=files[0], main_win=files[0].replace("/", "\\"),
                                             program_win=program.replace("/", "\\"), log=LOG, stamp=stamp_id),
                                  encoding="ascii", newline="\r\n")
    sh = d / "launch.sh"
    sh.write_text(SH.format(main=files[0], program=program, log=LOG, stamp=stamp_id), encoding="ascii", newline="\n")
    try:
        os.chmod(sh, 0o755)
    except OSError:
        pass
    print(f"stamped: {label} [{stamp_id}] — {files[0]} {manifest['files'][files[0]][:16]}… ({len(names)} file(s)); "
          "launcher: launch.cmd / launch.sh")
    return 0


def _manifest(d):
    try:
        m = json.loads((d / MANIFEST).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise InputError(f"{MANIFEST} が読めない: {e}")
    ok = (isinstance(m, dict) and m.get("schema") == SCHEMA and isinstance(m.get("files"), dict) and m["files"]
          and isinstance(m.get("stamp_id"), str) and re.fullmatch(r"[0-9a-f]{12}", m["stamp_id"] or "")
          and all(_safe(n) and isinstance(h, str) and HEX64.match(h) for n, h in m["files"].items())
          and isinstance(m.get("main"), str) and isinstance(m.get("program"), str)
          and m["main"] in m["files"] and m["program"] in m["files"])
    if not ok:
        raise InputError(f"{MANIFEST} の形が違う(schema・stamp_id・files の sha256・main・program)")
    return m


def check(d):
    d = Path(d)
    if not d.is_dir():
        raise InputError(f"フォルダが無い: {d}")
    m = _manifest(d)
    want = m["files"][m["main"]]
    mine, earlier, broken = [], 0, []
    if (d / LOG).exists():
        try:
            log_text = (d / LOG).read_text(encoding="utf-8", errors="replace")
        except OSError as e:   # フォルダ・読めないファイル — 測れない(exit 2)。「違う版が動いた」(exit 1)と混ぜない
            raise InputError(f"{LOG} が読めない: {e}")
        for raw in log_text.splitlines():
            if not raw.strip():
                continue
            parts = raw.rstrip("\r\n").split("\t")
            if len(parts) != 4 or not re.fullmatch(r"[0-9a-f]{12}", parts[1].strip()):
                broken.append(raw)
            elif parts[1].strip() == m["stamp_id"]:
                mine.append([p.strip() for p in parts])
            else:
                earlier += 1
    match = [l for l in mine if l[2] == m["main"] and l[3].lower() == want]
    other = [l for l in mine if l not in match]
    now_diff = [n for n, h in m["files"].items() if not (d / n).is_file() or sha256(d / n) != h]
    print(f"handover: {m.get('label')} [{m['stamp_id']}] — stamped {m.get('stamped_at')} main {m['main']} {want[:16]}…")
    print(f"launches through the launcher for this stamp: {len(mine)} (matching the stamp {len(match)}, not matching {len(other)})")
    for t, _sid, n, h in other:
        print(f"  [mismatch] {t} {n} {h[:16]}… — 渡した版と違うものが動いた")
    if now_diff:
        print(f"  [changed] 今のファイルが印と違う: {', '.join(now_diff)}")
    if broken:
        print(f"  [malformed] 読めない行が {len(broken)} 行ある(跡が壊れている — 数に入れていない)")
    if earlier:
        print(f"  earlier stamps: {earlier} line(s) of other stamps in the same folder (not counted for this one)")
    if mine:
        print(f"  first {mine[0][0]} last {mine[-1][0]}")
    print(f"record line — launches: {{count: {len(mine)}, matching: {len(match)}}}")
    if other or now_diff or broken:
        return 1
    if not mine:
        print("unknown — この stamp の起動口からの起動が無い(直接起動された場合、動いた版は分からない。合格ではない)")
        return 3
    return 0


def _run_launcher(d):
    env = dict(os.environ, HANDOVER_NO_START="1")
    quiet = dict(env=env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
    if os.name == "nt":
        return subprocess.run(["cmd", "/c", str(d / "launch.cmd")], **quiet)
    return subprocess.run(["sh", str(d / "launch.sh")], **quiet)


def _selftest():
    bad, arms = [], [0, 0]   # [known-bad, known-good]

    def run(*a):
        return subprocess.run([sys.executable, __file__, *a], capture_output=True, text=True, encoding="utf-8", errors="replace")

    def arm(label, good, r, want, must=None):
        arms[1 if good else 0] += 1
        out = (r.stdout or "") + (r.stderr or "")
        musts = [must] if isinstance(must, str) else list(must or [])
        if r.returncode != want or any(m not in out for m in musts) or "Traceback" in out:
            bad.append(f"{label}: 期待 exit {want}{' と ' + repr(musts) if musts else ''}・実測 {r.returncode}"
                       + ("(例外で落ちた)" if "Traceback" in out else ""))

    def fresh(t, name):
        d = Path(t) / name
        d.mkdir()
        (d / "main.bin").write_bytes(b"build one")
        (d / "extra.bin").write_bytes(b"extra one")
        (d / "prog.cmd").write_text("@exit /b 0\r\n", encoding="ascii")
        return d

    def stamped(t, name):
        d = fresh(t, name)
        s = run("stamp", "--dir", str(d), "--program", "prog.cmd", "--file", "main.bin", "--file", "extra.bin", "--label", "selftest 周1")
        if s.returncode != 0:
            bad.append(f"stamp({name}): exit {s.returncode} {s.stdout}{s.stderr}")
        return d

    with tempfile.TemporaryDirectory(prefix="handover-stamp-st-") as t:
        d = stamped(t, "a")
        arm("known-bad: 起動なし → 不明", False, run("check", "--dir", str(d)), 3, "unknown")
        _run_launcher(d)
        arm("known-good: 起動 1 回・一致", True, run("check", "--dir", str(d)), 0, "launches: {count: 1, matching: 1}")
        (d / "main.bin").write_bytes(b"build two")
        _run_launcher(d)
        arm("known-bad: 別の版が動いた", False, run("check", "--dir", str(d)), 1,
            ("[mismatch]", "launches: {count: 2, matching: 1}"))
        (d / "main.bin").write_bytes(b"build one")
        arm("known-bad: 違う版が動いた後で、ファイルが元に戻された", False, run("check", "--dir", str(d)), 1,
            ("[mismatch]", "launches: {count: 2, matching: 1}"))

        d = stamped(t, "b")
        _run_launcher(d)
        (d / "extra.bin").write_bytes(b"extra two")
        arm("known-bad: 主でないファイルが印と違う", False, run("check", "--dir", str(d)), 1, "[changed] 今のファイルが印と違う: extra.bin")

        d = stamped(t, "c")
        _run_launcher(d)
        (d / "prog.cmd").write_text("@rem replaced\r\n@exit /b 0\r\n", encoding="ascii")
        arm("known-bad: 起動するファイルが差し替わった", False, run("check", "--dir", str(d)), 1, "prog.cmd")

        d = stamped(t, "d")
        _run_launcher(d)
        run("stamp", "--dir", str(d), "--program", "prog.cmd", "--file", "main.bin", "--label", "selftest 周2")
        arm("known-bad: stamp し直した後は、前の起動を今の版に数えない", False, run("check", "--dir", str(d)), 3, "earlier stamps: 1")

        d = stamped(t, "e")
        _run_launcher(d)
        with open(d / LOG, "a", encoding="utf-8") as f:
            f.write("not a launch line\n")
        arm("known-bad: 跡に読めない行", False, run("check", "--dir", str(d)), 1, "[malformed]")

        d = fresh(t, "f")
        (d / "名前.bin").write_bytes(b"x")
        arm("known-bad: ASCII でないファイル名(実在する)", False,
            run("stamp", "--dir", str(d), "--program", "prog.cmd", "--file", "名前.bin", "--label", "x"), 2, "英数字")
        (d / "a&b.bin").write_bytes(b"x")
        arm("known-bad: 記号を含むファイル名(実在する)", False,
            run("stamp", "--dir", str(d), "--program", "prog.cmd", "--file", "a&b.bin", "--label", "x"), 2, "英数字")
        arm("known-bad: 親へ出るファイル名", False,
            run("stamp", "--dir", str(d), "--program", "prog.cmd", "--file", "../a/main.bin", "--label", "x"), 2, "英数字")

        d = stamped(t, "g")
        (d / MANIFEST).write_text("[]\n", encoding="utf-8")
        arm("known-bad: handover.json の形が違う", False, run("check", "--dir", str(d)), 2, "形が違う")

        # --- ECO-126 の直し(2026-11-17): 例外で exit 1 になっていた入力と、selftest が覆っていなかった検査 ---
        d = stamped(t, "h")
        _run_launcher(d)
        (d / "extra.bin").unlink()
        arm("known-bad: 印に入れたファイルが無くなった", False, run("check", "--dir", str(d)), 1, "[changed] 今のファイルが印と違う: extra.bin")

        d = stamped(t, "i")
        _run_launcher(d)
        good = json.loads((d / MANIFEST).read_text(encoding="utf-8"))
        with open(d / LOG, "a", encoding="utf-8") as f:
            f.write(f"2026-01-01T00:00:00Z\tNOT-A-STAMP\tmain.bin\t{good['files']['main.bin']}\n")
        arm("known-bad: 跡の行の stamp_id が形になっていない", False, run("check", "--dir", str(d)), 1, "[malformed]")

        d = stamped(t, "j")
        _run_launcher(d)
        good = json.loads((d / MANIFEST).read_text(encoding="utf-8"))
        with open(d / LOG, "a", encoding="utf-8") as f:
            f.write(f"2026-01-01T00:00:00Z\t{good['stamp_id']}\tother.bin\t{good['files']['main.bin']}\n")
        arm("known-bad: 跡の行の主ファイル名が印と違う", False, run("check", "--dir", str(d)), 1,
            ("[mismatch]", "launches: {count: 2, matching: 1}"))

        d = fresh(t, "k")
        (d / "sub").mkdir()
        (d / "sub" / "main.bin").write_bytes(b"x")
        arm("known-bad: / で始まるファイル名", False,
            run("stamp", "--dir", str(d), "--program", "prog.cmd", "--file", "/main.bin", "--label", "x"), 2, "英数字")
        arm("known-bad: \\ で区切ったファイル名(実在する)", False,
            run("stamp", "--dir", str(d), "--program", "prog.cmd", "--file", "sub\\main.bin", "--label", "x"), 2, "英数字")
        arm("known-bad: 無いファイル", False,
            run("stamp", "--dir", str(d), "--program", "prog.cmd", "--file", "missing.bin", "--label", "x"), 2, "ファイルが無い")

        d = stamped(t, "m")
        _run_launcher(d)
        good = json.loads((d / MANIFEST).read_text(encoding="utf-8"))
        for label, key, value in (
                ("files の sha256 が形になっていない", "files", dict(good["files"], **{"main.bin": "zz"})),
                ("stamp_id が形になっていない", "stamp_id", "XYZ"),
                ("main が files に無い", "main", "ghost.bin"),
                ("schema が違う", "schema", "handover-stamp/other"),
                ("main が文字列でない(list)", "main", ["main.bin"]),
                ("program が文字列でない(数)", "program", 7)):
            (d / MANIFEST).write_text(json.dumps(dict(good, **{key: value})) + "\n", encoding="utf-8")
            arm(f"known-bad: handover.json の {label}", False, run("check", "--dir", str(d)), 2, "形が違う")

        d = stamped(t, "n")
        (d / LOG).mkdir()
        arm("known-bad: launch-log.tsv がフォルダ", False, run("check", "--dir", str(d)), 2, ("[input]", "読めない"))

    # 想定外の例外は、exit 1(「違う版が動いた」)にならない — main() の受け口を、check を例外に差し替えて通す
    def boom(_d):
        raise RuntimeError("selftest: unexpected")

    g, buf, code = globals(), io.StringIO(), None
    orig, argv = g["check"], sys.argv
    try:
        g["check"] = boom
        sys.argv = [argv[0], "check", "--dir", "."]
        with contextlib.redirect_stdout(buf):
            try:
                main()
                code = 0
            except SystemExit as e:
                code = e.code
            except Exception as e:
                code = f"例外が外へ出た({type(e).__name__})"
    finally:
        g["check"], sys.argv = orig, argv
    arms[0] += 1
    if code != 2 or "[internal]" not in buf.getvalue():
        bad.append(f"known-bad: 想定外の例外: 期待 exit 2 と '[internal]'・実測 {code}")
    if bad:
        print("selftest FAIL(計器を先に疑う): " + " / ".join(bad))
        return 1
    print(f"selftest PASS({sum(arms)} 腕: known-bad {arms[0]}・known-good {arms[1]} — いまの OS の起動口を HANDOVER_NO_START で通した)")
    return 0


def main():
    if "--selftest" in sys.argv[1:]:
        sys.exit(_selftest())
    ap = argparse.ArgumentParser(description="渡した版のうち、どれが動いたかを跡で確かめる(BomDD ECO-126)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("stamp")
    s.add_argument("--dir", required=True)
    s.add_argument("--program", required=True, help="起動するファイル(--dir からの相対)")
    s.add_argument("--file", action="append", default=[], help="sha256 を取るファイル(最初のものが主ファイル)")
    s.add_argument("--label", required=True, help="印(例: ECO-012 周 1)")
    c = sub.add_parser("check")
    c.add_argument("--dir", required=True)
    args = ap.parse_args()
    try:
        sys.exit(stamp(args.dir, args.program, args.file, args.label) if args.cmd == "stamp" else check(args.dir))
    except InputError as e:
        print(f"[input] {e}")
        sys.exit(2)
    except Exception as e:   # 想定外の例外を、Python の既定の exit 1(= 「違う版が動いた」)にしない
        print(f"[internal] 測れない — {type(e).__name__}: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()
