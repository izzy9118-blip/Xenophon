from pathlib import Path
import json, sys, yaml, tempfile, shutil, subprocess
R=Path(__file__).resolve().parents[1]
P=R/'scripts/validate_repository_v1_65.py'
M=R/'manifest.yaml';A=R/'audits/founding-state.yaml'
R1=R/'studies/comparisons/anabasis-primary-strauss/syntheses/XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001-R1.yaml'
R1M=R/'studies/comparisons/anabasis-primary-strauss/syntheses/XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001-R1.md'
REV=R/'studies/comparisons/anabasis-primary-strauss/reviews/XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-R1-IN-DEPTH-REVIEW-001.yaml'
OWN=R/'governance/owner-reviews/2026-08-01-strauss-guided-controlled-synthesis-r1-in-depth-review.yaml'
DIR=R/'governance/owner-directives/2026-08-01-defer-greek-language-certification.yaml'
H=R/'history/2026-08-01-strauss-guided-controlled-synthesis-r1-review-adoption-and-greek-deferral.md'
OLDREV=R/'studies/comparisons/anabasis-primary-strauss/reviews/XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-IN-DEPTH-REVIEW-001.yaml'
OLDOWN=R/'governance/owner-reviews/2026-08-01-strauss-guided-controlled-synthesis-in-depth-review.yaml'
def load(p):
    with p.open(encoding='utf-8') as f:return yaml.safe_load(f)
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
def fail(x):print(x);return 1
def predecessor():
    if not P.exists():return fail('Frozen v1.65 validator missing')
    with tempfile.TemporaryDirectory() as d:
        t=Path(d)/'r';shutil.copytree(R,t,ignore=shutil.ignore_patterns('.git','__pycache__'))
        for p in [REV,OWN,DIR,H]:
            q=t/p.relative_to(R)
            if q.exists():q.unlink()
        m=load(t/'manifest.yaml')
        m['version']='1.65.0';m['state']='CONTROLLED_SYNTHESIS_R1_DRAFT_COMPLETE_PENDING_IN_DEPTH_OWNER_REVIEW'
        m['owner_reviews']=[x for x in m.get('owner_reviews',[]) if x!='governance/owner-reviews/2026-08-01-strauss-guided-controlled-synthesis-r1-in-depth-review.yaml']
        m.pop('owner_directives',None)
        sp=m['source_policy'];sp.pop('current_textual_jurisdiction',None);sp.pop('greek_language_review',None)
        m['current_phase']={'id':'XEN-PHASE-008','name':'Targeted R1 correction of the Strauss-guided controlled synthesis','completion_status':'R1_DRAFT_COMPLETE_PENDING_IN_DEPTH_OWNER_REVIEW'}
        m['primary_study']['cumulative_reconstruction']['secondary_comparison_status']='CONTROLLED_SYNTHESIS_R1_DRAFT_COMPLETE_PENDING_IN_DEPTH_OWNER_REVIEW'
        m['next_required_action']={'id':'XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-R1-IN_DEPTH-OWNER-REVIEW-001','description':'Conduct an in-depth owner review of R1 for cross-work jurisdiction, interrogative legitimacy, Xenophon as presenter of the problem of justice, preservation of the eight movements, and all nineteen unresolved questions.'}
        cs=m['controlled_synthesis'];cs['active_revision_status']='DRAFTED_PENDING_IN_DEPTH_OWNER_REVIEW';cs['r1_owner_review_status']='PENDING_IN_DEPTH_REVIEW';cs['r1_owner_reviewed']=False;cs['r1_owner_adopted']=False
        for k in ['r1_detailed_review_record','r1_owner_review_record','r1_review_disposition','r1_review_disposition_counts','greek_certification_status','greek_deferral_directive','minister_adapter_authorized']:
            cs.pop(k,None)
        dump(t/'manifest.yaml',m)
        a=load(t/'audits/founding-state.yaml');rs=a['repository_state']
        rs.pop('minister_adapter_authorized',None)
        rs['controlled_comparison_required_next_action']='XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-R1-IN_DEPTH-OWNER-REVIEW-001'
        rs['controlled_synthesis_r1_status']='DRAFTED_PENDING_IN_DEPTH_OWNER_REVIEW';rs['controlled_synthesis_r1_owner_reviewed']=False;rs['controlled_synthesis_r1_owner_adopted']=False
        for k in ['controlled_synthesis_r1_detailed_review_record','controlled_synthesis_r1_owner_review_record','controlled_synthesis_r1_review_disposition','controlled_synthesis_r1_review_pass_count','controlled_synthesis_r1_review_pass_with_limit_count','controlled_synthesis_r1_review_blocking_count','greek_language_certification_status','greek_language_certification_current_blocker','greek_language_future_phase','greek_language_deferral_directive','greek_dependent_claims_prohibited']:
            rs.pop(k,None)
        a['resolved_items']=[x for x in a.get('resolved_items',[]) if x.get('id') not in {'RES-024','RES-025'}]
        a['documented_gaps']=[{'id':'GAP-004','description':'No reviewed original-language Greek witness or critical edition is registered.','blocks':['Greek philological conclusions','translation adjudication','final textual certification']},{'id':'GAP-018','description':'The targeted R1 synthesis is draft-complete but has not undergone in-depth owner review of its cross-work jurisdiction, interrogative legitimacy structure, Xenophon-as-presenter direction, and preservation of all nineteen unresolved questions.','blocks':['owner-adopted synthesis','minister derivation']},{'id':'GAP-003','description':'No owner-approved Xenophon adapter exists.','blocks':['Assembly dispatch']}]
        a['next_required_action']='Conduct XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-R1-IN_DEPTH-OWNER-REVIEW-001 before adoption, minister adapter construction, or Sanctum registration.'
        dump(t/'audits/founding-state.yaml',a)
        z=subprocess.run([sys.executable,str(t/'scripts/validate_repository_v1_65.py')],cwd=t,text=True,capture_output=True)
        if z.returncode:return fail('v1.65 predecessor failed: '+(z.stdout+z.stderr).strip())
    return 0
def main():
    if predecessor():return 1
    for p in [M,A,R1,R1M,REV,OWN,DIR,H,OLDREV,OLDOWN,P]:
        if not p.exists():return fail('R1 adoption file missing: '+str(p))
    m=load(M);a=load(A);r1=load(R1);rev=load(REV);own=load(OWN);direc=load(DIR);oldrev=load(OLDREV);oldown=load(OLDOWN)
    if m.get('version')!='1.66.0' or m.get('state')!='CONTROLLED_SYNTHESIS_R1_OWNER_ADOPTED_GREEK_REVIEW_DEFERRED':return fail('v1.66 manifest state mismatch')
    phase=m.get('current_phase',{})
    if phase.get('id')!='XEN-PHASE-009' or phase.get('completion_status')!='R1_OWNER_ADOPTED_GREEK_REVIEW_DEFERRED':return fail('R1 adoption phase mismatch')
    if m.get('next_required_action',{}).get('id')!='XEN-MINISTER-ADAPTER-001':return fail('Minister adapter next action mismatch')
    if 'governance/owner-reviews/2026-08-01-strauss-guided-controlled-synthesis-r1-in-depth-review.yaml' not in m.get('owner_reviews',[]):return fail('R1 owner review missing from manifest')
    if m.get('owner_directives')!=['governance/owner-directives/2026-08-01-defer-greek-language-certification.yaml']:return fail('Greek deferral directive mismatch')
    sp=m.get('source_policy',{});gr=sp.get('greek_language_review',{})
    if gr.get('status')!='DEFERRED_BY_OWNER' or gr.get('required_for_current_production') is not False or gr.get('future_mode')!='OWNER_OPENED_FUTURE_PHASE':return fail('Greek source policy mismatch')
    cs=m.get('controlled_synthesis',{})
    if cs.get('active_revision')!='XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001-R1' or cs.get('active_revision_status')!='OWNER_ADOPTED':return fail('Active adopted R1 mismatch')
    if cs.get('r1_owner_review_status')!='OWNER_ADOPTED' or cs.get('r1_owner_reviewed') is not True or cs.get('r1_owner_adopted') is not True:return fail('R1 adoption gate mismatch')
    if cs.get('r1_review_disposition')!='PASS_ADOPTED_WITH_ENGLISH_WITNESS_JURISDICTION' or cs.get('r1_review_disposition_counts')!={'PASS':12,'PASS_WITH_LIMIT':1,'BLOCKING_REVISION':0}:return fail('R1 review disposition mismatch')
    for k in ['r1_predecessor_preserved','r1_targeted_revision_complete','r1_cross_work_scope_corrected','r1_anabasis_primary_center','r1_older_cyrus_education_of_cyrus_scope','r1_interrogative_legitimacy_preserved','r1_xenophon_presents_problem_of_justice','r1_eight_movements_preserved','r1_all_19_unresolved_questions_preserved','minister_adapter_authorized']:
        if cs.get(k) is not True:return fail('Adopted R1 safeguard missing: '+k)
    if cs.get('greek_certification_status')!='DEFERRED_BY_OWNER_NOT_CURRENT_BLOCKER':return fail('Manifest Greek status mismatch')
    if r1.get('status')!='DRAFTED_PENDING_IN_DEPTH_OWNER_REVIEW':return fail('Immutable R1 production record changed')
    if len(r1.get('sequential_synthesis',[]))!=8 or len(r1.get('unresolved_questions',[]))!=19:return fail('R1 architecture changed')
    if rev.get('status')!='IN_DEPTH_REVIEW_COMPLETE_RECOMMEND_OWNER_ADOPTION' or rev.get('overall_ruling',{}).get('disposition')!='PASS_RECOMMEND_OWNER_ADOPTION':return fail('R1 detailed review mismatch')
    if rev.get('disposition_counts')!={'PASS':12,'PASS_WITH_LIMIT':1,'BLOCKING_REVISION':0} or len(rev.get('findings',[]))!=13:return fail('R1 review coverage mismatch')
    if own.get('status')!='OWNER_ADOPTED_CONTROLLED_SYNTHESIS_R1' or own.get('owner_ruling',{}).get('adoption_status')!='ADOPTED':return fail('R1 owner adoption mismatch')
    if own.get('next_required_action',{}).get('id')!='XEN-MINISTER-ADAPTER-001':return fail('Owner review next action mismatch')
    if direc.get('directive_id')!='XEN-OWNER-DIRECTIVE-001' or direc.get('status')!='ACTIVE_OWNER_DIRECTIVE':return fail('Greek directive identity mismatch')
    pe=direc.get('present_effect',{})
    for k in ['greek_certification_required_for_current_phase','greek_certification_required_for_r1_synthesis_adoption','greek_certification_required_for_minister_adapter_construction','greek_certification_required_for_sanctum_registration']:
        if pe.get(k) is not False:return fail('Greek non-blocking control missing: '+k)
    if pe.get('current_production_may_continue') is not True:return fail('Current production continuation not authorized')
    if direc.get('future_reactivation',{}).get('mode')!='OWNER_OPENED_FUTURE_PHASE':return fail('Future Greek phase control mismatch')
    text=' '.join(json.dumps(x,ensure_ascii=False) for x in [r1,rev,own,direc]).casefold()
    for phrase in ['education of cyrus','iron alloy','questions rather than settled propositions','xenophon presents to the reader the problem of justice','all nineteen unresolved questions','deferred by owner','greek-dependent claims','not a completed model']:
        if phrase not in text:return fail('R1 adoption substance missing: '+phrase)
    if oldrev.get('overall_ruling',{}).get('adoption_status')!='NOT_ADOPTED' or oldown.get('owner_ruling',{}).get('adoption_status')!='NOT_ADOPTED':return fail('Predecessor adverse review changed')
    rs=a.get('repository_state',{})
    if rs.get('controlled_synthesis_r1_owner_reviewed') is not True or rs.get('controlled_synthesis_r1_owner_adopted') is not True:return fail('Audit R1 adoption mismatch')
    if rs.get('controlled_synthesis_r1_review_blocking_count')!=0 or rs.get('controlled_synthesis_r1_review_pass_count')!=12:return fail('Audit review counts mismatch')
    if rs.get('greek_language_certification_status')!='DEFERRED_BY_OWNER' or rs.get('greek_language_certification_current_blocker') is not False or rs.get('greek_dependent_claims_prohibited') is not True:return fail('Audit Greek deferral mismatch')
    if rs.get('minister_adapter_authorized') is not True or rs.get('minister_adapter_derived') is not False:return fail('Minister adapter gate mismatch')
    if rs.get('controlled_comparison_required_next_action')!='XEN-MINISTER-ADAPTER-001':return fail('Audit next action mismatch')
    ids=[x.get('id') for x in a.get('resolved_items',[])]
    if ids[-2:]!=['RES-024','RES-025']:return fail('Audit adoption resolutions missing')
    gaps=a.get('documented_gaps',[])
    if [x.get('id') for x in gaps]!=['GAP-004','GAP-003']:return fail('Audit gap transition mismatch')
    if gaps[0].get('status')!='DEFERRED_BY_OWNER' or gaps[0].get('current_blocking_effect') is not False:return fail('Greek gap classification mismatch')
    if a.get('next_required_action')!='Construct XEN-MINISTER-ADAPTER-001 from the owner-adopted R1 synthesis before Sanctum registration or Assembly dispatch.':return fail('Audit next action text mismatch')
    hist=H.read_text(encoding='utf-8').casefold()
    for phrase in ['does not erase the original-language limitation','twelve passes','owner adopted r1','owner_opened_future_phase','next production unit: `xen-minister-adapter-001`']:
        if phrase not in hist:return fail('Adoption history safeguard missing: '+phrase)
    if m.get('artificial_intelligence_self_certification_prohibited') is not True or rs.get('sanctum_registration_present') is not False:return fail('Governance prohibition mismatch')
    print('Xenophon repository validation passed');return 0
if __name__=='__main__':sys.exit(main())
