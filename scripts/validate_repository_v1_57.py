from pathlib import Path
import sys, yaml
R = Path(__file__).resolve().parents[1]
def load(path):
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)
def fail(msg):
    print(msg)
    return 1
def main():
    m = load(R/"manifest.yaml")
    a = load(R/"audits/founding-state.yaml")
    review = R/"governance/owner-reviews/2026-07-31-controlled-comparison-r1-in-depth-review.yaml"
    detail = R/"studies/comparisons/anabasis-primary-strauss/reviews/XEN-CONTROLLED-COMPARISON-R1-IN-DEPTH-REVIEW-001.yaml"
    r1 = R/"studies/comparisons/anabasis-primary-strauss/XEN-CONTROLLED-COMPARISON-001-R1.yaml"
    if any(not p.exists() for p in [review, detail, r1]):
        return fail("v1.57 review file missing")
    if m.get("version") != "1.57.0" or m.get("state") != "CONTROLLED_COMPARISON_R1_IN_DEPTH_REVIEWED_RETURNED_FOR_REVISION":
        return fail("v1.57 manifest state mismatch")
    q = m.get("controlled_comparison", {})
    if q.get("revision_id") != "XEN-CONTROLLED-COMPARISON-001-R1":
        return fail("v1.57 revision mismatch")
    if q.get("owner_review_status") != "RETURNED_FOR_REVISION" or q.get("r1_not_adopted") is not True:
        return fail("v1.57 review disposition mismatch")
    if q.get("review_disposition_counts") != {"PASS_AS_CLASSIFIED":11,"PASS_WITH_REQUIRED_REVISION":11,"RECLASSIFY":9}:
        return fail("v1.57 disposition counts mismatch")
    rs = a.get("repository_state", {})
    if rs.get("controlled_comparison_in_depth_review_complete") is not True:
        return fail("v1.57 audit review missing")
    if rs.get("controlled_comparison_owner_adopted") is not False:
        return fail("v1.57 adoption gate mismatch")
    if rs.get("controlled_comparison_review_disposition") != "RETURNED_FOR_SUBSTANTIVE_REVISION":
        return fail("v1.57 audit disposition mismatch")
    if rs.get("minister_adapter_derived") is not False or rs.get("sanctum_registration_present") is not False:
        return fail("v1.57 ministry gate mismatch")
    if m.get("artificial_intelligence_self_certification_prohibited") is not True:
        return fail("v1.57 self-certification gate missing")
    print("Xenophon repository v1.57 validation passed")
    return 0
if __name__ == "__main__":
    sys.exit(main())
