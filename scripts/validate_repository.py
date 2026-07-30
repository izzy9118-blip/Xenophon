from __future__ import annotations
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
SECONDARY_REVIEW = ROOT / "governance/owner-reviews/2026-07-30-strauss-witness-review.yaml"
PRIMARY_ADMISSION = ROOT / "governance/owner-reviews/2026-07-30-primary-anabasis-witness-admission.yaml"
SECONDARY_IDS = [f"XEN-RU-{n:03d}" for n in range(1, 9)]
PRIMARY_IDS = [f"XEN-PRI-RU-{n:03d}" for n in range(1, 24)]
PRIMARY_PATHS = {u: ROOT / f"studies/xenophon-anabasis-dakyns/units/{u}.yaml" for u in PRIMARY_IDS}
PRIMARY_PLAN = ROOT / "studies/xenophon-anabasis-dakyns/reading-plan.yaml"
NEXT_ID = "XEN-PRI-RU-024"

REQUIRED = [
    ROOT / "manifest.yaml", ROOT / "method/source-hierarchy.yaml", ROOT / "method/reading-protocol.yaml",
    ROOT / "corpus/index.yaml", ROOT / "corpus/sources/strauss-xenophons-anabasis.yaml",
    ROOT / "corpus/witnesses/strauss-spp-1983.yaml", ROOT / "corpus/sources/xenophon-anabasis.yaml",
    ROOT / "corpus/witnesses/gutenberg-1170-dakyns-pdf.yaml",
    ROOT / "studies/strauss-xenophons-anabasis/reading-plan.yaml",
    *[ROOT / f"studies/strauss-xenophons-anabasis/units/{u}.yaml" for u in SECONDARY_IDS],
    PRIMARY_PLAN, *PRIMARY_PATHS.values(), ROOT / "adapter/report-contract.yaml",
    ROOT / "audits/founding-state.yaml", SECONDARY_REVIEW, PRIMARY_ADMISSION,
    ROOT / "history/2026-07-30-primary-anabasis-witness-record.md",
]

def load(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)

def fail(message: str) -> int:
    print(message)
    return 1

def evidence_types(record: dict) -> set[str]:
    return {o.get("evidence_type") for o in record.get("documentary_observations", [])}

def observation_texts(record: dict) -> list[str]:
    return [o.get("observation", "") for o in record.get("documentary_observations", [])]

def require_types(record: dict, label: str, required: set[str]) -> str | None:
    missing = sorted(required - evidence_types(record))
    return f"{label} evidence types missing: {', '.join(missing)}" if missing else None

def narrative(record: dict) -> dict:
    return record.get("narrative_person_and_authorial_attribution", {})

def validate_unit(record: dict, unit_id: str) -> str | None:
    if record.get("unit_id") != unit_id:
        return f"Primary unit identifier mismatch for {unit_id}"
    if record.get("status") != "DRAFTED_PENDING_OWNER_REVIEW":
        return f"Primary unit status mismatch for {unit_id}"
    if "Translator wording is not unmediated Greek evidence" not in record.get("jurisdiction", ""):
        return f"Primary translation jurisdiction missing for {unit_id}"
    if record.get("secondary_comparison_status") != "DEFERRED":
        return f"Primary comparison gate mismatch for {unit_id}"
    required = [
        "bibliographic_and_witness_control", "narrative_person_and_authorial_attribution",
        "speakers_audiences_and_occasions", "speeches_deeds_and_outcomes",
        "sequence_repetition_omission_and_contradiction", "documentary_observations",
        "provisional_findings", "standing_unresolved_questions", "downstream_textual_checks",
    ]
    missing = [section for section in required if not record.get(section)]
    if missing:
        return f"Required primary sections missing for {unit_id}: {', '.join(missing)}"
    if any(not o.get("locator") or not o.get("evidence_type") for o in record["documentary_observations"]):
        return f"Untyped or unlocated primary observation in {unit_id}"
    if any(f.get("evidence_type") != "PROVISIONAL_INFERENCE" for f in record["provisional_findings"]):
        return f"Untyped provisional finding in {unit_id}"
    if any(q.get("evidence_type") != "UNRESOLVED_QUESTION" for q in record["standing_unresolved_questions"]):
        return f"Untyped unresolved question in {unit_id}"
    return None

def check_narrative(record: dict, label: str, character: object, self_id: object, first_person: object) -> str | None:
    n = narrative(record)
    if (
        n.get("xenophon_as_character_present") != character
        or n.get("direct_authorial_self_identification_present") != self_id
        or n.get("first_person_narrator_present") != first_person
    ):
        return f"{label} narrator-character distinction missing"
    return None

def main() -> int:
    missing = [str(p.relative_to(ROOT)) for p in REQUIRED if not p.exists()]
    if missing:
        print("Missing required files:", *missing, sep="\n- ")
        return 1
    docs = {p: load(p) for p in REQUIRED if p.suffix in {".yaml", ".yml"}}

    manifest = docs[ROOT / "manifest.yaml"]
    if not isinstance(manifest, dict):
        return fail("manifest.yaml must contain a mapping")
    if manifest.get("artificial_intelligence_self_certification_prohibited") is not True:
        return fail("AI self-certification safeguard must remain true")
    if manifest.get("version") != "1.23.0":
        return fail("Manifest version must be 1.23.0 after drafting Anabasis IV.2")
    if manifest.get("state") != "PRIMARY_RECONSTRUCTION_IN_PROGRESS":
        return fail("Manifest state mismatch")
    if manifest.get("next_required_unit", {}).get("id") != NEXT_ID:
        return fail("Manifest next primary unit mismatch")
    pm = manifest.get("primary_study", {})
    for key in [
        "book_one_draft_complete_pending_owner_review",
        "book_two_draft_complete_pending_owner_review",
        "book_three_draft_complete_pending_owner_review",
    ]:
        if pm.get(key) is not True:
            return fail(f"Manifest milestone safeguard missing: {key}")
    if pm.get("book_three_drafted_chapters") != [f"III.{n}" for n in range(1, 6)]:
        return fail("Manifest Book III coverage mismatch")
    if pm.get("book_four_drafted_chapters") != ["IV.1", "IV.2"]:
        return fail("Manifest Book IV coverage mismatch")
    if pm.get("drafted_units") != PRIMARY_IDS:
        return fail("Manifest primary drafted-unit list mismatch")
    if manifest.get("secondary_study", {}).get("drafted_units") != SECONDARY_IDS:
        return fail("Manifest secondary drafted-unit order mismatch")

    corpus = docs[ROOT / "corpus/index.yaml"]
    if corpus.get("counts") != {"primary_sources": 1, "secondary_sources": 1, "registered_witnesses": 2}:
        return fail("Corpus counts mismatch")
    if corpus.get("primary_original_language_gap", {}).get("status") != "DOCUMENTED_GAP":
        return fail("Original-language witness gap must remain documented")
    if docs[ROOT / "corpus/sources/strauss-xenophons-anabasis.yaml"].get("status") != "OWNER_ADOPTED_SECONDARY_SOURCE":
        return fail("Secondary source status mismatch")
    if docs[ROOT / "corpus/witnesses/strauss-spp-1983.yaml"].get("status") != "OWNER_ADOPTED_SECONDARY_WITNESS":
        return fail("Secondary witness status mismatch")

    source = docs[ROOT / "corpus/sources/xenophon-anabasis.yaml"]
    if source.get("status") != "OWNER_ADMITTED_PRIMARY_TRANSLATION_SOURCE":
        return fail("Primary source status mismatch")
    if source.get("work", {}).get("author") != "Xenophon":
        return fail("Primary source author mismatch")
    if source.get("edition", {}).get("translator") != "H. G. Dakyns":
        return fail("Primary source translator mismatch")
    witness = docs[ROOT / "corpus/witnesses/gutenberg-1170-dakyns-pdf.yaml"]
    if witness.get("status") != "OWNER_ADMITTED_PRIMARY_TRANSLATION_WITNESS":
        return fail("Primary witness status mismatch")
    if witness.get("source_id") != "XEN-SRC-PRI-001":
        return fail("Primary witness linkage mismatch")
    if witness.get("witness", {}).get("page_count") != 168:
        return fail("Primary witness page count mismatch")
    if witness.get("file_control", {}).get("sha256") != "6a7534d8d80153afc1623803ef129185aa8d3d41be692091f4e105375c65901e":
        return fail("Primary witness SHA-256 mismatch")

    review = docs[SECONDARY_REVIEW]
    if review.get("status") != "OWNER_ADOPTED_SECONDARY_RECONSTRUCTION" or review.get("scope", {}).get("units") != SECONDARY_IDS:
        return fail("Secondary owner review mismatch")
    admission = docs[PRIMARY_ADMISSION]
    if admission.get("status") != "OWNER_ADMITTED_PRIMARY_TRANSLATION_WITNESS":
        return fail("Primary admission status mismatch")
    if admission.get("scope", {}).get("initial_unit") != PRIMARY_IDS[0]:
        return fail("Primary admission initial-unit mismatch")
    if admission.get("limits", [])[-1:] != ["Artificial-intelligence self-certification remains prohibited."]:
        return fail("Primary admission safeguard missing")

    secondary_plan = docs[ROOT / "studies/strauss-xenophons-anabasis/reading-plan.yaml"]
    if secondary_plan.get("status") != "OWNER_ADOPTED_SECONDARY_RECONSTRUCTION":
        return fail("Secondary reading plan status mismatch")
    if [u["id"] for u in secondary_plan["reading_units"] if u.get("status") == "DRAFTED_PENDING_OWNER_REVIEW"] != SECONDARY_IDS:
        return fail("Secondary drafted-unit order mismatch")

    plan = docs[PRIMARY_PLAN]
    units = plan.get("reading_units", [])
    if plan.get("status") != "SEQUENTIAL_PRIMARY_READING_IN_PROGRESS_PENDING_OWNER_REVIEW":
        return fail("Primary reading plan status mismatch")
    if [u.get("id") for u in units] != [*PRIMARY_IDS, NEXT_ID]:
        return fail("Primary reading plan unit order mismatch")
    if [u.get("work_locator") for u in units[:10]] != [f"Anabasis I.{n}" for n in range(1, 11)]:
        return fail("Book I locator sequence mismatch")
    if [u.get("work_locator") for u in units[10:16]] != [f"Anabasis II.{n}" for n in range(1, 7)]:
        return fail("Book II locator sequence mismatch")
    if [u.get("work_locator") for u in units[16:21]] != [f"Anabasis III.{n}" for n in range(1, 6)]:
        return fail("Book III locator sequence mismatch")
    if [u.get("work_locator") for u in units[21:23]] != ["Anabasis IV.1", "Anabasis IV.2"]:
        return fail("Drafted Book IV locator sequence mismatch")
    if units[-1].get("work_locator") != "Anabasis IV.3" or units[-1].get("pdf_pages_one_based") != "75-78":
        return fail("Next primary unit must be Anabasis IV.3 on PDF pages 75-78")
    if [u.get("id") for u in units if u.get("status") == "DRAFTED_PENDING_OWNER_REVIEW"] != PRIMARY_IDS:
        return fail("Primary drafted-unit order mismatch")
    if [u.get("id") for u in units if u.get("status") == "NEXT"] != [NEXT_ID]:
        return fail("Primary next-unit status mismatch")
    if plan.get("comparison_gate", {}).get("strauss_comparison") != "DEFERRED":
        return fail("Strauss comparison must remain deferred")

    for unit_id, path in PRIMARY_PATHS.items():
        record = docs[path]
        if not isinstance(record, dict):
            return fail(f"Primary unit {unit_id} must contain a mapping")
        error = validate_unit(record, unit_id)
        if error:
            return fail(error)

    u11 = docs[PRIMARY_PATHS["XEN-PRI-RU-011"]]
    if narrative(u11).get("xenophon_as_character_present") != "TEXTUALLY_DISPUTED":
        return fail("II.1 attribution uncertainty missing")
    u12 = docs[PRIMARY_PATHS["XEN-PRI-RU-012"]]
    if "TEXTUAL_VARIANT_OBSERVATION" not in evidence_types(u12) or not any("fortune proved a better general" in t for t in observation_texts(u12)):
        return fail("II.2 textual safeguards missing")
    u13 = docs[PRIMARY_PATHS["XEN-PRI-RU-013"]]
    if narrative(u13).get("first_person_narrator_present") is not True:
        return fail("II.3 first-person intervention missing")

    u14 = docs[PRIMARY_PATHS["XEN-PRI-RU-014"]]
    if narrative(u14).get("xenophon_as_character_present") is not True or "possibly Xenophon" not in narrative(u14).get("textually_disputed_or_conjectural_identification", ""):
        return fail("II.4 Xenophon distinction missing")
    if error := require_types(u14, "II.4", {"FALSE_REPORT_OBSERVATION", "NARRATORIAL_INFERENCE_OBSERVATION", "NARRATORIAL_JUDGMENT_OBSERVATION"}):
        return fail(error)

    u15 = docs[PRIMARY_PATHS["XEN-PRI-RU-015"]]
    if narrative(u15).get("xenophon_as_character_present") is not True:
        return fail("II.5 Xenophon appearance missing")
    if error := require_types(u15, "II.5", {"NARRATORIAL_STATUS_OBSERVATION", "WARNING_OBSERVATION", "VIOLENT_OUTCOME_OBSERVATION", "CONFLICTING_REPORT_OBSERVATION"}):
        return fail(error)
    if not any("tiara" in t and "heart" in t for t in observation_texts(u15)):
        return fail("II.5 tiara-and-heart image missing")

    u16 = docs[PRIMARY_PATHS["XEN-PRI-RU-016"]]
    if narrative(u16).get("first_person_narrator_present") is not True or narrative(u16).get("xenophon_as_character_present") is not False:
        return fail("II.6 narrative distinction missing")
    if error := require_types(u16, "II.6", {"FIRST_PERSON_JUDGMENT_OBSERVATION", "EVIDENTIARY_LIMITATION_OBSERVATION", "REPORT_STATUS_OBSERVATION"}):
        return fail(error)

    u17 = docs[PRIMARY_PATHS["XEN-PRI-RU-017"]]
    if error := check_narrative(u17, "III.1", True, True, True):
        return fail(error)
    if error := require_types(u17, "III.1", {"EDITORIAL_PARATEXT_OBSERVATION", "FIRST_PERSON_SELF_REFERENCE_OBSERVATION", "DREAM_REPORT_OBSERVATION", "DREAM_INTERPRETATION_OBSERVATION", "ETHNIC_IDENTITY_CLAIM_OBSERVATION", "ELECTION_OUTCOME_OBSERVATION"}):
        return fail(error)

    u18 = docs[PRIMARY_PATHS["XEN-PRI-RU-018"]]
    if error := check_narrative(u18, "III.2", True, False, False):
        return fail(error)
    if error := require_types(u18, "III.2", {"OMEN_INTERPRETATION_OBSERVATION", "COLLECTIVE_RITUAL_OBSERVATION", "PARATEXT_OBSERVATION", "COLONISATION_ARGUMENT_OBSERVATION", "VOTE_OBSERVATION", "EXPERIMENTAL_GOVERNANCE_OBSERVATION"}):
        return fail(error)
    if not any("ten thousand Clearchuses" in t for t in observation_texts(u18)):
        return fail("III.2 Clearchuses metaphor missing")

    u19 = docs[PRIMARY_PATHS["XEN-PRI-RU-019"]]
    if error := check_narrative(u19, "III.3", True, False, False):
        return fail(error)
    if error := require_types(u19, "III.3", {"EDITORIAL_PARATEXT_OBSERVATION", "NARRATORIAL_INFERENCE_OBSERVATION", "WAR_POLICY_OBSERVATION", "SELF_CORRECTION_OBSERVATION", "FORCE_CREATION_OBSERVATION", "COMMAND_APPOINTMENT_OBSERVATION"}):
        return fail(error)

    u20 = docs[PRIMARY_PATHS["XEN-PRI-RU-020"]]
    if error := check_narrative(u20, "III.4", True, False, False):
        return fail(error)
    if error := require_types(u20, "III.4", {"MUTILATION_OBSERVATION", "DIVINE_CAUSATION_REPORT_OBSERVATION", "PARATEXT_OBSERVATION", "INSTITUTIONAL_ADAPTATION_OBSERVATION", "MEDICAL_INSTITUTION_OBSERVATION", "NARRATORIAL_GENERALISATION_OBSERVATION", "COLLECTIVE_COERCION_OBSERVATION", "TEXTUAL_VARIANT_OBSERVATION"}):
        return fail(error)

    u21 = docs[PRIMARY_PATHS["XEN-PRI-RU-021"]]
    if error := check_narrative(u21, "III.5", True, False, False):
        return fail(error)
    if error := require_types(u21, "III.5", {"POSSESSION_CLAIM_OBSERVATION", "COMMAND_DISAGREEMENT_OBSERVATION", "ENGINEERING_PROPOSAL_OBSERVATION", "FEASIBILITY_JUDGMENT_OBSERVATION", "COERCED_INTELLIGENCE_OBSERVATION", "AUTONOMY_REPORT_OBSERVATION", "REPORTED_HISTORICAL_CLAIM_OBSERVATION", "PARATEXT_OBSERVATION", "INTELLIGENCE_COMPARTMENTATION_OBSERVATION", "STRATEGIC_DECISION_OBSERVATION", "SACRIFICIAL_DECISION_OBSERVATION", "EDITORIAL_PARATEXT_OBSERVATION"}):
        return fail(error)
    boundary21 = u21.get("bibliographic_and_witness_control", {}).get("chapter_boundary_control", "")
    if "BOOK IV" not in boundary21 or "IV.1 begins on PDF page 70" not in boundary21:
        return fail("III.5 chapter boundary and paratext separation missing")

    u22 = docs[PRIMARY_PATHS["XEN-PRI-RU-022"]]
    if error := check_narrative(u22, "IV.1", True, False, False):
        return fail(error)
    if error := require_types(u22, "IV.1", {"EDITORIAL_PARATEXT_OBSERVATION", "THREAT_ASSESSMENT_OBSERVATION", "SELECTIVE_RESTRAINT_OBSERVATION", "NARRATORIAL_COUNTERFACTUAL_OBSERVATION", "CAPTIVE_RELEASE_OBSERVATION", "CONFISCATION_ENFORCEMENT_OBSERVATION", "COMMAND_COMMUNICATION_OBSERVATION", "COMMAND_DISAGREEMENT_OBSERVATION", "COERCIVE_INTERROGATION_OBSERVATION", "PRISONER_EXECUTION_OBSERVATION", "ROUTE_DISCLOSURE_OBSERVATION", "VOLUNTEER_FORMATION_OBSERVATION"}):
        return fail(error)
    boundary22 = u22.get("bibliographic_and_witness_control", {}).get("chapter_boundary_control", "")
    if "Book IV retrospective synopsis" not in boundary22 or "IV.2 begins" not in boundary22:
        return fail("IV.1 chapter boundary and paratext separation missing")

    u23 = docs[PRIMARY_PATHS["XEN-PRI-RU-023"]]
    if error := check_narrative(u23, "IV.2", True, False, False):
        return fail(error)
    boundary23 = u23.get("bibliographic_and_witness_control", {}).get("chapter_boundary_control", "")
    if "ends on PDF page 75 immediately" not in boundary23 or "IV.3 begins on page 75" not in boundary23:
        return fail("IV.2 chapter boundary missing")
    required23 = {
        "BOUND_GUIDE_OBSERVATION", "SIGNAL_PLAN_OBSERVATION", "DIVERSION_OPERATION_OBSERVATION",
        "HEAVY_BOULDER_DEFENSE_OBSERVATION", "FALSE_SUMMIT_OBSERVATION", "MIST_ASSAULT_OBSERVATION",
        "BAGGAGE_ROUTE_CONSTRAINT_OBSERVATION", "NARRATORIAL_INFERENCE_OBSERVATION",
        "NAMED_CASUALTY_OBSERVATION", "TRUCE_NEGOTIATION_OBSERVATION",
        "DEAD_RECOVERY_CONDITION_OBSERVATION", "TRUCE_AMBIGUITY_OBSERVATION",
        "ABANDONMENT_OBSERVATION", "RESCUE_OBSERVATION", "GUIDE_EXCHANGE_OBSERVATION",
        "FUNERARY_RITES_OBSERVATION", "MUTUAL_SUPPORT_OBSERVATION",
        "WEAPON_TECHNOLOGY_OBSERVATION", "ADAPTIVE_WEAPON_REUSE_OBSERVATION",
        "SPECIALIST_UTILITY_OBSERVATION", "PARATEXT_OBSERVATION", "EDITORIAL_PARATEXT_OBSERVATION",
    }
    if error := require_types(u23, "IV.2", required23):
        return fail(error)
    t23 = observation_texts(u23)
    for first, second, label in [
        ("binds the local guide", "volunteer storming party", "bound-guide deployment"),
        ("two thousand strong", "storming party", "force size"),
        ("think they possess the height", "lower outpost", "false summit"),
        ("Cephisodorus and Amphicrates", "Archagoras", "named ridge losses"),
        ("restore the bodies", "not to burn their houses", "body-recovery condition"),
        ("shield-bearer leaves", "Eurylochus", "abandonment and rescue"),
        ("recover the dead", "return the guide", "guide exchange"),
        ("rescue each other in turn", "Xenophon", "mutual relief"),
        ("captured Carduchian arrows", "javelins", "weapon adaptation"),
        ("Cretan troops under Stratocles", "highly useful", "Cretan utility"),
    ]:
        if not any(first in text and second in text for text in t23):
            return fail(f"IV.2 {label} missing")

    audit = docs[ROOT / "audits/founding-state.yaml"]
    state = audit.get("repository_state", {})
    if state.get("primary_witness_count") != 1 or state.get("drafted_primary_units") != len(PRIMARY_IDS) or state.get("drafted_secondary_units") != 8:
        return fail("Founding audit counts mismatch")
    if not all(state.get(k) is True for k in [
        "book_one_primary_draft_complete", "book_two_primary_draft_complete",
        "book_three_primary_draft_complete", "book_milestones_pending_owner_review",
    ]):
        return fail("Founding audit book milestone safeguards missing")
    if state.get("book_two_drafted_chapters") != [f"II.{n}" for n in range(1, 7)]:
        return fail("Founding audit Book II coverage mismatch")
    if state.get("book_three_drafted_chapters") != [f"III.{n}" for n in range(1, 6)]:
        return fail("Founding audit Book III coverage mismatch")
    if state.get("book_four_drafted_chapters") != ["IV.1", "IV.2"]:
        return fail("Founding audit Book IV coverage mismatch")
    if state.get("minister_adapter_derived") is not False or state.get("sanctum_registration_present") is not False:
        return fail("Adapter and Sanctum registration must remain absent")

    print("Xenophon repository validation passed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
