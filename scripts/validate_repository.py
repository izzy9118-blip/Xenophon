from pathlib import Path
import sys,yaml,tempfile,shutil,subprocess,json
R=Path(__file__).resolve().parents[1];P=R/"scripts/validate_repository_v1_49.py";U=R/"studies/xenophon-anabasis-dakyns/units/XEN-PRI-RU-050.yaml";L=R/"studies/xenophon-anabasis-dakyns/reading-plan.yaml";A=R/"audits/founding-state.yaml";H=R/"history/2026-07-31-anabasis-vii7-medosades-pay-settlement-transfer.md"
def load(p):
 with p.open(encoding="utf-8") as f:return yaml.safe_load(f)
def dump(p,x):
 with p.open("w",encoding="utf-8") as f:yaml.safe_dump(x,f,sort_keys=False,allow_unicode=True)
def fail(x):print(x);return 1
def predecessor():
 if not P.exists():return fail("Frozen v1.49 validator missing")
 with tempfile.TemporaryDirectory() as d:
  t=Path(d)/"r";shutil.copytree(R,t,ignore=shutil.ignore_patterns(".git","__pycache__"))
  m=load(t/"manifest.yaml");m["version"]="1.49.0";s=m["primary_study"];s["drafted_units"]=s["drafted_units"][:-1];s["book_seven_drafted_chapters"]=["VII.1","VII.2","VII.3","VII.4","VII.5","VII.6"];m["next_required_unit"]={"id":"XEN-PRI-RU-050","description":"Continue the independent primary reconstruction with Anabasis VII.7 using the Dakyns Project Gutenberg witness."};dump(t/"manifest.yaml",m)
  q=load(t/"studies/xenophon-anabasis-dakyns/reading-plan.yaml");q["reading_units"]=q["reading_units"][:-1];q["reading_units"][-1]["status"]="NEXT";q["remaining_sequence"]="Anabasis VII.8, strictly in chapter order.";dump(t/"studies/xenophon-anabasis-dakyns/reading-plan.yaml",q)
  a=load(t/"audits/founding-state.yaml");r=a["repository_state"];r["drafted_primary_units"]=49;r["book_seven_drafted_chapters"]=["VII.1","VII.2","VII.3","VII.4","VII.5","VII.6"];a["documented_gaps"][1]["description"]="The primary Anabasis reconstruction remains incomplete; Books I through VI are drafted pending owner review, and Book VII has drafted coverage through VII.6.";a["next_required_action"]="Complete XEN-PRI-RU-050 for Anabasis VII.7 without importing secondary interpretation or treating translated wording as unmediated Greek evidence.";dump(t/"audits/founding-state.yaml",a)
  z=subprocess.run([sys.executable,str(t/"scripts/validate_repository_v1_49.py")],cwd=t,text=True,capture_output=True);return fail("predecessor failed: "+(z.stdout+z.stderr).strip()) if z.returncode else 0
def main():
 if predecessor():return 1
 if any(not x.exists() for x in [U,L,A,H,P,R/"manifest.yaml"]):return fail("Missing VII.7 production file")
 m=load(R/"manifest.yaml");p=load(L);a=load(A);u=load(U);ids=[f"XEN-PRI-RU-{n:03d}" for n in range(1,51)];q=p.get("reading_units",[]);s=m.get("primary_study",{});r=a.get("repository_state",{})
 if m.get("version")!="1.50.0" or m.get("state")!="PRIMARY_RECONSTRUCTION_IN_PROGRESS":return fail("Manifest VII.7 mismatch")
 if m.get("artificial_intelligence_self_certification_prohibited") is not True or m.get("minister",{}).get("registration_status")!="NOT_YET_REGISTERED_IN_SANCTUM":return fail("Governance mismatch")
 if s.get("drafted_units")!=ids or s.get("book_seven_drafted_chapters")!=["VII.1","VII.2","VII.3","VII.4","VII.5","VII.6","VII.7"] or m.get("next_required_unit",{}).get("id")!="XEN-PRI-RU-051":return fail("Coverage mismatch")
 if [x.get("id") for x in q]!=ids+["XEN-PRI-RU-051"] or q[-2].get("work_locator")!="Anabasis VII.7" or q[-2].get("pdf_pages_one_based")!="159-164" or q[-2].get("status")!="DRAFTED_PENDING_OWNER_REVIEW" or q[-1].get("work_locator")!="Anabasis VII.8" or q[-1].get("pdf_pages_one_based")!="164-168" or q[-1].get("status")!="NEXT":return fail("Plan mismatch")
 if r.get("drafted_primary_units")!=50 or r.get("book_seven_drafted_chapters")!=["VII.1","VII.2","VII.3","VII.4","VII.5","VII.6","VII.7"] or r.get("minister_adapter_derived") is not False or r.get("sanctum_registration_present") is not False:return fail("Audit mismatch")
 if u.get("unit_id")!="XEN-PRI-RU-050" or u.get("status")!="DRAFTED_PENDING_OWNER_REVIEW" or u.get("scope",{}).get("pdf_pages_one_based")!="159-164" or u.get("secondary_comparison_status")!="DEFERRED":return fail("Unit mismatch")
 if "Translator wording is not unmediated Greek evidence" not in u.get("jurisdiction",""):return fail("Translation safeguard missing")
 n=u.get("narrative_person_and_authorial_attribution",{})
 if n.get("xenophon_as_character_present") is not True or n.get("first_person_narrator_present") is not False or n.get("direct_authorial_self_identification_present") is not False or n.get("interior_deliberation_report_present") is not True:return fail("Narrative mismatch")
 b=u.get("bibliographic_and_witness_control",{}).get("chapter_boundary_control","")
 for x in ["Heading VII begins VII.7 on PDF page 159","heading VIII begins VII.8 on page 164","stops before heading VIII","VII.8 continues from page 164 through the end","next unit covers pages 164-168"]:
  if x not in b:return fail("Boundary safeguard missing: "+x)
 types={o.get("evidence_type") for o in u.get("documentary_observations",[])}
 need={"BOOK_SEVEN_VII7_BOUNDARY_OBSERVATION","SEUTHES_DISTANCE_HELLENIC_VILLAGES_OBSERVATION","MEDOSADES_GRANTED_VILLAGES_PROPERTY_OBSERVATION","ODRYSIAN_THIRTY_HORSEMEN_CHALLENGE_OBSERVATION","PILLAGE_EVACUATION_ENEMY_THREAT_OBSERVATION","PREALLIANCE_FREE_RUN_PILLAGE_BURN_OBSERVATION","GREEK_CONQUEST_DIVINE_HELP_GIFT_OBSERVATION","XENOPHON_NO_LONGER_COMMAND_SPARTANS_OBSERVATION","ODRYSIAN_SHAME_BENEFACTOR_WITHDRAWAL_OBSERVATION","SPARTAN_SUMMONS_PAY_RECOVERY_OBSERVATION","NO_DEPARTURE_UNTIL_DUES_OBSERVATION","OATHBREAKER_PUNISHMENT_WARNING_OBSERVATION","LOCAL_BALLOT_WHO_LEAVES_OBSERVATION","MEDOSADES_REJECTS_BALLOT_NO_BURNING_OBSERVATION","SERVICEABLE_STAFF_SEUTHES_EMBASSY_OBSERVATION","PAYMENT_SEUTHES_INTEREST_BENEFACTOR_OBSERVATION","SIX_THOUSAND_REPUTATION_WORD_POWER_OBSERVATION","THIRTY_TALENTS_CREDIT_KINGDOM_OBSERVATION","FORCED_SUBJECTS_LIBERTY_PROTECTORS_OBSERVATION","PAY_DEBT_VERSUS_NEW_ARMY_COST_OBSERVATION","YEARLY_INCOME_CAPACITY_OBSERVATION","NO_PRIVATE_GAIN_COLLECTIVE_PAYMENT_OATH_OBSERVATION","VALOUR_JUSTICE_GENEROSITY_PRINCE_OBSERVATION","SEUTHES_REPAYMENT_RETENTION_MIXED_SETTLEMENT_OBSERVATION","FRACTION_DISTRIBUTION_VENDOR_BLAME_THIBRON_OBSERVATION"}
 if need-types:return fail("VII.7 evidence types missing: "+", ".join(sorted(need-types)))
 text=" ".join(o.get("observation","") for o in u["documentary_observations"]).casefold()
 for x in ["road to the sea","given by seuthes to medosades","about thirty mounted troopers","character can be relied upon","retaliation as foes","pillaging and burning","by god's help","back is turned","no longer in command","sinks under the earth for shame","four or five horsemen","recover the army's pay","received their dues","broke oaths","decide by ballot","not be burned","serviceable staff","ungrateful separation","six thousand men","word can achieve","thirty talents","desire liberty","greater cost","yearly income","took nothing privately","valour, justice, and generosity","one talent","six hundred cattle","four thousand sheep","one hundred twenty slaves","official vendors","conduct the army to thibron"]:
  if x not in text:return fail("VII.7 phrase safeguard missing: "+x)
 if [len(u.get(k,[])) for k in ["documentary_observations","speeches_deeds_and_outcomes","provisional_findings","standing_unresolved_questions","downstream_textual_checks"]]!=[30,10,10,16,12]:return fail("VII.7 counts mismatch")
 if "Strauss" in json.dumps(u,ensure_ascii=False):return fail("Primary unit imports secondary interpretation")
 if "certif" in u.get("status","").casefold():return fail("Unit status improperly certifies")
 h=H.read_text(encoding="utf-8")
 for x in ["PDF pages 159–164","PDF pages 164–168","Fifty drafted primary units","Preserved validator v1.49","XEN-PRI-RU-051"]:
  if x not in h:return fail("History safeguard missing: "+x)
 print("Xenophon repository validation passed");return 0
if __name__=="__main__":sys.exit(main())
