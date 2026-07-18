# negative control: 原品コピーへ故障 5 種を注入し、(1) 変異の適用を assert、
# (2) 変異体の観測可能な挙動が原品と実際に異なることを assert してから、oracle 較正に回す。
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORIG = Path("C:/Users/akira/source/repos/BomDD/method/tools/worklist.py")
MUT = HERE / "mutants"
MUT.mkdir(exist_ok=True)
FIX = HERE / "inspector" / "kit" / "fixtures"

src = ORIG.read_text(encoding="utf-8")

MUTS = {
    # M1 終了契約違反: 入力ファイル不在で exit 2(契約は exit 0)
    "m1-exit-contract": (
        "        return 0  # 読み取り専用ツール — ゲートとして使わない(v1 凍結)",
        "        return 2  # MUTANT",
    ),
    # M2 区分混同: PROMOTION DUE を actions due でなく validation warnings へ
    "m2-due-as-warning": (
        "            it[\"promotion_due\"] = True\n            dues.append(it)",
        "            it[\"promotion_due\"] = True\n            warnings.append((it[\"line_no\"], \"W4\", \"MUTANT due-as-warning\"))",
    ),
    # M3 stats キー欠落: validation_warnings 行を出力しない
    "m3-stats-key-missing": (
        "    w(f\"validation_warnings: {len(warnings)}\\n\")",
        "    pass",
    ),
    # M4 W1 検出除去: ID 重複を黙って受理
    "m4-w1-removed": (
        """    seen = {}
    for it in items:
        seen.setdefault(it["id"], []).append(it["line_no"])
    for id_, lines in seen.items():
        if len(lines) > 1:
            warnings.append((lines[1], "W1",
                             f"ID 重複: {id_}(L{', L'.join(map(str, lines))}"
                             " — 状態遷移は行内書き換え・行の複製禁止)"))""",
        "    seen = {}",
    ),
    # M5 除外領域無視: fenced code block 内も解析する
    # (blockquote 除去は fixtures 上で挙動差ゼロ= 無効変異と判明したため差し替え。
    #  引用行は「> -」始まりで bullet 正規表現に一致せず、除外の有無が観測に出ない)
    "m5-fence-parsed": (
        """        if FENCE_RE.match(line):
            in_fence = not in_fence
            attach = None
            continue
        if in_fence:
            continue
""",
        "",
    ),
}


def run(script, args):
    p = subprocess.run([sys.executable, str(script)] + args,
                       capture_output=True, text=True, encoding="utf-8")
    return p.returncode, p.stdout


probe = {
    "m1-exit-contract": [str(FIX / "does-not-exist.md")],
    "m2-due-as-warning": [str(FIX / "f1-normal.md")],
    "m3-stats-key-missing": [str(FIX / "f1-normal.md")],
    "m4-w1-removed": [str(FIX / "f2-warnings.md")],
    "m5-fence-parsed": [str(FIX / "f1-normal.md")],
}

print("== 変異の適用 assert(置換 1 件+挙動差)==")
all_ok = True
for name, (old, new) in MUTS.items():
    n = src.count(old)
    assert n == 1, f"{name}: 置換対象が {n} 件(1 件でなければ変異未適用/多重適用)"
    mutated = src.replace(old, new)
    path = MUT / f"{name}.py"
    path.write_text(mutated, encoding="utf-8")
    rc_o, out_o = run(ORIG, probe[name])
    rc_m, out_m = run(path, probe[name])
    differs = (rc_o != rc_m) or (out_o != out_m)
    print(f"{name}: 置換=1 件 / 挙動差={'あり' if differs else '★なし(未適用の偽陰性)'}"
          f" (exit {rc_o}->{rc_m})")
    all_ok = all_ok and differs
print("APPLY-ASSERT:", "PASS" if all_ok else "FAIL")
sys.exit(0 if all_ok else 1)
