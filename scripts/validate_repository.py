from __future__ import annotations

from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
SECONDARY_OWNER_REVIEW = ROOT / "governance/owner-reviews/2026-07-30-strauss-witness-review.yaml"
PRIMARY_ADMISSION = ROOT / "governance/owner-reviews/2026-07-30-primary-anabasis-witness-admission.yaml"
SECONDARY_UNIT_IDS = [f"XEN-RU-{number:03d}" for number in range(1, 9)]
PRIMARY_UNIT_IDS = [f"XEN-PRI-RU-{number:03d}" for number in range(1, 13)]
PRIMARY_UNIT_PATHS = {
    unit_id: ROOT / f"studies/xenophon-anabasis-dakyns/units/{unit_id}.yaml"
    for unit_id in PRIMARY_UNIT_IDS
}
PRIMARY_READING_PLAN = ROOT / "studies/xenophon-anabasis-dakyns/reading-plan.yaml"
NEXT_PRIMARY_UNIT_ID = "XEN-PRI-RU-013"

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


def validate_reading_unit(record: dict, unit_id: str) -> str | None:
    if record.get("unit_id") != unit_id:
        return f"Primary unit identifier mismatch for {unit_id}"
    if record.get("status") != "DRAFTED_PENDING_OWNER_REVIEW":
        return f"Primary unit status mismatch for {unit_id}"
    jurisdiction = record.get("jurisdiction", "")
    if "Translator wording is not unmediated Greek evidence" not in jurisdiction:
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
        print("manifest.yaml must contain a mapping")
        return 1
    if manifest.get("artificial_intelligence_self_certification_prohibited") is not True:
        print("AI self-certification safeguard must remain true")
        return 1
    if manifest.get("version") != "1.12.0":
        print("Manifest version must be 1.12.0 after drafting Anabasis II.2")
        return 1
    if manifest.get("state") != "PRIMARY_RECONSTRUCTION_IN_PROGRESS":
        print("Manifest primary reconstruction state mismatch")
        return 1
    if manifest.get("next_required_unit", {}).get("id") != NEXT_PRIMARY_UNIT_ID:
        print("Manifest next primary unit mismatch")
        return 1

    corpus = documents[ROOT / "corpus/index.yaml"]
    expected_counts = {
        "primary_sources": 1,
        "secondary_sources": 1,
        "registered_witnesses": 2,
    }
    if corpus.get("counts") != expected_counts:
        print("Corpus counts mismatch")
        return 1
    if corpus.get("primary_original_language_gap", {}).get("status") != "DOCUMENTED_GAP":
        print("Original-language witness gap must remain documented")
        return 1

    secondary_source = documents[ROOT / "corpus/sources/strauss-xenophons-anabasis.yaml"]
    if secondary_source.get("status") != "OWNER_ADOPTED_SECONDARY_SOURCE":
        print("Secondary source owner-adoption status mismatch")
        return 1

    secondary_witness = documents[ROOT / "corpus/witnesses/strauss-spp-1983.yaml"]
    if secondary_witness.get("status") != "OWNER_ADOPTED_SECONDARY_WITNESS":
        print("Secondary witness owner-adoption status mismatch")
        return 1

    primary_source = documents[ROOT / "corpus/sources/xenophon-anabasis.yaml"]
    if primary_source.get("status") != "OWNER_ADMITTED_PRIMARY_TRANSLATION_SOURCE":
        print("Primary source admission status mismatch")
        return 1
    if primary_source.get("work", {}).get("author") != "Xenophon":
        print("Primary source author mismatch")
        return 1
    if primary_source.get("edition", {}).get("translator") != "H. G. Dakyns":
        print("Primary source translator mismatch")
        return 1

    primary_witness = documents[ROOT / "corpus/witnesses/gutenberg-1170-dakyns-pdf.yaml"]
    if primary_witness.get("status") != "OWNER_ADMITTED_PRIMARY_TRANSLATION_WITNESS":
        print("Primary witness admission status mismatch")
        return 1
    if primary_witness.get("source_id") != "XEN-SRC-PRI-001":
        print("Primary witness/source linkage mismatch")
        return 1
    if primary_witness.get("witness", {}).get("page_count") != 168:
        print("Primary witness page count mismatch")
        return 1
    if primary_witness.get("file_control", {}).get("sha256") != "6a7534d8d80153afc1623803ef129185aa8d3d41be692091f4e105375c65901e":
        print("Primary witness SHA-256 mismatch")
        return 1

    secondary_owner_review = documents[SECONDARY_OWNER_REVIEW]
    if secondary_owner_review.get("status") != "OWNER_ADOPTED_SECONDARY_RECONSTRUCTION":
        print("Secondary owner review status mismatch")
        return 1
    if secondary_owner_review.get("scope", {}).get("units") != SECONDARY_UNIT_IDS:
        print("Secondary owner review unit scope mismatch")
        return 1

    primary_admission = documents[PRIMARY_ADMISSION]
    if primary_admission.get("status") != "OWNER_ADMITTED_PRIMARY_TRANSLATION_WITNESS":
        print("Primary admission record status mismatch")
        return 1
    if primary_admission.get("scope", {}).get("initial_unit") != PRIMARY_UNIT_IDS[0]:
        print("Primary admission initial-unit mismatch")
        return 1
    if primary_admission.get("limits", [])[-1:] != ["Artificial-intelligence self-certification remains prohibited."]:
        print("Primary admission safeguard missing")
        return 1

    secondary_reading_plan = documents[ROOT / "studies/strauss-xenophons-anabasis/reading-plan.yaml"]
    if secondary_reading_plan.get("status") != "OWNER_ADOPTED_SECONDARY_RECONSTRUCTION":
        print("Secondary reading plan owner-adoption status mismatch")
        return 1
    drafted_secondary = [
        unit["id"]
        for unit in secondary_reading_plan["reading_units"]
        if unit.get("status") == "DRAFTED_PENDING_OWNER_REVIEW"
    ]
    if drafted_secondary != SECONDARY_UNIT_IDS:
        print("Secondary drafted-unit order mismatch")
        return 1

    primary_reading_plan = documents[PRIMARY_READING_PLAN]
    if primary_reading_plan.get("status") != "SEQUENTIAL_PRIMARY_READING_IN_PROGRESS_PENDING_OWNER_REVIEW":
        print("Primary reading plan status mismatch")
        return 1
    primary_units = primary_reading_plan.get("reading_units", [])
    expected_plan_ids = [*PRIMARY_UNIT_IDS, NEXT_PRIMARY_UNIT_ID]
    if [unit.get("id") for unit in primary_units] != expected_plan_ids:
        print("Primary reading plan unit order mismatch")
        return 1

    expected_book_one_locators = [f"Anabasis I.{number}" for number in range(1, 11)]
    drafted_book_one_locators = [unit.get("work_locator") for unit in primary_units[:10]]
    if drafted_book_one_locators != expected_book_one_locators:
        print("Primary Book I locator sequence mismatch")
        return 1

    expected_book_two_locators = ["Anabasis II.1", "Anabasis II.2"]
    drafted_book_two_locators = [unit.get("work_locator") for unit in primary_units[10:12]]
    if drafted_book_two_locators != expected_book_two_locators:
        print("Primary drafted Book II locator sequence mismatch")
        return 1
    if primary_units[-1].get("work_locator") != "Anabasis II.3":
        print("Next primary locator must be Anabasis II.3")
        return 1

    drafted_plan_ids = [
        unit.get("id")
        for unit in primary_units
        if unit.get("status") == "DRAFTED_PENDING_OWNER_REVIEW"
    ]
    if drafted_plan_ids != PRIMARY_UNIT_IDS:
        print("Primary drafted-unit order mismatch")
        return 1
    next_plan_ids = [unit.get("id") for unit in primary_units if unit.get("status") == "NEXT"]
    if next_plan_ids != [NEXT_PRIMARY_UNIT_ID]:
        print("Primary next-unit status mismatch")
        return 1
    if primary_reading_plan.get("comparison_gate", {}).get("strauss_comparison") != "DEFERRED":
        print("Strauss comparison must remain deferred")
        return 1

    for unit_id, unit_path in PRIMARY_UNIT_PATHS.items():
        record = documents[unit_path]
        if not isinstance(record, dict):
            print(f"Primary unit {unit_id} must contain a mapping")
            return 1
        error = validate_reading_unit(record, unit_id)
        if error:
            print(error)
            return 1

    unit_011 = documents[PRIMARY_UNIT_PATHS["XEN-PRI-RU-011"]]
    if unit_011.get("narrative_person_and_authorial_attribution", {}).get("xenophon_as_character_present") != "TEXTUALLY_DISPUTED":
        print("Anabasis II.1 Theopompus/Xenophon attribution uncertainty must remain preserved")
        return 1

    unit_012 = documents[PRIMARY_UNIT_PATHS["XEN-PRI-RU-012"]]
    evidence_types_012 = {
        observation.get("evidence_type")
        for observation in unit_012.get("documentary_observations", [])
    }
    if "TEXTUAL_VARIANT_OBSERVATION" not in evidence_types_012:
        print("Anabasis II.2 wolf textual variant must remain documented")
        return 1
    if not any(
        "fortune proved a better general" in observation.get("observation", "")
        for observation in unit_012.get("documentary_observations", [])
    ):
        print("Anabasis II.2 narratorial judgment must remain represented")
        return 1

    if manifest.get("primary_study", {}).get("drafted_units") != PRIMARY_UNIT_IDS:
        print("Manifest primary drafted-unit list mismatch")
        return 1
    if manifest.get("secondary_study", {}).get("drafted_units") != SECONDARY_UNIT_IDS:
        print("Manifest secondary drafted-unit order mismatch")
        return 1

    audit = documents[ROOT / "audits/founding-state.yaml"]
    state = audit.get("repository_state", {})
    if state.get("primary_witness_count") != 1:
        print("Founding audit primary witness count mismatch")
        return 1
    if state.get("drafted_primary_units") != len(PRIMARY_UNIT_IDS):
        print("Founding audit primary unit count mismatch")
        return 1
    if state.get("drafted_secondary_units") != 8:
        print("Founding audit secondary unit count mismatch")
        return 1
    if state.get("book_one_primary_draft_complete") is not True:
        print("Founding audit must record complete Book I draft coverage")
        return 1
    if state.get("book_two_drafted_chapters") != ["II.1", "II.2"]:
        print("Founding audit Book II coverage mismatch")
        return 1
    if state.get("minister_adapter_derived") is not False:
        print("Adapter must remain underived")
        return 1

    print("Xenophon repository validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
