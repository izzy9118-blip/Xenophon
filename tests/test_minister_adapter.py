from pathlib import Path

import yaml

import adapter


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/xenophon-speech-request.yaml"


def load_fixture():
    return yaml.safe_load(FIXTURE.read_text(encoding="utf-8"))


def test_adapter_interface_and_request_validate():
    assert adapter.validate_manifest(adapter.load_manifest()) == []
    assert adapter.validate_mechanism(adapter.load_mechanism()) == []
    assert adapter.validate_speech_request(load_fixture()) == []


def test_adapter_builds_typed_candidate_report():
    report = adapter.build_candidate_report(load_fixture())
    assert report["record_type"] == "ministerial_report"
    assert report["report_status"] == "DRAFT_PENDING_MINISTER_REPOSITORY_VALIDATION"
    assert report["minister"]["actor"] == "xenophon"
    assert report["jurisdiction"]["current"] == "CONTROLLED_ENGLISH_WITNESS_PRIMARY_SECONDARY_SYNTHESIS"
    assert report["jurisdiction"]["greek_dependent_claims"] == "PROHIBITED"
    assert report["certification_status"] == "PENDING_OWNER_REVIEW"
    assert report["artificial_intelligence_self_certification"] == "PROHIBITED"
    assert {item["evidence_layer"] for item in report["propositions"]} == {
        "primary_showing",
        "strauss_explicit_argument",
        "controlled_synthetic_inference",
        "unresolved_question",
    }
    assert len(report["uncertainties"]) == 3
    assert report["dissent"]
    assert len(report["pedagogical_path"]) == 4


def test_adapter_rejects_tailored_briefing_and_greek_authority():
    request = load_fixture()
    request["briefing"]["tailored_feed"] = True
    request["claims_greek_textual_authority"] = True
    errors = adapter.validate_speech_request(request)
    assert "tailored briefing feeds are prohibited" in errors
    assert "Greek textual authority may not be claimed" in errors


def test_adapter_rejects_erasure_of_unresolved_questions():
    request = load_fixture()
    request["findings"] = [
        item for item in request["findings"] if item["evidence_layer"] != "unresolved_question"
    ]
    request["standing_unresolved_questions"] = []
    errors = adapter.validate_speech_request(request)
    assert "at least one unresolved question must remain standing" in errors
    assert "standing_unresolved_questions must be a non-empty list" in errors
