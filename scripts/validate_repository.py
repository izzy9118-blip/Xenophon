from __future__ import annotations

from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
SECONDARY_IDS = [f"XEN-RU-{n:03d}" for n in range(1, 9)]
PRIMARY_IDS = [f"XEN-PRI-RU-{n:03d}" for n in range(1, 14)]
NEXT_ID = "XEN-PRI-RU-014"
PRIMARY_PLAN = ROOT / "studies/xenophon-anabasis-dakyns/reading-plan.yaml"
PRIMARY_PATHS = {
    uid: ROOT / f"studies/xenophon-anabasis-dakyns/units/{uid}.yaml"
    for uid in PRIMARY_IDS
}
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
    *[ROOT / f"studies/strauss-xenophons-anabasis/units/{uid}.yaml" for uid in SECONDARY_IDS],
    PRIMARY_PLAN,
    *PRIMARY_PATHS.values(),
    ROOT / "adapter/report-contract.yaml",
    ROOT / "audits/founding-state.yaml",
    ROOT / "governance/owner-reviews/2026-07-30-strauss-witness-review.yaml",
    ROOT / "governance/owner-reviews/2026-07-30-primary-anabasis-witness-admission.yaml",
    ROOT / "history/2026-07-30-primary-anabasis-witness-record.md",
]


def load(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def fail(message: str) -> int:
    print(message)
    return 1


def validate_unit(record: dict, uid: str) -> str | None:
    if record.get("unit_id") != uid:
        return f"Primary unit identifier mismatch for {uid}"
    if record.get("status") != "DRAFTED_PENDING_OWNER_REVIEW":
        return f"Primary unit status mismatch for {uid}"
    if "Translator wording is not unmediated Greek evidence" not in record.get("jurisdiction", ""):
        return f"Primary translation jurisdiction missing for {uid}"
    if record.get("secondary_comparison_status") != "DEFERRED":
        return f"Primary comparison gate mismatch for {uid}"
    sections = [
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
    for section in sections:
        if not record.get(section):
            return f"Required section {section} missing for {uid}"
    if any(not obs.get("locator") or not obs.get("evidence_type") for obs in record["documentary_observations"]):
        return f"Untyped or unlocated observation in {uid}"
    if any(item.get("evidence_type") != "PROVISIONAL_INFERENCE" for item in record["provisional_findings"]):
        return f"Provisional finding type mismatch in {uid}"
    if any(item.get("evidence_type") != "UNRESOLVED_QUESTION" for item in record["standing_unresolved_questions"]):
        return f"Unresolved question type mismatch in {uid}"
    return None


def main() -> int:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED if not path.exists()]
    if missing:
        print("Missing required files:", *missing, sep="\n- ")
        return 1

    docs = {path: load(path) for path in REQUIRED if path.suffix in {".yaml", ".yml"}}
    manifest = docs[ROOT / "manifest.yaml"]
    if manifest.get("version") != "1.13.0":
        return fail("Manifest version must be 1.13.0 after drafting Anabasis II.3")
    if manifest.get("state") != "PRIMARY_RECONSTRUCTION_IN_PROGRESS":
        return fail("Manifest primary reconstruction state mismatch")
    if manifest.get("artificial_intelligence_self_certification_prohibited") is not True:
        return fail("AI self-certification safeguard must remain true")
    if manifest.get("next_required_unit", {}).get("id") != NEXT_ID:
        return fail("Manifest next primary unit mismatch")
    if manifest.get("primary_study", {}).get("drafted_units") != PRIMARY_IDS:
        return fail("Manifest primary drafted-unit list mismatch")
    if manifest.get("secondary_study", {}).get("drafted_units") != SECONDARY_IDS:
        return fail("Manifest secondary drafted-unit order mismatch")

    corpus = docs[ROOT / "corpus/index.yaml"]
    if corpus.get("counts") != {
        "primary_sources": 1,
        "secondary_sources": 1,
        "registered_witnesses": 2,
    }:
        return fail("Corpus counts mismatch")
    if corpus.get("primary_original_language_gap", {}).get("status") != "DOCUMENTED_GAP":
        return fail("Original-language witness gap must remain documented")

    primary_source = docs[ROOT / "corpus/sources/xenophon-anabasis.yaml"]
    if primary_source.get("status") != "OWNER_ADMITTED_PRIMARY_TRANSLATION_SOURCE":
        return fail("Primary source admission status mismatch")
    if primary_source.get("work", {}).get("author") != "Xenophon":
        return fail("Primary source author mismatch")
    if primary_source.get("edition", {}).get("translator") != "H. G. Dakyns":
        return fail("Primary source translator mismatch")

    witness = docs[ROOT / "corpus/witnesses/gutenberg-1170-dakyns-pdf.yaml"]
    if witness.get("status") != "OWNER_ADMITTED_PRIMARY_TRANSLATION_WITNESS":
        return fail("Primary witness admission status mismatch")
    if witness.get("witness", {}).get("page_count") != 168:
        return fail("Primary witness page count mismatch")
    if witness.get("file_control", {}).get("sha256") != "6a7534d8d80153afc1623803ef129185aa8d3d41be692091f4e105375c65901e":
        return fail("Primary witness SHA-256 mismatch")

    secondary_review = docs[ROOT / "governance/owner-reviews/2026-07-30-strauss-witness-review.yaml"]
    if secondary_review.get("status") != "OWNER_ADOPTED_SECONDARY_RECONSTRUCTION":
        return fail("Secondary owner review status mismatch")
    if secondary_review.get("scope", {}).get("units") != SECONDARY_IDS:
        return fail("Secondary owner review scope mismatch")

    admission = docs[ROOT / "governance/owner-reviews/2026-07-30-primary-anabasis-witness-admission.yaml"]
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
    if [u.get("id") for u in units] != [*PRIMARY_IDS, NEXT_ID]:
        return fail("Primary reading plan unit order mismatch")
    if [u.get("id") for u in units if u.get("status") == "DRAFTED_PENDING_OWNER_REVIEW"] != PRIMARY_IDS:
        return fail("Primary drafted-unit order mismatch")
    if [u.get("id") for u in units if u.get("status") == "NEXT"] != [NEXT_ID]:
        return fail("Primary next-unit status mismatch")
    if [u.get("work_locator") for u in units[:10]] != [f"Anabasis I.{n}" for n in range(1, 11)]:
        return fail("Primary Book I locator sequence mismatch")
    if [u.get("work_locator") for u in units[10:13]] != ["Anabasis II.1", "Anabasis II.2", "Anabasis II.3"]:
        return fail("Primary drafted Book II locator sequence mismatch")
    if units[-1].get("work_locator") != "Anabasis II.4":
        return fail("Next primary locator must be Anabasis II.4")
    if plan.get("comparison_gate", {}).get("strauss_comparison") != "DEFERRED":
        return fail("Strauss comparison must remain deferred")

    primary_docs = {}
    for uid, path in PRIMARY_PATHS.items():
        record = docs[path]
        error = validate_unit(record, uid)
        if error:
            return fail(error)
        primary_docs[uid] = record

    if primary_docs["XEN-PRI-RU-011"].get("narrative_person_and_authorial_attribution", {}).get("xenophon_as_character_present") != "TEXTUALLY_DISPUTED":
        return fail("Anabasis II.1 Theopompus/Xenophon uncertainty must remain preserved")

    observations_012 = primary_docs["XEN-PRI-RU-012"].get("documentary_observations", [])
    if not any(obs.get("evidence_type") == "TEXTUAL_VARIANT_OBSERVATION" for obs in observations_012):
        return fail("Anabasis II.2 wolf variant must remain documented")
    if not any("fortune proved a better general" in obs.get("observation", "") for obs in observations_012):
        return fail("Anabasis II.2 narratorial judgment must remain represented")

    unit_013 = primary_docs["XEN-PRI-RU-013"]
    if unit_013.get("narrative_person_and_authorial_attribution", {}).get("first_person_narrator_present") is not True:
        return fail("Anabasis II.3 first-person proof must remain represented")
    observations_013 = unit_013.get("documentary_observations", [])
    if not any(obs.get("evidence_type") == "NARRATORIAL_INTERVENTION_OBSERVATION" for obs in observations_013):
        return fail("Anabasis II.3 narratorial intervention must remain typed")
    if not any("oaths and pledges" in obs.get("observation", "") for obs in observations_013):
        return fail("Anabasis II.3 oath-and-pledge compact must remain represented")
    if not any("market" in obs.get("observation", "").lower() for obs in observations_013):
        return fail("Anabasis II.3 market terms must remain represented")

    audit = docs[ROOT / "audits/founding-state.yaml"].get("repository_state", {})
    if audit.get("drafted_primary_units") != 13:
        return fail("Founding audit primary unit count mismatch")
    if audit.get("drafted_secondary_units") != 8:
        return fail("Founding audit secondary unit count mismatch")
    if audit.get("book_one_primary_draft_complete") is not True:
        return fail("Founding audit must preserve Book I completion")
    if audit.get("book_two_drafted_chapters") != ["II.1", "II.2", "II.3"]:
        return fail("Founding audit Book II coverage mismatch")
    if audit.get("minister_adapter_derived") is not False:
        return fail("Adapter must remain underived")

    print("Xenophon repository validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
