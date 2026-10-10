PATCHES = {
    # A. Parse each register blob once instead of once per ECO inside the comprehension.
    #    The after-blob is parsed only when the before-blob states at least one entry, exactly as
    #    in the original, where an empty before-dict never evaluates states(after_register) - so a
    #    parse error in the after-blob surfaces in the same cases and in the same order.
    "record_consistency": [
        (
            "            moved = {eco: (state, states(after_register).get(eco))\n"
            "                     for eco, state in states(before_register).items()\n"
            "                     if states(after_register).get(eco) not in (None, state)}\n",
            "            _before_states = states(before_register)\n"
            "            _after_states = states(after_register) if _before_states else {}\n"
            "            moved = {eco: (state, _after_states.get(eco))\n"
            "                     for eco, state in _before_states.items()\n"
            "                     if _after_states.get(eco) not in (None, state)}\n",
        ),
    ],
    # B. Read and normalise each record-surface file once per run instead of once per claim.
    "machinery_claims": [
        (
            "    surface = None                      # built lazily; the sweep is the expensive part\n",
            "    surface = None                      # built lazily; the sweep is the expensive part\n"
            "    _normalised = {}\n",
        ),
        (
            "                text = io.open(path, encoding=\"utf-8\", errors=\"replace\", newline=\"\").read()\n"
            "                if needle in normalise(text, policy[\"remove\"], policy[\"casefold\"]):\n",
            "                if path not in _normalised:\n"
            "                    _normalised[path] = normalise(\n"
            "                        io.open(path, encoding=\"utf-8\", errors=\"replace\", newline=\"\").read(),\n"
            "                        policy[\"remove\"], policy[\"casefold\"])\n"
            "                if needle in _normalised[path]:\n",
        ),
    ],
    # D. Read the history's messages once per run instead of one `git log --grep` per ECO.
    #    `git log --fixed-strings --grep=X` (no -i) selects the commits whose message contains X
    #    case-sensitively; X holds no newline, so line containment is message containment; the
    #    original's casefold test then only ever sees selected messages. The equivalent predicate
    #    is therefore a case-sensitive substring test per message - NOT a casefolded one, which
    #    would widen the match.
    "process": [
        (
            "def _git_head_register(root: Path) -> dict[str, Any]:\n",
            "_HISTORY_MESSAGES: dict[str, list[str]] = {}\n"
            "\n"
            "\n"
            "def _history_has(root: Path, needle: str) -> bool:\n"
            "    key = str(root)\n"
            "    if key not in _HISTORY_MESSAGES:\n"
            "        _HISTORY_MESSAGES[key] = _run_git(\n"
            "            root, \"log\", \"--format=%B%x00\", check=False).split(\"\\0\")\n"
            "    return any(needle in message for message in _HISTORY_MESSAGES[key])\n"
            "\n"
            "\n"
            "def _git_head_register(root: Path) -> dict[str, Any]:\n",
        ),
        (
            "            fix_log = _run_git(\n"
            "                root,\n"
            "                \"log\",\n"
            "                \"--format=%B\",\n"
            "                \"--fixed-strings\",\n"
            "                f\"--grep=BomDD-ECO-Fix: {eco_id}\",\n"
            "                check=False,\n"
            "            )\n"
            "            if f\"BomDD-ECO-Fix: {eco_id}\".casefold() not in fix_log.casefold():\n",
            "            if not _history_has(root, f\"BomDD-ECO-Fix: {eco_id}\"):\n",
        ),
        (
            "                accept_log = _run_git(\n"
            "                    root,\n"
            "                    \"log\",\n"
            "                    \"--format=%B\",\n"
            "                    \"--fixed-strings\",\n"
            "                    f\"--grep=BomDD-ECO-Accept: {eco_id}\",\n"
            "                    check=False,\n"
            "                )\n"
            "                if f\"BomDD-ECO-Accept: {eco_id}\".casefold() not in accept_log.casefold():\n",
            "                if not _history_has(root, f\"BomDD-ECO-Accept: {eco_id}\"):\n",
        ),
    ],
}
