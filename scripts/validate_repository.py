from pathlib import Path
import copy, importlib.util, json, shutil, subprocess, sys, tempfile, yaml

R=Path(__file__).resolve().parents[1]
P=R/'scripts/validate_repository_v1_66.py'
M=R/'manifest.yaml'; A=R/'audits/founding-state.yaml'
AD=R/'adapter.py'; MECH=R/'speech/speech-mechanism.yaml'
REQ=R/'tests/fixtures/xenophon-speech-request.yaml'
BRIEF=R/'tests/fixtures/xenophon-adapter-common-briefing.yaml'
TEST=R/'tests/test_minister_adapter.py'
H=R/'history/2026-08-01-xenophon-minister-adapter-draft-completion.md'
R1=R/'studies/comparisons/anabasis-primary-strauss/syntheses/XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001-R1.yaml'

def load(p):
    with p.open(encoding='utf-8') as f:return yaml.safe_load(f)
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
def fail(x):print(x);return 1

def predecessor():
    if not P.exists():return fail('Frozen v1.66 validator missing')
    with tempfile.TemporaryDirectory() as d:
        t=Path(d)/'r';shutil.copytree(R,t,ignore=shutil.ignore_patterns('.git','__pycache__'))
        for p in [AD,MECH,REQ,BRIEF,TEST,H]:
            q=t/p.relative_to(R)
            if q.exists():q.unlink()
        m=load(t/'manifest.yaml')
        m['version']='1.66.0';m['state']='CONTROLLED_SYNTHESIS_R1_OWNER_ADOPTED_GREEK_REVIEW_DEFERRED'
        m['current_phase']={'id':'XEN-PHASE-009','name':'Owner adoption of targeted R1 synthesis and deferral of Greek-language certification','completion_status':'R1_OWNER_ADOPTED_GREEK_REVIEW_DEFERRED'}
        m['primary_study']['cumulative_reconstruction']['secondary_comparison_status']='CONTROLLED_SYNTHESIS_R1_OWNER_ADOPTED'
        m['next_required_action']={'id':'XEN-MINISTER-ADAPTER-001','description':'Construct the Xenophon minister adapter from the owner-adopted R1 synthesis while preserving English-witness jurisdiction, provenance, all nineteen unresolved questions, dissent, and the deferred Greek-language phase.'}
        m.pop('minister_adapter',None)
        dump(t/'manifest.yaml',m)
        a=load(t/'audits/founding-state.yaml');rs=a['repository_state']
        for k in ['minister_adapter_draft_complete','minister_adapter_id','minister_adapter_path','minister_speech_mechanism_path','minister_adapter_register_count','minister_adapter_guard_count','minister_adapter_behavioral_fixture_present','minister_adapter_owner_reviewed','minister_adapter_owner_adopted','minister_adapter_operational']:
            rs.pop(k,None)
        rs['minister_adapter_derived']=False
        rs['controlled_comparison_required_next_action']='XEN-MINISTER-ADAPTER-001'
        a['resolved_items']=[x for x in a.get('resolved_items',[]) if x.get('id')!='RES-026']
        a['documented_gaps']=[
            {'id':'GAP-004','status':'DEFERRED_BY_OWNER','classification':'DEFERRED_FUTURE_ENRICHMENT','description':'No reviewed original-language Greek witness or critical edition is registered. The owner intends to examine Greek much later while learning the language.','current_blocking_effect':False,'blocks':['Greek philological conclusions','translation adjudication against the Greek','Greek textual certification','claims of final original-language authority'],'does_not_block':['English-witness synthesis adoption','minister adapter construction','appropriately limited Sanctum registration']},
            {'id':'GAP-003','description':'No owner-approved Xenophon adapter exists.','blocks':['Assembly dispatch']}
        ]
        a['next_required_action']='Construct XEN-MINISTER-ADAPTER-001 from the owner-adopted R1 synthesis before Sanctum registration or Assembly dispatch.'
        dump(t/'audits/founding-state.yaml',a)
        z=subprocess.run([sys.executable,str(t/'scripts/validate_repository_v1_66.py')],cwd=t,text=True,capture_output=True)
        if z.returncode:return fail('v1.66 predecessor failed: '+(z.stdout+z.stderr).strip())
    return 0

def load_adapter():
    spec=importlib.util.spec_from_file_location('xenophon_adapter',AD)
    if spec is None or spec.loader is None:raise RuntimeError('Unable to load adapter.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def main():
    if predecessor():return 1
    for p in [M,A,AD,MECH,REQ,BRIEF,TEST,H,R1,P]:
        if not p.exists():return fail('Adapter production file missing: '+str(p))
    m=load(M);a=load(A);mech=load(MECH);req=load(REQ);brief=load(BRIEF);r1=load(R1)
    if m.get('version')!='1.67.0' or m.get('state')!='MINISTER_ADAPTER_DRAFT_COMPLETE_PENDING_OWNER_REVIEW':return fail('v1.67 manifest state mismatch')
    phase=m.get('current_phase',{})
    if phase.get('id')!='XEN-PHASE-010' or phase.get('completion_status')!='ADAPTER_DRAFT_COMPLETE_PENDING_OWNER_REVIEW':return fail('Adapter phase mismatch')
    if m.get('next_required_action',{}).get('id')!='XEN-MINISTER-ADAPTER-IN_DEPTH-OWNER-REVIEW-001':return fail('Adapter owner review next action mismatch')
    ma=m.get('minister_adapter',{})
    if ma.get('id')!='XEN-MINISTER-ADAPTER-001' or ma.get('status')!='DRAFT_COMPLETE_PENDING_OWNER_REVIEW':return fail('Adapter identity/status mismatch')
    if ma.get('register_count')!=4 or ma.get('guard_count')!=3:return fail('Adapter register/guard count mismatch')
    if ma.get('registers')!=[f'XEN-REGISTER-{i:03d}' for i in range(1,5)]:return fail('Manifest register order mismatch')
    if ma.get('guards')!=[f'XEN-GUARD-{i:03d}' for i in range(1,4)]:return fail('Manifest guard order mismatch')
    for k in ['all_19_unresolved_questions_available','identical_briefing_required','tailored_feed_prohibited','committed_judgment_required','self_reference_prohibited','greek_dependent_claims_prohibited','artificial_intelligence_self_certification_prohibited']:
        if ma.get(k) is not True:return fail('Manifest adapter safeguard missing: '+k)
    if ma.get('owner_reviewed') is not False or ma.get('owner_adopted') is not False or ma.get('operational_authorization') is not False:return fail('Adapter owner/operational gate mismatch')
    if ma.get('sanctum_registration_authorized') is not False or ma.get('assembly_dispatch_authorized') is not False:return fail('Adapter federation gate mismatch')
    if len(r1.get('unresolved_questions',[]))!=19:return fail('R1 nineteen-question inventory changed')

    if mech.get('identity',{}).get('id')!='XEN-SPEECH-MECHANISM-001' or mech.get('status')!='DRAFT_COMPLETE_PENDING_OWNER_REVIEW':return fail('Speech mechanism mismatch')
    if [x.get('id') for x in mech.get('registers',[])]!=[f'XEN-REGISTER-{i:03d}' for i in range(1,5)]:return fail('Mechanism register order mismatch')
    if [x.get('id') for x in mech.get('guards',[])]!=[f'XEN-GUARD-{i:03d}' for i in range(1,4)]:return fail('Mechanism guard order mismatch')
    cc=mech.get('constitutional_contract',{})
    for k in ['identical_briefing_required','tailored_briefing_prohibited','committed_judgment_required','internal_bothsidesism_prohibited','standing_unresolved_questions_required','unresolved_questions_are_positive_results','candor_of_fact_and_judgment_required','protective_esotericism_as_costume_prohibited','self_reference_prohibited','evidence_typing_required','artificial_intelligence_self_certification_prohibited','quote_engine_output_prohibited','disagreement_preservation_required']:
        if cc.get(k) is not True:return fail('Constitutional mechanism control missing: '+k)
    if mech.get('termination',{}).get('sanctum_registration')!='NOT_AUTHORIZED':return fail('Mechanism prematurely authorizes Sanctum')

    if brief.get('identical_for_all_ministers') is not True or brief.get('tailored_feed') is not False:return fail('Common briefing fixture violates standard')
    if req.get('fixture_status')!='TEST_FIXTURE_NO_ASSEMBLY_EFFECT':return fail('Proving request fixture effect mismatch')
    adapter=load_adapter()
    if adapter.validate_manifest(m):return fail('Adapter manifest validation failed: '+'; '.join(adapter.validate_manifest(m)))
    if adapter.validate_mechanism(mech):return fail('Adapter mechanism validation failed: '+'; '.join(adapter.validate_mechanism(mech)))
    errors=adapter.validate_speech_request(req)
    if errors:return fail('Adapter proving request failed: '+'; '.join(errors))
    report=adapter.build_candidate_report(req)
    if report.get('record_type')!='ministerial_report' or report.get('report_status')!='DRAFT_PENDING_MINISTER_REPOSITORY_VALIDATION':return fail('Candidate report shape/status mismatch')
    if report.get('minister',{}).get('actor')!='xenophon':return fail('Candidate minister identity mismatch')
    if report.get('certification_status')!='PENDING_OWNER_REVIEW' or report.get('artificial_intelligence_self_certification')!='PROHIBITED':return fail('Candidate report certification gate mismatch')
    if report.get('jurisdiction',{}).get('greek_dependent_claims')!='PROHIBITED':return fail('Candidate Greek claim guard missing')
    if report.get('termination',{}).get('presidential_synthesis')!='NOT_PERFORMED':return fail('Candidate report claims presidential synthesis')
    layers={x.get('evidence_layer') for x in report.get('propositions',[])}
    if layers!={'primary_showing','strauss_explicit_argument','controlled_synthetic_inference','unresolved_question'}:return fail('Candidate evidence layers mismatch')
    if len(report.get('pedagogical_path',[]))!=4 or not report.get('uncertainties') or not report.get('dissent'):return fail('Candidate pedagogy/uncertainty/dissent missing')

    bad=copy.deepcopy(req);bad['briefing']['tailored_feed']=True;bad['claims_greek_textual_authority']=True
    bad_errors=adapter.validate_speech_request(bad)
    if 'tailored briefing feeds are prohibited' not in bad_errors or 'Greek textual authority may not be claimed' not in bad_errors:return fail('Adapter does not reject tailored briefing or Greek authority')
    erased=copy.deepcopy(req);erased['findings']=[x for x in erased['findings'] if x.get('evidence_layer')!='unresolved_question'];erased['standing_unresolved_questions']=[]
    erased_errors=adapter.validate_speech_request(erased)
    if 'at least one unresolved question must remain standing' not in erased_errors or 'standing_unresolved_questions must be a non-empty list' not in erased_errors:return fail('Adapter does not reject uncertainty erasure')

    rs=a.get('repository_state',{})
    for k in ['minister_adapter_derived','minister_adapter_authorized','minister_adapter_draft_complete','minister_adapter_behavioral_fixture_present']:
        if rs.get(k) is not True:return fail('Audit adapter state missing: '+k)
    if rs.get('minister_adapter_register_count')!=4 or rs.get('minister_adapter_guard_count')!=3:return fail('Audit register/guard count mismatch')
    if rs.get('minister_adapter_owner_reviewed') is not False or rs.get('minister_adapter_owner_adopted') is not False or rs.get('minister_adapter_operational') is not False:return fail('Audit adapter gate mismatch')
    if rs.get('sanctum_registration_present') is not False:return fail('Sanctum registration occurred prematurely')
    if rs.get('controlled_comparison_required_next_action')!='XEN-MINISTER-ADAPTER-IN_DEPTH-OWNER-REVIEW-001':return fail('Audit next action mismatch')
    if a.get('resolved_items',[])[-1].get('id')!='RES-026':return fail('Audit RES-026 missing')
    gaps=a.get('documented_gaps',[])
    if [x.get('id') for x in gaps]!=['GAP-004','GAP-019']:return fail('Audit gap transition mismatch')
    if gaps[0].get('current_blocking_effect') is not False:return fail('Deferred Greek phase became a current blocker')
    if a.get('next_required_action')!='Conduct XEN-MINISTER-ADAPTER-IN_DEPTH-OWNER-REVIEW-001 before Sanctum registration or Assembly dispatch.':return fail('Audit next action text mismatch')
    hist=H.read_text(encoding='utf-8').casefold()
    for phrase in ['four registers','three guards','one identical, auditable briefing','committed judgment','all nineteen r1 unresolved questions','test_fixture_no_assembly_effect','xen-minister-adapter-in_depth-owner-review-001']:
        if phrase not in hist:return fail('Adapter history safeguard missing: '+phrase)
    print('Xenophon repository validation passed');return 0

if __name__=='__main__':sys.exit(main())
