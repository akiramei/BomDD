# Deriver B — final report (verbatim, as written)

Run 2026-10-31, 314.1 s, 10 tool uses; isolation (`../exp-20261030-04/isolation.py`): Bash 5, Read 2, Write 4, flags 0.
Model frozen: `domain-model.json` SHA-256 `e27f1891b8c50fc6268eafb9d9b6078e5f7a00755808e1472dc40a7570db0dce`.

---

`domain-model.json` is written and passes `check_model.py`: no ERROR lines, exit 0. I read only the files in the folder (prompt.md, 10-requirements.yaml, 20-spec.md, check_model.py).

File: C:\Users\akira\AppData\Local\Temp\claude\C--Users-akira-source-repos-BomDD\c6a0cd2c-98cc-4b3c-bca7-73f54d8a43a0\scratchpad\exp06\derive-b\domain-model.json

**Counts (from the checker):**
- 16 entities, 88 attributes, 42 relations, 18 questions.
- 76 attributes have a stated initial value; the other 12 are `"unknown"`, and every one of them is raised in `questions`.
- 41 attributes have `set_by`; 65 cite a REQ id and 88 cite a SPEC id or section.
- `output_frame_rate` lists 5 attributes: `OutputSettings.fps`, `ExportRequest.outFps`, `Exporter.vfrFpsFilter`, `ExportClock.F`, `CopyEligibility.canStreamCopy`. The source rate `ClipInfo.frameRate` does not match.

**The 16 entities:** Source, ClipInfo, Document, Region, KeptPiece, History, OutputSettings, ExportFormat, ExportRequest, Exporter, ExportClock, CopySpan, CopyEligibility, KeyframeLookup, ExportRun, FfmpegLocator.

**How I filled the fields:**
- `set_by` lists the operations that create or change the value, including the one that creates it.
- Values computed from other values have an `initial` starting with `derived: ...`. This counts them as having an initial value.
- I added a top-level `conventions` key that says both of these; the checker ignores it.
- Frame grid, snap and MinLen are definitions in the spec, not things the app holds, so they are not entities.

**Where I was unsure (main ones among the 18 questions):**
1. **The `fps` argument to edits:** SplitAt, MoveBoundary and MoveTrim take an `fps`, but the texts don't say whether it is the source rate or the output rate. They also don't say whether changing the output rate changes the frame grid edits snap to. Only the export clock (§2.7 step 2) names the clip's rate.
2. **Request ← settings:** the texts don't spell out how the export request's `outFps`, `outWidth` and `outHeight` are taken from the output settings. Only §1's definition of the exporter implies it.
3. **History:** its starting contents are not stated. Nor is whether changes to output settings count as edits that can be undone (REQ-012 says "every edit").
4. **Playhead, selection, new region ids:** nothing says what holds the playhead and the selected region, or how a split's new id is chosen.
5. **Where the requirements and the spec disagree:**
   - REQ-003 says a time outside the trim has no region, but `RegionAt` falls back to the last region.
   - REQ-010 refuses excluding the last kept region, but INV-005 says a merge can still leave none kept.
   - REQ-013 lists 24/30/60/120 as the output rates, but `SetFps` accepts any finite positive value.
   - REQ-017 asks for "rate equal to the source", but §2.9 allows a difference of up to 0.05.
6. **Not stated anywhere:**
   - the default export format;
   - the output folder and starting `outputPath`;
   - the starting progress value;
   - the output audio sample rate;
   - what a cancelled export does with a part-written file;
   - what the keyframe lookup's target is, and who calls it.

Several of the disagreements in item 5 are already acknowledged in the spec's own notes. I listed them anyway, citing both sides.
