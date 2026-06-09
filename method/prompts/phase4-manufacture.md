# Phase 4 — 製造(設計者 AI への指示)

典拠: `method/bomdd-playbook-v1.md` §5。入力: 製造パッケージ(G3 通過済み)。

## 隔離規律(絶対)
- **設計者 AI 自身は製造しない**(設計対話で文脈が汚染されている)。
- 製造は**クリーンな文脈のサブエージェント**(Claude Code なら Agent ツールの general-purpose を新規起動)に行わせる。
- 渡してよいもの: `bomdd/20-spec.md` / `30〜34` / `40-work-order.md`(+観測契約)。**ファイル内容を直接プロンプトに埋め込むか、パスを指定して読ませる**。
- 渡してはならないもの: この会話の履歴・`41-fixed-oracle.yaml`・`42-exploratory-probes.yaml`・他工場の成果と cheat・前ループの差分。

## 工場数(チャーターのティアに従う)
- 最小: 1工場。
- 推奨: 初回ループのみ 2–3 工場を**別モデルティア**(opus/sonnet/haiku — Agent ツールの model 指定)で並走。同一ティアは慣習を共有して穴を揃って隠すため、別ティアを混ぜることに意味がある。各工場は別ディレクトリ(例 `loops/<loop>/factory-0N/`)に製造させる。
- 各工場は**互いの存在を知らない**(並走しても成果・cheat を共有しない)。

## 工場への指示(work order に加えて明示する)
1. 入力ファイル一覧(これがすべて。これ以外を参照しない)。
2. Routing の工程順に製造し、自己受入(ビルド+受入ハーネス)を緑にする。
3. **ずる報告の義務**: BOM/K-BOM/Control Plan から導けなかった判断は、実装を止めずに全件 cheat-log 形式で報告する(work order の重点次元は必ず)。
4. 成果物の配置先。

## 製造後(設計者側)
- 各工場の `bomdd/50-as-built.yaml` エントリを記録(model / prompt_hash / artifacts_sha256 / self_acceptance / cheats)。
- ずる報告を `bomdd/51-cheat-log.md` に転記(side: factory)。
- **自己受入緑≠合格**(受入の被覆が捕捉を決める。webapi-01 で自己受入 26/26 緑のまま blocker が通過した)。Phase 5(`phase5-accept.md`)へ。
