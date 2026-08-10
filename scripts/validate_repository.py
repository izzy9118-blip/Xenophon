from pathlib import Path
import hashlib
import json
import subprocess
import sys

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

INTERFACE_COMMIT = "07997f8f8631d2dbac526ac4f368d467c7c62ae7"
MANIFEST = ROOT / "manifest.yaml"
REQUEST = ROOT / "tests/fixtures/xenophon-adapter-r2-speech-request.yaml"
ENVELOPE = ROOT / "tests/fixtures/xenophon-adapter-r2-inquiry-envelope.yaml"
BRIEFING = ROOT / "tests/fixtures/xenophon-adapter-r2-common-briefing.yaml"
SCHEMA = ROOT / "federation/contracts/ministerial-report.schema.v1.3.0.json"
ANABASIS_SYNTHESIS = ROOT / "studies/comparisons/anabasis-primary-strauss/syntheses/XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001-R1.yaml"
HIERON_CUMULATIVE = ROOT / "studies/hieron-on-tyranny/cumulative/XEN-HIERON-ON-TYRANNY-CUMULATIVE-001.yaml"
MECHANISM = ROOT / "speech/speech-mechanism-r2.yaml"
REVIEW = ROOT / "speech/reviews/XEN-MINISTER-ADAPTER-R2-IN-DEPTH-REVIEW-001.yaml"
OWNER = ROOT / "governance/owner-reviews/2026-08-10-xenophon-minister-adapter-r2-in-depth-review.yaml"
AUTH = ROOT / "governance/repository-authorization-r2.yaml"
BOUNDARY = ROOT / "governance/derivation-boundaries/2026-08-10-hieron-on-tyranny-operational-boundary.yaml"
AUDIT = ROOT / "audits/hieron-on-tyranny-operational-incorporation-state.yaml"
FROZEN = ROOT / "scripts/validate_repository_v1_70.py"

EXPECTED_PAIRS = {
    ("XEN-WIT-PRI-001", "XEN-SRC-PRI-001"),
    ("XEN-WIT-SEC-001", "XEN-SRC-SEC-001"),
    ("XEN-WIT-COMP-001", "XEN-SRC-PRI-002"),
    *{
        ("XEN-WIT-COMP-001", f"XEN-SRC-SEC-{number:03d}")
        for number in range(2, 7)
    },
}


def load_yaml(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def run(command):
    process = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if process.returncode:
        print(process.stdout)
        print(process.stderr)
        return False
    return True


def fail(message):
    print(message)
    return 1


def main():
    required = [
        MANIFEST,
        REQUEST,
        ENVELOPE,
        BRIEFING,
        SCHEMA,
        ANABASIS_SYNTHESIS,
        HIERON_CUMULATIVE,
        MECHANISM,
        REVIEW,
        OWNER,
        AUTH,
        BOUNDARY,
        AUDIT,
        FROZEN,
        ROOT / "adapter.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        return fail("required operational files missing: " + ", ".join(missing))
    if not run([sys.executable, str(FROZEN)]):
        return fail("v1.70 predecessor verification failed")

    manifest = load_yaml(MANIFEST)
    request = load_yaml(REQUEST)
    anabasis = load_yaml(ANABASIS_SYNTHESIS)
    hieron = load_yaml(HIERON_CUMULATIVE)
    mechanism = load_yaml(MECHANISM)
    review = load_yaml(REVIEW)
    owner = load_yaml(OWNER)
    authorization = load_yaml(AUTH)
    boundary = load_yaml(BOUNDARY)
    audit = load_yaml(AUDIT)
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    if manifest.get("version") != "1.71.0" or manifest.get("state") != "OPERATIONAL_OWNER_AUTHORIZED_MULTI_WORK_RESEARCH":
        return fail("R2 operational manifest state mismatch")
    predecessor = manifest.get("predecessor_state", {}).get("frozen_predecessor", {})
    if predecessor.get("version") != "1.70.0" or predecessor.get("exact_head") != "358fad19ea3361c027ba584fa41307f29c1338dd":
        return fail("v1.70 predecessor pin mismatch")
    repository_authorization = manifest.get("repository_authorization", {})
    if repository_authorization.get("id") != "XENOPHON-AUTH-002" or repository_authorization.get("status") != "ACTIVE_OWNER_AUTHORIZATION":
        return fail("R2 repository authorization not active")
    if repository_authorization.get("exact_interface_commit") != INTERFACE_COMMIT:
        return fail("R2 exact interface commit mismatch")

    adapter_state = manifest.get("minister_adapter", {})
    if adapter_state.get("id") != "XEN-MINISTER-ADAPTER-001-R2":
        return fail("R2 adapter identity mismatch")
    if any(adapter_state.get(key) is not True for key in ["owner_reviewed", "owner_adopted", "operational_authorization", "sanctum_registration_authorized"]):
        return fail("R2 operational authority incomplete")
    if adapter_state.get("assembly_dispatch_authorized") is not False:
        return fail("Assembly dispatch authorized before Sanctum registration")
    architecture = adapter_state.get("preserved_and_extended_architecture", {})
    if architecture.get("registers") != [f"XEN-REGISTER-{number:03d}" for number in range(1, 7)]:
        return fail("six-register R2 architecture mismatch")
    if architecture.get("guards") != [f"XEN-GUARD-{number:03d}" for number in range(1, 5)]:
        return fail("four-guard R2 architecture mismatch")
    if architecture.get("combined_unresolved_question_inventory") != 37:
        return fail("combined unresolved-question inventory mismatch")
    if len(anabasis.get("unresolved_questions", [])) != 19 or len(hieron.get("standing_unresolved_questions", [])) != 18:
        return fail("nineteen Anabasis and eighteen Hieron questions are not preserved")

    source_lines = manifest.get("source_policy", {}).get("operational_source_lines", {})
    if set(source_lines) != {"anabasis", "hieron_on_tyranny"}:
        return fail("operational source-line identities mismatch")
    observed_pairs = {
        (source.get("witness_id"), source.get("source_id"))
        for line in source_lines.values()
        for source in line.get("sources", [])
    }
    if observed_pairs != EXPECTED_PAIRS:
        return fail("eight operational source/witness pairs mismatch")

    if mechanism.get("identity", {}).get("id") != "XEN-SPEECH-MECHANISM-001-R2":
        return fail("R2 speech mechanism identity mismatch")
    if [item.get("id") for item in mechanism.get("registers", [])] != [f"XEN-REGISTER-{number:03d}" for number in range(1, 7)]:
        return fail("R2 mechanism register order mismatch")
    if [item.get("id") for item in mechanism.get("guards", [])] != [f"XEN-GUARD-{number:03d}" for number in range(1, 5)]:
        return fail("R2 mechanism guard order mismatch")

    counts = review.get("disposition_counts", {})
    if counts != {"PASS": 16, "PASS_WITH_LIMIT": 2, "BLOCKING_REVISION": 0}:
        return fail("R2 review counts mismatch")
    findings = review.get("findings", [])
    observed_counts = {
        "PASS": sum(item.get("severity") == "PASS" for item in findings),
        "PASS_WITH_LIMIT": sum(item.get("severity") == "PASS_WITH_LIMIT" for item in findings),
        "BLOCKING_REVISION": sum(item.get("severity") == "BLOCKING_REVISION" for item in findings),
    }
    if observed_counts != counts or review.get("reviewed_head") != INTERFACE_COMMIT:
        return fail("R2 detailed review does not match its reviewed interface")
    if review.get("overall_ruling", {}).get("disposition") != "PASS_RECOMMEND_OWNER_ADOPTION":
        return fail("R2 detailed review does not recommend adoption")
    if owner.get("review_id") != "XEN-OWNER-REVIEW-014" or owner.get("owner_ruling", {}).get("adoption_status") != "ADOPTED":
        return fail("R2 owner adoption missing")
    if owner.get("owner_ruling", {}).get("operational_authorization") != "GRANTED_WITH_RECORDED_LIMITS":
        return fail("R2 owner operational authorization missing")
    if authorization.get("authorization_id") != "XENOPHON-AUTH-002" or authorization.get("status") != "ACTIVE_OWNER_AUTHORIZATION":
        return fail("R2 authorization record inactive")
    if authorization.get("authorized_interface", {}).get("exact_interface_commit") != INTERFACE_COMMIT:
        return fail("R2 authorization interface commit mismatch")
    if authorization.get("scope", {}).get("semantic_completion") != "INCOMPLETE":
        return fail("R2 authorization falsely claims semantic completion")
    if boundary.get("boundary_id") != "XEN-HIERON-OT-DERIVATION-BOUNDARY-001":
        return fail("Hieron derivation boundary identity mismatch")
    if audit.get("status") != "OPERATIONAL_INCORPORATION_COMPLETE_OWNER_AUTHORIZED":
        return fail("Hieron operational incorporation audit incomplete")

    if schema.get("$id") != "urn:sanctum:federation:ministerial-report:1.3.0":
        return fail("Sanctum schema mismatch")
    if manifest.get("governing_hub", {}).get("accepted_contract_commit") != "4ad09dc75897dda2a4f68d32148a72a342c2917c":
        return fail("Sanctum contract pin mismatch")
    if hashlib.sha256(ENVELOPE.read_bytes()).hexdigest() != request["inquiry_ref"]["envelope_sha256"]:
        return fail("R2 inquiry envelope hash mismatch")
    if hashlib.sha256(BRIEFING.read_bytes()).hexdigest() != request["briefing"]["sha256"]:
        return fail("R2 briefing hash mismatch")
    pin = request.get("repository_pin", {})
    if pin.get("commit") != INTERFACE_COMMIT or pin.get("manifest_version") != "1.71.0":
        return fail("R2 proving pin mismatch")

    if not run([sys.executable, "adapter.py", "validate-interface"]):
        return fail("R2 adapter interface validation failed")
    if not run([sys.executable, "adapter.py", "validate-request", str(REQUEST.relative_to(ROOT))]):
        return fail("R2 proving request validation failed")

    import adapter

    report = adapter.build_candidate_report(request)
    errors = list(Draft202012Validator(schema).iter_errors(report))
    if errors:
        return fail("candidate report fails Sanctum schema: " + "; ".join(error.message for error in errors))
    authority = report.get("governing_manifest", {}).get("adapter_operational_authority", {})
    if authority.get("id") != "XENOPHON-AUTH-002" or authority.get("status") != "OWNER_AUTHORIZED_OPERATIONAL_INTERFACE":
        return fail("R2 report operational authority mismatch")
    if report.get("certification_status") != "PENDING_OWNER_CERTIFICATION":
        return fail("R2 report improperly self-certifies")
    if {item.get("witness_id") for item in report.get("evidence", [])} != {"XEN-WIT-PRI-001", "XEN-WIT-SEC-001", "XEN-WIT-COMP-001"}:
        return fail("R2 witness identities mismatch")
    if {item.get("source_id") for item in report.get("evidence", [])} != {source_id for _, source_id in EXPECTED_PAIRS}:
        return fail("R2 report does not exercise every authorized source role")
    if report.get("jurisdiction", {}).get("source_lines") != ["anabasis", "hieron_on_tyranny"]:
        return fail("R2 report source-line jurisdiction mismatch")
    if report.get("termination", {}).get("presidential_synthesis") != "NOT_PERFORMED":
        return fail("R2 report performs presidential synthesis")
    if not run([sys.executable, "-m", "pytest", "-q", "tests/test_minister_adapter.py"]):
        return fail("R2 adapter behavioral tests failed")

    greek = manifest.get("source_policy", {}).get("greek_language_review", {})
    if greek.get("required_for_current_production") is not False or greek.get("greek_dependent_claims") != "PROHIBITED":
        return fail("Greek deferral changed")
    gates = manifest.get("governance_gates", {})
    if gates.get("semantic_completion") != "INCOMPLETE" or gates.get("final_teaching_authorized") is not False:
        return fail("R2 operational state claims finality")
    if gates.get("artificial_intelligence_self_certification_prohibited") is not True:
        return fail("AI self-certification prohibition missing")
    if gates.get("sanctum_registration_present") is not False or gates.get("assembly_dispatch_authorized") is not False:
        return fail("Sanctum or Assembly authority asserted prematurely")

    print("Xenophon R2 multi-work repository validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
