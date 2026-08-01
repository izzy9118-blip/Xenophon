from pathlib import Path
import subprocess
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
COMMIT = "fe7171b4caca347ebd1fdcb7f2d221efa3bf3324"


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
    review = yaml.safe_load(show("speech/reviews/XEN-MINISTER-ADAPTER-IN-DEPTH-REVIEW-001.yaml"))
    owner = yaml.safe_load(show("governance/owner-reviews/2026-08-01-xenophon-minister-adapter-in-depth-review.yaml"))
    if manifest.get("version") != "1.68.0":
        print("v1.68 predecessor manifest version mismatch")
        return 1
    if manifest.get("state") != "MINISTER_ADAPTER_IN_DEPTH_REVIEWED_RETURNED_FOR_TARGETED_R1":
        print("v1.68 predecessor state mismatch")
        return 1
    if review.get("disposition_counts") != {"PASS": 9, "PASS_WITH_LIMIT": 1, "BLOCKING_REVISION": 5}:
        print("v1.68 predecessor review counts mismatch")
        return 1
    if owner.get("owner_ruling", {}).get("adoption_status") != "NOT_ADOPTED":
        print("v1.68 predecessor owner ruling mismatch")
        return 1
    print("Xenophon v1.68 predecessor verification passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
