from pathlib import Path
from collections import Counter
import json, sys, yaml, tempfile, shutil, subprocess
R=Path(__file__).resolve().parents[1]
P=R/"scripts/validate_repository_v1_58.py"
M=R/"manifest.yaml"
A=R/"audits/founding-state.yaml"
R2=R/"studies/comparisons/anabasis-primary-strauss/XEN-CONTROLLED-COMPARISON-001-R2.yaml"
SP=R/"studies/comparisons/anabasis-primary-strauss/r2/sequential-argument-spine.yaml"
EI=R/"studies/comparisons/anabasis-primary-strauss/r2/entry-integrations.yaml"
E1=R/"studies/comparisons/anabasis-primary-strauss/r2/entry-integrations-part-1.yaml"
E2=R/"studies/comparisons/anabasis-primary-strauss/r2/entry-integrations-part-2.yaml"
DE=R/"studies/comparisons/anabasis-primary-strauss/r2/deep-examinations.yaml"
REV=R/"studies/comparisons/anabasis-primary-strauss/reviews/XEN-CONTROLLED-COMPARISON-R2-IN-DEPTH-REVIEW-001.yaml"
OWN=R/"governance/owner-reviews/2026-07-31-controlled-comparison-r2-in-depth-review.yaml"
H=R/"history/2026-07-31-controlled-comparison-r2-in-depth-review.md"
def load(p):
    with p.open(encoding="utf-8") as f:return yaml.safe_load(f)
def dump(p,x):
    p.write_text(json.dumps(x,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
def fail(x):
    print(x);return 1
def predecessor():
    if not P.exists():return fail("Frozen v1.58 validator missing")
    with tempfile.TemporaryDirectory() as d:
        t=Path(d)/"r";shutil.copytree(R,t,ignore=shutil.ignore_patterns(".git","__pycache__"))
        for p in [REV,OWN,H]:
            q=t/p.relative_to(R)
            if q.exists():q.unlink()
        m=load(t/"manifest.yaml")
        m["version"]="1.58.0"
        m["state"]="CONTROLLED_COMPARISON_R2_DRAFT_COMPLETE_PENDING_IN_DEPTH_OWNER_REVIEW"
        m["owner_reviews"]=[x for x in m.get("owner_reviews",[]) if x!="governance/owner-reviews/2026-07-31-controlled-comparison-r2-in-depth-review.yaml"]
        m["current_phase"]={"id":"XEN-PHASE-005","name":"Sequential Strauss-guided reconstruction of the Anabasis comparison","completion_status":"R2_DRAFT_COMPLETE_PENDING_IN_DEPTH_OWNER_REVIEW"}
        m["primary_study"]["cumulative_reconstruction"]["secondary_comparison_status"]="R2_DRAFT_COMPLETE_PENDING_IN_DEPTH_OWNER_REVIEW"
        m["next_required_action"]={"id":"XEN-CONTROLLED-COMPARISON-R2-IN_DEPTH-OWNER-REVIEW-001","description":"Conduct an in-depth owner review of XEN-CONTROLLED-COMPARISON-001-R2 against its eight-movement sequential argument spine, all thirty-one entry integrations, the primary evidence record, and Strauss's complete essay before adoption or minister derivation."}
        q=m["controlled_comparison"]
        q["status"]="DRAFTED_PENDING_IN_DEPTH_OWNER_REVIEW"
        q["owner_review_status"]="PENDING_IN_DEPTH_REVIEW"
        for k in ["r2_in_depth_review_record","r2_owner_review_record","r2_preserved_not_adopted","source_exact_text_review_complete","r2_owner_reviewed","r2_owner_adopted","review_disposition","review_disposition_counts","required_next_revision","younger_older_cyrus_distinction_required","byzantium_deep_examination_required","post_question_coda_correction_required","thibron_primary_endpoint_preserved"]:
            q.pop(k,None)
        dump(t/"manifest.yaml",m)
        a=load(t/"audits/founding-state.yaml");rs=a["repository_state"]
        rs["controlled_comparison_owner_reviewed"]=False
        rs["controlled_comparison_review_disposition"]="R2_DRAFT_PENDING_IN_DEPTH_OWNER_REVIEW"
        rs["controlled_comparison_owner_review_record"]="governance/owner-reviews/2026-07-31-controlled-comparison-r1-in-depth-review.yaml"
        rs["controlled_comparison_detailed_review_record"]="studies/comparisons/anabasis-primary-strauss/reviews/XEN-CONTROLLED-COMPARISON-R1-IN-DEPTH-REVIEW-001.yaml"
        rs["controlled_comparison_required_next_revision"]=None
        rs["controlled_comparison_r2_owner_reviewed"]=False
        for k in ["controlled_comparison_r2_owner_adopted","controlled_comparison_r2_review_disposition","controlled_comparison_r2_exact_source_review_complete","controlled_comparison_r3_required","controlled_comparison_younger_older_cyrus_distinction_required","controlled_comparison_byzantium_deep_examination_required","controlled_comparison_post_question_coda_correction_required","controlled_comparison_thibron_primary_endpoint_preserved"]:
            rs.pop(k,None)
        rs["controlled_comparison_required_next_action"]="XEN-CONTROLLED-COMPARISON-R2-IN_DEPTH-OWNER-REVIEW-001"
        a["resolved_items"]=[x for x in a.get("resolved_items",[]) if x.get("id")!="RES-018"]
        a["documented_gaps"][1]={"id":"GAP-012","description":"The R2 sequential Strauss-guided comparison is draft-complete but has not undergone in-depth owner review.","blocks":["owner-adopted comparative reconstruction","controlled interpretive synthesis","minister derivation"]}
        a["next_required_action"]="Conduct an in-depth owner review of XEN-CONTROLLED-COMPARISON-001-R2 before adoption, minister adapter construction, or Sanctum registration."
        dump(t/"audits/founding-state.yaml",a)
        z=subprocess.run([sys.executable,str(t/"scripts/validate_repository_v1_58.py")],cwd=t,text=True,capture_output=True)
        if z.returncode:return fail("v1.58 predecessor failed: "+(z.stdout+z.stderr).strip())
    return 0
def main():
    if predecessor():return 1
    required=[P,M,A,R2,SP,EI,E1,E2,DE,REV,OWN,H]
    if any(not p.exists() for p in required):return fail("R2 review production file missing")
    m=load(M);a=load(A);r2=load(R2);rev=load(REV);own=load(OWN)
    if m.get("version")!="1.59.0" or m.get("state")!="CONTROLLED_COMPARISON_R2_IN_DEPTH_REVIEWED_RETURNED_FOR_TARGETED_REVISION":return fail("v1.59 manifest state mismatch")
    phase=m.get("current_phase",{})
    if phase.get("id")!="XEN-PHASE-005" or phase.get("completion_status")!="REVIEW_COMPLETE_TARGETED_R3_REVISION_REQUIRED":return fail("R2 review phase mismatch")
    q=m.get("controlled_comparison",{})
    if q.get("revision_id")!="XEN-CONTROLLED-COMPARISON-001-R2" or q.get("status")!="IN_DEPTH_REVIEW_COMPLETE_RETURNED_FOR_TARGETED_REVISION":return fail("Reviewed R2 identity mismatch")
    if q.get("owner_review_status")!="RETURNED_FOR_TARGETED_REVISION" or q.get("r2_owner_reviewed") is not True or q.get("r2_owner_adopted") is not False:return fail("R2 review gate mismatch")
    if q.get("r2_in_depth_review_record")!=str(REV.relative_to(R)) or q.get("r2_owner_review_record")!=str(OWN.relative_to(R)):return fail("R2 review path mismatch")
    if q.get("review_disposition_counts")!={"PASS_AS_INTEGRATED":21,"PASS_WITH_TARGETED_REVISION":8,"RESEQUENCE_REQUIRED":2}:return fail("R2 review disposition counts mismatch")
    for k in ["source_exact_text_review_complete","r2_preserved_not_adopted","younger_older_cyrus_distinction_required","byzantium_deep_examination_required","post_question_coda_correction_required","thibron_primary_endpoint_preserved"]:
        if q.get(k) is not True:return fail("R2 review safeguard missing: "+k)
    if q.get("required_next_revision")!="XEN-CONTROLLED-COMPARISON-001-R3" or m.get("next_required_action",{}).get("id")!="XEN-CONTROLLED-COMPARISON-001-R3":return fail("R3 next action mismatch")
    if r2.get("status")!="DRAFTED_PENDING_IN_DEPTH_OWNER_REVIEW":return fail("R2 immutable draft was rewritten")
    if rev.get("review_id")!="XEN-CMP-R2-REVIEW-001" or rev.get("status")!="IN_DEPTH_REVIEW_COMPLETE_RETURN_FOR_TARGETED_REVISION":return fail("Detailed R2 review identity mismatch")
    ruling=rev.get("overall_ruling",{})
    if ruling.get("disposition")!="RETURNED_FOR_TARGETED_REVISION" or ruling.get("adoption_status")!="NOT_ADOPTED" or ruling.get("revision_scope")!="TARGETED_NOT_WHOLESALE":return fail("Detailed R2 ruling mismatch")
    g=rev.get("global_findings",[])
    if len(g)!=6 or Counter(x.get("severity") for x in g)!=Counter({"PASS":2,"BLOCKING":2,"MAJOR":1,"PASS_WITH_LIMIT":1}):return fail("R2 global finding counts mismatch")
    text=json.dumps(rev,ensure_ascii=False).casefold()
    for phrase in ["younger cyrus","older cyrus","post_question_coda_booty","post_question_coda_gods_and_oaths","city, triremes, money, and army","thibron","not adopted","targeted not wholesale"]:
        if phrase not in text:return fail("R2 review substance missing: "+phrase)
    disp=rev.get("entry_dispositions",[])
    if len(disp)!=31 or [x.get("entry_id") for x in disp] != [f"CMP-{i:03d}" for i in range(1,32)]:return fail("R2 review entry coverage mismatch")
    if Counter(x.get("disposition") for x in disp)!=Counter({"PASS_AS_INTEGRATED":21,"PASS_WITH_TARGETED_REVISION":8,"RESEQUENCE_REQUIRED":2}):return fail("R2 review entry counts mismatch")
    affected={x.get("entry_id") for x in disp if x.get("disposition")!="PASS_AS_INTEGRATED"}
    if affected!={"CMP-001","CMP-004","CMP-006","CMP-016","CMP-018","CMP-019","CMP-027","CMP-028","CMP-029","CMP-030"}:return fail("R2 affected entry set mismatch")
    if own.get("review_id")!="XEN-OWNER-REVIEW-006" or own.get("status")!="OWNER_DIRECTED_IN_DEPTH_REVIEW_RETURNED_FOR_TARGETED_REVISION":return fail("Owner R2 review identity mismatch")
    if own.get("owner_review_ruling",{}).get("adoption_status")!="NOT_ADOPTED" or own.get("required_next_action",{}).get("id")!="XEN-CONTROLLED-COMPARISON-001-R3":return fail("Owner R2 review ruling mismatch")
    rs=a.get("repository_state",{})
    if rs.get("controlled_comparison_r2_owner_reviewed") is not True or rs.get("controlled_comparison_r2_owner_adopted") is not False:return fail("Audit R2 review mismatch")
    if rs.get("controlled_comparison_r3_required") is not True or rs.get("controlled_comparison_required_next_action")!="XEN-CONTROLLED-COMPARISON-001-R3":return fail("Audit R3 requirement mismatch")
    if a.get("resolved_items",[])[-1].get("id")!="RES-018" or a.get("documented_gaps",[])[1].get("id")!="GAP-013":return fail("Audit R2 review transition mismatch")
    if m.get("artificial_intelligence_self_certification_prohibited") is not True or rs.get("minister_adapter_derived") is not False or rs.get("sanctum_registration_present") is not False:return fail("R2 review governance gate mismatch")
    hist=H.read_text(encoding="utf-8")
    for phrase in ["R2 is not adopted","younger Cyrus","older Cyrus","war for booty","Byzantium","XEN-CONTROLLED-COMPARISON-001-R3"]:
        if phrase not in hist:return fail("R2 review history safeguard missing: "+phrase)
    print("Xenophon repository validation passed");return 0
if __name__=="__main__":sys.exit(main())
