from pathlib import Path
import json, sys, yaml, tempfile, shutil, subprocess
R=Path(__file__).resolve().parents[1]
P=R/'scripts/validate_repository_v1_63.py'
M=R/'manifest.yaml';A=R/'audits/founding-state.yaml'
SYN=R/'studies/comparisons/anabasis-primary-strauss/syntheses/XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001.yaml'
READ=R/'studies/comparisons/anabasis-primary-strauss/syntheses/XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001.md'
REV=R/'studies/comparisons/anabasis-primary-strauss/reviews/XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-IN-DEPTH-REVIEW-001.yaml'
OWN=R/'governance/owner-reviews/2026-08-01-strauss-guided-controlled-synthesis-in-depth-review.yaml'
H=R/'history/2026-08-01-strauss-guided-controlled-synthesis-in-depth-review.md'
R1Y=R/'studies/comparisons/anabasis-primary-strauss/syntheses/XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001-R1.yaml'
R1M=R/'studies/comparisons/anabasis-primary-strauss/syntheses/XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001-R1.md'
def load(p):
    with p.open(encoding='utf-8') as f:return yaml.safe_load(f)
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
def fail(x):print(x);return 1
def predecessor():
    if not P.exists():return fail('Frozen v1.63 validator missing')
    with tempfile.TemporaryDirectory() as d:
        t=Path(d)/'r';shutil.copytree(R,t,ignore=shutil.ignore_patterns('.git','__pycache__'))
        m=load(t/'manifest.yaml');m['version']='1.63.0';m['state']='CONTROLLED_SYNTHESIS_DRAFT_COMPLETE_PENDING_IN_DEPTH_OWNER_REVIEW'
        m['owner_reviews']=[x for x in m.get('owner_reviews',[]) if x!='governance/owner-reviews/2026-08-01-strauss-guided-controlled-synthesis-in-depth-review.yaml']
        m['current_phase']={'id':'XEN-PHASE-007','name':'Strauss-guided controlled synthesis from the owner-adopted R3 comparison','completion_status':'SYNTHESIS_DRAFT_COMPLETE_PENDING_IN_DEPTH_OWNER_REVIEW'}
        m['primary_study']['cumulative_reconstruction']['secondary_comparison_status']='CONTROLLED_SYNTHESIS_DRAFT_COMPLETE_PENDING_IN_DEPTH_OWNER_REVIEW'
        m['next_required_action']={'id':'XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-IN_DEPTH-OWNER-REVIEW-001','description':'Conduct an in-depth owner review of the controlled synthesis for source direction, sequential fidelity, preservation of concealment, treatment of Xenophon as revealing author, all nineteen unresolved questions, and the prohibition on declaring a final teaching.'}
        cs=m['controlled_synthesis'];cs['status']='DRAFTED_PENDING_IN_DEPTH_OWNER_REVIEW';cs['owner_review_status']='PENDING_IN_DEPTH_REVIEW'
        for k in ['owner_reviewed','owner_adopted','detailed_review_record','owner_review_record','review_disposition','review_disposition_counts','source_exact_text_review_complete','cross_work_scope_revision_required','interrogative_legitimacy_revision_required','xenophon_presents_problem_of_justice_required','required_next_revision','original_draft_preserved']:
            cs.pop(k,None)
        dump(t/'manifest.yaml',m)
        a=load(t/'audits/founding-state.yaml');a['as_of']='2026-07-31';rs=a['repository_state']
        rs['controlled_synthesis_owner_reviewed']=False;rs['controlled_synthesis_owner_adopted']=False;rs['controlled_synthesis_status']='DRAFTED_PENDING_IN_DEPTH_OWNER_REVIEW'
        rs['controlled_comparison_required_next_action']='XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-IN_DEPTH-OWNER-REVIEW-001'
        for k in ['controlled_synthesis_review_disposition','controlled_synthesis_detailed_review_record','controlled_synthesis_owner_review_record','controlled_synthesis_exact_source_review_complete','controlled_synthesis_cross_work_scope_revision_required','controlled_synthesis_interrogative_legitimacy_revision_required','controlled_synthesis_xenophon_presents_problem_of_justice_required','controlled_synthesis_r1_required','controlled_synthesis_required_next_revision','controlled_synthesis_original_draft_preserved']:
            rs.pop(k,None)
        a['resolved_items']=[x for x in a.get('resolved_items',[]) if x.get('id')!='RES-022']
        a['documented_gaps'][1]={'id':'GAP-016','description':'The controlled synthesis is draft-complete but has not undergone in-depth owner review of its source direction, sequential fidelity, authorial-revelation control, concealment, evidence layers, and preservation of all nineteen unresolved questions.','blocks':['owner-adopted synthesis','minister derivation']}
        a['next_required_action']='Conduct XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-IN_DEPTH-OWNER-REVIEW-001 before adoption, minister adapter construction, or Sanctum registration.'
        dump(t/'audits/founding-state.yaml',a)
        z=subprocess.run([sys.executable,str(t/'scripts/validate_repository_v1_63.py')],cwd=t,text=True,capture_output=True)
        if z.returncode:return fail('v1.63 predecessor failed: '+(z.stdout+z.stderr).strip())
    return 0
def main():
    if predecessor():return 1
    for p in [M,A,SYN,READ,REV,OWN,H,P]:
        if not p.exists():return fail('Synthesis review file missing: '+str(p))
    if R1Y.exists() or R1M.exists():return fail('R1 synthesis exists before authorized production stage')
    m=load(M);a=load(A);syn=load(SYN);rev=load(REV);own=load(OWN)
    if m.get('version')!='1.64.0' or m.get('state')!='CONTROLLED_SYNTHESIS_IN_DEPTH_REVIEWED_RETURNED_FOR_TARGETED_REVISION':return fail('v1.64 manifest state mismatch')
    phase=m.get('current_phase',{})
    if phase.get('id')!='XEN-PHASE-007' or phase.get('completion_status')!='REVIEW_COMPLETE_TARGETED_R1_REQUIRED':return fail('Synthesis review phase mismatch')
    if m.get('next_required_action',{}).get('id')!='XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001-R1':return fail('R1 next action mismatch')
    cs=m.get('controlled_synthesis',{})
    if cs.get('status')!='IN_DEPTH_REVIEW_COMPLETE_RETURNED_FOR_TARGETED_REVISION' or cs.get('owner_review_status')!='RETURNED_FOR_TARGETED_REVISION':return fail('Synthesis review disposition mismatch')
    if cs.get('owner_reviewed') is not True or cs.get('owner_adopted') is not False:return fail('Synthesis adoption gate mismatch')
    if cs.get('review_disposition_counts')!={'PASS':8,'PASS_WITH_LIMIT':1,'BLOCKING_REVISION':3}:return fail('Review disposition counts mismatch')
    for k in ['source_exact_text_review_complete','cross_work_scope_revision_required','interrogative_legitimacy_revision_required','xenophon_presents_problem_of_justice_required','original_draft_preserved']:
        if cs.get(k) is not True:return fail('Synthesis review safeguard missing: '+k)
    if cs.get('required_next_revision')!='XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001-R1':return fail('Required R1 identity mismatch')
    if syn.get('status')!='DRAFTED_PENDING_IN_DEPTH_OWNER_REVIEW':return fail('Immutable synthesis draft changed')
    if rev.get('review_id')!='XEN-SYNTHESIS-REVIEW-001' or rev.get('status')!='IN_DEPTH_REVIEW_COMPLETE_RETURNED_FOR_TARGETED_REVISION':return fail('Detailed review identity mismatch')
    if rev.get('overall_ruling',{}).get('disposition')!='RETURN_FOR_TARGETED_R1_REVISION' or rev.get('overall_ruling',{}).get('adoption_status')!='NOT_ADOPTED':return fail('Detailed review ruling mismatch')
    if rev.get('disposition_counts')!={'PASS':8,'PASS_WITH_LIMIT':1,'BLOCKING_REVISION':3}:return fail('Detailed review counts mismatch')
    if len(rev.get('findings',[]))!=12 or len(rev.get('required_r1_corrections',[]))!=3:return fail('Detailed review coverage mismatch')
    if own.get('status')!='OWNER_REVIEWED_RETURNED_FOR_TARGETED_REVISION' or own.get('owner_ruling',{}).get('adoption_status')!='NOT_ADOPTED':return fail('Owner review ruling mismatch')
    if own.get('next_required_action',{}).get('id')!='XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001-R1':return fail('Owner review next action mismatch')
    text=' '.join(json.dumps(x,ensure_ascii=False) for x in [rev,own]).casefold()
    for phrase in ['education of cyrus','cross-work','iron alloy','prescription','interrogative','presents to the reader the problem of justice','older cyrus is material','not_adopted','nineteen unresolved questions']:
        if phrase not in text:return fail('Synthesis review substance missing: '+phrase)
    rs=a.get('repository_state',{})
    if rs.get('controlled_synthesis_owner_reviewed') is not True or rs.get('controlled_synthesis_owner_adopted') is not False:return fail('Audit review gate mismatch')
    for k in ['controlled_synthesis_exact_source_review_complete','controlled_synthesis_cross_work_scope_revision_required','controlled_synthesis_interrogative_legitimacy_revision_required','controlled_synthesis_xenophon_presents_problem_of_justice_required','controlled_synthesis_r1_required','controlled_synthesis_original_draft_preserved']:
        if rs.get(k) is not True:return fail('Audit synthesis review safeguard missing: '+k)
    if rs.get('controlled_synthesis_required_next_revision')!='XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001-R1':return fail('Audit R1 identity mismatch')
    if a.get('resolved_items',[])[-1].get('id')!='RES-022' or a.get('documented_gaps',[])[1].get('id')!='GAP-017':return fail('Audit review transition mismatch')
    if m.get('artificial_intelligence_self_certification_prohibited') is not True or rs.get('minister_adapter_derived') is not False or rs.get('sanctum_registration_present') is not False:return fail('Governance gate mismatch')
    hist=H.read_text(encoding='utf-8').casefold()
    for phrase in ["older cyrus is xenophon's presentation",'education of cyrus','iron alloy','xenophon, by standing between the older cyrus and socrates, presents to the reader the problem of justice','not adopted','immutable draft']:
        if phrase not in hist:return fail('Review history safeguard missing: '+phrase)
    print('Xenophon repository validation passed');return 0
if __name__=='__main__':sys.exit(main())
