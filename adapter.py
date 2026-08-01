from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = ROOT / "manifest.yaml"
SYNTHESIS_PATH = ROOT / "studies/comparisons/anabasis-primary-strauss/syntheses/XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001-R1.yaml"
MECHANISM_PATH = ROOT / "speech/speech-mechanism.yaml"
REPOSITORY = "izzy9118-blip/Xenophon"
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


def load_manifest() -> dict[str, Any]:
    return load_yaml(MANIFEST_PATH)


def load_synthesis() -> dict[str, Any]:
    return load_yaml(SYNTHESIS_PATH)


def load_mechanism() -> dict[str, Any]:
    return load_yaml(MECHANISM_PATH)


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if manifest.get("repository") != REPOSITORY:
        errors.append("manifest repository mismatch")
    if manifest.get("version") != "1.67.0":
        errors.append("manifest version must be 1.67.0")
    if manifest.get("state") != "MINISTER_ADAPTER_DRAFT_COMPLETE_PENDING_OWNER_REVIEW":
        errors.append("manifest adapter state mismatch")
    synthesis = manifest.get("controlled_synthesis", {})
    if synthesis.get("active_revision") != "XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001-R1":
        errors.append("owner-adopted R1 synthesis is not active")
    if synthesis.get("r1_owner_adopted") is not True:
        errors.append("R1 synthesis must be owner adopted")
    adapter = manifest.get("minister_adapter", {})
    if adapter.get("id") != "XEN-MINISTER-ADAPTER-001":
        errors.append("minister adapter identity mismatch")
    if adapter.get("status") != "DRAFT_COMPLETE_PENDING_OWNER_REVIEW":
        errors.append("minister adapter status mismatch")
    if adapter.get("sanctum_registration_authorized") is not False:
        errors.append("Sanctum registration must remain unauthorized")
    greek = manifest.get("source_policy", {}).get("greek_language_review", {})
    if greek.get("status") != "DEFERRED_BY_OWNER":
        errors.append("Greek-language deferral missing")
    if greek.get("required_for_current_production") is not False:
        errors.append("Greek review may not be a current production prerequisite")
    if manifest.get("artificial_intelligence_self_certification_prohibited") is not True:
        errors.append("AI self-certification prohibition missing")
    return errors


def validate_mechanism(mechanism: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    identity = mechanism.get("identity", {})
    if identity.get("id") != "XEN-SPEECH-MECHANISM-001":
        errors.append("speech mechanism identity mismatch")
    if mechanism.get("status") != "DRAFT_COMPLETE_PENDING_OWNER_REVIEW":
        errors.append("speech mechanism status mismatch")
    registers = mechanism.get("registers", [])
    guards = mechanism.get("guards", [])
    if [r.get("id") for r in registers] != [
        "XEN-REGISTER-001",
        "XEN-REGISTER-002",
        "XEN-REGISTER-003",
        "XEN-REGISTER-004",
    ]:
        errors.append("four-register order mismatch")
    if [g.get("id") for g in guards] != [
        "XEN-GUARD-001",
        "XEN-GUARD-002",
        "XEN-GUARD-003",
    ]:
        errors.append("three-guard order mismatch")
    if mechanism.get("constitutional_contract", {}).get("self_reference_prohibited") is not True:
        errors.append("self-reference prohibition missing")
    if mechanism.get("constitutional_contract", {}).get("committed_judgment_required") is not True:
        errors.append("committed judgment requirement missing")
    if mechanism.get("constitutional_contract", {}).get("standing_unresolved_questions_required") is not True:
        errors.append("standing unresolved questions requirement missing")
    return errors


def _require_mapping(value: Any, label: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{label} must be a mapping")
        return {}
    return value


def _require_nonempty_string(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} must be a non-empty string")


def validate_speech_request(request: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if request.get("record_type") != "xenophon_speech_request":
        errors.append("record_type must be xenophon_speech_request")
    for field in ["request_id", "report_id", "question", "requested_output", "direct_answer", "termination_status"]:
        _require_nonempty_string(request.get(field), field, errors)
    if request.get("mode") not in ALLOWED_MODES:
        errors.append("mode must be reasoned or outside_my_ground")

    inquiry = _require_mapping(request.get("inquiry_ref"), "inquiry_ref", errors)
    _require_nonempty_string(inquiry.get("ref"), "inquiry_ref.ref", errors)
    if not SHA40.fullmatch(str(inquiry.get("commit", ""))):
        errors.append("inquiry_ref.commit must be a 40-character lowercase SHA")
    if not SHA256.fullmatch(str(inquiry.get("envelope_sha256", ""))):
        errors.append("inquiry_ref.envelope_sha256 must be a 64-character lowercase SHA-256")

    briefing = _require_mapping(request.get("briefing"), "briefing", errors)
    for field in ["briefing_id", "path", "sha256"]:
        _require_nonempty_string(briefing.get(field), f"briefing.{field}", errors)
    if not SHA256.fullmatch(str(briefing.get("sha256", ""))):
        errors.append("briefing.sha256 must be a 64-character lowercase SHA-256")
    if briefing.get("identical_for_all_ministers") is not True:
        errors.append("briefing must be identical for all ministers")
    if briefing.get("tailored_feed") is not False:
        errors.append("tailored briefing feeds are prohibited")

    pin = _require_mapping(request.get("repository_pin"), "repository_pin", errors)
    if pin.get("repository") != REPOSITORY:
        errors.append("repository_pin.repository mismatch")
    if not SHA40.fullmatch(str(pin.get("commit", ""))):
        errors.append("repository_pin.commit must be a 40-character lowercase SHA")
    if pin.get("manifest_path") != "manifest.yaml":
        errors.append("repository_pin.manifest_path must be manifest.yaml")
    if pin.get("manifest_version") != "1.67.0":
        errors.append("repository_pin.manifest_version must be 1.67.0")

    if request.get("self_reference_as_authority") is not False:
        errors.append("self-reference as authority is prohibited")
    if request.get("claims_greek_textual_authority") is not False:
        errors.append("Greek textual authority may not be claimed")
    if request.get("artificial_intelligence_self_certification") is not False:
        errors.append("artificial-intelligence self-certification is prohibited")

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
        for field in ["statement", "source_location", "confidence"]:
            _require_nonempty_string(finding.get(field), f"findings[{index}].{field}", errors)
        grounds = finding.get("grounds")
        if not isinstance(grounds, list) or not grounds:
            errors.append(f"findings[{index}].grounds must be a non-empty list")
        alternatives = finding.get("alternatives_considered")
        if not isinstance(alternatives, list):
            errors.append(f"findings[{index}].alternatives_considered must be a list")
    if request.get("mode") == "reasoned" and "controlled_synthetic_inference" not in seen_layers:
        errors.append("reasoned requests require at least one controlled synthetic inference")
    if "unresolved_question" not in seen_layers:
        errors.append("at least one unresolved question must remain standing")

    path = request.get("pedagogical_path")
    if not isinstance(path, list) or len(path) < 3:
        errors.append("pedagogical_path must contain at least three ordered steps")
    else:
        for index, step in enumerate(path):
            if not isinstance(step, dict):
                errors.append(f"pedagogical_path[{index}] must be a mapping")
                continue
            _require_nonempty_string(step.get("move"), f"pedagogical_path[{index}].move", errors)
            if step.get("register") not in {f"XEN-REGISTER-{i:03d}" for i in range(1, 5)}:
                errors.append(f"pedagogical_path[{index}].register is invalid")

    unresolved = request.get("standing_unresolved_questions")
    if not isinstance(unresolved, list) or not unresolved:
        errors.append("standing_unresolved_questions must be a non-empty list")
    dissent = request.get("contradictions_and_dissent")
    if not isinstance(dissent, list):
        errors.append("contradictions_and_dissent must be a list")
    return errors


def build_candidate_report(request: dict[str, Any]) -> dict[str, Any]:
    errors = validate_speech_request(request)
    if errors:
        raise AdapterError("; ".join(errors))

    pin = request["repository_pin"]
    evidence: list[dict[str, Any]] = []
    evidence_keys: set[tuple[str, str]] = set()
    propositions: list[dict[str, Any]] = []
    for finding in request["findings"]:
        grounds = finding["grounds"]
        for ground in grounds:
            ref = str(ground.get("ref", ""))
            path = str(ground.get("path", finding["source_location"]))
            key = (ref, path)
            if key not in evidence_keys:
                evidence_keys.add(key)
                evidence.append(
                    {
                        "ref": ref,
                        "path": path,
                        "repository_commit": pin["commit"],
                        "evidence_layer": finding["evidence_layer"],
                    }
                )
        propositions.append(
            {
                "kind": REPORT_KIND[finding["evidence_layer"]],
                "evidence_layer": finding["evidence_layer"],
                "claim": finding["statement"],
                "grounds": grounds,
                "source_location": finding["source_location"],
                "confidence": finding["confidence"],
                "alternatives_considered": finding["alternatives_considered"],
            }
        )

    return {
        "record_type": "ministerial_report",
        "id": request["report_id"],
        "report_id": request["report_id"],
        "report_status": "DRAFT_PENDING_MINISTER_REPOSITORY_VALIDATION",
        "inquiry_ref": request["inquiry_ref"],
        "minister": {
            "actor": MINISTER_ACTOR,
            "manifest_commit": pin["commit"],
            "title": "Xenophon Minister",
        },
        "mode": request["mode"],
        "repository": {"full_name": REPOSITORY, "git_commit": pin["commit"]},
        "governing_manifest": {
            "path": pin["manifest_path"],
            "version": pin["manifest_version"],
            "authorization_ref": "governance/owner-reviews/2026-08-01-strauss-guided-controlled-synthesis-r1-in-depth-review.yaml",
            "authorization_id": "XEN-OWNER-REVIEW-010",
        },
        "direct_answer": request["direct_answer"],
        "pedagogical_path": request["pedagogical_path"],
        "evidence": evidence,
        "propositions": propositions,
        "uncertainties": request["standing_unresolved_questions"],
        "dissent": request["contradictions_and_dissent"],
        "jurisdiction": {
            "current": "CONTROLLED_ENGLISH_WITNESS_PRIMARY_SECONDARY_SYNTHESIS",
            "greek_language_review": "DEFERRED_BY_OWNER_NOT_CURRENT_BLOCKER",
            "greek_dependent_claims": "PROHIBITED",
        },
        "termination": {
            "status": request["termination_status"],
            "authoritative_effect": "NONE_UNTIL_XENOPHON_REPOSITORY_OWNER_REVIEW_AND_SANCTUM_CERTIFICATION",
            "presidential_synthesis": "NOT_PERFORMED",
        },
        "provenance": {
            "produced_by": {
                "actor": "xenophon-adapter-draft",
                "repo": REPOSITORY,
                "commit": pin["commit"],
            },
            "consumed_records": [
                {"ref": "manifest.yaml", "commit": pin["commit"]},
                {"ref": "XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001-R1", "commit": pin["commit"]},
                {"ref": request["briefing"]["briefing_id"], "sha256": request["briefing"]["sha256"]},
            ],
        },
        "certification_status": "PENDING_OWNER_REVIEW",
        "artificial_intelligence_self_certification": "PROHIBITED",
    }


def _print_errors(errors: list[str]) -> int:
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("Xenophon adapter validation passed")
    return 0


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
        return _print_errors(validate_manifest(load_manifest()) + validate_mechanism(load_mechanism()))
    request = load_yaml(args.path)
    if args.command == "validate-request":
        return _print_errors(validate_speech_request(request))
    report = build_candidate_report(request)
    rendered = yaml.safe_dump(report, sort_keys=False, allow_unicode=True)
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
