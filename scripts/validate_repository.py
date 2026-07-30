from __future__ import annotations

from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
OWNER_REVIEW = ROOT / "governance/owner-reviews/2026-07-30-strauss-witness-review.yaml"
UNIT_IDS = [f"XEN-RU-{number:03d}" for number in range(1, 9)]
REQUIRED = [
    ROOT / "manifest.yaml",
    ROOT / "method/source-hierarchy.yaml",
    ROOT / "method/reading-protocol.yaml",
    ROOT / "corpus/index.yaml",
    ROOT / "corpus/sources/strauss-xenophons-anabasis.yaml",
    ROOT / "corpus/witnesses/strauss-spp-1983.yaml",
    ROOT / "studies/strauss-xenophons-anabasis/reading-plan.yaml",
    *[
        ROOT / f"studies/strauss-xenophons-anabasis/units/{unit_id}.yaml"
        for unit_id in UNIT_IDS
    ],
    ROOT / "adapter/report-contract.yaml",
    ROOT / "audits/founding-state.yaml",
    OWNER_REVIEW,
]


def load_yaml(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def main() -> int:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED if not path.exists()]
    if missing:
        print("Missing required files:", *missing, sep="\n- ")
        return 1

    documents = {path: load_yaml(path) for path in REQUIRED}
    manifest = documents[ROOT / "manifest.yaml"]
    if not isinstance(manifest, dict):
        print("manifest.yaml must contain a mapping")
        return 1
    if manifest.get("artificial_intelligence_self_certification_prohibited") is not True:
        print("AI self-certification safeguard must remain true")
        return 1
    if manifest.get("version") != "1.0.0":
        print("Manifest version must be 1.0.0 after owner adoption")
        return 1
    if manifest.get("state") != "SECONDARY_FOUNDING_OWNER_ADOPTED":
        print("Manifest secondary founding state mismatch")
        return 1

    corpus = documents[ROOT / "corpus/index.yaml"]
    if corpus["counts"]["primary_sources"] != 0:
        print("Primary source count must remain zero until a reviewed Xenophontic witness is admitted")
        return 1

    source = documents[ROOT / "corpus/sources/strauss-xenophons-anabasis.yaml"]
    if source.get("status") != "OWNER_ADOPTED_SECONDARY_SOURCE":
        print("Secondary source owner-adoption status mismatch")
        return 1

    witness = documents[ROOT / "corpus/witnesses/strauss-spp-1983.yaml"]
    if witness["source_id"] != "XEN-SRC-SEC-001":
        print("Witness/source linkage mismatch")
        return 1
    if witness.get("status") != "OWNER_ADOPTED_SECONDARY_WITNESS":
        print("Secondary witness owner-adoption status mismatch")
        return 1

    owner_review = documents[OWNER_REVIEW]
    if owner_review.get("status") != "OWNER_ADOPTED_SECONDARY_RECONSTRUCTION":
        print("Owner review status mismatch")
        return 1
    if owner_review.get("scope", {}).get("units") != UNIT_IDS:
        print("Owner review unit scope mismatch")
        return 1
    if owner_review.get("limits", [])[-1:] != ["Artificial-intelligence self-certification remains prohibited."]:
        print("Owner review safeguard missing")
        return 1

    reading_plan = documents[ROOT / "studies/strauss-xenophons-anabasis/reading-plan.yaml"]
    if reading_plan.get("status") != "OWNER_ADOPTED_SECONDARY_RECONSTRUCTION":
        print("Reading plan owner-adoption status mismatch")
        return 1
    drafted = {
        unit["id"]: unit
        for unit in reading_plan["reading_units"]
        if unit.get("status") == "DRAFTED_PENDING_OWNER_REVIEW"
    }
    if list(drafted) != UNIT_IDS:
        print("Reading plan drafted-unit order mismatch")
        return 1

    for unit_id in UNIT_IDS:
        record_path = ROOT / drafted[unit_id]["record"]
        record = documents[record_path]
        if record["unit_id"] != unit_id:
            print(f"Reading unit identifier mismatch for {unit_id}")
            return 1
        if record["status"] != "DRAFTED_PENDING_OWNER_REVIEW":
            print(f"Immutable reading unit status changed for {unit_id}")
            return 1
        if "no claim is promoted to Xenophon's teaching" not in record["jurisdiction"]:
            print(f"Secondary-source jurisdiction missing for {unit_id}")
            return 1
        if not record.get("documentary_observations"):
            print(f"Documentary observations missing for {unit_id}")
            return 1
        if not record.get("standing_unresolved_questions"):
            print(f"Standing unresolved questions missing for {unit_id}")
            return 1
        for observation in record["documentary_observations"]:
            if not observation.get("locator") or not observation.get("evidence_type"):
                print(f"Untyped or unlocated observation in {unit_id}")
                return 1

    next_units = [unit["id"] for unit in reading_plan["reading_units"] if unit.get("status") == "NEXT"]
    if next_units:
        print("No NEXT unit may remain after full witness coverage")
        return 1

    if manifest["secondary_study"]["drafted_units"] != UNIT_IDS:
        print("Manifest drafted-unit order mismatch")
        return 1
    if manifest["secondary_study"].get("status") != "OWNER_ADOPTED_SECONDARY_RECONSTRUCTION":
        print("Manifest secondary study status mismatch")
        return 1

    audit = documents[ROOT / "audits/founding-state.yaml"]
    if audit["repository_state"]["drafted_secondary_units"] != 8:
        print("Founding audit drafted-unit count mismatch")
        return 1
    if audit["repository_state"].get("secondary_study_owner_adopted") is not True:
        print("Founding audit owner-adoption state mismatch")
        return 1
    if audit["repository_state"].get("primary_witness_count") != 0:
        print("Founding audit must preserve the primary witness gap")
        return 1

    print("Xenophon repository validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
