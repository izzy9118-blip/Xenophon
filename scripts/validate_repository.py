from pathlib import Path
import json, sys, yaml, tempfile, shutil, subprocess
R=Path(__file__).resolve().parents[1]
P=R/'scripts/validate_repository_v1_64.py'
M=R/'manifest.yaml';A=R/'audits/founding-state.yaml'
S0=R/'studies/comparisons/anabasis-primary-strauss/syntheses/XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001.yaml'
S0M=R/'studies/comparisons/anabasis-primary-strauss/syntheses/XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001.md'
R1=R/'studies/comparisons/anabasis-primary-strauss/syntheses/XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001-R1.yaml'
R1M=R/'studies/comparisons/anabasis-primary-strauss/syntheses/XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001-R1.md'
REV=R/'studies/comparisons/anabasis-primary-strauss/reviews/XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-IN-DEPTH-REVIEW-001.yaml'
OWN=R/'governance/owner-reviews/2026-08-01-strauss-guided-controlled-synthesis-in-depth-review.yaml'
H=R/'history/2026-08-01-strauss-guided-controlled-synthesis-r1-draft-completion.md'
def load(p):
    with p.open(encoding='utf-8') as f:return yaml.safe_load(f)
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
def fail(x):print(x);return 1
def predecessor():
    if not P.exists():return fail('Frozen v1.64 validator missing')
    with tempfile.TemporaryDirectory() as d:
        t=Path(d)/'r';shutil.copytree(R,t,ignore=shutil.ignore_patterns('.git','__pycache__'))
        for p in [R1,R1M,H]:
            q=t/p.relative_to(R)
            if q.exists():q.unlink()
        m=load(t/'manifest.yaml')
        m['version']='1.64.0';m['state']='CONTROLLED_SYNTHESIS_IN_DEPTH_REVIEWED_RETURNED_FOR_TARGETED_REVISION'
        m['current_phase']={'id':'XEN-PHASE-007','name':'In-depth owner review of the Strauss-guided controlled synthesis','completion_status':'REVIEW_COMPLETE_TARGETED_R1_REQUIRED'}
        m['primary_study']['cumulative_reconstruction']['secondary_comparison_status']='CONTROLLED_SYNTHESIS_REVIEWED_RETURNED_FOR_TARGETED_R1'
        m['next_required_action']={'id':'XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001-R1','description':"Produce an additive targeted R1 synthesis that distinguishes the Anabasis from Xenophon's cross-work presentation of the older Cyrus, preserves Strauss's interrogative legitimacy structure, and restores Xenophon as the presenter of the problem of justice before another in-depth owner review."}
        cs=m['controlled_synthesis']
        for k in ['active_revision','active_revision_status','r1_structured_record','r1_readable_record','r1_predecessor_preserved','r1_targeted_revision_complete','r1_cross_work_scope_corrected','r1_anabasis_primary_center','r1_older_cyrus_education_of_cyrus_scope','r1_interrogative_legitimacy_preserved','r1_xenophon_presents_problem_of_justice','r1_eight_movements_preserved','r1_all_19_unresolved_questions_preserved','r1_owner_review_status','r1_owner_reviewed','r1_owner_adopted']:
            cs.pop(k,None)
        cs['required_next_revision']='XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001-R1'
        dump(t/'manifest.yaml',m)
        a=load(t/'audits/founding-state.yaml');rs=a['repository_state']
        for k in list(rs):
            if k.startswith('controlled_synthesis_r1_'):rs.pop(k,None)
        rs['controlled_comparison_required_next_action']='XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001-R1'
        a['resolved_items']=[x for x in a.get('resolved_items',[]) if x.get('id')!='RES-023']
        a['documented_gaps'][1]={'id':'GAP-017','description':"The synthesis completed exact-source owner review but was not adopted; additive R1 must distinguish the Anabasis from Xenophon's cross-work presentation of the older Cyrus, preserve Strauss's questions about legitimacy and prescription, and restore Xenophon as presenter of the problem of justice.",'blocks':['owner-adopted synthesis','minister derivation']}
        a['next_required_action']='Produce XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001-R1 before another owner review, minister adapter construction, or Sanctum registration.'
        dump(t/'audits/founding-state.yaml',a)
        z=subprocess.run([sys.executable,str(t/'scripts/validate_repository_v1_64.py')],cwd=t,text=True,capture_output=True)
        if z.returncode:return fail('v1.64 predecessor failed: '+(z.stdout+z.stderr).strip())
    return 0
def main():
    if predecessor():return 1
    for p in [M,A,S0,S0M,R1,R1M,REV,OWN,H,P]:
        if not p.exists():return fail('R1 production file missing: '+str(p))
    m=load(M);a=load(A);s0=load(S0);r1=load(R1);rev=load(REV);own=load(OWN)
    if m.get('version')!='1.65.0' or m.get('state')!='CONTROLLED_SYNTHESIS_R1_DRAFT_COMPLETE_PENDING_IN_DEPTH_OWNER_REVIEW':return fail('v1.65 manifest state mismatch')
    phase=m.get('current_phase',{})
    if phase.get('id')!='XEN-PHASE-008' or phase.get('completion_status')!='R1_DRAFT_COMPLETE_PENDING_IN_DEPTH_OWNER_REVIEW':return fail('R1 phase mismatch')
    if m.get('next_required_action',{}).get('id')!='XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-R1-IN_DEPTH-OWNER-REVIEW-001':return fail('R1 owner review next action mismatch')
    cs=m.get('controlled_synthesis',{})
    if cs.get('active_revision')!='XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001-R1' or cs.get('active_revision_status')!='DRAFTED_PENDING_IN_DEPTH_OWNER_REVIEW':return fail('Active R1 manifest mismatch')
    for k in ['r1_predecessor_preserved','r1_targeted_revision_complete','r1_cross_work_scope_corrected','r1_anabasis_primary_center','r1_older_cyrus_education_of_cyrus_scope','r1_interrogative_legitimacy_preserved','r1_xenophon_presents_problem_of_justice','r1_eight_movements_preserved','r1_all_19_unresolved_questions_preserved']:
        if cs.get(k) is not True:return fail('Manifest R1 safeguard missing: '+k)
    if cs.get('r1_owner_review_status')!='PENDING_IN_DEPTH_REVIEW' or cs.get('r1_owner_reviewed') is not False or cs.get('r1_owner_adopted') is not False:return fail('R1 owner gate mismatch')
    if s0.get('status')!='DRAFTED_PENDING_IN_DEPTH_OWNER_REVIEW':return fail('Immutable predecessor synthesis changed')
    if rev.get('overall_ruling',{}).get('adoption_status')!='NOT_ADOPTED' or own.get('owner_ruling',{}).get('adoption_status')!='NOT_ADOPTED':return fail('Predecessor review state changed')
    if r1.get('synthesis_id')!='XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001-R1' or r1.get('status')!='DRAFTED_PENDING_IN_DEPTH_OWNER_REVIEW':return fail('R1 identity mismatch')
    if r1.get('predecessor_synthesis')!='XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001':return fail('R1 predecessor identity mismatch')
    req=r1.get('revision_scope',{}).get('required_corrections',[])
    if len(req)!=3 or [x.get('id') for x in req]!=['SYN-R1-REQ-001','SYN-R1-REQ-002','SYN-R1-REQ-003']:return fail('R1 correction map mismatch')
    moves=r1.get('sequential_synthesis',[])
    if len(moves)!=8 or [x.get('movement_id') for x in moves] != [f'SYN-MOV-{i:03d}' for i in range(1,9)]:return fail('R1 movement sequence mismatch')
    for x in moves:
        if any(not x.get(k) for k in ['title','primary_showing','strauss_explicit_argument','controlled_synthetic_inference','unresolved_limit']):return fail('R1 evidence layer missing in '+str(x.get('movement_id')))
    if set(r1.get('evidence_layers',{}))!={'PRIMARY_SHOWING','STRAUSS_EXPLICIT_ARGUMENT','CONTROLLED_SYNTHETIC_INFERENCE','UNRESOLVED_QUESTION'}:return fail('R1 evidence layers mismatch')
    figs=r1.get('figural_revelations',{})
    if set(figs)!={'YOUNGER_CYRUS','OLDER_CYRUS','SOCRATES','XENOPHON_NARRATED_SELF'}:return fail('R1 figure set mismatch')
    if figs.get('OLDER_CYRUS',{}).get('work_scope','').startswith('Education of Cyrus') is not True:return fail('Older Cyrus cross-work scope missing')
    qs=r1.get('unresolved_questions',[])
    if len(qs)!=19 or [x.get('id') for x in qs] != [f'R3-UQ-{i:03d}' for i in range(1,20)]:return fail('R1 unresolved question preservation mismatch')
    text=json.dumps(r1,ensure_ascii=False).casefold()
    for phrase in ['anabasis is the primary center','education of cyrus','cross-work comparison','iron alloy','whether prescription is indispensable','questions rather than settled propositions','xenophon presents to the reader the problem of justice','not a completed model','cannot coexist in plenitude','all nineteen unresolved questions']:
        if phrase not in text:return fail('R1 substantive safeguard missing: '+phrase)
    md=R1M.read_text(encoding='utf-8').casefold()
    for phrase in ['the anabasis is the center','education of cyrus','those questions must remain questions','xenophon presents to the reader not indecision but the problem of justice','the older cyrus therefore supplies no answer to xenophon','thibron is the primary institutional endpoint','all nineteen unresolved r3 questions remain active','drafted_pending_in_depth_owner_review']:
        if phrase not in md:return fail('Readable R1 safeguard missing: '+phrase)
    rs=a.get('repository_state',{})
    for k in ['controlled_synthesis_r1_started','controlled_synthesis_r1_draft_complete','controlled_synthesis_r1_predecessor_preserved','controlled_synthesis_r1_anabasis_primary_center','controlled_synthesis_r1_cross_work_scope_corrected','controlled_synthesis_r1_interrogative_legitimacy_preserved','controlled_synthesis_r1_xenophon_presents_problem_of_justice','controlled_synthesis_r1_eight_movements_preserved','controlled_synthesis_r1_all_19_unresolved_questions_preserved']:
        if rs.get(k) is not True:return fail('Audit R1 safeguard missing: '+k)
    if rs.get('controlled_synthesis_r1_owner_reviewed') is not False or rs.get('controlled_synthesis_r1_owner_adopted') is not False:return fail('Audit R1 owner gate mismatch')
    if a.get('resolved_items',[])[-1].get('id')!='RES-023' or a.get('documented_gaps',[])[1].get('id')!='GAP-018':return fail('Audit R1 transition mismatch')
    if rs.get('controlled_comparison_required_next_action')!='XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-R1-IN_DEPTH-OWNER-REVIEW-001':return fail('Audit R1 next action mismatch')
    hist=H.read_text(encoding='utf-8').casefold()
    for phrase in ['education of cyrus','iron alloy','xenophon is the presenter of the problem of justice','eight movements','all nineteen unresolved questions','drafted_pending_in_depth_owner_review']:
        if phrase not in hist:return fail('R1 history safeguard missing: '+phrase)
    if m.get('artificial_intelligence_self_certification_prohibited') is not True or rs.get('minister_adapter_derived') is not False or rs.get('sanctum_registration_present') is not False:return fail('Governance gate mismatch')
    print('Xenophon repository validation passed');return 0
if __name__=='__main__':sys.exit(main())
