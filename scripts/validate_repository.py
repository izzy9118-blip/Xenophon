from pathlib import Path
from collections import Counter
import json, sys, yaml, tempfile, shutil, subprocess
R=Path(__file__).resolve().parents[1]
P=R/"scripts/validate_repository_v1_59.py"
M=R/"manifest.yaml"
A=R/"audits/founding-state.yaml"
R3=R/"studies/comparisons/anabasis-primary-strauss/XEN-CONTROLLED-COMPARISON-001-R3.yaml"
SP=R/"studies/comparisons/anabasis-primary-strauss/r3/targeted-argument-spine.yaml"
CA=R/"studies/comparisons/anabasis-primary-strauss/r3/controlled-cyrus-ambiguity.yaml"
BYZ=R/"studies/comparisons/anabasis-primary-strauss/r3/byzantium-examination.yaml"
CODA=R/"studies/comparisons/anabasis-primary-strauss/r3/final-coda-sequence.yaml"
EC=R/"studies/comparisons/anabasis-primary-strauss/r3/entry-corrections.yaml"
DE=R/"studies/comparisons/anabasis-primary-strauss/r3/deep-examinations.yaml"
COR=R/"governance/corrections/2026-07-31-r2-cyrus-ambiguity-clarification.yaml"
H=R/"history/2026-07-31-controlled-comparison-r3-targeted-draft-completion.md"
R2=R/"studies/comparisons/anabasis-primary-strauss/XEN-CONTROLLED-COMPARISON-001-R2.yaml"
def load(p):
    with p.open(encoding="utf-8") as f:return yaml.safe_load(f)
def dump(p,x):
    p.write_text(json.dumps(x,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
def fail(x):
    print(x);return 1
def predecessor():
    if not P.exists():return fail("Frozen v1.59 validator missing")
    with tempfile.TemporaryDirectory() as d:
        t=Path(d)/"r";shutil.copytree(R,t,ignore=shutil.ignore_patterns(".git","__pycache__"))
        for p in [R3,SP,CA,BYZ,CODA,EC,DE,COR,H]:
            q=t/p.relative_to(R)
            if q.exists():q.unlink()
        m=load(t/"manifest.yaml")
        m["version"]="1.59.0"
        m["state"]="CONTROLLED_COMPARISON_R2_IN_DEPTH_REVIEWED_RETURNED_FOR_TARGETED_REVISION"
        m["current_phase"]={"id":"XEN-PHASE-005","name":"In-depth owner review of the sequential Strauss-guided Anabasis comparison R2","completion_status":"REVIEW_COMPLETE_TARGETED_R3_REVISION_REQUIRED"}
        m["primary_study"]["cumulative_reconstruction"]["secondary_comparison_status"]="R2_IN_DEPTH_REVIEWED_RETURNED_FOR_TARGETED_REVISION"
        m["next_required_action"]={"id":"XEN-CONTROLLED-COMPARISON-001-R3","description":"Produce an additive targeted R3 preserving R2's sequential architecture while distinguishing younger Cyrus from older Cyrus, adding a Byzantium deep examination, and restoring Strauss's exact post-question booty and gods-and-oaths coda before another in-depth owner review."}
        m["controlled_comparison"]={"id":"XEN-CONTROLLED-COMPARISON-001","revision_id":"XEN-CONTROLLED-COMPARISON-001-R2","status":"IN_DEPTH_REVIEW_COMPLETE_RETURNED_FOR_TARGETED_REVISION","record":"studies/comparisons/anabasis-primary-strauss/XEN-CONTROLLED-COMPARISON-001-R2.yaml","predecessor_revision":"XEN-CONTROLLED-COMPARISON-001-R1","predecessor_record":"studies/comparisons/anabasis-primary-strauss/XEN-CONTROLLED-COMPARISON-001-R1.yaml","original_record":"studies/comparisons/anabasis-primary-strauss/XEN-CONTROLLED-COMPARISON-001.yaml","r2_in_depth_review_record":"studies/comparisons/anabasis-primary-strauss/reviews/XEN-CONTROLLED-COMPARISON-R2-IN-DEPTH-REVIEW-001.yaml","r2_owner_review_record":"governance/owner-reviews/2026-07-31-controlled-comparison-r2-in-depth-review.yaml","comparison_entry_count":31,"sequential_movement_count":8,"deep_examination_count":7,"classification_counts":{"GOVERNING_ARCHITECTURE":1,"GOVERNING_EXAMINATION":10,"CYRUS_SIDE_ELABORATION":2,"AGREEMENT":9,"QUALIFIED_AGREEMENT":5,"PRIMARY_SILENCE":3,"UNRESOLVED_RELATION":1},"review_application_counts":{"RETAINED":11,"REVISED_IN_PLACE":11,"RECLASSIFIED":9},"owner_review_status":"RETURNED_FOR_TARGETED_REVISION","source_independence_preserved":True,"strauss_guiding_architecture":True,"governing_opposition":"SOCRATES_VS_CYRUS","sequential_argument_spine_present":True,"proxenos_mediation_restored":True,"economic_art_integrated":True,"book_four_justice_transition_integrated":True,"justice_examination_expanded":True,"ending_examination_expanded":True,"r1_preserved_not_adopted":True,"r2_preserved_not_adopted":True,"historical_predecessors_preserved":True,"source_exact_text_review_complete":True,"r2_owner_reviewed":True,"r2_owner_adopted":False,"review_disposition":"RETURNED_FOR_TARGETED_REVISION","review_disposition_counts":{"PASS_AS_INTEGRATED":21,"PASS_WITH_TARGETED_REVISION":8,"RESEQUENCE_REQUIRED":2},"required_next_revision":"XEN-CONTROLLED-COMPARISON-001-R3","younger_older_cyrus_distinction_required":True,"byzantium_deep_examination_required":True,"post_question_coda_correction_required":True,"thibron_primary_endpoint_preserved":True}
        dump(t/"manifest.yaml",m)
        a=load(t/"audits/founding-state.yaml");rs=a["repository_state"]
        rs["controlled_comparison_record"]="studies/comparisons/anabasis-primary-strauss/XEN-CONTROLLED-COMPARISON-001-R2.yaml"
        rs["controlled_comparison_correction_record"]="governance/corrections/2026-07-31-controlled-comparison-strauss-guiding-architecture.yaml"
        rs["controlled_comparison_owner_reviewed"]=True
        rs["controlled_comparison_review_disposition"]="R2_RETURNED_FOR_TARGETED_REVISION"
        rs["controlled_comparison_owner_review_record"]="governance/owner-reviews/2026-07-31-controlled-comparison-r2-in-depth-review.yaml"
        rs["controlled_comparison_detailed_review_record"]="studies/comparisons/anabasis-primary-strauss/reviews/XEN-CONTROLLED-COMPARISON-R2-IN-DEPTH-REVIEW-001.yaml"
        rs["controlled_comparison_required_next_revision"]="XEN-CONTROLLED-COMPARISON-001-R3"
        rs["controlled_comparison_active_revision"]="XEN-CONTROLLED-COMPARISON-001-R2"
        for k in list(rs):
            if k.startswith("controlled_comparison_r3_") and k!="controlled_comparison_r3_required":rs.pop(k,None)
        rs["controlled_comparison_r3_required"]=True
        rs["controlled_comparison_required_next_action"]="XEN-CONTROLLED-COMPARISON-001-R3"
        a["resolved_items"]=[x for x in a.get("resolved_items",[]) if x.get("id")!="RES-019"]
        a["documented_gaps"][1]={"id":"GAP-013","description":"R2 completed exact-source in-depth review but was not adopted; targeted R3 correction is required for the younger/older Cyrus distinction, Byzantium, and Strauss's final post-question coda.","blocks":["owner-adopted comparative reconstruction","controlled interpretive synthesis","minister derivation"]}
        a["next_required_action"]="Produce XEN-CONTROLLED-COMPARISON-001-R3 as an additive targeted revision before another in-depth owner review, minister adapter construction, or Sanctum registration."
        dump(t/"audits/founding-state.yaml",a)
        z=subprocess.run([sys.executable,str(t/"scripts/validate_repository_v1_59.py")],cwd=t,text=True,capture_output=True)
        if z.returncode:return fail("v1.59 predecessor failed: "+(z.stdout+z.stderr).strip())
    return 0
def main():
    if predecessor():return 1
    required=[P,M,A,R3,SP,CA,BYZ,CODA,EC,DE,COR,H,R2]
    if any(not p.exists() for p in required):return fail("R3 production file missing")
    m=load(M);a=load(A);r3=load(R3);sp=load(SP);ca=load(CA);byz=load(BYZ);coda=load(CODA);ec=load(EC);de=load(DE);cor=load(COR);r2=load(R2)
    if m.get("version")!="1.60.0" or m.get("state")!="CONTROLLED_COMPARISON_R3_DRAFT_COMPLETE_PENDING_IN_DEPTH_OWNER_REVIEW":return fail("v1.60 manifest state mismatch")
    phase=m.get("current_phase",{})
    if phase.get("id")!="XEN-PHASE-006" or phase.get("completion_status")!="R3_DRAFT_COMPLETE_PENDING_IN_DEPTH_OWNER_REVIEW":return fail("R3 phase mismatch")
    q=m.get("controlled_comparison",{})
    if q.get("revision_id")!="XEN-CONTROLLED-COMPARISON-001-R3" or q.get("status")!="DRAFTED_PENDING_IN_DEPTH_OWNER_REVIEW":return fail("R3 manifest identity mismatch")
    if q.get("record")!=str(R3.relative_to(R)) or q.get("predecessor_record")!=str(R2.relative_to(R)):return fail("R3 manifest path mismatch")
    expected={"GOVERNING_ARCHITECTURE":1,"GOVERNING_EXAMINATION":10,"CYRUS_SIDE_ELABORATION":2,"AGREEMENT":9,"QUALIFIED_AGREEMENT":5,"PRIMARY_SILENCE":3,"UNRESOLVED_RELATION":1}
    if q.get("classification_counts")!=expected:return fail("R3 classification mismatch")
    if q.get("targeted_revision_counts")!={"PASS_THROUGH":21,"TARGETED_REVISION":8,"RESEQUENCE_REQUIRED":2}:return fail("R3 targeted counts mismatch")
    if q.get("comparison_entry_count")!=31 or q.get("sequential_movement_count")!=8 or q.get("deep_examination_count")!=8:return fail("R3 count mismatch")
    for k in ["controlled_intended_cyrus_ambiguity","younger_cyrus_role_distinguished","older_cyrus_role_distinguished","distinction_without_compartmentalization","justice_ambiguity_governs_cyrus_ambiguity","r2_eight_movement_spine_preserved","all_31_entry_ids_preserved","all_r2_classifications_preserved","byzantium_deep_examination_present","byzantium_foundation_monarchy_convergence_present","post_question_coda_exact_order_present","post_question_booty_present","final_gods_and_oaths_emphasis_present","thibron_primary_endpoint_preserved","primary_endpoint_and_textual_coda_distinguished","r1_preserved_not_adopted","r2_preserved_not_adopted","historical_predecessors_preserved"]:
        if q.get(k) is not True:return fail("R3 safeguard missing: "+k)
    if m.get("next_required_action",{}).get("id")!="XEN-CONTROLLED-COMPARISON-R3-IN_DEPTH-OWNER-REVIEW-001":return fail("R3 next action mismatch")
    if r3.get("revision_id")!="XEN-CONTROLLED-COMPARISON-001-R3" or r3.get("status")!="DRAFTED_PENDING_IN_DEPTH_OWNER_REVIEW":return fail("R3 record identity mismatch")
    if r3.get("classification_counts")!=expected:return fail("R3 record classification mismatch")
    if r3.get("preserved_counts")!={"sequential_movements":8,"comparison_entries":31}:return fail("R3 preserved counts mismatch")
    ga=r3.get("governing_architecture",{})
    if ga.get("cyrus_control")!="CONTROLLED_INTENDED_AMBIGUITY":return fail("R3 Cyrus control mismatch")
    terms=ga.get("controlled_terms",{})
    if set(terms)!={"YOUNGER_CYRUS_ROLE","OLDER_CYRUS_ROLE","CYRUS_SIDE_AMBIGUITY"}:return fail("R3 Cyrus terms mismatch")
    if ga.get("ending_order")!=["SOCRATIC_APPREHENSION_QUESTION","POST_QUESTION_CODA_BOOTY","POST_QUESTION_CODA_GODS_AND_OATHS"]:return fail("R3 ending order mismatch")
    if cor.get("correction_id")!="XEN-COR-002" or cor.get("status")!="OWNER_DIRECTED_INTERPRETIVE_CLARIFICATION":return fail("R3 owner clarification mismatch")
    if cor.get("r3_effect",{}).get("replace_term")!="CYRUS_SIDE_ABSTRACTION" or cor.get("r3_effect",{}).get("with_term")!="CYRUS_SIDE_AMBIGUITY":return fail("R3 ambiguity correction mismatch")
    moves=sp.get("movements",[])
    if len(moves)!=8 or [x.get("id") for x in moves] != [f"R3-MOV-{i:03d}" for i in range(1,9)]:return fail("R3 movement spine mismatch")
    if [x.get("inherits") for x in moves] != [f"R2-MOV-{i:03d}" for i in range(1,9)]:return fail("R2 spine inheritance mismatch")
    if ca.get("control_id")!="XEN-R3-CYRUS-AMBIGUITY-001" or len(ca.get("source_sequence",[]))!=6:return fail("Controlled Cyrus ambiguity record mismatch")
    if ca.get("justice_structure",{}).get("explicit_statement")!="Justice is an ambiguous term.":return fail("Justice ambiguity safeguard missing")
    if byz.get("examination_id")!="XEN-R3-BYZANTIUM-001" or len(byz.get("sequence",[]))!=6:return fail("Byzantium examination mismatch")
    bt=json.dumps(byz,ensure_ascii=False).casefold()
    for phrase in ["city, triremes, money, and many soldiers","wholly innocent greek city","voluntary restraint","stronger evidence than a verbal denial"]:
        if phrase not in bt:return fail("Byzantium safeguard missing: "+phrase)
    ordered=coda.get("ordered_elements",[])
    if [x.get("id") for x in ordered] != ["SOCRATIC_APPREHENSION_QUESTION","POST_QUESTION_CODA_BOOTY","POST_QUESTION_CODA_GODS_AND_OATHS"]:return fail("Final coda sequence mismatch")
    if coda.get("primary_endpoint_relation",{}).get("THIBRON_INCORPORATION") is None:return fail("Thibron endpoint missing")
    entries=ec.get("entries",[])
    if len(entries)!=10 or Counter(x.get("r3_action") for x in entries)!=Counter({"TARGETED_REVISION":8,"RESEQUENCE_REQUIRED":2}):return fail("R3 entry correction counts mismatch")
    if [x.get("entry_id") for x in entries] != ["CMP-001","CMP-004","CMP-006","CMP-016","CMP-018","CMP-019","CMP-027","CMP-028","CMP-029","CMP-030"]:return fail("R3 affected entry set mismatch")
    if de.get("examination_count")!=8 or len(de.get("examinations",[]))!=8:return fail("R3 deep examination count mismatch")
    if r2.get("status")!="DRAFTED_PENDING_IN_DEPTH_OWNER_REVIEW":return fail("R2 immutable draft changed")
    text=" ".join(json.dumps(x,ensure_ascii=False) for x in [r3,sp,ca,byz,coda,ec,de,cor]).casefold()
    for phrase in ["intended ambiguity","distinction must not become compartmentalization","younger cyrus","older cyrus","justice is an ambiguous term","byzantium","post_question_coda_booty","post_question_coda_gods_and_oaths","thibron","not two equal closures"]:
        if phrase not in text:return fail("R3 substantive safeguard missing: "+phrase)
    rs=a.get("repository_state",{})
    if rs.get("controlled_comparison_r3_drafted") is not True or rs.get("controlled_comparison_r3_draft_complete") is not True or rs.get("controlled_comparison_r3_owner_reviewed") is not False:return fail("R3 audit production mismatch")
    if rs.get("controlled_comparison_r3_controlled_intended_cyrus_ambiguity") is not True or rs.get("controlled_comparison_r3_distinction_without_compartmentalization") is not True:return fail("R3 audit ambiguity mismatch")
    if a.get("resolved_items",[])[-1].get("id")!="RES-019" or a.get("documented_gaps",[])[1].get("id")!="GAP-014":return fail("R3 audit transition mismatch")
    if m.get("artificial_intelligence_self_certification_prohibited") is not True or rs.get("minister_adapter_derived") is not False or rs.get("sanctum_registration_present") is not False:return fail("R3 governance gate mismatch")
    hist=H.read_text(encoding="utf-8")
    for phrase in ["ambiguity between the younger and older Cyrus is intended","eight R2 movements","Byzantium","Socrates' apprehension question","war for booty","gods and formal oaths","DRAFTED_PENDING_IN_DEPTH_OWNER_REVIEW"]:
        if phrase not in hist:return fail("R3 history safeguard missing: "+phrase)
    print("Xenophon repository validation passed");return 0
if __name__=="__main__":sys.exit(main())
