from pathlib import Path
import sys,yaml,tempfile,shutil,subprocess,json
R=Path(__file__).resolve().parents[1];P=R/"scripts/validate_repository_v1_42.py";U=R/"studies/xenophon-anabasis-dakyns/units/XEN-PRI-RU-043.yaml";L=R/"studies/xenophon-anabasis-dakyns/reading-plan.yaml";A=R/"audits/founding-state.yaml";H=R/"history/2026-07-31-anabasis-vi6-cleander-submission-chrysopolis.md";B=R/"history/2026-07-31-anabasis-book-vi-draft-completion.md"
def load(p):
 with p.open(encoding="utf-8") as f:return yaml.safe_load(f)
def dump(p,x):
 with p.open("w",encoding="utf-8") as f:yaml.safe_dump(x,f,sort_keys=False,allow_unicode=True)
def fail(x):print(x);return 1
def predecessor():
 if not P.exists():return fail("Frozen v1.42 validator missing")
 with tempfile.TemporaryDirectory() as d:
  t=Path(d)/"r";shutil.copytree(R,t,ignore=shutil.ignore_patterns(".git","__pycache__"))
  m=load(t/"manifest.yaml");m["version"]="1.42.0";s=m["primary_study"];s["drafted_units"]=s["drafted_units"][:-1];s["book_six_drafted_chapters"]=["VI.1","VI.2","VI.3","VI.4","VI.5"];s.pop("book_six_draft_complete_pending_owner_review",None);m["next_required_unit"]={"id":"XEN-PRI-RU-043","description":"Continue the independent primary reconstruction with Anabasis VI.6 using the Dakyns Project Gutenberg witness."};dump(t/"manifest.yaml",m)
  q=load(t/"studies/xenophon-anabasis-dakyns/reading-plan.yaml");q["reading_units"]=q["reading_units"][:-1];q["reading_units"][-1]["status"]="NEXT";q["remaining_sequence"]="Anabasis VII.1 through VII.8, strictly in chapter order.";dump(t/"studies/xenophon-anabasis-dakyns/reading-plan.yaml",q)
  a=load(t/"audits/founding-state.yaml");r=a["repository_state"];r["drafted_primary_units"]=42;r["book_six_drafted_chapters"]=["VI.1","VI.2","VI.3","VI.4","VI.5"];r.pop("book_six_primary_draft_complete",None);a["resolved_items"]=[x for x in a["resolved_items"] if x.get("id")!="RES-008"];a["documented_gaps"][1]["description"]="The primary Anabasis reconstruction remains incomplete; Books I through V are drafted pending owner review, and Book VI has drafted coverage through VI.5.";a["next_required_action"]="Complete XEN-PRI-RU-043 for Anabasis VI.6 without importing secondary interpretation or treating translated wording as unmediated Greek evidence.";dump(t/"audits/founding-state.yaml",a)
  z=subprocess.run([sys.executable,str(t/"scripts/validate_repository_v1_42.py")],cwd=t,text=True,capture_output=True);return fail("predecessor failed: "+(z.stdout+z.stderr).strip()) if z.returncode else 0
def main():
 if predecessor():return 1
 if any(not x.exists() for x in [U,L,A,H,B,P,R/"manifest.yaml"]):return fail("Missing VI.6 or Book VI completion production file")
 m=load(R/"manifest.yaml");p=load(L);a=load(A);u=load(U);ids=[f"XEN-PRI-RU-{n:03d}" for n in range(1,44)];q=p.get("reading_units",[]);s=m.get("primary_study",{});r=a.get("repository_state",{})
 if m.get("version")!="1.43.0" or m.get("state")!="PRIMARY_RECONSTRUCTION_IN_PROGRESS":return fail("Manifest VI.6 mismatch")
 if m.get("artificial_intelligence_self_certification_prohibited") is not True or m.get("minister",{}).get("registration_status")!="NOT_YET_REGISTERED_IN_SANCTUM":return fail("Governance mismatch")
 if s.get("drafted_units")!=ids or s.get("book_six_draft_complete_pending_owner_review") is not True or s.get("book_six_drafted_chapters")!=["VI.1","VI.2","VI.3","VI.4","VI.5","VI.6"] or m.get("next_required_unit",{}).get("id")!="XEN-PRI-RU-044":return fail("Coverage mismatch")
 if [x.get("id") for x in q]!=ids+["XEN-PRI-RU-044"] or q[-2].get("work_locator")!="Anabasis VI.6" or q[-2].get("pdf_pages_one_based")!="132-137" or q[-2].get("status")!="DRAFTED_PENDING_OWNER_REVIEW" or q[-1].get("work_locator")!="Anabasis VII.1" or q[-1].get("pdf_pages_one_based")!="137-143" or q[-1].get("status")!="NEXT":return fail("Plan mismatch")
 if r.get("drafted_primary_units")!=43 or r.get("book_six_primary_draft_complete") is not True or r.get("book_six_drafted_chapters")!=["VI.1","VI.2","VI.3","VI.4","VI.5","VI.6"] or r.get("minister_adapter_derived") is not False or r.get("sanctum_registration_present") is not False:return fail("Audit mismatch")
 if not any(x.get("id")=="RES-008" and "XEN-PRI-RU-038 through XEN-PRI-RU-043" in x.get("description","") for x in a.get("resolved_items",[])):return fail("Book VI milestone audit record missing")
 if u.get("unit_id")!="XEN-PRI-RU-043" or u.get("status")!="DRAFTED_PENDING_OWNER_REVIEW" or u.get("scope",{}).get("pdf_pages_one_based")!="132-137" or u.get("secondary_comparison_status")!="DEFERRED":return fail("Unit mismatch")
 if "Translator wording is not unmediated Greek evidence" not in u.get("jurisdiction",""):return fail("Translation safeguard missing")
 n=u.get("narrative_person_and_authorial_attribution",{})
 if n.get("xenophon_as_character_present") is not True or n.get("first_person_narrator_present") is not False or n.get("direct_authorial_self_identification_present") is not False or n.get("interior_deliberation_report_present") is not True:return fail("Narrative mismatch")
 b=u.get("bibliographic_and_witness_control",{}).get("chapter_boundary_control","")
 for x in ["Heading VI begins VI.6 on PDF page 132","BOOK VII begins on page 137","stops before BOOK VII","Next unit covers pages 137-143"]:
  if x not in b:return fail("Boundary safeguard missing: "+x)
 types={o.get("evidence_type") for o in u.get("documentary_observations",[])}
 need={"ENEMY_HOUSEHOLD_WITHDRAWAL_OBSERVATION","PUBLIC_PRIVATE_BOOTY_RULE_OBSERVATION","MARKET_CITY_RUMOR_OBSERVATION","HOSTILE_ENVOYS_XENOPHON_OBSERVATION","CLEANDER_TWO_WARSHIPS_NO_TRANSPORTS_OBSERVATION","DEXIPPUS_PRIVATE_SHARE_OFFER_OBSERVATION","AGASIAS_RESCUE_STONING_OBSERVATION","CLEANDER_INTERDICT_THREAT_OBSERVATION","SPARTAN_LAND_SEA_HEGEMONY_OBSERVATION","XENOPHON_SELF_SUBMISSION_EXTREME_PENALTY_OBSERVATION","AGASIAS_DENIAL_VOLUNTARY_SURRENDER_OBSERVATION","SCAMP_FAIR_TRIAL_OBSERVATION","RESCUED_MAN_PUBLIC_SHEEP_CLAIM_OBSERVATION","XENOPHON_RELEASE_INTERCESSION_OBSERVATION","THREE_DAY_ADVERSE_SACRIFICE_OBSERVATION","PUBLIC_CATTLE_GIFT_RETURN_OBSERVATION","REVERSE_RAID_OBSERVATION","CHRYSOPOLIS_SIXTH_DAY_SEVEN_DAY_SALE_OBSERVATION"}
 if need-types:return fail("VI.6 evidence types missing: "+", ".join(sorted(need-types)))
 text=" ".join(o.get("observation","") for o in u["documentary_observations"]).casefold()
 for x in ["good things except olives","general expedition is public","a city and harbor are being founded","two warships","no transports","private share","stone dexippus","every hellenic city","lords of hellas on land and sea","extreme penalty","voluntarily surrenders","entitled to a fair trial","sheep were public property","lead if the gods permit","three successive days","accepts and returns","reverses for one day and night","chrysopolis on the sixth day","seven days selling booty"]:
  if x not in text:return fail("VI.6 phrase safeguard missing: "+x)
 if [len(u.get(k,[])) for k in ["documentary_observations","speeches_deeds_and_outcomes","provisional_findings","standing_unresolved_questions","downstream_textual_checks"]]!=[30,10,10,16,12]:return fail("VI.6 counts mismatch")
 if "Strauss" in json.dumps(u,ensure_ascii=False):return fail("Primary unit imports secondary interpretation")
 if "certif" in u.get("status","").casefold():return fail("Unit status improperly certifies")
 h=H.read_text(encoding="utf-8")
 for x in ["PDF pages 132–137","PDF pages 137–143","forty-three drafted primary units","Preserved validator v1.42"]:
  if x not in h:return fail("History safeguard missing: "+x)
 z=B.read_text(encoding="utf-8")
 for x in ["XEN-PRI-RU-038` through `XEN-PRI-RU-043","VI.1 through VI.6","pending owner review","XEN-PRI-RU-044","PDF pages 137–143"]:
  if x not in z:return fail("Book VI completion safeguard missing: "+x)
 print("Xenophon repository validation passed");return 0
if __name__=="__main__":sys.exit(main())
