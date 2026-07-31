from pathlib import Path
import shutil, subprocess, sys, tempfile, yaml

ROOT = Path(__file__).resolve().parents[1]
PREV = ROOT / "scripts/validate_repository_v1_33.py"
PLAN = ROOT / "studies/xenophon-anabasis-dakyns/reading-plan.yaml"
UNIT = ROOT / "studies/xenophon-anabasis-dakyns/units/XEN-PRI-RU-034.yaml"
HIST = ROOT / "history/2026-07-30-anabasis-v5-cotyora-sinope-dispute.md"


def load(path):
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def dump(path, value):
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(value, f, sort_keys=False, allow_unicode=True)


def fail(message):
    print(message)
    return 1


def run_predecessor():
    if not PREV.exists():
        return fail("Frozen v1.33 predecessor validator missing")
    with tempfile.TemporaryDirectory(prefix="xenophon-v133-") as td:
        projected = Path(td) / "repo"
        shutil.copytree(ROOT, projected, ignore=shutil.ignore_patterns(".git", "__pycache__"))

        manifest = load(projected / "manifest.yaml")
        manifest["version"] = "1.33.0"
        primary = manifest["primary_study"]
        primary["drafted_units"] = primary["drafted_units"][:-1]
        primary["book_five_drafted_chapters"] = ["V.1", "V.2", "V.3", "V.4"]
        manifest["next_required_unit"] = {
            "id": "XEN-PRI-RU-034",
            "description": "Continue the independent primary reconstruction with Anabasis V.5 using the Dakyns Project Gutenberg witness.",
        }
        dump(projected / "manifest.yaml", manifest)

        plan = load(projected / "studies/xenophon-anabasis-dakyns/reading-plan.yaml")
        plan["reading_units"] = plan["reading_units"][:-1]
        plan["reading_units"][-1].pop("record", None)
        plan["reading_units"][-1]["status"] = "NEXT"
        plan["remaining_sequence"] = "Anabasis V.6 through VII.8, strictly in chapter order."
        dump(projected / "studies/xenophon-anabasis-dakyns/reading-plan.yaml", plan)

        audit = load(projected / "audits/founding-state.yaml")
        state = audit["repository_state"]
        state["drafted_primary_units"] = 33
        state["book_five_drafted_chapters"] = ["V.1", "V.2", "V.3", "V.4"]
        audit["documented_gaps"][1]["description"] = (
            "The primary Anabasis reconstruction remains incomplete; Books I through IV are drafted pending owner review, and Book V has drafted coverage through V.4."
        )
        audit["next_required_action"] = (
            "Complete XEN-PRI-RU-034 for Anabasis V.5 without importing Strauss or treating translated wording as unmediated Greek evidence."
        )
        dump(projected / "audits/founding-state.yaml", audit)

        result = subprocess.run(
            [sys.executable, str(projected / "scripts/validate_repository_v1_33.py")],
            cwd=projected,
            text=True,
            capture_output=True,
        )
        if result.returncode:
            return fail("Frozen v1.33 predecessor validation failed: " + (result.stdout + result.stderr).strip())
    return 0


def main():
    if run_predecessor():
        return 1

    required = [ROOT / "manifest.yaml", PLAN, ROOT / "audits/founding-state.yaml", UNIT, HIST, PREV]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    if missing:
        return fail("Missing V.5 production files: " + ", ".join(missing))

    manifest = load(ROOT / "manifest.yaml")
    audit = load(ROOT / "audits/founding-state.yaml")
    plan = load(PLAN)
    unit = load(UNIT)

    if manifest.get("version") != "1.34.0" or manifest.get("state") != "PRIMARY_RECONSTRUCTION_IN_PROGRESS":
        return fail("Manifest V.5 state mismatch")
    if manifest.get("artificial_intelligence_self_certification_prohibited") is not True:
        return fail("AI self-certification safeguard missing")
    if manifest.get("minister", {}).get("registration_status") != "NOT_YET_REGISTERED_IN_SANCTUM":
        return fail("Premature Sanctum registration")

    ids = [f"XEN-PRI-RU-{n:03d}" for n in range(1, 35)]
    chapters = ["V.1", "V.2", "V.3", "V.4", "V.5"]
    primary = manifest.get("primary_study", {})
    if primary.get("drafted_units") != ids or primary.get("book_five_drafted_chapters") != chapters:
        return fail("Manifest V.5 coverage mismatch")
    if manifest.get("next_required_unit", {}).get("id") != "XEN-PRI-RU-035":
        return fail("Manifest next unit mismatch")

    units = plan.get("reading_units", [])
    if [x.get("id") for x in units] != ids + ["XEN-PRI-RU-035"]:
        return fail("Reading-plan sequence mismatch")
    if [x.get("id") for x in units if x.get("status") == "DRAFTED_PENDING_OWNER_REVIEW"] != ids:
        return fail("Reading-plan drafted status mismatch")
    if units[-2].get("work_locator") != "Anabasis V.5" or units[-2].get("pdf_pages_one_based") != "104-106":
        return fail("V.5 reading-plan range mismatch")
    if units[-1].get("work_locator") != "Anabasis V.6" or units[-1].get("pdf_pages_one_based") != "107-111" or units[-1].get("status") != "NEXT":
        return fail("V.6 next-unit control mismatch")
    if plan.get("comparison_gate", {}).get("strauss_comparison") != "DEFERRED":
        return fail("Strauss comparison gate missing")

    state = audit.get("repository_state", {})
    if state.get("drafted_primary_units") != 34 or state.get("book_five_drafted_chapters") != chapters:
        return fail("Audit V.5 coverage mismatch")
    if state.get("minister_adapter_derived") is not False or state.get("sanctum_registration_present") is not False:
        return fail("Premature derivation or registration")

    if unit.get("unit_id") != "XEN-PRI-RU-034" or unit.get("status") != "DRAFTED_PENDING_OWNER_REVIEW":
        return fail("V.5 unit control mismatch")
    if unit.get("scope", {}).get("pdf_pages_one_based") != "104-106":
        return fail("V.5 unit range mismatch")
    if "Translator wording is not unmediated Greek evidence" not in unit.get("jurisdiction", ""):
        return fail("V.5 translation jurisdiction missing")
    if unit.get("secondary_comparison_status") != "DEFERRED":
        return fail("V.5 comparison gate missing")

    narrative = unit.get("narrative_person_and_authorial_attribution", {})
    if narrative.get("xenophon_as_character_present") is not True or narrative.get("first_person_narrator_present") is not False or narrative.get("direct_authorial_self_identification_present") is not False:
        return fail("V.5 narrative-person controls missing")

    boundary = unit.get("bibliographic_and_witness_control", {}).get("chapter_boundary_control", "")
    for phrase in [
        "V.5 begins beneath heading V on PDF page 104",
        "ends immediately before heading VI on page 107",
        "V.6 begins beneath heading VI on page 107",
    ]:
        if phrase not in boundary:
            return fail("V.5 boundary control missing: " + phrase)

    observations = unit.get("documentary_observations", [])
    actual_types = {o.get("evidence_type") for o in observations}
    expected_types = {
        "BOOK_BOUNDARY_OBSERVATION", "MIXED_RELATIONS_ROUTE_OBSERVATION", "SUBJECT_MINING_PEOPLE_OBSERVATION",
        "WEAKER_COASTAL_FORTRESS_OBSERVATION", "PLUNDER_MOTIVE_COUNCIL_OBSERVATION",
        "DEFERRED_HOSPITALITY_GIFT_OBSERVATION", "REPEATED_ABORTIVE_SACRIFICE_OBSERVATION",
        "DIVINE_NON_COUNTENANCE_OF_WAR_OBSERVATION", "SACRIFICE_RESTRAINS_PLUNDER_OBSERVATION",
        "HELLENIC_COLONY_OBSERVATION", "EDITORIAL_DISTANCE_NOTE_OBSERVATION", "FORTY_FIVE_DAY_HALT_OBSERVATION",
        "TRIBAL_PROCESSION_AND_GAMES_OBSERVATION", "MARKET_AND_SICK_ACCESS_REFUSAL_OBSERVATION",
        "ESTATE_PROVISIONING_OBSERVATION", "SINOPEAN_FEAR_AND_TRIBUTE_INTEREST_OBSERVATION",
        "REPORTED_CLEVER_ORATOR_OBSERVATION", "HELLENIC_SOLIDARITY_CLAIM_OBSERVATION",
        "COLONIAL_CONQUEST_TITLE_OBSERVATION", "FORCIBLE_ENTRY_AND_SEIZURE_ALLEGATION_OBSERVATION",
        "EXTERNAL_ALLIANCE_THREAT_OBSERVATION", "PAID_MARKET_RECIPROCITY_DEFENSE_OBSERVATION",
        "NECESSITY_NOT_INSOLENCE_DEFENSE_OBSERVATION", "COMPARATIVE_PEOPLE_PRECEDENT_OBSERVATION",
        "COTYORITE_BLAME_ATTRIBUTION_OBSERVATION", "SICK_SHELTER_FORCED_ENTRY_DEFENSE_OBSERVATION",
        "PATIENT_EXPENSE_PAYMENT_OBSERVATION", "GATE_SENTRY_CONTROL_OBSERVATION",
        "MAIN_ARMY_OUTSIDE_CAMP_OBSERVATION", "COUNTER_ALLIANCE_THREAT_OBSERVATION",
        "AMBASSADORIAL_INTERNAL_DISSENT_OBSERVATION", "DE_ESCALATORY_FRIENDSHIP_CLARIFICATION_OBSERVATION",
        "HOSPITALITY_RESTORATION_OBSERVATION", "ROUTE_CONSULTATION_OBSERVATION", "HARMOST_PARATEXT_OBSERVATION",
    }
    missing_types = expected_types - actual_types
    if missing_types:
        return fail("V.5 evidence types missing: " + ", ".join(sorted(missing_types)))

    text = " ".join(o.get("observation", "") for o in observations).casefold()
    phrases = [
        "eight stages", "few in number", "weaker by art or nature", "obtain pickings", "initially refused",
        "several sacrificial attempts fail", "do not countenance war", "accepts hospitality",
        "hellenic city and colony of sinope", "manuscript-distance calculation", "forty-five days",
        "processions by tribes", "refuse both a market", "cotyorite estates", "fear for cotyora",
        "clever orator", "fellow-hellenes owe kindness", "land earlier taken from unnamed barbarians",
        "forcible entry", "alliance with corylas", "paid market exchange", "necessity rather than insolence",
        "market-providing macrones", "blames cotyora", "sheltered sick and wounded", "pay their expenses",
        "sentry at the gates", "outside in regular order", "ally with paphlagonia",
        "annoyance with hecatonymus", "disclaims warlike intent", "send gifts", "remaining journey", "harmost",
    ]
    for phrase in phrases:
        if phrase.casefold() not in text:
            return fail("V.5 phrase safeguard missing: " + phrase)

    if len(observations) != 35 or len(unit.get("speeches_deeds_and_outcomes", [])) != 12:
        return fail("V.5 record counts mismatch")
    if len(unit.get("provisional_findings", [])) != 10 or len(unit.get("standing_unresolved_questions", [])) != 18 or len(unit.get("downstream_textual_checks", [])) != 12:
        return fail("V.5 analytical counts mismatch")

    print("Xenophon repository validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
