from pathlib import Path
import json, sys, yaml, tempfile, shutil, subprocess
R=Path(__file__).resolve().parents[1]
P=R/'scripts/validate_repository_v1_60.py'
M=R/'manifest.yaml'; A=R/'audits/founding-state.yaml'
REV=R/'studies/comparisons/anabasis-primary-strauss/reviews/XEN-CONTROLLED-COMPARISON-R3-IN-DEPTH-REVIEW-001.yaml'
OWN=R/'governance/owner-reviews/2026-07-31-controlled-comparison-r3-in-depth-review.yaml'
H=R/'history/2026-07-31-controlled-comparison-r3-owner-adoption.md'
R3=R/'studies/comparisons/anabasis-primary-strauss/XEN-CONTROLLED-COMPARISON-001-R3.yaml'
def load(p):
    with p.open(encoding='utf-8') as f:return yaml.safe_load(f)
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
def fail(x):print(x);return 1
def predecessor():
    if not P.exists():return fail('Frozen v1.60 validator missing')
    with tempfile.TemporaryDirectory() as d:
        t=Path(d)/'r';shutil.copytree(R,t,ignore=shutil.ignore_patterns('.git','__pycache__'))
        for p in [REV,OWN,H]:
            q=t/p.relative_to(R)
            if q.exists():q.unlink()
        m=load(t/'manifest.yaml');q=m['controlled_comparison']
        m['version']='1.60.0';m['state']='CONTROLLED_COMPARISON_R3_DRAFT_COMPLETE_PENDING_IN_DEPTH_OWNER_REVIEW'
        m['owner_reviews']=[x for x in m.get('owner_reviews',[]) if x!='governance/owner-reviews/2026-07-31-controlled-comparison-r3-in-depth-review.yaml']
        m['current_phase']={'id':'XEN-PHASE-006','name':'Targeted R3 correction of the sequential Strauss-guided Anabasis comparison','completion_status':'R3_DRAFT_COMPLETE_PENDING_IN_DEPTH_OWNER_REVIEW'}
        m['primary_study']['cumulative_reconstruction']['secondary_comparison_status']='R3_DRAFT_COMPLETE_PENDING_IN_DEPTH_OWNER_REVIEW'
        m['next_required_action']={'id':'XEN-CONTROLLED-COMPARISON-R3-IN_DEPTH-OWNER-REVIEW-001','description':'Conduct an in-depth owner review of R3 before adoption.'}
        q['status']='DRAFTED_PENDING_IN_DEPTH_OWNER_REVIEW';q['owner_review_status']='PENDING_IN_DEPTH_REVIEW'
        for k in ['r3_in_depth_review_record','r3_owner_review_record','unresolved_question_count','review_disposition','byzantium_mixed_motive_preserved','all_19_unresolved_questions_preserved','r3_owner_reviewed','r3_owner_adopted']:
            q.pop(k,None)
        dump(t/'manifest.yaml',m)
        a=load(t/'audits/founding-state.yaml');rs=a['repository_state']
        rs['controlled_comparison_owner_reviewed']=False;rs['controlled_comparison_owner_adopted']=False
        rs['controlled_comparison_review_disposition']='R3_DRAFT_PENDING_IN_DEPTH_OWNER_REVIEW'
        rs['controlled_comparison_owner_review_record']='governance/owner-reviews/2026-07-31-controlled-comparison-r2-in-depth-review.yaml'
        rs['controlled_comparison_detailed_review_record']='studies/comparisons/anabasis-primary-strauss/reviews/XEN-CONTROLLED-COMPARISON-R2-IN-DEPTH-REVIEW-001.yaml'
        rs['controlled_comparison_r3_owner_reviewed']=False;rs.pop('controlled_comparison_r3_owner_adopted',None)
        rs.pop('controlled_comparison_r3_byzantium_mixed_motive_preserved',None);rs.pop('controlled_comparison_r3_all_19_unresolved_questions_preserved',None)
        rs['controlled_comparison_required_next_action']='XEN-CONTROLLED-COMPARISON-R3-IN_DEPTH-OWNER-REVIEW-001'
        a['resolved_items']=[x for x in a.get('resolved_items',[]) if x.get('id')!='RES-020']
        a['documented_gaps'][1]={'id':'GAP-014','description':'R3 is draft-complete but has not undergone in-depth owner review of the controlled intended Cyrus ambiguity, Byzantium deed examination, and exact final coda.','blocks':['owner-adopted comparative reconstruction','controlled interpretive synthesis','minister derivation']}
        a['next_required_action']='Conduct XEN-CONTROLLED-COMPARISON-R3-IN_DEPTH-OWNER-REVIEW-001 before adoption, synthesis, minister adapter construction, or Sanctum registration.'
        dump(t/'audits/founding-state.yaml',a)
        z=subprocess.run([sys.executable,str(t/'scripts/validate_repository_v1_60.py')],cwd=t,text=True,capture_output=True)
        if z.returncode:return fail('v1.60 predecessor failed: '+(z.stdout+z.stderr).strip())
    return 0
def main():
    if predecessor():return 1
    for p in [M,A,REV,OWN,H,R3,P]:
        if not p.exists():return fail('Adoption file missing: '+str(p))
    m=load(M);a=load(A);rev=load(REV);own=load(OWN);r3=load(R3)
    if m.get('version')!='1.61.0' or m.get('state')!='CONTROLLED_COMPARISON_R3_OWNER_ADOPTED':return fail('v1.61 state mismatch')
    q=m.get('controlled_comparison',{})
    if q.get('status')!='OWNER_ADOPTED_CONTROLLED_COMPARISON' or q.get('owner_review_status')!='OWNER_ADOPTED':return fail('R3 adoption gate mismatch')
    if q.get('r3_owner_reviewed') is not True or q.get('r3_owner_adopted') is not True:return fail('R3 adoption flags missing')
    if q.get('r3_in_depth_review_record')!=str(REV.relative_to(R)) or q.get('r3_owner_review_record')!=str(OWN.relative_to(R)):return fail('R3 review path mismatch')
    for k in ['controlled_intended_cyrus_ambiguity','distinction_without_compartmentalization','justice_ambiguity_governs_cyrus_ambiguity','byzantium_mixed_motive_preserved','post_question_coda_exact_order_present','thibron_primary_endpoint_preserved','all_19_unresolved_questions_preserved']:
        if q.get(k) is not True:return fail('Adoption safeguard missing: '+k)
    if q.get('unresolved_question_count')!=19:return fail('Unresolved question count mismatch')
    if m.get('next_required_action',{}).get('id')!='XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001':return fail('Next action mismatch')
    if r3.get('status')!='DRAFTED_PENDING_IN_DEPTH_OWNER_REVIEW':return fail('Immutable R3 production record changed')
    if rev.get('status')!='IN_DEPTH_REVIEW_COMPLETE_RECOMMEND_OWNER_ADOPTION' or rev.get('overall_ruling',{}).get('disposition')!='PASS_RECOMMEND_OWNER_ADOPTION':return fail('Detailed review mismatch')
    if len(rev.get('findings',[]))!=9:return fail('Review finding count mismatch')
    if own.get('status')!='OWNER_ADOPTED_CONTROLLED_COMPARISON_R3' or own.get('owner_ruling',{}).get('adoption_status')!='OWNER_ADOPTED':return fail('Owner ruling mismatch')
    if len(own.get('adopted_controls',[]))!=7:return fail('Adopted controls mismatch')
    rs=a.get('repository_state',{})
    if rs.get('controlled_comparison_owner_adopted') is not True or rs.get('controlled_comparison_r3_owner_adopted') is not True:return fail('Audit adoption mismatch')
    if rs.get('controlled_comparison_required_next_action')!='XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001':return fail('Audit next action mismatch')
    if a.get('resolved_items',[])[-1].get('id')!='RES-020' or a.get('documented_gaps',[])[1].get('id')!='GAP-015':return fail('Audit transition mismatch')
    text=' '.join(json.dumps(x,ensure_ascii=False) for x in [rev,own]).casefold()
    for phrase in ['intended ambiguity','justice','byzantium','mixed motive','question, booty, gods, and oaths','thibron','nineteen unresolved questions','no final teaching']:
        if phrase not in text:return fail('Adoption substance missing: '+phrase)
    if m.get('artificial_intelligence_self_certification_prohibited') is not True or rs.get('minister_adapter_derived') is not False or rs.get('sanctum_registration_present') is not False:return fail('Governance gate mismatch')
    print('Xenophon repository validation passed');return 0
if __name__=='__main__':sys.exit(main())
