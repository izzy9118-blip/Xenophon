from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = ROOT / "manifest.yaml"
MECHANISM_PATH = ROOT / "speech/speech-mechanism-r2.yaml"
SCHEMA_PATH = ROOT / "federation/contracts/ministerial-report.schema.v1.3.0.json"
CORPUS_INDEX_PATH = ROOT / "corpus/index.yaml"
REPOSITORY = "izzy9118-blip/Xenophon"
MINISTER_ACTOR = "xenophon"
MANIFEST_VERSION = "1.71.0"
ADAPTER_ID = "XEN-MINISTER-ADAPTER-001-R2"
ALLOWED_MODES = {"reasoned", "outside_my_ground"}
ALLOWED_LAYERS = {
    "primary_showing",
    "strauss_explicit_argument",
    "kojeve_explicit_argument",
    "strauss_restatement_explicit_argument",
    "correspondence_documentary_showing",
    "editorial_apparatus_finding",
    "controlled_synthetic_inference",
    "unresolved_question",
}
REPORT_KIND = {
    "primary_showing": "documented_finding",
    "strauss_explicit_argument": "documented_finding",
    "kojeve_explicit_argument": "documented_finding",
    "strauss_restatement_explicit_argument": "documented_finding",
    "correspondence_documentary_showing": "documented_finding",
    "editorial_apparatus_finding": "documented_finding",
    "controlled_synthetic_inference": "supported_inference",
    "unresolved_question": "unresolved_uncertainty",
}
EXPECTED_OPERATIONAL_PAIRS = {
    ("XEN-WIT-PRI-001", "XEN-SRC-PRI-001"),
    ("XEN-WIT-SEC-001", "XEN-SRC-SEC-001"),
    ("XEN-WIT-COMP-001", "XEN-SRC-PRI-002"),
    ("XEN-WIT-COMP-001", "XEN-SRC-SEC-002"),
    ("XEN-WIT-COMP-001", "XEN-SRC-SEC-003"),
    ("XEN-WIT-COMP-001", "XEN-SRC-SEC-004"),
    ("XEN-WIT-COMP-001", "XEN-SRC-SEC-005"),
    ("XEN-WIT-COMP-001", "XEN-SRC-SEC-006"),
}
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


class AdapterError(ValueError):
    """Raised when a request exceeds the Xenophon minister contract."""


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise AdapterError(f"Expected mapping in {path}")
    return data


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise AdapterError(f"Expected object in {path}")
    return data


def resolve_repository_path(relative: str) -> Path:
    if not isinstance(relative, str) or not relative:
        raise AdapterError("repository path must be a non-empty string")
    path = (ROOT / relative).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise AdapterError(f"path escapes repository root: {relative}") from exc
    if not path.is_file():
        raise AdapterError(f"repository file does not exist: {relative}")
    return path


def sha256_file(relative: str) -> str:
    return hashlib.sha256(resolve_repository_path(relative).read_bytes()).hexdigest()


def git_show_text(commit: str, relative: str) -> str:
    if not SHA40.fullmatch(commit):
        raise AdapterError("repository commit must be a lowercase 40-character SHA")
    if relative.startswith("/") or ".." in Path(relative).parts:
        raise AdapterError("invalid git object path")
    process = subprocess.run(
        ["git", "show", f"{commit}:{relative}"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if process.returncode:
        raise AdapterError(f"pinned commit does not contain {relative}")
    return process.stdout


def validate_repository_pin(pin: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if pin.get("repository") != REPOSITORY:
        errors.append("repository_pin.repository mismatch")
    commit = str(pin.get("commit", ""))
    if not SHA40.fullmatch(commit):
        errors.append("repository_pin.commit must be a lowercase 40-character SHA")
        return errors
    if pin.get("manifest_path") != "manifest.yaml":
        errors.append("repository_pin.manifest_path must be manifest.yaml")
        return errors
    try:
        manifest = yaml.safe_load(git_show_text(commit, "manifest.yaml"))
        git_show_text(commit, "adapter.py")
    except AdapterError as exc:
        errors.append(str(exc))
        return errors
    if not isinstance(manifest, dict) or manifest.get("version") != pin.get("manifest_version"):
        errors.append("repository_pin manifest version does not match pinned commit")
    elif manifest.get("minister_adapter", {}).get("id") != ADAPTER_ID:
        errors.append("repository_pin does not contain the R2 adapter manifest")
    else:
        mechanism_path = manifest.get("minister_adapter", {}).get("speech_mechanism_path")
        try:
            git_show_text(commit, str(mechanism_path))
        except AdapterError as exc:
            errors.append(str(exc))
    return errors


def registered_witness_pairs() -> set[tuple[str, str]]:
    result: set[tuple[str, str]] = set()
    for source in load_yaml(CORPUS_INDEX_PATH).get("sources", []):
        if not isinstance(source, dict):
            continue
        source_id = source.get("id")
        for witness_id in source.get("witness_ids", []):
            if isinstance(source_id, str) and isinstance(witness_id, str):
                result.add((witness_id, source_id))
    return result


def operational_source_lines(manifest: dict[str, Any]) -> dict[str, set[tuple[str, str]]]:
    result: dict[str, set[tuple[str, str]]] = {}
    lines = manifest.get("source_policy", {}).get("operational_source_lines", {})
    if not isinstance(lines, dict):
        return result
    for line_id, line in lines.items():
        if not isinstance(line_id, str) or not isinstance(line, dict):
            continue
        pairs: set[tuple[str, str]] = set()
        for source in line.get("sources", []):
            if not isinstance(source, dict):
                continue
            witness_id = source.get("witness_id")
            source_id = source.get("source_id")
            if isinstance(witness_id, str) and isinstance(source_id, str):
                pairs.add((witness_id, source_id))
        result[line_id] = pairs
    return result


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if manifest.get("repository") != REPOSITORY:
        errors.append("manifest repository mismatch")
    if manifest.get("version") != MANIFEST_VERSION:
        errors.append(f"manifest version must be {MANIFEST_VERSION}")
    if manifest.get("state") != "OPERATIONAL_OWNER_AUTHORIZED_MULTI_WORK_RESEARCH":
        errors.append("manifest operational state mismatch")
    adapter = manifest.get("minister_adapter", {})
    if adapter.get("id") != ADAPTER_ID:
        errors.append("minister adapter R2 identity mismatch")
    if adapter.get("owner_adopted") is not True or adapter.get("operational_authorization") is not True:
        errors.append("adapter R2 lacks owner operational authorization")
    if adapter.get("sanctum_registration_authorized") is not True:
        errors.append("adapter is not authorized for exact-commit Sanctum registration")
    if adapter.get("assembly_dispatch_authorized") is not False:
        errors.append("Assembly dispatch must remain blocked until Sanctum registration")
    greek = manifest.get("source_policy", {}).get("greek_language_review", {})
    if greek.get("status") != "DEFERRED_BY_OWNER" or greek.get("greek_dependent_claims") != "PROHIBITED":
        errors.append("Greek-language jurisdiction mismatch")
    if manifest.get("governance_gates", {}).get("artificial_intelligence_self_certification_prohibited") is not True:
        errors.append("AI self-certification prohibition missing")
    source_lines = operational_source_lines(manifest)
    if set(source_lines) != {"anabasis", "hieron_on_tyranny"}:
        errors.append("operational source-line identities mismatch")
    elif set().union(*source_lines.values()) != EXPECTED_OPERATIONAL_PAIRS:
        errors.append("operational source and witness pairs mismatch")
    if not EXPECTED_OPERATIONAL_PAIRS.issubset(registered_witness_pairs()):
        errors.append("operational source policy contains an unregistered witness pair")
    boundary = adapter.get("hieron_derivation_boundary")
    if boundary != "governance/derivation-boundaries/2026-08-10-hieron-on-tyranny-operational-boundary.yaml":
        errors.append("Hieron operational derivation boundary missing")
    return errors


def validate_mechanism(mechanism: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if [item.get("id") for item in mechanism.get("registers", [])] != [f"XEN-REGISTER-{i:03d}" for i in range(1, 7)]:
        errors.append("six-register order mismatch")
    if [item.get("id") for item in mechanism.get("guards", [])] != [f"XEN-GUARD-{i:03d}" for i in range(1, 5)]:
        errors.append("four-guard order mismatch")
    contract = mechanism.get("constitutional_contract", {})
    for field in (
        "identical_briefing_required",
        "tailored_briefing_prohibited",
        "committed_judgment_required",
        "standing_unresolved_questions_required",
        "self_reference_prohibited",
        "evidence_typing_required",
        "artificial_intelligence_self_certification_prohibited",
        "source_role_non_absorption_required",
        "explicit_source_line_selection_required",
    ):
        if contract.get(field) is not True:
            errors.append(f"mechanism safeguard missing: {field}")
    return errors


def _require_string(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} must be a non-empty string")


def validate_speech_request(request: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if request.get("record_type") != "xenophon_speech_request":
        errors.append("record_type must be xenophon_speech_request")
    for field in ("request_id", "report_id", "question", "requested_output", "direct_answer", "termination_status"):
        _require_string(request.get(field), field, errors)
    if request.get("mode") not in ALLOWED_MODES:
        errors.append("mode must be reasoned or outside_my_ground")

    inquiry = request.get("inquiry_ref", {})
    if not isinstance(inquiry, dict):
        errors.append("inquiry_ref must be a mapping")
    else:
        if not SHA256.fullmatch(str(inquiry.get("envelope_sha256", ""))):
            errors.append("inquiry_ref.envelope_sha256 must be a lowercase SHA-256")
        else:
            try:
                if sha256_file(str(inquiry.get("path", ""))) != inquiry["envelope_sha256"]:
                    errors.append("inquiry envelope hash does not match referenced bytes")
            except AdapterError as exc:
                errors.append(str(exc))

    briefing = request.get("briefing", {})
    if not isinstance(briefing, dict):
        errors.append("briefing must be a mapping")
    else:
        if briefing.get("identical_for_all_ministers") is not True:
            errors.append("briefing must be identical for all ministers")
        if briefing.get("tailored_feed") is not False:
            errors.append("tailored briefing feeds are prohibited")
        if not SHA256.fullmatch(str(briefing.get("sha256", ""))):
            errors.append("briefing.sha256 must be a lowercase SHA-256")
        else:
            try:
                if sha256_file(str(briefing.get("path", ""))) != briefing["sha256"]:
                    errors.append("briefing hash does not match referenced bytes")
            except AdapterError as exc:
                errors.append(str(exc))

    pin = request.get("repository_pin")
    if isinstance(pin, dict):
        errors.extend(validate_repository_pin(pin))
    else:
        errors.append("repository_pin must be a mapping")
    if request.get("self_reference_as_authority") is not False:
        errors.append("self-reference as authority is prohibited")
    if request.get("claims_greek_textual_authority") is not False:
        errors.append("Greek textual authority may not be claimed")
    if request.get("artificial_intelligence_self_certification") is not False:
        errors.append("artificial-intelligence self-certification is prohibited")

    manifest = load_yaml(MANIFEST_PATH)
    available_lines = operational_source_lines(manifest)
    selected_lines = request.get("source_lines")
    if not isinstance(selected_lines, list) or not selected_lines:
        errors.append("source_lines must be a non-empty list")
        selected_lines = []
    elif any(line not in available_lines for line in selected_lines):
        errors.append("source_lines contains an unauthorized source line")
    authorized_pairs: set[tuple[str, str]] = set()
    for line in selected_lines:
        authorized_pairs.update(available_lines.get(line, set()))
    registered_pairs = registered_witness_pairs()
    used_lines: set[str] = set()
    used_pairs: set[tuple[str, str]] = set()
    findings = request.get("findings")
    if not isinstance(findings, list) or not findings:
        errors.append("findings must be a non-empty list")
        findings = []
    seen_layers: set[str] = set()
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            errors.append(f"findings[{index}] must be a mapping")
            continue
        layer = finding.get("evidence_layer")
        if layer not in ALLOWED_LAYERS:
            errors.append(f"findings[{index}].evidence_layer is invalid")
        else:
            seen_layers.add(layer)
        grounds = finding.get("grounds")
        if not isinstance(grounds, list) or not grounds:
            errors.append(f"findings[{index}].grounds must be a non-empty list")
            continue
        for ground_index, ground in enumerate(grounds):
            if not isinstance(ground, dict):
                errors.append(f"findings[{index}].grounds[{ground_index}] must be a mapping")
                continue
            pair = (str(ground.get("witness_id")), str(ground.get("source_id")))
            used_pairs.add(pair)
            if pair not in registered_pairs:
                errors.append(f"findings[{index}].grounds[{ground_index}] witness/source pair is not registered")
            elif pair not in authorized_pairs:
                errors.append(f"findings[{index}].grounds[{ground_index}] witness/source pair is not operationally authorized")
            for line_id in selected_lines:
                if pair in available_lines.get(line_id, set()):
                    used_lines.add(line_id)
            try:
                resolve_repository_path(str(ground.get("path", "")))
            except AdapterError as exc:
                errors.append(str(exc))
    if request.get("mode") == "reasoned":
        for required_layer in ("primary_showing", "controlled_synthetic_inference"):
            if required_layer not in seen_layers:
                errors.append(f"reasoned requests require {required_layer}")
    if "unresolved_question" not in seen_layers:
        errors.append("at least one unresolved question must remain standing")
    for line_id in selected_lines:
        if line_id not in used_lines:
            errors.append(f"selected source line has no evidence: {line_id}")
    if "hieron_on_tyranny" in selected_lines:
        if ("XEN-WIT-COMP-001", "XEN-SRC-PRI-002") not in used_pairs:
            errors.append("Hieron source line requires primary Hieron evidence")
        later_hieron_ids = {f"XEN-SRC-SEC-{number:03d}" for number in range(2, 7)}
        if not any(source_id in later_hieron_ids for _, source_id in used_pairs):
            errors.append("Hieron source line requires at least one distinct later source role")
    if not isinstance(request.get("standing_unresolved_questions"), list) or not request["standing_unresolved_questions"]:
        errors.append("standing_unresolved_questions must be a non-empty list")
    if not isinstance(request.get("contradictions_and_dissent"), list):
        errors.append("contradictions_and_dissent must be a list")
    return errors


def build_candidate_report(request: dict[str, Any]) -> dict[str, Any]:
    errors = validate_speech_request(request)
    if errors:
        raise AdapterError("; ".join(errors))
    pin = request["repository_pin"]
    evidence: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    propositions: list[dict[str, Any]] = []
    for finding in request["findings"]:
        for ground in finding["grounds"]:
            key = (ground["witness_id"], ground["source_id"], ground["path"])
            if key not in seen:
                seen.add(key)
                evidence.append({
                    "witness_id": ground["witness_id"],
                    "source_id": ground["source_id"],
                    "repository_commit": pin["commit"],
                    "path": ground["path"],
                    "evidence_layer": finding["evidence_layer"],
                    "ref": ground.get("ref"),
                })
        propositions.append({
            "kind": REPORT_KIND[finding["evidence_layer"]],
            "claim": finding["statement"],
            "grounds": finding["grounds"],
            "evidence_layer": finding["evidence_layer"],
            "source_location": finding["source_location"],
            "confidence": finding["confidence"],
            "alternatives_considered": finding["alternatives_considered"],
        })
    uncertainties = [item.get("question", str(item)) if isinstance(item, dict) else str(item) for item in request["standing_unresolved_questions"]]
    report = {
        "record_type": "ministerial_report",
        "id": request["report_id"],
        "report_id": request["report_id"],
        "report_status": "DRAFT_PENDING_MINISTER_REPOSITORY_VALIDATION",
        "inquiry_ref": request["inquiry_ref"],
        "minister": {"actor": MINISTER_ACTOR, "manifest_commit": pin["commit"], "title": "Xenophon Minister"},
        "mode": request["mode"],
        "repository": {"full_name": REPOSITORY, "git_commit": pin["commit"]},
        "governing_manifest": {
            "path": pin["manifest_path"],
            "version": pin["manifest_version"],
            "derivation_authority": {
                "status": "OWNER_ADOPTED_MULTI_WORK_DERIVATION",
                "source_lines": request["source_lines"],
            },
            "derivation_authorities": [
                {
                    "source_line": "anabasis",
                    "ref": "governance/owner-reviews/2026-08-01-strauss-guided-controlled-synthesis-r1-in-depth-review.yaml",
                    "id": "XEN-OWNER-REVIEW-010",
                    "status": "OWNER_ADOPTED_SYNTHESIS",
                },
                {
                    "source_line": "hieron_on_tyranny",
                    "ref": "governance/derivation-boundaries/2026-08-10-hieron-on-tyranny-operational-boundary.yaml",
                    "id": "XEN-HIERON-OT-DERIVATION-BOUNDARY-001",
                    "status": "OWNER_AUTHORIZED_OPERATIONAL_DERIVATION",
                },
            ],
            "adapter_operational_authority": {
                "ref": "governance/repository-authorization-r2.yaml",
                "id": "XENOPHON-AUTH-002",
                "status": "OWNER_AUTHORIZED_OPERATIONAL_INTERFACE",
            },
        },
        "direct_answer": request["direct_answer"],
        "pedagogical_path": request["pedagogical_path"],
        "evidence": evidence,
        "propositions": propositions,
        "uncertainties": uncertainties,
        "dissent": request["contradictions_and_dissent"],
        "jurisdiction": {
            "current": "CONTROLLED_MULTI_WORK_ENGLISH_WITNESS_PRIMARY_SECONDARY_SYNTHESIS",
            "source_lines": request["source_lines"],
            "greek_language_review": "DEFERRED_BY_OWNER_NOT_CURRENT_BLOCKER",
            "greek_dependent_claims": "PROHIBITED",
        },
        "termination": {
            "status": request["termination_status"],
            "authoritative_effect": "NONE_UNTIL_REPORT_OWNER_CERTIFICATION_AND_SANCTUM_ACCEPTANCE",
            "presidential_synthesis": "NOT_PERFORMED",
        },
        "provenance": {
            "produced_by": {"actor": "xenophon-adapter-r2-owner-authorized", "repo": REPOSITORY, "commit": pin["commit"]},
            "consumed_records": [
                {"ref": "manifest.yaml", "commit": pin["commit"]},
                {"ref": "XEN-HIERON-OT-DERIVATION-BOUNDARY-001", "path": "governance/derivation-boundaries/2026-08-10-hieron-on-tyranny-operational-boundary.yaml"},
                {"ref": request["inquiry_ref"]["ref"], "sha256": request["inquiry_ref"]["envelope_sha256"]},
                {"ref": request["briefing"]["briefing_id"], "sha256": request["briefing"]["sha256"]},
            ],
        },
        "certification_status": "PENDING_OWNER_CERTIFICATION",
        "artificial_intelligence_self_certification": "PROHIBITED",
    }
    schema_errors = sorted(Draft202012Validator(load_json(SCHEMA_PATH)).iter_errors(report), key=lambda item: list(item.path))
    if schema_errors:
        raise AdapterError("schema validation failed: " + "; ".join(error.message for error in schema_errors))
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate and render Xenophon ministerial reports")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate-interface")
    validate_request = sub.add_parser("validate-request")
    validate_request.add_argument("path", type=Path)
    build = sub.add_parser("build-report")
    build.add_argument("path", type=Path)
    build.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.command == "validate-interface":
        errors = validate_manifest(load_yaml(MANIFEST_PATH)) + validate_mechanism(load_yaml(MECHANISM_PATH))
        if errors:
            print("; ".join(errors), file=sys.stderr)
            return 1
        print("Xenophon owner-authorized adapter interface validation passed")
        return 0
    request = load_yaml(args.path)
    if args.command == "validate-request":
        errors = validate_speech_request(request)
        if errors:
            print("; ".join(errors), file=sys.stderr)
            return 1
        print("Xenophon speech request validation passed")
        return 0
    report = build_candidate_report(request)
    rendered = yaml.safe_dump(report, sort_keys=False, allow_unicode=True)
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
