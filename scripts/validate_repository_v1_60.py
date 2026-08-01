from pathlib import Path
import json, sys, yaml
R=Path(__file__).resolve().parents[1]
def load(p):
    with p.open(encoding='utf-8') as f:return yaml.safe_load(f)
def fail(x):
    print(x);return 1
def main():
    m=load(R/'manifest.yaml');a=load(R/'audits/founding-state.yaml')
    r3=load(R/'studies/comparisons/anabasis-primary-strauss/XEN-CONTROLLED-COMPARISON-001-R3.yaml')
    ca=load(R/'studies/comparisons/anabasis-primary-strauss/r3/controlled-cyrus-ambiguity.yaml')
    byz=load(R/'studies/comparisons/anabasis-primary-strauss/r3/byzantium-examination.yaml')
    coda=load(R/'studies/comparisons/anabasis-primary-strauss/r3/final-coda-sequence.yaml')
    ec=load(R/'studies/comparisons/anabasis-primary-strauss/r3/entry-corrections.yaml')
    de=load(R/'studies/comparisons/anabasis-primary-strauss/r3/deep-examinations.yaml')
    if m.get('version')!='1.60.0' or m.get('state')!='CONTROLLED_COMPARISON_R3_DRAFT_COMPLETE_PENDING_IN_DEPTH_OWNER_REVIEW':return fail('v1.60 state mismatch')
    q=m.get('controlled_comparison',{})
    if q.get('revision_id')!='XEN-CONTROLLED-COMPARISON-001-R3' or q.get('owner_review_status')!='PENDING_IN_DEPTH_REVIEW':return fail('v1.60 review gate mismatch')
    if q.get('comparison_entry_count')!=31 or q.get('sequential_movement_count')!=8 or q.get('deep_examination_count')!=8:return fail('v1.60 counts mismatch')
    for k in ['controlled_intended_cyrus_ambiguity','younger_cyrus_role_distinguished','older_cyrus_role_distinguished','distinction_without_compartmentalization','justice_ambiguity_governs_cyrus_ambiguity','byzantium_deep_examination_present','post_question_coda_exact_order_present','thibron_primary_endpoint_preserved']:
        if q.get(k) is not True:return fail('v1.60 safeguard missing: '+k)
    if r3.get('status')!='DRAFTED_PENDING_IN_DEPTH_OWNER_REVIEW':return fail('R3 draft status mismatch')
    terms=r3.get('governing_architecture',{}).get('controlled_terms',{})
    if set(terms)!={'YOUNGER_CYRUS_ROLE','OLDER_CYRUS_ROLE','CYRUS_SIDE_AMBIGUITY'}:return fail('Cyrus terms mismatch')
    if ca.get('justice_structure',{}).get('explicit_statement')!='Justice is an ambiguous term.':return fail('Justice ambiguity missing')
    if byz.get('examination_id')!='XEN-R3-BYZANTIUM-001':return fail('Byzantium record missing')
    if [x.get('id') for x in coda.get('ordered_elements',[])]!=['SOCRATIC_APPREHENSION_QUESTION','POST_QUESTION_CODA_BOOTY','POST_QUESTION_CODA_GODS_AND_OATHS']:return fail('Coda order mismatch')
    if ec.get('entry_count')!=10 or de.get('examination_count')!=8:return fail('R3 production counts mismatch')
    rs=a.get('repository_state',{})
    if rs.get('controlled_comparison_r3_draft_complete') is not True or rs.get('controlled_comparison_r3_owner_reviewed') is not False:return fail('v1.60 audit mismatch')
    if a.get('resolved_items',[])[-1].get('id')!='RES-019' or a.get('documented_gaps',[])[1].get('id')!='GAP-014':return fail('v1.60 audit transition mismatch')
    print('Xenophon repository validation passed');return 0
if __name__=='__main__':sys.exit(main())
