"""Render mock.html from the harness's mockdata.json (definitions.md section 5). No reading, no choices.

    python gen_mock.py <mockdata.json> <mock.html>
"""
import html
import json
import sys


def render(mock):
    out = ['<!doctype html>', '<html lang="en"><head><meta charset="utf-8"><title>MoviePad mock (generated)</title></head>',
           '<body>']
    for st in mock["states"]:
        out.append(f'<section data-ui-state="{html.escape(st["id"])}">')
        for a in st["actions"]:
            attrs = [f'data-ui-action="{html.escape(a["id"])}"', f'data-ui-surface="{html.escape(a["surface"] or "")}"',
                     f'data-ui-enabled="{"true" if a["enabled"] else "false"}"', f'data-ui-goto="{html.escape(a["goto"])}"']
            out.append(f'  <button {" ".join(attrs)}>{html.escape(a.get("label") or "")}</button>')
        out.append('</section>')
    out.append('</body></html>')
    return "\n".join(out) + "\n"


def main():
    mock = json.load(open(sys.argv[1], encoding="utf-8"))
    with open(sys.argv[2], "w", encoding="utf-8", newline="\n") as f:
        f.write(render(mock))
    print(f"states {len(mock['states'])} elements {sum(len(s['actions']) for s in mock['states'])}")


if __name__ == "__main__":
    main()
