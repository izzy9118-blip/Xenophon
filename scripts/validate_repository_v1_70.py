from pathlib import Path
import subprocess
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
COMMIT = "358fad19ea3361c027ba584fa41307f29c1338dd"


def show(path: str) -> str:
    process = subprocess.run(
        ["git", "show", f"{COMMIT}:{path}"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if process.returncode:
        raise RuntimeError(process.stderr.strip() or f"missing predecessor path: {path}")
    return process.stdout


def main() -> int:
    manifest = yaml.safe_load(show("manifest.yaml"))
    adoption = yaml.safe_load(show("governance/owner-reviews/2026-08-10-hieron-on-tyranny-in-depth-review.yaml"))
    audit = yaml.safe_load(show("audits/hieron-on-tyranny-owner-adoption-state.yaml"))
    if manifest.get("version") != "1.70.0":
        print("v1.70 predecessor manifest version mismatch")
        return 1
    if manifest.get("state") != "OPERATIONAL_OWNER_AUTHORIZED_OPEN_RESEARCH":
        print("v1.70 predecessor state mismatch")
        return 1
    if manifest.get("minister_adapter", {}).get("id") != "XEN-MINISTER-ADAPTER-001-R1":
        print("v1.70 predecessor adapter mismatch")
        return 1
    research = manifest.get("owner_adopted_open_research", {}).get("hieron_on_tyranny", {})
    if research.get("operational_adapter_effect") != "none":
        print("v1.70 Hieron predecessor state mismatch")
        return 1
    if adoption.get("review_id") != "XEN-OWNER-REVIEW-013":
        print("v1.70 Hieron adoption record mismatch")
        return 1
    state = audit.get("current_repository_state", {})
    if state.get("active_adapter_source_line") != "Anabasis only" or state.get("active_adapter_effect") != "none":
        print("v1.70 adoption audit mismatch")
        return 1
    print("Xenophon v1.70 predecessor verification passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
