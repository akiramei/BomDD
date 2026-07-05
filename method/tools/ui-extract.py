# ui-extract — UI モックの決定的 raw 抽出治具(PR-2・candidate)
#
# HTML モックから「機械的に確定できる事実」だけを ui-ir.raw.json として抽出する。
# AI は使わない。同じ HTML からは常に同じ出力(同じ nodeId / rawActionId)が出る。
# これにより stable id の維持が AI の自制心ではなく治具の性質になる(ui-ir-ui-bom.md §12)。
#
# 使い方:
#   python ui-extract.py <mock.html> [-o ui-ir.raw.json]        # 抽出(省略時 stdout)
#   python ui-extract.py <mock.html> --verify <ui-ir.raw.json>  # GU6: 再抽出して id 揺れを検査
#
# 抽出規約(candidate — 変更する場合は fork して宣言):
#  1. nodeId は data-ui-id があればそれを優先("UI:" 接頭辞)。なければ DOM パス+タグの
#     sha1 先頭 8 桁("DOM-" 接頭辞)。同一 HTML → 同一 id は保証するが、モック改変
#     (要素挿入等)への耐性は限定的。改変時の追跡は --verify の差分で行う(候補記録:
#     テキスト/属性由来の fingerprint 強化は揺れが実測されてから)。
#  2. interactable 判定: button/select/textarea/a[href]/input(hidden 除く)/
#     on{click,change,submit,input} 属性/contenteditable/data-ui-action/
#     role∈{button,link,menuitem,menuitemcheckbox,tab,checkbox,switch,option,combobox}/
#     data-snap-cursor∈{pointer,*-resize,grab,grabbing,move,crosshair}。
#     data-snap-cursor は DOM スナップショット治具が computed style の cursor を焼き込んだもの。
#     フレームワーク(React 等)が JS でリスナーを付ける要素は静的属性に痕跡が無く、
#     これが無いと丸ごと漏れる(X1 実例第1号: MoviePad モックの region/bound/trim-h/
#     カスタムラジオ。2026-07-05)。cursor=text は caret 表示と曖昧なため採用しない。
#  3. rawActionId は文書順に RAW-ACT-0001 から採番(決定的)。
#  4. surfaceLabel は textContent → aria-label → placeholder → value → title → name の順。
#  5. 出力にタイムスタンプを含めない(決定性の保証。時刻が要るなら外側で記録する)。
#  6. script/style の中身は捨てる。整形式でない HTML(暗黙閉じタグ)の解釈は
#     html.parser 準拠であり、限界はモック側の整形で吸収する。
#
# 終了コード: 0 = 成功 / 1 = --verify で id 揺れ検出 / 2 = 入力エラー

import argparse
import hashlib
import json
import sys
from html.parser import HTMLParser
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SCHEMA = "0.1-candidate"

VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input",
             "link", "meta", "param", "source", "track", "wbr"}
SKIP_CONTENT_TAGS = {"script", "style"}
INTERACTABLE_ROLES = {"button", "link", "menuitem", "menuitemcheckbox", "tab",
                      "checkbox", "switch", "option", "combobox"}
EVENT_ATTRS = {"onclick": "click", "onchange": "change",
               "onsubmit": "submit", "oninput": "input"}
SNAP_CURSOR_INTERACTIVE = {"pointer", "ew-resize", "ns-resize", "col-resize",
                           "row-resize", "grab", "grabbing", "move", "crosshair"}
SNAP_CURSOR_DRAG = {"ew-resize", "ns-resize", "col-resize", "row-resize",
                    "grab", "grabbing", "move"}
CAPTURED_ATTR_PREFIXES = ("aria-", "data-", "on")
CAPTURED_ATTRS = {"id", "class", "name", "type", "value", "placeholder", "href",
                  "role", "title", "for", "disabled", "checked", "selected",
                  "contenteditable", "draggable", "tabindex"}


def norm_text(s):
    return " ".join(s.split())


class Node:
    __slots__ = ("tag", "attrs", "dom_path", "parent", "children", "texts")

    def __init__(self, tag, attrs, dom_path, parent):
        self.tag = tag
        self.attrs = attrs
        self.dom_path = dom_path
        self.parent = parent
        self.children = []
        self.texts = []

    def text_content(self):
        parts = list(self.texts)
        for c in self.children:
            parts.append(c.text_content())
        return norm_text(" ".join(p for p in parts if p))


class Extractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # [(Node, {tag: count})]
        self.roots = []
        self.all_nodes = []      # 文書順
        self.root_counts = {}
        self.skip_depth = 0

    def _make_node(self, tag, attrs):
        attr_dict = {}
        for k, v in attrs:
            attr_dict[k] = v if v is not None else "true"
        if self.stack:
            parent, counts = self.stack[-1]
        else:
            parent, counts = None, self.root_counts
        counts[tag] = counts.get(tag, 0) + 1
        seg = f"{tag}[{counts[tag]}]"
        dom_path = f"{parent.dom_path}/{seg}" if parent else seg
        node = Node(tag, attr_dict, dom_path, parent)
        if parent:
            parent.children.append(node)
        else:
            self.roots.append(node)
        self.all_nodes.append(node)
        return node

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_CONTENT_TAGS:
            self.skip_depth += 1
            return
        if self.skip_depth:
            return
        node = self._make_node(tag, attrs)
        if tag not in VOID_TAGS:
            self.stack.append((node, {}))

    def handle_startendtag(self, tag, attrs):
        if self.skip_depth or tag in SKIP_CONTENT_TAGS:
            return
        self._make_node(tag, attrs)

    def handle_endtag(self, tag):
        if tag in SKIP_CONTENT_TAGS:
            self.skip_depth = max(0, self.skip_depth - 1)
            return
        if self.skip_depth or tag in VOID_TAGS:
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if self.skip_depth or not self.stack:
            return
        t = norm_text(data)
        if t:
            self.stack[-1][0].texts.append(t)


def node_id_of(node):
    ui_id = node.attrs.get("data-ui-id")
    if ui_id:
        return f"UI:{ui_id}"
    digest = hashlib.sha1(f"{node.dom_path}|{node.tag}".encode("utf-8")).hexdigest()
    return f"DOM-{digest[:8]}"


def captured_attrs(node):
    out = {}
    for k in sorted(node.attrs):
        if k in CAPTURED_ATTRS or k.startswith(CAPTURED_ATTR_PREFIXES):
            out[k] = node.attrs[k]
    return out


def role_hints(node):
    hints = []
    role = node.attrs.get("role")
    if role:
        hints.append(role)
    implicit = {"button": "button", "a": "link", "input": "textbox",
                "select": "combobox", "textarea": "textbox", "form": "form",
                "nav": "navigation", "table": "table", "ul": "list", "ol": "list"}
    if node.tag in implicit and implicit[node.tag] not in hints:
        hints.append(implicit[node.tag])
    return hints


def is_interactable(node):
    if node.attrs.get("data-ui-action"):
        return True
    if node.tag in {"button", "select", "textarea"}:
        return True
    if node.tag == "input":
        return node.attrs.get("type", "text").lower() != "hidden"
    if node.tag == "a" and node.attrs.get("href"):
        return True
    if any(k in node.attrs for k in EVENT_ATTRS):
        return True
    ce = node.attrs.get("contenteditable")
    if ce is not None and ce.lower() in {"true", "plaintext-only"}:
        return True
    if node.attrs.get("role") in INTERACTABLE_ROLES:
        return True
    if node.attrs.get("data-snap-cursor") in SNAP_CURSOR_INTERACTIVE:
        return True
    return False


def event_hint(node):
    for k, ev in EVENT_ATTRS.items():
        if k in node.attrs:
            return ev
    if node.attrs.get("data-snap-cursor") in SNAP_CURSOR_DRAG:
        return "drag"
    if node.tag in {"button", "a"} or node.attrs.get("role") in INTERACTABLE_ROLES:
        return "click"
    if node.tag == "select":
        return "change"
    if node.tag in {"input", "textarea"}:
        t = node.attrs.get("type", "text").lower()
        return "click" if t in {"button", "submit", "checkbox", "radio", "reset"} else "input"
    return "click"


def surface_label(node):
    for candidate in (node.text_content(), node.attrs.get("aria-label"),
                      node.attrs.get("placeholder"), node.attrs.get("value"),
                      node.attrs.get("title"), node.attrs.get("name")):
        if candidate:
            return norm_text(candidate)[:120]
    return ""


def extract(html_path):
    raw = Path(html_path).read_bytes()
    parser = Extractor()
    parser.feed(raw.decode("utf-8", errors="replace"))
    parser.close()

    nodes_out = []
    interactables = []
    act_no = 0
    ids = {}
    for node in parser.all_nodes:
        nid = node_id_of(node)
        ids[id(node)] = nid
        entry = {
            "nodeId": nid,
            "tag": node.tag,
            "domPath": node.dom_path,
            "text": node.text_content()[:120],
            "attrs": captured_attrs(node),
            "roleHint": role_hints(node),
            "interactable": is_interactable(node),
            "parentId": ids.get(id(node.parent)) if node.parent else None,
        }
        nodes_out.append(entry)
        if entry["interactable"]:
            act_no += 1
            interactables.append({
                "rawActionId": f"RAW-ACT-{act_no:04d}",
                "nodeId": nid,
                "surfaceLabel": surface_label(node),
                "eventHint": event_hint(node),
                "dataUiAction": node.attrs.get("data-ui-action"),
            })

    return {
        "schemaVersion": SCHEMA,
        "artifactType": "UI-IR-RAW",
        "source": {
            "file": Path(html_path).name,
            "sha256": hashlib.sha256(raw).hexdigest(),
        },
        "extractor": {"name": "ui-extract.py", "idScheme": "data-ui-id|sha1(domPath|tag)[:8]"},
        "nodes": nodes_out,
        "interactables": interactables,
    }


def verify(fresh, existing_path):
    """GU6: 既存 raw IR と再抽出結果の id 揺れを検査"""
    with open(existing_path, encoding="utf-8") as f:
        existing = json.load(f)
    old_nodes = {n["nodeId"] for n in existing.get("nodes") or []}
    new_nodes = {n["nodeId"] for n in fresh["nodes"]}
    old_acts = {(i["rawActionId"], i["nodeId"]) for i in existing.get("interactables") or []}
    new_acts = {(i["rawActionId"], i["nodeId"]) for i in fresh["interactables"]}

    removed, added = sorted(old_nodes - new_nodes), sorted(new_nodes - old_nodes)
    act_diff = sorted(old_acts ^ new_acts)
    if not removed and not added and not act_diff:
        print(f"[GU6] PASS stable id: {len(new_nodes)} nodes / {len(new_acts)} interactables 揺れなし")
        return 0
    print("[GU6] FAIL stable id 揺れを検出:")
    for nid in removed[:10]:
        print(f"    - 消えた nodeId: {nid}")
    for nid in added[:10]:
        print(f"    - 現れた nodeId: {nid}")
    for pair in act_diff[:10]:
        print(f"    - interactable 対応変化: {pair}")
    print(f"    (removed={len(removed)} added={len(added)} interactable差={len(act_diff)})")
    print("    モック改変が意図的なら raw IR を再生成し、下流の rawRefs を diff で追従させる。")
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mock", help="HTML モックのパス")
    ap.add_argument("-o", "--out", default=None, help="出力先(省略時 stdout)")
    ap.add_argument("--verify", default=None, metavar="RAW_JSON",
                    help="既存 ui-ir.raw.json と突合し id 揺れを検査(GU6)")
    args = ap.parse_args()

    if not Path(args.mock).exists():
        sys.exit(f"入力がありません: {args.mock}")

    result = extract(args.mock)

    if args.verify:
        if not Path(args.verify).exists():
            sys.exit(f"--verify 対象がありません: {args.verify}")
        sys.exit(verify(result, args.verify))

    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out}: {len(result['nodes'])} nodes / "
              f"{len(result['interactables'])} interactables")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
