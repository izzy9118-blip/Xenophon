from pathlib import Path
import sys,yaml,tempfile,shutil,subprocess,json
R=Path(__file__).resolve().parents[1];P=R/"scripts/validate_repository_v1_41.py";U=R/"studies/xenophon-anabasis-dakyns/units/XEN-PRI-RU-042.yaml";L=R/"studies/xenophon-anabasis-dakyns/reading-plan.yaml";A=R/"audits/founding-state.yaml";H=R/"history/2026-07-31-anabasis-vi5-fortification-battle-victory.md"
def load(p):
 with p.open(encoding="utf-8") as f:return yaml.safe_load(f)
def dump(p,x):
 with p.open("w",encoding="utf-8") as f:yaml.safe_dump(x,f,sort_keys=False,allow_unicode=True)
def fail(x):print(x);return 1
def predecessor():
 if not P.exists():return fail("Frozen v1.41 validator missing")
 with tempfile.TemporaryDirectory() as d:
  t=Path(d)/"r";shutil.copytree(R,t,ignore=shutil.ignore_patterns(".git","__pycache__"))
  m=load(t/"manifest.yaml");m["version"]="1.41.0";s=m["primary_study"];s["drafted_units"]=s["drafted_units"][:-1];s["book_six_drafted_chapters"]=["VI.1","VI.2","VI.3","VI.4"];m["next_required_unit"]={"id":"XEN-PRI-RU-042","description":"Continue the independent primary reconstruction with Anabasis VI.5 using the Dakyns Project Gutenberg witness."};dump(t/"manifest.yaml",m)
  q=load(t/"studies/xenophon-anabasis-dakyns/reading-plan.yaml");q["reading_units"]=q["reading_units"][:-1];q["reading_units"][-1]["status"]="NEXT";q["remaining_sequence"]="Anabasis VI.6 through VII.8, strictly in chapter order.";dump(t/"studies/xenophon-anabasis-dakyns/reading-plan.yaml",q)
  a=load(t/"audits/founding-state.yaml");r=a["repository_state"];r["drafted_primary_units"]=41;r["book_six_drafted_chapters"]=["VI.1","VI.2","VI.3","VI.4"];a["documented_gaps"][1]["description"]="The primary Anabasis reconstruction remains incomplete; Books I through V are drafted pending owner review, and Book VI has drafted coverage through VI.4.";a["next_required_action"]="Complete XEN-PRI-RU-042 for Anabasis VI.5 without importing secondary interpretation or treating translated wording as unmediated Greek evidence.";dump(t/"audits/founding-state.yaml",a)
  z=subprocess.run([sys.executable,str(t/"scripts/validate_repository_v1_41.py")],cwd=t,text=True,capture_output=True);return fail("predecessor failed: "+(z.stdout+z.stderr).strip()) if z.returncode else 0
def main():
 if predecessor():return 1
 if any(not x.exists() for x in [U,L,A,H,P,R/"manifest.yaml"]):return fail("Missing VI.5 production file")
 m=load(R/"manifest.yaml");p=load(L);a=load(A);u=load(U);ids=[f"XEN-PRI-RU-{n:03d}" for n in range(1,43)];q=p.get("reading_units",[]);s=m.get("primary_study",{});r=a.get("repository_state",{})
 if m.get("version")!="1.42.0" or m.get("state")!="PRIMARY_RECONSTRUCTION_IN_PROGRESS":return fail("Manifest VI.5 mismatch")
 if m.get("artificial_intelligence_self_certification_prohibited") is not True or m.get("minister",{}).get("registration_status")!="NOT_YET_REGISTERED_IN_SANCTUM":return fail("Governance mismatch")
 if s.get("drafted_units")!=ids or s.get("book_six_drafted_chapters")!=["VI.1","VI.2","VI.3","VI.4","VI.5"] or m.get("next_required_unit",{}).get("id")!="XEN-PRI-RU-043":return fail("Coverage mismatch")
 if [x.get("id") for x in q]!=ids+["XEN-PRI-RU-043"] or q[-2].get("work_locator")!="Anabasis VI.5" or q[-2].get("pdf_pages_one_based")!="129-132" or q[-2].get("status")!="DRAFTED_PENDING_OWNER_REVIEW" or q[-1].get("work_locator")!="Anabasis VI.6" or q[-1].get("pdf_pages_one_based")!="132-137" or q[-1].get("status")!="NEXT":return fail("Plan mismatch")
 if r.get("drafted_primary_units")!=42 or r.get("book_six_drafted_chapters")!=["VI.1","VI.2","VI.3","VI.4","VI.5"] or r.get("minister_adapter_derived") is not False or r.get("sanctum_registration_present") is not False:return fail("Audit mismatch")
 if u.get("unit_id")!="XEN-PRI-RU-042" or u.get("status")!="DRAFTED_PENDING_OWNER_REVIEW" or u.get("scope",{}).get("pdf_pages_one_based")!="129-132" or u.get("secondary_comparison_status")!="DEFERRED":return fail("Unit mismatch")
 if "Translator wording is not unmediated Greek evidence" not in u.get("jurisdiction",""):return fail("Translation safeguard missing")
 n=u.get("narrative_person_and_authorial_attribution",{})
 if n.get("xenophon_as_character_present") is not True or n.get("first_person_narrator_present") is not False or n.get("direct_authorial_self_identification_present") is not False or n.get("interior_deliberation_report_present") is not True:return fail("Narrative mismatch")
 b=u.get("bibliographic_and_witness_control",{}).get("chapter_boundary_control","")
 for x in ["Heading V begins VI.5 on PDF page 129","heading VI begins VI.6 on page 132","stops before heading VI","Next unit covers pages 132-137"]:
  if x not in b:return fail("Boundary safeguard missing: "+x)
 types={o.get("evidence_type") for o in u.get("documentary_observations",[])}
 need={"DAYBREAK_FASTNESS_OCCUPATION_OBSERVATION","DITCH_PALISADE_THREE_GATES_OBSERVATION","HERACLEOT_SUPPLY_SHIP_OBSERVATION","FIRST_VICTIM_FAVOURABLE_OBSERVATION","AREXION_EAGLE_OMEN_OBSERVATION","OVER_FORTY_FIVE_CAMP_GUARD_OBSERVATION","COLUMN_BURIAL_METHOD_OBSERVATION","COMMON_GRAVE_VILLAGE_ROAD_OBSERVATION","SPITHRIDATES_RHATHINES_APPEAR_OBSERVATION","SECOND_FIRST_ESSAY_FAVOURABLE_OBSERVATION","THREE_TWO_HUNDRED_RESERVE_BRIGADES_OBSERVATION","WOODED_GULLY_HALT_OBSERVATION","ATTACK_OVER_RETREAT_ARGUMENT_OBSERVATION","DIFFICULT_GROUND_BEHIND_ADVANTAGE_OBSERVATION","WATCHWORD_CHARGE_DISCIPLINE_OBSERVATION","PHALANX_CAVALRY_ENEMY_FLIGHT_OBSERVATION","TROPHY_SUNSET_RETURN_OBSERVATION"}
 if need-types:return fail("VI.5 evidence types missing: "+", ".join(sorted(need-types)))
 text=" ".join(o.get("observation","") for o in u["documentary_observations"]).casefold()
 for x in ["natural fastness","leaving three gates","barleymeal","first victim","sees an eagle","above forty-five","common grave","spithridates and rhathines","about two miles","three reserve brigades","wooded gully","attack with half","good breakfast","zeus the saviour","heracles our guide","erect a trophy","about sunset"]:
  if x not in text:return fail("VI.5 phrase safeguard missing: "+x)
 if [len(u.get(k,[])) for k in ["documentary_observations","speeches_deeds_and_outcomes","provisional_findings","standing_unresolved_questions","downstream_textual_checks"]]!=[30,10,10,16,12]:return fail("VI.5 counts mismatch")
 if "Strauss" in json.dumps(u,ensure_ascii=False):return fail("Primary unit imports secondary interpretation")
 if "certif" in u.get("status","").casefold():return fail("Unit status improperly certifies")
 h=H.read_text(encoding="utf-8")
 for x in ["PDF pages 129–132","PDF pages 132–137","forty-two drafted primary units","Preserved validator v1.41"]:
  if x not in h:return fail("History safeguard missing: "+x)
 print("Xenophon repository validation passed");return 0
if __name__=="__main__":sys.exit(main())
