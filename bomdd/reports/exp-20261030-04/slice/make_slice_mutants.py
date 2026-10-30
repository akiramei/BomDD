import json, pathlib, re, sys
d = pathlib.Path(sys.argv[1])
clean = (d / "mock.html").read_text(encoding="utf-8")
sec = lambda s: re.search(r'<section data-ui-state="%s">.*?</section>' % s, clean, re.S)

def in_state(state, f):
    m = sec(state)
    return clean[:m.start()] + f(m.group(0)) + clean[m.end():]

muts = {
    "a1": ("a", in_state("edit-split", lambda t: t.replace('data-ui-action="Undo" data-ui-surface="ToolbarView" data-ui-enabled="true"',
                                                         'data-ui-action="Undo" data-ui-surface="ToolbarView" data-ui-enabled="false"'))),
    "b1": ("b", re.sub(r'\s*<button data-ui-action="ApplySpeedPreset:0.5"[^>]*>[^<]*</button>', "", clean)),
    "c1": ("c", re.sub(r'\s*<button data-ui-action="Undo"[^>]*>[^<]*</button>', "", clean)),
    "d1": ("d", clean.replace('data-ui-action="Split" data-ui-surface="ToolbarView"', 'data-ui-action="Split" data-ui-surface="InspectorView"')),
    "e1": ("e", in_state("edit-fresh", lambda t: t.replace('data-ui-action="Split" data-ui-surface="ToolbarView" data-ui-enabled="true" data-ui-goto="edit-split"',
                                                         'data-ui-action="Split" data-ui-surface="ToolbarView" data-ui-enabled="true" data-ui-goto="edit-undone"'))),
    "f1": ("f", clean.replace(">Undo</button>", ">Revert</button>")),
}
rows = []
for mid, (cls, text) in muts.items():
    assert text != clean, mid
    (d / "mutants").mkdir(exist_ok=True)
    (d / "mutants" / f"{mid}.html").write_text(text, encoding="utf-8", newline="\n")
    rows.append({"id": mid, "class": cls, "file": f"{mid}.html", "what": "slice"})
(d / "mutants.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
print(len(rows))
