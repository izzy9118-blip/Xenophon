from pathlib import Path
import hashlib
import json

import pytest
import yaml
from jsonschema import Draft202012Validator

import adapter

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/xenophon-adapter-r2-speech-request.yaml"
SCHEMA = ROOT / "federation/contracts/ministerial-report.schema.v1.3.0.json"


def load_fixture():
    return yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))


def test_adapter_interface_and_request_validate():
    assert adapter.validate_manifest(adapter.load_yaml(adapter.MANIFEST_PATH)) == []
    assert adapter.validate_mechanism(adapter.load_yaml(adapter.MECHANISM_PATH)) == []
    assert adapter.validate_speech_request(load_fixture()) == []


def test_adapter_builds_live_schema_valid_report():
    report = adapter.build_candidate_report(load_fixture())
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(report)
    assert report["report_status"] == "DRAFT_PENDING_MINISTER_REPOSITORY_VALIDATION"
    assert report["certification_status"] == "PENDING_OWNER_CERTIFICATION"
    derivation = report["governing_manifest"]["derivation_authority"]
    assert derivation["status"] == "OWNER_ADOPTED_MULTI_WORK_DERIVATION"
    assert derivation["source_lines"] == ["anabasis", "hieron_on_tyranny"]
    authority = report["governing_manifest"]["adapter_operational_authority"]
    assert authority["id"] == "XENOPHON-AUTH-002"
    assert authority["status"] == "OWNER_AUTHORIZED_OPERATIONAL_INTERFACE"
    assert {item["witness_id"] for item in report["evidence"]} == {
        "XEN-WIT-PRI-001",
        "XEN-WIT-SEC-001",
        "XEN-WIT-COMP-001",
    }
    assert {item["source_id"] for item in report["evidence"]} == {
        "XEN-SRC-PRI-001",
        "XEN-SRC-PRI-002",
        "XEN-SRC-SEC-001",
        "XEN-SRC-SEC-002",
        "XEN-SRC-SEC-003",
        "XEN-SRC-SEC-004",
        "XEN-SRC-SEC-005",
        "XEN-SRC-SEC-006",
    }
    assert all(isinstance(item, str) for item in report["uncertainties"])
    assert len(report["pedagogical_path"]) == 5
    assert report["jurisdiction"]["source_lines"] == ["anabasis", "hieron_on_tyranny"]
    assert report["dissent"]


def test_fixture_hashes_match_exact_committed_bytes():
    request = load_fixture()
    envelope = ROOT / request["inquiry_ref"]["path"]
    briefing = ROOT / request["briefing"]["path"]
    assert hashlib.sha256(envelope.read_bytes()).hexdigest() == request["inquiry_ref"]["envelope_sha256"]
    assert hashlib.sha256(briefing.read_bytes()).hexdigest() == request["briefing"]["sha256"]


def test_adapter_rejects_tailored_briefing_and_greek_authority():
    request = load_fixture()
    request["briefing"]["tailored_feed"] = True
    request["claims_greek_textual_authority"] = True
    errors = adapter.validate_speech_request(request)
    assert "tailored briefing feeds are prohibited" in errors
    assert "Greek textual authority may not be claimed" in errors


def test_adapter_rejects_hash_tampering():
    request = load_fixture()
    request["briefing"]["sha256"] = "0" * 64
    request["inquiry_ref"]["envelope_sha256"] = "1" * 64
    errors = adapter.validate_speech_request(request)
    assert "briefing hash does not match referenced bytes" in errors
    assert "inquiry envelope hash does not match referenced bytes" in errors


def test_adapter_rejects_false_manifest_pin():
    request = load_fixture()
    request["repository_pin"]["manifest_version"] = "1.68.0"
    errors = adapter.validate_speech_request(request)
    assert "repository_pin manifest version does not match pinned commit" in errors


def test_adapter_rejects_unadmitted_witness_pair():
    request = load_fixture()
    request["findings"][0]["grounds"][0]["witness_id"] = "XEN-WIT-FAKE-001"
    errors = adapter.validate_speech_request(request)
    assert any("witness/source pair is not registered" in item for item in errors)


def test_adapter_rejects_pair_outside_selected_source_line():
    request = load_fixture()
    request["source_lines"] = ["anabasis"]
    errors = adapter.validate_speech_request(request)
    assert any("witness/source pair is not operationally authorized" in item for item in errors)


def test_composite_witness_preserves_all_six_hieron_source_roles():
    pairs = adapter.registered_witness_pairs()
    composite_sources = {
        source_id for witness_id, source_id in pairs if witness_id == "XEN-WIT-COMP-001"
    }
    assert composite_sources == {
        "XEN-SRC-PRI-002",
        "XEN-SRC-SEC-002",
        "XEN-SRC-SEC-003",
        "XEN-SRC-SEC-004",
        "XEN-SRC-SEC-005",
        "XEN-SRC-SEC-006",
    }


def test_adapter_rejects_erasure_of_unresolved_questions():
    request = load_fixture()
    request["findings"] = [item for item in request["findings"] if item["evidence_layer"] != "unresolved_question"]
    request["standing_unresolved_questions"] = []
    errors = adapter.validate_speech_request(request)
    assert "at least one unresolved question must remain standing" in errors
    assert "standing_unresolved_questions must be a non-empty list" in errors
