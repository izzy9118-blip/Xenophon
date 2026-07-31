from pathlib import Path
import sys,yaml,tempfile,shutil,subprocess,json
R=Path(__file__).resolve().parents[1];P=R/"scripts/validate_repository_v1_45.py";U=R/"studies/xenophon-anabasis-dakyns/units/XEN-PRI-RU-046.yaml";L=R/"studies/xenophon-anabasis-dakyns/reading-plan.yaml";A=R/"audits/founding-state.yaml";H=R/"history/2026-07-31-anabasis-vii3-public-choice-banquet-night-campaign.md"
def load(p):
 with p.open(encoding="utf-8") as f:return yaml.safe_load(f)
def dump(p,x):
 with p.open("w",encoding="utf-8") as f:yaml.safe_dump(x,f,sort_keys=False,allow_unicode=True)
def fail(x):print(x);return 1
def predecessor():
 if not P.exists():return fail("Frozen v1.45 validator missing")
 with tempfile.TemporaryDirectory() as d:
  t=Path(d)/"r";shutil.copytree(R,t,ignore=shutil.ignore_patterns(".git","__pycache__"))
  m=load(t/"manifest.yaml");m["version"]="1.45.0";s=m["primary_study"];s["drafted_units"]=s["drafted_units"][:-1];s["book_seven_drafted_chapters"]=["VII.1","VII.2"];m["next_required_unit"]={"id":"XEN-PRI-RU-046","description":"Continue the independent primary reconstruction with Anabasis VII.3 using the Dakyns Project Gutenberg witness."};dump(t/"manifest.yaml",m)
  q=load(t/"studies/xenophon-anabasis-dakyns/reading-plan.yaml");q["reading_units"]=q["reading_units"][:-1];q["reading_units"][-1]["status"]="NEXT";q["remaining_sequence"]="Anabasis VII.4 through VII.8, strictly in chapter order.";dump(t/"studies/xenophon-anabasis-dakyns/reading-plan.yaml",q)
  a=load(t/"audits/founding-state.yaml");r=a["repository_state"];r["drafted_primary_units"]=45;r["book_seven_drafted_chapters"]=["VII.1","VII.2"];a["documented_gaps"][1]["description"]="The primary Anabasis reconstruction remains incomplete; Books I through VI are drafted pending owner review, and Book VII has drafted coverage through VII.2.";a["next_required_action"]="Complete XEN-PRI-RU-046 for Anabasis VII.3 without importing secondary interpretation or treating translated wording as unmediated Greek evidence.";dump(t/"audits/founding-state.yaml",a)
  z=subprocess.run([sys.executable,str(t/"scripts/validate_repository_v1_45.py")],cwd=t,text=True,capture_output=True);return fail("predecessor failed: "+(z.stdout+z.stderr).strip()) if z.returncode else 0
def main():
 if predecessor():return 1
 if any(not x.exists() for x in [U,L,A,H,P,R/"manifest.yaml"]):return fail("Missing VII.3 production file")
 m=load(R/"manifest.yaml");p=load(L);a=load(A);u=load(U);ids=[f"XEN-PRI-RU-{n:03d}" for n in range(1,47)];q=p.get("reading_units",[]);s=m.get("primary_study",{});r=a.get("repository_state",{})
 if m.get("version")!="1.46.0" or m.get("state")!="PRIMARY_RECONSTRUCTION_IN_PROGRESS":return fail("Manifest VII.3 mismatch")
 if m.get("artificial_intelligence_self_certification_prohibited") is not True or m.get("minister",{}).get("registration_status")!="NOT_YET_REGISTERED_IN_SANCTUM":return fail("Governance mismatch")
 if s.get("drafted_units")!=ids or s.get("book_seven_drafted_chapters")!=["VII.1","VII.2","VII.3"] or m.get("next_required_unit",{}).get("id")!="XEN-PRI-RU-047":return fail("Coverage mismatch")
 if [x.get("id") for x in q]!=ids+["XEN-PRI-RU-047"] or q[-2].get("work_locator")!="Anabasis VII.3" or q[-2].get("pdf_pages_one_based")!="145-150" or q[-2].get("status")!="DRAFTED_PENDING_OWNER_REVIEW" or q[-1].get("work_locator")!="Anabasis VII.4" or q[-1].get("pdf_pages_one_based")!="150-153" or q[-1].get("status")!="NEXT":return fail("Plan mismatch")
 if r.get("drafted_primary_units")!=46 or r.get("book_seven_drafted_chapters")!=["VII.1","VII.2","VII.3"] or r.get("minister_adapter_derived") is not False or r.get("sanctum_registration_present") is not False:return fail("Audit mismatch")
 if u.get("unit_id")!="XEN-PRI-RU-046" or u.get("status")!="DRAFTED_PENDING_OWNER_REVIEW" or u.get("scope",{}).get("pdf_pages_one_based")!="145-150" or u.get("secondary_comparison_status")!="DEFERRED":return fail("Unit mismatch")
 if "Translator wording is not unmediated Greek evidence" not in u.get("jurisdiction",""):return fail("Translation safeguard missing")
 n=u.get("narrative_person_and_authorial_attribution",{})
 if n.get("xenophon_as_character_present") is not True or n.get("first_person_narrator_present") is not False or n.get("direct_authorial_self_identification_present") is not False or n.get("interior_deliberation_report_present") is not True:return fail("Narrative mismatch")
 b=u.get("bibliographic_and_witness_control",{}).get("chapter_boundary_control","")
 for x in ["Heading III begins VII.3 on PDF page 145","heading IV begins VII.4 on page 150","stops before heading IV","next unit covers pages 150-153","earlier tentative 150-155 range was not adopted"]:
  if x not in b:return fail("Boundary safeguard missing: "+x)
 types={o.get("evidence_type") for o in u.get("documentary_observations",[])}
 need={"BOOK_SEVEN_VII3_BOUNDARY_OBSERVATION","DEPUTATION_DAWN_REPORT_OBSERVATION","ARISTARCHUS_SUMMONS_REFUSED_OBSERVATION","NEON_TEN_FURLONG_ABSENCE_OBSERVATION","PUBLIC_ALTERNATIVES_DISCLOSURE_OBSERVATION","NO_MONEY_NO_LEAVE_PROVISION_OBSERVATION","ALL_HANDS_PROVISION_MOVE_OBSERVATION","NEON_ARISTARCHUS_AGENT_FAILURE_OBSERVATION","SEUTHES_PUBLIC_WITNESS_REQUEST_OBSERVATION","CLOSE_PACKED_PROVISION_VILLAGES_OBSERVATION","CYZICENE_PAY_CUSTOMARY_RATES_OBSERVATION","CAPTURED_PROPERTY_RULER_PAY_OBSERVATION","SEVEN_DAY_DISTANCE_LIMIT_OBSERVATION","WINTER_FRIENDLY_COUNTRY_ARGUMENT_OBSERVATION","UNOPPOSED_ARMY_VOTE_OBSERVATION","HERACLEIDES_GIFT_SOLICITATION_OBSERVATION","XENOPHON_NEAR_POVERTY_OBSERVATION","BANQUET_DISTRIBUTION_CUSTOM_OBSERVATION","ARYSTAS_COMIC_EATING_OBSERVATION","THRACIAN_GIFTS_OBSERVATION","XENOPHON_SELF_COMPANIONS_GIFT_OBSERVATION","FRATERNAL_WINE_SPRINKLING_OBSERVATION","MUSICIANS_WAR_DANCE_JESTERS_OBSERVATION","NIGHT_SENTINEL_THRACIAN_ENTRY_OBSERVATION","SLOWEST_ARM_NIGHT_MARCH_OBSERVATION","ATHENAIA_WATCHWORD_OBSERVATION","MIDNIGHT_ORDER_DAWN_COHESION_OBSERVATION","THOUSAND_CAPTIVES_TWO_THOUSAND_CATTLE_TEN_THOUSAND_SMALL_OBSERVATION"}
 if need-types:return fail("VII.3 evidence types missing: "+", ".join(sorted(need-types)))
 text=" ".join(o.get("observation","") for o in u["documentary_observations"]).casefold()
 for x in ["ten furlongs","ships of war","sacred mountain","neither money to buy","right to help ourselves is conferred by might","all held them up","three miles","in the presence of as many witnesses as possible","close-packed","a cyzicene","customary rate","seven days’ journey","winter","no one opposed","heracleides","one boy","traveling expenses","white horse","myself and these my dear comrades","god willing","sprinkled the last drops","war song","night sentinels","slowest arm","athenaia","deep snow","under thirty","one thousand","two thousand","ten thousand"]:
  if x not in text:return fail("VII.3 phrase safeguard missing: "+x)
 if [len(u.get(k,[])) for k in ["documentary_observations","speeches_deeds_and_outcomes","provisional_findings","standing_unresolved_questions","downstream_textual_checks"]]!=[30,10,10,16,12]:return fail("VII.3 counts mismatch")
 if "Strauss" in json.dumps(u,ensure_ascii=False):return fail("Primary unit imports secondary interpretation")
 if "certif" in u.get("status","").casefold():return fail("Unit status improperly certifies")
 h=H.read_text(encoding="utf-8")
 for x in ["PDF pages 145–150","PDF pages 150–153","earlier tentative 150–155 range was not adopted","forty-six drafted primary units","Preserved validator v1.45","XEN-PRI-RU-047"]:
  if x not in h:return fail("History safeguard missing: "+x)
 print("Xenophon repository validation passed");return 0
if __name__=="__main__":sys.exit(main())
