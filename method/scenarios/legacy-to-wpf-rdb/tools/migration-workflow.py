#!/usr/bin/env python3
"""Artifact-driven workflow helper for the legacy-wpf-rdb migration scenario.

This tool is deliberately scenario-local. It does not alter bomdd-init and refuses
to run unless bomdd/migration/migration-profile.json explicitly enables the
legacy-wpf-rdb scenario.
"""
from __future__ import annotations

import argparse
import csv
import copy
import hashlib
import json
import os
import re
import shutil
import sqlite3
import struct
import subprocess
import sys
import tempfile
import zlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCENARIO_ID = "legacy-wpf-rdb"
SCENARIO_ROOT = Path(__file__).resolve().parents[1]
METHOD_ROOT = SCENARIO_ROOT.parents[1]
TEMPLATES = SCENARIO_ROOT / "templates"
STANDARD_TEMPLATES = METHOD_ROOT / "templates"
DEFINITION_SOURCE = SCENARIO_ROOT / "milestone-definition.json"
GUIDE_SOURCE = SCENARIO_ROOT / "migration-runbook.md"
EXCEPTIONS_SOURCE = SCENARIO_ROOT / "exception-catalog.md"
ONBOARDING_SOURCE = SCENARIO_ROOT / "onboarding.md"

FOLLOWUP = {
    "MIG-00": ("STEP-002", "移行憲章を確定する"),
    "MIG-10": ("STEP-012", "現行ビルドを再現する"),
    "MIG-15": ("STEP-016", "代表リスクの実証を実行する"),
    "MIG-20": ("STEP-022", "機能台帳を作る"),
    "MIG-30": ("STEP-031", "要求と仕様を復元する"),
    "MIG-40": ("STEP-041", "E-BOM を作る"),
    "MIG-50": ("STEP-052", "仕様由来の固定オラクルを作る"),
    "MIG-60": ("STEP-062", "複製DBに対する読取りを実装する"),
    "MIG-70": ("STEP-072", "全画面で WPF 固有検査を行う"),
    "MIG-75": ("STEP-076", "同一Release Candidateで顧客UATと運用リハーサルを行う"),
    "MIG-80": ("STEP-081", "切替Runbookを作る"),
    "MIG-90": ("STEP-092", "現行書込みを停止し最終backupを取得する"),
    "MIG-100": ("STEP-102", "Service BOM を完成させる"),
}

TEMPLATE_MAP = {
    "migration-profile.json": "migration-profile.json",
    "migration-status.json": "migration-status.json",
    "responsibility-matrix.md": "responsibility-matrix.md",
    "current-baseline.md": "current-baseline.md",
    "db-baseline.md": "db-baseline.md",
    "current-observation-index.md": "current-observation-index.md",
    "feature-inventory.md": "feature-inventory.md",
    "ui-inventory.md": "ui-inventory.md",
    "db-object-inventory.md": "db-object-inventory.md",
    "external-dependency-inventory.md": "external-dependency-inventory.md",
    "db-compatibility-contract.md": "db-compatibility-contract.md",
    "db-preservation-oracle.md": "db-preservation-oracle.md",
    "slice-backlog.md": "slice-backlog.md",
    "cutover-runbook.md": "cutover-runbook.md",
    "rollback-runbook.md": "rollback-runbook.md",
    "display-contract.md": "display-contract.md",
    "spec-rulings.md": "spec-rulings.md",
    "feature-migration-index.md": "feature-migration-index.md",
    "difference-register.md": "difference-register.md",
    "legacy-system-disposition.md": "legacy-system-disposition.md",
    "feature-migration-status.json": ".templates/feature-migration-status.json",
    "gate-result.json": ".templates/gate-result.json",
    "exception-record.md": ".templates/exception-record.md",
    "db-technical-decisions.json": "decisions/MIG-30-db-technical-decisions.json",
    "implementation-decisions.json": "decisions/MIG-40-implementation-decisions.json",
    "deployment-decisions.json": "decisions/MIG-80-deployment-decisions.json",
    "baseline-fixture-manifest.json": ".templates/baseline-fixture-manifest.json",
    "baseline-fixture-postgresql-manifest.json": ".templates/baseline-fixture-postgresql-manifest.json",
    "current-ui-evidence-manifest.json": ".templates/current-ui-evidence-manifest.json",
    "program-governance.md": "program-governance.md",
    "customer-operations-boundary.md": "customer-operations-boundary.md",
    "java-runtime-baseline.md": "java-runtime-baseline.md",
    "nonfunctional-baseline.json": "nonfunctional-baseline.json",
    "security-baseline.md": "security-baseline.md",
    "deployment-operations-baseline.md": "deployment-operations-baseline.md",
    "feasibility-portfolio.json": "feasibility-portfolio.json",
    "feasibility-report.md": "feasibility-report.md",
    "code-inventory.json": "code-inventory.json",
    "javafx-surface-inventory.md": "javafx-surface-inventory.md",
    "dependency-replacement-ledger.md": "dependency-replacement-ledger.md",
    "customer-variant-matrix.md": "customer-variant-matrix.md",
    "test-asset-inventory.md": "test-asset-inventory.md",
    "java-csharp-semantic-contract.md": "java-csharp-semantic-contract.md",
    "javafx-wpf-interaction-contract.md": "javafx-wpf-interaction-contract.md",
    "nonfunctional-acceptance-contract.json": "nonfunctional-acceptance-contract.json",
    "security-acceptance-contract.md": "security-acceptance-contract.md",
    "customer-acceptance-contract.md": "customer-acceptance-contract.md",
    "workstream-register.json": "workstream-register.json",
    "target-architecture.md": "target-architecture.md",
    "workstream-interface-register.json": "workstream-interface-register.json",
    "build-release-architecture.md": "build-release-architecture.md",
    "observability-design.md": "observability-design.md",
    "security-design.md": "security-design.md",
    "migration-factory-plan.md": "migration-factory-plan.md",
    "contract-test-index.md": "contract-test-index.md",
    "test-data-plan.md": "test-data-plan.md",
    "ci-readiness.json": "ci-readiness.json",
    "pilot-portfolio.json": "pilot-portfolio.json",
    "workstream-status.json": ".templates/workstream-status.json",
    "workstream-snapshot.json": "workstream-snapshot.json",
    "release-candidate-acceptance.json": "release-candidate-acceptance.json",
    "customer-uat-ledger.md": "customer-uat-ledger.md",
    "operations-rehearsal.md": "operations-rehearsal.md",
    "security-assessment.md": "security-assessment.md",
    "rollout-plan.md": "rollout-plan.md",
    "support-readiness.md": "support-readiness.md",
    "signed-release-manifest.json": "signed-release-manifest.json",
    "cohort-deployment-ledger.json": "cohort-deployment-ledger.json",
    "stabilization-scorecard.md": "stabilization-scorecard.md",
}

PROJECT_TEMPLATE_MAP = {
    "migration-charter.md": "bomdd/00-charter.md",
    "migration-inventory.md": "bomdd/plm-intake/migration-inventory.md",
    "source-map.md": "bomdd/plm-intake/source-map.md",
}

STANDARD_PROJECT_TEMPLATE_MAP = {
    "10-requirements.yaml": "bomdd/10-requirements.yaml",
    "20-spec.md": "bomdd/20-spec.md",
    "30-ebom.yaml": "bomdd/30-ebom.yaml",
    "31-kbom.yaml": "bomdd/31-kbom.yaml",
    "32-mbom.yaml": "bomdd/32-mbom.yaml",
    "33-control-plan.yaml": "bomdd/33-control-plan.yaml",
    "34-routing.yaml": "bomdd/34-routing.yaml",
    "40-work-order.md": "bomdd/40-work-order.md",
    "41-fixed-oracle.yaml": "bomdd/41-fixed-oracle.yaml",
    "50-as-built.yaml": "bomdd/50-as-built.yaml",
    "53-service-bom.yaml": "bomdd/53-service-bom.yaml",
    "db/schema-intent.md": "bomdd/db/schema-intent.md",
}


class WorkflowError(RuntimeError):
    pass


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise WorkflowError(f"required file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise WorkflowError(f"invalid JSON: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise WorkflowError(f"JSON root must be an object: {path}")
    return data


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    temp.replace(path)


def render_text(source: Path, target: Path, replacements: dict[str, str]) -> None:
    text = source.read_text(encoding="utf-8")
    for key, value in replacements.items():
        text = text.replace("{{" + key + "}}", value)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")


def is_git_managed(root: Path) -> bool:
    current = root.resolve()
    return any((p / ".git").exists() for p in (current, *current.parents))


def migration_root(project_root: Path) -> Path:
    return project_root.resolve() / "bomdd" / "migration"


def require_scenario(project_root: Path) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    mig = migration_root(project_root)
    profile = read_json(mig / "migration-profile.json")
    scenario = profile.get("scenario") or {}
    if scenario.get("id") != SCENARIO_ID or scenario.get("enabled") is not True:
        raise WorkflowError(
            "This command is only available for the legacy-wpf-rdb migration scenario. "
            "The profile is absent, disabled, or has a different scenario. No files were changed."
        )
    status = read_json(mig / "migration-status.json")
    if status.get("scenario_id") != SCENARIO_ID:
        raise WorkflowError("status scenario_id does not match the enabled profile; use EX-STATE-001")
    return mig, profile, status


def load_definition(mig: Path) -> dict[str, Any]:
    definition = read_json(mig / "milestone-definition.json")
    if definition.get("scenario_id") != SCENARIO_ID:
        raise WorkflowError("milestone definition scenario_id mismatch; use EX-DOC-001")
    return definition


def milestone_map(definition: dict[str, Any]) -> dict[str, dict[str, Any]]:
    items = definition.get("milestones")
    if not isinstance(items, list):
        raise WorkflowError("milestone definition has no milestones list")
    result = {}
    for item in items:
        if not isinstance(item, dict) or not item.get("id"):
            raise WorkflowError("milestone definition contains an invalid item")
        result[str(item["id"])] = item
    return result


def decision_set_map(definition: dict[str, Any]) -> dict[str, dict[str, Any]]:
    items = definition.get("decision_sets")
    if not isinstance(items, list):
        raise WorkflowError("milestone definition has no decision_sets list; use EX-DOC-001")
    result: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict) or not item.get("id"):
            raise WorkflowError("milestone definition contains an invalid decision set")
        result[str(item["id"])] = item
    return result


def decision_document_problems(
    project_root: Path, spec: dict[str, Any], document: dict[str, Any]
) -> list[str]:
    problems: list[str] = []
    if document.get("schema") not in {
        "bomdd-legacy-wpf-technical-decisions/1.0",
        "bomdd-legacy-wpf-technical-decisions/2.0",
    }:
        problems.append(f"unexpected decision document schema: {document.get('schema')}")
    if document.get("decision_set") != spec.get("id"):
        problems.append(f"decision_set is {document.get('decision_set')!r}, expected {spec.get('id')!r}")
    if document.get("due_milestone") != spec.get("due_milestone"):
        problems.append(
            f"due_milestone is {document.get('due_milestone')!r}, expected {spec.get('due_milestone')!r}"
        )
    values = document.get("decisions")
    if not isinstance(values, list):
        return [*problems, "decisions must be a list"]
    records = {
        str(item.get("id")): item for item in values
        if isinstance(item, dict) and item.get("id")
    }
    expected = {str(item["id"]): item for item in spec.get("decisions", [])}
    for unexpected in sorted(set(records) - set(expected)):
        problems.append(f"unexpected decision ID: {unexpected}")
    root = project_root.resolve()
    for decision_id, expected_item in expected.items():
        record = records.get(decision_id)
        if record is None:
            problems.append(f"missing decision: {decision_id}")
            continue
        if record.get("owner") != expected_item.get("owner"):
            problems.append(
                f"{decision_id} owner is {record.get('owner')!r}, expected {expected_item.get('owner')!r}"
            )
        if record.get("decision_status") not in {"decided", "not-applicable"}:
            problems.append(f"{decision_id} status is not decided/not-applicable")
        value = str(record.get("value") or "").strip()
        if not value or value == "UNDECIDED":
            problems.append(f"{decision_id} value or not-applicable reason is missing")
        if not str(record.get("decider") or "").strip() or record.get("decider") == "UNASSIGNED":
            problems.append(f"{decision_id} decider is missing")
        if not str(record.get("decided_at") or "").strip():
            problems.append(f"{decision_id} decided_at is missing")
        evidence = str(record.get("evidence") or "").strip()
        if not evidence:
            problems.append(f"{decision_id} evidence is missing")
            continue
        actual = (root / evidence).resolve()
        try:
            actual.relative_to(root)
        except ValueError:
            problems.append(f"{decision_id} evidence must be a project-local file: {evidence}")
            continue
        if not actual.is_file():
            problems.append(f"{decision_id} evidence file not found: {evidence}")
            continue
        expected_hash = str(record.get("evidence_sha256") or "")
        if not expected_hash:
            problems.append(f"{decision_id} evidence hash is missing")
        elif file_sha256(actual).lower() != expected_hash.lower():
            problems.append(f"{decision_id} evidence hash mismatch: {evidence}")
    return problems


def decision_set_gate_problems(
    project_root: Path,
    status: dict[str, Any],
    definition: dict[str, Any],
    decision_set_id: str,
) -> list[str]:
    spec = decision_set_map(definition).get(decision_set_id)
    if spec is None:
        return [f"unknown decision set: {decision_set_id}"]
    records = artifact_records(status)
    artifact_id = str(spec.get("artifact_id"))
    record = records.get(artifact_id)
    problems: list[str] = []
    if record is None:
        problems.append(f"decision artifact is not registered: {artifact_id}")
    else:
        if record.get("path") != spec.get("path"):
            problems.append(f"decision artifact path differs: {record.get('path')}")
        if record.get("status") != "accepted":
            problems.append(f"decision artifact status is {record.get('status')!r}, expected 'accepted'")
        evidence = record.get("evidence")
        evidence_paths = [str(item) for item in evidence] if isinstance(evidence, list) else []
        if record.get("status") == "accepted":
            problems.extend(content_hash_problems(
                project_root,
                [str(spec.get("path")), *evidence_paths],
                record.get("content_hashes"),
            ))
    path = project_root.resolve() / str(spec.get("path"))
    if not path.is_file():
        problems.append(f"decision document not found: {spec.get('path')}")
        return problems
    try:
        document = read_json(path)
    except WorkflowError as exc:
        problems.append(str(exc))
        return problems
    problems.extend(decision_document_problems(project_root, spec, document))
    return problems


def exception_catalog_entries(mig: Path) -> dict[str, dict[str, str]]:
    catalog = mig / "guide" / "exception-catalog.md"
    pattern = re.compile(
        r"^\| (EX-[A-Z]+-[0-9]{3}) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|$"
    )
    result: dict[str, dict[str, str]] = {}
    for line in catalog.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if not match:
            continue
        catalog_id, symptom, classification, action, resume = match.groups()
        result[catalog_id] = {
            "id": catalog_id,
            "symptom": symptom,
            "catalog_classification": classification,
            "default_action": action,
            "resume": resume,
        }
    if not result:
        raise WorkflowError("exception catalog has no machine-readable entries; use EX-DOC-001")
    return result


def effective_exception_classification(catalog_value: str) -> tuple[str, str | None]:
    if catalog_value == "blocker":
        return "blocker", None
    if catalog_value == "non-blocker":
        return "non-blocker", None
    if catalog_value == "defect":
        return "defect", None
    if "blocker" in catalog_value and "non-blocker" in catalog_value:
        return "blocker", "ambiguous catalog classification defaults to blocker until owner resolution"
    raise WorkflowError(f"unknown exception classification in catalog: {catalog_value}")


def exception_owner_role(catalog_id: str) -> str:
    if catalog_id == "EX-WPF-005":
        return "UI Approver"
    category = catalog_id.split("-")[1]
    return {
        "DB": "DB Custodian",
        "WPF": "WPF Technical Owner",
        "JAVA": "Java Technical Owner",
        "FEAS": "Migration Owner",
        "SCALE": "Program Manager",
        "WS": "Program Manager",
        "SPEC": "Specification Owner",
        "ORACLE": "Acceptance Owner",
        "DIFF": "Acceptance Owner",
        "SEC": "Security Owner",
        "RC": "Release Owner",
        "REL": "Release Owner",
        "UAT": "Customer Acceptance Owner",
        "COHORT": "Migration Owner",
        "OPS": "Operations Owner",
    }.get(category, "Migration Owner")


def initialize(project_root: Path, product: str) -> None:
    root = project_root.resolve()
    if not root.is_dir():
        raise WorkflowError(f"project root does not exist: {root}")
    if not is_git_managed(root):
        raise WorkflowError("project is not inside a Git work tree; use EX-INIT-002. No files were changed.")
    mig = migration_root(root)
    if mig.exists():
        raise WorkflowError(f"{mig} already exists; use EX-INIT-001. No files were changed.")

    replacements = {"PRODUCT": product, "DATE": today()}
    for dirname in ("changes", "evidence", "exceptions", "gates", "handoffs", "work-items", "guide", "tools", ".templates"):
        (mig / dirname).mkdir(parents=True, exist_ok=False)
    for source_name, target_name in TEMPLATE_MAP.items():
        render_text(TEMPLATES / source_name, mig / target_name, replacements)
    for source_name, target_name in PROJECT_TEMPLATE_MAP.items():
        target = root / target_name
        if not target.exists():
            render_text(TEMPLATES / source_name, target, replacements)
    for source_name, target_name in STANDARD_PROJECT_TEMPLATE_MAP.items():
        target = root / target_name
        if not target.exists():
            render_text(STANDARD_TEMPLATES / source_name, target, replacements)
    shutil.copy2(DEFINITION_SOURCE, mig / "milestone-definition.json")
    shutil.copy2(GUIDE_SOURCE, mig / "guide" / "migration-runbook.md")
    shutil.copy2(EXCEPTIONS_SOURCE, mig / "guide" / "exception-catalog.md")
    shutil.copy2(ONBOARDING_SOURCE, mig / "guide" / "onboarding.md")
    shutil.copy2(Path(__file__).resolve(), mig / "tools" / "migration-workflow.py")

    status_path = mig / "migration-status.json"
    status = read_json(status_path)
    definition = read_json(mig / "milestone-definition.json")
    artifacts = []
    seen: set[str] = set()
    for milestone in definition["milestones"]:
        for spec in milestone["required_artifacts"]:
            artifact_id = spec["id"]
            if artifact_id in seen:
                continue
            seen.add(artifact_id)
            path = spec["path"]
            exists = (root / path).is_file()
            artifacts.append({
                "id": artifact_id,
                "path": path,
                "status": "present" if exists else "missing",
                "evidence": [],
            })
    status["artifacts"] = artifacts
    status["updated_at"] = now_iso()
    atomic_write_json(status_path, status)
    print(f"[ok] scenario activated: {SCENARIO_ID}")
    print(f"[ok] migration workspace: {mig}")
    print("[next] fill charter, profile, responsibility matrix, program governance, and customer boundary")
    frozen_tool = mig / "tools" / "migration-workflow.py"
    print(f"[next] {sys.executable} {frozen_tool} status --project-root {root}")


def artifact_records(status: dict[str, Any]) -> dict[str, dict[str, Any]]:
    records = status.get("artifacts")
    if not isinstance(records, list):
        raise WorkflowError("migration-status.json artifacts must be a list")
    result: dict[str, dict[str, Any]] = {}
    for record in records:
        if isinstance(record, dict) and record.get("id"):
            result[str(record["id"])] = record
    return result


def active_change(status: dict[str, Any]) -> dict[str, Any] | None:
    value = status.get("active_accepted_change")
    if value is None:
        return None
    if not isinstance(value, dict) or not value.get("id"):
        raise WorkflowError("migration-status.json active_accepted_change is invalid; use EX-STATE-001")
    return value


def require_no_active_change(status: dict[str, Any], command: str) -> None:
    change = active_change(status)
    if change is not None:
        raise WorkflowError(
            f"accepted change {change['id']} is active; run next and close it before {command}"
        )


def require_no_blockers(status: dict[str, Any], command: str) -> None:
    blockers = status.get("blockers")
    if blockers:
        first = blockers[0] if isinstance(blockers, list) else "invalid blockers field"
        raise WorkflowError(
            f"active blocker {first} exists; run next and resolve blockers before {command}"
        )


def exception_records(status: dict[str, Any]) -> list[dict[str, Any]]:
    records = status.setdefault("exceptions", [])
    if not isinstance(records, list):
        raise WorkflowError("migration-status.json exceptions must be a list")
    return [item for item in records if isinstance(item, dict)]


def status_list(status: dict[str, Any], key: str) -> list[Any]:
    value = status.setdefault(key, [])
    if not isinstance(value, list):
        raise WorkflowError(f"migration-status.json {key} must be a list")
    return value


def find_open_exception(status: dict[str, Any], occurrence_id: str) -> dict[str, Any]:
    matches = [
        item for item in exception_records(status)
        if item.get("occurrence_id") == occurrence_id and item.get("status") == "open"
    ]
    if not matches:
        raise WorkflowError(f"open exception not found: {occurrence_id}")
    return matches[-1]


def project_relative_path(project_root: Path, value: str) -> str:
    root = project_root.resolve()
    candidate = Path(value)
    actual = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    try:
        return actual.relative_to(root).as_posix()
    except ValueError as exc:
        raise WorkflowError(f"path must be inside the project root: {actual}") from exc


def project_evidence_paths(project_root: Path, values: list[str]) -> list[str]:
    if not values:
        raise WorkflowError("at least one --evidence path is required")
    root = project_root.resolve()
    normalized: list[str] = []
    for value in values:
        candidate = Path(value)
        actual = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
        try:
            relative = actual.relative_to(root)
        except ValueError as exc:
            raise WorkflowError(f"evidence must be inside the project root: {actual}") from exc
        if not actual.is_file():
            raise WorkflowError(f"evidence file not found: {actual}")
        normalized.append(relative.as_posix())
    return normalized


def unique_paths(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def sealed_paths_are_current(project_root: Path, sealed: Any, label: str) -> None:
    problems = sealed_mapping_problems(project_root, sealed)
    if problems:
        raise WorkflowError(f"{label} changed after recording: {problems[0]}")


def sealed_mapping_problems(project_root: Path, sealed: Any) -> list[str]:
    if not isinstance(sealed, dict) or not sealed:
        return ["hash seal is missing"]
    missing = [
        f"sealed file is missing: {relative}"
        for relative in sealed
        if not (project_root.resolve() / str(relative)).is_file()
    ]
    return [*missing, *content_hash_problems(project_root, [str(path) for path in sealed], sealed)]


def exception_seal_problems(project_root: Path, status: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    for exception in exception_records(status):
        occurrence_id = str(exception.get("occurrence_id"))
        mappings: list[tuple[str, Any]] = [
            ("open record", {str(exception.get("open_record")): exception.get("open_record_sha256")}),
            ("observation evidence", exception.get("evidence_hashes")),
        ]
        for item in exception.get("safe_work", []):
            if not isinstance(item, dict):
                problems.append(f"{occurrence_id}: alternate safe work entry is invalid")
                continue
            mappings.extend([
                ("safe work record", {str(item.get("event_record")): item.get("event_record_sha256")}),
                ("safe work evidence", {str(item.get("evidence")): item.get("evidence_sha256")}),
            ])
        if exception.get("status") == "resolved":
            mappings.extend([
                ("resolution record", {
                    str(exception.get("resolution_record")): exception.get("resolution_record_sha256")
                }),
                ("resolution evidence", exception.get("resolution_evidence_hashes")),
            ])
        for label, sealed in mappings:
            for problem in sealed_mapping_problems(project_root, sealed):
                problems.append(f"{occurrence_id} {label}: {problem}")
    return problems


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def content_hashes(project_root: Path, relative_paths: list[str]) -> dict[str, str]:
    root = project_root.resolve()
    result: dict[str, str] = {}
    for value in relative_paths:
        actual = (root / value).resolve()
        try:
            relative = actual.relative_to(root).as_posix()
        except ValueError as exc:
            raise WorkflowError(f"sealed file must be inside the project root: {actual}") from exc
        if not actual.is_file():
            raise WorkflowError(f"sealed file not found: {actual}")
        result[relative] = file_sha256(actual)
    return result


def content_hash_problems(project_root: Path, expected_paths: list[str], sealed: Any) -> list[str]:
    if not isinstance(sealed, dict) or not sealed:
        return ["content hash seal is missing"]
    problems: list[str] = []
    root = project_root.resolve()
    expected = list(dict.fromkeys(expected_paths))
    expected_set = set(expected)
    sealed_set = {str(path) for path in sealed}
    for unexpected in sorted(sealed_set - expected_set):
        problems.append(f"content hash seal has unexpected path: {unexpected}")
    for relative in expected:
        expected_hash = sealed.get(relative)
        if not isinstance(expected_hash, str) or not expected_hash:
            problems.append(f"content hash seal is missing for: {relative}")
            continue
        actual = (root / relative).resolve()
        if not actual.is_file():
            continue
        actual_hash = file_sha256(actual)
        if actual_hash.lower() != expected_hash.lower():
            problems.append(
                f"content hash mismatch: {relative}; accepted={expected_hash.lower()} current={actual_hash.lower()}"
            )
    return problems


def manifest_file_problems(
    project_root: Path, item: Any, label: str
) -> tuple[list[str], Path | None]:
    if not isinstance(item, dict):
        return [f"{label} must be an object"], None
    path_text = str(item.get("path") or "").strip()
    expected_hash = str(item.get("sha256") or "").strip().lower()
    if not path_text:
        return [f"{label} path is missing"], None
    try:
        normalized = project_relative_path(project_root, path_text)
    except WorkflowError as exc:
        return [f"{label}: {exc}"], None
    if normalized != Path(path_text).as_posix():
        return [f"{label} path is not normalized: {path_text}"], None
    actual = project_root.resolve() / normalized
    problems: list[str] = []
    if not actual.is_file():
        problems.append(f"{label} file not found: {normalized}")
        return problems, None
    if not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
        problems.append(f"{label} sha256 is missing or invalid: {normalized}")
    else:
        actual_hash = file_sha256(actual)
        if actual_hash != expected_hash:
            problems.append(
                f"{label} hash mismatch: {normalized}; manifest={expected_hash} current={actual_hash}"
            )
    return problems, actual


def image_metadata(path: Path) -> tuple[str, int, int]:
    data = path.read_bytes()
    if len(data) >= 24 and data[:8] == b"\x89PNG\r\n\x1a\n":
        width, height = struct.unpack(">II", data[16:24])
        return "image/png", width, height
    if len(data) >= 4 and data[:2] == b"\xff\xd8":
        offset = 2
        sof_markers = {
            0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
            0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF,
        }
        while offset + 4 <= len(data):
            if data[offset] != 0xFF:
                offset += 1
                continue
            while offset < len(data) and data[offset] == 0xFF:
                offset += 1
            if offset >= len(data):
                break
            marker = data[offset]
            offset += 1
            if marker in {0x01, *range(0xD0, 0xDA)}:
                continue
            if offset + 2 > len(data):
                break
            segment_length = struct.unpack(">H", data[offset:offset + 2])[0]
            if segment_length < 2 or offset + segment_length > len(data):
                break
            if marker in sof_markers and segment_length >= 7:
                height, width = struct.unpack(">HH", data[offset + 3:offset + 7])
                return "image/jpeg", width, height
            offset += segment_length
    raise WorkflowError(f"unsupported or malformed screenshot format: {path}")


def sqlite_baseline_fixture_manifest_problems(project_root: Path, document: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    if document.get("schema") != "bomdd-legacy-wpf-baseline-fixture/1.0":
        problems.append(f"unexpected fixture manifest schema: {document.get('schema')}")
    if not str(document.get("fixture_id") or "").strip():
        problems.append("fixture_id is missing")
    if not str(document.get("source_snapshot") or "").strip():
        problems.append("source_snapshot is missing")
    if document.get("working_copy_policy") != "copy-per-test":
        problems.append("working_copy_policy must be copy-per-test")
    if str(document.get("engine") or "").lower() != "sqlite":
        problems.append("this validator currently requires engine=sqlite")

    fixture_item = document.get("fixture")
    item_problems, fixture_path = manifest_file_problems(
        project_root, fixture_item, "baseline fixture"
    )
    problems.extend(item_problems)
    if not isinstance(fixture_item, dict) or fixture_item.get("immutable_baseline") is not True:
        problems.append("baseline fixture immutable_baseline must be true")
    for key, label in (
        ("restore_copy", "restore control copy"),
        ("baseline_document", "DB baseline document"),
        ("schema_evidence", "schema evidence"),
    ):
        item_problems, _ = manifest_file_problems(project_root, document.get(key), label)
        problems.extend(item_problems)
    schema_evidence = document.get("schema_evidence")
    if not isinstance(schema_evidence, dict) or not re.fullmatch(
        r"[0-9a-fA-F]{64}", str(schema_evidence.get("normalized_schema_sha256") or "")
    ):
        problems.append("schema_evidence normalized_schema_sha256 is missing or invalid")
    observation_evidence = document.get("observation_evidence")
    if not isinstance(observation_evidence, list) or not observation_evidence:
        problems.append("observation_evidence must contain at least one file")
    else:
        for index, item in enumerate(observation_evidence, 1):
            item_problems, _ = manifest_file_problems(
                project_root, item, f"observation evidence {index}"
            )
            problems.extend(item_problems)

    checks = document.get("expected_checks")
    fixture_hash = str(fixture_item.get("sha256") or "").lower() if isinstance(fixture_item, dict) else ""
    if not isinstance(checks, dict):
        problems.append("expected_checks must be an object")
    else:
        if checks.get("integrity_check") != "ok":
            problems.append("expected integrity_check must be ok")
        if checks.get("foreign_key_violations") != 0:
            problems.append("expected foreign_key_violations must be 0")
        if checks.get("restore_result") != "pass":
            problems.append("restore_result must be pass")
        if str(checks.get("restored_sha256") or "").lower() != fixture_hash:
            problems.append("restored_sha256 must equal the baseline fixture sha256")

    queries = document.get("canonical_queries")
    if not isinstance(queries, list) or not queries:
        problems.append("canonical_queries must contain at least one read-only query")
        queries = []
    if fixture_path is not None:
        try:
            if fixture_path.read_bytes()[:16] != b"SQLite format 3\x00":
                raise WorkflowError("baseline fixture does not have a SQLite header")
            connection = sqlite3.connect(fixture_path.as_uri() + "?mode=ro&immutable=1", uri=True)
            try:
                connection.execute("PRAGMA query_only=ON")
                integrity = [row[0] for row in connection.execute("PRAGMA integrity_check")]
                if integrity != ["ok"]:
                    problems.append(f"live SQLite integrity_check failed: {integrity}")
                foreign_keys = list(connection.execute("PRAGMA foreign_key_check"))
                if foreign_keys:
                    problems.append(f"live SQLite foreign_key_check returned {len(foreign_keys)} row(s)")
                seen_query_ids: set[str] = set()
                for index, query in enumerate(queries, 1):
                    if not isinstance(query, dict):
                        problems.append(f"canonical query {index} must be an object")
                        continue
                    query_id = str(query.get("id") or "").strip()
                    sql = str(query.get("sql") or "").strip()
                    if not query_id or query_id in seen_query_ids:
                        problems.append(f"canonical query {index} has a missing or duplicate id")
                    seen_query_ids.add(query_id)
                    if not re.match(r"(?is)^select\s", sql) or ";" in sql:
                        problems.append(f"canonical query {query_id or index} must be one SELECT without semicolon")
                        continue
                    expected_rows = query.get("expected_rows")
                    if not isinstance(expected_rows, list):
                        problems.append(f"canonical query {query_id or index} expected_rows must be a list")
                        continue
                    actual_rows = [list(row) for row in connection.execute(sql)]
                    if actual_rows != expected_rows:
                        problems.append(
                            f"canonical query {query_id or index} differs: "
                            f"expected={expected_rows!r} actual={actual_rows!r}"
                        )
            finally:
                connection.close()
        except (OSError, sqlite3.Error, WorkflowError) as exc:
            problems.append(f"live SQLite fixture validation failed: {exc}")
    return problems


def normalized_postgresql_schema(text: str) -> str:
    """Remove pg_dump's per-run guard tokens and normalize text for a stable seal."""
    lines = []
    for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if line.startswith("\\restrict ") or line.startswith("\\unrestrict "):
            continue
        lines.append(line.rstrip())
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines) + "\n"


def postgresql_baseline_fixture_manifest_problems(
    project_root: Path, document: dict[str, Any]
) -> list[str]:
    problems: list[str] = []
    if document.get("schema") != "bomdd-legacy-wpf-baseline-fixture/1.1":
        problems.append(f"unexpected fixture manifest schema: {document.get('schema')}")
    if not str(document.get("fixture_id") or "").strip():
        problems.append("fixture_id is missing")
    if not str(document.get("source_snapshot") or "").strip():
        problems.append("source_snapshot is missing")
    if document.get("working_copy_policy") != "restore-per-test":
        problems.append("working_copy_policy must be restore-per-test")

    fixture_item = document.get("fixture")
    item_problems, fixture_path = manifest_file_problems(
        project_root, fixture_item, "baseline fixture"
    )
    problems.extend(item_problems)
    if not isinstance(fixture_item, dict):
        fixture_item = {}
    if fixture_item.get("immutable_baseline") is not True:
        problems.append("baseline fixture immutable_baseline must be true")
    if fixture_item.get("format") != "postgresql-custom":
        problems.append("baseline fixture format must be postgresql-custom")

    for key, label in (
        ("baseline_document", "DB baseline document"),
        ("schema_evidence", "schema evidence"),
    ):
        item_problems, _ = manifest_file_problems(project_root, document.get(key), label)
        problems.extend(item_problems)
    schema_evidence = document.get("schema_evidence")
    normalized_schema_hash = ""
    if isinstance(schema_evidence, dict):
        normalized_schema_hash = str(
            schema_evidence.get("normalized_schema_sha256") or ""
        ).lower()
    if not re.fullmatch(r"[0-9a-f]{64}", normalized_schema_hash):
        problems.append("schema_evidence normalized_schema_sha256 is missing or invalid")

    restore_control = document.get("restore_control")
    restore_database = ""
    if not isinstance(restore_control, dict):
        problems.append("restore_control must be an object")
    else:
        restore_database = str(restore_control.get("database") or "").strip()
        if not restore_database:
            problems.append("restore_control database is missing")
        item_problems, _ = manifest_file_problems(
            project_root, restore_control.get("evidence"), "restore control evidence"
        )
        problems.extend(item_problems)

    observation_evidence = document.get("observation_evidence")
    if not isinstance(observation_evidence, list) or not observation_evidence:
        problems.append("observation_evidence must contain at least one file")
    else:
        for index, item in enumerate(observation_evidence, 1):
            item_problems, _ = manifest_file_problems(
                project_root, item, f"observation evidence {index}"
            )
            problems.extend(item_problems)

    client = document.get("postgresql_client")
    client_paths: dict[str, Path] = {}
    credential_env = ""
    if not isinstance(client, dict):
        problems.append("postgresql_client must be an object")
    else:
        for key, label in (
            ("psql", "PostgreSQL psql client"),
            ("pg_dump", "PostgreSQL pg_dump client"),
            ("pg_restore", "PostgreSQL pg_restore client"),
        ):
            path_key = f"{key}_path"
            hash_key = f"{key}_sha256"
            item = {"path": client.get(path_key), "sha256": client.get(hash_key)}
            item_problems, actual = manifest_file_problems(project_root, item, label)
            problems.extend(item_problems)
            if actual is not None:
                client_paths[key] = actual
        credential_env = str(client.get("credential_env") or "").strip()
        if not re.fullmatch(r"BOMDD_[A-Z0-9_]+", credential_env):
            problems.append("postgresql_client credential_env must be a BOMDD_* environment variable")
        elif not os.environ.get(credential_env):
            problems.append(f"required credential environment variable is not set: {credential_env}")

    connection = document.get("connection")
    connection_values: dict[str, Any] = {}
    if not isinstance(connection, dict):
        problems.append("connection must be an object")
    else:
        connection_values = connection
        host = str(connection.get("host") or "").strip()
        port = connection.get("port")
        database = str(connection.get("database") or "").strip()
        user = str(connection.get("user") or "").strip()
        sslmode = str(connection.get("sslmode") or "").strip()
        timeout = connection.get("connect_timeout_seconds")
        if not host:
            problems.append("connection host is missing")
        if not isinstance(port, int) or not 1 <= port <= 65535:
            problems.append("connection port must be an integer from 1 to 65535")
        if not database:
            problems.append("connection database is missing")
        elif database != restore_database:
            problems.append("connection database must equal restore_control database")
        if not user:
            problems.append("connection user is missing")
        if sslmode not in {"disable", "allow", "prefer", "require", "verify-ca", "verify-full"}:
            problems.append("connection sslmode is invalid")
        if not isinstance(timeout, int) or not 1 <= timeout <= 60:
            problems.append("connection connect_timeout_seconds must be from 1 to 60")

    checks = document.get("expected_checks")
    if not isinstance(checks, dict):
        problems.append("expected_checks must be an object")
        checks = {}
    else:
        if checks.get("restore_result") != "pass":
            problems.append("restore_result must be pass")
        if not isinstance(checks.get("server_version_major"), int):
            problems.append("server_version_major must be an integer")
        if checks.get("default_transaction_read_only") != "on":
            problems.append("default_transaction_read_only must be on")
        if checks.get("unvalidated_constraints") != 0:
            problems.append("unvalidated_constraints must be 0")
        if checks.get("invalid_indexes") != 0:
            problems.append("invalid_indexes must be 0")

    queries = document.get("canonical_queries")
    if not isinstance(queries, list) or not queries:
        problems.append("canonical_queries must contain at least one read-only query")
        queries = []

    # Do not attempt a live connection while required structure, clients, or credentials are invalid.
    if problems:
        return problems

    assert fixture_path is not None
    psql_path = client_paths["psql"]
    pg_dump_path = client_paths["pg_dump"]
    pg_restore_path = client_paths["pg_restore"]
    timeout_seconds = int(connection_values["connect_timeout_seconds"])
    process_env = os.environ.copy()
    process_env["PGPASSWORD"] = os.environ[credential_env]
    process_env["PGSSLMODE"] = str(connection_values["sslmode"])
    process_env["PGCONNECT_TIMEOUT"] = str(timeout_seconds)
    connect_args = [
        "-h", str(connection_values["host"]),
        "-p", str(connection_values["port"]),
        "-U", str(connection_values["user"]),
        "-d", str(connection_values["database"]),
    ]

    def run_client(executable: Path, arguments: list[str], label: str) -> subprocess.CompletedProcess[str] | None:
        try:
            result = subprocess.run(
                [str(executable), *arguments],
                cwd=project_root,
                env=process_env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_seconds + 10,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            problems.append(f"{label} could not run: {exc}")
            return None
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip().replace("\r", " ").replace("\n", " ")
            problems.append(f"{label} failed with exit {result.returncode}: {detail[:500]}")
            return None
        return result

    def select_rows(sql: str, label: str) -> list[list[str]] | None:
        result = run_client(
            psql_path,
            [
                "-X", "--no-password", *connect_args, "--csv", "--tuples-only",
                "--set=ON_ERROR_STOP=1", f"--command={sql}",
            ],
            label,
        )
        if result is None:
            return None
        return [row for row in csv.reader(result.stdout.splitlines())]

    dump_list = run_client(
        pg_restore_path, ["--list", str(fixture_path)], "PostgreSQL custom dump inspection"
    )
    if dump_list is not None and not dump_list.stdout.strip():
        problems.append("PostgreSQL custom dump inspection returned an empty catalog")

    live_checks = (
        ("default_transaction_read_only", "SHOW default_transaction_read_only", [["on"]]),
        (
            "server_version_major",
            "SELECT (current_setting('server_version_num')::int / 10000)::text",
            [[str(checks["server_version_major"])]],
        ),
        (
            "unvalidated_constraints",
            "SELECT COUNT(*)::text FROM pg_constraint WHERE NOT convalidated",
            [[str(checks["unvalidated_constraints"])]],
        ),
        (
            "invalid_indexes",
            "SELECT COUNT(*)::text FROM pg_index WHERE NOT indisvalid",
            [[str(checks["invalid_indexes"])]],
        ),
    )
    for check_id, sql, expected in live_checks:
        actual = select_rows(sql, f"PostgreSQL live check {check_id}")
        if actual is not None and actual != expected:
            problems.append(f"PostgreSQL live check {check_id} differs: expected={expected!r} actual={actual!r}")

    schema_result = run_client(
        pg_dump_path,
        [*connect_args, "--schema-only", "--no-owner", "--no-acl"],
        "PostgreSQL live schema extraction",
    )
    if schema_result is not None:
        live_schema_hash = hashlib.sha256(
            normalized_postgresql_schema(schema_result.stdout).encode("utf-8")
        ).hexdigest()
        if live_schema_hash != normalized_schema_hash:
            problems.append(
                "PostgreSQL live schema hash differs: "
                f"expected={normalized_schema_hash} actual={live_schema_hash}"
            )

    seen_query_ids: set[str] = set()
    for index, query in enumerate(queries, 1):
        if not isinstance(query, dict):
            problems.append(f"canonical query {index} must be an object")
            continue
        query_id = str(query.get("id") or "").strip()
        sql = str(query.get("sql") or "").strip()
        if not query_id or query_id in seen_query_ids:
            problems.append(f"canonical query {index} has a missing or duplicate id")
        seen_query_ids.add(query_id)
        if not re.match(r"(?is)^select\s", sql) or ";" in sql:
            problems.append(f"canonical query {query_id or index} must be one SELECT without semicolon")
            continue
        expected_rows = query.get("expected_rows")
        if not isinstance(expected_rows, list) or not all(isinstance(row, list) for row in expected_rows):
            problems.append(f"canonical query {query_id or index} expected_rows must be a list of rows")
            continue
        expected_text = [[str(value) for value in row] for row in expected_rows]
        actual_rows = select_rows(sql, f"PostgreSQL canonical query {query_id or index}")
        if actual_rows is not None and actual_rows != expected_text:
            problems.append(
                f"canonical query {query_id or index} differs: "
                f"expected={expected_text!r} actual={actual_rows!r}"
            )
    return problems


def baseline_fixture_manifest_problems(project_root: Path, document: dict[str, Any]) -> list[str]:
    schema = document.get("schema")
    engine = str(document.get("engine") or "").lower()
    if schema == "bomdd-legacy-wpf-baseline-fixture/1.0" and engine == "sqlite":
        return sqlite_baseline_fixture_manifest_problems(project_root, document)
    if schema == "bomdd-legacy-wpf-baseline-fixture/1.1" and engine == "postgresql":
        return postgresql_baseline_fixture_manifest_problems(project_root, document)
    return [f"unsupported fixture manifest schema/engine: {schema} / {engine or '<missing>'}"]


def ui_evidence_manifest_problems(project_root: Path, document: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    if document.get("schema") != "bomdd-legacy-wpf-ui-evidence/1.0":
        problems.append(f"unexpected UI evidence manifest schema: {document.get('schema')}")
    if not str(document.get("source_version") or "").strip():
        problems.append("source_version is missing")
    index_problems, index_path = manifest_file_problems(
        project_root, document.get("observation_index"), "observation index"
    )
    problems.extend(index_problems)
    policy = document.get("coverage_policy")
    if not isinstance(policy, dict):
        problems.append("coverage_policy must be an object")
        policy = {}
    required_states = policy.get("required_states")
    if not isinstance(required_states, list) or not required_states:
        problems.append("coverage_policy required_states must be a non-empty list")
        required_states = []
    minimum_width = policy.get("minimum_width")
    minimum_height = policy.get("minimum_height")
    if not isinstance(minimum_width, int) or minimum_width <= 0:
        problems.append("coverage_policy minimum_width must be a positive integer")
        minimum_width = 1
    if not isinstance(minimum_height, int) or minimum_height <= 0:
        problems.append("coverage_policy minimum_height must be a positive integer")
        minimum_height = 1

    observations = document.get("observations")
    if not isinstance(observations, list) or not observations:
        problems.append("observations must contain at least one observation")
        observations = []
    observation_ids: list[str] = []
    covered_states: set[str] = set()
    allowed_kinds = {"screenshot", "dom", "accessibility-tree", "database", "execution-log", "text"}
    for obs_index, observation in enumerate(observations, 1):
        if not isinstance(observation, dict):
            problems.append(f"observation {obs_index} must be an object")
            continue
        observation_id = str(observation.get("id") or "").strip()
        if not re.fullmatch(r"OBS-CURRENT-[0-9]{3}", observation_id):
            problems.append(f"observation {obs_index} has an invalid id: {observation_id!r}")
        if observation_id in observation_ids:
            problems.append(f"duplicate observation id: {observation_id}")
        observation_ids.append(observation_id)
        states = observation.get("states")
        if not isinstance(states, list) or not states or not all(isinstance(item, str) and item for item in states):
            problems.append(f"{observation_id or obs_index} states must be a non-empty string list")
            states = []
        covered_states.update(str(item) for item in states)
        evidence = observation.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            problems.append(f"{observation_id or obs_index} evidence must be non-empty")
            evidence = []
        evidence_kinds: dict[str, str] = {}
        for evidence_index, item in enumerate(evidence, 1):
            if not isinstance(item, dict):
                problems.append(f"{observation_id} evidence {evidence_index} must be an object")
                continue
            evidence_id = str(item.get("id") or "").strip()
            kind = str(item.get("kind") or "").strip()
            if not evidence_id or evidence_id in evidence_kinds:
                problems.append(f"{observation_id} evidence has a missing or duplicate id")
            if kind not in allowed_kinds:
                problems.append(f"{observation_id}/{evidence_id} has unsupported kind: {kind}")
            evidence_kinds[evidence_id] = kind
            item_problems, actual = manifest_file_problems(
                project_root, item, f"{observation_id}/{evidence_id or evidence_index}"
            )
            problems.extend(item_problems)
            if kind == "screenshot" and actual is not None:
                try:
                    media_type, width, height = image_metadata(actual)
                    expected_media = str(item.get("media_type") or "")
                    if media_type != expected_media:
                        problems.append(
                            f"{observation_id}/{evidence_id} media type differs: "
                            f"manifest={expected_media!r} actual={media_type!r}"
                        )
                    valid_suffixes = {
                        "image/png": {".png"},
                        "image/jpeg": {".jpg", ".jpeg"},
                    }.get(media_type, set())
                    if actual.suffix.lower() not in valid_suffixes:
                        problems.append(
                            f"{observation_id}/{evidence_id} extension does not match {media_type}: {actual.name}"
                        )
                    if item.get("width") != width or item.get("height") != height:
                        problems.append(
                            f"{observation_id}/{evidence_id} dimensions differ: "
                            f"manifest={item.get('width')}x{item.get('height')} actual={width}x{height}"
                        )
                    if width < minimum_width or height < minimum_height:
                        problems.append(
                            f"{observation_id}/{evidence_id} is below minimum dimensions: "
                            f"{width}x{height} < {minimum_width}x{minimum_height}"
                        )
                except WorkflowError as exc:
                    problems.append(f"{observation_id}/{evidence_id}: {exc}")
        if "screenshot" not in evidence_kinds.values():
            problems.append(f"{observation_id} requires at least one screenshot")
        if not any(kind != "screenshot" for kind in evidence_kinds.values()):
            problems.append(f"{observation_id} requires at least one non-screenshot semantic evidence")
        claims = observation.get("claims")
        if not isinstance(claims, list) or not claims:
            problems.append(f"{observation_id} claims must be non-empty")
            claims = []
        supported_kinds: set[str] = set()
        for claim_index, claim in enumerate(claims, 1):
            if not isinstance(claim, dict) or not str(claim.get("text") or "").strip():
                problems.append(f"{observation_id} claim {claim_index} text is missing")
                continue
            supports = claim.get("supported_by")
            if not isinstance(supports, list) or not supports:
                problems.append(f"{observation_id} claim {claim_index} supported_by is empty")
                continue
            for evidence_id in supports:
                if evidence_id not in evidence_kinds:
                    problems.append(
                        f"{observation_id} claim {claim_index} references unknown evidence: {evidence_id}"
                    )
                else:
                    supported_kinds.add(evidence_kinds[evidence_id])
        if "screenshot" not in supported_kinds:
            problems.append(f"{observation_id} has no claim supported by a screenshot")
        if not any(kind != "screenshot" for kind in supported_kinds):
            problems.append(f"{observation_id} has no claim supported by semantic evidence")

    missing_states = sorted(set(str(item) for item in required_states) - covered_states)
    if missing_states:
        problems.append(f"required UI states are not covered: {', '.join(missing_states)}")
    if index_path is not None:
        index_ids = re.findall(
            r"^\|\s*(OBS-CURRENT-[0-9]{3})\s*\|", index_path.read_text(encoding="utf-8"), re.MULTILINE
        )
        if sorted(set(index_ids)) != sorted(set(observation_ids)):
            problems.append(
                f"observation index IDs differ from manifest: index={sorted(set(index_ids))} "
                f"manifest={sorted(set(observation_ids))}"
            )
    return problems


def placeholder(value: Any) -> bool:
    text = str(value or "").strip()
    return not text or text in {"REPLACE", "UNASSIGNED", "UNDECIDED"} or text.startswith("REPLACE-")


def referenced_evidence_problems(
    project_root: Path, values: list[Any], accepted_evidence: list[str], label: str
) -> list[str]:
    problems: list[str] = []
    root = project_root.resolve()
    for value in values:
        path_text = str(value or "").strip()
        if placeholder(path_text):
            problems.append(f"{label} evidence path is missing")
            continue
        actual = (root / path_text).resolve()
        try:
            actual.relative_to(root)
        except ValueError:
            problems.append(f"{label} evidence must be project-local: {path_text}")
            continue
        if not actual.is_file():
            problems.append(f"{label} evidence file not found: {path_text}")
        if path_text not in accepted_evidence:
            problems.append(f"{label} evidence must be included in --evidence: {path_text}")
    return problems


def json_content_document(project_root: Path, required: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    actual = project_root.resolve() / str(required.get("path") or "")
    try:
        return read_json(actual), []
    except WorkflowError as exc:
        return None, [str(exc)]


def basic_artifact_problems(project_root: Path, required: dict[str, Any]) -> list[str]:
    path_text = str(required.get("path") or "")
    actual = project_root.resolve() / path_text
    if not actual.is_file():
        return [f"artifact file not found: {path_text}"]
    if actual.stat().st_size < 8:
        return [f"artifact is empty or too small to be a completed result: {path_text}"]
    if actual.suffix.lower() not in {".md", ".json", ".yaml", ".yml", ".log", ".txt", ".sql"}:
        return []
    try:
        text = actual.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    tokens = sorted(set(re.findall(r"\b(?:UNASSIGNED|REPLACE(?:-[A-Za-z0-9_-]+)?|TBD|TODO)\b", text)))
    problems = [f"artifact contains unresolved placeholder {token!r}: {path_text}" for token in tokens]
    if re.search(r"\{\{[^}\r\n]+\}\}", text):
        problems.append(f"artifact contains an unresolved template expression: {path_text}")
    if re.search(r"<(?:値|対象|責任者|なければ|絶対パス|既存|記載|入力|説明)[^>\r\n]*>", text):
        problems.append(f"artifact contains an unresolved angle-bracket instruction: {path_text}")
    return problems


def required_ids_problems(records: Any, required_ids: set[str], label: str) -> list[str]:
    if not isinstance(records, list):
        return [f"{label} must be a list"]
    ids = [str(item.get("id")) for item in records if isinstance(item, dict) and item.get("id")]
    problems: list[str] = []
    if len(ids) != len(set(ids)):
        problems.append(f"{label} IDs must be unique")
    missing = sorted(required_ids - set(ids))
    if missing:
        problems.append(f"{label} missing required IDs: {', '.join(missing)}")
    return problems


def artifact_content_problems(
    project_root: Path, required: dict[str, Any], evidence_paths: list[str]
) -> list[str]:
    problems = basic_artifact_problems(project_root, required)
    validation_type = required.get("content_validation")
    if validation_type is None:
        return problems
    document, json_problems = json_content_document(project_root, required)
    problems.extend(json_problems)
    if document is None:
        return problems

    if validation_type == "enterprise-profile":
        if document.get("schema") != "bomdd-legacy-wpf-profile/2.0":
            problems.append("profile schema must be bomdd-legacy-wpf-profile/2.0")
        scenario = document.get("scenario") or {}
        source = document.get("source") or {}
        target = document.get("target") or {}
        constraints = document.get("constraints") or {}
        scale = document.get("scale_control") or {}
        if scenario.get("mode") != "enterprise-javafx":
            problems.append("scenario.mode must be enterprise-javafx")
        if source.get("language") != "Java" or source.get("ui_framework") != "JavaFX":
            problems.append("source must explicitly be Java + JavaFX")
        if target.get("language") != "C#" or target.get("ui_framework") != "WPF":
            problems.append("target must explicitly be C# + WPF")
        for key in ("jdk_line", "javafx_line"):
            if placeholder(source.get(key)):
                problems.append(f"source.{key} must be decided")
        builds = source.get("build_systems")
        if not isinstance(builds, list) or not builds or any(placeholder(item) for item in builds):
            problems.append("source.build_systems must name the actual build systems")
        for key in ("estimated_loc", "repository_count", "module_count", "screen_count", "customer_count", "active_user_count"):
            if not isinstance(source.get(key), int) or source.get(key, 0) <= 0:
                problems.append(f"source.{key} must be greater than zero")
        for key in ("database_engine", "customer_outage_budget"):
            if placeholder(constraints.get(key)):
                problems.append(f"constraints.{key} must be decided")
        for key in ("maximum_slice_person_days", "maximum_work_in_progress_per_worker"):
            if not isinstance(scale.get(key), int) or scale.get(key, 0) <= 0:
                problems.append(f"scale_control.{key} must be greater than zero")
        owners = document.get("owners")
        if not isinstance(owners, dict):
            problems.append("owners must be an object")
        else:
            missing = [key for key, value in owners.items() if placeholder(value)]
            if missing:
                problems.append(f"owners are unassigned: {', '.join(missing)}")
            if owners.get("Migration Owner") == owners.get("Customer Acceptance Owner"):
                problems.append("Migration Owner and Customer Acceptance Owner must be different")
            if owners.get("Release Owner") == owners.get("Security Owner"):
                problems.append("Release Owner and Security Owner must be different")

    elif validation_type == "nfr-baseline":
        if document.get("schema") != "bomdd-javafx-wpf-nfr-baseline/2.0":
            problems.append("unexpected NFR baseline schema")
        if placeholder(document.get("source_version")) or placeholder(document.get("environment_id")):
            problems.append("NFR source_version and environment_id must be fixed")
        if not isinstance(document.get("datasets"), list) or not document["datasets"]:
            problems.append("NFR datasets must be non-empty")
        if not isinstance(document.get("workloads"), list) or not document["workloads"]:
            problems.append("NFR workloads must be non-empty")
        required_metrics = {"NFR-START-COLD", "NFR-UI-INPUT", "NFR-DB-ROUNDTRIP", "NFR-MEMORY-SOAK", "NFR-BATCH"}
        metrics = document.get("metrics")
        problems.extend(required_ids_problems(metrics, required_metrics, "NFR metrics"))
        refs: list[Any] = []
        if isinstance(metrics, list):
            for item in metrics:
                if not isinstance(item, dict):
                    continue
                if not isinstance(item.get("sample_count"), int) or item.get("sample_count", 0) <= 0:
                    problems.append(f"{item.get('id')} sample_count must be greater than zero")
                refs.append(item.get("evidence"))
        problems.extend(referenced_evidence_problems(project_root, refs, evidence_paths, "NFR"))

    elif validation_type == "feasibility-portfolio":
        if document.get("schema") != "bomdd-javafx-wpf-feasibility/2.0":
            problems.append("unexpected feasibility portfolio schema")
        required_classes = {"javafx-ui", "rdb-read-write", "external-integration", "performance-memory", "install-update", "security-identity", "third-party-replacement"}
        items = document.get("items")
        if not isinstance(items, list):
            problems.append("feasibility items must be a list")
            items = []
        classes = [str(item.get("risk_class")) for item in items if isinstance(item, dict)]
        if set(classes) != required_classes or len(classes) != len(required_classes):
            problems.append("feasibility portfolio must cover every required risk class exactly once")
        refs: list[Any] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            if item.get("result") not in {"pass", "accepted-risk"}:
                problems.append(f"{item.get('id')} result must be pass or accepted-risk")
            if placeholder(item.get("representative_ref")) or placeholder(item.get("owner")) or placeholder(item.get("fallback")):
                problems.append(f"{item.get('id')} representative, owner and fallback must be decided")
            values = item.get("evidence")
            if not isinstance(values, list) or not values:
                problems.append(f"{item.get('id')} evidence must be non-empty")
            else:
                refs.extend(values)
        if document.get("go_no_go") != "go":
            problems.append("feasibility go_no_go must be go")
        problems.extend(referenced_evidence_problems(project_root, refs, evidence_paths, "feasibility"))

    elif validation_type == "code-inventory":
        if document.get("schema") != "bomdd-javafx-wpf-code-inventory/2.0":
            problems.append("unexpected code inventory schema")
        totals = document.get("totals") or {}
        for key in ("files", "loc", "modules"):
            if not isinstance(totals.get(key), int) or totals.get(key, 0) <= 0:
                problems.append(f"code inventory totals.{key} must be greater than zero")
        if document.get("unclassified_files") != 0 or document.get("unclassified_loc") != 0:
            problems.append("code inventory must have zero unclassified files and LOC")
        modules = document.get("modules")
        if not isinstance(modules, list) or not modules:
            problems.append("code inventory modules must be non-empty")
        else:
            for item in modules:
                if not isinstance(item, dict) or placeholder(item.get("owner")) or item.get("disposition") == "open":
                    problems.append(f"module {item.get('id') if isinstance(item, dict) else '?'} owner/disposition is incomplete")
        required_categories = {"production-java", "test-java", "fxml", "css", "resources-i18n", "generated", "native", "build-deploy"}
        categories = document.get("categories")
        problems.extend(required_ids_problems(categories, required_categories, "code categories"))
        if isinstance(categories, list):
            category_files = sum(item.get("files", 0) for item in categories if isinstance(item, dict) and isinstance(item.get("files"), int))
            category_loc = sum(item.get("loc", 0) for item in categories if isinstance(item, dict) and isinstance(item.get("loc"), int))
            if category_files != totals.get("files") or category_loc != totals.get("loc"):
                problems.append("code category counts must equal total files and LOC")
        refs = document.get("evidence")
        if not isinstance(refs, list) or not refs:
            problems.append("code inventory evidence must be non-empty")
        else:
            problems.extend(referenced_evidence_problems(project_root, refs, evidence_paths, "code inventory"))

    elif validation_type == "workstream-register":
        if document.get("schema") != "bomdd-javafx-wpf-workstream-register/2.0":
            problems.append("unexpected workstream register schema")
        streams = document.get("workstreams")
        if not isinstance(streams, list) or not streams:
            return [*problems, "workstream register must contain at least one workstream"]
        stream_ids = [str(item.get("id")) for item in streams if isinstance(item, dict)]
        if len(stream_ids) != len(set(stream_ids)) or any(not re.fullmatch(r"WS-[A-Z0-9-]+", item) for item in stream_ids):
            problems.append("workstream IDs must be unique WS-* identifiers")
        slice_ids: list[str] = []
        maximum = ((read_json(migration_root(project_root) / "migration-profile.json").get("scale_control") or {}).get("maximum_slice_person_days", 0))
        dependencies: dict[str, list[str]] = {}
        for stream in streams:
            if not isinstance(stream, dict):
                problems.append("workstream entry must be an object")
                continue
            sid = str(stream.get("id"))
            if placeholder(stream.get("lead")) or placeholder(stream.get("reviewer")) or placeholder(stream.get("acceptance_delegate")):
                problems.append(f"{sid} assignments are incomplete")
            if stream.get("lead") == stream.get("reviewer"):
                problems.append(f"{sid} lead and reviewer must be different")
            deps = stream.get("depends_on") if isinstance(stream.get("depends_on"), list) else []
            dependencies[sid] = [str(item) for item in deps]
            slices = stream.get("slices")
            if not isinstance(slices, list) or not slices:
                problems.append(f"{sid} must contain slices")
                continue
            for item in slices:
                if not isinstance(item, dict):
                    continue
                slice_id = str(item.get("id"))
                slice_ids.append(slice_id)
                if not re.fullmatch(r"SLICE-[A-Z0-9-]+", slice_id):
                    problems.append(f"invalid slice ID: {slice_id}")
                estimate = item.get("estimated_person_days")
                if not isinstance(estimate, (int, float)) or estimate <= 0 or estimate > maximum:
                    problems.append(f"{slice_id} estimate must be >0 and <= {maximum}")
                if item.get("state") != "planned" or not item.get("refs") or not item.get("risk_classes"):
                    problems.append(f"{slice_id} must start planned with refs and risk classes")
        if len(slice_ids) != len(set(slice_ids)):
            problems.append("slice IDs must be globally unique")
        for sid, deps in dependencies.items():
            if sid in deps or any(dep not in stream_ids for dep in deps):
                problems.append(f"{sid} has an invalid dependency")
        def reaches(start: str, node: str, visited: set[str]) -> bool:
            if node == start:
                return True
            if node in visited:
                return False
            return any(reaches(start, nxt, visited | {node}) for nxt in dependencies.get(node, []))
        if any(reaches(sid, dep, set()) for sid, deps in dependencies.items() for dep in deps):
            problems.append("workstream dependency graph contains a cycle")

    elif validation_type == "nfr-contract":
        if document.get("schema") != "bomdd-javafx-wpf-nfr-contract/2.0":
            problems.append("unexpected NFR contract schema")
        required_metrics = {"NFR-START-COLD", "NFR-UI-INPUT", "NFR-DB-ROUNDTRIP", "NFR-MEMORY-SOAK", "NFR-BATCH"}
        metrics = document.get("metrics")
        problems.extend(required_ids_problems(metrics, required_metrics, "NFR contract metrics"))
        for item in metrics if isinstance(metrics, list) else []:
            if not isinstance(item, dict):
                continue
            if not isinstance(item.get("limit"), (int, float)) or item.get("limit", 0) <= 0:
                problems.append(f"{item.get('id')} limit must be greater than zero")
            if any(placeholder(item.get(key)) for key in ("workload", "dataset", "evidence_required", "owner")):
                problems.append(f"{item.get('id')} contract fields are incomplete")

    elif validation_type == "interface-register":
        if document.get("schema") != "bomdd-javafx-wpf-interface-register/2.0":
            problems.append("unexpected interface register schema")
        streams_doc = read_json(migration_root(project_root) / "workstream-register.json")
        valid_streams = {str(item.get("id")) for item in streams_doc.get("workstreams", []) if isinstance(item, dict)}
        interfaces = document.get("interfaces")
        if not isinstance(interfaces, list):
            problems.append("interfaces must be a list")
            interfaces = []
        ids = [str(item.get("id")) for item in interfaces if isinstance(item, dict)]
        if len(ids) != len(set(ids)):
            problems.append("interface IDs must be unique")
        refs: list[Any] = []
        for item in interfaces:
            if not isinstance(item, dict):
                continue
            iid = item.get("id")
            producer = item.get("producer_workstream")
            consumers = item.get("consumer_workstreams")
            if producer not in valid_streams or not isinstance(consumers, list) or any(value not in valid_streams for value in consumers):
                problems.append(f"{iid} producer/consumer references are invalid")
            if placeholder(item.get("version")) or placeholder(item.get("owner")) or item.get("status") not in {"decided", "accepted"}:
                problems.append(f"{iid} version, owner or status is incomplete")
            contract_path = item.get("contract_path")
            refs.append(contract_path)
            if not item.get("contract_tests"):
                problems.append(f"{iid} contract_tests must be non-empty")
            if not placeholder(contract_path):
                actual = project_root.resolve() / str(contract_path)
                if actual.is_file() and str(item.get("contract_sha256") or "").lower() != file_sha256(actual).lower():
                    problems.append(f"{iid} contract_sha256 mismatch")
        problems.extend(referenced_evidence_problems(project_root, refs, evidence_paths, "interface contract"))

    elif validation_type == "ci-readiness":
        if document.get("schema") != "bomdd-javafx-wpf-ci-readiness/2.0":
            problems.append("unexpected CI readiness schema")
        required_checks = {"CI-RESTORE", "CI-BUILD", "CI-TEST", "CI-PUBLISH", "CI-INSTALL-SMOKE", "CI-SBOM", "CI-SIGN-VERIFY-DRYRUN"}
        checks = document.get("checks")
        problems.extend(required_ids_problems(checks, required_checks, "CI checks"))
        refs: list[Any] = []
        for item in checks if isinstance(checks, list) else []:
            if isinstance(item, dict):
                if item.get("result") != "pass" or placeholder(item.get("command")):
                    problems.append(f"{item.get('id')} must have command and pass result")
                refs.append(item.get("evidence"))
        problems.extend(referenced_evidence_problems(project_root, refs, evidence_paths, "CI"))

    elif validation_type == "pilot-portfolio":
        if document.get("schema") != "bomdd-javafx-wpf-pilot-portfolio/2.0":
            problems.append("unexpected pilot portfolio schema")
        if placeholder(document.get("release_candidate")):
            problems.append("pilot release_candidate must be fixed")
        required_classes = set(document.get("required_risk_classes") or [])
        items = document.get("items") if isinstance(document.get("items"), list) else []
        actual_classes = [str(item.get("risk_class")) for item in items if isinstance(item, dict)]
        if not required_classes or set(actual_classes) != required_classes or len(actual_classes) != len(required_classes):
            problems.append("pilot portfolio must cover each required risk class exactly once")
        refs: list[Any] = [document.get("clean_install_evidence")]
        for item in items:
            if not isinstance(item, dict):
                continue
            if item.get("status") not in {"pass", "accepted"} or placeholder(item.get("approver")):
                problems.append(f"pilot {item.get('risk_class')} is not accepted")
            values = item.get("evidence")
            if not isinstance(values, list) or not values:
                problems.append(f"pilot {item.get('risk_class')} evidence is empty")
            else:
                refs.extend(values)
        if document.get("aggregate_result") != "pass":
            problems.append("pilot aggregate_result must be pass")
        problems.extend(referenced_evidence_problems(project_root, refs, evidence_paths, "pilot"))

    elif validation_type == "workstream-snapshot":
        if document.get("schema") != "bomdd-javafx-wpf-workstream-snapshot/2.0":
            problems.append("unexpected workstream snapshot schema")
        register = document.get("register") or {}
        register_path = str(register.get("path") or "")
        actual_register = project_root.resolve() / register_path
        if not actual_register.is_file() or str(register.get("sha256") or "").lower() != file_sha256(actual_register).lower():
            problems.append("workstream snapshot register hash is missing or mismatched")
        streams = document.get("workstreams") if isinstance(document.get("workstreams"), list) else []
        totals = {"workstreams": len(streams), "slices": 0, "as_built": 0, "blockers": 0}
        refs: list[Any] = [register_path]
        for item in streams:
            if not isinstance(item, dict):
                continue
            status_path = str(item.get("status_path") or "")
            refs.append(status_path)
            actual = project_root.resolve() / status_path
            if not actual.is_file() or str(item.get("sha256") or "").lower() != file_sha256(actual).lower():
                problems.append(f"{item.get('id')} status hash is missing or mismatched")
                continue
            status_doc = read_json(actual)
            for problem in workstream_status_problems(project_root, status_doc):
                problems.append(f"{item.get('id')}: {problem}")
            slices = status_doc.get("slices") if isinstance(status_doc.get("slices"), list) else []
            as_built = sum(1 for value in slices if isinstance(value, dict) and value.get("state") == "as-built")
            blockers = sum(len(value.get("blockers") or []) for value in slices if isinstance(value, dict))
            totals["slices"] += len(slices); totals["as_built"] += as_built; totals["blockers"] += blockers
            if item.get("slice_count") != len(slices) or item.get("as_built_count") != as_built or item.get("blocker_count") != blockers:
                problems.append(f"{item.get('id')} snapshot counters mismatch")
        if document.get("totals") != totals:
            problems.append("workstream snapshot totals mismatch")
        if totals["slices"] == 0 or totals["slices"] != totals["as_built"] or totals["blockers"] != 0 or document.get("result") != "pass":
            problems.append("all slices must be as-built with zero blockers and result pass")
        problems.extend(referenced_evidence_problems(project_root, refs, evidence_paths, "workstream snapshot"))

    elif validation_type == "rc-acceptance":
        if document.get("schema") != "bomdd-javafx-wpf-rc-acceptance/2.0":
            problems.append("unexpected RC acceptance schema")
        if placeholder(document.get("release_id")):
            problems.append("RC release_id must be fixed")
        required_checks = {"RC-FUNCTIONAL", "RC-NFR", "RC-SECURITY", "RC-UAT", "RC-INSTALL-UPGRADE", "RC-OPERATIONS", "RC-ACCESSIBILITY"}
        checks = document.get("checks")
        problems.extend(required_ids_problems(checks, required_checks, "RC checks"))
        refs: list[Any] = [document.get("release_manifest_path")]
        for item in checks if isinstance(checks, list) else []:
            if isinstance(item, dict):
                if item.get("result") != "pass":
                    problems.append(f"{item.get('id')} must pass")
                if placeholder(item.get("approver_role")):
                    problems.append(f"{item.get('id')} approver_role is missing")
                refs.append(item.get("evidence"))
        manifest_path = project_root.resolve() / str(document.get("release_manifest_path") or "")
        if manifest_path.is_file() and str(document.get("release_manifest_sha256") or "").lower() != file_sha256(manifest_path).lower():
            problems.append("release candidate manifest hash mismatch")
        if document.get("aggregate_result") != "pass":
            problems.append("RC aggregate_result must be pass")
        problems.extend(referenced_evidence_problems(project_root, refs, evidence_paths, "RC"))

    elif validation_type == "signed-release":
        if document.get("schema") != "bomdd-javafx-wpf-signed-release/2.0":
            problems.append("unexpected signed release schema")
        if any(placeholder(document.get(key)) for key in ("release_id", "version", "source_commit", "approved_at")):
            problems.append("signed release identity/approval fields are incomplete")
        refs: list[Any] = [document.get("build_evidence")]
        artifacts = document.get("artifacts") if isinstance(document.get("artifacts"), list) else []
        if not artifacts:
            problems.append("signed release artifacts must be non-empty")
        for item in artifacts:
            if not isinstance(item, dict):
                continue
            path_text = str(item.get("path") or "")
            refs.append(path_text)
            actual = project_root.resolve() / path_text
            if not actual.is_file() or str(item.get("sha256") or "").lower() != file_sha256(actual).lower():
                problems.append(f"release artifact hash mismatch: {path_text}")
            elif item.get("size") != actual.stat().st_size:
                problems.append(f"release artifact size mismatch: {path_text}")
            if item.get("signature_verified") is not True or placeholder(item.get("signature")):
                problems.append(f"release artifact signature is not verified: {path_text}")
        sbom = document.get("sbom") or {}
        refs.append(sbom.get("path"))
        sbom_path = project_root.resolve() / str(sbom.get("path") or "")
        if not sbom_path.is_file() or str(sbom.get("sha256") or "").lower() != file_sha256(sbom_path).lower():
            problems.append("SBOM hash is missing or mismatched")
        certificate = document.get("certificate") or {}
        if any(placeholder(certificate.get(key)) for key in ("subject", "thumbprint", "valid_from", "valid_to")):
            problems.append("signing certificate metadata is incomplete")
        if placeholder(document.get("promoted_from_release_candidate_sha256")):
            problems.append("release candidate promotion hash is missing")
        problems.extend(referenced_evidence_problems(project_root, refs, evidence_paths, "signed release"))

    elif validation_type == "cohort-ledger":
        if document.get("schema") != "bomdd-javafx-wpf-cohort-ledger/2.0":
            problems.append("unexpected cohort ledger schema")
        if placeholder(document.get("release_id")) or placeholder(document.get("rollout_plan_sha256")):
            problems.append("cohort release_id and rollout_plan_sha256 must be fixed")
        cohorts = document.get("cohorts") if isinstance(document.get("cohorts"), list) else []
        if not cohorts:
            problems.append("cohort ledger must contain cohorts")
        rollout_path = migration_root(project_root) / "rollout-plan.md"
        refs: list[Any] = ["bomdd/migration/rollout-plan.md"]
        if not rollout_path.is_file() or str(document.get("rollout_plan_sha256") or "").lower() != file_sha256(rollout_path).lower():
            problems.append("cohort rollout_plan_sha256 is missing or mismatched")
        customers = accepted = deferred = 0
        for item in cohorts:
            if not isinstance(item, dict):
                continue
            count = item.get("customer_count") if isinstance(item.get("customer_count"), int) else 0
            customers += count
            if item.get("state") == "accepted":
                accepted += count
                refs.extend(item.get(key) for key in ("go_no_go_evidence", "smoke_evidence", "db_reconciliation_evidence", "telemetry_evidence", "customer_acceptance_evidence"))
            elif item.get("state") == "deferred":
                deferred += count
                refs.extend(item.get(key) for key in ("go_no_go_evidence", "customer_acceptance_evidence"))
                if not item.get("blockers"):
                    problems.append(f"{item.get('id')} deferred state requires a bounded blocker/reason")
            else: problems.append(f"{item.get('id')} must be accepted or formally deferred")
        if document.get("in_scope_customer_count") != customers or document.get("accepted_customer_count") != accepted or document.get("formally_deferred_customer_count") != deferred:
            problems.append("cohort customer counters mismatch")
        if customers <= 0 or customers != accepted + deferred or document.get("aggregate_result") != "pass":
            problems.append("all in-scope customers must be accepted or formally deferred with aggregate pass")
        problems.extend(referenced_evidence_problems(project_root, refs, evidence_paths, "cohort"))
    else:
        problems.append(f"unknown content validation type: {validation_type}")
    return problems


def artifact_semantic_problems(
    project_root: Path, required: dict[str, Any], evidence_paths: list[str]
) -> list[str]:
    problems = artifact_content_problems(project_root, required, evidence_paths)
    spec = required.get("semantic_validation")
    if spec is None:
        return problems
    if not isinstance(spec, dict):
        return [*problems, "semantic_validation definition must be an object"]
    manifest_path = str(spec.get("manifest") or "").strip()
    if not manifest_path:
        return [*problems, "semantic validation manifest path is missing"]
    if manifest_path not in evidence_paths:
        return [*problems, f"semantic manifest must be included in artifact evidence: {manifest_path}"]
    actual = project_root.resolve() / manifest_path
    try:
        document = read_json(actual)
    except WorkflowError as exc:
        return [*problems, str(exc)]
    validation_type = spec.get("type")
    if validation_type == "baseline-fixture-manifest":
        return [*problems, *baseline_fixture_manifest_problems(project_root, document)]
    if validation_type == "ui-evidence-manifest":
        return [*problems, *ui_evidence_manifest_problems(project_root, document)]
    return [*problems, f"unknown semantic validation type: {validation_type}"]


def milestone_steps(mig: Path, milestone_id: str) -> list[tuple[str, str]]:
    milestones = load_definition(mig).get("milestones")
    if not isinstance(milestones, list):
        raise WorkflowError("milestone definition has no milestones list")
    index = next((i for i, item in enumerate(milestones) if item.get("id") == milestone_id), None)
    if index is None:
        raise WorkflowError(f"invalid milestone id for STEP lookup: {milestone_id}")
    entry_match = re.fullmatch(r"STEP-(\d{3})", str(milestones[index].get("entry_step")))
    if entry_match is None:
        raise WorkflowError(f"invalid entry_step for {milestone_id}")
    first_step = int(entry_match.group(1))
    next_step: int | None = None
    if index + 1 < len(milestones):
        next_match = re.fullmatch(r"STEP-(\d{3})", str(milestones[index + 1].get("entry_step")))
        if next_match is None:
            raise WorkflowError(f"invalid entry_step for {milestones[index + 1].get('id')}")
        next_step = int(next_match.group(1))
    guide = mig / "guide" / "migration-runbook.md"
    pattern = re.compile(r"^### (STEP-(\d{3})) (.+)$")
    result: list[tuple[str, str]] = []
    for line in guide.read_text(encoding="utf-8").splitlines():
        step_match = pattern.match(line)
        if not step_match:
            continue
        step_number = int(step_match.group(2))
        if step_number >= first_step and (next_step is None or step_number < next_step):
            result.append((step_match.group(1), step_match.group(3).strip()))
    if not result:
        raise WorkflowError(f"no STEP headings found for {milestone_id}; use EX-DOC-001")
    return result


def complete_step(project_root: Path, evidence: list[str]) -> None:
    mig, _, status = require_scenario(project_root)
    require_no_active_change(status, "complete-step")
    require_no_blockers(status, "complete-step")
    current = status.get("current") or {}
    milestone_id = str(current.get("milestone"))
    current_step = str(current.get("step"))
    steps = milestone_steps(mig, milestone_id)
    step_ids = [item[0] for item in steps]
    if current_step not in step_ids:
        if current_step == f"GATE-{milestone_id}":
            raise WorkflowError(f"all STEP work is complete; run check, then advance for {milestone_id}")
        raise WorkflowError(f"current STEP {current_step} is not defined for {milestone_id}; use EX-STATE-001")
    definition = load_definition(mig)
    current_def = milestone_map(definition).get(milestone_id, {})
    for decision_set_id in current_def.get("required_decision_sets", []):
        problems = decision_set_gate_problems(
            project_root, status, definition, str(decision_set_id)
        )
        if problems:
            raise WorkflowError(
                f"cannot complete {current_step}; required technical decision set "
                f"{decision_set_id} is not accepted: {problems[0]}"
            )
    normalized = project_evidence_paths(project_root, evidence)
    index = step_ids.index(current_step)
    history = status.setdefault("step_history", [])
    if not isinstance(history, list):
        raise WorkflowError("migration-status.json step_history must be a list")
    history.append({
        "milestone": milestone_id,
        "step": current_step,
        "action": current.get("action"),
        "completed_at": now_iso(),
        "evidence": normalized,
    })
    if index + 1 < len(steps):
        next_step, next_action = steps[index + 1]
        current["step"] = next_step
        current["action"] = next_action
        if index + 2 < len(steps):
            after_step, after_action = steps[index + 2]
        else:
            after_step, after_action = f"GATE-{milestone_id}", f"{milestone_id} Gate を確認する"
        status["next"] = {"step": after_step, "action": after_action}
    else:
        current["step"] = f"GATE-{milestone_id}"
        current["action"] = f"{milestone_id} Gate を確認する"
        status["next"] = {"step": "advance", "action": "Gate PASS 後に次のマイルストーンへ進む"}
    status["updated_at"] = now_iso()
    atomic_write_json(mig / "migration-status.json", status)
    print(f"[completed] {current_step}")
    print(f"[next] {current.get('step')} - {current.get('action')}")


def accept_artifact(project_root: Path, artifact_id: str, evidence: list[str]) -> None:
    mig, _, status = require_scenario(project_root)
    require_no_active_change(status, "accept-artifact")
    require_no_blockers(status, "accept-artifact")
    definition = load_definition(mig)
    milestones = milestone_map(definition)
    current_id = str((status.get("current") or {}).get("milestone"))
    current_def = milestones.get(current_id)
    if current_def is None:
        raise WorkflowError(f"unknown current milestone: {current_id}")
    required_specs = {
        item["id"]: item for item in current_def.get("required_artifacts", [])
    }
    allowed = set(required_specs)
    if artifact_id not in allowed:
        raise WorkflowError(
            f"{artifact_id} is not required by current milestone {current_id}; "
            "do not accept future-milestone artifacts"
        )
    records = artifact_records(status)
    record = records.get(artifact_id)
    if record is None:
        raise WorkflowError(f"artifact is not registered: {artifact_id}")
    if record.get("status") == "accepted":
        raise WorkflowError(
            f"{artifact_id} is already accepted; use check and change-open for any content change"
        )
    artifact_path = project_root.resolve() / str(record.get("path"))
    if not artifact_path.is_file():
        raise WorkflowError(f"artifact file not found: {artifact_path}")
    decision_spec = next(
        (
            item for item in decision_set_map(definition).values()
            if item.get("artifact_id") == artifact_id
        ),
        None,
    )
    if decision_spec is not None:
        document = read_json(artifact_path)
        problems = decision_document_problems(project_root, decision_spec, document)
        if problems:
            raise WorkflowError(
                f"cannot accept {artifact_id}; technical decision set is incomplete: {problems[0]}"
            )
    normalized = project_evidence_paths(project_root, evidence)
    semantic_problems = artifact_semantic_problems(
        project_root, required_specs[artifact_id], normalized
    )
    if semantic_problems:
        raise WorkflowError(
            f"cannot accept {artifact_id}; semantic evidence validation failed: "
            f"{semantic_problems[0]}"
        )
    record["status"] = "accepted"
    record["evidence"] = normalized
    record["content_hashes"] = content_hashes(
        project_root, [str(record.get("path")), *normalized]
    )
    record["accepted_at"] = now_iso()
    if artifact_id == "ART-PROFILE":
        accepted_profile = read_json(artifact_path)
        migration_owner = (accepted_profile.get("owners") or {}).get("Migration Owner")
        current = status.get("current")
        if isinstance(current, dict) and migration_owner and migration_owner != "UNASSIGNED":
            current["owner"] = migration_owner
    status["updated_at"] = now_iso()
    atomic_write_json(mig / "migration-status.json", status)
    print(f"[accepted] {artifact_id} - {record.get('path')}")


def approve_milestone(project_root: Path, role: str, approver: str, evidence: str) -> None:
    mig, _, status = require_scenario(project_root)
    require_no_active_change(status, "approve")
    require_no_blockers(status, "approve")
    definition = load_definition(mig)
    milestones = milestone_map(definition)
    current_id = str((status.get("current") or {}).get("milestone"))
    current_def = milestones.get(current_id)
    if current_def is None:
        raise WorkflowError(f"unknown current milestone: {current_id}")
    required_roles = set(current_def.get("required_approvals", []))
    if role not in required_roles:
        raise WorkflowError(f"role {role!r} is not a required approver for {current_id}")
    records = artifact_records(status)
    unfinished = [item["id"] for item in current_def.get("required_artifacts", [])
                  if records.get(item["id"], {}).get("status") != "accepted"]
    if unfinished:
        raise WorkflowError(f"cannot approve {current_id}; unaccepted artifacts: {', '.join(unfinished)}")
    if not approver.strip() or approver == "UNASSIGNED":
        raise WorkflowError("--approver must name the assigned person/team")
    evidence_path = project_evidence_paths(project_root, [evidence])[0]
    approvals = status.setdefault("approvals", [])
    if not isinstance(approvals, list):
        raise WorkflowError("migration-status.json approvals must be a list")
    existing = [item for item in approvals if (
        isinstance(item, dict)
        and item.get("milestone") == current_id
        and item.get("role") == role
        and item.get("status") == "approved"
    )]
    if existing:
        raise WorkflowError(
            f"{current_id} already has an approved record for {role}; use change-open to replace it"
        )
    approvals.append({
        "milestone": current_id,
        "role": role,
        "status": "approved",
        "approver": approver,
        "evidence": evidence_path,
        "evidence_sha256": file_sha256(project_root.resolve() / evidence_path),
        "approved_at": now_iso(),
    })
    status["updated_at"] = now_iso()
    atomic_write_json(mig / "migration-status.json", status)
    print(f"[approved] {current_id} by {role}: {approver}")


def seal_milestone(project_root: Path, milestone_id: str, reviewer: str, review_evidence: str) -> None:
    mig, _, status = require_scenario(project_root)
    require_no_active_change(status, "seal-milestone")
    require_no_blockers(status, "seal-milestone")
    definition = load_definition(mig)
    milestones = milestone_map(definition)
    milestone = milestones.get(milestone_id)
    if milestone is None:
        raise WorkflowError(f"unknown milestone: {milestone_id}")
    if not reviewer.strip() or reviewer == "UNASSIGNED":
        raise WorkflowError("--reviewer must name the person/team reviewing the existing accepted content")
    review_path = project_evidence_paths(project_root, [review_evidence])[0]
    records = artifact_records(status)
    required_records: list[dict[str, Any]] = []
    for required in milestone.get("required_artifacts", []):
        record = records.get(required["id"])
        if record is None or record.get("status") != "accepted":
            raise WorkflowError(f"cannot seal {milestone_id}; artifact is not accepted: {required['id']}")
        if isinstance(record.get("content_hashes"), dict) and record.get("content_hashes"):
            raise WorkflowError(
                f"cannot seal {milestone_id}; {required['id']} already has a content seal; "
                "use change-open for accepted changes"
            )
        evidence = record.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            raise WorkflowError(f"cannot seal {milestone_id}; evidence is missing: {required['id']}")
        required_records.append(record)
    for record in required_records:
        evidence = record["evidence"]
        if review_path not in evidence:
            evidence.append(review_path)
        record["content_hashes"] = content_hashes(
            project_root, [str(record.get("path")), *[str(path) for path in evidence]]
        )
        record["content_sealed_at"] = now_iso()
        record["content_sealed_by"] = reviewer
    approvals = status.get("approvals")
    if not isinstance(approvals, list):
        raise WorkflowError("migration-status.json approvals must be a list")
    for role in milestone.get("required_approvals", []):
        matches = [item for item in approvals if isinstance(item, dict)
                   and item.get("milestone") == milestone_id and item.get("role") == role
                   and item.get("status") == "approved"]
        if not matches:
            raise WorkflowError(f"cannot seal {milestone_id}; approval is missing: {role}")
        approval = matches[-1]
        evidence_path = project_evidence_paths(project_root, [str(approval.get("evidence"))])[0]
        approval["evidence"] = evidence_path
        approval["evidence_sha256"] = file_sha256(project_root.resolve() / evidence_path)
    history = status.setdefault("content_seal_history", [])
    if not isinstance(history, list):
        raise WorkflowError("migration-status.json content_seal_history must be a list")
    history.append({
        "milestone": milestone_id,
        "reviewer": reviewer,
        "review_evidence": review_path,
        "review_evidence_sha256": file_sha256(project_root.resolve() / review_path),
        "sealed_at": now_iso(),
    })
    status["updated_at"] = now_iso()
    atomic_write_json(mig / "migration-status.json", status)
    print(f"[sealed] {milestone_id} accepted content by {reviewer}")


def change_open(
    project_root: Path, milestone_id: str, changed_file: str | list[str], reason: str
) -> None:
    mig, _, status = require_scenario(project_root)
    require_no_active_change(status, "change-open")
    require_no_blockers(status, "change-open")
    definition = load_definition(mig)
    milestones = milestone_map(definition)
    milestone = milestones.get(milestone_id)
    if milestone is None:
        raise WorkflowError(f"unknown milestone: {milestone_id}")
    if not reason.strip():
        raise WorkflowError("--reason must describe why accepted content is changing")

    changed_values = changed_file if isinstance(changed_file, list) else [changed_file]
    changed_paths = unique_paths([
        project_relative_path(project_root, value) for value in changed_values
    ])
    if not changed_paths:
        raise WorkflowError("at least one --changed-file is required")
    changed_path = changed_paths[0]
    records = artifact_records(status)
    required_ids = {str(item["id"]) for item in milestone.get("required_artifacts", [])}
    affected_artifacts: list[str] = []
    previous_acceptances: dict[str, Any] = {}
    for artifact_id in required_ids:
        record = records.get(artifact_id)
        if not record or record.get("status") != "accepted":
            continue
        sealed = record.get("content_hashes")
        if isinstance(sealed, dict) and any(path in sealed for path in changed_paths):
            affected_artifacts.append(artifact_id)
            previous_acceptances[artifact_id] = copy.deepcopy(record)

    approvals = status.get("approvals")
    if not isinstance(approvals, list):
        raise WorkflowError("migration-status.json approvals must be a list")
    affected_approval_roles = sorted({
        str(item.get("role"))
        for item in approvals
        if isinstance(item, dict)
        and item.get("milestone") == milestone_id
        and item.get("status") == "approved"
        and item.get("evidence") in changed_paths
    })
    if not affected_artifacts and not affected_approval_roles:
        raise WorkflowError(
            f"none of the changed files are sealed by an accepted artifact or approval in "
            f"{milestone_id}: {', '.join(changed_paths)}"
        )

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    change_id = f"COR-{milestone_id}-{stamp}"
    owner = str((status.get("current") or {}).get("owner") or "UNASSIGNED")
    change_path = mig / "changes" / f"{change_id}.md"
    change_path.parent.mkdir(parents=True, exist_ok=True)
    prior_gate_ref = None
    supersessions = status.get("gate_supersessions")
    if isinstance(supersessions, list):
        replacements = [
            item.get("replacement_gate_ref")
            for item in supersessions
            if isinstance(item, dict)
            and item.get("milestone") == milestone_id
            and item.get("status") == "replaced"
            and item.get("replacement_gate_ref")
        ]
        if replacements:
            prior_gate_ref = str(replacements[-1])
    last = status.get("last_passed_milestone")
    if prior_gate_ref is None and isinstance(last, dict) and last.get("id") == milestone_id:
        candidate = last.get("gate_result_ref")
        if candidate and (project_root.resolve() / str(candidate)).is_file():
            prior_gate_ref = str(candidate)
    if prior_gate_ref is None:
        prior_gate = mig / "gates" / f"{milestone_id}-result.json"
        if prior_gate.is_file():
            prior_gate_ref = prior_gate.relative_to(project_root.resolve()).as_posix()
    lines = [
        f"# Accepted Change {change_id}",
        "",
        f"- Milestone: {milestone_id}",
        f"- Changed files: {', '.join(f'`{path}`' for path in changed_paths)}",
        f"- Reason: {reason.strip().replace(chr(10), ' ')}",
        f"- Owner: {owner}",
        f"- Opened at: {now_iso()}",
        f"- Affected artifacts: {', '.join(sorted(affected_artifacts)) or 'none'}",
        f"- Affected approval evidence: {', '.join(affected_approval_roles) or 'none'}",
        f"- Superseded Gate: `{prior_gate_ref}`" if prior_gate_ref else "- Superseded Gate: none (Gate had not passed)",
        "",
        "## Required sequence",
        "",
        "1. Correct the file without changing the normal migration position.",
        "2. Run the required regression/retest and record its evidence.",
        "3. Reaccept the affected artifact set.",
        "4. Obtain every required milestone approval again.",
        "5. Close this change only after the replacement Gate passes.",
        "",
    ]
    change_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    change_ref = change_path.relative_to(project_root.resolve()).as_posix()

    for artifact_id in affected_artifacts:
        record = records[artifact_id]
        record["status"] = "change-open"
        record["active_change_id"] = change_id

    previous_approvals: list[dict[str, Any]] = []
    superseded_at = now_iso()
    for approval in approvals:
        if not isinstance(approval, dict):
            continue
        if approval.get("milestone") == milestone_id and approval.get("status") == "approved":
            previous_approvals.append(copy.deepcopy(approval))
            approval["status"] = "superseded"
            approval["superseded_by"] = change_id
            approval["superseded_at"] = superseded_at

    change = {
        "id": change_id,
        "state": "opened",
        "milestone": milestone_id,
        "changed_file": changed_path,
        "changed_files": changed_paths,
        "reason": reason.strip(),
        "owner": owner,
        "opened_at": superseded_at,
        "change_record": change_ref,
        "change_record_sha256": file_sha256(change_path),
        "affected_artifacts": sorted(affected_artifacts),
        "affected_approval_evidence_roles": affected_approval_roles,
        "previous_acceptances": previous_acceptances,
        "previous_approvals": previous_approvals,
        "superseded_gate_ref": prior_gate_ref,
        "resume_current": copy.deepcopy(status.get("current")),
        "resume_next": copy.deepcopy(status.get("next")),
    }
    status["active_accepted_change"] = change
    if prior_gate_ref:
        supersessions = status.setdefault("gate_supersessions", [])
        if not isinstance(supersessions, list):
            raise WorkflowError("migration-status.json gate_supersessions must be a list")
        supersessions.append({
            "milestone": milestone_id,
            "change_id": change_id,
            "superseded_gate_ref": prior_gate_ref,
            "replacement_gate_ref": None,
            "status": "open",
            "opened_at": superseded_at,
        })
    status["schema"] = "bomdd-legacy-wpf-status/1.1"
    status["updated_at"] = now_iso()
    atomic_write_json(mig / "migration-status.json", status)
    print(f"[opened] {change_id} - {', '.join(changed_paths)}")
    print(f"[paused] normal position remains {(status.get('current') or {}).get('step')}")
    print("[next] correct the file, run the required retest, then run change-retest --evidence <RETEST_EVIDENCE>")


def change_retest(project_root: Path, evidence: list[str]) -> None:
    mig, _, status = require_scenario(project_root)
    require_no_blockers(status, "change-retest")
    change = active_change(status)
    if change is None:
        raise WorkflowError("no accepted change is active; run change-open first")
    if change.get("state") != "opened":
        raise WorkflowError(f"{change['id']} state is {change.get('state')}; run next")
    sealed_paths_are_current(
        project_root,
        {str(change["change_record"]): str(change["change_record_sha256"])},
        "accepted change record",
    )
    normalized = project_evidence_paths(project_root, evidence)
    change["retest_evidence"] = normalized
    change["retest_evidence_hashes"] = content_hashes(project_root, normalized)
    change["retested_at"] = now_iso()
    change["state"] = "retested"
    status["updated_at"] = now_iso()
    atomic_write_json(mig / "migration-status.json", status)
    print(f"[retested] {change['id']}")
    print("[next] run change-accept --reviewer <NAME> --evidence <REACCEPTANCE_REVIEW>")


def change_accept(project_root: Path, reviewer: str, evidence: list[str]) -> None:
    mig, _, status = require_scenario(project_root)
    require_no_blockers(status, "change-accept")
    change = active_change(status)
    if change is None:
        raise WorkflowError("no accepted change is active; run change-open first")
    if change.get("state") != "retested":
        raise WorkflowError(f"{change['id']} state is {change.get('state')}; run next")
    if not reviewer.strip() or reviewer == "UNASSIGNED":
        raise WorkflowError("--reviewer must name the person/team performing reacceptance")
    sealed_paths_are_current(
        project_root,
        {str(change["change_record"]): str(change["change_record_sha256"])},
        "accepted change record",
    )
    sealed_paths_are_current(
        project_root, change.get("retest_evidence_hashes"), "retest evidence"
    )
    review_paths = project_evidence_paths(project_root, evidence)
    records = artifact_records(status)
    definition = load_definition(mig)
    milestone = milestone_map(definition).get(str(change.get("milestone")))
    if milestone is None:
        raise WorkflowError(f"unknown change milestone: {change.get('milestone')}")
    required_specs = {
        str(item["id"]): item for item in milestone.get("required_artifacts", [])
    }
    for artifact_id in change.get("affected_artifacts", []):
        record = records.get(str(artifact_id))
        if record is None or record.get("active_change_id") != change["id"]:
            raise WorkflowError(f"affected artifact state is invalid: {artifact_id}; use EX-STATE-001")
        artifact_path = project_root.resolve() / str(record.get("path"))
        if not artifact_path.is_file():
            raise WorkflowError(f"artifact file not found: {artifact_path}")
        history = record.setdefault("acceptance_history", [])
        if not isinstance(history, list):
            raise WorkflowError(f"artifact acceptance_history must be a list: {artifact_id}")
        history.append({
            "superseded_by": change["id"],
            "superseded_at": change["opened_at"],
            "acceptance": copy.deepcopy(change["previous_acceptances"][artifact_id]),
        })
        prior_evidence = [str(path) for path in record.get("evidence", [])]
        all_evidence = unique_paths([
            *prior_evidence,
            str(change["change_record"]),
            *[str(path) for path in change.get("retest_evidence", [])],
            *review_paths,
        ])
        required_spec = required_specs.get(str(artifact_id))
        if required_spec is None:
            raise WorkflowError(f"affected artifact is no longer required: {artifact_id}")
        semantic_problems = artifact_semantic_problems(
            project_root, required_spec, all_evidence
        )
        if semantic_problems:
            raise WorkflowError(
                f"cannot reaccept {artifact_id}; semantic evidence validation failed: "
                f"{semantic_problems[0]}"
            )
        record["status"] = "accepted"
        record["evidence"] = all_evidence
        record["content_hashes"] = content_hashes(
            project_root, [str(record.get("path")), *all_evidence]
        )
        record["accepted_at"] = now_iso()
        record["accepted_by"] = reviewer
        record["accepted_change_id"] = change["id"]
        record.pop("active_change_id", None)
    change["reacceptance_reviewer"] = reviewer
    change["reacceptance_evidence"] = review_paths
    change["reacceptance_evidence_hashes"] = content_hashes(project_root, review_paths)
    change["reaccepted_at"] = now_iso()
    change["state"] = "reaccepted"
    status["updated_at"] = now_iso()
    atomic_write_json(mig / "migration-status.json", status)
    print(f"[reaccepted] {change['id']} by {reviewer}")
    print("[next] run next to see the first required reapproval command")


def change_approve(
    project_root: Path, role: str, approver: str, evidence: str
) -> None:
    mig, _, status = require_scenario(project_root)
    require_no_blockers(status, "change-approve")
    change = active_change(status)
    if change is None:
        raise WorkflowError("no accepted change is active; run change-open first")
    if change.get("state") not in {"reaccepted", "approving"}:
        raise WorkflowError(f"{change['id']} state is {change.get('state')}; run next")
    definition = load_definition(mig)
    milestone = milestone_map(definition).get(str(change.get("milestone")))
    if milestone is None:
        raise WorkflowError(f"unknown change milestone: {change.get('milestone')}")
    required_roles = [str(item) for item in milestone.get("required_approvals", [])]
    if role not in required_roles:
        raise WorkflowError(f"role {role!r} is not a required approver for {change['milestone']}")
    if not approver.strip() or approver == "UNASSIGNED":
        raise WorkflowError("--approver must name the assigned person/team")
    sealed_paths_are_current(
        project_root, change.get("reacceptance_evidence_hashes"), "reacceptance evidence"
    )
    evidence_path = project_evidence_paths(project_root, [evidence])[0]
    approvals = status.setdefault("approvals", [])
    if not isinstance(approvals, list):
        raise WorkflowError("migration-status.json approvals must be a list")
    approvals[:] = [item for item in approvals if not (
        isinstance(item, dict)
        and item.get("milestone") == change["milestone"]
        and item.get("role") == role
        and item.get("change_id") == change["id"]
    )]
    approvals.append({
        "milestone": change["milestone"],
        "role": role,
        "status": "approved",
        "approver": approver,
        "evidence": evidence_path,
        "evidence_sha256": file_sha256(project_root.resolve() / evidence_path),
        "approved_at": now_iso(),
        "change_id": change["id"],
    })
    completed_roles = {
        str(item.get("role"))
        for item in approvals
        if isinstance(item, dict)
        and item.get("milestone") == change["milestone"]
        and item.get("status") == "approved"
        and item.get("change_id") == change["id"]
    }
    change["state"] = "approved" if set(required_roles) <= completed_roles else "approving"
    status["updated_at"] = now_iso()
    atomic_write_json(mig / "migration-status.json", status)
    print(f"[reapproved] {change['milestone']} by {role}: {approver}")
    if change["state"] == "approved":
        print("[next] run change-close to execute and record the replacement Gate")
    else:
        missing = [item for item in required_roles if item not in completed_roles]
        print(f"[next] run change-approve for required role: {missing[0]}")


def change_close(project_root: Path) -> None:
    mig, _, status = require_scenario(project_root)
    require_no_blockers(status, "change-close")
    change = active_change(status)
    if change is None:
        raise WorkflowError("no accepted change is active; run change-open first")
    if change.get("state") != "approved":
        raise WorkflowError(f"{change['id']} state is {change.get('state')}; run next")
    result = check_gate(project_root, str(change["milestone"]))
    result["schema"] = "bomdd-legacy-wpf-gate-result/1.2"
    result["accepted_change_id"] = change["id"]
    result["supersedes"] = change.get("superseded_gate_ref")
    gate_path = mig / "gates" / f"{change['milestone']}-recheck-{change['id']}.json"
    atomic_write_json(gate_path, result)
    print_gate(result)
    if result["gate"]["result"] != "pass":
        raise WorkflowError(f"replacement Gate failed. Result saved to {gate_path}; run next")

    gate_ref = gate_path.relative_to(project_root.resolve()).as_posix()
    closed_at = now_iso()
    for item in status.get("gate_supersessions", []):
        if isinstance(item, dict) and item.get("change_id") == change["id"]:
            item["replacement_gate_ref"] = gate_ref
            item["status"] = "replaced"
            item["closed_at"] = closed_at
    change["state"] = "closed"
    change["closed_at"] = closed_at
    change["replacement_gate_ref"] = gate_ref
    history = status.setdefault("accepted_change_history", [])
    if not isinstance(history, list):
        raise WorkflowError("migration-status.json accepted_change_history must be a list")
    history.append(copy.deepcopy(change))
    last = status.get("last_passed_milestone")
    if isinstance(last, dict) and last.get("id") == change["milestone"]:
        last["gate_result_ref"] = gate_ref
        last["revalidated_at"] = closed_at
        last["accepted_change_id"] = change["id"]
    status.pop("active_accepted_change", None)
    status["updated_at"] = closed_at
    atomic_write_json(mig / "migration-status.json", status)
    print(f"[closed] {change['id']} - replacement Gate recorded")
    current = status.get("current") or {}
    print(f"[resume] {current.get('step')} - {current.get('action')}")


def show_decision_status(project_root: Path) -> None:
    mig, _, status = require_scenario(project_root)
    definition = load_definition(mig)
    sets = decision_set_map(definition)
    current_id = str((status.get("current") or {}).get("milestone"))
    records = artifact_records(status)
    for spec in sets.values():
        artifact = records.get(str(spec.get("artifact_id")), {})
        due_mark = "CURRENT" if spec.get("due_milestone") == current_id else "scheduled"
        print(
            f"{spec['id']} due={spec.get('due_milestone')} [{due_mark}] "
            f"artifact={artifact.get('status', 'unregistered')}"
        )
        path = project_root.resolve() / str(spec.get("path"))
        if not path.is_file():
            print(f"  [MISSING] {spec.get('path')}")
            continue
        document = read_json(path)
        values = document.get("decisions") if isinstance(document.get("decisions"), list) else []
        mapped = {str(item.get("id")): item for item in values if isinstance(item, dict)}
        for expected in spec.get("decisions", []):
            item = mapped.get(str(expected.get("id")), {})
            print(
                f"  - {expected.get('id')} [{item.get('decision_status', 'missing')}] "
                f"owner={expected.get('owner')} decider={item.get('decider', 'UNASSIGNED')}"
            )


def decision_record(
    project_root: Path,
    decision_set_id: str,
    decision_id: str,
    decider: str,
    decision_status: str,
    value: str,
    evidence: str,
) -> None:
    mig, profile, status = require_scenario(project_root)
    require_no_active_change(status, "decision-record")
    require_no_blockers(status, "decision-record")
    definition = load_definition(mig)
    spec = decision_set_map(definition).get(decision_set_id)
    if spec is None:
        raise WorkflowError(f"unknown decision set: {decision_set_id}")
    current_id = str((status.get("current") or {}).get("milestone"))
    if spec.get("due_milestone") != current_id:
        raise WorkflowError(
            f"{decision_set_id} is due at {spec.get('due_milestone')}, not {current_id}; "
            "do not decide it early or late"
        )
    expected = {
        str(item["id"]): item for item in spec.get("decisions", [])
    }.get(decision_id)
    if expected is None:
        raise WorkflowError(f"{decision_id} does not belong to {decision_set_id}")
    if decision_status not in {"decided", "not-applicable"}:
        raise WorkflowError("--status must be decided or not-applicable")
    if not value.strip() or value.strip() == "UNDECIDED":
        raise WorkflowError("--value must contain the decision or a not-applicable reason")
    owner_role = str(expected.get("owner"))
    owners = profile.get("owners") if isinstance(profile.get("owners"), dict) else {}
    assigned = str(owners.get(owner_role) or "UNASSIGNED")
    if assigned == "UNASSIGNED":
        raise WorkflowError(f"{owner_role} is UNASSIGNED; assign the role before deciding {decision_id}")
    if decider.strip() != assigned:
        raise WorkflowError(
            f"--decider must match the assigned {owner_role}: {assigned}"
        )
    evidence_path = project_evidence_paths(project_root, [evidence])[0]
    artifact = artifact_records(status).get(str(spec.get("artifact_id")))
    if artifact is None:
        raise WorkflowError(
            f"decision artifact is unregistered; run adopt-decision-layout for an upgraded project"
        )
    if artifact.get("status") == "accepted":
        raise WorkflowError(
            f"{spec.get('artifact_id')} is already accepted; use the accepted change workflow"
        )
    path = project_root.resolve() / str(spec.get("path"))
    document = read_json(path)
    values = document.get("decisions")
    if not isinstance(values, list):
        raise WorkflowError("decision document decisions must be a list")
    matches = [item for item in values if isinstance(item, dict) and item.get("id") == decision_id]
    if len(matches) != 1:
        raise WorkflowError(f"decision document must contain exactly one {decision_id} record")
    record = matches[0]
    history = document.setdefault("decision_history", [])
    if not isinstance(history, list):
        raise WorkflowError("decision_history must be a list")
    if record.get("decision_status") in {"decided", "not-applicable"}:
        history.append({
            "decision_id": decision_id,
            "replaced_at": now_iso(),
            "previous": copy.deepcopy(record),
        })
    decided_at = now_iso()
    record.update({
        "topic": expected.get("topic"),
        "owner": owner_role,
        "decision_status": decision_status,
        "value": value.strip(),
        "decider": assigned,
        "evidence": evidence_path,
        "evidence_sha256": file_sha256(project_root.resolve() / evidence_path),
        "decided_at": decided_at,
    })
    atomic_write_json(path, document)
    events = status_list(status, "decision_events")
    events.append({
        "decision_set": decision_set_id,
        "decision_id": decision_id,
        "status": decision_status,
        "decider": assigned,
        "evidence": evidence_path,
        "evidence_sha256": file_sha256(project_root.resolve() / evidence_path),
        "recorded_at": decided_at,
    })
    status["schema"] = "bomdd-legacy-wpf-status/1.3"
    status["updated_at"] = decided_at
    atomic_write_json(mig / "migration-status.json", status)
    print(f"[decided] {decision_id} [{decision_status}] by {assigned}")
    print("[next] run next to obtain the next due decision or artifact acceptance action")


def adopt_decision_layout(
    project_root: Path, reviewer: str, review_evidence: str
) -> None:
    mig, profile, status = require_scenario(project_root)
    require_no_active_change(status, "adopt-decision-layout")
    require_no_blockers(status, "adopt-decision-layout")
    if not reviewer.strip() or reviewer == "UNASSIGNED":
        raise WorkflowError("--reviewer must name the person/team adopting the new decision layout")
    evidence_path = project_evidence_paths(project_root, [review_evidence])[0]
    upgrades = status_list(status, "scenario_upgrade_history")
    if any(isinstance(item, dict) and item.get("id") == "decision-layout/1.0" for item in upgrades):
        raise WorkflowError("decision-layout/1.0 was already adopted")
    definition = load_definition(mig)
    sets = decision_set_map(definition)
    legacy_values = profile.get("decisions")
    legacy_items = legacy_values if isinstance(legacy_values, list) else []
    legacy_map = {
        str(item.get("id")): item for item in legacy_items
        if isinstance(item, dict) and item.get("id")
    }
    owners = profile.get("owners") if isinstance(profile.get("owners"), dict) else {}
    imported: list[str] = []
    reaffirm: list[str] = []
    artifact_list = status_list(status, "artifacts")
    registered = artifact_records(status)
    adopted_at = now_iso()
    existing_targets = [
        project_root.resolve() / str(spec.get("path"))
        for spec in sets.values()
        if (project_root.resolve() / str(spec.get("path"))).exists()
    ]
    if existing_targets:
        raise WorkflowError(
            f"decision layout target already exists; no files changed: {existing_targets[0]}"
        )
    for spec in sets.values():
        path = project_root.resolve() / str(spec.get("path"))
        decisions: list[dict[str, Any]] = []
        for expected in spec.get("decisions", []):
            decision_id = str(expected.get("id"))
            legacy = legacy_map.get(decision_id, {})
            legacy_evidence = str(legacy.get("evidence") or "")
            actual_evidence = (project_root.resolve() / legacy_evidence).resolve() if legacy_evidence else None
            assigned = str(owners.get(str(expected.get("owner"))) or "UNASSIGNED")
            can_import = (
                legacy.get("decision_status") in {"decided", "not-applicable"}
                and str(legacy.get("value") or "").strip() not in {"", "UNDECIDED"}
                and actual_evidence is not None
                and actual_evidence.is_file()
                and assigned != "UNASSIGNED"
            )
            if can_import:
                evidence_ref = actual_evidence.relative_to(project_root.resolve()).as_posix()
                decisions.append({
                    "id": decision_id,
                    "topic": expected.get("topic"),
                    "owner": expected.get("owner"),
                    "decision_status": legacy.get("decision_status"),
                    "value": legacy.get("value"),
                    "decider": assigned,
                    "evidence": evidence_ref,
                    "evidence_sha256": file_sha256(actual_evidence),
                    "decided_at": adopted_at,
                    "imported_from": "migration-profile.json",
                })
                imported.append(decision_id)
            else:
                decisions.append({
                    "id": decision_id,
                    "topic": expected.get("topic"),
                    "owner": expected.get("owner"),
                    "decision_status": "open",
                    "value": "UNDECIDED",
                    "decider": "UNASSIGNED",
                    "evidence": "",
                    "evidence_sha256": "",
                    "decided_at": "",
                    "legacy_value": legacy.get("value"),
                    "legacy_evidence": legacy.get("evidence"),
                    "legacy_status": legacy.get("decision_status"),
                })
                reaffirm.append(decision_id)
        document = {
            "schema": "bomdd-legacy-wpf-technical-decisions/1.0",
            "decision_set": spec.get("id"),
            "due_milestone": spec.get("due_milestone"),
            "decisions": decisions,
            "decision_history": [],
            "layout_adoption": {
                "reviewer": reviewer,
                "review_evidence": evidence_path,
                "review_evidence_sha256": file_sha256(project_root.resolve() / evidence_path),
                "adopted_at": adopted_at,
            },
        }
        atomic_write_json(path, document)
        artifact_id = str(spec.get("artifact_id"))
        if artifact_id not in registered:
            artifact_list.append({
                "id": artifact_id,
                "path": spec.get("path"),
                "status": "present",
                "evidence": [],
            })
    upgrades.append({
        "id": "decision-layout/1.0",
        "reviewer": reviewer,
        "review_evidence": evidence_path,
        "review_evidence_sha256": file_sha256(project_root.resolve() / evidence_path),
        "imported_decisions": imported,
        "requires_reaffirmation": reaffirm,
        "adopted_at": adopted_at,
    })
    status["schema"] = "bomdd-legacy-wpf-status/1.3"
    status["updated_at"] = adopted_at
    atomic_write_json(mig / "migration-status.json", status)
    print(f"[adopted] decision-layout/1.0 by {reviewer}")
    print(f"[imported] {', '.join(imported) or 'none'}")
    print(f"[reaffirm at due milestone] {', '.join(reaffirm) or 'none'}")
    print("[next] run decision-status; the normal milestone/STEP was not changed")


def show_exception_catalog(project_root: Path, query: str | None) -> None:
    mig, _, _ = require_scenario(project_root)
    entries = exception_catalog_entries(mig)
    needle = (query or "").casefold()
    matches = [
        item for item in entries.values()
        if not needle or needle in " ".join(item.values()).casefold()
    ]
    if not matches:
        raise WorkflowError(f"no exception catalog entry matched: {query}")
    for item in matches:
        effective, note = effective_exception_classification(item["catalog_classification"])
        suffix = f"; {note}" if note else ""
        print(f"{item['id']} [{effective}] {item['symptom']}")
        print(f"  action: {item['default_action']}")
        print(f"  resume: {item['resume']}{suffix}")


def exception_open(
    project_root: Path,
    catalog_id: str,
    symptom: str,
    evidence: list[str],
    production_db: str,
    baseline_fixture: str,
    current_source: str,
) -> None:
    mig, profile, status = require_scenario(project_root)
    entries = exception_catalog_entries(mig)
    catalog = entries.get(catalog_id)
    if catalog is None:
        raise WorkflowError(
            f"unknown exception catalog ID: {catalog_id}; run exception-catalog --query <WORD>"
        )
    if not symptom.strip():
        raise WorkflowError("--symptom must state observed facts without an unverified cause")
    boundaries = {
        "production_db": production_db,
        "baseline_fixture": baseline_fixture,
        "current_source": current_source,
    }
    allowed_boundaries = {"unchanged", "changed", "unknown"}
    invalid = [f"{key}={value}" for key, value in boundaries.items() if value not in allowed_boundaries]
    if invalid:
        raise WorkflowError(f"invalid unchanged-boundary value: {', '.join(invalid)}")
    normalized = project_evidence_paths(project_root, evidence)
    classification, classification_note = effective_exception_classification(
        catalog["catalog_classification"]
    )
    unsafe_boundaries = [key for key, value in boundaries.items() if value != "unchanged"]
    if unsafe_boundaries and classification != "blocker":
        classification = "blocker"
        classification_note = (
            "boundary is changed or unknown; classification escalated to blocker: "
            + ", ".join(unsafe_boundaries)
        )
    current = status.get("current") or {}
    catalog_resume = catalog["resume"]
    if catalog_resume == "現在 STEP":
        catalog_resume = str(current.get("step"))
    resume_position = str(current.get("step"))
    owner_role = exception_owner_role(catalog_id)
    owners = profile.get("owners") if isinstance(profile.get("owners"), dict) else {}
    owner = str(owners.get(owner_role) or "UNASSIGNED")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    occurrence_id = f"{catalog_id}-{stamp}"
    record_path = mig / "exceptions" / f"{occurrence_id}-open.md"
    occurred_at = now_iso()
    lines = [
        f"# {occurrence_id} - Open",
        "",
        f"- Catalog ID: {catalog_id}",
        f"- Occurred at milestone: {current.get('milestone')}",
        f"- Occurred at STEP: {current.get('step')}",
        f"- Classification: {classification}",
        f"- Catalog classification: {catalog['catalog_classification']}",
        f"- Owner role: {owner_role}",
        f"- Owner: {owner}",
        f"- Status: open",
        f"- Occurred at: {occurred_at}",
        "",
        "## Symptom",
        "",
        symptom.strip(),
        "",
        "## Evidence",
        "",
        *[f"- `{path}`" for path in normalized],
        "",
        "## Unchanged boundaries",
        "",
        f"- Production DB: {production_db}",
        f"- Baseline fixture: {baseline_fixture}",
        f"- Current-system source: {current_source}",
        "",
        "## Catalog default action",
        "",
        catalog["default_action"],
        "",
        "## Resume",
        "",
        f"- Preserved normal position: {resume_position}",
        f"- Catalog follow-up target: {catalog_resume}",
        "- Alternate safe work: none until explicitly authorized",
        "",
    ]
    if classification_note:
        lines.extend(["## Automatic safety decision", "", classification_note, ""])
    record_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    record_ref = record_path.relative_to(project_root.resolve()).as_posix()
    exception = {
        "occurrence_id": occurrence_id,
        "catalog_id": catalog_id,
        "status": "open",
        "classification": classification,
        "catalog_classification": catalog["catalog_classification"],
        "classification_note": classification_note,
        "symptom": symptom.strip(),
        "default_action": catalog["default_action"],
        "resume_position": resume_position,
        "catalog_resume": catalog_resume,
        "owner_role": owner_role,
        "owner": owner,
        "occurred_at": occurred_at,
        "occurred_position": copy.deepcopy(current),
        "evidence": normalized,
        "evidence_hashes": content_hashes(project_root, normalized),
        "unchanged_boundaries": boundaries,
        "open_record": record_ref,
        "open_record_sha256": file_sha256(record_path),
        "safe_work": [],
    }
    records = status_list(status, "exceptions")
    records.append(exception)
    if classification == "blocker":
        status_list(status, "blockers").append(occurrence_id)
    elif classification == "non-blocker":
        status_list(status, "non_blockers").append(occurrence_id)
    else:
        status_list(status, "defects").append(occurrence_id)
    status["schema"] = "bomdd-legacy-wpf-status/1.2"
    status["updated_at"] = now_iso()
    atomic_write_json(mig / "migration-status.json", status)
    color = "RED" if classification == "blocker" else "YELLOW"
    print(f"[{color}] opened {occurrence_id} [{classification}]")
    print(f"[owner] {owner_role}: {owner}")
    print(f"[DO] {catalog['default_action']}")
    print("[next] run next; do not edit migration-status.json by hand")


def exception_safe_work(
    project_root: Path,
    occurrence_id: str,
    work: str,
    authorizer: str,
    evidence: str,
) -> None:
    mig, _, status = require_scenario(project_root)
    exception = find_open_exception(status, occurrence_id)
    if exception.get("classification") != "blocker":
        raise WorkflowError("alternate safe work is only needed for an active blocker")
    if not work.strip():
        raise WorkflowError("--work must name one bounded safe action")
    if not authorizer.strip() or authorizer == "UNASSIGNED":
        raise WorkflowError("--authorizer must name the responsible person/team")
    evidence_path = project_evidence_paths(project_root, [evidence])[0]
    sequence = len(exception.get("safe_work", [])) + 1
    event_path = mig / "exceptions" / f"{occurrence_id}-safe-work-{sequence:02d}.md"
    authorized_at = now_iso()
    event_path.write_text(
        "\n".join([
            f"# {occurrence_id} - Alternate Safe Work {sequence:02d}",
            "",
            f"- Work: {work.strip()}",
            f"- Authorizer: {authorizer}",
            f"- Authorized at: {authorized_at}",
            f"- Evidence: `{evidence_path}`",
            "",
        ]),
        encoding="utf-8",
        newline="\n",
    )
    event_ref = event_path.relative_to(project_root.resolve()).as_posix()
    safe_work = exception.setdefault("safe_work", [])
    if not isinstance(safe_work, list):
        raise WorkflowError("exception safe_work must be a list")
    safe_work.append({
        "work": work.strip(),
        "authorizer": authorizer,
        "authorized_at": authorized_at,
        "evidence": evidence_path,
        "evidence_sha256": file_sha256(project_root.resolve() / evidence_path),
        "event_record": event_ref,
        "event_record_sha256": file_sha256(event_path),
    })
    status_list(status, "alternate_safe_work").append(f"{occurrence_id}: {work.strip()}")
    status["updated_at"] = now_iso()
    atomic_write_json(mig / "migration-status.json", status)
    print(f"[authorized] {occurrence_id} alternate safe work: {work.strip()}")
    print("[next] run next; the blocker remains open")


def exception_resolve(
    project_root: Path,
    occurrence_id: str,
    resolver: str,
    resolution: str,
    evidence: list[str],
) -> None:
    mig, _, status = require_scenario(project_root)
    exception = find_open_exception(status, occurrence_id)
    if not resolver.strip() or resolver == "UNASSIGNED":
        raise WorkflowError("--resolver must name the responsible person/team")
    if not resolution.strip():
        raise WorkflowError("--resolution must state the applied decision or corrective result")
    sealed_paths_are_current(
        project_root,
        {str(exception["open_record"]): str(exception["open_record_sha256"])},
        "exception open record",
    )
    sealed_paths_are_current(project_root, exception.get("evidence_hashes"), "exception evidence")
    for item in exception.get("safe_work", []):
        if not isinstance(item, dict):
            raise WorkflowError("exception safe_work entry is invalid; use EX-STATE-001")
        sealed_paths_are_current(
            project_root,
            {str(item["event_record"]): str(item["event_record_sha256"])},
            "alternate safe work record",
        )
        sealed_paths_are_current(
            project_root,
            {str(item["evidence"]): str(item["evidence_sha256"])},
            "alternate safe work evidence",
        )
    normalized = project_evidence_paths(project_root, evidence)
    resolved_at = now_iso()
    event_path = mig / "exceptions" / f"{occurrence_id}-resolved.md"
    event_path.write_text(
        "\n".join([
            f"# {occurrence_id} - Resolved",
            "",
            f"- Catalog ID: {exception.get('catalog_id')}",
            f"- Classification: {exception.get('classification')}",
            f"- Resolver: {resolver}",
            f"- Resolved at: {resolved_at}",
            f"- Preserved normal position: {exception.get('resume_position')}",
            f"- Catalog follow-up target: {exception.get('catalog_resume')}",
            "",
            "## Resolution",
            "",
            resolution.strip(),
            "",
            "## Resolution evidence",
            "",
            *[f"- `{path}`" for path in normalized],
            "",
        ]),
        encoding="utf-8",
        newline="\n",
    )
    event_ref = event_path.relative_to(project_root.resolve()).as_posix()
    exception["status"] = "resolved"
    exception["resolver"] = resolver
    exception["resolution"] = resolution.strip()
    exception["resolution_evidence"] = normalized
    exception["resolution_evidence_hashes"] = content_hashes(project_root, normalized)
    exception["resolved_at"] = resolved_at
    exception["resolution_record"] = event_ref
    exception["resolution_record_sha256"] = file_sha256(event_path)
    for key in ("blockers", "non_blockers", "defects"):
        values = status_list(status, key)
        values[:] = [item for item in values if item != occurrence_id]
    safe = status_list(status, "alternate_safe_work")
    safe[:] = [item for item in safe if not str(item).startswith(f"{occurrence_id}:")]
    history = status_list(status, "exception_history")
    history.append({
        "occurrence_id": occurrence_id,
        "catalog_id": exception.get("catalog_id"),
        "classification": exception.get("classification"),
        "open_record": exception.get("open_record"),
        "resolution_record": event_ref,
        "resolved_at": resolved_at,
    })
    status["updated_at"] = resolved_at
    atomic_write_json(mig / "migration-status.json", status)
    print(f"[resolved] {occurrence_id} by {resolver}")
    print(f"[resume] preserved normal position: {exception.get('resume_position')}")
    if exception.get("catalog_resume") != exception.get("resume_position"):
        print(f"[follow-up] catalog target: {exception.get('catalog_resume')}")
    print("[next] run next to obtain the current executable action")


def check_gate(project_root: Path, milestone_id: str | None = None) -> dict[str, Any]:
    mig, _, status = require_scenario(project_root)
    definition = load_definition(mig)
    milestones = milestone_map(definition)
    current = status.get("current") or {}
    target_id = milestone_id or current.get("milestone")
    if target_id not in milestones:
        raise WorkflowError(f"unknown milestone: {target_id}")
    milestone = milestones[target_id]
    records = artifact_records(status)
    checks: list[dict[str, Any]] = []

    for required in milestone.get("required_artifacts", []):
        artifact_id = required["id"]
        path_text = required["path"]
        record = records.get(artifact_id)
        actual = project_root.resolve() / path_text
        problems = []
        if record is None:
            problems.append("artifact is not registered in migration-status.json")
        else:
            if record.get("path") != path_text:
                problems.append(f"registered path differs: {record.get('path')}")
            if record.get("status") != "accepted":
                problems.append(f"status is {record.get('status')!r}, expected 'accepted'")
            evidence = record.get("evidence")
            if not isinstance(evidence, list) or not evidence:
                problems.append("evidence list is empty")
            else:
                for evidence_path in evidence:
                    if not isinstance(evidence_path, str) or not (project_root.resolve() / evidence_path).is_file():
                        problems.append(f"evidence file not found: {evidence_path}")
            if record.get("status") == "accepted":
                evidence_paths = [str(item) for item in evidence] if isinstance(evidence, list) else []
                problems.extend(content_hash_problems(
                    project_root, [path_text, *evidence_paths], record.get("content_hashes")
                ))
                problems.extend(artifact_semantic_problems(
                    project_root, required, evidence_paths
                ))
        if not actual.is_file():
            problems.append(f"artifact file not found: {path_text}")
        checks.append({
            "id": f"ART:{artifact_id}",
            "description": path_text,
            "result": "pass" if not problems else "fail",
            "problems": problems,
        })

    approvals = status.get("approvals")
    if not isinstance(approvals, list):
        approvals = []
    for role in milestone.get("required_approvals", []):
        matches = [a for a in approvals if isinstance(a, dict) and a.get("milestone") == target_id
                   and a.get("role") == role and a.get("status") == "approved"]
        problems = []
        if not matches:
            problems.append("approval record not found")
        else:
            approval = matches[-1]
            if not approval.get("approver") or approval.get("approver") == "UNASSIGNED":
                problems.append("approver is missing")
            evidence = approval.get("evidence")
            if not evidence or not (project_root.resolve() / str(evidence)).is_file():
                problems.append(f"approval evidence not found: {evidence}")
            else:
                expected_hash = approval.get("evidence_sha256")
                if not isinstance(expected_hash, str) or not expected_hash:
                    problems.append("approval evidence content hash seal is missing")
                else:
                    actual_hash = file_sha256(project_root.resolve() / str(evidence))
                    if actual_hash.lower() != expected_hash.lower():
                        problems.append(
                            f"approval evidence content hash mismatch: {evidence}; "
                            f"accepted={expected_hash.lower()} current={actual_hash.lower()}"
                        )
        checks.append({
            "id": f"APPROVAL:{role}",
            "description": f"{target_id} approval by {role}",
            "result": "pass" if not problems else "fail",
            "problems": problems,
        })

    for decision_set_id in milestone.get("required_decision_sets", []):
        problems = decision_set_gate_problems(
            project_root, status, definition, str(decision_set_id)
        )
        checks.append({
            "id": f"DECISION-SET:{decision_set_id}",
            "description": f"{decision_set_id} is decided, evidenced, accepted and unchanged",
            "result": "pass" if not problems else "fail",
            "problems": problems,
        })

    exception_problems = exception_seal_problems(project_root, status)
    checks.append({
        "id": "EXCEPTION-SEALS",
        "description": "exception open/resolution records and evidence retain their recorded contents",
        "result": "pass" if not exception_problems else "fail",
        "problems": exception_problems,
    })

    blockers = status.get("blockers")
    active_blockers = blockers if isinstance(blockers, list) else ["invalid blockers field"]
    checks.append({
        "id": "ACTIVE-BLOCKERS",
        "description": "active blockers are zero",
        "result": "pass" if not active_blockers else "fail",
        "problems": [str(b) for b in active_blockers],
    })

    passed = all(c["result"] == "pass" for c in checks)
    change_candidates: list[str] = []
    mismatch_pattern = re.compile(r"(?:content hash mismatch|approval evidence content hash mismatch): ([^;]+);")
    for check in checks:
        if not str(check.get("id", "")).startswith(("ART:", "APPROVAL:")):
            continue
        for problem in check.get("problems", []):
            match = mismatch_pattern.search(str(problem))
            if match:
                change_candidates.append(match.group(1))
    change_candidates = unique_paths(change_candidates)
    change = active_change(status)
    resume_from = current.get("step")
    if change is not None and change.get("milestone") == target_id:
        resume_from = f"accepted change {change['id']} ({change.get('state')})"
    return {
        "schema": "bomdd-legacy-wpf-gate-result/1.2",
        "gate": {
            "id": target_id,
            "name": milestone["name"],
            "result": "pass" if passed else "fail",
            "checked_at": now_iso(),
        },
        "checks": checks,
        "decision": {
            "status": "advance" if passed else "stay",
            "remain_at": None if passed else target_id,
            "resume_from": resume_from if not passed else None,
            "change_candidates": change_candidates,
            "active_change_id": change.get("id") if change is not None else None,
        },
    }


def print_gate(result: dict[str, Any]) -> None:
    gate = result["gate"]
    print(f"{gate['id']} {gate['name']}: {gate['result'].upper()}")
    for check in result["checks"]:
        mark = "PASS" if check["result"] == "pass" else "FAIL"
        print(f"  [{mark}] {check['id']} - {check['description']}")
        for problem in check.get("problems", []):
            print(f"         {problem}")
    if gate["result"] != "pass":
        print(f"[stay] resume from {result['decision']['resume_from']}")
        candidates = result["decision"].get("change_candidates") or []
        if candidates and not result["decision"].get("active_change_id"):
            print("[next] open one accepted change for the first mismatched file:")
            print(
                "       python bomdd/migration/tools/migration-workflow.py change-open "
                f"--project-root <PROJECT_ROOT> --milestone {gate['id']} "
                f"--changed-file {candidates[0]} --reason \"<CHANGE_REASON>\""
            )


SLICE_STATES = [
    "planned", "ready", "claimed", "manufacturing", "self-accepted",
    "integrated", "compared", "accepted", "as-built",
]


def workstream_register(project_root: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    document = read_json(migration_root(project_root) / "workstream-register.json")
    streams = document.get("workstreams")
    if not isinstance(streams, list):
        raise WorkflowError("workstream-register.json workstreams must be a list")
    result = {
        str(item.get("id")): item for item in streams
        if isinstance(item, dict) and item.get("id")
    }
    if not result:
        raise WorkflowError("workstream register is empty; complete MIG-20")
    return document, result


def workstream_status_file(project_root: Path, workstream_id: str) -> Path:
    if not re.fullmatch(r"WS-[A-Z0-9-]+", workstream_id):
        raise WorkflowError(f"invalid workstream ID: {workstream_id}")
    return migration_root(project_root) / "workstreams" / workstream_id / "status.json"


def load_workstream_status(project_root: Path, workstream_id: str) -> tuple[Path, dict[str, Any]]:
    path = workstream_status_file(project_root, workstream_id)
    document = read_json(path)
    if document.get("workstream_id") != workstream_id:
        raise WorkflowError(f"workstream status ID mismatch: {path}")
    return path, document


def find_slice(document: dict[str, Any], slice_id: str) -> dict[str, Any]:
    slices = document.get("slices")
    if not isinstance(slices, list):
        raise WorkflowError("workstream status slices must be a list")
    matches = [item for item in slices if isinstance(item, dict) and item.get("id") == slice_id]
    if len(matches) != 1:
        raise WorkflowError(f"slice not found or duplicated: {slice_id}")
    return matches[0]


def append_slice_evidence(
    project_root: Path, item: dict[str, Any], evidence: list[str], event: str, actor: str
) -> list[str]:
    normalized = project_evidence_paths(project_root, evidence)
    values = item.setdefault("evidence", [])
    seals = item.setdefault("evidence_hashes", {})
    history = item.setdefault("history", [])
    if not isinstance(values, list) or not isinstance(seals, dict) or not isinstance(history, list):
        raise WorkflowError("slice evidence/history structure is invalid; use EX-STATE-001")
    for path_text in normalized:
        if path_text not in values:
            values.append(path_text)
        seals[path_text] = file_sha256(project_root.resolve() / path_text)
    history.append({"event": event, "actor": actor, "at": now_iso(), "evidence": normalized})
    item["updated_at"] = now_iso()
    return normalized


def workstream_status_problems(project_root: Path, document: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    if document.get("schema") != "bomdd-javafx-wpf-workstream-status/2.0":
        problems.append("unexpected workstream status schema")
    register_path = migration_root(project_root) / "workstream-register.json"
    if str(document.get("register_sha256") or "").lower() != file_sha256(register_path).lower():
        problems.append("workstream register changed after workstream-init; re-plan through accepted change")
    slices = document.get("slices")
    if not isinstance(slices, list) or not slices:
        return [*problems, "workstream has no slices"]
    ids = [str(item.get("id")) for item in slices if isinstance(item, dict)]
    if len(ids) != len(set(ids)):
        problems.append("slice IDs are duplicated")
    for item in slices:
        if not isinstance(item, dict):
            problems.append("slice status entry is invalid")
            continue
        sid = item.get("id")
        if item.get("state") not in SLICE_STATES:
            problems.append(f"{sid} state is invalid: {item.get('state')}")
        for problem in sealed_mapping_problems(project_root, item.get("evidence_hashes")) if item.get("evidence") else []:
            problems.append(f"{sid}: {problem}")
        evidence = item.get("evidence") if isinstance(item.get("evidence"), list) else []
        seals = item.get("evidence_hashes") if isinstance(item.get("evidence_hashes"), dict) else {}
        if set(str(value) for value in evidence) != set(str(value) for value in seals):
            problems.append(f"{sid} evidence and evidence_hashes differ")
        if item.get("state") not in {"planned", "ready"} and placeholder(item.get("claimed_by")):
            problems.append(f"{sid} has no claimant")
        if item.get("state") in {"integrated", "compared", "accepted", "as-built"} and placeholder(item.get("reviewer")):
            problems.append(f"{sid} has no independent reviewer")
    return problems


def workstream_init(project_root: Path) -> None:
    mig, _, status = require_scenario(project_root)
    require_no_active_change(status, "workstream-init")
    require_no_blockers(status, "workstream-init")
    definition = load_definition(mig)
    order = [str(item.get("id")) for item in definition.get("milestones", [])]
    current_id = str((status.get("current") or {}).get("milestone"))
    if current_id not in order or order.index(current_id) < order.index("MIG-50"):
        raise WorkflowError("workstream-init is available from MIG-50 after the register is accepted")
    record = artifact_records(status).get("ART-WORKSTREAM-REGISTER")
    if record is None or record.get("status") != "accepted":
        raise WorkflowError("ART-WORKSTREAM-REGISTER must be accepted before workstream-init")
    sealed_paths_are_current(project_root, record.get("content_hashes"), "workstream register acceptance")
    _, streams = workstream_register(project_root)
    register_hash = file_sha256(mig / "workstream-register.json")
    existing_ids = {path.parent.name for path in (mig / "workstreams").glob("WS-*/status.json")}
    removed_streams = sorted(existing_ids - set(streams))
    if removed_streams:
        raise WorkflowError(
            "accepted register removed existing workstreams; preserve them with an explicit disposition: "
            + ", ".join(removed_streams)
        )
    created = 0; updated = 0
    for workstream_id, stream in streams.items():
        target = workstream_status_file(project_root, workstream_id)
        if target.exists():
            document = read_json(target)
            if document.get("register_sha256") == register_hash:
                continue
            values = document.get("slices") if isinstance(document.get("slices"), list) else []
            old = {str(item.get("id")): item for item in values if isinstance(item, dict) and item.get("id")}
            new = {str(item.get("id")): item for item in stream.get("slices", []) if isinstance(item, dict) and item.get("id")}
            removed = sorted(set(old) - set(new))
            if removed:
                raise WorkflowError(
                    f"{workstream_id} register removed existing slices; preserve with disposition: {', '.join(removed)}"
                )
            for slice_id, source in new.items():
                if slice_id not in old:
                    values.append({
                        "id": slice_id, "state": "planned", "allowed_states": SLICE_STATES,
                        "claimed_by": None, "claim_evidence": None, "claim_evidence_sha256": None,
                        "refs": source.get("refs") or [], "risk_classes": source.get("risk_classes") or [],
                        "interface_versions": {}, "evidence": [], "evidence_hashes": {}, "blockers": [],
                        "reviewer": None, "accepted_at": None, "updated_at": now_iso(), "history": [],
                    })
                    continue
                current_slice = old[slice_id]
                changed_scope = (
                    current_slice.get("refs") != (source.get("refs") or [])
                    or current_slice.get("risk_classes") != (source.get("risk_classes") or [])
                )
                if changed_scope and current_slice.get("state") not in {"planned", "ready"}:
                    raise WorkflowError(
                        f"{workstream_id}/{slice_id} scope changed after claim; close/release and use an explicit replacement slice"
                    )
                current_slice["refs"] = source.get("refs") or []
                current_slice["risk_classes"] = source.get("risk_classes") or []
            document["owner"] = stream.get("lead")
            document["reviewer"] = stream.get("reviewer")
            document["acceptance_delegate"] = stream.get("acceptance_delegate")
            document["register_sha256"] = register_hash
            atomic_write_json(target, document)
            updated += 1
            continue
        slices = []
        for source in stream.get("slices", []):
            slices.append({
                "id": source.get("id"), "state": "planned", "allowed_states": SLICE_STATES,
                "claimed_by": None, "claim_evidence": None, "claim_evidence_sha256": None,
                "refs": source.get("refs") or [], "risk_classes": source.get("risk_classes") or [],
                "interface_versions": {}, "evidence": [], "evidence_hashes": {}, "blockers": [],
                "reviewer": None, "accepted_at": None, "updated_at": now_iso(), "history": [],
            })
        document = {
            "schema": "bomdd-javafx-wpf-workstream-status/2.0",
            "workstream_id": workstream_id,
            "owner": stream.get("lead"), "reviewer": stream.get("reviewer"),
            "acceptance_delegate": stream.get("acceptance_delegate"),
            "register_sha256": register_hash, "slices": slices,
        }
        atomic_write_json(target, document)
        created += 1
    print(f"[workstreams] initialized={created} reconciled={updated} total={len(streams)}")
    print("[next] each lead runs slice-transition --to ready with readiness evidence")


def slice_transition(
    project_root: Path, workstream_id: str, slice_id: str, target_state: str,
    actor: str, evidence: list[str]
) -> None:
    _, _, status = require_scenario(project_root)
    require_no_active_change(status, "slice-transition")
    require_no_blockers(status, "slice-transition")
    path, document = load_workstream_status(project_root, workstream_id)
    problems = workstream_status_problems(project_root, document)
    if problems:
        raise WorkflowError(f"workstream status validation failed: {problems[0]}")
    item = find_slice(document, slice_id)
    if item.get("blockers"):
        raise WorkflowError(f"{slice_id} has blockers: {item['blockers'][0]}")
    current_state = str(item.get("state"))
    if target_state not in SLICE_STATES or target_state == "claimed":
        raise WorkflowError("target state must be a normal next state; use slice-claim for claimed")
    expected_index = SLICE_STATES.index(current_state) + 1
    if expected_index >= len(SLICE_STATES) or SLICE_STATES[expected_index] != target_state:
        raise WorkflowError(f"invalid slice transition {current_state} -> {target_state}")
    if not actor.strip() or actor == "UNASSIGNED":
        raise WorkflowError("--actor must name the person performing the transition")
    if target_state == "ready" and actor != document.get("owner"):
        raise WorkflowError(f"planned -> ready must be performed by workstream lead {document.get('owner')}")
    if target_state in {"manufacturing", "self-accepted"} and actor != item.get("claimed_by"):
        raise WorkflowError(f"{target_state} must be recorded by claimant {item.get('claimed_by')}")
    if target_state in {"integrated", "compared", "accepted", "as-built"}:
        allowed = {document.get("reviewer"), document.get("acceptance_delegate")}
        if actor not in allowed or actor == item.get("claimed_by"):
            raise WorkflowError("integration and acceptance require an assigned independent reviewer/delegate")
        item["reviewer"] = actor
        if target_state == "accepted":
            item["accepted_at"] = now_iso()
    append_slice_evidence(project_root, item, evidence, f"transition:{current_state}->{target_state}", actor)
    item["state"] = target_state
    atomic_write_json(path, document)
    print(f"[slice] {workstream_id}/{slice_id}: {current_state} -> {target_state}")


def slice_claim(
    project_root: Path, workstream_id: str, slice_id: str, worker: str, evidence: list[str]
) -> None:
    mig, profile, status = require_scenario(project_root)
    require_no_active_change(status, "slice-claim")
    require_no_blockers(status, "slice-claim")
    if not worker.strip() or worker == "UNASSIGNED":
        raise WorkflowError("--worker must name the actual worker")
    path, document = load_workstream_status(project_root, workstream_id)
    problems = workstream_status_problems(project_root, document)
    if problems:
        raise WorkflowError(f"workstream status validation failed: {problems[0]}")
    item = find_slice(document, slice_id)
    if item.get("state") != "ready" or item.get("blockers"):
        raise WorkflowError(f"{slice_id} must be ready with zero blockers before claim")
    active_states = {"claimed", "manufacturing", "self-accepted", "integrated", "compared", "accepted"}
    active = 0
    for status_path in (mig / "workstreams").glob("WS-*/status.json"):
        other = read_json(status_path)
        active += sum(1 for value in other.get("slices", []) if isinstance(value, dict) and value.get("claimed_by") == worker and value.get("state") in active_states)
    limit = int((profile.get("scale_control") or {}).get("maximum_work_in_progress_per_worker", 1))
    if active >= limit:
        raise WorkflowError(f"worker {worker} already has {active} active slice(s); WIP limit is {limit}")
    normalized = append_slice_evidence(project_root, item, evidence, "claim", worker)
    item["state"] = "claimed"; item["claimed_by"] = worker
    item["claim_evidence"] = normalized[0]
    item["claim_evidence_sha256"] = file_sha256(project_root.resolve() / normalized[0])
    atomic_write_json(path, document)
    print(f"[claimed] {workstream_id}/{slice_id} by {worker}")


def slice_release(
    project_root: Path, workstream_id: str, slice_id: str, actor: str, evidence: list[str]
) -> None:
    _, _, status = require_scenario(project_root)
    require_no_active_change(status, "slice-release")
    path, document = load_workstream_status(project_root, workstream_id)
    item = find_slice(document, slice_id)
    if item.get("state") not in {"claimed", "manufacturing"}:
        raise WorkflowError("only a claimed/manufacturing slice can be released")
    if actor not in {item.get("claimed_by"), document.get("owner")}:
        raise WorkflowError("slice release must be recorded by claimant or workstream lead")
    previous = item.get("claimed_by")
    append_slice_evidence(project_root, item, evidence, "release", actor)
    item["state"] = "ready"; item["claimed_by"] = None
    item["claim_evidence"] = None; item["claim_evidence_sha256"] = None
    atomic_write_json(path, document)
    print(f"[released] {workstream_id}/{slice_id} from {previous}; state=ready")


def slice_block_change(
    project_root: Path, workstream_id: str, slice_id: str, blocker: str,
    actor: str, evidence: list[str], resolve: bool
) -> None:
    _, _, status = require_scenario(project_root)
    require_no_active_change(status, "slice-unblock" if resolve else "slice-block")
    path, document = load_workstream_status(project_root, workstream_id)
    item = find_slice(document, slice_id)
    blockers = item.setdefault("blockers", [])
    if not isinstance(blockers, list):
        raise WorkflowError("slice blockers must be a list")
    if resolve:
        if blocker not in blockers:
            raise WorkflowError(f"slice blocker not found: {blocker}")
        blockers.remove(blocker); event = f"unblock:{blocker}"
    else:
        if blocker in blockers:
            raise WorkflowError(f"slice blocker already open: {blocker}")
        blockers.append(blocker); event = f"block:{blocker}"
    append_slice_evidence(project_root, item, evidence, event, actor)
    atomic_write_json(path, document)
    print(f"[{'unblocked' if resolve else 'blocked'}] {workstream_id}/{slice_id}: {blocker}")


def show_workstream_status(project_root: Path, selected: str | None = None) -> None:
    mig, _, _ = require_scenario(project_root)
    paths = [workstream_status_file(project_root, selected)] if selected else sorted((mig / "workstreams").glob("WS-*/status.json"))
    if not paths:
        raise WorkflowError("no workstream statuses; run workstream-init at MIG-50")
    totals = {state: 0 for state in SLICE_STATES}; blockers = 0; invalid = 0
    for path in paths:
        document = read_json(path); problems = workstream_status_problems(project_root, document)
        invalid += len(problems)
        slices = document.get("slices") if isinstance(document.get("slices"), list) else []
        for item in slices:
            if isinstance(item, dict):
                totals[str(item.get("state"))] = totals.get(str(item.get("state")), 0) + 1
                blockers += len(item.get("blockers") or [])
        print(f"{document.get('workstream_id')}: slices={len(slices)} blockers={sum(len(item.get('blockers') or []) for item in slices if isinstance(item, dict))} validation={'PASS' if not problems else 'FAIL'}")
        for problem in problems[:5]: print(f"  - {problem}")
    print("states: " + " ".join(f"{key}={value}" for key, value in totals.items()))
    print(f"total blockers={blockers} validation problems={invalid}")


def create_workstream_snapshot(project_root: Path) -> None:
    mig, _, status = require_scenario(project_root)
    require_no_active_change(status, "workstream-snapshot")
    require_no_blockers(status, "workstream-snapshot")
    register_path = mig / "workstream-register.json"
    _, streams = workstream_register(project_root)
    values: list[dict[str, Any]] = []
    totals = {"workstreams": len(streams), "slices": 0, "as_built": 0, "blockers": 0}
    for workstream_id in streams:
        path, document = load_workstream_status(project_root, workstream_id)
        problems = workstream_status_problems(project_root, document)
        if problems:
            raise WorkflowError(f"cannot snapshot {workstream_id}: {problems[0]}")
        slices = document.get("slices") or []
        as_built = sum(1 for item in slices if isinstance(item, dict) and item.get("state") == "as-built")
        blockers = sum(len(item.get("blockers") or []) for item in slices if isinstance(item, dict))
        totals["slices"] += len(slices); totals["as_built"] += as_built; totals["blockers"] += blockers
        values.append({"id": workstream_id, "status_path": path.relative_to(project_root.resolve()).as_posix(), "sha256": file_sha256(path), "slice_count": len(slices), "as_built_count": as_built, "blocker_count": blockers})
    result = "pass" if totals["slices"] > 0 and totals["slices"] == totals["as_built"] and totals["blockers"] == 0 else "fail"
    document = {"schema": "bomdd-javafx-wpf-workstream-snapshot/2.0", "created_at": now_iso(), "register": {"path": register_path.relative_to(project_root.resolve()).as_posix(), "sha256": file_sha256(register_path)}, "workstreams": values, "totals": totals, "result": result}
    atomic_write_json(mig / "workstream-snapshot.json", document)
    print(f"[snapshot] result={result.upper()} slices={totals['slices']} as-built={totals['as_built']} blockers={totals['blockers']}")


def show_status(project_root: Path) -> None:
    mig, _, status = require_scenario(project_root)
    definition = load_definition(mig)
    milestones = milestone_map(definition)
    current = status.get("current") or {}
    current_id = current.get("milestone")
    current_def = milestones.get(current_id, {})
    last = status.get("last_passed_milestone") or {}
    change = active_change(status)
    last_suffix = ""
    if change is not None and change.get("milestone") == last.get("id"):
        last_suffix = " [superseded; replacement Gate pending]"
    print(f"Project      : {status.get('product')}")
    print(f"Scenario     : {status.get('scenario_id')}")
    print(f"Last passed  : {last.get('id', 'none')} {last.get('name', '')}{last_suffix}".rstrip())
    print(f"Current      : {current_id} {current_def.get('name', '')}".rstrip())
    print(f"Current step : {current.get('step')}")
    print(f"Owner        : {current.get('owner')}")
    print(f"Work item    : {current.get('work_item')}")
    print(f"Action       : {current.get('action')}")
    if change is not None:
        print(f"Paused by    : {change.get('id')} [{change.get('state')}]")
        print(f"Changed file : {change.get('changed_file')}")
        print(f"Change owner : {change.get('owner')}")
    blockers = status.get("blockers") or []
    print(f"Blockers     : {len(blockers)}")
    for blocker in blockers:
        print(f"  - {blocker}")
    open_items = [item for item in exception_records(status) if item.get("status") == "open"]
    print(f"Open except. : {len(open_items)}")
    for item in open_items:
        print(
            f"  - {item.get('occurrence_id')} [{item.get('classification')}] "
            f"owner={item.get('owner_role')}"
        )
    records = artifact_records(status)
    missing = []
    for required in current_def.get("required_artifacts", []):
        record = records.get(required["id"])
        if not record or record.get("status") != "accepted":
            missing.append((required["id"], required["path"], record.get("status") if record else "unregistered"))
    print(f"Unaccepted   : {len(missing)}")
    for artifact_id, path, state in missing:
        print(f"  - {artifact_id} [{state}] {path}")
    nxt = status.get("next") or {}
    print(f"Next         : {nxt.get('step')} {nxt.get('action')}".rstrip())


def print_exception_next(status: dict[str, Any], exception: dict[str, Any]) -> None:
    classification = exception.get("classification")
    color = "RED" if classification == "blocker" else "YELLOW"
    print(f"[{color}] {exception.get('occurrence_id')} [{classification}]")
    print(f"Owner: {exception.get('owner_role')} - {exception.get('owner')}")
    print(f"[DO] {exception.get('default_action')}")
    safe_work = exception.get("safe_work") if isinstance(exception.get("safe_work"), list) else []
    if classification == "blocker":
        if safe_work:
            print("Authorized alternate safe work:")
            for item in safe_work:
                if isinstance(item, dict):
                    print(f"  - {item.get('work')}")
        else:
            print("Authorized alternate safe work: none")
    print(f"Preserved normal position after resolution: {exception.get('resume_position')}")
    if exception.get("catalog_resume") != exception.get("resume_position"):
        print(f"Catalog follow-up target: {exception.get('catalog_resume')}")
    print(
        "[THEN] python bomdd/migration/tools/migration-workflow.py exception-resolve "
        f"--project-root <PROJECT_ROOT> --exception {exception.get('occurrence_id')} "
        "--resolver <NAME> --resolution \"<APPLIED_RESULT>\" --evidence <RESOLUTION_EVIDENCE>"
    )


def show_due_decision_next(
    project_root: Path,
    mig: Path,
    profile: dict[str, Any],
    status: dict[str, Any],
) -> bool:
    definition = load_definition(mig)
    milestones = milestone_map(definition)
    sets = decision_set_map(definition)
    current_id = str((status.get("current") or {}).get("milestone"))
    current_def = milestones.get(current_id, {})
    artifacts = artifact_records(status)
    owners = profile.get("owners") if isinstance(profile.get("owners"), dict) else {}
    for decision_set_id in current_def.get("required_decision_sets", []):
        spec = sets.get(str(decision_set_id))
        if spec is None:
            print(f"[RED] unknown required decision set: {decision_set_id}; use EX-DOC-001")
            return True
        problems = decision_set_gate_problems(
            project_root, status, definition, str(decision_set_id)
        )
        if not problems:
            continue
        artifact = artifacts.get(str(spec.get("artifact_id")), {})
        if spec.get("due_milestone") != current_id or artifact.get("status") == "accepted":
            print(f"[RED] accepted prerequisite decision set is invalid: {decision_set_id}")
            print(f"  - {problems[0]}")
            print(
                "[DO] python bomdd/migration/tools/migration-workflow.py check "
                f"--project-root <PROJECT_ROOT> --milestone {spec.get('due_milestone')}"
            )
            print("[THEN] use the displayed accepted-change recovery command; do not edit the seal")
            return True
        path = project_root.resolve() / str(spec.get("path"))
        if not path.is_file():
            print(f"[RED] due decision document is missing: {spec.get('path')}")
            print("[DO] upgraded projects run adopt-decision-layout; new projects use EX-STATE-001")
            return True
        document = read_json(path)
        values = document.get("decisions") if isinstance(document.get("decisions"), list) else []
        mapped = {str(item.get("id")): item for item in values if isinstance(item, dict)}
        for expected in spec.get("decisions", []):
            decision_id = str(expected.get("id"))
            record = mapped.get(decision_id, {})
            one_spec = {**spec, "decisions": [expected]}
            one_doc = {**document, "decisions": [record] if record else []}
            if decision_document_problems(project_root, one_spec, one_doc):
                owner_role = str(expected.get("owner"))
                assigned = str(owners.get(owner_role) or "UNASSIGNED")
                print(f"[DECISION] {decision_id} is due now in {decision_set_id}")
                print(f"Owner: {owner_role} - {assigned}")
                print(
                    "[DO] python bomdd/migration/tools/migration-workflow.py decision-record "
                    f"--project-root <PROJECT_ROOT> --set {decision_set_id} "
                    f"--decision {decision_id} --decider \"{assigned}\" --status decided "
                    "--value \"<DECISION>\" --evidence <LOCAL_DECISION_EVIDENCE>"
                )
                return True
        print(f"[DECISION] all records in {decision_set_id} are complete; accept the set")
        print(
            "[DO] python bomdd/migration/tools/migration-workflow.py accept-artifact "
            f"--project-root <PROJECT_ROOT> --artifact {spec.get('artifact_id')} "
            "--evidence <DECISION_SET_REVIEW>"
        )
        return True
    return False


def show_next(project_root: Path) -> None:
    mig, profile, status = require_scenario(project_root)
    blockers = status.get("blockers") or []
    current = status.get("current") or {}
    open_items = [item for item in exception_records(status) if item.get("status") == "open"]
    if blockers:
        first_id = str(blockers[0]) if isinstance(blockers, list) and blockers else ""
        structured = next((item for item in open_items if item.get("occurrence_id") == first_id), None)
        if structured is not None:
            print_exception_next(status, structured)
        else:
            print(f"[RED] {len(blockers)} blocker(s). Do not advance {current.get('step')}.")
            for blocker in blockers:
                print(f"  - {blocker}")
            print("No structured exception record exists. Open EX-STATE-001 and preserve the current STEP.")
        return
    audit_problems = exception_seal_problems(project_root, status)
    if audit_problems:
        print("[RED] recorded exception evidence or event content changed.")
        print(f"  - {audit_problems[0]}")
        print("[DO] Preserve the current files, create an observation evidence file, and open EX-STATE-001.")
        print(
            "[THEN] python bomdd/migration/tools/migration-workflow.py exception-open "
            "--project-root <PROJECT_ROOT> --catalog-id EX-STATE-001 "
            "--symptom \"exception history seal mismatch\" --evidence <OBSERVATION_EVIDENCE> "
            "--production-db unknown --baseline-fixture unknown --current-source unknown"
        )
        return
    change = active_change(status)
    if change is not None:
        print(f"[CHANGE] {change['id']} - {change.get('state')}")
        print(f"Normal work is paused at {(status.get('current') or {}).get('step')}.")
        state = change.get("state")
        if state == "opened":
            print(f"[DO] Correct `{change.get('changed_file')}`, run the required retest, and save its evidence.")
            print("[THEN] python bomdd/migration/tools/migration-workflow.py change-retest --project-root <PROJECT_ROOT> --evidence <RETEST_EVIDENCE>")
        elif state == "retested":
            print("[DO] python bomdd/migration/tools/migration-workflow.py change-accept --project-root <PROJECT_ROOT> --reviewer <NAME> --evidence <REACCEPTANCE_REVIEW>")
        elif state in {"reaccepted", "approving"}:
            milestone = milestone_map(load_definition(mig)).get(str(change.get("milestone")), {})
            required = [str(item) for item in milestone.get("required_approvals", [])]
            approvals = status.get("approvals") if isinstance(status.get("approvals"), list) else []
            completed = {
                str(item.get("role"))
                for item in approvals
                if isinstance(item, dict)
                and item.get("change_id") == change["id"]
                and item.get("status") == "approved"
            }
            missing = [item for item in required if item not in completed]
            if not missing:
                print("[DO] python bomdd/migration/tools/migration-workflow.py change-close --project-root <PROJECT_ROOT>")
            else:
                print(
                    "[DO] python bomdd/migration/tools/migration-workflow.py change-approve "
                    f"--project-root <PROJECT_ROOT> --role \"{missing[0]}\" "
                    "--approver <NAME> --evidence <REAPPROVAL_EVIDENCE>"
                )
        elif state == "approved":
            print("[DO] python bomdd/migration/tools/migration-workflow.py change-close --project-root <PROJECT_ROOT>")
        else:
            raise WorkflowError(f"unknown accepted change state: {state}; use EX-STATE-001")
        return
    pending = next((item for item in open_items if item.get("classification") != "blocker"), None)
    if pending is not None:
        print_exception_next(status, pending)
        return
    if show_due_decision_next(project_root, mig, profile, status):
        return
    current_id = str(current.get("milestone") or "")
    if current.get("step") == f"GATE-{current_id}":
        gate = check_gate(project_root, current_id)
        print(f"[GATE] {current_id} read-only evaluation: {gate['gate']['result'].upper()}")
        print(
            f"[DO] python {Path(__file__).resolve()} check "
            f"--project-root {project_root.resolve()} --milestone {current_id}"
        )
        print("[NOTE] check is read-only and does not create the persisted Gate result file.")
        print(
            f"[THEN] If PASS, python {Path(__file__).resolve()} advance "
            f"--project-root {project_root.resolve()}"
        )
        print("[NOTE] advance rechecks, writes the Gate result, and moves to the next milestone.")
        return
    print(f"[DO] {current.get('step')} - {current.get('action')}")
    print(f"Work item: {current.get('work_item')}")
    nxt = status.get("next") or {}
    print(f"After completion: {nxt.get('step')} - {nxt.get('action')}")


def advance(project_root: Path) -> None:
    mig, profile, status = require_scenario(project_root)
    require_no_active_change(status, "advance")
    require_no_blockers(status, "advance")
    definition = load_definition(mig)
    milestones = milestone_map(definition)
    current_id = (status.get("current") or {}).get("milestone")
    result = check_gate(project_root, current_id)
    gate_path = mig / "gates" / f"{current_id}-result.json"
    atomic_write_json(gate_path, result)
    print_gate(result)
    if result["gate"]["result"] != "pass":
        raise WorkflowError(f"Gate failed. Result saved to {gate_path}. No milestone advance was made.")

    current_def = milestones[current_id]
    status["last_passed_milestone"] = {
        "id": current_id,
        "name": current_def["name"],
        "passed_at": now_iso(),
        "gate_result_ref": gate_path.relative_to(project_root.resolve()).as_posix(),
    }
    next_id = current_def.get("next_milestone")
    if next_id is None:
        status["current"] = {
            "milestone": "COMPLETE",
            "step": "COMPLETE",
            "work_item": "MIGRATION-COMPLETE",
            "action": "移行完了。新規変更は通常のECO/CAPA入口を使う",
            "owner": (status.get("current") or {}).get("owner", "UNASSIGNED"),
            "started_at": now_iso(),
        }
        status["next"] = {"step": None, "action": None}
    else:
        next_def = milestones[next_id]
        follow_step, follow_action = FOLLOWUP[next_id]
        owners = profile.get("owners") or {}
        worker = owners.get("Migration Worker") or owners.get("Migration Owner") or "UNASSIGNED"
        status["current"] = {
            "milestone": next_id,
            "step": next_def["entry_step"],
            "work_item": next_id,
            "action": next_def["entry_action"],
            "owner": worker,
            "started_at": now_iso(),
        }
        status["next"] = {"step": follow_step, "action": follow_action}
    status["updated_at"] = now_iso()
    atomic_write_json(mig / "migration-status.json", status)
    print(f"[advanced] {current_id} -> {next_id or 'COMPLETE'}")


def handoff(project_root: Path) -> None:
    mig, _, status = require_scenario(project_root)
    current = status.get("current") or {}
    definition = load_definition(mig)
    milestones = definition.get("milestones") if isinstance(definition.get("milestones"), list) else []
    milestone_positions = {
        str(item.get("id")): index
        for index, item in enumerate(milestones)
        if isinstance(item, dict) and item.get("id")
    }
    current_id = str(current.get("milestone") or "")
    current_position = milestone_positions.get(current_id, -1)
    current_def = next(
        (item for item in milestones if isinstance(item, dict) and item.get("id") == current_id),
        {},
    )
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = mig / "handoffs" / f"handoff-{stamp}.md"
    records = artifact_records(status)
    accepted = [r for r in records.values() if r.get("status") == "accepted"]
    current_required_ids = [
        str(item.get("id"))
        for item in current_def.get("required_artifacts", [])
        if isinstance(item, dict) and item.get("id")
    ]
    current_unaccepted = [
        records[artifact_id]
        for artifact_id in current_required_ids
        if artifact_id in records and records[artifact_id].get("status") != "accepted"
    ]
    artifact_due: dict[str, str] = {}
    for milestone in milestones:
        if not isinstance(milestone, dict):
            continue
        milestone_id = str(milestone.get("id") or "")
        for item in milestone.get("required_artifacts", []):
            if isinstance(item, dict) and item.get("id"):
                artifact_due.setdefault(str(item["id"]), milestone_id)
    future_unfinished: list[tuple[dict[str, Any], str]] = []
    historical_unfinished: list[tuple[dict[str, Any], str]] = []
    for artifact_id, due_id in artifact_due.items():
        record = records.get(artifact_id)
        if record is None or record.get("status") == "accepted" or due_id == current_id:
            continue
        due_position = milestone_positions.get(due_id, -1)
        target_list = future_unfinished if due_position > current_position else historical_unfinished
        target_list.append((record, due_id))
    approvals = status.get("approvals") if isinstance(status.get("approvals"), list) else []
    approved_roles = {
        str(item.get("role"))
        for item in approvals
        if isinstance(item, dict)
        and item.get("milestone") == current_id
        and item.get("status") == "approved"
    }
    missing_roles = [
        str(role) for role in current_def.get("required_approvals", [])
        if str(role) not in approved_roles
    ]
    at_gate = current.get("step") == f"GATE-{current_id}"
    gate_now = check_gate(project_root, current_id)["gate"]["result"].upper() if at_gate else None
    lines = [
        f"# Migration Handoff {stamp}",
        "",
        f"- Product: {status.get('product')}",
        f"- Scenario: {status.get('scenario_id')}",
        f"- Current milestone: {current.get('milestone')}",
        f"- Current STEP: {current.get('step')}",
        f"- Current action: {current.get('action')}",
        f"- Work item: {current.get('work_item')}",
        f"- Current milestone unaccepted artifacts: {len(current_unaccepted)}",
        f"- Current milestone missing approvals: {len(missing_roles)}",
        "",
        "## Active accepted change",
        "",
    ]
    change = active_change(status)
    if change is None:
        lines.append("- none")
    else:
        lines.extend([
            f"- ID: {change.get('id')}",
            f"- State: {change.get('state')}",
            f"- Milestone: {change.get('milestone')}",
            f"- Changed file: `{change.get('changed_file')}`",
            "- Resume the change with `next`; do not resume the normal STEP first.",
        ])
    lines.extend([
        "",
        "## Blockers",
        "",
    ])
    blockers = status.get("blockers") or []
    lines.extend([f"- {b}" for b in blockers] or ["- none"])
    lines.extend(["", "## Non-blockers", ""])
    non_blockers = status.get("non_blockers") or []
    lines.extend([f"- {b}" for b in non_blockers] or ["- none"])
    lines.extend(["", "## Open exception actions", ""])
    open_items = [item for item in exception_records(status) if item.get("status") == "open"]
    if open_items:
        for item in open_items:
            lines.extend([
                f"- {item.get('occurrence_id')} [{item.get('classification')}]: {item.get('symptom')}",
                f"  - Owner: {item.get('owner_role')} - {item.get('owner')}",
                f"  - Default action: {item.get('default_action')}",
                f"  - Preserved position: {item.get('resume_position')}",
                f"  - Catalog follow-up: {item.get('catalog_resume')}",
            ])
    else:
        lines.append("- none")
    lines.extend(["", "## Recently accepted artifacts", ""])
    lines.extend([f"- {r.get('id')}: `{r.get('path')}`" for r in accepted[-10:]] or ["- none"])
    lines.extend(["", "## Current milestone unaccepted artifacts", ""])
    lines.extend([
        f"- {record.get('id')} [{record.get('status')}]: `{record.get('path')}`"
        for record in current_unaccepted
    ] or ["- none (count: 0)"])
    lines.extend(["", "## Current milestone missing approvals", ""])
    lines.extend([f"- {role}" for role in missing_roles] or ["- none (count: 0)"])
    if at_gate:
        lines.extend([
            "",
            "## Current Gate state",
            "",
            f"- Read-only evaluation while creating this handoff: {gate_now}",
            "- `check` evaluates only; it does not create the persisted Gate result file.",
            "- `advance` rechecks, writes the Gate result, and then moves to the next milestone.",
        ])
    if historical_unfinished:
        lines.extend(["", "## Historical required artifacts needing attention", ""])
        lines.extend([
            f"- {record.get('id')} [{record.get('status')}], required at {due_id}: `{record.get('path')}`"
            for record, due_id in historical_unfinished[:10]
        ])
    lines.extend(["", "## Future artifacts (not current milestone blockers)", ""])
    lines.extend([
        f"- {record.get('id')} [{record.get('status')}], required at {due_id}: `{record.get('path')}`"
        for record, due_id in future_unfinished[:10]
    ] or ["- none"])
    lines.extend(["", "## Resume", ""])
    tool_path = Path(__file__).resolve()
    root_path = project_root.resolve()
    interrupted = bool(blockers or open_items or change is not None)
    if at_gate and not interrupted:
        lines.extend([
            f"Run now: `python {tool_path} check --project-root {root_path} --milestone {current_id}`",
            "",
            f"If PASS: `python {tool_path} advance --project-root {root_path}`",
            "",
            "Do not treat future artifacts listed above as current milestone failures.",
        ])
    else:
        lines.append(f"Run: `python {tool_path} next --project-root {root_path}`")
    lines.append("")
    target.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"[ok] handoff written: {target}")


def frozen_runtime_context() -> tuple[Path, Path] | None:
    tool = Path(__file__).resolve()
    candidate_migration = tool.parent.parent
    if tool.parent.name != "tools":
        return None
    required = (
        candidate_migration / "migration-status.json",
        candidate_migration / "migration-profile.json",
        candidate_migration / "milestone-definition.json",
    )
    if not all(path.is_file() for path in required):
        return None
    project_root = candidate_migration.parent.parent
    return candidate_migration, project_root


def frozen_runtime_selftest(mig: Path, project_root: Path) -> int:
    observed_files = [
        mig / "migration-status.json",
        mig / "migration-profile.json",
        mig / "milestone-definition.json",
        mig / "guide" / "migration-runbook.md",
        mig / "guide" / "onboarding.md",
        mig / "guide" / "exception-catalog.md",
    ]
    missing = [path for path in observed_files if not path.is_file()]
    if missing:
        print(f"frozen-selftest: FAIL - required file not found: {missing[0]}")
        return 1
    before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in observed_files}
    try:
        actual_mig, _, status = require_scenario(project_root)
        if actual_mig.resolve() != mig.resolve():
            print("frozen-selftest: FAIL - detected migration root does not match tool location")
            return 1
        definition = load_definition(mig)
        milestones = milestone_map(definition)
        current = status.get("current") or {}
        current_id = str(current.get("milestone"))
        current_step = str(current.get("step"))
        if current_id != "COMPLETE":
            if current_id not in milestones:
                print(f"frozen-selftest: FAIL - unknown current milestone: {current_id}")
                return 1
            steps = milestone_steps(mig, current_id)
            valid_steps = {item[0] for item in steps} | {f"GATE-{current_id}"}
            if current_step not in valid_steps:
                print(f"frozen-selftest: FAIL - current STEP is not in frozen guide: {current_step}")
                return 1
            check_gate(project_root, current_id)
    except WorkflowError as exc:
        print(f"frozen-selftest: FAIL - {exc}")
        return 1
    after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in observed_files}
    changed = [path for path in observed_files if before[path] != after[path]]
    if changed:
        print(f"frozen-selftest: FAIL - read-only check changed: {changed[0]}")
        return 1
    print(f"frozen-selftest: PASS - {current_id} {current_step}; files unchanged")
    return 0


def selftest() -> int:
    frozen = frozen_runtime_context()
    if frozen is not None:
        return frozen_runtime_selftest(*frozen)
    with tempfile.TemporaryDirectory(prefix="bomdd-migration-selftest-") as temp:
        root = Path(temp) / "product"
        root.mkdir()
        (root / ".git").mkdir()
        initialize(root, "SelfTestProduct")
        mig = migration_root(root)
        if not (mig / "guide" / "onboarding.md").is_file():
            print("selftest: FAIL - onboarding entry was not installed")
            return 1
        frozen_check = subprocess.run(
            [sys.executable, str(mig / "tools" / "migration-workflow.py"), "--selftest"],
            capture_output=True, text=True, encoding="utf-8",
        )
        if frozen_check.returncode != 0 or "frozen-selftest: PASS" not in frozen_check.stdout:
            print("selftest: FAIL - copied scenario tool is not self-contained")
            print(frozen_check.stdout); print(frozen_check.stderr)
            return 1
        profile_path = mig / "migration-profile.json"
        selftest_profile = read_json(profile_path)
        for role in selftest_profile.get("owners", {}):
            selftest_profile["owners"][role] = "Self Test Owner"
        selftest_profile["owners"]["Customer Acceptance Owner"] = "Self Test Customer"
        selftest_profile["owners"]["Security Owner"] = "Self Test Security"
        selftest_profile["source"].update({
            "jdk_line": "21", "javafx_line": "21", "build_systems": ["Gradle 8"],
            "estimated_loc": 300000, "repository_count": 3, "module_count": 20,
            "screen_count": 120, "customer_count": 5, "active_user_count": 500,
        })
        selftest_profile["constraints"]["database_engine"] = "SQLite selftest"
        selftest_profile["constraints"]["customer_outage_budget"] = "30 minutes"
        atomic_write_json(profile_path, selftest_profile)

        initial = check_gate(root, "MIG-00")
        if initial["gate"]["result"] != "fail":
            print("selftest: FAIL - incomplete MIG-00 unexpectedly passed")
            return 1

        charter = root / "bomdd" / "00-charter.md"
        charter.write_text("# Accepted migration charter\n", encoding="utf-8")
        for path in (
            mig / "responsibility-matrix.md",
            mig / "program-governance.md",
            mig / "customer-operations-boundary.md",
        ):
            completed = path.read_text(encoding="utf-8").replace("UNASSIGNED", "Self Test Assigned")
            completed = completed.replace("REPLACE", "SelfTestValue")
            path.write_text(completed, encoding="utf-8")
        approval = mig / "evidence" / "MIG-00-approval.md"
        approval.write_text("approved by Self Test Owner\n", encoding="utf-8")
        accept_artifact(root, "ART-CHARTER", ["bomdd/00-charter.md"])
        accept_artifact(root, "ART-PROFILE", ["bomdd/migration/migration-profile.json"])
        accept_artifact(root, "ART-ROLES", ["bomdd/migration/responsibility-matrix.md"])
        accept_artifact(root, "ART-PROGRAM-GOVERNANCE", ["bomdd/migration/program-governance.md"])
        accept_artifact(root, "ART-CUSTOMER-BOUNDARY", ["bomdd/migration/customer-operations-boundary.md"])
        for role in ("Migration Owner", "Operations Owner", "Customer Acceptance Owner"):
            approve_milestone(root, role, f"Self Test {role}",
                              "bomdd/migration/evidence/MIG-00-approval.md")
        bypass_checks = [
            ("direct reacceptance", lambda: accept_artifact(
                root, "ART-CHARTER", ["bomdd/00-charter.md"]
            )),
            ("direct reapproval", lambda: approve_milestone(
                root, "Migration Owner", "Self Test Owner",
                "bomdd/migration/evidence/MIG-00-approval.md",
            )),
            ("reseal", lambda: seal_milestone(
                root, "MIG-00", "Self Test Owner",
                "bomdd/migration/evidence/MIG-00-approval.md",
            )),
        ]
        for label, operation in bypass_checks:
            try:
                operation()
                print(f"selftest: FAIL - {label} bypassed the accepted change workflow")
                return 1
            except WorkflowError:
                pass

        for _ in range(4):
            complete_step(root, ["bomdd/00-charter.md"])
        stepped = read_json(mig / "migration-status.json")
        if stepped["current"]["step"] != "GATE-MIG-00":
            print("selftest: FAIL - complete-step did not reach GATE-MIG-00")
            return 1

        passed = check_gate(root, "MIG-00")
        if passed["gate"]["result"] != "pass":
            print_gate(passed)
            print("selftest: FAIL - completed MIG-00 did not pass")
            return 1
        advance(root)
        advanced = read_json(mig / "migration-status.json")
        if advanced["current"]["milestone"] != "MIG-10":
            print("selftest: FAIL - advance did not move to MIG-10")
            return 1

        baseline = mig / "current-baseline.md"
        build_log = mig / "evidence" / "baseline-build.log"
        db_baseline = mig / "db-baseline.md"
        db_observation = mig / "evidence" / "baseline-db-observation.md"
        schema_evidence = mig / "evidence" / "baseline-schema.sql"
        ui_index = mig / "current-observation-index.md"
        ui_root = mig / "evidence" / "current-ui"
        ui_root.mkdir(parents=True)
        screenshot = ui_root / "OBS-UI-001.png"
        semantic_log = mig / "evidence" / "OBS-UI-001.log"
        fixture = root / "fixtures" / "baseline" / "selftest.db"
        restore_copy = root / "fixtures" / "restore-control" / "selftest.db"
        fixture.parent.mkdir(parents=True)
        restore_copy.parent.mkdir(parents=True)
        connection = sqlite3.connect(fixture)
        connection.execute("CREATE TABLE sample (id INTEGER PRIMARY KEY, value TEXT NOT NULL)")
        connection.execute("INSERT INTO sample (value) VALUES ('accepted')")
        connection.commit()
        connection.close()
        shutil.copy2(fixture, restore_copy)

        def png_chunk(kind: bytes, payload: bytes) -> bytes:
            return (
                struct.pack(">I", len(payload)) + kind + payload
                + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
            )

        screenshot_bytes = (
            b"\x89PNG\r\n\x1a\n"
            + png_chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
            + png_chunk(b"IDAT", zlib.compress(b"\x00\x00\x00\x00"))
            + png_chunk(b"IEND", b"")
        )
        screenshot.write_bytes(screenshot_bytes)
        baseline.write_text("# Frozen current baseline\n", encoding="utf-8")
        build_log.write_text("selftest build passed\n", encoding="utf-8")
        db_baseline.write_text("# Accepted DB baseline\n", encoding="utf-8")
        db_observation.write_text("integrity ok; foreign keys 0; sample rows 1\n", encoding="utf-8")
        schema_evidence.write_text(
            "CREATE TABLE sample (id INTEGER PRIMARY KEY, value TEXT NOT NULL);\n",
            encoding="utf-8",
        )
        ui_index.write_text(
            "# Current observations\n\n"
            "| Observation ID | Result |\n|---|---|\n"
            "| OBS-CURRENT-001 | empty state is visible |\n",
            encoding="utf-8",
        )
        semantic_log.write_text("empty state confirmed by semantic probe\n", encoding="utf-8")
        fixture_hash = file_sha256(fixture)
        fixture_manifest = {
            "schema": "bomdd-legacy-wpf-baseline-fixture/1.0",
            "fixture_id": "SELFTEST-FIXTURE-001",
            "engine": "sqlite",
            "source_snapshot": now_iso(),
            "working_copy_policy": "copy-per-test",
            "fixture": {
                "path": "fixtures/baseline/selftest.db",
                "sha256": fixture_hash,
                "immutable_baseline": True,
            },
            "restore_copy": {
                "path": "fixtures/restore-control/selftest.db",
                "sha256": file_sha256(restore_copy),
            },
            "baseline_document": {
                "path": "bomdd/migration/db-baseline.md",
                "sha256": file_sha256(db_baseline),
            },
            "schema_evidence": {
                "path": "bomdd/migration/evidence/baseline-schema.sql",
                "sha256": file_sha256(schema_evidence),
                "normalized_schema_sha256": file_sha256(schema_evidence),
            },
            "observation_evidence": [{
                "path": "bomdd/migration/evidence/baseline-db-observation.md",
                "sha256": file_sha256(db_observation),
            }],
            "expected_checks": {
                "integrity_check": "ok",
                "foreign_key_violations": 0,
                "restore_result": "pass",
                "restored_sha256": fixture_hash,
            },
            "canonical_queries": [{
                "id": "SAMPLE-COUNT",
                "sql": "SELECT COUNT(*) FROM sample",
                "expected_rows": [[1]],
            }],
        }
        fixture_manifest_path = mig / "evidence" / "baseline-fixture-manifest.json"
        atomic_write_json(fixture_manifest_path, fixture_manifest)
        ui_manifest = {
            "schema": "bomdd-legacy-wpf-ui-evidence/1.0",
            "source_version": "selftest-version",
            "observation_index": {
                "path": "bomdd/migration/current-observation-index.md",
                "sha256": file_sha256(ui_index),
            },
            "coverage_policy": {
                "required_states": ["empty"],
                "minimum_width": 1,
                "minimum_height": 1,
            },
            "observations": [{
                "id": "OBS-CURRENT-001",
                "states": ["empty"],
                "evidence": [
                    {
                        "id": "SHOT-001",
                        "kind": "screenshot",
                        "path": "bomdd/migration/evidence/current-ui/OBS-UI-001.png",
                        "sha256": file_sha256(screenshot),
                        "media_type": "image/png",
                        "width": 1,
                        "height": 1,
                    },
                    {
                        "id": "SEM-001",
                        "kind": "execution-log",
                        "path": "bomdd/migration/evidence/OBS-UI-001.log",
                        "sha256": file_sha256(semantic_log),
                    },
                ],
                "claims": [{
                    "text": "empty state is visible and semantically confirmed",
                    "supported_by": ["SHOT-001", "SEM-001"],
                }],
            }],
        }
        ui_manifest_path = mig / "evidence" / "current-ui-evidence-manifest.json"
        atomic_write_json(ui_manifest_path, ui_manifest)
        java_baseline = mig / "java-runtime-baseline.md"
        security_baseline = mig / "security-baseline.md"
        ops_baseline = mig / "deployment-operations-baseline.md"
        java_baseline.write_text("# JDK 21 / JavaFX 21 / Gradle 8 frozen\n", encoding="utf-8")
        security_baseline.write_text("# Security baseline\nAuthentication and signing observed.\n", encoding="utf-8")
        ops_baseline.write_text("# Operations baseline\nInstall, update, logging and support observed.\n", encoding="utf-8")
        nfr_evidence = mig / "evidence" / "MIG-10-nfr.json"
        atomic_write_json(nfr_evidence, {"result": "pass", "samples": 5})
        nfr = read_json(mig / "nonfunctional-baseline.json")
        nfr["captured_at"] = now_iso(); nfr["source_version"] = "selftest-source"
        nfr["environment_id"] = "selftest-windows"
        nfr["datasets"] = [{"id": "DATA-SMALL", "description": "selftest", "row_counts": {"sample": 1}}]
        nfr["workloads"] = [{"id": "LOAD-ONE", "users": 1, "duration_seconds": 60, "description": "selftest"}]
        for metric in nfr["metrics"]:
            metric.update({"sample_count": 5, "p50": 1, "p95": 2, "max": 3,
                           "evidence": "bomdd/migration/evidence/MIG-10-nfr.json"})
        atomic_write_json(mig / "nonfunctional-baseline.json", nfr)
        mig10_review = mig / "evidence" / "MIG-10-review.md"
        mig10_approval = mig / "evidence" / "MIG-10-approval.md"
        mig10_review.write_text("fixture and UI manifests reviewed\n", encoding="utf-8")
        mig10_approval.write_text("MIG-10 approved\n", encoding="utf-8")
        accept_artifact(root, "ART-BASELINE", ["bomdd/migration/evidence/MIG-10-review.md"])
        accept_artifact(root, "ART-BUILD-LOG", ["bomdd/migration/evidence/MIG-10-review.md"])
        accept_artifact(root, "ART-DB-BASELINE", [
            "bomdd/migration/evidence/baseline-fixture-manifest.json",
            "bomdd/migration/evidence/MIG-10-review.md",
        ])
        accept_artifact(root, "ART-CURRENT-OBS", [
            "bomdd/migration/evidence/current-ui-evidence-manifest.json",
            "bomdd/migration/evidence/MIG-10-review.md",
        ])
        accept_artifact(root, "ART-JAVA-BASELINE", ["bomdd/migration/evidence/MIG-10-review.md"])
        accept_artifact(root, "ART-NFR-BASELINE", [
            "bomdd/migration/evidence/MIG-10-nfr.json",
            "bomdd/migration/evidence/MIG-10-review.md",
        ])
        accept_artifact(root, "ART-SECURITY-BASELINE", ["bomdd/migration/evidence/MIG-10-review.md"])
        accept_artifact(root, "ART-OPS-BASELINE", ["bomdd/migration/evidence/MIG-10-review.md"])
        for role in ("Java Technical Owner", "DB Custodian", "UI Approver", "Acceptance Owner", "Security Owner", "Operations Owner"):
            approve_milestone(
                root, role, "Self Test Owner", "bomdd/migration/evidence/MIG-10-approval.md"
            )
        evidence_pass = check_gate(root, "MIG-10")
        if evidence_pass["gate"]["result"] != "pass":
            print_gate(evidence_pass)
            print("selftest: FAIL - valid fixture/UI manifests did not pass")
            return 1
        fixture.unlink()
        missing_fixture = check_gate(root, "MIG-10")
        if missing_fixture["gate"]["result"] != "fail" or not any(
            "baseline fixture file not found" in str(problem)
            for check in missing_fixture["checks"] for problem in check.get("problems", [])
        ):
            print("selftest: FAIL - Gate did not reject a missing baseline fixture")
            return 1
        shutil.copy2(restore_copy, fixture)
        screenshot.write_bytes(b"not an image")
        changed_ui = check_gate(root, "MIG-10")
        if changed_ui["gate"]["result"] != "fail" or not any(
            "hash mismatch" in str(problem)
            for check in changed_ui["checks"] for problem in check.get("problems", [])
        ):
            print("selftest: FAIL - Gate did not reject changed UI evidence bytes")
            return 1
        screenshot.write_bytes(screenshot_bytes)

        handoff_status = read_json(mig / "migration-status.json")
        saved_current = copy.deepcopy(handoff_status.get("current"))
        saved_next = copy.deepcopy(handoff_status.get("next"))
        handoff_status["current"]["step"] = "GATE-MIG-10"
        handoff_status["current"]["action"] = "MIG-10 Gate を確認する"
        handoff_status["next"] = {
            "step": "advance",
            "action": "Gate PASS 後に次のマイルストーンへ進む",
        }
        atomic_write_json(mig / "migration-status.json", handoff_status)
        handoff(root)
        gate_handoffs = sorted((mig / "handoffs").glob("handoff-*.md"))
        if not gate_handoffs:
            print("selftest: FAIL - Gate handoff was not generated")
            return 1
        gate_handoff = gate_handoffs[-1].read_text(encoding="utf-8")
        required_handoff_text = (
            "Current milestone unaccepted artifacts: 0",
            "## Current milestone unaccepted artifacts",
            "- none (count: 0)",
            "## Future artifacts (not current milestone blockers)",
            "Read-only evaluation while creating this handoff: PASS",
            "check --project-root",
            "--milestone MIG-10",
            "If PASS:",
            "advance --project-root",
            "Do not treat future artifacts listed above as current milestone failures.",
        )
        if any(text not in gate_handoff for text in required_handoff_text):
            print("selftest: FAIL - Gate handoff does not separate current readiness and future work")
            return 1
        if "## First unfinished artifacts" in gate_handoff:
            print("selftest: FAIL - ambiguous unfinished-artifact section remains in Gate handoff")
            return 1
        next_result = subprocess.run(
            [
                sys.executable,
                str(mig / "tools" / "migration-workflow.py"),
                "next",
                "--project-root",
                str(root),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if next_result.returncode != 0 or not all(
            text in next_result.stdout
            for text in (
                "[GATE] MIG-10 read-only evaluation: PASS",
                "check ",
                "--milestone MIG-10",
                "check is read-only",
                "advance rechecks, writes the Gate result",
            )
        ):
            print("selftest: FAIL - next did not give the exact Gate check/persistence sequence")
            return 1
        handoff_status = read_json(mig / "migration-status.json")
        handoff_status["current"] = saved_current
        handoff_status["next"] = saved_next
        atomic_write_json(mig / "migration-status.json", handoff_status)

        exception_observation = mig / "evidence" / "EX-DB-001-observation.md"
        exception_resolution = mig / "evidence" / "EX-DB-001-resolution.md"
        exception_observation.write_text("database connection failed in isolated test\n", encoding="utf-8")
        exception_resolution.write_text("read-only connection restored and verified\n", encoding="utf-8")
        exception_open(
            root,
            "EX-DB-001",
            "Read-only inventory connection returned a connection error.",
            ["bomdd/migration/evidence/EX-DB-001-observation.md"],
            "unchanged",
            "unchanged",
            "unchanged",
        )
        blocked = read_json(mig / "migration-status.json")
        occurrence_id = str(blocked["blockers"][0])
        if blocked["current"]["milestone"] != "MIG-10" or not occurrence_id.startswith("EX-DB-001-"):
            print("selftest: FAIL - exception-open did not preserve position and register blocker")
            return 1
        try:
            complete_step(root, ["bomdd/migration/evidence/EX-DB-001-observation.md"])
            print("selftest: FAIL - blocker did not stop normal STEP work")
            return 1
        except WorkflowError:
            pass
        exception_safe_work(
            root,
            occurrence_id,
            "Review the frozen schema documentation without connecting to the database",
            "Self Test DB Custodian",
            "bomdd/migration/evidence/EX-DB-001-observation.md",
        )
        exception_resolve(
            root,
            occurrence_id,
            "Self Test DB Custodian",
            "The approved read-only connection was restored and the inventory query succeeded.",
            ["bomdd/migration/evidence/EX-DB-001-resolution.md"],
        )
        unblocked = read_json(mig / "migration-status.json")
        if unblocked.get("blockers") or unblocked.get("alternate_safe_work"):
            print("selftest: FAIL - exception resolution did not clear blocker and safe work")
            return 1
        if not unblocked.get("exception_history") or unblocked["exceptions"][-1].get("status") != "resolved":
            print("selftest: FAIL - resolved exception history is missing")
            return 1

        charter.write_text("# Tampered after acceptance\n", encoding="utf-8")
        tampered = check_gate(root, "MIG-00")
        mismatch_found = any(
            "content hash mismatch" in str(problem)
            for check in tampered["checks"]
            for problem in check.get("problems", [])
        )
        if tampered["gate"]["result"] != "fail" or not mismatch_found:
            print_gate(tampered)
            print("selftest: FAIL - accepted content mutation was not rejected")
            return 1

        change_open(
            root,
            "MIG-00",
            ["bomdd/00-charter.md", "bomdd/migration/migration-profile.json"],
            "selftest accepted correction",
        )
        opened = read_json(mig / "migration-status.json")
        if opened["current"]["milestone"] != "MIG-10" or opened["active_accepted_change"]["state"] != "opened":
            print("selftest: FAIL - accepted change did not pause and preserve the normal position")
            return 1
        if any(
            item.get("milestone") == "MIG-00" and item.get("status") == "approved"
            for item in opened.get("approvals", []) if isinstance(item, dict)
        ):
            print("selftest: FAIL - prior MIG-00 approval was not superseded")
            return 1
        try:
            complete_step(root, ["bomdd/00-charter.md"])
            print("selftest: FAIL - normal STEP work continued during accepted change")
            return 1
        except WorkflowError:
            pass

        retest = mig / "evidence" / "COR-MIG-00-retest.md"
        review = mig / "evidence" / "COR-MIG-00-reacceptance.md"
        reapproval = mig / "evidence" / "COR-MIG-00-reapproval.md"
        retest.write_text("regression passed\n", encoding="utf-8")
        review.write_text("changed charter reviewed\n", encoding="utf-8")
        reapproval.write_text("replacement approval\n", encoding="utf-8")
        change_retest(root, ["bomdd/migration/evidence/COR-MIG-00-retest.md"])
        change_accept(
            root, "Self Test Reviewer", ["bomdd/migration/evidence/COR-MIG-00-reacceptance.md"]
        )
        change_approve(
            root, "Migration Owner", "Self Test Owner",
            "bomdd/migration/evidence/COR-MIG-00-reapproval.md",
        )
        change_approve(
            root, "Operations Owner", "Self Test Owner",
            "bomdd/migration/evidence/COR-MIG-00-reapproval.md",
        )
        change_approve(
            root, "Customer Acceptance Owner", "Self Test Customer",
            "bomdd/migration/evidence/COR-MIG-00-reapproval.md",
        )
        change_close(root)
        closed = read_json(mig / "migration-status.json")
        if "active_accepted_change" in closed or closed["current"]["milestone"] != "MIG-10":
            print("selftest: FAIL - accepted change did not resume the preserved position")
            return 1
        if not closed.get("accepted_change_history") or not closed.get("gate_supersessions"):
            print("selftest: FAIL - accepted change history or Gate supersession is missing")
            return 1
        replacement_ref = closed["accepted_change_history"][-1].get("replacement_gate_ref")
        if not replacement_ref or not (root / replacement_ref).is_file():
            print("selftest: FAIL - replacement Gate result is missing")
            return 1
        revalidated = check_gate(root, "MIG-00")
        if revalidated["gate"]["result"] != "pass":
            print_gate(revalidated)
            print("selftest: FAIL - formally corrected content did not pass")
            return 1

        decision_status = read_json(mig / "migration-status.json")
        decision_status["current"] = {
            "milestone": "MIG-30",
            "step": "STEP-030",
            "work_item": "SELFTEST-DECISIONS",
            "action": "test scheduled DB decision",
            "owner": "Self Test Owner",
            "started_at": now_iso(),
        }
        decision_status["next"] = {"step": "STEP-031", "action": "要求と仕様を復元する"}
        atomic_write_json(mig / "migration-status.json", decision_status)
        decision_evidence = mig / "evidence" / "DEC-DB-SEMANTICS.md"
        decision_review = mig / "evidence" / "DECSET-DB-review.md"
        decision_evidence.write_text("DB semantics observed and approved\n", encoding="utf-8")
        decision_review.write_text("DB decision set reviewed\n", encoding="utf-8")
        incomplete_decision_gate = check_gate(root, "MIG-30")
        decision_checks = [
            item for item in incomplete_decision_gate.get("checks", [])
            if item.get("id") == "DECISION-SET:DECSET-DB-COMPATIBILITY"
        ]
        if not decision_checks or decision_checks[0].get("result") != "fail":
            print("selftest: FAIL - MIG-30 Gate did not reject the open due decision set")
            return 1
        try:
            complete_step(root, ["bomdd/migration/evidence/DECSET-DB-review.md"])
            print("selftest: FAIL - STEP-030 completed before its decision set was accepted")
            return 1
        except WorkflowError:
            pass
        try:
            decision_record(
                root,
                "DECSET-IMPLEMENTATION",
                "DEC-DOTNET",
                "Self Test Owner",
                "decided",
                ".NET selftest value",
                "bomdd/migration/evidence/DEC-DB-SEMANTICS.md",
            )
            print("selftest: FAIL - a MIG-40 decision was recorded early at MIG-30")
            return 1
        except WorkflowError:
            pass
        decision_record(
            root,
            "DECSET-DB-COMPATIBILITY",
            "DEC-DB-SEMANTICS",
            "Self Test Owner",
            "decided",
            "Preserve observed transaction, NULL, collation and time semantics",
            "bomdd/migration/evidence/DEC-DB-SEMANTICS.md",
        )
        accept_artifact(
            root,
            "ART-DB-TECH-DECISIONS",
            ["bomdd/migration/evidence/DECSET-DB-review.md"],
        )
        decision_status = read_json(mig / "migration-status.json")
        decision_problems = decision_set_gate_problems(
            root,
            decision_status,
            load_definition(mig),
            "DECSET-DB-COMPATIBILITY",
        )
        if decision_problems:
            print(f"selftest: FAIL - completed due decision set is invalid: {decision_problems[0]}")
            return 1
        future_gate = check_gate(root, "MIG-40")
        future_decision_checks = {
            item.get("id"): item for item in future_gate.get("checks", [])
            if str(item.get("id", "")).startswith("DECISION-SET:")
        }
        if (
            future_decision_checks.get("DECISION-SET:DECSET-DB-COMPATIBILITY", {}).get("result") != "pass"
            or future_decision_checks.get("DECISION-SET:DECSET-IMPLEMENTATION", {}).get("result") != "fail"
        ):
            print("selftest: FAIL - MIG-40 did not retain the prior DB decision and reject its open due set")
            return 1
        complete_step(root, ["bomdd/migration/evidence/DECSET-DB-review.md"])
        stepped_decision = read_json(mig / "migration-status.json")
        if stepped_decision["current"]["step"] != "STEP-031":
            print("selftest: FAIL - accepted decision set did not release STEP-030")
            return 1
        original_decision_evidence = decision_evidence.read_text(encoding="utf-8")
        decision_evidence.write_text("tampered decision evidence\n", encoding="utf-8")
        tampered_decisions = decision_set_gate_problems(
            root,
            stepped_decision,
            load_definition(mig),
            "DECSET-DB-COMPATIBILITY",
        )
        if not any("evidence hash mismatch" in problem for problem in tampered_decisions):
            print("selftest: FAIL - technical decision evidence mutation was not rejected")
            return 1
        tampered_future_gate = check_gate(root, "MIG-40")
        tampered_db_check = next(
            (
                item for item in tampered_future_gate.get("checks", [])
                if item.get("id") == "DECISION-SET:DECSET-DB-COMPATIBILITY"
            ),
            {},
        )
        if tampered_db_check.get("result") != "fail":
            print("selftest: FAIL - later Gate did not detect a prior decision evidence mutation")
            return 1
        decision_evidence.write_text(original_decision_evidence, encoding="utf-8")

        # Enterprise workstream controls: unique claim, WIP, ordered states,
        # local blockers, independent review, release and aggregate snapshot.
        workstream_review = mig / "evidence" / "workstream-register-review.md"
        workstream_review.write_text("workstream scope, ownership and dependencies reviewed\n", encoding="utf-8")
        register = {
            "schema": "bomdd-javafx-wpf-workstream-register/2.0",
            "program": "SelfTestProduct",
            "interface_change_policy": "producer-and-all-consumers-approve",
            "workstreams": [
                {"id": "WS-ALPHA", "name": "Alpha", "lead": "Lead Alpha", "reviewer": "Reviewer Alpha", "acceptance_delegate": "Delegate Alpha", "scope_refs": ["FUNC-A"], "depends_on": [], "interfaces_produced": ["IF-A"], "interfaces_consumed": [], "slices": [
                    {"id": "SLICE-A1", "risk_classes": ["db-read"], "refs": ["FUNC-A1"], "estimated_person_days": 5, "state": "planned"},
                    {"id": "SLICE-A2", "risk_classes": ["javafx-complex-ui"], "refs": ["FUNC-A2"], "estimated_person_days": 5, "state": "planned"},
                ]},
                {"id": "WS-BETA", "name": "Beta", "lead": "Lead Beta", "reviewer": "Reviewer Beta", "acceptance_delegate": "Delegate Beta", "scope_refs": ["FUNC-B"], "depends_on": ["WS-ALPHA"], "interfaces_produced": [], "interfaces_consumed": ["IF-A"], "slices": [
                    {"id": "SLICE-B1", "risk_classes": ["external-integration"], "refs": ["FUNC-B1"], "estimated_person_days": 5, "state": "planned"},
                ]},
            ],
        }
        atomic_write_json(mig / "workstream-register.json", register)
        ws_status = read_json(mig / "migration-status.json")
        ws_status["current"] = {"milestone": "MIG-20", "step": "STEP-026", "work_item": "SELFTEST-WORKSTREAM", "action": "register", "owner": "Self Test Owner", "started_at": now_iso()}
        atomic_write_json(mig / "migration-status.json", ws_status)
        accept_artifact(root, "ART-WORKSTREAM-REGISTER", ["bomdd/migration/evidence/workstream-register-review.md"])
        ws_status = read_json(mig / "migration-status.json")
        ws_status["current"] = {"milestone": "MIG-50", "step": "STEP-056", "work_item": "SELFTEST-FACTORY", "action": "initialize workstreams", "owner": "Self Test Owner", "started_at": now_iso()}
        atomic_write_json(mig / "migration-status.json", ws_status)
        workstream_init(root)
        slice_evidence = mig / "evidence" / "slice-state.md"
        slice_evidence.write_text("state transition independently evidenced\n", encoding="utf-8")
        evidence_ref = ["bomdd/migration/evidence/slice-state.md"]
        for ws_id, slice_id, lead in (("WS-ALPHA", "SLICE-A1", "Lead Alpha"), ("WS-ALPHA", "SLICE-A2", "Lead Alpha"), ("WS-BETA", "SLICE-B1", "Lead Beta")):
            slice_transition(root, ws_id, slice_id, "ready", lead, evidence_ref)
        slice_claim(root, "WS-ALPHA", "SLICE-A1", "Worker One", evidence_ref)
        try:
            slice_claim(root, "WS-ALPHA", "SLICE-A2", "Worker One", evidence_ref)
            print("selftest: FAIL - worker WIP limit was bypassed")
            return 1
        except WorkflowError:
            pass
        slice_block_change(root, "WS-ALPHA", "SLICE-A1", "LOCAL-001", "Worker One", evidence_ref, False)
        try:
            slice_transition(root, "WS-ALPHA", "SLICE-A1", "manufacturing", "Worker One", evidence_ref)
            print("selftest: FAIL - local blocker did not stop its slice")
            return 1
        except WorkflowError:
            pass
        slice_block_change(root, "WS-ALPHA", "SLICE-A1", "LOCAL-001", "Reviewer Alpha", evidence_ref, True)

        def finish_slice(ws_id: str, slice_id: str, worker: str, reviewer: str) -> None:
            slice_transition(root, ws_id, slice_id, "manufacturing", worker, evidence_ref)
            slice_transition(root, ws_id, slice_id, "self-accepted", worker, evidence_ref)
            for target in ("integrated", "compared", "accepted", "as-built"):
                slice_transition(root, ws_id, slice_id, target, reviewer, evidence_ref)

        finish_slice("WS-ALPHA", "SLICE-A1", "Worker One", "Reviewer Alpha")
        slice_claim(root, "WS-ALPHA", "SLICE-A2", "Worker One", evidence_ref)
        slice_release(root, "WS-ALPHA", "SLICE-A2", "Worker One", evidence_ref)
        slice_claim(root, "WS-ALPHA", "SLICE-A2", "Worker Two", evidence_ref)
        finish_slice("WS-ALPHA", "SLICE-A2", "Worker Two", "Delegate Alpha")
        slice_claim(root, "WS-BETA", "SLICE-B1", "Worker One", evidence_ref)
        finish_slice("WS-BETA", "SLICE-B1", "Worker One", "Reviewer Beta")
        create_workstream_snapshot(root)
        snapshot = read_json(mig / "workstream-snapshot.json")
        snapshot_evidence = [
            "bomdd/migration/workstream-register.json",
            "bomdd/migration/workstreams/WS-ALPHA/status.json",
            "bomdd/migration/workstreams/WS-BETA/status.json",
        ]
        snapshot_spec = {"path": "bomdd/migration/workstream-snapshot.json", "content_validation": "workstream-snapshot"}
        snapshot_problems = artifact_content_problems(root, snapshot_spec, snapshot_evidence)
        if snapshot.get("result") != "pass" or snapshot_problems:
            print(f"selftest: FAIL - enterprise workstream snapshot invalid: {snapshot_problems[:1]}")
            return 1
        original_slice_evidence = slice_evidence.read_text(encoding="utf-8")
        slice_evidence.write_text("tampered after slice acceptance\n", encoding="utf-8")
        _, alpha_status = load_workstream_status(root, "WS-ALPHA")
        if not any("hash mismatch" in item for item in workstream_status_problems(root, alpha_status)):
            print("selftest: FAIL - slice evidence mutation was not rejected")
            return 1
        slice_evidence.write_text(original_slice_evidence, encoding="utf-8")

        # Positive controls for every enterprise JSON Gate validator.
        generic = mig / "evidence" / "enterprise-validator-evidence.md"
        generic.write_text("measured, reviewed and accepted\n", encoding="utf-8")
        generic_ref = "bomdd/migration/evidence/enterprise-validator-evidence.md"
        portfolio = read_json(mig / "feasibility-portfolio.json")
        portfolio["source_version"] = "commit-abc"; portfolio["target_toolchain_candidate"] = ".NET 10 candidate"; portfolio["go_no_go"] = "go"
        for item in portfolio["items"]:
            item.update({"representative_ref": "FUNC-HARD", "result": "pass", "evidence": [generic_ref], "fallback": "retain bounded legacy component"})
        atomic_write_json(mig / "feasibility-portfolio.json", portfolio)

        inventory = read_json(mig / "code-inventory.json")
        inventory["source_commit"] = "commit-abc"; inventory["inventory_rule"] = "repository scanner v1"
        for index, item in enumerate(inventory["categories"]):
            item["files"] = 10; item["loc"] = 1000
        inventory["totals"] = {"files": 80, "loc": 8000, "modules": 2}
        inventory["modules"] = [{"id": "MOD-A", "path": "src/a", "files": 40, "loc": 4000, "owner": "Lead Alpha", "disposition": "migrate"}, {"id": "MOD-B", "path": "src/b", "files": 40, "loc": 4000, "owner": "Lead Beta", "disposition": "migrate"}]
        inventory["evidence"] = [generic_ref]
        atomic_write_json(mig / "code-inventory.json", inventory)

        nfr_contract = read_json(mig / "nonfunctional-acceptance-contract.json")
        for metric in nfr_contract["metrics"]:
            metric.update({"limit": 100, "workload": "LOAD-ONE", "dataset": "DATA-SMALL", "evidence_required": "measurement log"})
        atomic_write_json(mig / "nonfunctional-acceptance-contract.json", nfr_contract)

        contract = mig / "evidence" / "IF-A-contract.json"
        atomic_write_json(contract, {"schema": "selftest-interface/1", "operation": "read"})
        interfaces = {"schema": "bomdd-javafx-wpf-interface-register/2.0", "interfaces": [{"id": "IF-A", "version": "1", "producer_workstream": "WS-ALPHA", "consumer_workstreams": ["WS-BETA"], "contract_path": "bomdd/migration/evidence/IF-A-contract.json", "contract_sha256": file_sha256(contract), "compatibility": "backward-compatible-until-approved-cut", "contract_tests": ["CT-IF-A"], "owner": "Integration Owner", "status": "accepted"}]}
        atomic_write_json(mig / "workstream-interface-register.json", interfaces)

        ci = read_json(mig / "ci-readiness.json"); ci["clean_agent_id"] = "WIN-CLEAN-001"
        for item in ci["checks"]:
            item.update({"command": f"selftest {item['id']}", "result": "pass", "evidence": generic_ref})
        atomic_write_json(mig / "ci-readiness.json", ci)

        pilot = read_json(mig / "pilot-portfolio.json"); pilot["release_candidate"] = "RC-001"; pilot["clean_install_evidence"] = generic_ref; pilot["aggregate_result"] = "pass"
        pilot["items"] = [{"risk_class": risk, "slice_id": "SLICE-A1", "workstream_id": "WS-ALPHA", "status": "accepted", "evidence": [generic_ref], "approver": "Independent Approver"} for risk in pilot["required_risk_classes"]]
        atomic_write_json(mig / "pilot-portfolio.json", pilot)

        rc_manifest = mig / "evidence" / "release-candidate-manifest.json"
        atomic_write_json(rc_manifest, {"release_id": "RC-001", "source_commit": "commit-abc"})
        rc = read_json(mig / "release-candidate-acceptance.json"); rc["release_id"] = "RC-001"; rc["release_manifest_sha256"] = file_sha256(rc_manifest); rc["aggregate_result"] = "pass"
        for item in rc["checks"]: item.update({"result": "pass", "evidence": generic_ref})
        atomic_write_json(mig / "release-candidate-acceptance.json", rc)

        release_artifact = mig / "evidence" / "SelfTest.msi"; release_artifact.write_bytes(b"signed selftest release")
        sbom = mig / "evidence" / "sbom.json"; atomic_write_json(sbom, {"components": ["SelfTest"]})
        signed = read_json(mig / "signed-release-manifest.json")
        signed.update({"release_id": "REL-001", "version": "1.0.0", "source_commit": "commit-abc", "artifacts": [{"path": "bomdd/migration/evidence/SelfTest.msi", "sha256": file_sha256(release_artifact), "size": release_artifact.stat().st_size, "signature": "test-signature", "signature_verified": True}], "sbom": {"path": "bomdd/migration/evidence/sbom.json", "sha256": file_sha256(sbom)}, "certificate": {"subject": "CN=SelfTest", "thumbprint": "001122", "valid_from": "2026-01-01", "valid_to": "2027-01-01"}, "build_evidence": generic_ref, "promoted_from_release_candidate_sha256": file_sha256(rc_manifest), "approved_at": now_iso()})
        atomic_write_json(mig / "signed-release-manifest.json", signed)

        rollout = mig / "rollout-plan.md"; rollout.write_text("# Accepted rollout plan\nCanary then general cohort.\n", encoding="utf-8")
        cohort = read_json(mig / "cohort-deployment-ledger.json")
        cohort.update({"release_id": "REL-001", "rollout_plan_sha256": file_sha256(rollout), "cohorts": [{"id": "COHORT-CANARY", "customer_count": 2, "device_count": 20, "state": "accepted", "release_sha256": file_sha256(release_artifact), "go_no_go_evidence": generic_ref, "smoke_evidence": generic_ref, "db_reconciliation_evidence": generic_ref, "telemetry_evidence": generic_ref, "customer_acceptance_evidence": generic_ref, "blockers": []}], "in_scope_customer_count": 2, "accepted_customer_count": 2, "formally_deferred_customer_count": 0, "aggregate_result": "pass"})
        atomic_write_json(mig / "cohort-deployment-ledger.json", cohort)

        validation_cases = [
            ("feasibility-portfolio.json", "feasibility-portfolio", [generic_ref]),
            ("code-inventory.json", "code-inventory", [generic_ref]),
            ("nonfunctional-acceptance-contract.json", "nfr-contract", []),
            ("workstream-interface-register.json", "interface-register", ["bomdd/migration/evidence/IF-A-contract.json"]),
            ("ci-readiness.json", "ci-readiness", [generic_ref]),
            ("pilot-portfolio.json", "pilot-portfolio", [generic_ref]),
            ("release-candidate-acceptance.json", "rc-acceptance", ["bomdd/migration/evidence/release-candidate-manifest.json", generic_ref]),
            ("signed-release-manifest.json", "signed-release", ["bomdd/migration/evidence/SelfTest.msi", "bomdd/migration/evidence/sbom.json", generic_ref]),
            ("cohort-deployment-ledger.json", "cohort-ledger", ["bomdd/migration/rollout-plan.md", generic_ref]),
        ]
        for filename, kind, evidence_paths in validation_cases:
            spec = {"path": f"bomdd/migration/{filename}", "content_validation": kind}
            problems = artifact_content_problems(root, spec, evidence_paths)
            if problems:
                print(f"selftest: FAIL - {kind} positive control: {problems[0]}")
                return 1
        failed_pilot = read_json(mig / "pilot-portfolio.json"); failed_pilot["aggregate_result"] = "open"
        atomic_write_json(mig / "pilot-portfolio.json", failed_pilot)
        if not artifact_content_problems(root, {"path": "bomdd/migration/pilot-portfolio.json", "content_validation": "pilot-portfolio"}, [generic_ref]):
            print("selftest: FAIL - pilot negative control unexpectedly passed")
            return 1
        handoff(root)
        if not list((mig / "handoffs").glob("handoff-*.md")):
            print("selftest: FAIL - handoff was not generated")
            return 1
    print("selftest: PASS")
    return 0


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="legacy-wpf-rdb artifact workflow")
    parser.add_argument("--selftest", action="store_true",
                        help="run isolated positive and negative controls")
    sub = parser.add_subparsers(dest="command")

    p_init = sub.add_parser("init", help="activate the scenario in one existing project")
    p_init.add_argument("--project-root", required=True)
    p_init.add_argument("--product", required=True)

    for name in ("status", "next", "check", "advance", "handoff"):
        p = sub.add_parser(name)
        p.add_argument("--project-root", default=".")
        if name == "check":
            p.add_argument("--milestone", default=None)

    p_complete = sub.add_parser("complete-step", help="record evidence and move to the next defined STEP")
    p_complete.add_argument("--project-root", default=".")
    p_complete.add_argument("--evidence", action="append", required=True)

    p_accept = sub.add_parser("accept-artifact", help="accept one current-milestone artifact with evidence")
    p_accept.add_argument("--project-root", default=".")
    p_accept.add_argument("--artifact", required=True)
    p_accept.add_argument("--evidence", action="append", required=True)

    p_approve = sub.add_parser("approve", help="record one required current-milestone approval")
    p_approve.add_argument("--project-root", default=".")
    p_approve.add_argument("--role", required=True)
    p_approve.add_argument("--approver", required=True)
    p_approve.add_argument("--evidence", required=True)

    p_seal = sub.add_parser(
        "seal-milestone", help="add SHA-256 seals to an existing accepted milestone after explicit review"
    )
    p_seal.add_argument("--project-root", default=".")
    p_seal.add_argument("--milestone", required=True)
    p_seal.add_argument("--reviewer", required=True)
    p_seal.add_argument("--review-evidence", required=True)

    p_change_open = sub.add_parser(
        "change-open", help="open the formal workflow for changing sealed accepted content"
    )
    p_change_open.add_argument("--project-root", default=".")
    p_change_open.add_argument("--milestone", required=True)
    p_change_open.add_argument("--changed-file", action="append", required=True)
    p_change_open.add_argument("--reason", required=True)

    p_change_retest = sub.add_parser(
        "change-retest", help="record regression/retest evidence for the active accepted change"
    )
    p_change_retest.add_argument("--project-root", default=".")
    p_change_retest.add_argument("--evidence", action="append", required=True)

    p_change_accept = sub.add_parser(
        "change-accept", help="reaccept the affected artifact set after retest"
    )
    p_change_accept.add_argument("--project-root", default=".")
    p_change_accept.add_argument("--reviewer", required=True)
    p_change_accept.add_argument("--evidence", action="append", required=True)

    p_change_approve = sub.add_parser(
        "change-approve", help="record one required fresh approval for the active accepted change"
    )
    p_change_approve.add_argument("--project-root", default=".")
    p_change_approve.add_argument("--role", required=True)
    p_change_approve.add_argument("--approver", required=True)
    p_change_approve.add_argument("--evidence", required=True)

    p_change_close = sub.add_parser(
        "change-close", help="run the replacement Gate and resume the paused normal position"
    )
    p_change_close.add_argument("--project-root", default=".")

    p_exception_catalog = sub.add_parser(
        "exception-catalog", help="list frozen exception IDs and their default actions"
    )
    p_exception_catalog.add_argument("--project-root", default=".")
    p_exception_catalog.add_argument("--query", default=None)

    p_exception_open = sub.add_parser(
        "exception-open", help="create an exception record and register its blocker/non-blocker state"
    )
    p_exception_open.add_argument("--project-root", default=".")
    p_exception_open.add_argument("--catalog-id", required=True)
    p_exception_open.add_argument("--symptom", required=True)
    p_exception_open.add_argument("--evidence", action="append", required=True)
    boundary_choices = ("unchanged", "changed", "unknown")
    p_exception_open.add_argument("--production-db", choices=boundary_choices, required=True)
    p_exception_open.add_argument("--baseline-fixture", choices=boundary_choices, required=True)
    p_exception_open.add_argument("--current-source", choices=boundary_choices, required=True)

    p_exception_safe = sub.add_parser(
        "exception-safe-work", help="authorize one bounded alternate action while a blocker remains open"
    )
    p_exception_safe.add_argument("--project-root", default=".")
    p_exception_safe.add_argument("--exception", required=True)
    p_exception_safe.add_argument("--work", required=True)
    p_exception_safe.add_argument("--authorizer", required=True)
    p_exception_safe.add_argument("--evidence", required=True)

    p_exception_resolve = sub.add_parser(
        "exception-resolve", help="resolve one open exception with sealed evidence and resume instruction"
    )
    p_exception_resolve.add_argument("--project-root", default=".")
    p_exception_resolve.add_argument("--exception", required=True)
    p_exception_resolve.add_argument("--resolver", required=True)
    p_exception_resolve.add_argument("--resolution", required=True)
    p_exception_resolve.add_argument("--evidence", action="append", required=True)

    p_decision_status = sub.add_parser(
        "decision-status", help="show technical decision sets at their scheduled milestones"
    )
    p_decision_status.add_argument("--project-root", default=".")

    p_decision_record = sub.add_parser(
        "decision-record", help="record one due technical decision with owner evidence"
    )
    p_decision_record.add_argument("--project-root", default=".")
    p_decision_record.add_argument("--set", required=True)
    p_decision_record.add_argument("--decision", required=True)
    p_decision_record.add_argument("--decider", required=True)
    p_decision_record.add_argument("--status", choices=("decided", "not-applicable"), required=True)
    p_decision_record.add_argument("--value", required=True)
    p_decision_record.add_argument("--evidence", required=True)

    p_adopt_decisions = sub.add_parser(
        "adopt-decision-layout",
        help="one-time upgrade from legacy profile decisions to scheduled decision artifacts",
    )
    p_adopt_decisions.add_argument("--project-root", default=".")
    p_adopt_decisions.add_argument("--reviewer", required=True)
    p_adopt_decisions.add_argument("--review-evidence", required=True)

    p_ws_init = sub.add_parser("workstream-init", help="materialize status files from the accepted workstream register")
    p_ws_init.add_argument("--project-root", default=".")

    p_ws_status = sub.add_parser("workstream-status", help="show aggregate or selected workstream/slice state")
    p_ws_status.add_argument("--project-root", default=".")
    p_ws_status.add_argument("--workstream", default=None)

    p_slice_claim = sub.add_parser("slice-claim", help="claim exactly one ready slice subject to worker WIP limit")
    p_slice_claim.add_argument("--project-root", default=".")
    p_slice_claim.add_argument("--workstream", required=True)
    p_slice_claim.add_argument("--slice", required=True)
    p_slice_claim.add_argument("--worker", required=True)
    p_slice_claim.add_argument("--evidence", action="append", required=True)

    p_slice_transition = sub.add_parser("slice-transition", help="advance one slice by exactly one allowed evidenced state")
    p_slice_transition.add_argument("--project-root", default=".")
    p_slice_transition.add_argument("--workstream", required=True)
    p_slice_transition.add_argument("--slice", required=True)
    p_slice_transition.add_argument("--to", required=True, choices=[state for state in SLICE_STATES if state != "claimed"])
    p_slice_transition.add_argument("--actor", required=True)
    p_slice_transition.add_argument("--evidence", action="append", required=True)

    p_slice_release = sub.add_parser("slice-release", help="return an abandoned claimed/manufacturing slice to ready")
    p_slice_release.add_argument("--project-root", default=".")
    p_slice_release.add_argument("--workstream", required=True)
    p_slice_release.add_argument("--slice", required=True)
    p_slice_release.add_argument("--actor", required=True)
    p_slice_release.add_argument("--evidence", action="append", required=True)

    for name, help_text in (("slice-block", "record a local slice blocker without stopping unrelated workstreams"), ("slice-unblock", "resolve a local slice blocker with evidence")):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("--project-root", default=".")
        p.add_argument("--workstream", required=True)
        p.add_argument("--slice", required=True)
        p.add_argument("--blocker", required=True)
        p.add_argument("--actor", required=True)
        p.add_argument("--evidence", action="append", required=True)

    p_ws_snapshot = sub.add_parser("workstream-snapshot", help="seal and aggregate every workstream for MIG-70")
    p_ws_snapshot.add_argument("--project-root", default=".")
    args = parser.parse_args(argv)
    try:
        if args.selftest:
            return selftest()
        if args.command is None:
            parser.error("a command is required unless --selftest is used")
        if args.command == "init":
            initialize(Path(args.project_root), args.product)
        elif args.command == "status":
            show_status(Path(args.project_root))
        elif args.command == "next":
            show_next(Path(args.project_root))
        elif args.command == "check":
            result = check_gate(Path(args.project_root), args.milestone)
            print_gate(result)
            return 0 if result["gate"]["result"] == "pass" else 2
        elif args.command == "advance":
            advance(Path(args.project_root))
        elif args.command == "handoff":
            handoff(Path(args.project_root))
        elif args.command == "complete-step":
            complete_step(Path(args.project_root), args.evidence)
        elif args.command == "accept-artifact":
            accept_artifact(Path(args.project_root), args.artifact, args.evidence)
        elif args.command == "approve":
            approve_milestone(Path(args.project_root), args.role, args.approver, args.evidence)
        elif args.command == "seal-milestone":
            seal_milestone(
                Path(args.project_root), args.milestone, args.reviewer, args.review_evidence
            )
        elif args.command == "change-open":
            change_open(Path(args.project_root), args.milestone, args.changed_file, args.reason)
        elif args.command == "change-retest":
            change_retest(Path(args.project_root), args.evidence)
        elif args.command == "change-accept":
            change_accept(Path(args.project_root), args.reviewer, args.evidence)
        elif args.command == "change-approve":
            change_approve(
                Path(args.project_root), args.role, args.approver, args.evidence
            )
        elif args.command == "change-close":
            change_close(Path(args.project_root))
        elif args.command == "exception-catalog":
            show_exception_catalog(Path(args.project_root), args.query)
        elif args.command == "exception-open":
            exception_open(
                Path(args.project_root),
                args.catalog_id,
                args.symptom,
                args.evidence,
                args.production_db,
                args.baseline_fixture,
                args.current_source,
            )
        elif args.command == "exception-safe-work":
            exception_safe_work(
                Path(args.project_root),
                args.exception,
                args.work,
                args.authorizer,
                args.evidence,
            )
        elif args.command == "exception-resolve":
            exception_resolve(
                Path(args.project_root),
                args.exception,
                args.resolver,
                args.resolution,
                args.evidence,
            )
        elif args.command == "decision-status":
            show_decision_status(Path(args.project_root))
        elif args.command == "decision-record":
            decision_record(
                Path(args.project_root),
                args.set,
                args.decision,
                args.decider,
                args.status,
                args.value,
                args.evidence,
            )
        elif args.command == "adopt-decision-layout":
            adopt_decision_layout(
                Path(args.project_root), args.reviewer, args.review_evidence
            )
        elif args.command == "workstream-init":
            workstream_init(Path(args.project_root))
        elif args.command == "workstream-status":
            show_workstream_status(Path(args.project_root), args.workstream)
        elif args.command == "slice-claim":
            slice_claim(Path(args.project_root), args.workstream, args.slice, args.worker, args.evidence)
        elif args.command == "slice-transition":
            slice_transition(Path(args.project_root), args.workstream, args.slice, args.to, args.actor, args.evidence)
        elif args.command == "slice-release":
            slice_release(Path(args.project_root), args.workstream, args.slice, args.actor, args.evidence)
        elif args.command in {"slice-block", "slice-unblock"}:
            slice_block_change(Path(args.project_root), args.workstream, args.slice, args.blocker, args.actor, args.evidence, args.command == "slice-unblock")
        elif args.command == "workstream-snapshot":
            create_workstream_snapshot(Path(args.project_root))
        return 0
    except WorkflowError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
