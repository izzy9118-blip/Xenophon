from __future__ import annotations

from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
SECONDARY_OWNER_REVIEW = ROOT / "governance/owner-reviews/2026-07-30-strauss-witness-review.yaml"
PRIMARY_ADMISSION = ROOT / "governance/owner-reviews/2026-07-30-primary-anabasis-witness-admission.yaml"
SECONDARY_UNIT_IDS = [f"XEN-RU-{number:03d}" for number in range(1, 9)]
PRIMARY_UNIT_ID = "XEN-PRI-RU-001"
PRIMARY_UNIT_PATH = ROOT / "studies/xenophon-anabasis-dakyns/units/XEN-PRI-RU-001.yaml"
PRIMARY_READING_PLAN = ROOT / "studies/xenophon-anabasis-dakyns/reading-plan.yaml"

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
    PRIMARY_UNIT_PATH,
    ROOT / "adapter/report-contract.yaml",
    ROOT / "audits/founding-state.yaml",
    SECONDARY_OWNER_REVIEW,
    PRIMARY_ADMISSION,
    ROOT / "history/2026-07-30-primary-anabasis-witness-record.md",
]


def load_yaml(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


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
    if manifest.get("version") != "1.1.0":
        print("Manifest version must be 1.1.0 after primary witness admission")
        return 1
    if manifest.get("state") != "PRIMARY_RECONSTRUCTION_IN_PROGRESS":
        print("Manifest primary reconstruction state mismatch")
        return 1
    if manifest.get("next_required_unit", {}).get("id") != "XEN-PRI-RU-002":
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
    if primary_admission.get("scope", {}).get("initial_unit") != PRIMARY_UNIT_ID:
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
    if [unit.get("id") for unit in primary_units] != ["XEN-PRI-RU-001", "XEN-PRI-RU-002"]:
        print("Primary reading plan unit order mismatch")
        return 1
    if primary_units[0].get("status") != "DRAFTED_PENDING_OWNER_REVIEW":
        print("Primary first-unit status mismatch")
        return 1
    if primary_units[1].get("status") != "NEXT":
        print("Primary next-unit status mismatch")
        return 1
    if primary_reading_plan.get("comparison_gate", {}).get("strauss_comparison") != "DEFERRED":
        print("Strauss comparison must remain deferred")
        return 1

    primary_unit = documents[PRIMARY_UNIT_PATH]
    if primary_unit.get("unit_id") != PRIMARY_UNIT_ID:
        print("Primary unit identifier mismatch")
        return 1
    if primary_unit.get("status") != "DRAFTED_PENDING_OWNER_REVIEW":
        print("Primary unit status mismatch")
        return 1
    jurisdiction = primary_unit.get("jurisdiction", "")
    if "Translator wording is not unmediated Greek evidence" not in jurisdiction:
        print("Primary translation jurisdiction missing")
        return 1
    if primary_unit.get("secondary_comparison_status") != "DEFERRED":
        print("Primary unit secondary comparison must remain deferred")
        return 1
    if not primary_unit.get("documentary_observations"):
        print("Primary documentary observations missing")
        return 1
    if not primary_unit.get("standing_unresolved_questions"):
        print("Primary unresolved questions missing")
        return 1
    for observation in primary_unit["documentary_observations"]:
        if not observation.get("locator") or not observation.get("evidence_type"):
            print("Untyped or unlocated primary observation")
            return 1
    for question in primary_unit["standing_unresolved_questions"]:
        if question.get("evidence_type") != "UNRESOLVED_QUESTION":
            print("Primary unresolved question must be typed")
            return 1

    if manifest.get("primary_study", {}).get("drafted_units") != [PRIMARY_UNIT_ID]:
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
    if state.get("drafted_primary_units") != 1:
        print("Founding audit primary unit count mismatch")
        return 1
    if state.get("drafted_secondary_units") != 8:
        print("Founding audit secondary unit count mismatch")
        return 1
    if state.get("minister_adapter_derived") is not False:
        print("Adapter must remain underived")
        return 1

    print("Xenophon repository validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
