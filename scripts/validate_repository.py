from pathlib import Path
import sys, yaml, tempfile, shutil, subprocess
ROOT=Path(__file__).resolve().parents[1]
PREV=ROOT/'scripts/validate_repository_v1_32.py'
UP=lambda n: ROOT/f'studies/xenophon-anabasis-dakyns/units/XEN-PRI-RU-{n:03d}.yaml'
PLAN=ROOT/'studies/xenophon-anabasis-dakyns/reading-plan.yaml'
HIST=ROOT/'history/2026-07-30-anabasis-v4-mossynoecian-alliance.md'
def load(p):
 with p.open(encoding='utf-8') as f:return yaml.safe_load(f)
def dump(p,x):
 with p.open('w',encoding='utf-8') as f:yaml.safe_dump(x,f,sort_keys=False,allow_unicode=True)
def fail(x):print(x);return 1
def types(r):return {o.get('evidence_type') for o in r.get('documentary_observations',[])}
def texts(r):return [o.get('observation','') for o in r.get('documentary_observations',[])]
def run_predecessor():
 if not PREV.exists():return fail('Frozen v1.32 predecessor validator missing')
 with tempfile.TemporaryDirectory(prefix='xenophon-v132-') as td:
  t=Path(td)/'repo';shutil.copytree(ROOT,t,ignore=shutil.ignore_patterns('.git','__pycache__'))
  m=load(t/'manifest.yaml');m['version']='1.32.0';ps=m['primary_study'];ps['drafted_units']=ps['drafted_units'][:-1];ps['book_five_drafted_chapters']=['V.1','V.2','V.3'];m['next_required_unit']={'id':'XEN-PRI-RU-033','description':'Continue the independent primary reconstruction with Anabasis V.4 using the Dakyns Project Gutenberg witness.'};dump(t/'manifest.yaml',m)
  p=load(t/'studies/xenophon-anabasis-dakyns/reading-plan.yaml');p['reading_units']=p['reading_units'][:-1];u=p['reading_units'][-1];u.pop('record',None);u['status']='NEXT';p['remaining_sequence']='Anabasis V.4 through VII.8, strictly in chapter order.';dump(t/'studies/xenophon-anabasis-dakyns/reading-plan.yaml',p)
  a=load(t/'audits/founding-state.yaml');rs=a['repository_state'];rs['drafted_primary_units']=32;rs['book_five_drafted_chapters']=['V.1','V.2','V.3'];a['documented_gaps'][1]['description']='The primary Anabasis reconstruction remains incomplete; Books I through IV are drafted pending owner review, and Book V has drafted coverage through V.3.';a['next_required_action']='Complete XEN-PRI-RU-033 for Anabasis V.4 without importing Strauss or treating translated wording as unmediated Greek evidence.';dump(t/'audits/founding-state.yaml',a)
  r=subprocess.run([sys.executable,str(t/'scripts/validate_repository_v1_32.py')],cwd=t,text=True,capture_output=True)
  if r.returncode:return fail('Frozen v1.32 predecessor validation failed: '+(r.stdout+r.stderr).strip())
 return 0
def main():
 if run_predecessor():return 1
 req=[ROOT/'manifest.yaml',PLAN,ROOT/'audits/founding-state.yaml',UP(33),HIST,PREV]
 miss=[str(p.relative_to(ROOT)) for p in req if not p.exists()]
 if miss:return fail('Missing V.4 production files: '+', '.join(miss))
 m=load(ROOT/'manifest.yaml');a=load(ROOT/'audits/founding-state.yaml');p=load(PLAN);u=load(UP(33))
 if m.get('version')!='1.33.0' or m.get('state')!='PRIMARY_RECONSTRUCTION_IN_PROGRESS':return fail('Manifest V.4 state mismatch')
 if m.get('artificial_intelligence_self_certification_prohibited') is not True:return fail('AI self-certification safeguard missing')
 if m.get('minister',{}).get('registration_status')!='NOT_YET_REGISTERED_IN_SANCTUM':return fail('Premature Sanctum registration')
 pid=[f'XEN-PRI-RU-{n:03d}' for n in range(1,34)]
 ps=m.get('primary_study',{})
 if ps.get('drafted_units')!=pid or ps.get('book_five_drafted_chapters')!=['V.1','V.2','V.3','V.4']:return fail('Manifest V.4 coverage mismatch')
 if m.get('next_required_unit',{}).get('id')!='XEN-PRI-RU-034':return fail('Manifest next unit mismatch')
 units=p.get('reading_units',[])
 if [x.get('id') for x in units]!=pid+['XEN-PRI-RU-034']:return fail('Reading-plan sequence mismatch')
 if [x.get('id') for x in units if x.get('status')=='DRAFTED_PENDING_OWNER_REVIEW']!=pid:return fail('Reading-plan drafted status mismatch')
 if units[-2].get('work_locator')!='Anabasis V.4' or units[-2].get('pdf_pages_one_based')!='101-103':return fail('V.4 reading-plan range mismatch')
 if units[-1].get('work_locator')!='Anabasis V.5' or units[-1].get('pdf_pages_one_based')!='104-106' or units[-1].get('status')!='NEXT':return fail('V.5 next-unit control mismatch')
 if p.get('comparison_gate',{}).get('strauss_comparison')!='DEFERRED':return fail('Strauss comparison gate missing')
 rs=a.get('repository_state',{})
 if rs.get('drafted_primary_units')!=33 or rs.get('book_five_drafted_chapters')!=['V.1','V.2','V.3','V.4']:return fail('Audit V.4 coverage mismatch')
 if rs.get('minister_adapter_derived') is not False or rs.get('sanctum_registration_present') is not False:return fail('Premature derivation or registration')
 if u.get('unit_id')!='XEN-PRI-RU-033' or u.get('status')!='DRAFTED_PENDING_OWNER_REVIEW':return fail('V.4 unit control mismatch')
 if u.get('scope',{}).get('pdf_pages_one_based')!='101-103':return fail('V.4 unit range mismatch')
 if 'Translator wording is not unmediated Greek evidence' not in u.get('jurisdiction',''):return fail('V.4 translation jurisdiction missing')
 if u.get('secondary_comparison_status')!='DEFERRED':return fail('V.4 comparison gate missing')
 n=u.get('narrative_person_and_authorial_attribution',{})
 if n.get('xenophon_as_character_present') is not True or n.get('first_person_narrator_present') is not False or n.get('direct_authorial_self_identification_present') is not False:return fail('V.4 narrative-person controls missing')
 b=u.get('bibliographic_and_witness_control',{}).get('chapter_boundary_control','')
 if 'note (5)' not in b or 'V.4 begins beneath heading IV on page 101' not in b or 'ends immediately before heading V on page 104' not in b or 'V.5 begins on page 104' not in b:return fail('V.4 boundary and paratext control missing')
 need={'BOOK_BOUNDARY_PARATEXT_OBSERVATION','CONTINUED_DUAL_TRANSPORT_OBSERVATION','PROXENOS_MEDIATION_OBSERVATION','FORTRESS_BASED_PASSAGE_REFUSAL_OBSERVATION','INTERNAL_FACTIONAL_HOSTILITY_OBSERVATION','INTERPRETER_MEDIATED_ALLIANCE_OBSERVATION','VENGEANCE_AND_SUBJECTION_PROPOSAL_OBSERVATION','RECIPROCAL_OPERATIONAL_AID_OBSERVATION','RECIPROCAL_PLEDGE_OBSERVATION','THREE_HUNDRED_CANOE_OBSERVATION','ALLIED_FORCE_DISEMBARKATION_OBSERVATION','CHORAL_FORMATION_AND_SONG_OBSERVATION','LOCAL_ARMAMENT_AND_DRESS_OBSERVATION','CITADEL_SUPREMACY_CLAIM_OBSERVATION','COMMON_PROPERTY_USURPATION_REPORT_OBSERVATION','UNAUTHORIZED_PLUNDER_FOLLOWING_OBSERVATION','ROUT_AND_FIRST_REPORTED_FLIGHT_OBSERVATION','DECAPITATION_DISPLAY_OBSERVATION','DISCIPLINE_REFRAMING_OBSERVATION','FAVORABLE_SACRIFICE_OBSERVATION','COLUMN_AND_MISSILE_SUPPORT_OBSERVATION','ORDERED_ADVANCE_CONTRAST_OBSERVATION','KING_MAINTAINED_IN_TOWER_OBSERVATION','BURNING_DEATH_OBSERVATION','PILLAGED_ANCESTRAL_STORES_OBSERVATION','FORTRESS_TRANSFER_AND_ADHESION_OBSERVATION','ELEVATED_SETTLEMENT_NETWORK_OBSERVATION','ELITE_CHILD_FATTENING_REPORT_OBSERVATION','TATTOO_AND_SEXUAL_CUSTOM_REPORT_OBSERVATION','HELLENOCENTRIC_ETHNOGRAPHIC_JUDGMENT_OBSERVATION','EDITORIAL_PARATEXT_OBSERVATION'}
 if need-types(u):return fail('V.4 evidence types missing: '+', '.join(sorted(need-types(u))))
 t=' '.join(texts(u))
 for x in ['selected group continues by sea','Timesitheus the Trapezuntine','refuses passage','hostile faction on the farther side','interprets Xenophon’s alliance speech','vengeance and future subjection','reverse incursion, ships, men','exchange pledges','three hundred single-trunk canoes','Two men per canoe','form facing rows, sing','ivy-leaf shields','high citadel','common property','without orders for plunder','are routed','decapitate the dead','punishment for disorder','reportedly favorable sacrifice','Companies advance in columns','unbroken order','king sits in a guarded wooden tower','are burned','ancestral loaves','stronghold goes to the allies','about ten miles apart','fattened on boiled chestnuts','floral tattoos','most barbaric and outlandish','Notes gloss Mossynoecians']:
  if x not in t:return fail(f'V.4 phrase safeguard missing: {x}')
 if len(u.get('documentary_observations',[]))!=31 or len(u.get('speeches_deeds_and_outcomes',[]))!=10:return fail('V.4 record counts mismatch')
 if len(u.get('provisional_findings',[]))!=8 or len(u.get('standing_unresolved_questions',[]))!=16 or len(u.get('downstream_textual_checks',[]))!=12:return fail('V.4 analytical counts mismatch')
 print('Xenophon repository validation passed');return 0
if __name__=='__main__':sys.exit(main())
