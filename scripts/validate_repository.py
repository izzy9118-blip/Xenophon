from pathlib import Path
import sys,yaml,tempfile,shutil,subprocess,json
R=Path(__file__).resolve().parents[1];P=R/"scripts/validate_repository_v1_50.py";U=R/"studies/xenophon-anabasis-dakyns/units/XEN-PRI-RU-051.yaml";L=R/"studies/xenophon-anabasis-dakyns/reading-plan.yaml";A=R/"audits/founding-state.yaml";H=R/"history/2026-07-31-anabasis-vii8-poverty-sacrifice-asidates-thibron.md";B=R/"history/2026-07-31-anabasis-book-vii-draft-completion.md";C=R/"history/2026-07-31-anabasis-primary-sequential-draft-completion.md"
def load(p):
 with p.open(encoding="utf-8") as f:return yaml.safe_load(f)
def dump(p,x):
 with p.open("w",encoding="utf-8") as f:yaml.safe_dump(x,f,sort_keys=False,allow_unicode=True)
def fail(x):print(x);return 1
def predecessor():
 if not P.exists():return fail("Frozen v1.50 validator missing")
 with tempfile.TemporaryDirectory() as d:
  t=Path(d)/"r";shutil.copytree(R,t,ignore=shutil.ignore_patterns(".git","__pycache__"))
  for p in [t/"studies/xenophon-anabasis-dakyns/units/XEN-PRI-RU-051.yaml",t/"history/2026-07-31-anabasis-vii8-poverty-sacrifice-asidates-thibron.md",t/"history/2026-07-31-anabasis-book-vii-draft-completion.md",t/"history/2026-07-31-anabasis-primary-sequential-draft-completion.md"]:
   if p.exists():p.unlink()
  m=load(t/"manifest.yaml");m["version"]="1.50.0";m["state"]="PRIMARY_RECONSTRUCTION_IN_PROGRESS";m["current_phase"]["completion_status"]="IN_PROGRESS";s=m["primary_study"];s["status"]="SEQUENTIAL_PRIMARY_READING_IN_PROGRESS_PENDING_OWNER_REVIEW";s["drafted_units"]=s["drafted_units"][:-1];s["book_seven_drafted_chapters"]=[f"VII.{i}" for i in range(1,8)];s.pop("book_seven_draft_complete_pending_owner_review",None);s.pop("all_books_draft_complete_pending_owner_review",None);m["next_required_unit"]={"id":"XEN-PRI-RU-051","description":"Complete the independent primary reconstruction with Anabasis VII.8 using the Dakyns Project Gutenberg witness."};m.pop("next_required_action",None);dump(t/"manifest.yaml",m)
  q=load(t/"studies/xenophon-anabasis-dakyns/reading-plan.yaml");q["status"]="SEQUENTIAL_PRIMARY_READING_IN_PROGRESS_PENDING_OWNER_REVIEW";q.pop("completion_status",None);q["reading_units"][-1]["status"]="NEXT";q["remaining_sequence"]="Anabasis VII.8, strictly in chapter order.";q["comparison_gate"]={"strauss_comparison":"DEFERRED","rule":"Primary sequence first."};dump(t/"studies/xenophon-anabasis-dakyns/reading-plan.yaml",q)
  a=load(t/"audits/founding-state.yaml");r=a["repository_state"];r["drafted_primary_units"]=50;r["book_seven_drafted_chapters"]=[f"VII.{i}" for i in range(1,8)];r.pop("book_seven_primary_draft_complete",None);r.pop("primary_sequential_draft_complete",None);a["resolved_items"]=a["resolved_items"][:8];a["documented_gaps"][1]={"id":"GAP-005","description":"The primary Anabasis reconstruction remains incomplete; Books I through VI are drafted pending owner review, and Book VII has drafted coverage through VII.7.","blocks":["complete primary argument map","systematic deed extraction","speech-register derivation","operational capacity derivation"]};a["next_required_action"]="Complete XEN-PRI-RU-051 for Anabasis VII.8 without importing secondary interpretation or treating translated wording as unmediated Greek evidence.";dump(t/"audits/founding-state.yaml",a)
  z=subprocess.run([sys.executable,str(t/"scripts/validate_repository_v1_50.py")],cwd=t,text=True,capture_output=True);return fail("predecessor failed: "+(z.stdout+z.stderr).strip()) if z.returncode else 0
def main():
 if predecessor():return 1
 if any(not x.exists() for x in [U,L,A,H,B,C,P,R/"manifest.yaml"]):return fail("Missing VII.8 completion production file")
 m=load(R/"manifest.yaml");p=load(L);a=load(A);u=load(U);ids=[f"XEN-PRI-RU-{n:03d}" for n in range(1,52)];q=p.get("reading_units",[]);s=m.get("primary_study",{});r=a.get("repository_state",{})
 if m.get("version")!="1.51.0" or m.get("state")!="PRIMARY_RECONSTRUCTION_DRAFT_COMPLETE_PENDING_OWNER_REVIEW" or m.get("current_phase",{}).get("completion_status")!="DRAFT_COMPLETE_PENDING_OWNER_REVIEW":return fail("Manifest completion mismatch")
 if m.get("artificial_intelligence_self_certification_prohibited") is not True or m.get("minister",{}).get("registration_status")!="NOT_YET_REGISTERED_IN_SANCTUM":return fail("Governance mismatch")
 if s.get("drafted_units")!=ids or s.get("book_seven_drafted_chapters")!=[f"VII.{i}" for i in range(1,9)] or s.get("book_seven_draft_complete_pending_owner_review") is not True or s.get("all_books_draft_complete_pending_owner_review") is not True:return fail("Primary completion mismatch")
 if m.get("next_required_unit") is not None or m.get("next_required_action",{}).get("id")!="XEN-PRIMARY-OWNER-REVIEW-001":return fail("Next action mismatch")
 if [x.get("id") for x in q]!=ids or any(x.get("status")!="DRAFTED_PENDING_OWNER_REVIEW" for x in q) or q[-1].get("work_locator")!="Anabasis VII.8" or q[-1].get("pdf_pages_one_based")!="164-168" or p.get("completion_status")!="DRAFT_COMPLETE_PENDING_OWNER_REVIEW":return fail("Plan completion mismatch")
 if "None. All fifty-one numbered chapters" not in p.get("remaining_sequence","") or p.get("comparison_gate",{}).get("strauss_comparison")!="DEFERRED":return fail("Plan gate mismatch")
 if r.get("drafted_primary_units")!=51 or r.get("book_seven_primary_draft_complete") is not True or r.get("primary_sequential_draft_complete") is not True or r.get("book_seven_drafted_chapters")!=[f"VII.{i}" for i in range(1,9)] or r.get("minister_adapter_derived") is not False or r.get("sanctum_registration_present") is not False:return fail("Audit completion mismatch")
 if [x.get("id") for x in a.get("resolved_items",[])[-2:]]!=["RES-009","RES-010"] or "owner review" not in a.get("documented_gaps",[])[1].get("description","").casefold():return fail("Audit milestone mismatch")
 if u.get("unit_id")!="XEN-PRI-RU-051" or u.get("status")!="DRAFTED_PENDING_OWNER_REVIEW" or u.get("scope",{}).get("pdf_pages_one_based")!="164-168" or u.get("secondary_comparison_status")!="DEFERRED":return fail("Unit mismatch")
 if "Translator wording is not unmediated Greek evidence" not in u.get("jurisdiction",""):return fail("Translation safeguard missing")
 n=u.get("narrative_person_and_authorial_attribution",{})
 if n.get("xenophon_as_character_present") is not True or n.get("first_person_narrator_present") is not False or n.get("direct_authorial_self_identification_present") is not False or n.get("interior_deliberation_report_present") is not True:return fail("Narrative mismatch")
 b=u.get("bibliographic_and_witness_control",{}).get("chapter_boundary_control","")
 for x in ["Heading VIII begins VII.8 on PDF page 164","covers pages 164-168","No subsequent numbered chapter follows","manuscript governor list","paratextual apparatus"]:
  if x not in b:return fail("Boundary safeguard missing: "+x)
 types={o.get("evidence_type") for o in u.get("documentary_observations",[])}
 need={"BOOK_SEVEN_VII8_FINAL_BOUNDARY_OBSERVATION","LAMPSACUS_EUCLEIDES_SAFE_RETURN_OBSERVATION","XENOPHON_BARELY_ENOUGH_HOME_OBSERVATION","EUCLEIDES_DISBELIEF_APOLLO_VICTIMS_OBSERVATION","XENOPHON_SELF_OBSTACLE_OBSERVATION","ZEUS_MEILICHIOS_NEGLECT_OBSERVATION","NO_SACRIFICE_SINCE_ABROAD_OBSERVATION","OPHRYNIUM_FAMILY_HOLOCAUST_OBSERVATION","BION_NAUSICLEIDES_GIFTS_OBSERVATION","FIFTY_DARIC_HORSE_RESTORATION_OBSERVATION","TROAD_IDA_MYSIA_PERGAMUS_ROUTE_OBSERVATION","HELLAS_GONGYLUS_HOSPITALITY_OBSERVATION","ASIDATES_THIRTY_MAN_NIGHT_PROPOSAL_OBSERVATION","COUSIN_DAPHNAGORAS_GUIDES_OBSERVATION","BASIAS_PROMISING_VICTIMS_EASY_PREY_OBSERVATION","STAUNCHEST_FRIENDS_GOOD_TURN_OBSERVATION","SIX_HUNDRED_VOLUNTEERS_EXCLUDED_OBSERVATION","ASIDATES_TOWER_ASSAULT_FAILURE_OBSERVATION","EIGHT_BRICK_WALL_OX_SPIT_OBSERVATION","BEACONS_RELIEF_FORCES_OBSERVATION","HOLLOW_SQUARE_RETREAT_PROPERTY_OBSERVATION","GONGYLUS_PROCLES_RESCUE_OBSERVATION","CURVED_SHIELD_RETREAT_CARCASUS_OBSERVATION","HALF_WOUNDED_AGASIAS_OBSERVATION","TWO_HUNDRED_CAPTIVES_SACRIFICE_SHEEP_OBSERVATION","SECOND_SACRIFICE_WHOLE_ARMY_DECEPTION_OBSERVATION","ASIDATES_LEAVES_TOWER_PARTHENIUM_OBSERVATION","ASIDATES_HOUSEHOLD_PROPERTY_CAPTURE_OBSERVATION","EARLIER_VICTIMS_LITERAL_FULFILLMENT_OBSERVATION","COLLECTIVE_REWARD_THIBRON_TRANSFER_OBSERVATION"}
 if need-types:return fail("VII.8 evidence types missing: "+", ".join(sorted(need-types)))
 text=" ".join(o.get("observation","") for o in u["documentary_observations"]).casefold()
 for x in ["lampsacus","eucleides","barely has enough to get home","apollo sacrifice","xenophon himself","zeus meilichios","not sacrificed","holocaust of swine","bion and nausicleides","fifty darics","mount ida","pergamus","thirty men","daphnagoras","easy prey","staunchest officer-friends","six hundred","high, solid","eight-clay-brick wall","ox-spit","shouts and beacons","hollow square","gongylus and procles","carcasus","nearly half","agasias","two hundred captives","whole army by night","parthenium","wife, children, horses","literally fulfilled","first choice","thibron"]:
  if x not in text:return fail("VII.8 phrase safeguard missing: "+x)
 if [len(u.get(k,[])) for k in ["documentary_observations","speeches_deeds_and_outcomes","provisional_findings","standing_unresolved_questions","downstream_textual_checks"]]!=[30,10,10,16,12]:return fail("VII.8 counts mismatch")
 if "Strauss" in json.dumps(u,ensure_ascii=False):return fail("Primary unit imports secondary interpretation")
 if "certif" in u.get("status","").casefold():return fail("Unit status improperly certifies")
 for path,phrases in [(H,["PDF pages 164–168","Fifty-one drafted primary units","Preserved validator v1.50","owner review"]),(B,["XEN-PRI-RU-051","DRAFT_COMPLETE_PENDING_OWNER_REVIEW","all seven books"]),(C,["fifty-one numbered chapters","Total: 51 drafted primary units","primary-only cumulative register"])]:
  textx=path.read_text(encoding="utf-8")
  for x in phrases:
   if x not in textx:return fail("History safeguard missing: "+x)
 print("Xenophon repository validation passed");return 0
if __name__=="__main__":sys.exit(main())
