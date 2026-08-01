from pathlib import Path
import hashlib
import json
import subprocess
import sys

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.yaml"
ADAPTER = ROOT / "adapter.py"
MECHANISM = ROOT / "speech/speech-mechanism.yaml"
REQUEST = ROOT / "tests/fixtures/xenophon-speech-request.yaml"
ENVELOPE = ROOT / "tests/fixtures/xenophon-adapter-inquiry-envelope.yaml"
BRIEFING = ROOT / "tests/fixtures/xenophon-adapter-common-briefing.yaml"
SCHEMA = ROOT / "federation/contracts/ministerial-report.schema.v1.3.0.json"
R1_SYNTHESIS = ROOT / "studies/comparisons/anabasis-primary-strauss/syntheses/XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001-R1.yaml"
FROZEN = ROOT / "scripts/validate_repository_v1_68.py"


def load_yaml(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def fail(message):
    print(message)
    return 1


def run(command):
    process = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if process.returncode:
        print(process.stdout)
        print(process.stderr)
        return False
    return True


def main():
    for path in [MANIFEST, ADAPTER, MECHANISM, REQUEST, ENVELOPE, BRIEFING, SCHEMA, R1_SYNTHESIS, FROZEN]:
        if not path.is_file():
            return fail(f"required R1 file missing: {path}")

    if not run([sys.executable, str(FROZEN)]):
        return fail("v1.68 predecessor verification failed")

    manifest = load_yaml(MANIFEST)
    request = load_yaml(REQUEST)
    synthesis = load_yaml(R1_SYNTHESIS)
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    if manifest.get("version") != "1.69.0":
        return fail("manifest version mismatch")
    if manifest.get("state") != "MINISTER_ADAPTER_R1_DRAFT_COMPLETE_PENDING_OWNER_REVIEW":
        return fail("manifest R1 state mismatch")
    predecessor = manifest.get("predecessor_state", {})
    if predecessor.get("exact_head") != "fe7171b4caca347ebd1fdcb7f2d221efa3bf3324":
        return fail("v1.68 predecessor pin mismatch")
    adapter_state = manifest.get("minister_adapter", {})
    if adapter_state.get("id") != "XEN-MINISTER-ADAPTER-001-R1":
        return fail("adapter R1 id mismatch")
    if adapter_state.get("federation_dependency", {}).get("status") != "RESOLVED_BY_SANCTUM_CONTRACT_1_3_0":
        return fail("Sanctum witness identity dependency unresolved")
    if adapter_state.get("corrected_defects") != [
        "LIVE_SCHEMA_NONCONFORMANCE",
        "WITNESS_IDENTIFIER_INCOMPATIBILITY",
        "FALSE_REPOSITORY_PIN",
        "PLACEHOLDER_UNVERIFIED_HASHES",
        "DERIVATION_AND_OPERATIONAL_AUTHORITY_COLLAPSE",
    ]:
        return fail("R1 correction inventory mismatch")
    if any(adapter_state.get(key) is not False for key in ["owner_adopted", "operational_authorization", "sanctum_registration_authorized", "assembly_dispatch_authorized"]):
        return fail("R1 gained premature authority")
    preserved = adapter_state.get("preserved_architecture", {})
    if preserved.get("registers") != [f"XEN-REGISTER-{i:03d}" for i in range(1, 5)]:
        return fail("four-register architecture changed")
    if preserved.get("guards") != [f"XEN-GUARD-{i:03d}" for i in range(1, 4)]:
        return fail("three-guard architecture changed")
    if preserved.get("all_19_unresolved_questions_preserved") is not True:
        return fail("nineteen unresolved questions not preserved")
    if len(synthesis.get("unresolved_questions", [])) != 19:
        return fail("R1 synthesis unresolved-question inventory changed")

    if schema.get("$id") != "urn:sanctum:federation:ministerial-report:1.3.0":
        return fail("vendored Sanctum schema id mismatch")
    if manifest.get("governing_hub", {}).get("accepted_contract_commit") != "4ad09dc75897dda2a4f68d32148a72a342c2917c":
        return fail("Sanctum contract commit mismatch")

    if hashlib.sha256(ENVELOPE.read_bytes()).hexdigest() != request["inquiry_ref"]["envelope_sha256"]:
        return fail("inquiry envelope hash mismatch")
    if hashlib.sha256(BRIEFING.read_bytes()).hexdigest() != request["briefing"]["sha256"]:
        return fail("briefing hash mismatch")
    if request.get("repository_pin", {}).get("commit") != "312d5fddf2f6e63ba383e3cfb8a45ba0641a480b":
        return fail("code-bearing repository pin mismatch")
    if request.get("repository_pin", {}).get("manifest_version") != "1.69.0":
        return fail("request manifest version mismatch")

    if not run([sys.executable, "adapter.py", "validate-interface"]):
        return fail("adapter interface validation failed")
    if not run([sys.executable, "adapter.py", "validate-request", str(REQUEST.relative_to(ROOT))]):
        return fail("adapter request validation failed")

    import adapter
    report = adapter.build_candidate_report(request)
    errors = list(Draft202012Validator(schema).iter_errors(report))
    if errors:
        return fail("candidate report fails vendored Sanctum schema: " + "; ".join(error.message for error in errors))
    if report.get("certification_status") != "PENDING_OWNER_CERTIFICATION":
        return fail("candidate report certification status mismatch")
    if report.get("governing_manifest", {}).get("adapter_operational_authority", {}).get("status") != "PENDING_OWNER_ADOPTION":
        return fail("derivation and operational authority remain collapsed")
    if {item.get("witness_id") for item in report.get("evidence", [])} != {"XEN-WIT-PRI-001", "XEN-WIT-SEC-001"}:
        return fail("sovereign witness identities not preserved")
    if not all(isinstance(item, str) for item in report.get("uncertainties", [])):
        return fail("uncertainties are not schema strings")
    if report.get("termination", {}).get("presidential_synthesis") != "NOT_PERFORMED":
        return fail("candidate report performs presidential synthesis")

    if not run([sys.executable, "-m", "pytest", "-q", "tests/test_minister_adapter.py"]):
        return fail("adapter R1 behavioral tests failed")

    greek = manifest.get("source_policy", {}).get("greek_language_review", {})
    if greek.get("required_for_current_production") is not False or greek.get("greek_dependent_claims") != "PROHIBITED":
        return fail("Greek deferral changed")
    gates = manifest.get("governance_gates", {})
    if gates.get("artificial_intelligence_self_certification_prohibited") is not True:
        return fail("AI self-certification prohibition missing")
    if gates.get("sanctum_registration_present") is not False or gates.get("assembly_dispatch_authorized") is not False:
        return fail("federation authority granted prematurely")

    print("Xenophon repository validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
