from __future__ import annotations
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
SECONDARY_IDS = [f"XEN-RU-{n:03d}" for n in range(1, 9)]
PRIMARY_IDS = [f"XEN-PRI-RU-{n:03d}" for n in range(1, 26)]
UNIT = lambda n: ROOT / f"studies/xenophon-anabasis-dakyns/units/XEN-PRI-RU-{n:03d}.yaml"
PLAN = ROOT / "studies/xenophon-anabasis-dakyns/reading-plan.yaml"
SECONDARY_REVIEW = ROOT / "governance/owner-reviews/2026-07-30-strauss-witness-review.yaml"
PRIMARY_ADMISSION = ROOT / "governance/owner-reviews/2026-07-30-primary-anabasis-witness-admission.yaml"
REQUIRED = [
    ROOT / "manifest.yaml", ROOT / "method/source-hierarchy.yaml", ROOT / "method/reading-protocol.yaml",
    ROOT / "corpus/index.yaml", ROOT / "corpus/sources/strauss-xenophons-anabasis.yaml",
    ROOT / "corpus/witnesses/strauss-spp-1983.yaml", ROOT / "corpus/sources/xenophon-anabasis.yaml",
    ROOT / "corpus/witnesses/gutenberg-1170-dakyns-pdf.yaml",
    ROOT / "studies/strauss-xenophons-anabasis/reading-plan.yaml",
    *[ROOT / f"studies/strauss-xenophons-anabasis/units/{u}.yaml" for u in SECONDARY_IDS],
    PLAN, *[UNIT(n) for n in range(1, 26)], ROOT / "adapter/report-contract.yaml",
    ROOT / "audits/founding-state.yaml", SECONDARY_REVIEW, PRIMARY_ADMISSION,
    ROOT / "history/2026-07-30-primary-anabasis-witness-record.md",
]


def load(path: Path):
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def fail(message: str) -> int:
    print(message)
    return 1


def types(record: dict) -> set[str]:
    return {o.get("evidence_type") for o in record.get("documentary_observations", [])}


def texts(record: dict) -> list[str]:
    return [o.get("observation", "") for o in record.get("documentary_observations", [])]


def require_types(record: dict, label: str, required: set[str]) -> int | None:
    missing = sorted(required - types(record))
    return fail(f"{label} evidence types missing: {', '.join(missing)}") if missing else None


def narrative_ok(record: dict, values: tuple[object, object, object]) -> bool:
    narrative = record.get("narrative_person_and_authorial_attribution", {})
    keys = ("xenophon_as_character_present", "direct_authorial_self_identification_present", "first_person_narrator_present")
    return tuple(narrative.get(k) for k in keys) == values


def validate_unit(record: dict, unit_id: str) -> str | None:
    if record.get("unit_id") != unit_id or record.get("status") != "DRAFTED_PENDING_OWNER_REVIEW":
        return f"Primary unit control mismatch for {unit_id}"
    if "Translator wording is not unmediated Greek evidence" not in record.get("jurisdiction", ""):
        return f"Primary translation jurisdiction missing for {unit_id}"
    if record.get("secondary_comparison_status") != "DEFERRED":
        return f"Primary comparison gate mismatch for {unit_id}"
    sections = [
        "bibliographic_and_witness_control", "narrative_person_and_authorial_attribution",
        "speakers_audiences_and_occasions", "speeches_deeds_and_outcomes",
        "sequence_repetition_omission_and_contradiction", "documentary_observations",
        "provisional_findings", "standing_unresolved_questions", "downstream_textual_checks",
    ]
    if any(not record.get(section) for section in sections):
        return f"Required section missing for {unit_id}"
    if any(not o.get("locator") or not o.get("evidence_type") for o in record["documentary_observations"]):
        return f"Untyped observation in {unit_id}"
    if any(x.get("evidence_type") != "PROVISIONAL_INFERENCE" for x in record["provisional_findings"]):
        return f"Untyped finding in {unit_id}"
    if any(x.get("evidence_type") != "UNRESOLVED_QUESTION" for x in record["standing_unresolved_questions"]):
        return f"Untyped question in {unit_id}"
    return None


def main() -> int:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED if not path.exists()]
    if missing:
        print("Missing required files:", *missing, sep="\n- ")
        return 1
    docs = {path: load(path) for path in REQUIRED if path.suffix in {".yaml", ".yml"}}

    manifest = docs[ROOT / "manifest.yaml"]
    primary = manifest.get("primary_study", {})
    if manifest.get("version") != "1.25.0" or manifest.get("state") != "PRIMARY_RECONSTRUCTION_IN_PROGRESS":
        return fail("Manifest version or state mismatch")
    if manifest.get("artificial_intelligence_self_certification_prohibited") is not True:
        return fail("AI self-certification safeguard missing")
    if manifest.get("next_required_unit", {}).get("id") != "XEN-PRI-RU-026":
        return fail("Manifest next unit mismatch")
    if not all(primary.get(k) is True for k in [
        "book_one_draft_complete_pending_owner_review",
        "book_two_draft_complete_pending_owner_review",
        "book_three_draft_complete_pending_owner_review",
    ]):
        return fail("Manifest completed-book safeguards missing")
    if primary.get("book_three_drafted_chapters") != [f"III.{n}" for n in range(1, 6)]:
        return fail("Manifest Book III coverage mismatch")
    if primary.get("book_four_drafted_chapters") != ["IV.1", "IV.2", "IV.3", "IV.4"]:
        return fail("Manifest Book IV coverage mismatch")
    if primary.get("drafted_units") != PRIMARY_IDS:
        return fail("Manifest primary-unit list mismatch")
    if manifest.get("secondary_study", {}).get("drafted_units") != SECONDARY_IDS:
        return fail("Secondary unit order mismatch")

    corpus = docs[ROOT / "corpus/index.yaml"]
    if corpus.get("counts") != {"primary_sources": 1, "secondary_sources": 1, "registered_witnesses": 2}:
        return fail("Corpus counts mismatch")
    if corpus.get("primary_original_language_gap", {}).get("status") != "DOCUMENTED_GAP":
        return fail("Greek witness gap missing")
    if docs[ROOT / "corpus/sources/strauss-xenophons-anabasis.yaml"].get("status") != "OWNER_ADOPTED_SECONDARY_SOURCE":
        return fail("Secondary source status mismatch")
    if docs[ROOT / "corpus/witnesses/strauss-spp-1983.yaml"].get("status") != "OWNER_ADOPTED_SECONDARY_WITNESS":
        return fail("Secondary witness status mismatch")

    source = docs[ROOT / "corpus/sources/xenophon-anabasis.yaml"]
    witness = docs[ROOT / "corpus/witnesses/gutenberg-1170-dakyns-pdf.yaml"]
    if source.get("status") != "OWNER_ADMITTED_PRIMARY_TRANSLATION_SOURCE" or source.get("edition", {}).get("translator") != "H. G. Dakyns":
        return fail("Primary source control mismatch")
    if witness.get("status") != "OWNER_ADMITTED_PRIMARY_TRANSLATION_WITNESS" or witness.get("source_id") != "XEN-SRC-PRI-001":
        return fail("Primary witness control mismatch")
    if witness.get("witness", {}).get("page_count") != 168:
        return fail("Primary witness page count mismatch")
    if witness.get("file_control", {}).get("sha256") != "6a7534d8d80153afc1623803ef129185aa8d3d41be692091f4e105375c65901e":
        return fail("Primary witness digest mismatch")

    secondary_review = docs[SECONDARY_REVIEW]
    admission = docs[PRIMARY_ADMISSION]
    if secondary_review.get("status") != "OWNER_ADOPTED_SECONDARY_RECONSTRUCTION" or secondary_review.get("scope", {}).get("units") != SECONDARY_IDS:
        return fail("Secondary owner-review mismatch")
    if admission.get("status") != "OWNER_ADMITTED_PRIMARY_TRANSLATION_WITNESS" or admission.get("scope", {}).get("initial_unit") != PRIMARY_IDS[0]:
        return fail("Primary admission mismatch")
    if admission.get("limits", [])[-1:] != ["Artificial-intelligence self-certification remains prohibited."]:
        return fail("Primary admission safeguard missing")

    secondary_plan = docs[ROOT / "studies/strauss-xenophons-anabasis/reading-plan.yaml"]
    if secondary_plan.get("status") != "OWNER_ADOPTED_SECONDARY_RECONSTRUCTION":
        return fail("Secondary plan status mismatch")
    if [u["id"] for u in secondary_plan["reading_units"] if u.get("status") == "DRAFTED_PENDING_OWNER_REVIEW"] != SECONDARY_IDS:
        return fail("Secondary plan order mismatch")

    plan = docs[PLAN]
    units = plan.get("reading_units", [])
    if plan.get("status") != "SEQUENTIAL_PRIMARY_READING_IN_PROGRESS_PENDING_OWNER_REVIEW":
        return fail("Primary plan status mismatch")
    if [u.get("id") for u in units] != [*PRIMARY_IDS, "XEN-PRI-RU-026"]:
        return fail("Primary plan order mismatch")
    expected = (
        [f"Anabasis I.{n}" for n in range(1, 11)]
        + [f"Anabasis II.{n}" for n in range(1, 7)]
        + [f"Anabasis III.{n}" for n in range(1, 6)]
        + ["Anabasis IV.1", "Anabasis IV.2", "Anabasis IV.3", "Anabasis IV.4", "Anabasis IV.5"]
    )
    if [u.get("work_locator") for u in units] != expected:
        return fail("Primary locator sequence mismatch")
    if units[-2].get("pdf_pages_one_based") != "79-81":
        return fail("IV.4 page range mismatch")
    if units[-1].get("pdf_pages_one_based") != "81-84" or units[-1].get("status") != "NEXT":
        return fail("Next unit page range or status mismatch")
    if [u.get("id") for u in units if u.get("status") == "DRAFTED_PENDING_OWNER_REVIEW"] != PRIMARY_IDS:
        return fail("Drafted primary order mismatch")
    if plan.get("comparison_gate", {}).get("strauss_comparison") != "DEFERRED":
        return fail("Strauss comparison must remain deferred")

    unit_docs = {n: docs[UNIT(n)] for n in range(1, 26)}
    for n, record in unit_docs.items():
        if error := validate_unit(record, f"XEN-PRI-RU-{n:03d}"):
            return fail(error)

    if unit_docs[11].get("narrative_person_and_authorial_attribution", {}).get("xenophon_as_character_present") != "TEXTUALLY_DISPUTED":
        return fail("II.1 attribution uncertainty missing")
    if "TEXTUAL_VARIANT_OBSERVATION" not in types(unit_docs[12]) or not any("fortune proved a better general" in text for text in texts(unit_docs[12])):
        return fail("II.2 safeguards missing")
    if unit_docs[13].get("narrative_person_and_authorial_attribution", {}).get("first_person_narrator_present") is not True:
        return fail("II.3 first-person intervention missing")

    narrative_expectations = {
        17: (True, True, True), 18: (True, False, False), 19: (True, False, False),
        20: (True, False, False), 21: (True, False, False), 22: (True, False, False),
        23: (True, False, False), 24: (True, False, False), 25: (True, False, False),
    }
    for number, values in narrative_expectations.items():
        if not narrative_ok(unit_docs[number], values):
            return fail(f"Unit {number} narrator-character distinction missing")

    required_types = {
        14: {"FALSE_REPORT_OBSERVATION", "NARRATORIAL_INFERENCE_OBSERVATION", "NARRATORIAL_JUDGMENT_OBSERVATION"},
        15: {"NARRATORIAL_STATUS_OBSERVATION", "WARNING_OBSERVATION", "VIOLENT_OUTCOME_OBSERVATION", "CONFLICTING_REPORT_OBSERVATION"},
        16: {"FIRST_PERSON_JUDGMENT_OBSERVATION", "EVIDENTIARY_LIMITATION_OBSERVATION", "REPORT_STATUS_OBSERVATION"},
        17: {"EDITORIAL_PARATEXT_OBSERVATION", "FIRST_PERSON_SELF_REFERENCE_OBSERVATION", "DREAM_REPORT_OBSERVATION", "DREAM_INTERPRETATION_OBSERVATION", "ETHNIC_IDENTITY_CLAIM_OBSERVATION", "ELECTION_OUTCOME_OBSERVATION"},
        18: {"OMEN_INTERPRETATION_OBSERVATION", "COLLECTIVE_RITUAL_OBSERVATION", "PARATEXT_OBSERVATION", "COLONISATION_ARGUMENT_OBSERVATION", "VOTE_OBSERVATION", "EXPERIMENTAL_GOVERNANCE_OBSERVATION"},
        19: {"EDITORIAL_PARATEXT_OBSERVATION", "NARRATORIAL_INFERENCE_OBSERVATION", "WAR_POLICY_OBSERVATION", "SELF_CORRECTION_OBSERVATION", "FORCE_CREATION_OBSERVATION", "COMMAND_APPOINTMENT_OBSERVATION"},
        20: {"MUTILATION_OBSERVATION", "DIVINE_CAUSATION_REPORT_OBSERVATION", "PARATEXT_OBSERVATION", "INSTITUTIONAL_ADAPTATION_OBSERVATION", "MEDICAL_INSTITUTION_OBSERVATION", "NARRATORIAL_GENERALISATION_OBSERVATION", "COLLECTIVE_COERCION_OBSERVATION", "TEXTUAL_VARIANT_OBSERVATION"},
        21: {"POSSESSION_CLAIM_OBSERVATION", "COMMAND_DISAGREEMENT_OBSERVATION", "ENGINEERING_PROPOSAL_OBSERVATION", "FEASIBILITY_JUDGMENT_OBSERVATION", "COERCED_INTELLIGENCE_OBSERVATION", "AUTONOMY_REPORT_OBSERVATION", "REPORTED_HISTORICAL_CLAIM_OBSERVATION", "PARATEXT_OBSERVATION", "INTELLIGENCE_COMPARTMENTATION_OBSERVATION", "STRATEGIC_DECISION_OBSERVATION", "SACRIFICIAL_DECISION_OBSERVATION", "EDITORIAL_PARATEXT_OBSERVATION"},
        22: {"EDITORIAL_PARATEXT_OBSERVATION", "THREAT_ASSESSMENT_OBSERVATION", "SELECTIVE_RESTRAINT_OBSERVATION", "NARRATORIAL_COUNTERFACTUAL_OBSERVATION", "CAPTIVE_RELEASE_OBSERVATION", "CONFISCATION_ENFORCEMENT_OBSERVATION", "COMMAND_COMMUNICATION_OBSERVATION", "COMMAND_DISAGREEMENT_OBSERVATION", "COERCIVE_INTERROGATION_OBSERVATION", "PRISONER_EXECUTION_OBSERVATION", "ROUTE_DISCLOSURE_OBSERVATION", "VOLUNTEER_FORMATION_OBSERVATION"},
        23: {"BOUND_GUIDE_OBSERVATION", "SIGNAL_PLAN_OBSERVATION", "DIVERSION_OPERATION_OBSERVATION", "HEAVY_BOULDER_DEFENSE_OBSERVATION", "FALSE_SUMMIT_OBSERVATION", "MIST_ASSAULT_OBSERVATION", "BAGGAGE_ROUTE_CONSTRAINT_OBSERVATION", "NARRATORIAL_INFERENCE_OBSERVATION", "NAMED_CASUALTY_OBSERVATION", "TRUCE_NEGOTIATION_OBSERVATION", "DEAD_RECOVERY_CONDITION_OBSERVATION", "TRUCE_AMBIGUITY_OBSERVATION", "ABANDONMENT_OBSERVATION", "RESCUE_OBSERVATION", "GUIDE_EXCHANGE_OBSERVATION", "FUNERARY_RITES_OBSERVATION", "MUTUAL_SUPPORT_OBSERVATION", "WEAPON_TECHNOLOGY_OBSERVATION", "ADAPTIVE_WEAPON_REUSE_OBSERVATION", "SPECIALIST_UTILITY_OBSERVATION", "PARATEXT_OBSERVATION", "EDITORIAL_PARATEXT_OBSERVATION"},
        24: {"NARRATORIAL_SUMMARY_OBSERVATION", "DREAM_REPORT_OBSERVATION", "EDITORIAL_PARATEXT_OBSERVATION", "DREAM_INTERPRETATION_OBSERVATION", "SACRIFICIAL_DECISION_OBSERVATION", "SCOUT_DISCOVERY_OBSERVATION", "LIBATION_OBSERVATION", "COMMAND_PLAN_OBSERVATION", "CEREMONIAL_LEADERSHIP_OBSERVATION", "COLLECTIVE_RITUAL_OBSERVATION", "TACTICAL_FEINT_OBSERVATION", "COMMAND_RESTRAINT_OBSERVATION", "FORMATION_ADAPTATION_OBSERVATION", "DISCIPLINE_FAILURE_OBSERVATION", "SIGNAL_COORDINATION_OBSERVATION", "SUCCESSFUL_WITHDRAWAL_OBSERVATION", "OVEREXTENSION_OBSERVATION"},
        25: {"GEOGRAPHIC_ROUTE_OBSERVATION", "OFFICE_AND_PRIVILEGE_OBSERVATION", "TREATY_TERMS_OBSERVATION", "TREATY_OUTCOME_OBSERVATION", "SURVEILLANCE_OBSERVATION", "STRAGGLER_REPORT_OBSERVATION", "WEATHER_OBSERVATION", "EXEMPLARY_LEADERSHIP_DEED_OBSERVATION", "COLLECTIVE_IMITATION_OBSERVATION", "EDITORIAL_PARATEXT_OBSERVATION", "RETRIBUTIVE_OUTCOME_OBSERVATION", "SCOUT_SELECTION_OBSERVATION", "SCOUT_REPORT_OBSERVATION", "TEXTUAL_VARIANT_OBSERVATION", "PRISONER_IDENTITY_REPORT_OBSERVATION", "FORCE_COMPOSITION_REPORT_OBSERVATION", "AMBUSH_PLAN_REPORT_OBSERVATION", "INTELLIGENCE_TO_ACTION_OBSERVATION", "IMPETUOUS_ASSAULT_OBSERVATION", "CAPTURE_AND_RECALL_OBSERVATION"},
    }
    for number, wanted in required_types.items():
        if result := require_types(unit_docs[number], f"Unit {number}", wanted):
            return result

    if "possibly Xenophon" not in unit_docs[14].get("narrative_person_and_authorial_attribution", {}).get("textually_disputed_or_conjectural_identification", ""):
        return fail("II.4 conjectural identification missing")
    if not any("tiara" in text and "heart" in text for text in texts(unit_docs[15])):
        return fail("II.5 tiara-and-heart image missing")
    if not any("ten thousand Clearchuses" in text for text in texts(unit_docs[18])):
        return fail("III.2 Clearchuses metaphor missing")
    if "BOOK IV" not in unit_docs[21].get("bibliographic_and_witness_control", {}).get("chapter_boundary_control", ""):
        return fail("III.5 Book IV boundary missing")
    if "Book IV retrospective synopsis" not in unit_docs[22].get("bibliographic_and_witness_control", {}).get("chapter_boundary_control", ""):
        return fail("IV.1 paratext boundary missing")
    if "IV.3 begins on page 75" not in unit_docs[23].get("bibliographic_and_witness_control", {}).get("chapter_boundary_control", ""):
        return fail("IV.2 chapter boundary missing")
    boundary24 = unit_docs[24].get("bibliographic_and_witness_control", {}).get("chapter_boundary_control", "")
    if "corrected" not in boundary24 or "page 79" not in boundary24:
        return fail("IV.3 corrected boundary missing")
    boundary25 = unit_docs[25].get("bibliographic_and_witness_control", {}).get("chapter_boundary_control", "")
    if "ends on PDF page 81" not in boundary25 or "IV.5 begins on page 81" not in boundary25:
        return fail("IV.4 chapter boundary missing")

    t25 = texts(unit_docs[25])
    phrase_checks = [
        ("Tiribazus", "mount the visiting king", "office and privilege"),
        ("non-burning of houses", "needed provisions", "treaty terms"),
        ("covers weapons and sleeping soldiers", "snowfall", "snow exposure"),
        ("without his cloak", "splitting wood", "Xenophon example"),
        ("distinguishes fact from fiction", "Democrates", "scout characterization"),
        ("Chalybian and Taochian mercenaries", "no numerical total", "force report"),
        ("without waiting for the heavy infantry", "rushes the entrenchment", "light-infantry initiative"),
        ("twenty horses", "silver-footed couches", "captured camp goods"),
    ]
    for first, second, label in phrase_checks:
        if not any(first in text and second in text for text in t25):
            return fail(f"IV.4 {label} missing")

    audit_state = docs[ROOT / "audits/founding-state.yaml"].get("repository_state", {})
    if audit_state.get("primary_witness_count") != 1 or audit_state.get("drafted_primary_units") != 25 or audit_state.get("drafted_secondary_units") != 8:
        return fail("Founding audit counts mismatch")
    if not all(audit_state.get(k) is True for k in [
        "book_one_primary_draft_complete", "book_two_primary_draft_complete",
        "book_three_primary_draft_complete", "book_milestones_pending_owner_review",
    ]):
        return fail("Founding audit milestones missing")
    if audit_state.get("book_two_drafted_chapters") != [f"II.{n}" for n in range(1, 7)]:
        return fail("Audit Book II coverage mismatch")
    if audit_state.get("book_three_drafted_chapters") != [f"III.{n}" for n in range(1, 6)]:
        return fail("Audit Book III coverage mismatch")
    if audit_state.get("book_four_drafted_chapters") != ["IV.1", "IV.2", "IV.3", "IV.4"]:
        return fail("Audit Book IV coverage mismatch")
    if audit_state.get("minister_adapter_derived") is not False or audit_state.get("sanctum_registration_present") is not False:
        return fail("Adapter or Sanctum registration safeguard missing")

    print("Xenophon repository validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
