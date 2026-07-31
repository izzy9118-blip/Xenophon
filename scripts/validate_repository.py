from pathlib import Path
import sys,yaml,tempfile,shutil,subprocess,json
R=Path(__file__).resolve().parents[1];P=R/"scripts/validate_repository_v1_43.py";U=R/"studies/xenophon-anabasis-dakyns/units/XEN-PRI-RU-044.yaml";L=R/"studies/xenophon-anabasis-dakyns/reading-plan.yaml";A=R/"audits/founding-state.yaml";H=R/"history/2026-07-31-anabasis-vii1-byzantine-reentry-refused-seizure.md"
def load(p):
 with p.open(encoding="utf-8") as f:return yaml.safe_load(f)
def dump(p,x):
 with p.open("w",encoding="utf-8") as f:yaml.safe_dump(x,f,sort_keys=False,allow_unicode=True)
def fail(x):print(x);return 1
def predecessor():
 if not P.exists():return fail("Frozen v1.43 validator missing")
 with tempfile.TemporaryDirectory() as d:
  t=Path(d)/"r";shutil.copytree(R,t,ignore=shutil.ignore_patterns(".git","__pycache__"))
  m=load(t/"manifest.yaml");m["version"]="1.43.0";s=m["primary_study"];s["drafted_units"]=s["drafted_units"][:-1];s.pop("book_seven_drafted_chapters",None);m["next_required_unit"]={"id":"XEN-PRI-RU-044","description":"Continue the independent primary reconstruction with Anabasis VII.1 using the Dakyns Project Gutenberg witness."};dump(t/"manifest.yaml",m)
  q=load(t/"studies/xenophon-anabasis-dakyns/reading-plan.yaml");q["reading_units"]=q["reading_units"][:-1];q["reading_units"][-1]["status"]="NEXT";q["reading_units"][-1]["pdf_pages_one_based"]="137-143";q["remaining_sequence"]="Anabasis VII.2 through VII.8, strictly in chapter order.";dump(t/"studies/xenophon-anabasis-dakyns/reading-plan.yaml",q)
  a=load(t/"audits/founding-state.yaml");r=a["repository_state"];r["drafted_primary_units"]=43;r.pop("book_seven_drafted_chapters",None);a["documented_gaps"][1]["description"]="The primary Anabasis reconstruction remains incomplete; Books I through VI are drafted pending owner review, while Book VII has not yet received sequential draft coverage.";a["next_required_action"]="Complete XEN-PRI-RU-044 for Anabasis VII.1 without importing secondary interpretation or treating translated wording as unmediated Greek evidence.";dump(t/"audits/founding-state.yaml",a)
  z=subprocess.run([sys.executable,str(t/"scripts/validate_repository_v1_43.py")],cwd=t,text=True,capture_output=True);return fail("predecessor failed: "+(z.stdout+z.stderr).strip()) if z.returncode else 0
def main():
 if predecessor():return 1
 if any(not x.exists() for x in [U,L,A,H,P,R/"manifest.yaml"]):return fail("Missing VII.1 production file")
 m=load(R/"manifest.yaml");p=load(L);a=load(A);u=load(U);ids=[f"XEN-PRI-RU-{n:03d}" for n in range(1,45)];q=p.get("reading_units",[]);s=m.get("primary_study",{});r=a.get("repository_state",{})
 if m.get("version")!="1.44.0" or m.get("state")!="PRIMARY_RECONSTRUCTION_IN_PROGRESS":return fail("Manifest VII.1 mismatch")
 if m.get("artificial_intelligence_self_certification_prohibited") is not True or m.get("minister",{}).get("registration_status")!="NOT_YET_REGISTERED_IN_SANCTUM":return fail("Governance mismatch")
 if s.get("drafted_units")!=ids or s.get("book_six_draft_complete_pending_owner_review") is not True or s.get("book_seven_drafted_chapters")!=["VII.1"] or m.get("next_required_unit",{}).get("id")!="XEN-PRI-RU-045":return fail("Coverage mismatch")
 if [x.get("id") for x in q]!=ids+["XEN-PRI-RU-045"] or q[-2].get("work_locator")!="Anabasis VII.1" or q[-2].get("pdf_pages_one_based")!="137-141" or q[-2].get("status")!="DRAFTED_PENDING_OWNER_REVIEW" or q[-1].get("work_locator")!="Anabasis VII.2" or q[-1].get("pdf_pages_one_based")!="141-145" or q[-1].get("status")!="NEXT":return fail("Plan mismatch")
 if r.get("drafted_primary_units")!=44 or r.get("book_six_primary_draft_complete") is not True or r.get("book_seven_drafted_chapters")!=["VII.1"] or r.get("minister_adapter_derived") is not False or r.get("sanctum_registration_present") is not False:return fail("Audit mismatch")
 if u.get("unit_id")!="XEN-PRI-RU-044" or u.get("status")!="DRAFTED_PENDING_OWNER_REVIEW" or u.get("scope",{}).get("pdf_pages_one_based")!="137-141" or u.get("secondary_comparison_status")!="DEFERRED":return fail("Unit mismatch")
 if "Translator wording is not unmediated Greek evidence" not in u.get("jurisdiction",""):return fail("Translation safeguard missing")
 n=u.get("narrative_person_and_authorial_attribution",{})
 if n.get("xenophon_as_character_present") is not True or n.get("first_person_narrator_present") is not False or n.get("direct_authorial_self_identification_present") is not False or n.get("interior_deliberation_report_present") is not True:return fail("Narrative mismatch")
 b=u.get("bibliographic_and_witness_control",{}).get("chapter_boundary_control","")
 for x in ["BOOK VII and heading I begin VII.1 on PDF page 137","heading II begins on page 141","stops before heading II","earlier provisional plan range 137-143 is corrected forward","Next unit covers pages 141-145"]:
  if x not in b:return fail("Boundary safeguard missing: "+x)
 types={o.get("evidence_type") for o in u.get("documentary_observations",[])}
 need={"BOOK_SEVEN_VII1_BOUNDARY_CORRECTION_OBSERVATION","PHARNABAZUS_ANAXIBIUS_REMOVAL_OBSERVATION","PAY_PROMISE_CROSSING_OBSERVATION","NO_PERSONAL_OBLIGATION_CROSSING_OBSERVATION","PAY_WITHHELD_EXPULSION_OBSERVATION","ETEONICUS_GATE_CLOSURE_OBSERVATION","FORCED_REENTRY_THREE_ROUTES_OBSERVATION","XENOPHON_ALARM_PILLAGE_OBSERVATION","CITY_TRIREMES_MONEY_MEN_OFFER_OBSERVATION","TACTICAL_ASSENT_FORMATION_OBSERVATION","EIGHT_DEEP_SELF_MARSHALLING_OBSERVATION","ATHENIAN_DEFEAT_ARGUMENT_OBSERVATION","ALL_GREECE_WAR_WARNING_OBSERVATION","INNOCENT_CITY_DISTINCTION_OBSERVATION","TEN_THOUSAND_FATHOMS_PRAYER_OBSERVATION","HELLENIC_OBEDIENCE_JUST_RIGHTS_OBSERVATION","ANAXIBIUS_SALE_PROCLAMATION_OBSERVATION","COERATADAS_SACRIFICE_PROVISION_FAILURE_OBSERVATION"}
 if need-types:return fail("VII.1 evidence types missing: "+", ".join(sorted(need-types)))
 text=" ".join(o.get("observation","") for o in u["documentary_observations"]).casefold()
 for x in ["correcting the earlier provisional 137-143 range to 137-141","should not lack pay","already intends to cross","clean sweep","thrusts in the bolt pin","jaws of their enemies","by battering the gates","incurable harm","city, triremes, money, and men","outwardly tells them to form up","eight deep","three hundred line-of-battle ships","war with sparta","innocent city","first hellenic city","ten thousand fathoms","head of hellas","knocked down to the hammer and sold","twenty barleymeal bearers","less than one day's provisions"]:
  if x not in text:return fail("VII.1 phrase safeguard missing: "+x)
 if [len(u.get(k,[])) for k in ["documentary_observations","speeches_deeds_and_outcomes","provisional_findings","standing_unresolved_questions","downstream_textual_checks"]]!=[30,10,10,16,12]:return fail("VII.1 counts mismatch")
 if "Strauss" in json.dumps(u,ensure_ascii=False):return fail("Primary unit imports secondary interpretation")
 if "certif" in u.get("status","").casefold():return fail("Unit status improperly certifies")
 h=H.read_text(encoding="utf-8")
 for x in ["PDF pages 137–141","PDF pages 141–145","137–143 was provisional and inaccurate","forty-four","Preserved validator v1.43","XEN-PRI-RU-045"]:
  if x not in h:return fail("History safeguard missing: "+x)
 print("Xenophon repository validation passed");return 0
if __name__=="__main__":sys.exit(main())
