from pathlib import Path
from collections import Counter
import json, sys, yaml, tempfile, shutil, subprocess
R=Path(__file__).resolve().parents[1]
P=R/"scripts/validate_repository_v1_57.py"
M=R/"manifest.yaml"
A=R/"audits/founding-state.yaml"
R2=R/"studies/comparisons/anabasis-primary-strauss/XEN-CONTROLLED-COMPARISON-001-R2.yaml"
SP=R/"studies/comparisons/anabasis-primary-strauss/r2/sequential-argument-spine.yaml"
EI=R/"studies/comparisons/anabasis-primary-strauss/r2/entry-integrations.yaml"
E1=R/"studies/comparisons/anabasis-primary-strauss/r2/entry-integrations-part-1.yaml"
E2=R/"studies/comparisons/anabasis-primary-strauss/r2/entry-integrations-part-2.yaml"
DE=R/"studies/comparisons/anabasis-primary-strauss/r2/deep-examinations.yaml"
H=R/"history/2026-07-31-controlled-comparison-r2-draft-completion.md"
R1=R/"studies/comparisons/anabasis-primary-strauss/XEN-CONTROLLED-COMPARISON-001-R1.yaml"
REV=R/"studies/comparisons/anabasis-primary-strauss/reviews/XEN-CONTROLLED-COMPARISON-R1-IN-DEPTH-REVIEW-001.yaml"
def load(p):
    with p.open(encoding="utf-8") as f:return yaml.safe_load(f)
def dump(p,x):
    p.write_text(json.dumps(x,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
def fail(x):
    print(x);return 1
def predecessor():
    if not P.exists():return fail("Frozen v1.57 validator missing")
    with tempfile.TemporaryDirectory() as d:
        t=Path(d)/"r";shutil.copytree(R,t,ignore=shutil.ignore_patterns(".git","__pycache__"))
        for p in [R2,SP,EI,E1,E2,DE,H]:
            q=t/p.relative_to(R)
            if q.exists():q.unlink()
        m=load(t/"manifest.yaml")
        m["version"]="1.57.0"
        m["state"]="CONTROLLED_COMPARISON_R1_IN_DEPTH_REVIEWED_RETURNED_FOR_REVISION"
        m["current_phase"]={"id":"XEN-PHASE-004","name":"In-depth owner review of the Strauss-guided Anabasis comparison","completion_status":"REVIEW_COMPLETE_SUBSTANTIVE_REVISION_REQUIRED"}
        m["primary_study"]["cumulative_reconstruction"]["secondary_comparison_status"]="R1_RETURNED_FOR_SUBSTANTIVE_REVISION"
        m["next_required_action"]={"id":"XEN-CONTROLLED-COMPARISON-001-R2","description":"Produce additive R2 before another owner review."}
        m["controlled_comparison"]={"id":"XEN-CONTROLLED-COMPARISON-001","revision_id":"XEN-CONTROLLED-COMPARISON-001-R1","status":"IN_DEPTH_REVIEW_COMPLETE_RETURNED_FOR_SUBSTANTIVE_REVISION","record":"studies/comparisons/anabasis-primary-strauss/XEN-CONTROLLED-COMPARISON-001-R1.yaml","owner_review_status":"RETURNED_FOR_REVISION","r1_not_adopted":True,"review_disposition_counts":{"PASS_AS_CLASSIFIED":11,"PASS_WITH_REQUIRED_REVISION":11,"RECLASSIFY":9}}
        dump(t/"manifest.yaml",m)
        a=load(t/"audits/founding-state.yaml");rs=a["repository_state"]
        rs["controlled_comparison_in_depth_review_complete"]=True
        rs["controlled_comparison_owner_adopted"]=False
        rs["controlled_comparison_review_disposition"]="RETURNED_FOR_SUBSTANTIVE_REVISION"
        rs["minister_adapter_derived"]=False
        rs["sanctum_registration_present"]=False
        dump(t/"audits/founding-state.yaml",a)
        z=subprocess.run([sys.executable,str(t/"scripts/validate_repository_v1_57.py")],cwd=t,text=True,capture_output=True)
        if z.returncode:return fail("v1.57 predecessor failed: "+(z.stdout+z.stderr).strip())
    return 0
def main():
    if predecessor():return 1
    required=[P,M,A,R2,SP,EI,E1,E2,DE,H,R1,REV]
    if any(not p.exists() for p in required):return fail("R2 production file missing")
    m=load(M);a=load(A);r2=load(R2);sp=load(SP);ei=load(EI);e1=load(E1);e2=load(E2);de=load(DE)
    if m.get("version")!="1.58.0" or m.get("state")!="CONTROLLED_COMPARISON_R2_DRAFT_COMPLETE_PENDING_IN_DEPTH_OWNER_REVIEW":return fail("v1.58 manifest state mismatch")
    phase=m.get("current_phase",{})
    if phase.get("id")!="XEN-PHASE-005" or phase.get("completion_status")!="R2_DRAFT_COMPLETE_PENDING_IN_DEPTH_OWNER_REVIEW":return fail("R2 phase mismatch")
    q=m.get("controlled_comparison",{})
    if q.get("revision_id")!="XEN-CONTROLLED-COMPARISON-001-R2" or q.get("status")!="DRAFTED_PENDING_IN_DEPTH_OWNER_REVIEW":return fail("R2 manifest identity mismatch")
    if q.get("record")!=str(R2.relative_to(R)) or q.get("predecessor_record")!=str(R1.relative_to(R)):return fail("R2 manifest path mismatch")
    expected={"GOVERNING_ARCHITECTURE":1,"GOVERNING_EXAMINATION":10,"CYRUS_SIDE_ELABORATION":2,"AGREEMENT":9,"QUALIFIED_AGREEMENT":5,"PRIMARY_SILENCE":3,"UNRESOLVED_RELATION":1}
    if q.get("classification_counts")!=expected:return fail("R2 manifest classification mismatch")
    if q.get("review_application_counts")!={"RETAINED":11,"REVISED_IN_PLACE":11,"RECLASSIFIED":9}:return fail("R2 review application mismatch")
    if q.get("comparison_entry_count")!=31 or q.get("sequential_movement_count")!=8 or q.get("deep_examination_count")!=7:return fail("R2 manifest counts mismatch")
    for k in ["source_independence_preserved","strauss_guiding_architecture","sequential_argument_spine_present","proxenos_mediation_restored","economic_art_integrated","book_four_justice_transition_integrated","justice_examination_expanded","ending_examination_expanded","r1_preserved_not_adopted","historical_predecessors_preserved"]:
        if q.get(k) is not True:return fail("R2 safeguard missing: "+k)
    if m.get("next_required_action",{}).get("id")!="XEN-CONTROLLED-COMPARISON-R2-IN_DEPTH-OWNER-REVIEW-001":return fail("R2 next action mismatch")
    if r2.get("revision_id")!="XEN-CONTROLLED-COMPARISON-001-R2" or r2.get("status")!="DRAFTED_PENDING_IN_DEPTH_OWNER_REVIEW":return fail("R2 record identity mismatch")
    ga=r2.get("governing_architecture",{})
    if ga.get("opposition")!="SOCRATES_VS_CYRUS" or ga.get("mediating_figure")!="XENOPHON":return fail("R2 architecture mismatch")
    if r2.get("classification_counts")!=expected or r2.get("sequential_movements")!=8 or r2.get("comparison_entries")!=31 or r2.get("deep_examinations")!=7:return fail("R2 record counts mismatch")
    moves=sp.get("movements",[])
    if len(moves)!=8 or [x.get("id") for x in moves] != [f"R2-MOV-{i:03d}" for i in range(1,9)]:return fail("R2 movement spine mismatch")
    titles=["Misleading surfaces","Menon, Proxenos","Delphi, political self-direction","Xenophon's ascent","Book Four as compositional center","Founding, trial, acquittal","Monarchy, Spartan hegemony","Seuthes, apology, reconciliation"]
    if any(titles[i] not in moves[i].get("title","") for i in range(8)):return fail("R2 movement order mismatch")
    if ei.get("entry_count")!=31 or len(ei.get("parts",[]))!=2:return fail("R2 entry index mismatch")
    entries=e1.get("entries",[])+e2.get("entries",[])
    if len(e1.get("entries",[]))!=16 or len(e2.get("entries",[]))!=15 or len(entries)!=31:return fail("R2 entry count mismatch")
    if [x.get("entry_id") for x in entries] != [f"CMP-{i:03d}" for i in range(1,32)]:return fail("R2 entry ID order mismatch")
    if Counter(x.get("r2_classification") for x in entries)!=Counter(expected):return fail("R2 entry classification mismatch")
    if Counter(x.get("review_application") for x in entries)!=Counter({"RETAINED":11,"REVISED_IN_PLACE":11,"RECLASSIFIED":9}):return fail("R2 entry review counts mismatch")
    byid={x.get("entry_id"):x for x in entries}
    required_reclass={"CMP-001":"GOVERNING_EXAMINATION","CMP-006":"GOVERNING_ARCHITECTURE","CMP-007":"GOVERNING_EXAMINATION","CMP-008":"GOVERNING_EXAMINATION","CMP-016":"GOVERNING_EXAMINATION","CMP-018":"GOVERNING_EXAMINATION","CMP-025":"GOVERNING_EXAMINATION","CMP-026":"GOVERNING_EXAMINATION","CMP-028":"GOVERNING_EXAMINATION"}
    if any(byid[k].get("r2_classification")!=v or byid[k].get("review_application")!="RECLASSIFIED" for k,v in required_reclass.items()):return fail("R2 required reclassification mismatch")
    if de.get("examination_count")!=7 or len(de.get("examinations",[]))!=7:return fail("R2 deep examination mismatch")
    text=" ".join(json.dumps(x,ensure_ascii=False) for x in [r2,sp,ei,e1,e2,de]).casefold()
    for phrase in ["proxenos as indispensable mediator","economic art","deus sive casus","manly and socratic justice","closest approximation","practical supremacy","thibron","socrates' final question","independently disclosed","not two equal closures"]:
        if phrase not in text:return fail("R2 substantive safeguard missing: "+phrase)
    rs=a.get("repository_state",{})
    if rs.get("controlled_comparison_r2_drafted") is not True or rs.get("controlled_comparison_r2_draft_complete") is not True:return fail("R2 audit production mismatch")
    if rs.get("controlled_comparison_r2_owner_reviewed") is not False or rs.get("controlled_comparison_owner_adopted") is not False:return fail("R2 audit review gate mismatch")
    if a.get("resolved_items",[])[-1].get("id")!="RES-017" or a.get("documented_gaps",[])[1].get("id")!="GAP-012":return fail("R2 audit transition mismatch")
    if m.get("artificial_intelligence_self_certification_prohibited") is not True or rs.get("minister_adapter_derived") is not False or rs.get("sanctum_registration_present") is not False:return fail("R2 governance gate mismatch")
    hist=H.read_text(encoding="utf-8")
    for phrase in ["R2 is additive","eight movements","All nine required reclassifications","Proxenos has been restored","R2 is `DRAFTED_PENDING_IN_DEPTH_OWNER_REVIEW`"]:
        if phrase not in hist:return fail("R2 history safeguard missing: "+phrase)
    print("Xenophon repository validation passed");return 0
if __name__=="__main__":sys.exit(main())
