# Classifier 1 — final report (verbatim, Japanese as written)

---

8 組すべてを判定し、verdicts.json に書きました。結果は named 1・touch 7・no 0 です。

書いたファイル: C:\Users\akira\AppData\Local\Temp\claude\C--Users-akira-source-repos-BomDD\c6a0cd2c-98cc-4b3c-bca7-73f54d8a43a0\scratchpad\exp06\classify-1\verdicts.json(JSON として読めること、8 件あることを確認済み)

| 項目 | A | B |
|---|---|---|
| D01 エラー判定の順(FfmpegUnavailable を後ろへ) | named(questions の 19 番目) | touch(ExportRun.outcome) |
| D02 受入で音声を比べる方法 | touch(OutputFile.frameCount / sampleCount) | touch(ExportClock.frameCount / sampleCount、questions の 15 番目) |
| D03 キーフレーム検索の窓 | touch(KeyframeLookup) | touch(KeyframeLookup.copyStart、questions の 16 番目) |
| D06 音声なしのソースでの音量条件 | touch(CopySpan.canStreamCopy) | touch(CopyEligibility.canStreamCopy) |

- **named は A の D01 だけです。** A の 19 番目の問いが、仕様の判定順では FfmpegUnavailable が ZeroDuration / NoRegions より先で、要求の文面と食い違う、と問うています。これは修正が変えた点そのものです。A の属性 ExportJob.outcome の書き方は before のままなので、named の根拠は問いだけです。
- **ほかの 7 組は touch です。** どのモデルの属性も before のとおりに書かれています。近くの問い(B の 16 番目は target がスパン開始かどうか、B の 11 番目はレートの許容)も、変わった点は問うていません。
- **where の「何番目」は 1 から数えています。** JSON の添字(0 から)ではありません。

迷った組:
- **D02 は A・B とも touch と no の境目です。** 変わった文は受入の比べ方(音声をパケットの framemd5 で比べるか、復号したサンプルの SHA-256 で比べるか)で、ドメインの状態ではありません。どちらのモデルにも比べ方の記述はありません(framemd5・復号・パケットで検索して 0 件)。比べられる量(出力のフレーム数・サンプル数)を挙げていることを、主語を挙げたとみなして touch にしました。厳しく読めば両方 no です。
- **B の D02 は A より根拠が弱いです。** A は実際の書き出し(OutputFile)の属性ですが、B にはその実体がありません。B の ExportClock は計画の値で、変わった文の前半にある「時計の単体検査」の側に当たります。そこで出力の音声を問う 15 番目の問いも根拠に足しています。
