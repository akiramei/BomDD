# Classifier 2 — final report (verbatim, as written)

---

I judged all 8 pairs (2 models × D01, D02, D03, D06) and wrote them to verdicts.json. Only one pair is named: model A on D01. The other 7 are touch, and none are no.

Results:
- A-D01 **named**: model A's 19th question (`questions`, counting from 1; subject "ExportJob.outcome (順序)") asks about the very point the fix changed. In the spec's order, FfmpegUnavailable is checked before ZeroDuration and NoRegions, which conflicts with REQ-018's "empty output is rejected before ffmpeg runs". This meets criterion 1. The attribute `ExportJob.outcome` itself still has the pre-fix order.
- B-D01 **touch**: `ExportRun.outcome` lists the outcomes in the pre-fix order. No question in B asks about the order; question 8 is about INV-005.
- D02, A and B both **touch**:
  - A lists the exported output's frame count and sample count as `OutputFile.frameCount` and `OutputFile.sampleCount`.
  - B lists them as `ExportClock.frameCount` and `ExportClock.sampleCount` (N and M), and has `Exporter`.
  - Neither says anything about whether the audio is compared by packet `framemd5` or by the content of the decoded samples.
- D03, A and B both **touch**: both describe the keyframe lookup with the pre-fix window `[max(0, target − L), target]`. B's 16th question is only about what `target` is and who calls the lookup.
- D06, A and B both **touch**: both describe `canStreamCopy` with the pre-fix condition "speed and volume are 1". Neither mentions the exception for a source with no audio. B's 11th question is about the 0.05 frame-rate tolerance.

Pairs I hesitated over:
1. **D02, both models.** It turns on what counts as the subject of the changed sentence. If it is the exported output, both models are touch, because both list its frame and sample counts. If it is how the audio is compared, both are no, because neither model has anything for the content of the output's audio. My first draft had A touch and B no. I changed B to touch so the two models are judged by the same reading. B's attributes come from the export plan rather than the output file, so B is the closer call.
2. **A-D01.** It is named on the strength of the question alone. The model's attribute still has the pre-fix order.

Files are in C:\Users\akira\AppData\Local\Temp\claude\C--Users-akira-source-repos-BomDD\c6a0cd2c-98cc-4b3c-bca7-73f54d8a43a0\scratchpad\exp06\classify-2:
- verdicts.json
- work\ (my working files: A.txt, B.txt, fix.py, check.txt)
