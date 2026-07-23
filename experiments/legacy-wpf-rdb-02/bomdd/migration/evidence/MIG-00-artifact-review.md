# EXP-LWR-002 MIG-00 artifact review

Reviewed: 2026-07-19  
Reviewer: Experiment Operator (Codex)

- Charterは第二実験をMIG-10までのclient-server RDB検査に限定している。
- Profileのscenarioは`legacy-wpf-rdb`、DB engineはPostgreSQL 16.14である。
- 全roleは実験上の単一operatorへ割当済みである。
- production相当DBとrestore-control DBを分離し、Gateは後者だけを使う。
- 資格情報を成果物へ記録しない。
- 技術判断は期限milestoneまで先送りし、MIG-00では確定しない。

Result: reviewed; MIG-00 artifacts are ready for acceptance.

