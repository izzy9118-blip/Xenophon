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
MECHANISM_PATH = ROOT / "speech/speech-mechanism.yaml"
SCHEMA_PATH = ROOT / "federation/contracts/ministerial-report.schema.v1.3.0.json"
CORPUS_INDEX_PATH = ROOT / "corpus/index.yaml"
REPOSITORY = "izzy9118-blip/Xenophon"
MANIFEST_VERSION = "1.69.0"
MINISTER_ACTOR = "xenophon"
ALLOWED_MODES = {"reasoned", "outside_my_ground"}
ALLOWED_LAYERS = {
    "primary_showing",
    "strauss_explicit_argument",
    "controlled_synthetic_inference",
    "unresolved_question",
}
REPORT_KIND = {
    "primary_showing": "documented_finding",
    "strauss_explicit_argument": "documented_finding",
    "controlled_synthetic_inference": "supported_inference",
    "unresolved_question": "unresolved_uncertainty",
}
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


class AdapterError(ValueError):
    """Raised when a request exceeds the Xenophon adapter contract."""


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
    if not isinstance(manifest, dict):
        errors.append("pinned manifest is not a mapping")
    elif manifest.get("version") != pin.get("manifest_version"):
        errors.append("repository_pin manifest version does not match pinned commit")
    return errors


def admitted_witnesses() -> dict[str, str]:
    index = load_yaml(CORPUS_INDEX_PATH)
    result: dict[str, str] = {}
    for source in index.get("sources", []):
        if not isinstance(source, dict):
            continue
        source_id = source.get("id")
        for witness_id in source.get("witness_ids", []):
            if isinstance(source_id, str) and isinstance(witness_id, str):
                result[witness_id] = source_id
    return result


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if manifest.get("repository") != REPOSITORY:
        errors.append("manifest repository mismatch")
    if manifest.get("version") != MANIFEST_VERSION:
        errors.append(f"manifest version must be {MANIFEST_VERSION}")
    if manifest.get("state") != "MINISTER_ADAPTER_R1_DRAFT_COMPLETE_PENDING_OWNER_REVIEW":
        errors.append("manifest R1 state mismatch")
    adapter = manifest.get("minister_adapter", {})
    if adapter.get("id") != "XEN-MINISTER-ADAPTER-001-R1":
        errors.append("minister adapter R1 identity mismatch")
    if adapter.get("owner_adopted") is not False or adapter.get("operational_authorization") is not False:
        errors.append("adapter R1 must remain unadopted and non-operational")
    if adapter.get("sanctum_registration_authorized") is not False:
        errors.append("Sanctum registration must remain unauthorized")
    greek = manifest.get("source_policy", {}).get("greek_language_review", {})
    if greek.get("status") != "DEFERRED_BY_OWNER" or greek.get("greek_dependent_claims") != "PROHIBITED":
        errors.append("Greek-language jurisdiction mismatch")
    return errors


def validate_mechanism(mechanism: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if [item.get("id") for item in mechanism.get("registers", [])] != [f"XEN-REGISTER-{i:03d}" for i in range(1, 5)]:
        errors.append("four-register order mismatch")
    if [item.get("id") for item in mechanism.get("guards", [])] != [f"XEN-GUARD-{i:03d}" for i in range(1, 4)]:
        errors.append("three-guard order mismatch")
    contract = mechanism.get("constitutional_contract", {})
    for field in (
        "identical_briefing_required",
        "tailored_briefing_prohibited",
        "committed_judgment_required",
        "standing_unresolved_questions_required",
        "self_reference_prohibited",
        "evidence_typing_required",
        "artificial_intelligence_self_certification_prohibited",
    ):
        if contract.get(field) is not True:
            errors.append(f"mechanism safeguard missing: {field}")
    return errors


def _require_nonempty_string(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} must be a non-empty string")


def validate_speech_request(request: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if request.get("record_type") != "xenophon_speech_request":
        errors.append("record_type must be xenophon_speech_request")
    for field in ("request_id", "report_id", "question", "requested_output", "direct_answer", "termination_status"):
        _require_nonempty_string(request.get(field), field, errors)
    if request.get("mode") not in ALLOWED_MODES:
        errors.append("mode must be reasoned or outside_my_ground")

    inquiry = request.get("inquiry_ref")
    if not isinstance(inquiry, dict):
        errors.append("inquiry_ref must be a mapping")
    else:
        for field in ("ref", "path", "envelope_sha256"):
            _require_nonempty_string(inquiry.get(field), f"inquiry_ref.{field}", errors)
        if SHA256.fullmatch(str(inquiry.get("envelope_sha256", ""))):
            try:
                if sha256_file(str(inquiry["path"])) != inquiry["envelope_sha256"]:
                    errors.append("inquiry envelope hash does not match referenced bytes")
            except AdapterError as exc:
                errors.append(str(exc))
        else:
            errors.append("inquiry_ref.envelope_sha256 must be a lowercase SHA-256")

    briefing = request.get("briefing")
    if not isinstance(briefing, dict):
        errors.append("briefing must be a mapping")
    else:
        for field in ("briefing_id", "path", "sha256"):
            _require_nonempty_string(briefing.get(field), f"briefing.{field}", errors)
        if briefing.get("identical_for_all_ministers") is not True:
            errors.append("briefing must be identical for all ministers")
        if briefing.get("tailored_feed") is not False:
            errors.append("tailored briefing feeds are prohibited")
        if SHA256.fullmatch(str(briefing.get("sha256", ""))):
            try:
                if sha256_file(str(briefing["path"])) != briefing["sha256"]:
                    errors.append("briefing hash does not match referenced bytes")
            except AdapterError as exc:
                errors.append(str(exc))
        else:
            errors.append("briefing.sha256 must be a lowercase SHA-256")

    pin = request.get("repository_pin")
    if not isinstance(pin, dict):
        errors.append("repository_pin must be a mapping")
    else:
        errors.extend(validate_repository_pin(pin))

    if request.get("self_reference_as_authority") is not False:
        errors.append("self-reference as authority is prohibited")
    if request.get("claims_greek_textual_authority") is not False:
        errors.append("Greek textual authority may not be claimed")
    if request.get("artificial_intelligence_self_certification") is not False:
        errors.append("artificial-intelligence self-certification is prohibited")

    admitted = admitted_witnesses()
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
        for field in ("statement", "source_location", "confidence"):
            _require_nonempty_string(finding.get(field), f"findings[{index}].{field}", errors)
        grounds = finding.get("grounds")
        if not isinstance(grounds, list) or not grounds:
            errors.append(f"findings[{index}].grounds must be a non-empty list")
            continue
        for ground_index, ground in enumerate(grounds):
            if not isinstance(ground, dict):
                errors.append(f"findings[{index}].grounds[{ground_index}] must be a mapping")
                continue
            witness_id = ground.get("witness_id")
            source_id = ground.get("source_id")
            if admitted.get(str(witness_id)) != source_id:
                errors.append(f"findings[{index}].grounds[{ground_index}] witness/source pair is not admitted")
            try:
                resolve_repository_path(str(ground.get("path", "")))
            except AdapterError as exc:
                errors.append(str(exc))
        if not isinstance(finding.get("alternatives_considered"), list):
            errors.append(f"findings[{index}].alternatives_considered must be a list")
    if request.get("mode") == "reasoned" and "controlled_synthetic_inference" not in seen_layers:
        errors.append("reasoned requests require controlled synthetic inference")
    if "unresolved_question" not in seen_layers:
        errors.append("at least one unresolved question must remain standing")

    path = request.get("pedagogical_path")
    if not isinstance(path, list) or len(path) < 3:
        errors.append("pedagogical_path must contain at least three ordered steps")
    else:
        for index, step in enumerate(path):
            if not isinstance(step, dict) or step.get("register") not in {f"XEN-REGISTER-{i:03d}" for i in range(1, 5)}:
                errors.append(f"pedagogical_path[{index}] is invalid")
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
    evidence_keys: set[tuple[str, str, str]] = set()
    propositions: list[dict[str, Any]] = []
    for finding in request["findings"]:
        for ground in finding["grounds"]:
            key = (ground["witness_id"], ground["source_id"], ground["path"])
            if key not in evidence_keys:
                evidence_keys.add(key)
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
    uncertainties = [
        item["question"] if isinstance(item, dict) and isinstance(item.get("question"), str) else str(item)
        for item in request["standing_unresolved_questions"]
    ]
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
                "ref": "governance/owner-reviews/2026-08-01-strauss-guided-controlled-synthesis-r1-in-depth-review.yaml",
                "id": "XEN-OWNER-REVIEW-010",
                "status": "OWNER_ADOPTED_SYNTHESIS",
            },
            "adapter_operational_authority": {"status": "PENDING_OWNER_ADOPTION"},
        },
        "direct_answer": request["direct_answer"],
        "pedagogical_path": request["pedagogical_path"],
        "evidence": evidence,
        "propositions": propositions,
        "uncertainties": uncertainties,
        "dissent": request["contradictions_and_dissent"],
        "jurisdiction": {
            "current": "CONTROLLED_ENGLISH_WITNESS_PRIMARY_SECONDARY_SYNTHESIS",
            "greek_language_review": "DEFERRED_BY_OWNER_NOT_CURRENT_BLOCKER",
            "greek_dependent_claims": "PROHIBITED",
        },
        "termination": {
            "status": request["termination_status"],
            "authoritative_effect": "NONE_UNTIL_OWNER_ADOPTION_AND_SANCTUM_CERTIFICATION",
            "presidential_synthesis": "NOT_PERFORMED",
        },
        "provenance": {
            "produced_by": {"actor": "xenophon-adapter-r1-draft", "repo": REPOSITORY, "commit": pin["commit"]},
            "consumed_records": [
                {"ref": "manifest.yaml", "commit": pin["commit"]},
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
        print("Xenophon adapter R1 interface validation passed")
        return 0
    request = load_yaml(args.path)
    if args.command == "validate-request":
        errors = validate_speech_request(request)
        if errors:
            print("; ".join(errors), file=sys.stderr)
            return 1
        print("Xenophon adapter R1 request validation passed")
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
