from pathlib import Path
import sys,yaml,tempfile,shutil,subprocess,json
R=Path(__file__).resolve().parents[1];P=R/"scripts/validate_repository_v1_46.py";U=R/"studies/xenophon-anabasis-dakyns/units/XEN-PRI-RU-047.yaml";L=R/"studies/xenophon-anabasis-dakyns/reading-plan.yaml";A=R/"audits/founding-state.yaml";H=R/"history/2026-07-31-anabasis-vii4-terror-winter-intercession-submission.md"
def load(p):
 with p.open(encoding="utf-8") as f:return yaml.safe_load(f)
def dump(p,x):
 with p.open("w",encoding="utf-8") as f:yaml.safe_dump(x,f,sort_keys=False,allow_unicode=True)
def fail(x):print(x);return 1
def predecessor():
 if not P.exists():return fail("Frozen v1.46 validator missing")
 with tempfile.TemporaryDirectory() as d:
  t=Path(d)/"r";shutil.copytree(R,t,ignore=shutil.ignore_patterns(".git","__pycache__"))
  m=load(t/"manifest.yaml");m["version"]="1.46.0";s=m["primary_study"];s["drafted_units"]=s["drafted_units"][:-1];s["book_seven_drafted_chapters"]=["VII.1","VII.2","VII.3"];m["next_required_unit"]={"id":"XEN-PRI-RU-047","description":"Continue the independent primary reconstruction with Anabasis VII.4 using the Dakyns Project Gutenberg witness."};dump(t/"manifest.yaml",m)
  q=load(t/"studies/xenophon-anabasis-dakyns/reading-plan.yaml");q["reading_units"]=q["reading_units"][:-1];q["reading_units"][-1]["status"]="NEXT";q["remaining_sequence"]="Anabasis VII.5 through VII.8, strictly in chapter order.";dump(t/"studies/xenophon-anabasis-dakyns/reading-plan.yaml",q)
  a=load(t/"audits/founding-state.yaml");r=a["repository_state"];r["drafted_primary_units"]=46;r["book_seven_drafted_chapters"]=["VII.1","VII.2","VII.3"];a["documented_gaps"][1]["description"]="The primary Anabasis reconstruction remains incomplete; Books I through VI are drafted pending owner review, and Book VII has drafted coverage through VII.3.";a["next_required_action"]="Complete XEN-PRI-RU-047 for Anabasis VII.4 without importing secondary interpretation or treating translated wording as unmediated Greek evidence.";dump(t/"audits/founding-state.yaml",a)
  z=subprocess.run([sys.executable,str(t/"scripts/validate_repository_v1_46.py")],cwd=t,text=True,capture_output=True);return fail("predecessor failed: "+(z.stdout+z.stderr).strip()) if z.returncode else 0
def main():
 if predecessor():return 1
 if any(not x.exists() for x in [U,L,A,H,P,R/"manifest.yaml"]):return fail("Missing VII.4 production file")
 m=load(R/"manifest.yaml");p=load(L);a=load(A);u=load(U);ids=[f"XEN-PRI-RU-{n:03d}" for n in range(1,48)];q=p.get("reading_units",[]);s=m.get("primary_study",{});r=a.get("repository_state",{})
 if m.get("version")!="1.47.0" or m.get("state")!="PRIMARY_RECONSTRUCTION_IN_PROGRESS":return fail("Manifest VII.4 mismatch")
 if m.get("artificial_intelligence_self_certification_prohibited") is not True or m.get("minister",{}).get("registration_status")!="NOT_YET_REGISTERED_IN_SANCTUM":return fail("Governance mismatch")
 if s.get("drafted_units")!=ids or s.get("book_seven_drafted_chapters")!=["VII.1","VII.2","VII.3","VII.4"] or m.get("next_required_unit",{}).get("id")!="XEN-PRI-RU-048":return fail("Coverage mismatch")
 if [x.get("id") for x in q]!=ids+["XEN-PRI-RU-048"] or q[-2].get("work_locator")!="Anabasis VII.4" or q[-2].get("pdf_pages_one_based")!="150-153" or q[-2].get("status")!="DRAFTED_PENDING_OWNER_REVIEW" or q[-1].get("work_locator")!="Anabasis VII.5" or q[-1].get("pdf_pages_one_based")!="153-155" or q[-1].get("status")!="NEXT":return fail("Plan mismatch")
 if r.get("drafted_primary_units")!=47 or r.get("book_seven_drafted_chapters")!=["VII.1","VII.2","VII.3","VII.4"] or r.get("minister_adapter_derived") is not False or r.get("sanctum_registration_present") is not False:return fail("Audit mismatch")
 if u.get("unit_id")!="XEN-PRI-RU-047" or u.get("status")!="DRAFTED_PENDING_OWNER_REVIEW" or u.get("scope",{}).get("pdf_pages_one_based")!="150-153" or u.get("secondary_comparison_status")!="DEFERRED":return fail("Unit mismatch")
 if "Translator wording is not unmediated Greek evidence" not in u.get("jurisdiction",""):return fail("Translation safeguard missing")
 n=u.get("narrative_person_and_authorial_attribution",{})
 if n.get("xenophon_as_character_present") is not True or n.get("first_person_narrator_present") is not False or n.get("direct_authorial_self_identification_present") is not False or n.get("interior_deliberation_report_present") is not True:return fail("Narrative mismatch")
 b=u.get("bibliographic_and_witness_control",{}).get("chapter_boundary_control","")
 for x in ["Heading IV begins VII.4 on PDF page 150","heading V begins VII.5 on page 153","stops before heading V","Heading VI begins on page 155","next unit covers pages 153-155"]:
  if x not in b:return fail("Boundary safeguard missing: "+x)
 types={o.get("evidence_type") for o in u.get("documentary_observations",[])}
 need={"BOOK_SEVEN_VII4_BOUNDARY_OBSERVATION","SEUTHES_TOTAL_VILLAGE_BURNING_OBSERVATION","TERROR_REFUSAL_OBEDIENCE_OBSERVATION","HERACLEIDES_PERINTHUS_BOOTY_SALE_OBSERVATION","FROZEN_WATER_WINE_FROSTBITE_OBSERVATION","THRACIAN_WINTER_CLOTHING_OBSERVATION","PRISONER_HUNGER_THREAT_MESSAGE_OBSERVATION","YOUNGEST_HEAVY_INFANTRY_NIGHT_EXPEDITION_OBSERVATION","SEUTHES_UNSPARING_SHOOTING_OBSERVATION","EPISTHENES_HANDSOME_YOUTH_INTERCESSION_OBSERVATION","EPISTHENES_LIFE_SUBSTITUTION_OBSERVATION","YOUTH_REFUSES_BOTH_DEATHS_OBSERVATION","SEUTHES_LAUGHTER_MERCY_OBSERVATION","SUBSISTENCE_DENIAL_BIVOUAC_OBSERVATION","XENOPHON_BAD_QUARTERS_WARNING_OBSERVATION","FALSE_PARLEY_RECONNAISSANCE_OBSERVATION","HOUSEHOLDER_GUIDED_NIGHT_ATTACK_OBSERVATION","SPEAR_CLUB_FIRE_XENOPHON_CALL_OBSERVATION","SILANUS_TRUMPET_BREAKOUT_OBSERVATION","DARKNESS_GLARE_WOUNDED_CAPTAINS_OBSERVATION","SEVEN_TROOPERS_HOSTAGES_SUBMISSION_OBSERVATION"}
 if need-types:return fail("VII.4 evidence types missing: "+", ".join(sorted(need-types)))
 text=" ".join(o.get("observation","") for o in u["documentary_observations"]).casefold()
 for x in ["not a single house","inspire terror","future pay","freeze dinner water and wine","frostbitten noses and ears","fox-skin caps","perish with hunger","women, children, and older men","youngest heavy infantry","unsparingly shoots down","handsome youth","stretches out his neck","kill neither","laughs and consents","deprive the mountaineers","quarters are bad","closer inspection","house owners guide","roasted alive","about eighteen years old","hieronymus and theogenes","seven troopers","tripled force","capable troublemakers"]:
  if x not in text:return fail("VII.4 phrase safeguard missing: "+x)
 if [len(u.get(k,[])) for k in ["documentary_observations","speeches_deeds_and_outcomes","provisional_findings","standing_unresolved_questions","downstream_textual_checks"]]!=[30,10,10,16,12]:return fail("VII.4 counts mismatch")
 if "Strauss" in json.dumps(u,ensure_ascii=False):return fail("Primary unit imports secondary interpretation")
 if "certif" in u.get("status","").casefold():return fail("Unit status improperly certifies")
 h=H.read_text(encoding="utf-8")
 for x in ["PDF pages 150–153","PDF pages 153–155","forty-seven drafted primary units","Preserved validator v1.46","XEN-PRI-RU-048"]:
  if x not in h:return fail("History safeguard missing: "+x)
 print("Xenophon repository validation passed");return 0
if __name__=="__main__":sys.exit(main())
