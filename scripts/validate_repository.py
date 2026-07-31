from pathlib import Path
import sys,yaml,tempfile,shutil,subprocess,json
R=Path(__file__).resolve().parents[1];P=R/"scripts/validate_repository_v1_47.py";U=R/"studies/xenophon-anabasis-dakyns/units/XEN-PRI-RU-048.yaml";L=R/"studies/xenophon-anabasis-dakyns/reading-plan.yaml";A=R/"audits/founding-state.yaml";H=R/"history/2026-07-31-anabasis-vii5-deficient-pay-calumny-salmydessus.md"
def load(p):
 with p.open(encoding="utf-8") as f:return yaml.safe_load(f)
def dump(p,x):
 with p.open("w",encoding="utf-8") as f:yaml.safe_dump(x,f,sort_keys=False,allow_unicode=True)
def fail(x):print(x);return 1
def predecessor():
 if not P.exists():return fail("Frozen v1.47 validator missing")
 with tempfile.TemporaryDirectory() as d:
  t=Path(d)/"r";shutil.copytree(R,t,ignore=shutil.ignore_patterns(".git","__pycache__"))
  m=load(t/"manifest.yaml");m["version"]="1.47.0";s=m["primary_study"];s["drafted_units"]=s["drafted_units"][:-1];s["book_seven_drafted_chapters"]=["VII.1","VII.2","VII.3","VII.4"];m["next_required_unit"]={"id":"XEN-PRI-RU-048","description":"Continue the independent primary reconstruction with Anabasis VII.5 using the Dakyns Project Gutenberg witness."};dump(t/"manifest.yaml",m)
  q=load(t/"studies/xenophon-anabasis-dakyns/reading-plan.yaml");q["reading_units"]=q["reading_units"][:-1];q["reading_units"][-1]["status"]="NEXT";q["remaining_sequence"]="Anabasis VII.6 through VII.8, strictly in chapter order.";dump(t/"studies/xenophon-anabasis-dakyns/reading-plan.yaml",q)
  a=load(t/"audits/founding-state.yaml");r=a["repository_state"];r["drafted_primary_units"]=47;r["book_seven_drafted_chapters"]=["VII.1","VII.2","VII.3","VII.4"];a["documented_gaps"][1]["description"]="The primary Anabasis reconstruction remains incomplete; Books I through VI are drafted pending owner review, and Book VII has drafted coverage through VII.4.";a["next_required_action"]="Complete XEN-PRI-RU-048 for Anabasis VII.5 without importing secondary interpretation or treating translated wording as unmediated Greek evidence.";dump(t/"audits/founding-state.yaml",a)
  z=subprocess.run([sys.executable,str(t/"scripts/validate_repository_v1_47.py")],cwd=t,text=True,capture_output=True);return fail("predecessor failed: "+(z.stdout+z.stderr).strip()) if z.returncode else 0
def main():
 if predecessor():return 1
 if any(not x.exists() for x in [U,L,A,H,P,R/"manifest.yaml"]):return fail("Missing VII.5 production file")
 m=load(R/"manifest.yaml");p=load(L);a=load(A);u=load(U);ids=[f"XEN-PRI-RU-{n:03d}" for n in range(1,49)];q=p.get("reading_units",[]);s=m.get("primary_study",{});r=a.get("repository_state",{})
 if m.get("version")!="1.48.0" or m.get("state")!="PRIMARY_RECONSTRUCTION_IN_PROGRESS":return fail("Manifest VII.5 mismatch")
 if m.get("artificial_intelligence_self_certification_prohibited") is not True or m.get("minister",{}).get("registration_status")!="NOT_YET_REGISTERED_IN_SANCTUM":return fail("Governance mismatch")
 if s.get("drafted_units")!=ids or s.get("book_seven_drafted_chapters")!=["VII.1","VII.2","VII.3","VII.4","VII.5"] or m.get("next_required_unit",{}).get("id")!="XEN-PRI-RU-049":return fail("Coverage mismatch")
 if [x.get("id") for x in q]!=ids+["XEN-PRI-RU-049"] or q[-2].get("work_locator")!="Anabasis VII.5" or q[-2].get("pdf_pages_one_based")!="153-155" or q[-2].get("status")!="DRAFTED_PENDING_OWNER_REVIEW" or q[-1].get("work_locator")!="Anabasis VII.6" or q[-1].get("pdf_pages_one_based")!="155-159" or q[-1].get("status")!="NEXT":return fail("Plan mismatch")
 if r.get("drafted_primary_units")!=48 or r.get("book_seven_drafted_chapters")!=["VII.1","VII.2","VII.3","VII.4","VII.5"] or r.get("minister_adapter_derived") is not False or r.get("sanctum_registration_present") is not False:return fail("Audit mismatch")
 if u.get("unit_id")!="XEN-PRI-RU-048" or u.get("status")!="DRAFTED_PENDING_OWNER_REVIEW" or u.get("scope",{}).get("pdf_pages_one_based")!="153-155" or u.get("secondary_comparison_status")!="DEFERRED":return fail("Unit mismatch")
 if "Translator wording is not unmediated Greek evidence" not in u.get("jurisdiction",""):return fail("Translation safeguard missing")
 n=u.get("narrative_person_and_authorial_attribution",{})
 if n.get("xenophon_as_character_present") is not True or n.get("first_person_narrator_present") is not False or n.get("direct_authorial_self_identification_present") is not False or n.get("interior_deliberation_report_present") is not True:return fail("Narrative mismatch")
 b=u.get("bibliographic_and_witness_control",{}).get("chapter_boundary_control","")
 for x in ["Heading V begins VII.5 on PDF page 153","heading VI begins VII.6 on page 155","stops before heading VI","Heading VII begins on page 159","next unit covers pages 155-159"]:
  if x not in b:return fail("Boundary safeguard missing: "+x)
 types={o.get("evidence_type") for o in u.get("documentary_observations",[])}
 need={"BOOK_SEVEN_VII5_BOUNDARY_OBSERVATION","DELTA_TERES_TERRITORY_OBSERVATION","HERACLEIDES_SPOIL_PROCEEDS_RETURN_OBSERVATION","THREE_MULE_TEAMS_OX_TEAMS_OBSERVATION","XENOPHON_DEFERS_PERSONAL_SHARE_OBSERVATION","COMMANDER_OFFICER_GIFT_REDISTRIBUTION_OBSERVATION","MONTH_DUE_TWENTY_DAYS_PAYMENT_OBSERVATION","HERACLEIDES_TRAFFICKING_ACCOUNT_OBSERVATION","XENOPHON_FULL_PAY_LOAN_COAT_REBUKE_OBSERVATION","HERACLEIDES_FRIENDSHIP_FEAR_OBSERVATION","HERACLEIDES_CALUMNY_OBSERVATION","SOLDIERS_PAY_BLAME_XENOPHON_OBSERVATION","SEUTHES_VEXED_PAY_ADVOCACY_OBSERVATION","BISANTHE_GANOS_NEONTICHOS_PROMISE_OBSERVATION","FORTIFIED_TOWNS_PROMISE_SILENCE_OBSERVATION","XENOPHON_FURTHER_MARCH_DELIBERATION_OBSERVATION","OTHER_GENERALS_SUBSTITUTION_ATTEMPT_OBSERVATION","TWO_MONTHS_PAY_PROMISE_OBSERVATION","TIMASION_FIVE_MONTHS_REFUSAL_OBSERVATION","PHRYNISCUS_CLEANOR_CONCURRENCE_OBSERVATION","SEUTHES_HERACLEIDES_REBUKE_OBSERVATION","XENOPHON_ALL_COMMANDERS_PRESENT_OBSERVATION","JOINT_CONSENT_CONTINUED_CAMPAIGN_OBSERVATION","MILLET_EATING_THRACIANS_SALMYDESSUS_OBSERVATION","SALMYDESSUS_WRECKING_BOUNDARIES_OBSERVATION","WRECKER_FEUD_BOOKS_TREASURE_OBSERVATION","SEUTHES_ARMY_OUTGROWS_HELLENES_OBSERVATION","SELYBRIA_NONPAYMENT_AVOIDED_ACCESS_OBSERVATION"}
 if need-types:return fail("VII.5 evidence types missing: "+", ".join(sorted(need-types)))
 text=" ".join(o.get("observation","") for o in u["documentary_observations"]).casefold()
 for x in ["delta","teres the odrysian","proceeds of the spoil","three pairs of mules","receive his own share another time","timasion, cleanor, and phryniscus","twenty days' pay","trafficking in the spoil","raised a loan","coat off his own back","ousted from seuthes's friendship","calumniate xenophon","where their pay is","persistently demanding","bisanthe, ganos, and neontichos","fortified towns","marching farther","equally able to lead","full pay for two months","five months' pay","phryniscus and cleanor","upbraids heracleides","all generals and officers","joint consent","millet-eating thracians","salmydessus","flotsam and jetsam","written books","considerably larger","not a penny more","want of leisure"]:
  if x not in text:return fail("VII.5 phrase safeguard missing: "+x)
 if [len(u.get(k,[])) for k in ["documentary_observations","speeches_deeds_and_outcomes","provisional_findings","standing_unresolved_questions","downstream_textual_checks"]]!=[30,10,10,16,12]:return fail("VII.5 counts mismatch")
 if "Strauss" in json.dumps(u,ensure_ascii=False):return fail("Primary unit imports secondary interpretation")
 if "certif" in u.get("status","").casefold():return fail("Unit status improperly certifies")
 h=H.read_text(encoding="utf-8")
 for x in ["PDF pages 153–155","PDF pages 155–159","Forty-eight drafted primary units","Preserved validator v1.47","XEN-PRI-RU-049"]:
  if x not in h:return fail("History safeguard missing: "+x)
 print("Xenophon repository validation passed");return 0
if __name__=="__main__":sys.exit(main())
