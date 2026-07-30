from __future__ import annotations

from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
SECONDARY_OWNER_REVIEW = ROOT / "governance/owner-reviews/2026-07-30-strauss-witness-review.yaml"
PRIMARY_ADMISSION = ROOT / "governance/owner-reviews/2026-07-30-primary-anabasis-witness-admission.yaml"
SECONDARY_UNIT_IDS = [f"XEN-RU-{number:03d}" for number in range(1, 9)]
PRIMARY_UNIT_IDS = [f"XEN-PRI-RU-{number:03d}" for number in range(1, 18)]
PRIMARY_UNIT_PATHS = {
    unit_id: ROOT / f"studies/xenophon-anabasis-dakyns/units/{unit_id}.yaml"
    for unit_id in PRIMARY_UNIT_IDS
}
PRIMARY_READING_PLAN = ROOT / "studies/xenophon-anabasis-dakyns/reading-plan.yaml"
NEXT_PRIMARY_UNIT_ID = "XEN-PRI-RU-018"

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


def evidence_types(record: dict) -> set[str]:
    return {
        observation.get("evidence_type")
        for observation in record.get("documentary_observations", [])
    }


def observations(record: dict) -> list[str]:
    return [
        observation.get("observation", "")
        for observation in record.get("documentary_observations", [])
    ]


def main() -> int:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED if not path.exists()]
    if missing:
        print("Missing required files:", *missing, sep="\n- ")
        return 1

    documents = {
        path: load_yaml(path)
        for path in REQUIRED
        if path.suffix in {".yaml", ".yml"}
    }

    manifest = documents[ROOT / "manifest.yaml"]
    if not isinstance(manifest, dict):
        return fail("manifest.yaml must contain a mapping")
    if manifest.get("artificial_intelligence_self_certification_prohibited") is not True:
        return fail("AI self-certification safeguard must remain true")
    if manifest.get("version") != "1.17.0":
        return fail("Manifest version must be 1.17.0 after drafting Anabasis III.1")
    if manifest.get("state") != "PRIMARY_RECONSTRUCTION_IN_PROGRESS":
        return fail("Manifest primary reconstruction state mismatch")
    if manifest.get("next_required_unit", {}).get("id") != NEXT_PRIMARY_UNIT_ID:
        return fail("Manifest next primary unit mismatch")
    primary_manifest = manifest.get("primary_study", {})
    if primary_manifest.get("book_one_draft_complete_pending_owner_review") is not True:
        return fail("Manifest must preserve complete Book I draft coverage pending owner review")
    if primary_manifest.get("book_two_draft_complete_pending_owner_review") is not True:
        return fail("Manifest must preserve complete Book II draft coverage pending owner review")
    if primary_manifest.get("book_three_drafted_chapters") != ["III.1"]:
        return fail("Manifest Book III draft coverage mismatch")

    corpus = documents[ROOT / "corpus/index.yaml"]
    if corpus.get("counts") != {
        "primary_sources": 1,
        "secondary_sources": 1,
        "registered_witnesses": 2,
    }:
        return fail("Corpus counts mismatch")
    if corpus.get("primary_original_language_gap", {}).get("status") != "DOCUMENTED_GAP":
        return fail("Original-language witness gap must remain documented")
    if documents[ROOT / "corpus/sources/strauss-xenophons-anabasis.yaml"].get("status") != "OWNER_ADOPTED_SECONDARY_SOURCE":
        return fail("Secondary source owner-adoption status mismatch")
    if documents[ROOT / "corpus/witnesses/strauss-spp-1983.yaml"].get("status") != "OWNER_ADOPTED_SECONDARY_WITNESS":
        return fail("Secondary witness owner-adoption status mismatch")

    primary_source = documents[ROOT / "corpus/sources/xenophon-anabasis.yaml"]
    if primary_source.get("status") != "OWNER_ADMITTED_PRIMARY_TRANSLATION_SOURCE":
        return fail("Primary source admission status mismatch")
    if primary_source.get("work", {}).get("author") != "Xenophon":
        return fail("Primary source author mismatch")
    if primary_source.get("edition", {}).get("translator") != "H. G. Dakyns":
        return fail("Primary source translator mismatch")

    primary_witness = documents[ROOT / "corpus/witnesses/gutenberg-1170-dakyns-pdf.yaml"]
    if primary_witness.get("status") != "OWNER_ADMITTED_PRIMARY_TRANSLATION_WITNESS":
        return fail("Primary witness admission status mismatch")
    if primary_witness.get("source_id") != "XEN-SRC-PRI-001":
        return fail("Primary witness/source linkage mismatch")
    if primary_witness.get("witness", {}).get("page_count") != 168:
        return fail("Primary witness page count mismatch")
    if primary_witness.get("file_control", {}).get("sha256") != "6a7534d8d80153afc1623803ef129185aa8d3d41be692091f4e105375c65901e":
        return fail("Primary witness SHA-256 mismatch")

    secondary_review = documents[SECONDARY_OWNER_REVIEW]
    if secondary_review.get("status") != "OWNER_ADOPTED_SECONDARY_RECONSTRUCTION":
        return fail("Secondary owner review status mismatch")
    if secondary_review.get("scope", {}).get("units") != SECONDARY_UNIT_IDS:
        return fail("Secondary owner review unit scope mismatch")

    primary_admission = documents[PRIMARY_ADMISSION]
    if primary_admission.get("status") != "OWNER_ADMITTED_PRIMARY_TRANSLATION_WITNESS":
        return fail("Primary admission record status mismatch")
    if primary_admission.get("scope", {}).get("initial_unit") != PRIMARY_UNIT_IDS[0]:
        return fail("Primary admission initial-unit mismatch")
    if primary_admission.get("limits", [])[-1:] != [
        "Artificial-intelligence self-certification remains prohibited."
    ]:
        return fail("Primary admission safeguard missing")

    secondary_plan = documents[ROOT / "studies/strauss-xenophons-anabasis/reading-plan.yaml"]
    if secondary_plan.get("status") != "OWNER_ADOPTED_SECONDARY_RECONSTRUCTION":
        return fail("Secondary reading plan owner-adoption status mismatch")
    drafted_secondary = [
        unit["id"]
        for unit in secondary_plan["reading_units"]
        if unit.get("status") == "DRAFTED_PENDING_OWNER_REVIEW"
    ]
    if drafted_secondary != SECONDARY_UNIT_IDS:
        return fail("Secondary drafted-unit order mismatch")

    plan = documents[PRIMARY_READING_PLAN]
    if plan.get("status") != "SEQUENTIAL_PRIMARY_READING_IN_PROGRESS_PENDING_OWNER_REVIEW":
        return fail("Primary reading plan status mismatch")
    units = plan.get("reading_units", [])
    if [unit.get("id") for unit in units] != [*PRIMARY_UNIT_IDS, NEXT_PRIMARY_UNIT_ID]:
        return fail("Primary reading plan unit order mismatch")
    if [unit.get("work_locator") for unit in units[:10]] != [
        f"Anabasis I.{number}" for number in range(1, 11)
    ]:
        return fail("Primary Book I locator sequence mismatch")
    if [unit.get("work_locator") for unit in units[10:16]] != [
        f"Anabasis II.{number}" for number in range(1, 7)
    ]:
        return fail("Primary Book II locator sequence mismatch")
    if [unit.get("work_locator") for unit in units[16:17]] != ["Anabasis III.1"]:
        return fail("Primary drafted Book III locator sequence mismatch")
    if units[-1].get("work_locator") != "Anabasis III.2":
        return fail("Next primary locator must be Anabasis III.2")
    if [
        unit.get("id")
        for unit in units
        if unit.get("status") == "DRAFTED_PENDING_OWNER_REVIEW"
    ] != PRIMARY_UNIT_IDS:
        return fail("Primary drafted-unit order mismatch")
    if [unit.get("id") for unit in units if unit.get("status") == "NEXT"] != [NEXT_PRIMARY_UNIT_ID]:
        return fail("Primary next-unit status mismatch")
    if plan.get("comparison_gate", {}).get("strauss_comparison") != "DEFERRED":
        return fail("Strauss comparison must remain deferred")

    for unit_id, unit_path in PRIMARY_UNIT_PATHS.items():
        record = documents[unit_path]
        if not isinstance(record, dict):
            return fail(f"Primary unit {unit_id} must contain a mapping")
        error = validate_reading_unit(record, unit_id)
        if error:
            return fail(error)

    unit11 = documents[PRIMARY_UNIT_PATHS["XEN-PRI-RU-011"]]
    if unit11.get("narrative_person_and_authorial_attribution", {}).get("xenophon_as_character_present") != "TEXTUALLY_DISPUTED":
        return fail("Anabasis II.1 Theopompus/Xenophon attribution uncertainty must remain preserved")

    unit12 = documents[PRIMARY_UNIT_PATHS["XEN-PRI-RU-012"]]
    if "TEXTUAL_VARIANT_OBSERVATION" not in evidence_types(unit12):
        return fail("Anabasis II.2 wolf textual variant must remain documented")
    if not any("fortune proved a better general" in text for text in observations(unit12)):
        return fail("Anabasis II.2 narratorial judgment must remain represented")

    unit13 = documents[PRIMARY_UNIT_PATHS["XEN-PRI-RU-013"]]
    if unit13.get("narrative_person_and_authorial_attribution", {}).get("first_person_narrator_present") is not True:
        return fail("Anabasis II.3 first-person narratorial intervention must remain represented")

    unit14 = documents[PRIMARY_UNIT_PATHS["XEN-PRI-RU-014"]]
    narrative14 = unit14.get("narrative_person_and_authorial_attribution", {})
    if narrative14.get("xenophon_as_character_present") is not True:
        return fail("Anabasis II.4 named Xenophon appearance must remain represented")
    if "possibly Xenophon" not in narrative14.get("textually_disputed_or_conjectural_identification", ""):
        return fail("Anabasis II.4 conjectural young-man identification must remain preserved")
    for required in {
        "FALSE_REPORT_OBSERVATION",
        "NARRATORIAL_INFERENCE_OBSERVATION",
        "NARRATORIAL_JUDGMENT_OBSERVATION",
    }:
        if required not in evidence_types(unit14):
            return fail(f"Anabasis II.4 evidence type missing: {required}")

    unit15 = documents[PRIMARY_UNIT_PATHS["XEN-PRI-RU-015"]]
    if unit15.get("narrative_person_and_authorial_attribution", {}).get("xenophon_as_character_present") is not True:
        return fail("Anabasis II.5 named Xenophon appearance must remain represented")
    for required in {
        "NARRATORIAL_STATUS_OBSERVATION",
        "WARNING_OBSERVATION",
        "VIOLENT_OUTCOME_OBSERVATION",
        "CONFLICTING_REPORT_OBSERVATION",
    }:
        if required not in evidence_types(unit15):
            return fail(f"Anabasis II.5 evidence type missing: {required}")
    if not any("tiara" in text and "heart" in text for text in observations(unit15)):
        return fail("Anabasis II.5 tiara-and-heart image must remain represented")
    if not any("Proxenus and Menon" in text and "honor" in text for text in observations(unit15)):
        return fail("Anabasis II.5 conflicting report about Proxenus and Menon must remain represented")

    unit16 = documents[PRIMARY_UNIT_PATHS["XEN-PRI-RU-016"]]
    narrative16 = unit16.get("narrative_person_and_authorial_attribution", {})
    if narrative16.get("first_person_narrator_present") is not True:
        return fail("Anabasis II.6 first-person narratorial judgments must remain represented")
    if narrative16.get("xenophon_as_character_present") is not False:
        return fail("Anabasis II.6 must not invent Xenophon as a character")
    for required in {
        "FIRST_PERSON_JUDGMENT_OBSERVATION",
        "EVIDENTIARY_LIMITATION_OBSERVATION",
        "REPORT_STATUS_OBSERVATION",
    }:
        if required not in evidence_types(unit16):
            return fail(f"Anabasis II.6 evidence type missing: {required}")
    tensions16 = unit16.get("sequence_repetition_omission_and_contradiction", {}).get("tensions", [])
    if not any("opening says" in text and "Menon" in text for text in tensions16):
        return fail("Anabasis II.6 collective-death and Menon qualification must remain preserved")

    unit17 = documents[PRIMARY_UNIT_PATHS["XEN-PRI-RU-017"]]
    narrative17 = unit17.get("narrative_person_and_authorial_attribution", {})
    if narrative17.get("xenophon_as_character_present") is not True:
        return fail("Anabasis III.1 named Xenophon appearance must remain represented")
    if narrative17.get("direct_authorial_self_identification_present") is not True:
        return fail("Anabasis III.1 first-person self-identification must remain represented")
    if narrative17.get("first_person_narrator_present") is not True:
        return fail("Anabasis III.1 first-person narration must remain represented")
    required17 = {
        "EDITORIAL_PARATEXT_OBSERVATION",
        "FIRST_PERSON_SELF_REFERENCE_OBSERVATION",
        "DREAM_REPORT_OBSERVATION",
        "DREAM_INTERPRETATION_OBSERVATION",
        "ETHNIC_IDENTITY_CLAIM_OBSERVATION",
        "ELECTION_OUTCOME_OBSERVATION",
    }
    for required in required17:
        if required not in evidence_types(unit17):
            return fail(f"Anabasis III.1 evidence type missing: {required}")
    texts17 = observations(unit17)
    if not any("my friendship with Cyrus" in text for text in texts17):
        return fail("Anabasis III.1 first-person friendship phrase must remain represented")
    if not any("fatherland" in text and "Proxenus" in text for text in texts17):
        return fail("Anabasis III.1 Proxenus fatherland statement must remain represented")
    if not any("Xenophon the Athenian replaces Proxenus" in text for text in texts17):
        return fail("Anabasis III.1 election of Xenophon must remain represented")

    if primary_manifest.get("drafted_units") != PRIMARY_UNIT_IDS:
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
        return fail("Founding audit must record complete Book I draft coverage")
    if state.get("book_two_primary_draft_complete") is not True:
        return fail("Founding audit must record complete Book II draft coverage")
    if state.get("book_milestones_pending_owner_review") is not True:
        return fail("Founding audit must preserve pending owner review for drafted book milestones")
    if state.get("book_two_drafted_chapters") != [f"II.{number}" for number in range(1, 7)]:
        return fail("Founding audit Book II coverage mismatch")
    if state.get("book_three_drafted_chapters") != ["III.1"]:
        return fail("Founding audit Book III coverage mismatch")
    if state.get("minister_adapter_derived") is not False:
        return fail("Adapter must remain underived")
    if state.get("sanctum_registration_present") is not False:
        return fail("Sanctum registration must remain absent")

    print("Xenophon repository validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
