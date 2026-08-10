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
PREDECESSOR_WITNESS = ROOT / "corpus/witnesses/on-tyranny-uchicago-2013.yaml"
WITNESS_VERIFICATION = ROOT / "corpus/witnesses/on-tyranny-uchicago-2013-verification-001.yaml"
READING_PLAN = ROOT / "studies/hieron-on-tyranny/reading-plan.yaml"
ARTIFACT_INDEX = ROOT / "studies/hieron-on-tyranny/artifacts/completed-close-reading-index.yaml"
CUMULATIVE = ROOT / "studies/hieron-on-tyranny/cumulative/XEN-HIERON-ON-TYRANNY-CUMULATIVE-001.yaml"
DETAILED_REVIEW = ROOT / "studies/hieron-on-tyranny/reviews/XEN-HIERON-OT-IN-DEPTH-REVIEW-001.yaml"
DIRECTIVE = ROOT / "governance/owner-directives/2026-08-07-integrate-completed-on-tyranny-close-reading.yaml"
OWNER_REVIEW = ROOT / "governance/owner-reviews/2026-08-10-hieron-on-tyranny-in-depth-review.yaml"
INTEGRATION_HISTORY = ROOT / "history/2026-08-07-hieron-on-tyranny-completed-work-integration.md"
ADOPTION_HISTORY = ROOT / "history/2026-08-10-hieron-on-tyranny-owner-adoption.md"
PREDECESSOR_AUDIT = ROOT / "audits/hieron-on-tyranny-integration-state.yaml"
CURRENT_AUDIT = ROOT / "audits/hieron-on-tyranny-owner-adoption-state.yaml"
OPERATIONAL_DIRECTIVE = ROOT / "governance/owner-directives/2026-08-10-finish-hieron-incorporation.yaml"
DERIVATION_BOUNDARY = ROOT / "governance/derivation-boundaries/2026-08-10-hieron-on-tyranny-operational-boundary.yaml"
ADAPTER_REVIEW = ROOT / "speech/reviews/XEN-MINISTER-ADAPTER-R2-IN-DEPTH-REVIEW-001.yaml"
ADAPTER_OWNER_REVIEW = ROOT / "governance/owner-reviews/2026-08-10-xenophon-minister-adapter-r2-in-depth-review.yaml"
AUTHORIZATION = ROOT / "governance/repository-authorization-r2.yaml"
OPERATIONAL_AUDIT = ROOT / "audits/hieron-on-tyranny-operational-incorporation-state.yaml"
OPERATIONAL_HISTORY = ROOT / "history/2026-08-10-hieron-on-tyranny-operational-incorporation.md"

EXPECTED_SHA256 = "f6a397d8e59ac1214cb339b4705a365ff5a9d45e3997205e8f968aad8b870bc6"


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def fail(message: str) -> int:
    print(message)
    return 1


def main() -> int:
    required = [
        ROOT / "corpus/index.yaml",
        ROOT / "manifest.yaml",
        PREDECESSOR_WITNESS,
        WITNESS_VERIFICATION,
        READING_PLAN,
        ARTIFACT_INDEX,
        CUMULATIVE,
        DETAILED_REVIEW,
        DIRECTIVE,
        OWNER_REVIEW,
        INTEGRATION_HISTORY,
        ADOPTION_HISTORY,
        PREDECESSOR_AUDIT,
        CURRENT_AUDIT,
        OPERATIONAL_DIRECTIVE,
        DERIVATION_BOUNDARY,
        ADAPTER_REVIEW,
        ADAPTER_OWNER_REVIEW,
        AUTHORIZATION,
        OPERATIONAL_AUDIT,
        OPERATIONAL_HISTORY,
        *SOURCE_RECORDS.values(),
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        return fail("missing Hieron / On Tyranny files: " + ", ".join(missing))

    manifest = load_yaml(ROOT / "manifest.yaml")
    if manifest.get("version") != "1.71.0":
        return fail("Hieron operational incorporation manifest version mismatch")
    if manifest.get("state") != "OPERATIONAL_OWNER_AUTHORIZED_MULTI_WORK_RESEARCH":
        return fail("Hieron is not incorporated into the active multi-work state")
    source_lines = manifest.get("source_policy", {}).get("operational_source_lines", {})
    if set(source_lines) != {"anabasis", "hieron_on_tyranny"}:
        return fail("Anabasis and Hieron are not preserved as distinct operational source lines")
    adapter = manifest.get("minister_adapter", {})
    if adapter.get("id") != "XEN-MINISTER-ADAPTER-001-R2":
        return fail("Hieron operational incorporation did not activate R2")
    if adapter.get("preserved_and_extended_architecture", {}).get("registers") != [
        f"XEN-REGISTER-{number:03d}" for number in range(1, 7)
    ]:
        return fail("R2 does not preserve four registers and add two Hieron registers")
    if adapter.get("preserved_and_extended_architecture", {}).get("guards") != [
        f"XEN-GUARD-{number:03d}" for number in range(1, 5)
    ]:
        return fail("R2 does not preserve three guards and add the Hieron source-role guard")
    incorporated = manifest.get("operationally_incorporated_research", {}).get("hieron_on_tyranny", {})
    if incorporated.get("status") != "OPERATIONALLY_INCORPORATED_OWNER_AUTHORIZED":
        return fail("manifest does not record completed Hieron operational incorporation")
    if incorporated.get("source_role_count") != 6 or incorporated.get("unresolved_question_count") != 18:
        return fail("manifest Hieron inventory mismatch")
    if manifest.get("owner_reviews", {}).get("hieron_on_tyranny_adoption") != str(OWNER_REVIEW.relative_to(ROOT)):
        return fail("manifest does not point to the Hieron owner-adoption review")

    index = load_yaml(ROOT / "corpus/index.yaml")
    if index.get("counts") != {
        "primary_sources": 2,
        "secondary_sources": 6,
        "registered_witnesses": 3,
    }:
        return fail("corpus counts changed instead of preserving one stable composite witness identity")
    indexed = {item.get("id"): item for item in index.get("sources", [])}
    expected_ids = {"XEN-SRC-PRI-001", "XEN-SRC-SEC-001", *SOURCE_RECORDS}
    if set(indexed) != expected_ids:
        return fail("corpus source identifiers do not preserve the complete source set")

    predecessor_status = "REGISTERED_FROM_COMPLETED_CLOSE_READING_PENDING_OWNER_ADMISSION"
    current_statuses = {
        "XEN-SRC-PRI-002": "OWNER_ADMITTED_PRIMARY_TRANSLATION_SOURCE",
        "XEN-SRC-SEC-002": "OWNER_ADOPTED_SECONDARY_SOURCE",
        "XEN-SRC-SEC-003": "OWNER_ADOPTED_SECONDARY_SOURCE",
        "XEN-SRC-SEC-004": "OWNER_ADOPTED_SECONDARY_SOURCE",
        "XEN-SRC-SEC-005": "OWNER_ADOPTED_SECONDARY_SOURCE",
        "XEN-SRC-SEC-006": "OWNER_ADOPTED_SECONDARY_SOURCE",
    }
    for source_id, path in SOURCE_RECORDS.items():
        source = load_yaml(path)
        if source.get("id") != source_id or source.get("status") != predecessor_status:
            return fail(f"immutable source registration changed: {source_id}")
        if source.get("witness_ids") != ["XEN-WIT-COMP-001"]:
            return fail(f"source does not retain the stable composite witness: {source_id}")
        if indexed[source_id].get("record") != str(path.relative_to(ROOT)):
            return fail(f"corpus index path mismatch: {source_id}")
        if indexed[source_id].get("status") != current_statuses[source_id]:
            return fail(f"current owner-adopted source status mismatch: {source_id}")
        if indexed[source_id].get("witness_ids") != ["XEN-WIT-COMP-001"]:
            return fail(f"corpus index changed the stable witness identity: {source_id}")

    predecessor_witness = load_yaml(PREDECESSOR_WITNESS)
    if predecessor_witness.get("id") != "XEN-WIT-COMP-001":
        return fail("composite witness identity mismatch")
    if predecessor_witness.get("source_ids") != list(SOURCE_RECORDS):
        return fail("composite witness source order or membership mismatch")
    predecessor_control = predecessor_witness.get("file_control", {})
    if predecessor_control.get("repository_deposition") != "not_deposited":
        return fail("predecessor registration falsely claims source deposition")
    if predecessor_control.get("sha256") != "not_preserved_in_current_repository_handoff":
        return fail("predecessor missing-hash history was silently rewritten")
    corrections = predecessor_witness.get("documentary_corrections", [])
    if len(corrections) != 1 or corrections[0].get("id") != "XEN-HIERON-DOC-COR-001":
        return fail("5 November 1957 documentary correction is not preserved")

    verification = load_yaml(WITNESS_VERIFICATION)
    if verification.get("verification_id") != "XEN-WIT-COMP-001-VERIFICATION-001":
        return fail("witness verification identity mismatch")
    if verification.get("applies_to_witness_id") != "XEN-WIT-COMP-001":
        return fail("witness verification does not retain the stable witness identity")
    recovered = verification.get("recovered_file", {})
    if recovered.get("sha256") != EXPECTED_SHA256 or recovered.get("byte_size") != 24279699:
        return fail("recovered witness byte identity mismatch")
    if recovered.get("physical_pdf_pages") != 354 or recovered.get("repository_deposition") != "not_deposited":
        return fail("recovered witness physical extent or deposition state mismatch")
    boundaries = verification.get("visual_and_textual_boundary_checks", [])
    if len(boundaries) != 13:
        return fail("witness verification does not preserve all thirteen boundary checks")
    if verification.get("verification_ruling", {}).get("documentary_correction") != "PASS":
        return fail("witness verification does not confirm the documentary correction")

    plan = load_yaml(READING_PLAN)
    if plan.get("study_id") != "XEN-STUDY-HIERON-OT-001":
        return fail("reading plan identity mismatch")
    if plan.get("status") != "COMPLETED_PRE_REPOSITORY_CLOSE_READING_REGISTERED_PENDING_OWNER_REVIEW":
        return fail("immutable reading-plan production state was rewritten")

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
        return fail("immutable artifact-index production state was rewritten")

    cumulative = load_yaml(CUMULATIVE)
    questions = cumulative.get("standing_unresolved_questions", [])
    if len(questions) != 18:
        return fail("eighteen unresolved questions are not preserved")
    limits = cumulative.get("governance_limits", {})
    if limits.get("owner_adopted") is not False:
        return fail("immutable cumulative predecessor status was rewritten")
    if limits.get("minister_adapter_expansion_authorized") is not False:
        return fail("Hieron package improperly expands the operational adapter")
    if limits.get("artificial_intelligence_self_certification_prohibited") is not True:
        return fail("AI self-certification prohibition is missing")

    directive = load_yaml(DIRECTIVE)
    if directive.get("directive_id") != "XEN-OWNER-DIRECTIVE-002":
        return fail("owner integration directive identity mismatch")
    distinction = directive.get("governing_distinction", {})
    if distinction.get("completed_close_reading") is not True:
        return fail("directive falsely reopens completed close reading")
    if distinction.get("repository_owner_adoption") != "pending_in_depth_review":
        return fail("immutable directive-stage adoption status was rewritten")

    predecessor_audit = load_yaml(PREDECESSOR_AUDIT)
    if predecessor_audit.get("audit_id") != "XEN-AUDIT-HIERON-OT-001":
        return fail("predecessor integration audit identity mismatch")
    predecessor_integration = predecessor_audit.get("repository_integration", {})
    if predecessor_integration.get("owner_directed") is not True or predecessor_integration.get("owner_adopted") is not False:
        return fail("predecessor audit was silently converted into adoption")

    detailed_review = load_yaml(DETAILED_REVIEW)
    if detailed_review.get("review_id") != "XEN-HIERON-OT-IN-DEPTH-REVIEW-001":
        return fail("detailed review identity mismatch")
    counts = detailed_review.get("disposition_counts", {})
    if counts != {"PASS": 10, "PASS_WITH_LIMIT": 3, "BLOCKING_REVISION": 0}:
        return fail("detailed review disposition counts mismatch")
    findings = detailed_review.get("findings", [])
    observed_counts = {
        "PASS": sum(item.get("severity") == "PASS" for item in findings),
        "PASS_WITH_LIMIT": sum(item.get("severity") == "PASS_WITH_LIMIT" for item in findings),
        "BLOCKING_REVISION": sum(item.get("severity") == "BLOCKING_REVISION" for item in findings),
    }
    if observed_counts != counts:
        return fail("detailed review findings do not match disposition counts")
    if detailed_review.get("overall_ruling", {}).get("disposition") != "PASS_RECOMMEND_OWNER_ADOPTION":
        return fail("detailed review does not recommend owner adoption")

    owner_review = load_yaml(OWNER_REVIEW)
    if owner_review.get("review_id") != "XEN-OWNER-REVIEW-013":
        return fail("owner-review sequence identity mismatch")
    if owner_review.get("status") != "OWNER_ADOPTED_HIERON_ON_TYRANNY_RECONSTRUCTION":
        return fail("owner review does not adopt the Hieron reconstruction")
    ruling = owner_review.get("owner_ruling", {})
    if ruling.get("adoption_status") != "ADOPTED_WITH_ENGLISH_COMPOSITE_WITNESS_JURISDICTION":
        return fail("owner review exceeds or omits English witness jurisdiction")
    if ruling.get("witness_status") != "OWNER_ADMITTED_EXTERNAL_COMPOSITE_ENGLISH_WITNESS":
        return fail("owner review does not admit the verified composite witness")
    if owner_review.get("scope", {}).get("unresolved_questions_preserved") != 18:
        return fail("owner review does not preserve all eighteen unresolved questions")

    current_audit = load_yaml(CURRENT_AUDIT)
    if current_audit.get("audit_id") != "XEN-AUDIT-HIERON-OT-002":
        return fail("owner-adoption predecessor audit identity mismatch")
    if current_audit.get("review_completion", {}).get("owner_adopted") is not True:
        return fail("owner-adoption predecessor audit does not record adoption")
    current_state = current_audit.get("current_repository_state", {})
    if current_state.get("active_adapter_source_line") != "Anabasis only" or current_state.get("active_adapter_effect") != "none":
        return fail("owner-adoption predecessor audit was silently rewritten")

    integration = index.get("hieron_on_tyranny_integration", {})
    if integration.get("status") != "OWNER_ADOPTED_WITH_ENGLISH_COMPOSITE_WITNESS_JURISDICTION":
        return fail("corpus index does not expose the current owner-adopted state")
    if integration.get("owner_review") != str(OWNER_REVIEW.relative_to(ROOT)):
        return fail("corpus index owner-review pointer mismatch")
    if integration.get("active_adapter_effect") != "none":
        return fail("corpus index improperly expands the operational adapter")
    if str(OWNER_REVIEW.relative_to(ROOT)) not in index.get("owner_reviews", []):
        return fail("corpus index does not register the owner review")

    operational_directive = load_yaml(OPERATIONAL_DIRECTIVE)
    if operational_directive.get("directive_id") != "XEN-OWNER-DIRECTIVE-003":
        return fail("Hieron operational-incorporation directive identity mismatch")
    if operational_directive.get("owner_instruction") != "no the proper step it to finish incorporating hieron":
        return fail("Hieron operational-incorporation directive does not preserve the owner instruction")

    boundary = load_yaml(DERIVATION_BOUNDARY)
    if boundary.get("boundary_id") != "XEN-HIERON-OT-DERIVATION-BOUNDARY-001":
        return fail("Hieron derivation boundary identity mismatch")
    operational_scope = boundary.get("operational_scope", {})
    primary = operational_scope.get("primary_work", {})
    later = operational_scope.get("later_source_roles", [])
    boundary_pairs = {(primary.get("witness_id"), primary.get("source_id"))}
    boundary_pairs.update((item.get("witness_id"), item.get("source_id")) for item in later)
    expected_hieron_pairs = {
        ("XEN-WIT-COMP-001", "XEN-SRC-PRI-002"),
        *{
            ("XEN-WIT-COMP-001", f"XEN-SRC-SEC-{number:03d}")
            for number in range(2, 7)
        },
    }
    if boundary_pairs != expected_hieron_pairs:
        return fail("Hieron derivation boundary does not preserve all six source roles")
    boundary_architecture = boundary.get("adapter_architecture", {})
    if boundary_architecture.get("preserved_registers") != [f"XEN-REGISTER-{number:03d}" for number in range(1, 5)]:
        return fail("Hieron boundary does not preserve the R1 registers")
    if boundary_architecture.get("added_registers") != ["XEN-REGISTER-005", "XEN-REGISTER-006"]:
        return fail("Hieron boundary does not add both Hieron registers")
    if boundary.get("unresolved_question_control", {}).get("combined_inventory_without_absorption") != 37:
        return fail("Hieron boundary does not preserve the separate unresolved inventories")

    adapter_review = load_yaml(ADAPTER_REVIEW)
    if adapter_review.get("review_id") != "XEN-MINISTER-ADAPTER-R2-IN-DEPTH-REVIEW-001":
        return fail("R2 Hieron adapter review identity mismatch")
    if adapter_review.get("disposition_counts") != {"PASS": 16, "PASS_WITH_LIMIT": 2, "BLOCKING_REVISION": 0}:
        return fail("R2 Hieron adapter review disposition mismatch")
    if adapter_review.get("overall_ruling", {}).get("disposition") != "PASS_RECOMMEND_OWNER_ADOPTION":
        return fail("R2 Hieron adapter review does not recommend adoption")

    adapter_owner_review = load_yaml(ADAPTER_OWNER_REVIEW)
    if adapter_owner_review.get("review_id") != "XEN-OWNER-REVIEW-014":
        return fail("R2 owner-review sequence identity mismatch")
    adapter_ruling = adapter_owner_review.get("owner_ruling", {})
    if adapter_ruling.get("adoption_status") != "ADOPTED" or adapter_ruling.get("operational_authorization") != "GRANTED_WITH_RECORDED_LIMITS":
        return fail("R2 owner review does not authorize operational Hieron incorporation")

    authorization = load_yaml(AUTHORIZATION)
    if authorization.get("authorization_id") != "XENOPHON-AUTH-002":
        return fail("R2 repository authorization identity mismatch")
    if authorization.get("status") != "ACTIVE_OWNER_AUTHORIZATION":
        return fail("R2 repository authorization is not active")
    auth_scope = authorization.get("scope", {})
    if auth_scope.get("source_lines") != ["anabasis", "hieron_on_tyranny"]:
        return fail("R2 authorization does not include both source lines")
    if (auth_scope.get("authorized_source_witness_pairs"), auth_scope.get("registers"), auth_scope.get("guards"), auth_scope.get("evidence_layers"), auth_scope.get("unresolved_question_count")) != (8, 6, 4, 8, 37):
        return fail("R2 authorization inventory mismatch")

    operational_audit = load_yaml(OPERATIONAL_AUDIT)
    if operational_audit.get("audit_id") != "XEN-AUDIT-HIERON-OT-003":
        return fail("Hieron operational-incorporation audit identity mismatch")
    if operational_audit.get("status") != "OPERATIONAL_INCORPORATION_COMPLETE_OWNER_AUTHORIZED":
        return fail("Hieron operational incorporation is not complete")
    if operational_audit.get("incorporation", {}).get("source_line_status") != "OPERATIONALLY_INCORPORATED":
        return fail("Hieron source line is not operationally incorporated")

    print("Hieron / On Tyranny operational-incorporation validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
