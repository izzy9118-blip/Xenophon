from pathlib import Path
import sys,yaml,tempfile,shutil,subprocess,json
R=Path(__file__).resolve().parents[1];P=R/"scripts/validate_repository_v1_48.py";U=R/"studies/xenophon-anabasis-dakyns/units/XEN-PRI-RU-049.yaml";L=R/"studies/xenophon-anabasis-dakyns/reading-plan.yaml";A=R/"audits/founding-state.yaml";H=R/"history/2026-07-31-anabasis-vii6-spartan-recruitment-public-defense-departure.md"
def load(p):
 with p.open(encoding="utf-8") as f:return yaml.safe_load(f)
def dump(p,x):
 with p.open("w",encoding="utf-8") as f:yaml.safe_dump(x,f,sort_keys=False,allow_unicode=True)
def fail(x):print(x);return 1
def predecessor():
 if not P.exists():return fail("Frozen v1.48 validator missing")
 with tempfile.TemporaryDirectory() as d:
  t=Path(d)/"r";shutil.copytree(R,t,ignore=shutil.ignore_patterns(".git","__pycache__"))
  m=load(t/"manifest.yaml");m["version"]="1.48.0";s=m["primary_study"];s["drafted_units"]=s["drafted_units"][:-1];s["book_seven_drafted_chapters"]=["VII.1","VII.2","VII.3","VII.4","VII.5"];m["next_required_unit"]={"id":"XEN-PRI-RU-049","description":"Continue the independent primary reconstruction with Anabasis VII.6 using the Dakyns Project Gutenberg witness."};dump(t/"manifest.yaml",m)
  q=load(t/"studies/xenophon-anabasis-dakyns/reading-plan.yaml");q["reading_units"]=q["reading_units"][:-1];q["reading_units"][-1]["status"]="NEXT";q["remaining_sequence"]="Anabasis VII.7 through VII.8, strictly in chapter order.";dump(t/"studies/xenophon-anabasis-dakyns/reading-plan.yaml",q)
  a=load(t/"audits/founding-state.yaml");r=a["repository_state"];r["drafted_primary_units"]=48;r["book_seven_drafted_chapters"]=["VII.1","VII.2","VII.3","VII.4","VII.5"];a["documented_gaps"][1]["description"]="The primary Anabasis reconstruction remains incomplete; Books I through VI are drafted pending owner review, and Book VII has drafted coverage through VII.5.";a["next_required_action"]="Complete XEN-PRI-RU-049 for Anabasis VII.6 without importing secondary interpretation or treating translated wording as unmediated Greek evidence.";dump(t/"audits/founding-state.yaml",a)
  z=subprocess.run([sys.executable,str(t/"scripts/validate_repository_v1_48.py")],cwd=t,text=True,capture_output=True);return fail("predecessor failed: "+(z.stdout+z.stderr).strip()) if z.returncode else 0
def main():
 if predecessor():return 1
 if any(not x.exists() for x in [U,L,A,H,P,R/"manifest.yaml"]):return fail("Missing VII.6 production file")
 m=load(R/"manifest.yaml");p=load(L);a=load(A);u=load(U);ids=[f"XEN-PRI-RU-{n:03d}" for n in range(1,50)];q=p.get("reading_units",[]);s=m.get("primary_study",{});r=a.get("repository_state",{})
 if m.get("version")!="1.49.0" or m.get("state")!="PRIMARY_RECONSTRUCTION_IN_PROGRESS":return fail("Manifest VII.6 mismatch")
 if m.get("artificial_intelligence_self_certification_prohibited") is not True or m.get("minister",{}).get("registration_status")!="NOT_YET_REGISTERED_IN_SANCTUM":return fail("Governance mismatch")
 if s.get("drafted_units")!=ids or s.get("book_seven_drafted_chapters")!=["VII.1","VII.2","VII.3","VII.4","VII.5","VII.6"] or m.get("next_required_unit",{}).get("id")!="XEN-PRI-RU-050":return fail("Coverage mismatch")
 if [x.get("id") for x in q]!=ids+["XEN-PRI-RU-050"] or q[-2].get("work_locator")!="Anabasis VII.6" or q[-2].get("pdf_pages_one_based")!="155-159" or q[-2].get("status")!="DRAFTED_PENDING_OWNER_REVIEW" or q[-1].get("work_locator")!="Anabasis VII.7" or q[-1].get("pdf_pages_one_based")!="159-164" or q[-1].get("status")!="NEXT":return fail("Plan mismatch")
 if r.get("drafted_primary_units")!=49 or r.get("book_seven_drafted_chapters")!=["VII.1","VII.2","VII.3","VII.4","VII.5","VII.6"] or r.get("minister_adapter_derived") is not False or r.get("sanctum_registration_present") is not False:return fail("Audit mismatch")
 if u.get("unit_id")!="XEN-PRI-RU-049" or u.get("status")!="DRAFTED_PENDING_OWNER_REVIEW" or u.get("scope",{}).get("pdf_pages_one_based")!="155-159" or u.get("secondary_comparison_status")!="DEFERRED":return fail("Unit mismatch")
 if "Translator wording is not unmediated Greek evidence" not in u.get("jurisdiction",""):return fail("Translation safeguard missing")
 n=u.get("narrative_person_and_authorial_attribution",{})
 if n.get("xenophon_as_character_present") is not True or n.get("first_person_narrator_present") is not False or n.get("direct_authorial_self_identification_present") is not False or n.get("interior_deliberation_report_present") is not True:return fail("Narrative mismatch")
 b=u.get("bibliographic_and_witness_control",{}).get("chapter_boundary_control","")
 for x in ["Heading VI begins VII.6 on PDF page 155","heading VII begins VII.7 on page 159","stops before heading VII","Heading VIII begins on page 164","next unit covers pages 159-164"]:
  if x not in b:return fail("Boundary safeguard missing: "+x)
 types={o.get("evidence_type") for o in u.get("documentary_observations",[])}
 need={"BOOK_SEVEN_VII6_BOUNDARY_OBSERVATION","NEARLY_TWO_MONTHS_SPARTAN_EMBASSY_OBSERVATION","TISSAPHERNES_WAR_RECRUITMENT_OBSERVATION","DARIC_DOUBLE_QUADRUPLE_PAY_OBSERVATION","HERACLEIDES_DISPOSAL_PAY_ESCAPE_OBSERVATION","SEUTHES_SPARTAN_FRIEND_ALLY_OBSERVATION","MAGNIFICENT_HOSPITALITY_COMMAND_EXCLUSION_OBSERVATION","TOO_MUCH_SOLDIERS_FRIEND_OBSERVATION","POPULAR_LEADER_ASSEMBLY_STRATEGY_OBSERVATION","PUBLIC_SPARTAN_PAY_OFFER_OBSERVATION","ARCADIAN_PRIVATE_ENRICHMENT_ACCUSATION_OBSERVATION","STONING_CAPITAL_DEMAND_OBSERVATION","XENOPHON_RETURN_FROM_HOMEWARD_ROUTE_OBSERVATION","SEUTHES_MESSAGES_PROMISES_INITIAL_REFUSAL_OBSERVATION","ARISTARCHUS_SEUTHES_PUBLIC_VOTE_OBSERVATION","SEUTHES_LIES_PAY_VARIANCE_OBSERVATION","ALL_GODS_GODDESSES_NONRECEIPT_OATH_OBSERVATION","LESS_THAN_OTHER_GENERALS_OFFICERS_OBSERVATION","POVERTY_FRIEND_POWER_MISCALCULATION_OBSERVATION","FRIEND_CHEATS_FRIEND_STAIN_OBSERVATION","PERINTHUS_MIDWINTER_BLOCKADE_RECOLLECTION_OBSERVATION","SEUTHES_CAVALRY_LIGHT_INFANTRY_SECURITY_OBSERVATION","NO_COMRADE_DEATH_DOUBLE_GLORY_OBSERVATION","REFUGE_CHILDREN_FUTURE_OBSERVATION","FATHER_BENEFACTOR_MEMORY_REBUKE_OBSERVATION","CHARMINUS_SEUTHES_FAVORABLE_TESTIMONY_OBSERVATION","EURYLOCHUS_FULL_PAY_PRECONDITION_OBSERVATION","POLYCRATES_HERACLEIDES_THEFT_ACCUSATION_OBSERVATION","SEUTHES_HERACLEIDES_FLIGHT_RETENTION_OFFER_OBSERVATION","THIBRON_DEATH_WARNING_ZEUS_KING_DEPARTURE_OBSERVATION"}
 if need-types:return fail("VII.6 evidence types missing: "+", ".join(sorted(need-types)))
 text=" ".join(o.get("observation","") for o in u["documentary_observations"]).casefold()
 for x in ["nearly two months","charminus and polynicus","war against tissaphernes","one daric per month","end pay demands","friend and ally of lacedaemon","too much the soldiers' friend","popular leader","stoned to death","traveling home","quickest crossing to asia","soldiers voted for seuthes","lies and cheating about pay","all the gods and goddesses","other generals","friend cheats friend","perinthus","cavalry and light infantry","lost no comrade","future children","father and benefactor","full pay","captured property","one thousand hoplites","zeus the king","depart with the army"]:
  if x not in text:return fail("VII.6 phrase safeguard missing: "+x)
 if [len(u.get(k,[])) for k in ["documentary_observations","speeches_deeds_and_outcomes","provisional_findings","standing_unresolved_questions","downstream_textual_checks"]]!=[30,10,10,16,12]:return fail("VII.6 counts mismatch")
 if "Strauss" in json.dumps(u,ensure_ascii=False):return fail("Primary unit imports secondary interpretation")
 if "certif" in u.get("status","").casefold():return fail("Unit status improperly certifies")
 h=H.read_text(encoding="utf-8")
 for x in ["PDF pages 155–159","PDF pages 159–164","Forty-nine drafted primary units","Preserved validator v1.48","XEN-PRI-RU-050"]:
  if x not in h:return fail("History safeguard missing: "+x)
 print("Xenophon repository validation passed");return 0
if __name__=="__main__":sys.exit(main())
