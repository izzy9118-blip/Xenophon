from __future__ import annotations

from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
SECONDARY_OWNER_REVIEW = ROOT / "governance/owner-reviews/2026-07-30-strauss-witness-review.yaml"
PRIMARY_ADMISSION = ROOT / "governance/owner-reviews/2026-07-30-primary-anabasis-witness-admission.yaml"
SECONDARY_UNIT_IDS = [f"XEN-RU-{number:03d}" for number in range(1, 9)]
PRIMARY_UNIT_IDS = [f"XEN-PRI-RU-{number:03d}" for number in range(1, 17)]
PRIMARY_UNIT_PATHS = {unit_id: ROOT / f"studies/xenophon-anabasis-dakyns/units/{unit_id}.yaml" for unit_id in PRIMARY_UNIT_IDS}
PRIMARY_READING_PLAN = ROOT / "studies/xenophon-anabasis-dakyns/reading-plan.yaml"
NEXT_PRIMARY_UNIT_ID = "XEN-PRI-RU-017"

REQUIRED = [
    ROOT / "manifest.yaml", ROOT / "method/source-hierarchy.yaml", ROOT / "method/reading-protocol.yaml",
    ROOT / "corpus/index.yaml", ROOT / "corpus/sources/strauss-xenophons-anabasis.yaml",
    ROOT / "corpus/witnesses/strauss-spp-1983.yaml", ROOT / "corpus/sources/xenophon-anabasis.yaml",
    ROOT / "corpus/witnesses/gutenberg-1170-dakyns-pdf.yaml",
    ROOT / "studies/strauss-xenophons-anabasis/reading-plan.yaml",
    *[ROOT / f"studies/strauss-xenophons-anabasis/units/{unit_id}.yaml" for unit_id in SECONDARY_UNIT_IDS],
    PRIMARY_READING_PLAN, *PRIMARY_UNIT_PATHS.values(), ROOT / "adapter/report-contract.yaml",
    ROOT / "audits/founding-state.yaml", SECONDARY_OWNER_REVIEW, PRIMARY_ADMISSION,
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
        "bibliographic_and_witness_control", "narrative_person_and_authorial_attribution",
        "speakers_audiences_and_occasions", "speeches_deeds_and_outcomes",
        "sequence_repetition_omission_and_contradiction", "documentary_observations",
        "provisional_findings", "standing_unresolved_questions", "downstream_textual_checks",
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
    documents = {path: load_yaml(path) for path in REQUIRED if path.suffix in {".yaml", ".yml"}}

    manifest = documents[ROOT / "manifest.yaml"]
    if not isinstance(manifest, dict):
        return fail("manifest.yaml must contain a mapping")
    if manifest.get("artificial_intelligence_self_certification_prohibited") is not True:
        return fail("AI self-certification safeguard must remain true")
    if manifest.get("version") != "1.16.0":
        return fail("Manifest version must be 1.16.0 after drafting Anabasis II.6")
    if manifest.get("state") != "PRIMARY_RECONSTRUCTION_IN_PROGRESS":
        return fail("Manifest primary reconstruction state mismatch")
    if manifest.get("next_required_unit", {}).get("id") != NEXT_PRIMARY_UNIT_ID:
        return fail("Manifest next primary unit mismatch")
    if manifest.get("primary_study", {}).get("book_two_draft_complete_pending_owner_review") is not True:
        return fail("Manifest must record complete Book II draft coverage pending owner review")

    corpus = documents[ROOT / "corpus/index.yaml"]
    if corpus.get("counts") != {"primary_sources": 1, "secondary_sources": 1, "registered_witnesses": 2}:
        return fail("Corpus counts mismatch")
    if corpus.get("primary_original_language_gap", {}).get("status") != "DOCUMENTED_GAP":
        return fail("Original-language witness gap must remain documented")
    if documents[ROOT / "corpus/sources/strauss-xenophons-anabasis.yaml"].get("status") != "OWNER_ADOPTED_SECONDARY_SOURCE":
        return fail("Secondary source owner-adoption status mismatch")
    if documents[ROOT / "corpus/witnesses/strauss-spp-1983.yaml"].get("status") != "OWNER_ADOPTED_SECONDARY_WITNESS":
        return fail("Secondary witness owner-adoption status mismatch")

    primary_source = documents[ROOT / "corpus/sources/xenophon-anabasis.yaml"]
    if primary_source.get("status") != "OWNER_ADMITTED_PRIMARY_TRANSLATION_SOURCE" or primary_source.get("work", {}).get("author") != "Xenophon" or primary_source.get("edition", {}).get("translator") != "H. G. Dakyns":
        return fail("Primary source control mismatch")
    primary_witness = documents[ROOT / "corpus/witnesses/gutenberg-1170-dakyns-pdf.yaml"]
    if primary_witness.get("status") != "OWNER_ADMITTED_PRIMARY_TRANSLATION_WITNESS" or primary_witness.get("source_id") != "XEN-SRC-PRI-001":
        return fail("Primary witness admission mismatch")
    if primary_witness.get("witness", {}).get("page_count") != 168:
        return fail("Primary witness page count mismatch")
    if primary_witness.get("file_control", {}).get("sha256") != "6a7534d8d80153afc1623803ef129185aa8d3d41be692091f4e105375c65901e":
        return fail("Primary witness SHA-256 mismatch")

    secondary_review = documents[SECONDARY_OWNER_REVIEW]
    if secondary_review.get("status") != "OWNER_ADOPTED_SECONDARY_RECONSTRUCTION" or secondary_review.get("scope", {}).get("units") != SECONDARY_UNIT_IDS:
        return fail("Secondary owner review mismatch")
    primary_admission = documents[PRIMARY_ADMISSION]
    if primary_admission.get("status") != "OWNER_ADMITTED_PRIMARY_TRANSLATION_WITNESS":
        return fail("Primary admission record status mismatch")
    if primary_admission.get("scope", {}).get("initial_unit") != PRIMARY_UNIT_IDS[0]:
        return fail("Primary admission initial-unit mismatch")
    if primary_admission.get("limits", [])[-1:] != ["Artificial-intelligence self-certification remains prohibited."]:
        return fail("Primary admission safeguard missing")

    secondary_plan = documents[ROOT / "studies/strauss-xenophons-anabasis/reading-plan.yaml"]
    if secondary_plan.get("status") != "OWNER_ADOPTED_SECONDARY_RECONSTRUCTION":
        return fail("Secondary reading plan owner-adoption status mismatch")
    drafted_secondary = [u["id"] for u in secondary_plan["reading_units"] if u.get("status") == "DRAFTED_PENDING_OWNER_REVIEW"]
    if drafted_secondary != SECONDARY_UNIT_IDS:
        return fail("Secondary drafted-unit order mismatch")

    plan = documents[PRIMARY_READING_PLAN]
    if plan.get("status") != "SEQUENTIAL_PRIMARY_READING_IN_PROGRESS_PENDING_OWNER_REVIEW":
        return fail("Primary reading plan status mismatch")
    units = plan.get("reading_units", [])
    if [u.get("id") for u in units] != [*PRIMARY_UNIT_IDS, NEXT_PRIMARY_UNIT_ID]:
        return fail("Primary reading plan unit order mismatch")
    if [u.get("work_locator") for u in units[:10]] != [f"Anabasis I.{n}" for n in range(1, 11)]:
        return fail("Primary Book I locator sequence mismatch")
    if [u.get("work_locator") for u in units[10:16]] != [f"Anabasis II.{n}" for n in range(1, 7)]:
        return fail("Primary Book II locator sequence mismatch")
    if units[-1].get("work_locator") != "Anabasis III.1":
        return fail("Next primary locator must be Anabasis III.1")
    if [u.get("id") for u in units if u.get("status") == "DRAFTED_PENDING_OWNER_REVIEW"] != PRIMARY_UNIT_IDS:
        return fail("Primary drafted-unit order mismatch")
    if [u.get("id") for u in units if u.get("status") == "NEXT"] != [NEXT_PRIMARY_UNIT_ID]:
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
    if "TEXTUAL_VARIANT_OBSERVATION" not in {o.get("evidence_type") for o in unit12.get("documentary_observations", [])}:
        return fail("Anabasis II.2 wolf textual variant must remain documented")
    if not any("fortune proved a better general" in o.get("observation", "") for o in unit12.get("documentary_observations", [])):
        return fail("Anabasis II.2 narratorial judgment must remain represented")
    unit13 = documents[PRIMARY_UNIT_PATHS["XEN-PRI-RU-013"]]
    if unit13.get("narrative_person_and_authorial_attribution", {}).get("first_person_narrator_present") is not True:
        return fail("Anabasis II.3 first-person narratorial intervention must remain represented")
    unit14 = documents[PRIMARY_UNIT_PATHS["XEN-PRI-RU-014"]]
    if unit14.get("narrative_person_and_authorial_attribution", {}).get("xenophon_as_character_present") is not True:
        return fail("Anabasis II.4 named Xenophon appearance must remain represented")
    if "possibly Xenophon" not in unit14.get("narrative_person_and_authorial_attribution", {}).get("textually_disputed_or_conjectural_identification", ""):
        return fail("Anabasis II.4 conjectural young-man identification must remain preserved")
    types14 = {o.get("evidence_type") for o in unit14.get("documentary_observations", [])}
    for required in {"FALSE_REPORT_OBSERVATION", "NARRATORIAL_INFERENCE_OBSERVATION", "NARRATORIAL_JUDGMENT_OBSERVATION"}:
        if required not in types14:
            return fail(f"Anabasis II.4 evidence type missing: {required}")
    unit15 = documents[PRIMARY_UNIT_PATHS["XEN-PRI-RU-015"]]
    if unit15.get("narrative_person_and_authorial_attribution", {}).get("xenophon_as_character_present") is not True:
        return fail("Anabasis II.5 named Xenophon appearance must remain represented")
    types15 = {o.get("evidence_type") for o in unit15.get("documentary_observations", [])}
    for required in {"NARRATORIAL_STATUS_OBSERVATION", "WARNING_OBSERVATION", "VIOLENT_OUTCOME_OBSERVATION", "CONFLICTING_REPORT_OBSERVATION"}:
        if required not in types15:
            return fail(f"Anabasis II.5 evidence type missing: {required}")
    observations15 = [o.get("observation", "") for o in unit15.get("documentary_observations", [])]
    if not any("tiara" in text and "heart" in text for text in observations15):
        return fail("Anabasis II.5 tiara-and-heart image must remain represented")
    if not any("Proxenus and Menon" in text and "honor" in text for text in observations15):
        return fail("Anabasis II.5 conflicting report about Proxenus and Menon must remain represented")

    unit16 = documents[PRIMARY_UNIT_PATHS["XEN-PRI-RU-016"]]
    narrative16 = unit16.get("narrative_person_and_authorial_attribution", {})
    if narrative16.get("first_person_narrator_present") is not True:
        return fail("Anabasis II.6 first-person narratorial judgments must remain represented")
    if narrative16.get("xenophon_as_character_present") is not False:
        return fail("Anabasis II.6 must not invent Xenophon as a character")
    types16 = {o.get("evidence_type") for o in unit16.get("documentary_observations", [])}
    for required in {"FIRST_PERSON_JUDGMENT_OBSERVATION", "EVIDENTIARY_LIMITATION_OBSERVATION", "REPORT_STATUS_OBSERVATION"}:
        if required not in types16:
            return fail(f"Anabasis II.6 evidence type missing: {required}")
    tensions16 = unit16.get("sequence_repetition_omission_and_contradiction", {}).get("tensions", [])
    if not any("opening says" in text and "Menon" in text for text in tensions16):
        return fail("Anabasis II.6 collective-death and Menon qualification must remain preserved")

    if manifest.get("primary_study", {}).get("drafted_units") != PRIMARY_UNIT_IDS:
        return fail("Manifest primary drafted-unit list mismatch")
    if manifest.get("secondary_study", {}).get("drafted_units") != SECONDARY_UNIT_IDS:
        return fail("Manifest secondary drafted-unit order mismatch")

    audit = documents[ROOT / "audits/founding-state.yaml"]
    state = audit.get("repository_state", {})
    if state.get("primary_witness_count") != 1 or state.get("drafted_primary_units") != len(PRIMARY_UNIT_IDS) or state.get("drafted_secondary_units") != 8:
        return fail("Founding audit count mismatch")
    if state.get("book_one_primary_draft_complete") is not True:
        return fail("Founding audit must record complete Book I draft coverage")
    if state.get("book_two_primary_draft_complete") is not True:
        return fail("Founding audit must record complete Book II draft coverage")
    if state.get("book_milestones_pending_owner_review") is not True:
        return fail("Founding audit must preserve pending owner review for drafted book milestones")
    if state.get("book_two_drafted_chapters") != [f"II.{n}" for n in range(1, 7)]:
        return fail("Founding audit Book II coverage mismatch")
    if state.get("minister_adapter_derived") is not False or state.get("sanctum_registration_present") is not False:
        return fail("Adapter and Sanctum registration must remain absent")

    print("Xenophon repository validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
