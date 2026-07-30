from pathlib import Path
import sys, yaml
ROOT=Path(__file__).resolve().parents[1]
SID=[f'XEN-RU-{n:03d}' for n in range(1,9)]
PID=[f'XEN-PRI-RU-{n:03d}' for n in range(1,32)]
UP=lambda n: ROOT/f'studies/xenophon-anabasis-dakyns/units/XEN-PRI-RU-{n:03d}.yaml'
PLAN=ROOT/'studies/xenophon-anabasis-dakyns/reading-plan.yaml'
REQ=[ROOT/'manifest.yaml',ROOT/'corpus/index.yaml',ROOT/'corpus/sources/xenophon-anabasis.yaml',ROOT/'corpus/witnesses/gutenberg-1170-dakyns-pdf.yaml',PLAN,ROOT/'audits/founding-state.yaml',ROOT/'governance/owner-reviews/2026-07-30-strauss-witness-review.yaml',ROOT/'governance/owner-reviews/2026-07-30-primary-anabasis-witness-admission.yaml',ROOT/'history/2026-07-30-primary-anabasis-witness-record.md',ROOT/'history/2026-07-30-anabasis-book-iv-draft-completion.md',ROOT/'history/2026-07-30-anabasis-book-v-draft-start.md',ROOT/'history/2026-07-30-anabasis-v2-drilaean-operation.md',*[UP(n) for n in range(1,32)]]
def load(p):
 with p.open(encoding='utf-8') as f:return yaml.safe_load(f)
def fail(x):print(x);return 1
def types(r):return {o.get('evidence_type') for o in r.get('documentary_observations',[])}
def texts(r):return [o.get('observation','') for o in r.get('documentary_observations',[])]
def main():
 missing=[str(p.relative_to(ROOT)) for p in REQ if not p.exists()]
 if missing:return fail('Missing required files: '+', '.join(missing))
 m=load(ROOT/'manifest.yaml'); a=load(ROOT/'audits/founding-state.yaml'); p=load(PLAN)
 if m.get('version')!='1.31.0' or m.get('state')!='PRIMARY_RECONSTRUCTION_IN_PROGRESS':return fail('Manifest state mismatch')
 if m.get('artificial_intelligence_self_certification_prohibited') is not True:return fail('AI self-certification safeguard missing')
 if m.get('minister',{}).get('registration_status')!='NOT_YET_REGISTERED_IN_SANCTUM':return fail('Premature Sanctum registration')
 ps=m.get('primary_study',{})
 chapters=['IV.1','IV.2','IV.3','IV.4','IV.5','IV.6','IV.7','IV.8']
 if ps.get('drafted_units')!=PID or ps.get('book_four_drafted_chapters')!=chapters:return fail('Manifest primary coverage mismatch')
 if ps.get('book_four_draft_complete_pending_owner_review') is not True:return fail('Book IV draft-complete marker missing')
 if ps.get('book_five_drafted_chapters')!=['V.1','V.2']:return fail('Manifest Book V coverage mismatch')
 if m.get('next_required_unit',{}).get('id')!='XEN-PRI-RU-032':return fail('Manifest next unit mismatch')
 units=p.get('reading_units',[])
 if [u.get('id') for u in units]!=PID+['XEN-PRI-RU-032']:return fail('Reading plan order mismatch')
 if [u.get('id') for u in units if u.get('status')=='DRAFTED_PENDING_OWNER_REVIEW']!=PID:return fail('Drafted status mismatch')
 if units[-1].get('work_locator')!='Anabasis V.3' or units[-1].get('pdf_pages_one_based')!='99-100' or units[-1].get('status')!='NEXT':return fail('Next unit control mismatch')
 if units[-2].get('work_locator')!='Anabasis V.2' or units[-2].get('pdf_pages_one_based')!='96-98':return fail('V.2 range missing')
 if p.get('comparison_gate',{}).get('strauss_comparison')!='DEFERRED':return fail('Strauss comparison gate missing')
 rs=a.get('repository_state',{})
 if rs.get('drafted_primary_units')!=31:return fail('Audit count mismatch')
 if rs.get('book_four_drafted_chapters')!=chapters or rs.get('book_four_primary_draft_complete') is not True:return fail('Audit Book IV mismatch')
 if rs.get('book_five_drafted_chapters')!=['V.1','V.2']:return fail('Audit Book V mismatch')
 if rs.get('minister_adapter_derived') is not False or rs.get('sanctum_registration_present') is not False:return fail('Premature derivation or registration')
 w=load(ROOT/'corpus/witnesses/gutenberg-1170-dakyns-pdf.yaml')
 if w.get('status')!='OWNER_ADMITTED_PRIMARY_TRANSLATION_WITNESS' or w.get('witness',{}).get('page_count')!=168:return fail('Witness control mismatch')
 if w.get('file_control',{}).get('sha256')!='6a7534d8d80153afc1623803ef129185aa8d3d41be692091f4e105375c65901e':return fail('Witness digest mismatch')
 docs={n:load(UP(n)) for n in range(1,32)}
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
 if docs[28].get('scope',{}).get('pdf_pages_one_based')!='87-90':return fail('IV.7 corrected boundary missing')
 u=docs[29]; b=u.get('bibliographic_and_witness_control',{}).get('chapter_boundary_control','')
 if 'ends on PDF page 93' not in b or 'Book V retrospective synopsis' not in b or 'V.1 begins' not in b:return fail('IV.8 boundary and paratext control missing')
 need={'BORDER_RIVER_OBSERVATION','MACRONE_ARMAMENT_OBSERVATION','FORMER_ENSLAVEMENT_OBSERVATION','LANGUAGE_RECOGNITION_OBSERVATION','INTERPRETER_MEDIATED_DIPLOMACY_OBSERVATION','RECIPROCAL_PLEDGE_OBSERVATION','FORMER_ENEMY_ASSISTANCE_OBSERVATION','FORMATION_COUNCIL_OBSERVATION','COMPANY_COLUMN_ARGUMENT_OBSERVATION','HOMERIC_ALLUSION_PARATEXT_OBSERVATION','APPROXIMATE_FORCE_STRUCTURE_OBSERVATION','PRAYER_AND_BATTLE_HYMN_OBSERVATION','ENEMY_EXTENSION_OBSERVATION','MISINTERPRETED_MOVEMENT_OBSERVATION','HONEY_TOXICITY_OBSERVATION','MASS_NONFATAL_DISABLEMENT_OBSERVATION','HELLENIC_COASTAL_CITY_OBSERVATION','RAVAGING_BASE_OBSERVATION','HOSPITALITY_AND_MARKET_OBSERVATION','MEDIATED_COLCHIAN_GIFT_OBSERVATION','VOW_FULFILLMENT_SACRIFICE_OBSERVATION','EXILED_GAME_PRESIDENT_OBSERVATION','CAPTIVE_CHILD_COMPETITOR_OBSERVATION','CRETAN_LONG_RACE_OBSERVATION','MIXED_SPECTATOR_OBSERVATION','STEEP_HORSE_RACE_OBSERVATION','BOOK_TRANSITION_PARATEXT_OBSERVATION','COAST_NOT_TERMINUS_OBSERVATION'}
 if need-types(u):return fail('IV.8 evidence types missing: '+', '.join(sorted(need-types(u))))
 t=' '.join(texts(u))
 for x in ['slave at Athens','recognizes Macrone speech','exchange different lances','cut trees, build the road','columns with intervals','prayer and battle hymn','mistakes enemy redeployment for flight','Honeycomb causes vomiting','no death is reported','thirty-day base for ravaging Colchis','Zeus the Saviour','captive lads','More than sixty Cretans','Male and female companions','more than half tumbling','Book V synopsis']:
  if x not in t:return fail(f'IV.8 phrase safeguard missing: {x}')
 if len(u.get('documentary_observations',[]))!=28 or len(u.get('speeches_deeds_and_outcomes',[]))!=12:return fail('IV.8 record counts mismatch')
 v=docs[30]; b=v.get('bibliographic_and_witness_control',{}).get('chapter_boundary_control','')
 if 'Book V retrospective synopsis' not in b or 'V.1 begins beneath heading I on PDF page 94' not in b or 'V.2 begins on page 96' not in b:return fail('V.1 boundary and paratext control missing')
 need={'BOOK_TRANSITION_PARATEXT_OBSERVATION','MARCH_WEARINESS_OBSERVATION','SEA_RETURN_PREFERENCE_OBSERVATION','ODYSSEAN_ALLUSION_PARATEXT_OBSERVATION','PERSONAL_CONNECTION_PROCUREMENT_OBSERVATION','INSUFFICIENT_MARKET_OBSERVATION','ORGANIZED_FORAGING_OBSERVATION','PILLAGE_REGISTRATION_OBSERVATION','EXPERIENCE_OVERSIGHT_OBSERVATION','APPROPRIATION_ACKNOWLEDGMENT_OBSERVATION','ROTATING_OUTPOST_OBSERVATION','DUAL_TRANSPORT_STRATEGY_OBSERVATION','VESSEL_DETENTION_OBSERVATION','COMMON_FUND_OBSERVATION','FARE_COMPENSATION_OBSERVATION','LAND_ROUTE_REJECTION_OBSERVATION','WITHHELD_VOTE_OBSERVATION','COERCIVE_VOLUNTARINESS_OBSERVATION','TRAPEZUNTINE_GALLEY_OBSERVATION','PERIOECUS_PARATEXT_OBSERVATION','ENTRUSTED_COMMAND_DESERTION_OBSERVATION','PROLEPTIC_PUNISHMENT_REPORT_OBSERVATION','CARGO_REMOVAL_AND_CUSTODY_OBSERVATION','FORAY_FAILURE_AND_COMMAND_DEATH_OBSERVATION'}
 if need-types(v):return fail('V.1 evidence types missing: '+', '.join(sorted(need-types(v))))
 t=' '.join(texts(v))
 for x in ['packing, marching, carrying arms','returning by sea','friendship with Anaxibius','market is insufficient','organized parties to capture provisions','report their intent and direction','appropriated what belongs to them','Regular outposts','guarded with rudders removed','general fund','agreeing a fare','loud protest','voluntarily after pressure','fifty-oared galley','perioecus','leaves Pontus with the entrusted galley','later killing by Nicander','freight is removed and guarded','Cleanetus is killed']:
  if x not in t:return fail(f'V.1 phrase safeguard missing: {x}')
 if len(v.get('documentary_observations',[]))!=24 or len(v.get('speeches_deeds_and_outcomes',[]))!=10:return fail('V.1 record counts mismatch')
 z=docs[31]; b=z.get('bibliographic_and_witness_control',{}).get('chapter_boundary_control','')
 if 'V.2 begins beneath heading II on PDF page 96' not in b or 'ends on PDF page 98' not in b or 'V.3 begins beneath heading III on PDF page 99' not in b:return fail('V.2 boundary control missing')
 need={'PROVISION_RADIUS_FAILURE_OBSERVATION','DIVIDED_FORCE_OBSERVATION','DISPLACED_COLCHIAN_SURVEILLANCE_OBSERVATION','GUIDE_PARTIALITY_OBSERVATION','REPORTED_WARLIKE_SUPERLATIVE_OBSERVATION','DEFENSIVE_SCORCHED_EARTH_OBSERVATION','FORTIFIED_METROPOLIS_OBSERVATION','UNAUTHORIZED_VANGUARD_RUSH_OBSERVATION','APPROXIMATE_STORMING_FORCE_OBSERVATION','SINGLE_FILE_RETREAT_TRAP_OBSERVATION','TRAPPED_FORCE_MESSAGE_OBSERVATION','WITHDRAW_OR_REINFORCE_COUNCIL_OBSERVATION','SACRIFICIAL_FORECAST_OBSERVATION','CAPTAIN_CONFIGURATION_DISCRETION_OBSERVATION','COMPETITIVE_MANLY_VIRTUE_OBSERVATION','MISSILE_READINESS_OBSERVATION','CRESCENT_TERRAIN_FORMATION_OBSERVATION','RITUALIZED_ASSAULT_SIGNAL_OBSERVATION','FIREBRAND_ASSAULT_OBSERVATION','ARMOR_SHEDDING_SCALING_OBSERVATION','PREMATURE_CAPTURE_ASSESSMENT_OBSERVATION','LOOTING_SURGE_OBSERVATION','GATE_RESERVE_OBSERVATION','PLUNDER_PROCLAMATION_AS_REINFORCEMENT_OBSERVATION','INNER_CITADEL_IMPREGNABILITY_OBSERVATION','SELECTIVE_RETREAT_ECHELON_OBSERVATION','DIVINE_ESCAPE_REPORT_OBSERVATION','FORTUNE_LESSON_OBSERVATION','CITY_BURNING_OBSERVATION','FALSE_AMBUSH_OBSERVATION','DECOY_ROUTE_DIVERGENCE_OBSERVATION','WOUNDED_DECOY_RESCUE_OBSERVATION','EDITORIAL_PARATEXT_OBSERVATION'}
 if need-types(z):return fail('V.2 evidence types missing: '+', '.join(sorted(need-types(z))))
 t=' '.join(texts(z))
 for x in ['no longer possible to capture provisions','half the army','Trapezuntines refuse to guide','Drilae are called the most warlike','burn fastnesses','More than two thousand','single-file','Seers announce battle','award of manly virtue','crescent-like','warrior-god','firebrands','taken only','snatch whatever','capture anything','citadel impregnable','some god gives a means of safety','lesson of fortune','city except the citadel','false ambush','Mysus is recovered wounded','Mysus as both a Mysian']:
  if x not in t:return fail(f'V.2 phrase safeguard missing: {x}')
 if len(z.get('documentary_observations',[]))!=33 or len(z.get('speeches_deeds_and_outcomes',[]))!=12:return fail('V.2 record counts mismatch')
 print('Xenophon repository validation passed');return 0
if __name__=='__main__':sys.exit(main())
