from pathlib import Path
import sys, yaml, tempfile, shutil, subprocess
ROOT=Path(__file__).resolve().parents[1]
PREV=ROOT/'scripts/validate_repository_v1_33.py'
UP=lambda n: ROOT/f'studies/xenophon-anabasis-dakyns/units/XEN-PRI-RU-{n:03d}.yaml'
PLAN=ROOT/'studies/xenophon-anabasis-dakyns/reading-plan.yaml'
HIST=ROOT/'history/2026-07-30-anabasis-v5-cotyora-sinope-dispute.md'
def load(p):
 with p.open(encoding='utf-8') as f:return yaml.safe_load(f)
def dump(p,x):
 with p.open('w',encoding='utf-8') as f:yaml.safe_dump(x,f,sort_keys=False,allow_unicode=True)
def fail(x):print(x);return 1
def types(r):return {o.get('evidence_type') for o in r.get('documentary_observations',[])}
def texts(r):return [o.get('observation','') for o in r.get('documentary_observations',[])]
def run_predecessor():
 if not PREV.exists():return fail('Frozen v1.33 predecessor validator missing')
 with tempfile.TemporaryDirectory(prefix='xenophon-v133-') as td:
  t=Path(td)/'repo';shutil.copytree(ROOT,t,ignore=shutil.ignore_patterns('.git','__pycache__'))
  m=load(t/'manifest.yaml');m['version']='1.33.0';ps=m['primary_study'];ps['drafted_units']=ps['drafted_units'][:-1];ps['book_five_drafted_chapters']=['V.1','V.2','V.3','V.4'];m['next_required_unit']={'id':'XEN-PRI-RU-034','description':'Continue the independent primary reconstruction with Anabasis V.5 using the Dakyns Project Gutenberg witness.'};dump(t/'manifest.yaml',m)
  p=load(t/'studies/xenophon-anabasis-dakyns/reading-plan.yaml');p['reading_units']=p['reading_units'][:-1];u=p['reading_units'][-1];u.pop('record',None);u['status']='NEXT';p['remaining_sequence']='Anabasis V.6 through VII.8, strictly in chapter order.';dump(t/'studies/xenophon-anabasis-dakyns/reading-plan.yaml',p)
  a=load(t/'audits/founding-state.yaml');rs=a['repository_state'];rs['drafted_primary_units']=33;rs['book_five_drafted_chapters']=['V.1','V.2','V.3','V.4'];a['documented_gaps'][1]['description']='The primary Anabasis reconstruction remains incomplete; Books I through IV are drafted pending owner review, and Book V has drafted coverage through V.4.';a['next_required_action']='Complete XEN-PRI-RU-034 for Anabasis V.5 without importing Strauss or treating translated wording as unmediated Greek evidence.';dump(t/'audits/founding-state.yaml',a)
  r=subprocess.run([sys.executable,str(t/'scripts/validate_repository_v1_33.py')],cwd=t,text=True,capture_output=True)
  if r.returncode:return fail('Frozen v1.33 predecessor validation failed: '+(r.stdout+r.stderr).strip())
 return 0
def main():
 if run_predecessor():return 1
 req=[ROOT/'manifest.yaml',PLAN,ROOT/'audits/founding-state.yaml',UP(34),HIST,PREV]
 miss=[str(p.relative_to(ROOT)) for p in req if not p.exists()]
 if miss:return fail('Missing V.5 production files: '+', '.join(miss))
 m=load(ROOT/'manifest.yaml');a=load(ROOT/'audits/founding-state.yaml');p=load(PLAN);u=load(UP(34))
 if m.get('version')!='1.34.0' or m.get('state')!='PRIMARY_RECONSTRUCTION_IN_PROGRESS':return fail('Manifest V.5 state mismatch')
 if m.get('artificial_intelligence_self_certification_prohibited') is not True:return fail('AI self-certification safeguard missing')
 if m.get('minister',{}).get('registration_status')!='NOT_YET_REGISTERED_IN_SANCTUM':return fail('Premature Sanctum registration')
 pid=[f'XEN-PRI-RU-{n:03d}' for n in range(1,35)]
 ps=m.get('primary_study',{})
 if ps.get('drafted_units')!=pid or ps.get('book_five_drafted_chapters')!=['V.1','V.2','V.3','V.4','V.5']:return fail('Manifest V.5 coverage mismatch')
 if m.get('next_required_unit',{}).get('id')!='XEN-PRI-RU-035':return fail('Manifest next unit mismatch')
 units=p.get('reading_units',[])
 if [x.get('id') for x in units]!=pid+['XEN-PRI-RU-035']:return fail('Reading-plan sequence mismatch')
 if [x.get('id') for x in units if x.get('status')=='DRAFTED_PENDING_OWNER_REVIEW']!=pid:return fail('Reading-plan drafted status mismatch')
 if units[-2].get('work_locator')!='Anabasis V.5' or units[-2].get('pdf_pages_one_based')!='104-106':return fail('V.5 reading-plan range mismatch')
 if units[-1].get('work_locator')!='Anabasis V.6' or units[-1].get('pdf_pages_one_based')!='107-111' or units[-1].get('status')!='NEXT':return fail('V.6 next-unit control mismatch')
 if p.get('comparison_gate',{}).get('strauss_comparison')!='DEFERRED':return fail('Strauss comparison gate missing')
 rs=a.get('repository_state',{})
 if rs.get('drafted_primary_units')!=34 or rs.get('book_five_drafted_chapters')!=['V.1','V.2','V.3','V.4','V.5']:return fail('Audit V.5 coverage mismatch')
 if rs.get('minister_adapter_derived') is not False or rs.get('sanctum_registration_present') is not False:return fail('Premature derivation or registration')
 if u.get('unit_id')!='XEN-PRI-RU-034' or u.get('status')!='DRAFTED_PENDING_OWNER_REVIEW':return fail('V.5 unit control mismatch')
 if u.get('scope',{}).get('pdf_pages_one_based')!='104-106':return fail('V.5 unit range mismatch')
 if 'Translator wording is not unmediated Greek evidence' not in u.get('jurisdiction',''):return fail('V.5 translation jurisdiction missing')
 if u.get('secondary_comparison_status')!='DEFERRED':return fail('V.5 comparison gate missing')
 n=u.get('narrative_person_and_authorial_attribution',{})
 if n.get('xenophon_as_character_present') is not True or n.get('first_person_narrator_present') is not False or n.get('direct_authorial_self_identification_present') is not False:return fail('V.5 narrative-person controls missing')
 b=u.get('bibliographic_and_witness_control',{}).get('chapter_boundary_control','')
 if 'V.5 begins beneath heading V on PDF page 104' not in b or 'ends immediately before heading VI on page 107' not in b or 'V.6 begins beneath heading VI on page 107' not in b:return fail('V.5 boundary control missing')
 need={'BOOK_BOUNDARY_OBSERVATION','MIXED_RELATIONS_ROUTE_OBSERVATION','SUBJECT_MINING_PEOPLE_OBSERVATION','WEAKER_COASTAL_FORTRESS_OBSERVATION','PLUNDER_MOTIVE_COUNCIL_OBSERVATION','DEFERRED_HOSPITALITY_GIFT_OBSERVATION','REPEATED_ABORTIVE_SACRIFICE_OBSERVATION','DIVINE_NON_COUNTENANCE_OF_WAR_OBSERVATION','SACRIFICE_RESTRAINS_PLUNDER_OBSERVATION','HELLENIC_COLONY_OBSERVATION','EDITORIAL_DISTANCE_NOTE_OBSERVATION','FORTY_FIVE_DAY_HALT_OBSERVATION','TRIBAL_PROCESSION_AND_GAMES_OBSERVATION','MARKET_AND_SICK_ACCESS_REFUSAL_OBSERVATION','ESTATE_PROVISIONING_OBSERVATION','SINOPEAN_FEAR_AND_TRIBUTE_INTEREST_OBSERVATION','REPORTED_CLEVER_ORATOR_OBSERVATION','HELLENIC_SOLIDARITY_CLAIM_OBSERVATION','COLONIAL_CONQUEST_TITLE_OBSERVATION','FORCIBLE_ENTRY_AND_SEIZURE_ALLEGATION_OBSERVATION','EXTERNAL_ALLIANCE_THREAT_OBSERVATION','PAID_MARKET_RECIPROCITY_DEFENSE_OBSERVATION','NECESSITY_NOT_INSOLENCE_DEFENSE_OBSERVATION','COMPARATIVE_PEOPLE_PRECEDENT_OBSERVATION','COTYORITE_BLAME_ATTRIBUTION_OBSERVATION','SICK_SHELTER_FORCED_ENTRY_DEFENSE_OBSERVATION','PATIENT_EXPENSE_PAYMENT_OBSERVATION','GATE_SENTRY_CONTROL_OBSERVATION','MAIN_ARMY_OUTSIDE_CAMP_OBSERVATION','COUNTER_ALLIANCE_THREAT_OBSERVATION','AMBASSADORIAL_INTERNAL_DISSENT_OBSERVATION','DE_ESCALATORY_FRIENDSHIP_CLARIFICATION_OBSERVATION','HOSPITALITY_RESTORATION_OBSERVATION','ROUTE_CONSULTATION_OBSERVATION','HARMOST_PARATEXT_OBSERVATION'}
 if need-types(u):return fail('V.5 evidence types missing: '+', '.join(sorted(need-types(u))))
 t=' '.join(texts(u))
 for x in ['eight stages','few in number','weaker by art or nature','obtain pickings','initially refused','Several sacrificial attempts fail','do not countenance war','accepts hospitality','Hellenic city and colony of Sinope','manuscript-distance calculation','forty-five days','processions by tribes','refuse both a market','Cotyorite estates','fear for Cotyora','clever orator','fellow-Hellenes owe kindness','land earlier taken from unnamed barbarians','forcible entry','alliance with Corylas','paid market exchange','necessity rather than insolence','market-providing Macrones','blames Cotyora','shelter sick and wounded','pay their expenses','sentry at the gates','outside in regular order','ally with Paphlagonia','annoyance with Hecatonymus','disclaims warlike intent','send gifts','remaining journey','harmost']:
  if x not in t:return fail(f'V.5 phrase safeguard missing: {x}')
 if len(u.get('documentary_observations',[]))!=35 or len(u.get('speeches_deeds_and_outcomes',[]))!=12:return fail('V.5 record counts mismatch')
 if len(u.get('provisional_findings',[]))!=10 or len(u.get('standing_unresolved_questions',[]))!=18 or len(u.get('downstream_textual_checks',[]))!=12:return fail('V.5 analytical counts mismatch')
 print('Xenophon repository validation passed');return 0
if __name__=='__main__':sys.exit(main())
