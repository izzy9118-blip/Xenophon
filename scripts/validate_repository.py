from pathlib import Path
import json, py_compile, re, sys, yaml

R=Path(__file__).resolve().parents[1]
M=R/'manifest.yaml'
A=R/'audits/founding-state.yaml'
AD=R/'adapter.py'
MECH=R/'speech/speech-mechanism.yaml'
REQ=R/'tests/fixtures/xenophon-speech-request.yaml'
BRIEF=R/'tests/fixtures/xenophon-adapter-common-briefing.yaml'
R1=R/'studies/comparisons/anabasis-primary-strauss/syntheses/XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001-R1.yaml'
REV=R/'speech/reviews/XEN-MINISTER-ADAPTER-IN-DEPTH-REVIEW-001.yaml'
REVMD=R/'speech/reviews/XEN-MINISTER-ADAPTER-IN-DEPTH-REVIEW-001.md'
OWN=R/'governance/owner-reviews/2026-08-01-xenophon-minister-adapter-in-depth-review.yaml'
H=R/'history/2026-08-01-xenophon-minister-adapter-in-depth-review.md'
PIN=R/'federation/contracts/SANCTUM-CONTRACT-PIN-001.yaml'
SCHEMA=R/'federation/contracts/ministerial-report.schema.1.2.0.json'
FROZEN=R/'scripts/validate_repository_v1_67.py'


def load_yaml(path):
    with path.open(encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_json(path):
    with path.open(encoding='utf-8') as f:
        return json.load(f)


def fail(message):
    print(message)
    return 1


def main():
    required=[M,A,AD,MECH,REQ,BRIEF,R1,REV,REVMD,OWN,H,PIN,SCHEMA,FROZEN]
    for path in required:
        if not path.exists():
            return fail('Review-state file missing: '+str(path))

    py_compile.compile(str(AD),doraise=True)
    py_compile.compile(str(FROZEN),doraise=True)

    m=load_yaml(M); a=load_yaml(A); mech=load_yaml(MECH); req=load_yaml(REQ)
    brief=load_yaml(BRIEF); r1=load_yaml(R1); rev=load_yaml(REV); own=load_yaml(OWN)
    pin=load_yaml(PIN); schema=load_json(SCHEMA)
    adapter_text=AD.read_text(encoding='utf-8')

    if m.get('version')!='1.68.0' or m.get('state')!='MINISTER_ADAPTER_IN_DEPTH_REVIEWED_RETURNED_FOR_TARGETED_R1':
        return fail('v1.68 manifest state mismatch')
    pred=m.get('predecessor_state',{})
    if pred.get('version')!='1.67.0' or pred.get('exact_head')!='689e222ddf0debe24119769a6d9b15552f20c685':
        return fail('Reviewed predecessor pin mismatch')
    if pred.get('frozen_validator')!='scripts/validate_repository_v1_67.py':
        return fail('Frozen predecessor validator not declared')
    phase=m.get('current_phase',{})
    if phase.get('id')!='XEN-PHASE-011' or phase.get('completion_status')!='REVIEW_COMPLETE_TARGETED_R1_REQUIRED':
        return fail('Adapter review phase mismatch')
    if m.get('next_required_action',{}).get('id')!='XEN-MINISTER-ADAPTER-001-R1':
        return fail('Targeted R1 next action mismatch')

    ma=m.get('minister_adapter',{})
    if ma.get('id')!='XEN-MINISTER-ADAPTER-001' or ma.get('status')!='IN_DEPTH_REVIEW_COMPLETE_RETURNED_FOR_TARGETED_R1':
        return fail('Reviewed adapter state mismatch')
    if ma.get('review_disposition')!='RETURN_FOR_TARGETED_R1_REVISION':
        return fail('Adapter review disposition mismatch')
    if ma.get('review_counts')!={'PASS':9,'PASS_WITH_LIMIT':1,'BLOCKING_REVISION':5}:
        return fail('Adapter review counts mismatch')
    if ma.get('blocking_defects')!=[
        'LIVE_SCHEMA_NONCONFORMANCE','WITNESS_IDENTIFIER_INCOMPATIBILITY','FALSE_REPOSITORY_PIN',
        'PLACEHOLDER_UNVERIFIED_HASHES','DERIVATION_AND_OPERATIONAL_AUTHORITY_COLLAPSE']:
        return fail('Manifest blocking-defect inventory mismatch')
    preserved=ma.get('preserved_architecture',{})
    if preserved.get('register_count')!=4 or preserved.get('guard_count')!=3:
        return fail('Preserved adapter architecture count mismatch')
    if preserved.get('all_19_unresolved_questions_preserved') is not True:
        return fail('Nineteen-question preservation missing')
    if any(ma.get(k) is not False for k in ['owner_adopted','operational_authorization','sanctum_registration_authorized','assembly_dispatch_authorized']):
        return fail('Adapter authority granted despite adverse review')

    if rev.get('review_id')!='XEN-MINISTER-ADAPTER-IN-DEPTH-REVIEW-001' or rev.get('status')!='IN_DEPTH_REVIEW_COMPLETE_RETURN_FOR_TARGETED_R1':
        return fail('Detailed review identity/status mismatch')
    if rev.get('overall_ruling',{}).get('adoption_status')!='NOT_ADOPTED':
        return fail('Detailed review improperly adopts adapter')
    if rev.get('disposition_counts')!={'PASS':9,'PASS_WITH_LIMIT':1,'BLOCKING_REVISION':5}:
        return fail('Detailed review counts mismatch')
    findings=rev.get('findings',[])
    if [x.get('id') for x in findings] != [f'XEN-ADAPTER-RF-{i:03d}' for i in range(1,16)]:
        return fail('Detailed review finding sequence mismatch')
    severity=[x.get('severity') for x in findings]
    if severity.count('PASS')!=9 or severity.count('PASS_WITH_LIMIT')!=1 or severity.count('BLOCKING_REVISION')!=5:
        return fail('Detailed review severity count mismatch')
    if rev.get('required_successor',{}).get('id')!='XEN-MINISTER-ADAPTER-001-R1':
        return fail('Detailed review successor mismatch')
    if rev.get('required_successor',{}).get('dependency',{}).get('id')!='SANCTUM-XENOPHON-WITNESS-ID-COMPATIBILITY-001':
        return fail('Federation witness dependency missing')

    if own.get('review_id')!='XEN-OWNER-REVIEW-011' or own.get('status')!='OWNER_REVIEWED_ADAPTER_RETURNED_FOR_TARGETED_R1':
        return fail('Owner review identity/status mismatch')
    ruling=own.get('owner_ruling',{})
    if ruling.get('adoption_status')!='NOT_ADOPTED' or ruling.get('operational_authorization')!='NOT_GRANTED':
        return fail('Owner review improperly authorizes adapter')
    if own.get('external_dependency',{}).get('status')!='REQUIRED_BEFORE_ADAPTER_ADOPTION':
        return fail('Owner review federation dependency mismatch')

    if [x.get('id') for x in mech.get('registers',[])] != [f'XEN-REGISTER-{i:03d}' for i in range(1,5)]:
        return fail('Four reviewed registers changed')
    if [x.get('id') for x in mech.get('guards',[])] != [f'XEN-GUARD-{i:03d}' for i in range(1,4)]:
        return fail('Three reviewed guards changed')
    if len(r1.get('unresolved_questions',[]))!=19:
        return fail('R1 unresolved-question inventory changed')
    if m.get('source_policy',{}).get('greek_language_review',{}).get('required_for_current_production') is not False:
        return fail('Deferred Greek phase became current blocker')
    if m.get('source_policy',{}).get('greek_language_review',{}).get('greek_dependent_claims')!='PROHIBITED':
        return fail('Greek-dependent claim prohibition missing')

    if pin.get('record_id')!='SANCTUM-CONTRACT-PIN-001':
        return fail('Sanctum contract pin missing')
    contracts=pin.get('contracts',{})
    if contracts.get('ministerial_report_schema',{}).get('blob_sha')!='4353735e7cdcdb8896b88f11da3c5d0cc44fd470':
        return fail('Pinned report schema blob mismatch')
    if schema.get('$id')!='urn:sanctum:federation:ministerial-report:1.2.0':
        return fail('Vendored report schema identity mismatch')
    evidence_schema=schema['properties']['evidence']['items']
    if evidence_schema.get('required')!=['witness_id','source_id','repository_commit','path']:
        return fail('Pinned schema evidence contract changed')
    if evidence_schema['properties']['witness_id'].get('pattern')!='^CORPUS-WIT-[0-9]{3}$':
        return fail('Pinned schema witness pattern changed')
    if schema['properties']['uncertainties']['items'].get('type')!='string':
        return fail('Pinned schema uncertainty type changed')
    if schema['properties']['certification_status'].get('enum')!=['PENDING_OWNER_CERTIFICATION','OWNER_CERTIFIED']:
        return fail('Pinned schema certification enum changed')

    # Verify that the adverse findings remain materially true of the reviewed draft.
    if '"ref": ref' not in adapter_text or '"evidence_layer": finding["evidence_layer"]' not in adapter_text:
        return fail('Reviewed evidence-rendering defect no longer identifiable')
    report_builder=adapter_text.split('def build_candidate_report',1)[1]
    if '"witness_id"' in report_builder or '"source_id"' in report_builder:
        return fail('Reviewed adapter changed without targeted R1 record')
    if '"certification_status": "PENDING_OWNER_REVIEW"' not in adapter_text:
        return fail('Reviewed certification-enum defect no longer identifiable')
    if req.get('repository_pin',{}).get('commit')!='b71a6a171fd2467cb712e9f9203d05791268bab4' or req.get('repository_pin',{}).get('manifest_version')!='1.67.0':
        return fail('Reviewed false repository pin changed without R1')
    if req.get('inquiry_ref',{}).get('envelope_sha256')!='a'*64 or req.get('briefing',{}).get('sha256')!='b'*64:
        return fail('Reviewed placeholder hashes changed without R1')
    if brief.get('provenance',{}).get('hash_status')!='FIXTURE_HASH_DECLARED_IN_SPEECH_REQUEST_NOT_BYTE_CERTIFIED':
        return fail('Reviewed briefing hash defect changed without R1')
    if 'import hashlib' in adapter_text or 'hashlib.' in adapter_text:
        return fail('Hash verification added without targeted R1 record')
    if 'authorization_ref": "governance/owner-reviews/2026-08-01-strauss-guided-controlled-synthesis-r1-in-depth-review.yaml"' not in adapter_text:
        return fail('Reviewed authority-collapse defect changed without R1')

    audit_review=a.get('minister_adapter_review',{})
    if audit_review.get('disposition')!='RETURN_FOR_TARGETED_R1_REVISION' or audit_review.get('review_counts')!={'PASS':9,'PASS_WITH_LIMIT':1,'BLOCKING_REVISION':5}:
        return fail('Audit review disposition mismatch')
    if audit_review.get('owner_adopted') is not False or audit_review.get('operational') is not False:
        return fail('Audit grants rejected adapter authority')
    if [x.get('id') for x in a.get('resolved_items',[])]!=['RES-026','RES-027']:
        return fail('Audit resolution sequence mismatch')
    if [x.get('id') for x in a.get('documented_gaps',[])]!=['GAP-004','GAP-020','GAP-021']:
        return fail('Audit gap sequence mismatch')
    if a.get('next_required_action','').startswith('Produce XEN-MINISTER-ADAPTER-001-R1') is not True:
        return fail('Audit next action mismatch')

    combined=(REVMD.read_text(encoding='utf-8')+'\n'+H.read_text(encoding='utf-8')).casefold()
    for phrase in ['report-schema failure','witness-identity incompatibility','false repository pin','placeholder hashes','authorization collapse','xen-minister-adapter-001-r1']:
        if phrase not in combined:
            return fail('Readable review/history safeguard missing: '+phrase)

    if (R/'adapter-r1.py').exists() or (R/'speech/speech-mechanism-r1.yaml').exists():
        return fail('Unauthorized R1 artifact present')
    if m.get('governance_gates',{}).get('artificial_intelligence_self_certification_prohibited') is not True:
        return fail('AI self-certification prohibition missing')
    if m.get('governance_gates',{}).get('sanctum_registration_present') is not False:
        return fail('Sanctum registration occurred prematurely')

    print('Xenophon repository validation passed')
    return 0


if __name__=='__main__':
    sys.exit(main())
