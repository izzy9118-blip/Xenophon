from pathlib import Path
import hashlib
import json
import subprocess
import sys

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
MANIFEST = ROOT / "manifest.yaml"
REQUEST = ROOT / "tests/fixtures/xenophon-speech-request.yaml"
ENVELOPE = ROOT / "tests/fixtures/xenophon-adapter-inquiry-envelope.yaml"
BRIEFING = ROOT / "tests/fixtures/xenophon-adapter-common-briefing.yaml"
SCHEMA = ROOT / "federation/contracts/ministerial-report.schema.v1.3.0.json"
SYNTHESIS = ROOT / "studies/comparisons/anabasis-primary-strauss/syntheses/XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001-R1.yaml"
REVIEW = ROOT / "speech/reviews/XEN-MINISTER-ADAPTER-R1-IN-DEPTH-REVIEW-001.yaml"
OWNER = ROOT / "governance/owner-reviews/2026-08-01-xenophon-minister-adapter-r1-in-depth-review.yaml"
AUTH = ROOT / "governance/repository-authorization.yaml"
FROZEN = ROOT / "scripts/validate_repository_v1_68.py"


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
    for path in [MANIFEST, REQUEST, ENVELOPE, BRIEFING, SCHEMA, SYNTHESIS, REVIEW, OWNER, AUTH, FROZEN, ROOT / "adapter.py", ROOT / "speech/speech-mechanism.yaml"]:
        if not path.is_file():
            return fail(f"required operational file missing: {path}")
    if not run([sys.executable, str(FROZEN)]):
        return fail("v1.68 predecessor verification failed")

    manifest = load_yaml(MANIFEST)
    request = load_yaml(REQUEST)
    synthesis = load_yaml(SYNTHESIS)
    review = load_yaml(REVIEW)
    owner = load_yaml(OWNER)
    authorization = load_yaml(AUTH)
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    if manifest.get("version") != "1.70.0" or manifest.get("state") != "OPERATIONAL_OWNER_AUTHORIZED_OPEN_RESEARCH":
        return fail("operational manifest state mismatch")
    if manifest.get("repository_authorization", {}).get("status") != "ACTIVE_OWNER_AUTHORIZATION":
        return fail("repository authorization not active")
    if manifest.get("repository_authorization", {}).get("exact_interface_commit") != "00292dce72870a79e21630b1014eedbcd7ddf327":
        return fail("exact interface commit mismatch")
    adapter_state = manifest.get("minister_adapter", {})
    if adapter_state.get("id") != "XEN-MINISTER-ADAPTER-001-R1":
        return fail("adapter id mismatch")
    if any(adapter_state.get(key) is not True for key in ["owner_reviewed", "owner_adopted", "operational_authorization", "sanctum_registration_authorized"]):
        return fail("adapter operational authority incomplete")
    if adapter_state.get("assembly_dispatch_authorized") is not False:
        return fail("Assembly dispatch authorized before Sanctum registration")
    preserved = adapter_state.get("preserved_architecture", {})
    if preserved.get("registers") != [f"XEN-REGISTER-{i:03d}" for i in range(1, 5)] or preserved.get("guards") != [f"XEN-GUARD-{i:03d}" for i in range(1, 4)]:
        return fail("approved architecture changed")
    if preserved.get("all_19_unresolved_questions_preserved") is not True or len(synthesis.get("unresolved_questions", [])) != 19:
        return fail("nineteen unresolved questions not preserved")

    if review.get("disposition_counts") != {"PASS": 15, "PASS_WITH_LIMIT": 1, "BLOCKING_REVISION": 0}:
        return fail("R1 review counts mismatch")
    if review.get("overall_ruling", {}).get("disposition") != "PASS_RECOMMEND_OWNER_ADOPTION":
        return fail("R1 review disposition mismatch")
    if owner.get("owner_ruling", {}).get("adoption_status") != "ADOPTED":
        return fail("owner adoption missing")
    if owner.get("owner_ruling", {}).get("operational_authorization") != "GRANTED_WITH_RECORDED_LIMITS":
        return fail("owner operational authorization missing")
    if authorization.get("status") != "ACTIVE_OWNER_AUTHORIZATION":
        return fail("authorization record inactive")
    if authorization.get("authorized_interface", {}).get("exact_interface_commit") != "00292dce72870a79e21630b1014eedbcd7ddf327":
        return fail("authorization interface commit mismatch")
    if authorization.get("scope", {}).get("semantic_completion") != "INCOMPLETE":
        return fail("operational authorization falsely claims semantic completion")

    if schema.get("$id") != "urn:sanctum:federation:ministerial-report:1.3.0":
        return fail("Sanctum schema mismatch")
    if manifest.get("governing_hub", {}).get("accepted_contract_commit") != "4ad09dc75897dda2a4f68d32148a72a342c2917c":
        return fail("Sanctum contract pin mismatch")
    if hashlib.sha256(ENVELOPE.read_bytes()).hexdigest() != request["inquiry_ref"]["envelope_sha256"]:
        return fail("inquiry envelope hash mismatch")
    if hashlib.sha256(BRIEFING.read_bytes()).hexdigest() != request["briefing"]["sha256"]:
        return fail("briefing hash mismatch")
    if request.get("repository_pin", {}).get("commit") != "3db18a1ce85c89054a6805311cc68970abda54cc" or request.get("repository_pin", {}).get("manifest_version") != "1.70.0":
        return fail("owner-authorized proving pin mismatch")

    if not run([sys.executable, "adapter.py", "validate-interface"]):
        return fail("operational adapter interface validation failed")
    if not run([sys.executable, "adapter.py", "validate-request", str(REQUEST.relative_to(ROOT))]):
        return fail("operational request validation failed")

    import adapter
    report = adapter.build_candidate_report(request)
    errors = list(Draft202012Validator(schema).iter_errors(report))
    if errors:
        return fail("candidate report fails Sanctum schema: " + "; ".join(error.message for error in errors))
    authority = report.get("governing_manifest", {}).get("adapter_operational_authority", {})
    if authority.get("id") != "XENOPHON-AUTH-001" or authority.get("status") != "OWNER_AUTHORIZED_OPERATIONAL_INTERFACE":
        return fail("report operational authority mismatch")
    if report.get("certification_status") != "PENDING_OWNER_CERTIFICATION":
        return fail("report improperly self-certifies")
    if {item.get("witness_id") for item in report.get("evidence", [])} != {"XEN-WIT-PRI-001", "XEN-WIT-SEC-001"}:
        return fail("sovereign witness identities changed")
    if report.get("termination", {}).get("presidential_synthesis") != "NOT_PERFORMED":
        return fail("report performs presidential synthesis")
    if not run([sys.executable, "-m", "pytest", "-q", "tests/test_minister_adapter.py"]):
        return fail("operational adapter behavioral tests failed")

    greek = manifest.get("source_policy", {}).get("greek_language_review", {})
    if greek.get("required_for_current_production") is not False or greek.get("greek_dependent_claims") != "PROHIBITED":
        return fail("Greek deferral changed")
    gates = manifest.get("governance_gates", {})
    if gates.get("semantic_completion") != "INCOMPLETE" or gates.get("final_teaching_authorized") is not False:
        return fail("operational state claims finality")
    if gates.get("artificial_intelligence_self_certification_prohibited") is not True:
        return fail("AI self-certification prohibition missing")
    if gates.get("sanctum_registration_present") is not False or gates.get("assembly_dispatch_authorized") is not False:
        return fail("Sanctum or Assembly authority asserted prematurely")

    print("Xenophon repository validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
