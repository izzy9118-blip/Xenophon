from __future__ import annotations

from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
SECONDARY_OWNER_REVIEW = ROOT / "governance/owner-reviews/2026-07-30-strauss-witness-review.yaml"
PRIMARY_ADMISSION = ROOT / "governance/owner-reviews/2026-07-30-primary-anabasis-witness-admission.yaml"
SECONDARY_UNIT_IDS = [f"XEN-RU-{number:03d}" for number in range(1, 9)]
PRIMARY_UNIT_IDS = [f"XEN-PRI-RU-{number:03d}" for number in range(1, 12)]
PRIMARY_UNIT_PATHS = {
    unit_id: ROOT / f"studies/xenophon-anabasis-dakyns/units/{unit_id}.yaml"
    for unit_id in PRIMARY_UNIT_IDS
}
PRIMARY_READING_PLAN = ROOT / "studies/xenophon-anabasis-dakyns/reading-plan.yaml"
NEXT_PRIMARY_UNIT_ID = "XEN-PRI-RU-012"

REQUIRED = [
    ROOT / "manifest.yaml",
    ROOT / "method/source-hierarchy.yaml",
    ROOT / "method/reading-protocol.yaml",
    ROOT / "corpus/index.yaml",
    ROOT / "corpus/sources/strauss-xenophons-anabasis.yaml",
    ROOT / "corpus/witnesses/strauss-spp-1983.yaml",
    ROOT / "corpus/sources/xenophon-anabasis.yaml",
    ROOT / "corpus/witnesses/gutenberg-1170-dakyns-pdf.yaml",
    ROOT / "studies/strauss-xenophons-anabasis/reading-plan.yaml",
    *[
        ROOT / f"studies/strauss-xenophons-anabasis/units/{unit_id}.yaml"
        for unit_id in SECONDARY_UNIT_IDS
    ],
    PRIMARY_READING_PLAN,
    *PRIMARY_UNIT_PATHS.values(),
    ROOT / "adapter/report-contract.yaml",
    ROOT / "audits/founding-state.yaml",
    SECONDARY_OWNER_REVIEW,
    PRIMARY_ADMISSION,
    ROOT / "history/2026-07-30-primary-anabasis-witness-record.md",
]


def load_yaml(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def fail(message: str) -> int:
    print(message)
    return 1


def validate_reading_unit(record: dict, unit_id: str) -> str | None:
    if record.get("unit_id") != unit_id:
        return f"Primary unit identifier mismatch for {unit_id}"
    if record.get("status") != "DRAFTED_PENDING_OWNER_REVIEW":
        return f"Primary unit status mismatch for {unit_id}"
    if "Translator wording is not unmediated Greek evidence" not in record.get("jurisdiction", ""):
        return f"Primary translation jurisdiction missing for {unit_id}"
    if record.get("secondary_comparison_status") != "DEFERRED":
        return f"Primary unit secondary comparison must remain deferred for {unit_id}"
    required_sections = [
        "bibliographic_and_witness_control",
        "narrative_person_and_authorial_attribution",
        "speakers_audiences_and_occasions",
        "speeches_deeds_and_outcomes",
        "sequence_repetition_omission_and_contradiction",
        "documentary_observations",
        "provisional_findings",
        "standing_unresolved_questions",
        "downstream_textual_checks",
    ]
    for section in required_sections:
        if not record.get(section):
            return f"Required primary section {section} missing for {unit_id}"
    for observation in record["documentary_observations"]:
        if not observation.get("locator") or not observation.get("evidence_type"):
            return f"Untyped or unlocated primary observation in {unit_id}"
    for finding in record["provisional_findings"]:
        if finding.get("evidence_type") != "PROVISIONAL_INFERENCE":
            return f"Primary provisional finding must be typed in {unit_id}"
    for question in record["standing_unresolved_questions"]:
        if question.get("evidence_type") != "UNRESOLVED_QUESTION":
            return f"Primary unresolved question must be typed in {unit_id}"
    return None


def main() -> int:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED if not path.exists()]
    if missing:
        print("Missing required files:", *missing, sep="\n- ")
        return 1

    yaml_paths = [path for path in REQUIRED if path.suffix in {".yaml", ".yml"}]
    documents = {path: load_yaml(path) for path in yaml_paths}

    manifest = documents[ROOT / "manifest.yaml"]
    if not isinstance(manifest, dict):
        return fail("manifest.yaml must contain a mapping")
    if manifest.get("artificial_intelligence_self_certification_prohibited") is not True:
        return fail("AI self-certification safeguard must remain true")
    if manifest.get("version") != "1.11.0":
        return fail("Manifest version must be 1.11.0 after drafting Anabasis II.1")
    if manifest.get("state") != "PRIMARY_RECONSTRUCTION_IN_PROGRESS":
        return fail("Manifest primary reconstruction state mismatch")
    if manifest.get("next_required_unit", {}).get("id") != NEXT_PRIMARY_UNIT_ID:
        return fail("Manifest next primary unit mismatch")
    if manifest.get("primary_study", {}).get("book_one_draft_complete") is not True:
        return fail("Manifest must preserve the Book I draft milestone")

    corpus = documents[ROOT / "corpus/index.yaml"]
    if corpus.get("counts") != {
        "primary_sources": 1,
        "secondary_sources": 1,
        "registered_witnesses": 2,
    }:
        return fail("Corpus counts mismatch")
    if corpus.get("primary_original_language_gap", {}).get("status") != "DOCUMENTED_GAP":
        return fail("Original-language witness gap must remain documented")

    secondary_source = documents[ROOT / "corpus/sources/strauss-xenophons-anabasis.yaml"]
    secondary_witness = documents[ROOT / "corpus/witnesses/strauss-spp-1983.yaml"]
    if secondary_source.get("status") != "OWNER_ADOPTED_SECONDARY_SOURCE":
        return fail("Secondary source owner-adoption status mismatch")
    if secondary_witness.get("status") != "OWNER_ADOPTED_SECONDARY_WITNESS":
        return fail("Secondary witness owner-adoption status mismatch")

    primary_source = documents[ROOT / "corpus/sources/xenophon-anabasis.yaml"]
    primary_witness = documents[ROOT / "corpus/witnesses/gutenberg-1170-dakyns-pdf.yaml"]
    if primary_source.get("status") != "OWNER_ADMITTED_PRIMARY_TRANSLATION_SOURCE":
        return fail("Primary source admission status mismatch")
    if primary_source.get("work", {}).get("author") != "Xenophon":
        return fail("Primary source author mismatch")
    if primary_source.get("edition", {}).get("translator") != "H. G. Dakyns":
        return fail("Primary source translator mismatch")
    if primary_witness.get("status") != "OWNER_ADMITTED_PRIMARY_TRANSLATION_WITNESS":
        return fail("Primary witness admission status mismatch")
    if primary_witness.get("source_id") != "XEN-SRC-PRI-001":
        return fail("Primary witness/source linkage mismatch")
    if primary_witness.get("witness", {}).get("page_count") != 168:
        return fail("Primary witness page count mismatch")
    if primary_witness.get("file_control", {}).get("sha256") != "6a7534d8d80153afc1623803ef129185aa8d3d41be692091f4e105375c65901e":
        return fail("Primary witness SHA-256 mismatch")

    secondary_owner_review = documents[SECONDARY_OWNER_REVIEW]
    primary_admission = documents[PRIMARY_ADMISSION]
    if secondary_owner_review.get("status") != "OWNER_ADOPTED_SECONDARY_RECONSTRUCTION":
        return fail("Secondary owner review status mismatch")
    if secondary_owner_review.get("scope", {}).get("units") != SECONDARY_UNIT_IDS:
        return fail("Secondary owner review unit scope mismatch")
    if primary_admission.get("status") != "OWNER_ADMITTED_PRIMARY_TRANSLATION_WITNESS":
        return fail("Primary admission record status mismatch")
    if primary_admission.get("scope", {}).get("initial_unit") != PRIMARY_UNIT_IDS[0]:
        return fail("Primary admission initial-unit mismatch")
    if primary_admission.get("limits", [])[-1:] != ["Artificial-intelligence self-certification remains prohibited."]:
        return fail("Primary admission safeguard missing")

    secondary_plan = documents[ROOT / "studies/strauss-xenophons-anabasis/reading-plan.yaml"]
    if secondary_plan.get("status") != "OWNER_ADOPTED_SECONDARY_RECONSTRUCTION":
        return fail("Secondary reading plan owner-adoption status mismatch")
    drafted_secondary = [
        unit["id"] for unit in secondary_plan["reading_units"]
        if unit.get("status") == "DRAFTED_PENDING_OWNER_REVIEW"
    ]
    if drafted_secondary != SECONDARY_UNIT_IDS:
        return fail("Secondary drafted-unit order mismatch")

    primary_plan = documents[PRIMARY_READING_PLAN]
    if primary_plan.get("status") != "SEQUENTIAL_PRIMARY_READING_IN_PROGRESS_PENDING_OWNER_REVIEW":
        return fail("Primary reading plan status mismatch")
    primary_units = primary_plan.get("reading_units", [])
    expected_ids = [*PRIMARY_UNIT_IDS, NEXT_PRIMARY_UNIT_ID]
    if [unit.get("id") for unit in primary_units] != expected_ids:
        return fail("Primary reading plan unit order mismatch")
    if [unit.get("work_locator") for unit in primary_units[:10]] != [f"Anabasis I.{n}" for n in range(1, 11)]:
        return fail("Primary Book I locator sequence mismatch")
    if primary_units[10].get("work_locator") != "Anabasis II.1":
        return fail("Drafted Book II opening locator mismatch")
    if primary_units[10].get("pdf_pages_one_based") != "31-34":
        return fail("Anabasis II.1 page range mismatch")
    if primary_units[-1].get("work_locator") != "Anabasis II.2":
        return fail("Next primary locator mismatch")
    drafted_ids = [
        unit.get("id") for unit in primary_units
        if unit.get("status") == "DRAFTED_PENDING_OWNER_REVIEW"
    ]
    if drafted_ids != PRIMARY_UNIT_IDS:
        return fail("Primary drafted-unit order mismatch")
    if [unit.get("id") for unit in primary_units if unit.get("status") == "NEXT"] != [NEXT_PRIMARY_UNIT_ID]:
        return fail("Primary next-unit status mismatch")
    if primary_plan.get("comparison_gate", {}).get("strauss_comparison") != "DEFERRED":
        return fail("Strauss comparison must remain deferred")

    for unit_id, unit_path in PRIMARY_UNIT_PATHS.items():
        record = documents[unit_path]
        if not isinstance(record, dict):
            return fail(f"Primary unit {unit_id} must contain a mapping")
        error = validate_reading_unit(record, unit_id)
        if error:
            return fail(error)

    if manifest.get("primary_study", {}).get("drafted_units") != PRIMARY_UNIT_IDS:
        return fail("Manifest primary drafted-unit list mismatch")
    if manifest.get("secondary_study", {}).get("drafted_units") != SECONDARY_UNIT_IDS:
        return fail("Manifest secondary drafted-unit order mismatch")

    audit = documents[ROOT / "audits/founding-state.yaml"]
    state = audit.get("repository_state", {})
    if state.get("primary_witness_count") != 1:
        return fail("Founding audit primary witness count mismatch")
    if state.get("drafted_primary_units") != len(PRIMARY_UNIT_IDS):
        return fail("Founding audit primary unit count mismatch")
    if state.get("drafted_secondary_units") != 8:
        return fail("Founding audit secondary unit count mismatch")
    if state.get("book_one_primary_draft_complete") is not True:
        return fail("Founding audit must preserve complete Book I draft coverage")
    if state.get("book_two_primary_units_drafted") != 1:
        return fail("Founding audit Book II unit count mismatch")
    if state.get("minister_adapter_derived") is not False:
        return fail("Adapter must remain underived")

    print("Xenophon repository validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
