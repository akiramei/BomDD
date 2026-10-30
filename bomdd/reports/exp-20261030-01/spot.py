import glob
import json
import re
import sys
from pathlib import Path

repos = Path(sys.argv[1])
vt = repos / "ViewTube" / "bomdd" / "ui"
raw_text = (vt / "ui-ir.raw.json").read_text(encoding="utf-8")
raw_ids = set(re.findall(r'"([a-z]+\.[A-Za-z0-9_.-]+)"', raw_text))
mock = "".join(Path(f).read_text(encoding="utf-8") for f in glob.glob(str(vt / "mock" / "*.html")))
mock_ids = set(re.findall(r'data-ui-id="([^"]+)"', mock))
print("mock ids", len(mock_ids), "mock ids absent from raw IR text", len(mock_ids - raw_ids))
print("create-manual in mock:", any("create-manual" in i for i in mock_ids), "in raw IR:", "create-manual" in raw_text)
ir = json.loads((vt / "ui-ir.json").read_text(encoding="utf-8"))
acts = ir.get("actions", [])
cited = {r for a in acts for r in (a.get("requirementRefs") or [])}
print("ui-ir actions", len(acts), "REQs cited by an action", len(cited), "REQ-024 cited:", "REQ-024" in cited)
vp_html = glob.glob(str(repos / "ViewPrism2" / "**" / "*.html"), recursive=True)
print("ViewPrism2 html files", len(vp_html), "with data-ui-id", sum("data-ui-id" in Path(f).read_text(encoding="utf-8", errors="replace") for f in vp_html))
