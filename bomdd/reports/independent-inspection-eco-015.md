# ECO-015 独立受入検査 — transfer-04

判定: **REJECT / 製造前凍結不可**

対象コミット `933d181` の blob を直接検査した。禁止された `bomdd/60-change-order-eco-015.md` および `bomdd/60-change-register.yaml` の検証節・verification欄は読んでおらず、既存検証結果の混入はない。

読み取り専用で対象 validator の selftest を実行し、既定ケースは全PASSを確認した。一方、追加した敵対プローブで複数の回避経路を再現した。作業ツリー・index は検査前後とも clean である。書込みを伴う full OQ は read-only 制約上実行していない。

## 所見

- ID: REV-ECO015-01
- 重大度: high
- 該当ファイルと行番号:
  - `method/templates/process-core/hooks/pre-commit:6-8`
  - `method/templates/process-core/hooks/commit-msg:4-6`
  - `method/templates/process-core/tools/process-validator.py:94-108, 320-324`
  - `method/templates/process-core/process-profile.yaml:3-5, 15, 34-36`
- 再現条件:
  - `git rm bomdd/process-profile.yaml && git commit -m "disable process core"` とすると、hookは作業ツリー上のprofile不在を見て即 `exit 0` する。profile削除コミット自身も検査されない。
  - また `trailers.accept` を削除しても、top-level `trailers` が存在すればprofileロードは成功し、E05/E06は `if not name: continue` により無音で無効化される。純関数プローブでも両検査が `[]` を返した。
  - profile自身は既定の保護パス `src/`, `test/`, `tests/` に含まれない。
- 是正提案:
  - HEADにprofileが存在した場合、index/作業ツリーでの削除をfail-closedにする。
  - profileとhooks/toolsを自己保護パスに含める。
  - nested schema、型、非空trailer名、状態集合の一意性・包含関係を厳格検証する。

- ID: REV-ECO015-02
- 重大度: high
- 該当ファイルと行番号:
  - `method/templates/process-core/tools/process-validator.py:175-186, 236-253`
- 再現条件:
  - 次のメッセージは最終段落が通常本文なのでGit trailerではないが、対象実装は中間行をaccept trailerとして認識する。

    ```text
    subject

    BomDD-ECO-Accept: ECO-1

    ordinary final paragraph
    ```

  - 実行したプローブでは `{'BomDD-ECO-Accept': ['ECO-1']}` が返った。
  - ViewPrism2実装 `bomdd/validate_bom.py:210-225` は、この既知故障を避けるため最終段落ブロックだけを認識している。
- 是正提案:
  - `git interpret-trailers --parse` 相当、またはViewPrism2と同じ最終段落ブロック解析を唯一の実装として共有する。
  - 中間段落、件名、コメント行、trailer後の本文を負例に追加する。

- ID: REV-ECO015-03
- 重大度: high
- 該当ファイルと行番号:
  - `method/templates/process-core/tools/process-validator.py:159-172, 268-286, 342-355`
- 再現条件:
  - 履歴証拠をSHA・順序なしのID集合へ縮約している。
  - staged状態のまま無関係コミットへ `BomDD-ECO-Accept: ECO-1` を置いても違反なし。その後 `--no-verify` でapplied化すると、その事前に植えた証拠だけでvalidateが通る。
  - appliedからstagedへ `--no-verify` で逆行した場合も、現在状態がstagedなので既存accept証拠との乖離を検出せず通過する。
  - 実施した両プローブはいずれも所見 `[]` だった。
- 是正提案:
  - trailerごとにcommit SHAを保持し、そのcommitで当該register遷移が発生したことを照合する。
  - fix→acceptの祖先関係・順序、accept証拠とstaged/implemented状態の乖離を検査する。
  - `validate` で履歴中のE02/E03違反も復元検査する。

- ID: REV-ECO015-04
- 重大度: high
- 該当ファイルと行番号:
  - `method/templates/process-core/tools/process-validator.py:112-127`
  - `method/templates/process-core/tools/process-qualification.py:120-127, 139-170`
- 再現条件:
  - `changes` 中の非mapping、ID欠落entryを無音で無視する。
  - 重複IDは辞書への後勝ち代入で潰れる。次の台帳では末尾のstagedだけが見え、applied遷移が消える。

    ```yaml
    changes:
      - {id: ECO-1, title: real, status: applied}
      - {id: ECO-1, title: shadow, status: staged}
    ```

  - プローブではeffective mapがstaged一件となり、遷移所見は `[]`。
  - `changes: [42]` も空台帳として解釈されるため、対象registerが壊れていてもIQ-06とfull qualificationがPASSし得る。OQは別sandboxでregisterを正常内容へ上書きするため、対象台帳の欠陥を再現しない。
- 是正提案:
  - top-level mapping、`changes` list、全entryのmapping・必須フィールド・ID形式・ID一意性を強制する。
  - 不正entryはskipせず測定不能または違反にする。
  - placeholderはtitle先頭文字ではなく、明示的かつ完全一致するsentinelで判定する。

- ID: REV-ECO015-05
- 重大度: high
- 該当ファイルと行番号:
  - `method/templates/process-core/tools/process-qualification.py:91-113, 139-162, 193-259`
- 再現条件:
  - IQ-03は `hp.endswith("/bomdd/hooks")` だけで判定するため、`C:/outside/bomdd/hooks` もPASSすることをプローブで確認した。
  - IQ-02はhook本文に文字列 `process-validator.py` が一度現れるだけでPASSする。
  - WindowsのIQ-04は実行可能性を無条件PASSする。
  - OQは別sandboxで `core.hooksPath=bomdd/hooks` を再設定するため、実対象が外部hookや無効hookを指していてもそれを測らない。
- 是正提案:
  - hooksPathをGitの解決規則で絶対化し、対象root配下の正確な `bomdd/hooks` とcanonical比較する。
  - 対象リポの実hook経路で隔離された負例を発火させる。
  - hook内容はsubstringではなくhash/構造検査または実行probeで確認する。

- ID: REV-ECO015-06
- 重大度: high
- 該当ファイルと行番号:
  - `method/tools/bomdd-init.py:346-367, 374-377`
  - `method/templates/process-core/tools/process-qualification.py:72-128`
- 再現条件:
  - `git commit` の失敗は `committed` に記録されるだけで、qualification実行条件や最終exitへ反映されない。
  - 空のglobal Git設定でuser.name/emailがない、または署名設定で初回commitが失敗する環境を用意する。
  - 対象には `.git`、hooksPath、staged registerが残る。IQにはHEAD実在検査がなく、OQは独自user設定を使うためqualificationがPASSし、`bomdd-init` は最終的にexit 0となり得る。
- 是正提案:
  - 製品リポのinit/config/add/初回commitのいずれかが失敗した時点でexit非0にする。
  - IQへHEAD実在、初回commit成功、clean index/worktreeを追加する。

- ID: REV-ECO015-07
- 重大度: high
- 該当ファイルと行番号:
  - `method/tools/bomdd-init.py:187-205, 284-312`
- 再現条件:
  - `--skills-only` 対象に空の `bomdd/hooks/` ディレクトリだけを置く。
  - `install_process_core` はprofile、validator、qualificationの欠落を検査せず「既存設備を保持」として `False` を返す。
  - 呼出側は `fresh_core == False` のためhooksPath設定とqualificationを両方skipし、`[ok]` とexit 0を返す。
  - 中断設置でprofileだけ残った場合も同じ経路になる。
- 是正提案:
  - 「新規」「完全な既存設備」「不完全な既存設備」の三状態で判定し、不完全状態はFAILにする。
  - Gitリポではfresh/既存にかかわらずqualificationを実行する。

- ID: REV-ECO015-08
- 重大度: high
- 該当ファイルと行番号:
  - `method/templates/process-core/tools/process-validator.py:159-164, 342-359`
- 再現条件:
  - `--root` にprofileとstaged状態のregisterを持つ非Gitディレクトリを指定する。
  - `git log` 失敗は「証拠ゼロ」に変換される。staged entryにはE06が要求されずE07集合も空なので、`validate OK` / exit 0となる。
  - ファイル先頭の契約「git障害はexit 2」と矛盾する。
- 是正提案:
  - `git log` 失敗を空集合と区別し、明示的なopt-outがない限りexit 2にする。
  - Git root・HEAD・shallow状態を検査する。

- ID: REV-ECO015-09
- 重大度: med
- 該当ファイルと行番号:
  - `method/templates/process-core/tools/process-validator.py:201-233`
- 再現条件:
  - old statusを未知値、new statusを`rejected`または`superseded`として `check_transitions` を呼ぶ。
  - `st in extra` が旧状態妥当性より先に評価されるため、プローブは `[]` を返した。未知状態をterminalへ移せばE03違反を洗浄できる。
- 是正提案:
  - old/new両状態がknownであることを先に検証し、その後にterminal edgeを評価する。

- ID: REV-ECO015-10
- 重大度: med
- 該当ファイルと行番号:
  - `method/templates/process-core/tools/process-validator.py:190-198, 290-297, 326-329`
- 再現条件:
  - ECO-1をstagedで新規追加し、同じindexに `src/a.py` を追加して一つのcommitにする。
  - E01はHEADではなくindex側のnew entriesを見るため、新規ECOをopen ECOとして数え、起票前の保護変更を通す。
  - エラーメッセージの「起票が先」およびViewTube実装のHEAD側active ECO判定と一致しない。
- 是正提案:
  - 保護変更の許可判定にはHEAD時点でopenだったECOを用いる。起票と製品変更を別commitに固定する負例を追加する。

- ID: REV-ECO015-11
- 重大度: med
- 該当ファイルと行番号:
  - `method/templates/process-core/tools/process-qualification.py:214-259, 267-300`
  - `method/tools/self-conformance.py:238-247`
- 再現条件:
  - `--runs 0` または負数を指定すると `max(1, a.runs)` により1回だけ実行され、DET PASSを表示する。
  - C11自身も明示的に `--runs 1` を使用し、二回決定性を回帰固定していない。
  - C11のIQ-03変異判定は「qualification全体が非0」かつ出力中に文字列`IQ-03`があることだけを見る。`[IQ-03] PASS` と別IQのFAILでも `ok2=True` になる。
  - 実Git OQ負例にはE04とE07がなく、両者は純関数selftestだけである。
- 是正提案:
  - full qualificationでは `runs >= 2` をargparseで強制する。
  - C11も2回実行し、構造化結果からIQ-03自身の `pass == false` を確認する。
  - 3状態E04と未知参照E07を実hook/Git負例として追加する。

- ID: REV-ECO015-12
- 重大度: high
- 該当ファイルと行番号:
  - `method/templates/process-core/tools/process-qualification.py:51-63, 139-177`
- 再現条件:
  - OQ環境は `os.environ` を丸ごと継承し、global/system configだけを上書きする。
  - `GIT_DIR`、`GIT_WORK_TREE`、`GIT_INDEX_FILE`、object directory系、`GIT_CONFIG_COUNT/KEY/VALUE` 系は残る。
  - これらを別リポへ向けてqualificationを起動すると、`git -C sandbox` より環境変数が優先され、init/config/add/commitがsandbox外を対象にし得る。
- 是正提案:
  - Git subprocess用環境をallowlistで構築するか、Gitのrepo/index/object/configリダイレクト変数を明示削除する。
  - sandbox rootの実Git dir/worktreeを各操作前に実測する。

- ID: REV-ECO015-13
- 重大度: med
- 該当ファイルと行番号:
  - `method/templates/process-core/tools/process-validator.py:153-156, 290-297`
- 再現条件:
  - 正規遷移済みの別ブランチをmergeし、MERGE_HEAD側で既にappliedのECOがindex registerへ入る場合、比較元がHEAD一つだけなので「新規非initial」または飛び越しとして誤判定する。
  - ViewPrism2実装 `bomdd/validate_bom.py:313-333` が保持する複数親合算不変条件が移植されていない。
- 是正提案:
  - merge中はHEADとMERGE_HEAD双方のregisterを読み、定義した状態順序で比較元を合算する。
  - 正規遷移済みbranch mergeを統合陽性対照へ追加する。

## 受入基準への独立判定

- (a) 陽性対照: 対象selftestの既定陽性はPASS。ただしfull Git OQはread-only制約により未実行。
- (b) 負例6種: runnerへの登録は確認したが、E04/E07の実経路、profile自己無効化、重複ID、事前植込み証拠など重要負例が欠落。
- (c) 2回決定性: 既定値は2だが、C11は1回、CLIは0/負数を1回へ丸めてDET PASSするため保証不成立。
- (d) scaffold回帰: C4/C11入口は存在するが、初回commit失敗の無視と`--skills-only`不完全設備の成功があるため不成立。
- (e) ViewPrism2・ViewTube対応表: **不成立**。特にtrailer最終ブロック、証拠SHA/祖先・順序、状態との逆行乖離、Git測定不能、merge複数親の不変条件が欠落している。

実応答モデル: `gpt-5.6-sol`  
セッション識別子: `019f9b81-bc1b-78d0-9870-40eb15e7a252`

Codex session ID: 019f9b81-bc1b-78d0-9870-40eb15e7a252
Resume in Codex: codex resume 019f9b81-bc1b-78d0-9870-40eb15e7a252

---

## 真正判定(当方検証・2026-07-26 — 検査官出力の後付け注記)

- 実施: Claude(製造者側)による各所見の実プローブ+コード読解検証。プローブ 6 件
  (REV-01 部分/02/03 部分/04/09/10)は純関数直接実行で成立を実測・残り 7 件はコード読解で成立確認。
- **裁定: 13/13 CONFIRMED・誤検出 0**(transfer-04 定義: 指摘が事実として成立し、宣言仕様に照らし
  欠陥を構成する)。うち部分留保 3 件:
  - REV-01: profile **全撤去**による無効化は gate ① 裁定 5 で文書化済みの設計境界(脱出経路)—
    その部分は欠陥でない。**部分変異**(trailers.accept 削除等)の無音無効化と自己保護パス欠如は
    未宣言の真欠陥。
  - REV-03: 逆行乖離(ViewPrism2 E17)は order 対応表で「未移植」宣言済み — その部分は既知。
    **事前植込み証拠**(SHA・遷移紐付けなしの ID 集合縮約)は未宣言の真欠陥。
  - REV-06: 初回 commit 失敗の非致命扱いは CI 環境考慮の設計判断だったが order に未文書化 —
    総合 disposition の不整合([git] 失敗表示のまま line ready PASS)は欠陥として受理。
- 特記: REV-07 は ECO-009 #2(kit 完全性検査)と**同族の穴の再演** — 是正済み様式が隣の新設装置へ
  適用されない(transfer-04 4類型の水平展開漏れ)。REV-04 は ECO-011/012(重複キー情報損失)の
  **1 段上の同型**(YAML キーは厳格・entry ID 値は後勝ち)。
- 検査官: Codex CLI・実応答モデル **gpt-5.6-sol**(検査官自己申告+セッション記録)・
  セッション 019f9b81-bc1b-78d0-9870-40eb15e7a252。transfer-04(2026-07-11)時点で
  クライアント識別ゲートにより到達不可だった個体が、プラグイン 1.0.6 で到達。
- 処置: 全所見は是正 ECO(起票裁定待ち)へ。ECO-015 の verified 状態の扱い(維持+後続 ECO /
  格下げ)も同裁定に含める。
