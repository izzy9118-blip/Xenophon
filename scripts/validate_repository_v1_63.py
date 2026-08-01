from pathlib import Path
import json, sys, yaml, tempfile, shutil, subprocess
R=Path(__file__).resolve().parents[1]
P=R/'scripts/validate_repository_v1_62.py'
M=R/'manifest.yaml';A=R/'audits/founding-state.yaml'
SYN=R/'studies/comparisons/anabasis-primary-strauss/syntheses/XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001.yaml'
READ=R/'studies/comparisons/anabasis-primary-strauss/syntheses/XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001.md'
COR=R/'governance/corrections/2026-07-31-xenophon-authorial-revelation-direction.yaml'
CTL=R/'studies/comparisons/anabasis-primary-strauss/synthesis-controls/xenophon-authorial-revelation.yaml'
R3=R/'studies/comparisons/anabasis-primary-strauss/XEN-CONTROLLED-COMPARISON-001-R3.yaml'
H=R/'history/2026-07-31-strauss-guided-controlled-synthesis-draft-completion.md'
def load(p):
    with p.open(encoding='utf-8') as f:return yaml.safe_load(f)
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
def fail(x):print(x);return 1
def predecessor():
    if not P.exists():return fail('Frozen v1.62 validator missing')
    with tempfile.TemporaryDirectory() as d:
        t=Path(d)/'r';shutil.copytree(R,t,ignore=shutil.ignore_patterns('.git','__pycache__'))
        for p in [SYN,READ,H]:
            q=t/p.relative_to(R)
            if q.exists():q.unlink()
        m=load(t/'manifest.yaml')
        m['version']='1.61.0';m['state']='CONTROLLED_COMPARISON_R3_OWNER_ADOPTED'
        m['owner_reviews']=[x for x in m.get('owner_reviews',[]) if x!='governance/owner-reviews/2026-07-31-xenophon-authorial-revelation-direction.yaml']
        m['current_phase']={'id':'XEN-PHASE-006','name':'In-depth owner review and adoption of the targeted R3 controlled comparison','completion_status':'R3_OWNER_ADOPTED'}
        m['primary_study']['cumulative_reconstruction']['secondary_comparison_status']='R3_OWNER_ADOPTED_CONTROLLED_COMPARISON'
        m['next_required_action']={'id':'XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001','description':'Produce a controlled interpretive synthesis from the owner-adopted R3 comparison while preserving primary-secondary source distinctions, the intended Cyrus ambiguity, all nineteen unresolved questions, and the prohibition on declaring a final teaching.'}
        q=m['controlled_comparison']
        for k in ['authorial_direction_correction_record','authorial_direction_owner_review_record','authorial_revelation_direction_active','xenophon_revealing_author','strauss_recovers_concealed_order']:
            q.pop(k,None)
        m.pop('controlled_synthesis',None)
        dump(t/'manifest.yaml',m)
        a=load(t/'audits/founding-state.yaml');rs=a['repository_state']
        for k in list(rs):
            if k.startswith('controlled_synthesis_'):rs.pop(k,None)
        for k in ['controlled_comparison_authorial_direction_correction_record','controlled_comparison_authorial_direction_owner_review_record','controlled_comparison_authorial_revelation_direction_active','controlled_comparison_xenophon_revealing_author','controlled_comparison_strauss_recovers_concealed_order']:
            rs.pop(k,None)
        rs['controlled_comparison_required_next_action']='XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001'
        a['resolved_items']=[x for x in a.get('resolved_items',[]) if x.get('id')!='RES-021']
        a['documented_gaps'][1]={'id':'GAP-015','description':'The owner-adopted R3 controlled comparison has not yet been rendered as a controlled interpretive synthesis that preserves its evidence layers and nineteen unresolved questions.','blocks':['synthesis-level presentation','minister derivation']}
        a['next_required_action']='Produce XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001 before minister adapter construction or Sanctum registration.'
        dump(t/'audits/founding-state.yaml',a)
        z=subprocess.run([sys.executable,str(t/'scripts/validate_repository_v1_62.py')],cwd=t,text=True,capture_output=True)
        if z.returncode:return fail('v1.62 predecessor failed: '+(z.stdout+z.stderr).strip())
    return 0
def main():
    if predecessor():return 1
    for p in [M,A,SYN,READ,COR,CTL,R3,H,P]:
        if not p.exists():return fail('Controlled synthesis file missing: '+str(p))
    m=load(M);a=load(A);syn=load(SYN);cor=load(COR);ctl=load(CTL);r3=load(R3)
    if m.get('version')!='1.63.0' or m.get('state')!='CONTROLLED_SYNTHESIS_DRAFT_COMPLETE_PENDING_IN_DEPTH_OWNER_REVIEW':return fail('v1.63 manifest state mismatch')
    phase=m.get('current_phase',{})
    if phase.get('id')!='XEN-PHASE-007' or phase.get('completion_status')!='SYNTHESIS_DRAFT_COMPLETE_PENDING_IN_DEPTH_OWNER_REVIEW':return fail('Synthesis phase mismatch')
    if m.get('next_required_action',{}).get('id')!='XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-IN_DEPTH-OWNER-REVIEW-001':return fail('Synthesis next action mismatch')
    cs=m.get('controlled_synthesis',{})
    if cs.get('id')!='XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001' or cs.get('status')!='DRAFTED_PENDING_IN_DEPTH_OWNER_REVIEW':return fail('Manifest synthesis identity mismatch')
    if cs.get('structured_record')!=str(SYN.relative_to(R)) or cs.get('readable_record')!=str(READ.relative_to(R)):return fail('Manifest synthesis path mismatch')
    if cs.get('sequential_movement_count')!=8 or cs.get('figural_presentation_count')!=4 or cs.get('governing_examination_count')!=6 or cs.get('unresolved_question_count')!=19:return fail('Manifest synthesis counts mismatch')
    for k in ['xenophon_revealing_author','narrated_xenophon_distinguished','younger_older_cyrus_distinguished','controlled_cyrus_ambiguity_preserved','justice_ambiguity_governs','material_governance_independent','byzantium_mixed_motive_preserved','exact_final_coda_preserved','thibron_primary_endpoint_preserved','all_19_unresolved_questions_preserved','no_final_teaching']:
        if cs.get(k) is not True:return fail('Manifest synthesis safeguard missing: '+k)
    if cs.get('owner_review_status')!='PENDING_IN_DEPTH_REVIEW':return fail('Synthesis review gate mismatch')
    if syn.get('synthesis_id')!='XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001' or syn.get('status')!='DRAFTED_PENDING_IN_DEPTH_OWNER_REVIEW':return fail('Synthesis record identity mismatch')
    moves=syn.get('sequential_synthesis',[])
    if len(moves)!=8 or [x.get('movement_id') for x in moves] != [f'SYN-MOV-{i:03d}' for i in range(1,9)]:return fail('Synthesis sequence mismatch')
    for x in moves:
        if any(not x.get(k) for k in ['title','primary_showing','strauss_explicit_argument','controlled_synthetic_inference','unresolved_limit']):return fail('Synthesis evidence layer missing in '+str(x.get('movement_id')))
    layers=syn.get('evidence_layers',{})
    if set(layers)!={'PRIMARY_SHOWING','STRAUSS_EXPLICIT_ARGUMENT','CONTROLLED_SYNTHETIC_INFERENCE','UNRESOLVED_QUESTION'}:return fail('Synthesis evidence layers mismatch')
    figures=syn.get('figural_revelations',{})
    if set(figures)!={'YOUNGER_CYRUS','OLDER_CYRUS','SOCRATES','XENOPHON_NARRATED_SELF'}:return fail('Figural presentation set mismatch')
    exams=syn.get('governing_examinations',{})
    if set(exams)!={'JUSTICE','LEGITIMACY','FATHERLAND','MATERIAL_GOVERNANCE','PIETY_AND_WILINESS','ENDING'}:return fail('Governing examination set mismatch')
    questions=syn.get('unresolved_questions',[])
    if len(questions)!=19 or [x.get('id') for x in questions] != [f'R3-UQ-{i:03d}' for i in range(1,20)]:return fail('Unresolved question preservation mismatch')
    if cor.get('correction_id')!='XEN-COR-003' or ctl.get('control_id')!='XEN-SYNTHESIS-CONTROL-001':return fail('Authorial direction governance mismatch')
    if r3.get('status')!='DRAFTED_PENDING_IN_DEPTH_OWNER_REVIEW':return fail('Immutable R3 production record changed')
    text=json.dumps(syn,ensure_ascii=False).casefold()
    for phrase in ['xenophon is the revealing author','xenophon reveals','through his presentation of the older cyrus','strauss uncovers the hidden order','justice is the heart of the synthesis','material governance','byzantium','socratic apprehension','booty','gods, and oaths','nineteen unresolved']:
        if phrase not in text:return fail('Synthesis substantive safeguard missing: '+phrase)
    md=READ.read_text(encoding='utf-8').casefold()
    for phrase in ['xenophon is the revealing author','the older cyrus does not supply xenophon','justice governs the ambiguity between the two cyruses','byzantium','thibron is the primary institutional endpoint','all nineteen unresolved r3 questions remain active','drafted_pending_in_depth_owner_review']:
        if phrase not in md:return fail('Readable synthesis safeguard missing: '+phrase)
    rs=a.get('repository_state',{})
    if rs.get('controlled_synthesis_started') is not True or rs.get('controlled_synthesis_draft_complete') is not True:return fail('Audit synthesis production mismatch')
    if rs.get('controlled_synthesis_owner_reviewed') is not False or rs.get('controlled_synthesis_owner_adopted') is not False:return fail('Audit synthesis adoption gate mismatch')
    if rs.get('controlled_synthesis_xenophon_revealing_author') is not True or rs.get('controlled_synthesis_all_19_unresolved_questions_preserved') is not True:return fail('Audit synthesis safeguards missing')
    if a.get('resolved_items',[])[-1].get('id')!='RES-021' or a.get('documented_gaps',[])[1].get('id')!='GAP-016':return fail('Audit synthesis transition mismatch')
    if rs.get('controlled_comparison_required_next_action')!='XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-IN_DEPTH-OWNER-REVIEW-001':return fail('Audit next action mismatch')
    if m.get('artificial_intelligence_self_certification_prohibited') is not True or rs.get('minister_adapter_derived') is not False or rs.get('sanctum_registration_present') is not False:return fail('Governance gate mismatch')
    hist=H.read_text(encoding='utf-8').casefold()
    for phrase in ['xenophon is the revealing author','eight-movement r3 argument sequence','all nineteen unresolved r3 questions','drafted_pending_in_depth_owner_review']:
        if phrase not in hist:return fail('Synthesis history safeguard missing: '+phrase)
    print('Xenophon repository validation passed');return 0
if __name__=='__main__':sys.exit(main())
