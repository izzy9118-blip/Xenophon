from pathlib import Path
import sys, yaml
ROOT=Path(__file__).resolve().parents[1]
SID=[f'XEN-RU-{n:03d}' for n in range(1,9)]
PID=[f'XEN-PRI-RU-{n:03d}' for n in range(1,28)]
UP=lambda n: ROOT/f'studies/xenophon-anabasis-dakyns/units/XEN-PRI-RU-{n:03d}.yaml'
PLAN=ROOT/'studies/xenophon-anabasis-dakyns/reading-plan.yaml'
REQ=[ROOT/'manifest.yaml',ROOT/'corpus/index.yaml',ROOT/'corpus/sources/xenophon-anabasis.yaml',ROOT/'corpus/witnesses/gutenberg-1170-dakyns-pdf.yaml',PLAN,ROOT/'audits/founding-state.yaml',ROOT/'governance/owner-reviews/2026-07-30-strauss-witness-review.yaml',ROOT/'governance/owner-reviews/2026-07-30-primary-anabasis-witness-admission.yaml',ROOT/'history/2026-07-30-primary-anabasis-witness-record.md',*[UP(n) for n in range(1,28)]]
def load(p):
 with p.open(encoding='utf-8') as f:return yaml.safe_load(f)
def fail(x):print(x);return 1
def types(r):return {o.get('evidence_type') for o in r.get('documentary_observations',[])}
def texts(r):return [o.get('observation','') for o in r.get('documentary_observations',[])]
def main():
 missing=[str(p.relative_to(ROOT)) for p in REQ if not p.exists()]
 if missing:return fail('Missing required files: '+', '.join(missing))
 m=load(ROOT/'manifest.yaml'); a=load(ROOT/'audits/founding-state.yaml'); p=load(PLAN)
 if m.get('version')!='1.27.0' or m.get('state')!='PRIMARY_RECONSTRUCTION_IN_PROGRESS':return fail('Manifest state mismatch')
 if m.get('artificial_intelligence_self_certification_prohibited') is not True:return fail('AI self-certification safeguard missing')
 if m.get('minister',{}).get('registration_status')!='NOT_YET_REGISTERED_IN_SANCTUM':return fail('Premature Sanctum registration')
 ps=m.get('primary_study',{})
 if ps.get('drafted_units')!=PID or ps.get('book_four_drafted_chapters')!=['IV.1','IV.2','IV.3','IV.4','IV.5','IV.6']:return fail('Manifest primary coverage mismatch')
 if m.get('next_required_unit',{}).get('id')!='XEN-PRI-RU-028':return fail('Manifest next unit mismatch')
 units=p.get('reading_units',[])
 if [u.get('id') for u in units]!=PID+['XEN-PRI-RU-028']:return fail('Reading plan order mismatch')
 if [u.get('id') for u in units if u.get('status')=='DRAFTED_PENDING_OWNER_REVIEW']!=PID:return fail('Drafted status mismatch')
 if units[-1].get('work_locator')!='Anabasis IV.7' or units[-1].get('pdf_pages_one_based')!='87-89' or units[-1].get('status')!='NEXT':return fail('Next unit control mismatch')
 if p.get('comparison_gate',{}).get('strauss_comparison')!='DEFERRED':return fail('Strauss comparison gate missing')
 if a.get('repository_state',{}).get('drafted_primary_units')!=27:return fail('Audit count mismatch')
 if a.get('repository_state',{}).get('book_four_drafted_chapters')!=['IV.1','IV.2','IV.3','IV.4','IV.5','IV.6']:return fail('Audit Book IV mismatch')
 if a.get('repository_state',{}).get('minister_adapter_derived') is not False or a.get('repository_state',{}).get('sanctum_registration_present') is not False:return fail('Premature derivation or registration')
 w=load(ROOT/'corpus/witnesses/gutenberg-1170-dakyns-pdf.yaml')
 if w.get('status')!='OWNER_ADMITTED_PRIMARY_TRANSLATION_WITNESS' or w.get('witness',{}).get('page_count')!=168:return fail('Witness control mismatch')
 if w.get('file_control',{}).get('sha256')!='6a7534d8d80153afc1623803ef129185aa8d3d41be692091f4e105375c65901e':return fail('Witness digest mismatch')
 docs={n:load(UP(n)) for n in range(1,28)}
 required=['bibliographic_and_witness_control','narrative_person_and_authorial_attribution','speakers_audiences_and_occasions','speeches_deeds_and_outcomes','sequence_repetition_omission_and_contradiction','documentary_observations','provisional_findings','standing_unresolved_questions','downstream_textual_checks']
 for n,r in docs.items():
  uid=f'XEN-PRI-RU-{n:03d}'
  if r.get('unit_id')!=uid or r.get('status')!='DRAFTED_PENDING_OWNER_REVIEW':return fail(f'Unit control mismatch: {uid}')
  if 'Translator wording is not unmediated Greek evidence' not in r.get('jurisdiction',''):return fail(f'Translation jurisdiction missing: {uid}')
  if r.get('secondary_comparison_status')!='DEFERRED':return fail(f'Comparison gate mismatch: {uid}')
  if any(not r.get(x) for x in required):return fail(f'Required section missing: {uid}')
  if any(not o.get('locator') or not o.get('evidence_type') for o in r['documentary_observations']):return fail(f'Untyped observation: {uid}')
  if any(x.get('evidence_type')!='PROVISIONAL_INFERENCE' for x in r['provisional_findings']):return fail(f'Untyped finding: {uid}')
  if any(x.get('evidence_type')!='UNRESOLVED_QUESTION' for x in r['standing_unresolved_questions']):return fail(f'Untyped question: {uid}')
 if docs[11].get('narrative_person_and_authorial_attribution',{}).get('xenophon_as_character_present')!='TEXTUALLY_DISPUTED':return fail('II.1 attribution uncertainty missing')
 if 'TEXTUAL_VARIANT_OBSERVATION' not in types(docs[12]):return fail('II.2 variant safeguard missing')
 if docs[13].get('narrative_person_and_authorial_attribution',{}).get('first_person_narrator_present') is not True:return fail('II.3 first-person safeguard missing')
 if docs[17].get('narrative_person_and_authorial_attribution',{}).get('direct_authorial_self_identification_present') is not True:return fail('III.1 self-reference safeguard missing')
 if 'Book IV retrospective synopsis' not in docs[22].get('bibliographic_and_witness_control',{}).get('chapter_boundary_control',''):return fail('IV.1 paratext safeguard missing')
 if 'corrected' not in docs[24].get('bibliographic_and_witness_control',{}).get('chapter_boundary_control',''):return fail('IV.3 corrected boundary missing')
 u=docs[27]; b=u.get('bibliographic_and_witness_control',{}).get('chapter_boundary_control','')
 if 'ends on PDF page 87' not in b or 'IV.7 begins on page 87' not in b:return fail('IV.6 boundary missing')
 need={'CONDITIONAL_CHILD_CUSTODY_OBSERVATION','CORPORAL_VIOLENCE_OBSERVATION','GUIDE_ESCAPE_OBSERVATION','NARRATORIAL_DISPUTE_JUDGMENT_OBSERVATION','REPORTED_ATTACHMENT_OBSERVATION','ENEMY_COALITION_OBSERVATION','CASUALTY_MINIMIZATION_ARGUMENT_OBSERVATION','NIGHT_FEINT_PLAN_OBSERVATION','CIVIC_STEREOTYPE_OBSERVATION','COERCED_ROUTE_INTELLIGENCE_OBSERVATION','SIGNAL_AND_DECEPTION_OBSERVATION','VICTORY_RITUAL_AND_PROVISION_OBSERVATION'}
 if need-types(u):return fail('IV.6 evidence types missing: '+', '.join(sorted(need-types(u))))
 t=' '.join(texts(u))
 for x,y in [('young son','good guide'),('Ill-treatment and neglect','sole ground of difference'),('passion for the youth','faithful friend'),('fewest wounds','least loss of good men'),('Spartan-theft','Athenian-public-money'),('Captured rear-followers','route intelligence'),('watchfires','feint'),('wicker shields','trophy')]:
  if x not in t or y not in t:return fail(f'IV.6 phrase safeguard missing: {x}')
 print('Xenophon repository validation passed');return 0
if __name__=='__main__':sys.exit(main())
