from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]

SOURCE_RECORDS = {
    "XEN-SRC-PRI-002": ROOT / "corpus/sources/xenophon-hieron.yaml",
    "XEN-SRC-SEC-002": ROOT / "corpus/sources/strauss-on-tyranny.yaml",
    "XEN-SRC-SEC-003": ROOT / "corpus/sources/kojeve-tyranny-and-wisdom.yaml",
    "XEN-SRC-SEC-004": ROOT / "corpus/sources/strauss-restatement-on-xenophons-hiero.yaml",
    "XEN-SRC-SEC-005": ROOT / "corpus/sources/strauss-kojeve-correspondence.yaml",
    "XEN-SRC-SEC-006": ROOT / "corpus/sources/gourevitch-roth-on-tyranny-editorial-apparatus.yaml",
}
WITNESS = ROOT / "corpus/witnesses/on-tyranny-uchicago-2013.yaml"
READING_PLAN = ROOT / "studies/hieron-on-tyranny/reading-plan.yaml"
ARTIFACT_INDEX = ROOT / "studies/hieron-on-tyranny/artifacts/completed-close-reading-index.yaml"
CUMULATIVE = ROOT / "studies/hieron-on-tyranny/cumulative/XEN-HIERON-ON-TYRANNY-CUMULATIVE-001.yaml"
DIRECTIVE = ROOT / "governance/owner-directives/2026-08-07-integrate-completed-on-tyranny-close-reading.yaml"
REVIEW_PROGRESS = ROOT / "governance/owner-reviews/2026-08-09-hieron-on-tyranny-bounded-review-progress.yaml"
HISTORY = ROOT / "history/2026-08-07-hieron-on-tyranny-completed-work-integration.md"
AUDIT = ROOT / "audits/hieron-on-tyranny-integration-state.yaml"


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def fail(message: str) -> int:
    print(message)
    return 1


def main() -> int:
    required = [
        ROOT / "corpus/index.yaml",
        ROOT / "manifest.yaml",
        WITNESS,
        READING_PLAN,
        ARTIFACT_INDEX,
        CUMULATIVE,
        DIRECTIVE,
        REVIEW_PROGRESS,
        HISTORY,
        AUDIT,
        *SOURCE_RECORDS.values(),
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        return fail("missing Hieron / On Tyranny integration files: " + ", ".join(missing))

    manifest = load_yaml(ROOT / "manifest.yaml")
    if manifest.get("version") != "1.70.0":
        return fail("integration changed the authorized operational manifest version")
    adapter = manifest.get("minister_adapter", {})
    if adapter.get("id") != "XEN-MINISTER-ADAPTER-001-R1":
        return fail("integration changed the authorized adapter identity")
    if adapter.get("preserved_architecture", {}).get("registers") != [
        f"XEN-REGISTER-{number:03d}" for number in range(1, 5)
    ]:
        return fail("integration changed the four authorized registers")
    if adapter.get("preserved_architecture", {}).get("guards") != [
        f"XEN-GUARD-{number:03d}" for number in range(1, 4)
    ]:
        return fail("integration changed the three authorized guards")

    index = load_yaml(ROOT / "corpus/index.yaml")
    if index.get("counts") != {
        "primary_sources": 2,
        "secondary_sources": 6,
        "registered_witnesses": 3,
    }:
        return fail("corpus counts do not include the complete registered source set")
    indexed = {item.get("id"): item for item in index.get("sources", [])}
    expected_ids = {"XEN-SRC-PRI-001", "XEN-SRC-SEC-001", *SOURCE_RECORDS}
    if set(indexed) != expected_ids:
        return fail("corpus source identifiers do not preserve old sources plus the new package")

    pending_status = "REGISTERED_FROM_COMPLETED_CLOSE_READING_PENDING_OWNER_ADMISSION"
    for source_id, path in SOURCE_RECORDS.items():
        source = load_yaml(path)
        if source.get("id") != source_id or source.get("status") != pending_status:
            return fail(f"source registration mismatch: {source_id}")
        if source.get("witness_ids") != ["XEN-WIT-COMP-001"]:
            return fail(f"source does not retain the composite witness: {source_id}")
        if indexed[source_id].get("record") != str(path.relative_to(ROOT)):
            return fail(f"corpus index path mismatch: {source_id}")

    witness = load_yaml(WITNESS)
    if witness.get("id") != "XEN-WIT-COMP-001":
        return fail("composite witness identity mismatch")
    if witness.get("source_ids") != list(SOURCE_RECORDS):
        return fail("composite witness source order or membership mismatch")
    control = witness.get("file_control", {})
    if control.get("repository_deposition") != "not_deposited":
        return fail("integration falsely claims source deposition")
    if control.get("sha256") != "not_preserved_in_current_repository_handoff":
        return fail("integration invents or silently supplies an unverified witness hash")
    corrections = witness.get("documentary_corrections", [])
    if len(corrections) != 1 or corrections[0].get("id") != "XEN-HIERON-DOC-COR-001":
        return fail("5 November 1957 documentary correction is not preserved")

    plan = load_yaml(READING_PLAN)
    if plan.get("study_id") != "XEN-STUDY-HIERON-OT-001":
        return fail("reading plan identity mismatch")
    if plan.get("status") != "COMPLETED_PRE_REPOSITORY_CLOSE_READING_REGISTERED_PENDING_OWNER_REVIEW":
        return fail("completed predecessor work is not correctly distinguished from owner adoption")

    artifacts = load_yaml(ARTIFACT_INDEX)
    correspondence = artifacts.get("artifact_groups", {}).get("correspondence", {})
    if correspondence.get("unit_count") != 44:
        return fail("forty-four completed correspondence units are not preserved")
    if correspondence.get("predecessor_segment", {}).get("units") != "1-17":
        return fail("completed predecessor handoff segment is not preserved")
    if correspondence.get("repository_continuation_segment", {}).get("units") != "18-44":
        return fail("completed continuation segment is not preserved")
    synthesis = artifacts.get("artifact_groups", {}).get("integrated_synthesis", {})
    if synthesis.get("artifact") != "Integrated Synthesis Unit 48":
        return fail("Integrated Synthesis Unit 48 is not preserved")
    preservation = artifacts.get("preservation_status", {})
    if preservation.get("completion_claim") != "PRESERVED" or preservation.get("owner_adoption_claim") != "NOT_YET_MADE":
        return fail("completion and repository adoption are collapsed")

    cumulative = load_yaml(CUMULATIVE)
    questions = cumulative.get("standing_unresolved_questions", [])
    if len(questions) != 18:
        return fail("eighteen integration-stage unresolved questions are not preserved")
    if cumulative.get("governance_limits", {}).get("minister_adapter_expansion_authorized") is not False:
        return fail("integration improperly expands the operational adapter")
    if cumulative.get("governance_limits", {}).get("artificial_intelligence_self_certification_prohibited") is not True:
        return fail("AI self-certification prohibition is missing")

    normalization = cumulative.get("normalization_review", {})
    if normalization.get("review_id") != "XEN-HIERON-OT-IN-DEPTH-OWNER-REVIEW-001":
        return fail("bounded owner-review identity is not linked from the cumulative record")
    if normalization.get("status") != "IN_PROGRESS" or normalization.get("owner_adoption_effect") != "none":
        return fail("bounded review progress is collapsed into owner adoption")
    corrected_layers = normalization.get("corrected_layers", {})
    if corrected_layers.get("primary_Hieron_showing") != "PASS_WITH_NORMALIZATION_CORRECTION_APPLIED":
        return fail("reviewed Hieron normalization correction is not preserved")
    if corrected_layers.get("Strauss_explicit_argument") != "PASS_WITH_NORMALIZATION_CORRECTIONS_APPLIED":
        return fail("reviewed Strauss normalization corrections are not preserved")
    if corrected_layers.get("Kojeve_explicit_argument") != "PASS_WITH_NORMALIZATION_CORRECTIONS_APPLIED":
        return fail("reviewed Kojeve normalization corrections are not preserved")

    findings = cumulative.get("source_specific_findings", {})
    hieron_findings = findings.get("primary_Hieron_showing", [])
    if not hieron_findings or not hieron_findings[0].startswith("Hiero presents the tyrant's possession"):
        return fail("Hieron finding again collapses Hiero's account into unmediated Xenophon")

    strauss_findings = findings.get("Strauss_explicit_argument", [])
    if len(strauss_findings) < 9:
        return fail("Strauss layer has again been compressed below the reviewed normalization")
    required_strauss_markers = [
        "modern political science",
        "legitimate rule",
        "theoretically conceivable",
        "wisdom outranks political office",
        "piety and law",
    ]
    strauss_text = "\n".join(strauss_findings).lower()
    for marker in required_strauss_markers:
        if marker.lower() not in strauss_text:
            return fail(f"reviewed Strauss finding missing required concept: {marker}")

    kojeve_findings = findings.get("Kojeve_explicit_argument", [])
    if len(kojeve_findings) < 11:
        return fail("Kojeve layer has again been compressed below the reviewed normalization")
    required_kojeve_markers = [
        "recognition",
        "authority",
        "universal and homogeneous state",
        "historical verification",
        "intellectual mediators",
        "revolutionary political action",
    ]
    kojeve_text = "\n".join(kojeve_findings).lower()
    for marker in required_kojeve_markers:
        if marker.lower() not in kojeve_text:
            return fail(f"reviewed Kojeve finding missing required concept: {marker}")
    if "strauss contests" in kojeve_text or "strauss's criticism" in kojeve_text:
        return fail("Strauss-side criticism has leaked back into Kojeve's explicit-argument layer")

    review = load_yaml(REVIEW_PROGRESS)
    if review.get("review_id") != "XEN-HIERON-OT-IN-DEPTH-OWNER-REVIEW-001":
        return fail("bounded owner-review progress record identity mismatch")
    if review.get("status") != "OWNER_REVIEW_IN_PROGRESS_CORRECTIONS_APPLIED":
        return fail("bounded owner-review progress status mismatch")
    if review.get("owner_adoption_effect") != "none":
        return fail("review progress record falsely claims owner adoption")
    if review.get("minister_adapter_effect") != "none":
        return fail("review progress record improperly changes the minister adapter")
    if review.get("artificial_intelligence_self_certification_prohibited") is not True:
        return fail("review progress record omits AI self-certification prohibition")
    reviewed_layers = review.get("reviewed_layers", {})
    if reviewed_layers.get("Kojeve_explicit_argument", {}).get("status") != "PASS_WITH_NORMALIZATION_CORRECTIONS_APPLIED":
        return fail("review progress record does not preserve the reviewed Kojeve correction")
    if "Kojeve_explicit_argument" in review.get("not_yet_reviewed", []):
        return fail("review progress still marks Kojeve as not reviewed")

    directive = load_yaml(DIRECTIVE)
    if directive.get("directive_id") != "XEN-OWNER-DIRECTIVE-002":
        return fail("owner integration directive identity mismatch")
    distinction = directive.get("governing_distinction", {})
    if distinction.get("completed_close_reading") is not True:
        return fail("directive falsely reopens completed close reading")
    if distinction.get("repository_owner_adoption") != "pending_in_depth_review":
        return fail("directive falsely claims owner adoption")

    audit = load_yaml(AUDIT)
    if audit.get("audit_id") != "XEN-AUDIT-HIERON-OT-001":
        return fail("integration audit identity mismatch")
    integrated = audit.get("repository_integration", {})
    if integrated.get("owner_directed") is not True or integrated.get("owner_adopted") is not False:
        return fail("integration audit collapses owner direction into owner adoption")
    if integrated.get("source_records_registered") != 6:
        return fail("integration audit source count mismatch")

    print("Hieron / On Tyranny integration validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
