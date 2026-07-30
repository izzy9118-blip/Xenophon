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

    print("Xenophon repository validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
