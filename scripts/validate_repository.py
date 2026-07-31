from pathlib import Path
from collections import Counter
import sys, yaml, tempfile, shutil, subprocess, json

R = Path(__file__).resolve().parents[1]
P = R / "scripts/validate_repository_v1_56.py"
M = R / "manifest.yaml"
A = R / "audits/founding-state.yaml"
R1 = R / "studies/comparisons/anabasis-primary-strauss/XEN-CONTROLLED-COMPARISON-001-R1.yaml"
OR = R / "governance/owner-reviews/2026-07-31-controlled-comparison-r1-in-depth-review.yaml"
DR = R / "studies/comparisons/anabasis-primary-strauss/reviews/XEN-CONTROLLED-COMPARISON-R1-IN-DEPTH-REVIEW-001.yaml"
H = R / "history/2026-07-31-controlled-comparison-r1-in-depth-review.md"


def load(path):
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def dump(path, value):
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(value, f, sort_keys=False, allow_unicode=True)


def fail(message):
    print(message)
    return 1


def predecessor():
    if not P.exists():
        return fail("Frozen v1.56 validator missing")
    with tempfile.TemporaryDirectory() as d:
        t = Path(d) / "r"
        shutil.copytree(R, t, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        for source in [OR, DR, H]:
            target = t / source.relative_to(R)
            if target.exists():
                target.unlink()

        m = load(t / "manifest.yaml")
        m["version"] = "1.56.0"
        m["state"] = "CONTROLLED_COMPARISON_CORRECTED_DRAFT_COMPLETE_PENDING_OWNER_REVIEW"
        m["owner_reviews"] = m["owner_reviews"][:-1]
        m["current_phase"] = {
            "id": "XEN-PHASE-004",
            "name": "Strauss-guided controlled examination of the owner-adopted primary Anabasis reconstruction",
            "completion_status": "CORRECTED_DRAFT_COMPLETE_PENDING_OWNER_REVIEW",
        }
        m["primary_study"]["cumulative_reconstruction"]["secondary_comparison_status"] = "CORRECTED_DRAFT_COMPLETE_PENDING_OWNER_REVIEW"
        m["next_required_action"] = {
            "id": "XEN-CONTROLLED-COMPARISON-R1-OWNER-REVIEW-001",
            "description": "Owner review of the corrected Strauss-guided comparison before interpretive adoption, minister derivation, or Sanctum registration.",
        }
        q = m["controlled_comparison"]
        q["status"] = "CORRECTED_DRAFT_PENDING_OWNER_REVIEW"
        q["owner_review_status"] = "PENDING"
        for key in [
            "owner_review_record",
            "detailed_review_record",
            "r1_not_adopted",
            "review_disposition_counts",
            "required_next_revision",
        ]:
            q.pop(key, None)
        dump(t / "manifest.yaml", m)

        a = load(t / "audits/founding-state.yaml")
        r = a["repository_state"]
        r["controlled_comparison_owner_reviewed"] = False
        for key in [
            "controlled_comparison_in_depth_review_complete",
            "controlled_comparison_owner_adopted",
            "controlled_comparison_review_disposition",
            "controlled_comparison_owner_review_record",
            "controlled_comparison_detailed_review_record",
            "controlled_comparison_required_next_revision",
        ]:
            r.pop(key, None)
        a["resolved_items"] = a["resolved_items"][:-1]
        a["documented_gaps"][1] = {
            "id": "GAP-010",
            "description": "The corrected Strauss-guided controlled comparison is draft-complete but has not received owner review.",
            "blocks": [
                "owner-adopted comparative reconstruction",
                "controlled interpretive synthesis",
                "minister derivation",
            ],
        }
        a["next_required_action"] = "Conduct owner review of XEN-CONTROLLED-COMPARISON-001-R1 before interpretive adoption, minister adapter construction, or Sanctum registration."
        dump(t / "audits/founding-state.yaml", a)

        run = subprocess.run(
            [sys.executable, str(t / "scripts/validate_repository_v1_56.py")],
            cwd=t,
            text=True,
            capture_output=True,
        )
        if run.returncode:
            return fail("predecessor failed: " + (run.stdout + run.stderr).strip())
    return 0


def main():
    if predecessor():
        return 1
    required = [P, M, A, R1, OR, DR, H]
    if any(not p.exists() for p in required):
        return fail("Missing in-depth-review production file")

    m = load(M)
    a = load(A)
    r1 = load(R1)
    owner = load(OR)
    detail = load(DR)
    state = a.get("repository_state", {})
    comparison = m.get("controlled_comparison", {})

    if m.get("version") != "1.57.0" or m.get("state") != "CONTROLLED_COMPARISON_R1_IN_DEPTH_REVIEWED_RETURNED_FOR_REVISION":
        return fail("Manifest in-depth-review state mismatch")
    phase = m.get("current_phase", {})
    if phase.get("id") != "XEN-PHASE-004" or phase.get("completion_status") != "REVIEW_COMPLETE_SUBSTANTIVE_REVISION_REQUIRED" or "In-depth owner review" not in phase.get("name", ""):
        return fail("In-depth-review phase mismatch")
    if m.get("owner_reviews", [])[-1] != str(OR.relative_to(R)):
        return fail("In-depth owner-review registry mismatch")
    if m.get("primary_study", {}).get("cumulative_reconstruction", {}).get("secondary_comparison_status") != "R1_RETURNED_FOR_SUBSTANTIVE_REVISION":
        return fail("Primary comparison review gate mismatch")
    if m.get("next_required_action", {}).get("id") != "XEN-CONTROLLED-COMPARISON-001-R2":
        return fail("R2 next action mismatch")

    if comparison.get("id") != "XEN-CONTROLLED-COMPARISON-001" or comparison.get("revision_id") != "XEN-CONTROLLED-COMPARISON-001-R1":
        return fail("Reviewed comparison identity mismatch")
    if comparison.get("status") != "IN_DEPTH_REVIEW_COMPLETE_RETURNED_FOR_SUBSTANTIVE_REVISION":
        return fail("Reviewed comparison disposition mismatch")
    if comparison.get("owner_review_status") != "RETURNED_FOR_REVISION" or comparison.get("r1_not_adopted") is not True:
        return fail("Non-adoption control mismatch")
    if comparison.get("owner_review_record") != str(OR.relative_to(R)) or comparison.get("detailed_review_record") != str(DR.relative_to(R)):
        return fail("Review record path mismatch")
    if comparison.get("review_disposition_counts") != {
        "PASS_AS_CLASSIFIED": 11,
        "PASS_WITH_REQUIRED_REVISION": 11,
        "RECLASSIFY": 9,
    }:
        return fail("Review disposition count mismatch")
    if comparison.get("required_next_revision") != "XEN-CONTROLLED-COMPARISON-001-R2":
        return fail("Required revision mismatch")

    if r1.get("comparison_id") != "XEN-CONTROLLED-COMPARISON-001" or r1.get("revision_id") != "XEN-CONTROLLED-COMPARISON-001-R1" or r1.get("status") != "CORRECTED_DRAFT_PENDING_OWNER_REVIEW":
        return fail("R1 immutable production record was rewritten")

    if owner.get("review_id") != "XEN-OWNER-REVIEW-005" or owner.get("status") != "OWNER_DIRECTED_IN_DEPTH_REVIEW_RETURNED_FOR_SUBSTANTIVE_REVISION":
        return fail("Owner review identity mismatch")
    ruling = owner.get("owner_review_ruling", {})
    if ruling.get("comparison_status") != "RETURNED_FOR_SUBSTANTIVE_REVISION" or ruling.get("adoption_status") != "NOT_ADOPTED":
        return fail("Owner review ruling mismatch")
    results = owner.get("review_results", {})
    if results != {
        "pass_as_classified": 11,
        "pass_with_required_revision": 11,
        "reclassify": 9,
        "blocking_global_findings": 9,
        "major_global_findings": 2,
    }:
        return fail("Owner review result mismatch")
    if owner.get("required_next_action", {}).get("id") != "XEN-CONTROLLED-COMPARISON-001-R2":
        return fail("Owner ruling next action mismatch")

    if detail.get("review_id") != "XEN-CMP-R1-REVIEW-001" or detail.get("status") != "IN_DEPTH_REVIEW_COMPLETE_RETURN_FOR_SUBSTANTIVE_REVISION":
        return fail("Detailed review identity mismatch")
    dispositions = detail.get("entry_dispositions", [])
    if len(dispositions) != 31 or {x.get("entry_id") for x in dispositions} != {f"CMP-{i:03d}" for i in range(1, 32)}:
        return fail("Detailed review entry coverage mismatch")
    expected_dispositions = Counter({
        "PASS_AS_CLASSIFIED": 11,
        "PASS_WITH_REQUIRED_REVISION": 11,
        "RECLASSIFY": 9,
    })
    if Counter(x.get("disposition") for x in dispositions) != expected_dispositions:
        return fail("Detailed review disposition totals mismatch")
    if detail.get("disposition_counts") != {
        "entries_reviewed": 31,
        "pass_as_classified": 11,
        "pass_with_required_revision": 11,
        "reclassify": 9,
    }:
        return fail("Detailed review aggregate mismatch")
    required_reclasses = {
        "CMP-001": "GOVERNING_EXAMINATION",
        "CMP-006": "GOVERNING_ARCHITECTURE",
        "CMP-007": "GOVERNING_EXAMINATION",
        "CMP-008": "GOVERNING_EXAMINATION",
        "CMP-016": "GOVERNING_EXAMINATION",
        "CMP-018": "GOVERNING_EXAMINATION",
        "CMP-025": "GOVERNING_EXAMINATION",
        "CMP-026": "GOVERNING_EXAMINATION",
        "CMP-028": "GOVERNING_EXAMINATION",
    }
    if detail.get("required_reclassifications") != required_reclasses:
        return fail("Required reclassification map mismatch")
    findings = detail.get("global_findings", [])
    if len(findings) != 11 or Counter(x.get("severity") for x in findings) != Counter({"BLOCKING": 9, "MAJOR": 2}):
        return fail("Global finding count or severity mismatch")
    architecture = detail.get("required_r2_architecture", {})
    if architecture.get("revision_id") != "XEN-CONTROLLED-COMPARISON-001-R2" or architecture.get("sequential_argument_spine_required") is not True or architecture.get("new_active_classification") != "GOVERNING_ARCHITECTURE" or len(architecture.get("required_movements", [])) != 8:
        return fail("Required R2 architecture mismatch")
    if detail.get("ruling", {}).get("adopted") is not False or detail.get("ruling", {}).get("decision") != "RETURN_FOR_SUBSTANTIVE_REVISION":
        return fail("Detailed non-adoption ruling mismatch")

    if state.get("controlled_comparison_in_depth_review_complete") is not True or state.get("controlled_comparison_owner_reviewed") is not True or state.get("controlled_comparison_owner_adopted") is not False:
        return fail("Audit owner-review state mismatch")
    if state.get("controlled_comparison_review_disposition") != "RETURNED_FOR_SUBSTANTIVE_REVISION":
        return fail("Audit review disposition mismatch")
    if state.get("controlled_comparison_owner_review_record") != str(OR.relative_to(R)) or state.get("controlled_comparison_detailed_review_record") != str(DR.relative_to(R)):
        return fail("Audit review path mismatch")
    if state.get("controlled_comparison_required_next_revision") != "XEN-CONTROLLED-COMPARISON-001-R2":
        return fail("Audit next revision mismatch")
    if a.get("resolved_items", [])[-1].get("id") != "RES-016" or a.get("documented_gaps", [None, {}])[1].get("id") != "GAP-011":
        return fail("Audit in-depth-review transition mismatch")

    text = (json.dumps(owner, ensure_ascii=False, default=str) + " " + json.dumps(detail, ensure_ascii=False, default=str)).casefold()
    for phrase in [
        "in-depth review",
        "not_adopted",
        "returned_for_substantive_revision",
        "all thirty-one",
        "nine required reclassifications",
        "governing_architecture",
        "proxenos",
        "economic art",
        "book four",
        "manly and socratic justice",
        "thibron",
        "seuthes",
        "artificial-intelligence self-certification remains prohibited",
    ]:
        if phrase not in text:
            return fail("In-depth-review safeguard missing: " + phrase)

    history = H.read_text(encoding="utf-8")
    for phrase in [
        "in-depth review",
        "R1 is **not adopted**",
        "31 entries reviewed",
        "11 pass as classified",
        "11 pass only with required revision",
        "9 require reclassification",
        "XEN-CONTROLLED-COMPARISON-001-R2",
    ]:
        if phrase not in history:
            return fail("In-depth-review history safeguard missing: " + phrase)

    if m.get("artificial_intelligence_self_certification_prohibited") is not True or state.get("minister_adapter_derived") is not False or state.get("sanctum_registration_present") is not False:
        return fail("Governance gate mismatch")

    print("Xenophon repository validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
