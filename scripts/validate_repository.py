from __future__ import annotations

from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    ROOT / "manifest.yaml",
    ROOT / "method/source-hierarchy.yaml",
    ROOT / "method/reading-protocol.yaml",
    ROOT / "corpus/index.yaml",
    ROOT / "corpus/sources/strauss-xenophons-anabasis.yaml",
    ROOT / "corpus/witnesses/strauss-spp-1983.yaml",
    ROOT / "studies/strauss-xenophons-anabasis/reading-plan.yaml",
    ROOT / "studies/strauss-xenophons-anabasis/units/XEN-RU-001.yaml",
    ROOT / "studies/strauss-xenophons-anabasis/units/XEN-RU-002.yaml",
    ROOT / "studies/strauss-xenophons-anabasis/units/XEN-RU-003.yaml",
    ROOT / "studies/strauss-xenophons-anabasis/units/XEN-RU-004.yaml",
    ROOT / "adapter/report-contract.yaml",
    ROOT / "audits/founding-state.yaml",
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

    corpus = documents[ROOT / "corpus/index.yaml"]
    if corpus["counts"]["primary_sources"] != 0:
        print("Primary source count must remain zero until a reviewed Xenophontic witness is admitted")
        return 1

    witness = documents[ROOT / "corpus/witnesses/strauss-spp-1983.yaml"]
    if witness["source_id"] != "XEN-SRC-SEC-001":
        print("Witness/source linkage mismatch")
        return 1

    reading_plan = documents[ROOT / "studies/strauss-xenophons-anabasis/reading-plan.yaml"]
    drafted = {
        unit["id"]: unit
        for unit in reading_plan["reading_units"]
        if unit.get("status") == "DRAFTED_PENDING_OWNER_REVIEW"
    }
    expected_drafted = {"XEN-RU-001", "XEN-RU-002", "XEN-RU-003", "XEN-RU-004"}
    if set(drafted) != expected_drafted:
        print("Reading plan drafted-unit set mismatch")
        return 1

    for unit_id in sorted(expected_drafted):
        record_path = ROOT / drafted[unit_id]["record"]
        record = documents[record_path]
        if record["unit_id"] != unit_id:
            print(f"Reading unit identifier mismatch for {unit_id}")
            return 1
        if record["status"] != "DRAFTED_PENDING_OWNER_REVIEW":
            print(f"Reading unit status mismatch for {unit_id}")
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
    if next_units != ["XEN-RU-005"]:
        print("Reading plan must identify XEN-RU-005 as the sole next unit")
        return 1

    expected_manifest_units = ["XEN-RU-001", "XEN-RU-002", "XEN-RU-003", "XEN-RU-004"]
    if manifest["secondary_study"]["drafted_units"] != expected_manifest_units:
        print("Manifest drafted-unit order mismatch")
        return 1
    if manifest["next_required_unit"]["id"] != "XEN-RU-005":
        print("Manifest next-unit mismatch")
        return 1

    audit = documents[ROOT / "audits/founding-state.yaml"]
    if audit["repository_state"]["drafted_secondary_units"] != 4:
        print("Founding audit drafted-unit count mismatch")
        return 1

    print("Xenophon repository validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())