from pathlib import Path
import sys,yaml,tempfile,shutil,subprocess,json
R=Path(__file__).resolve().parents[1];P=R/"scripts/validate_repository_v1_44.py";U=R/"studies/xenophon-anabasis-dakyns/units/XEN-PRI-RU-045.yaml";L=R/"studies/xenophon-anabasis-dakyns/reading-plan.yaml";A=R/"audits/founding-state.yaml";H=R/"history/2026-07-31-anabasis-vii2-fragmentation-blocked-passage-seuthes-pledges.md"
def load(p):
 with p.open(encoding="utf-8") as f:return yaml.safe_load(f)
def dump(p,x):
 with p.open("w",encoding="utf-8") as f:yaml.safe_dump(x,f,sort_keys=False,allow_unicode=True)
def fail(x):print(x);return 1
def predecessor():
 if not P.exists():return fail("Frozen v1.44 validator missing")
 with tempfile.TemporaryDirectory() as d:
  t=Path(d)/"r";shutil.copytree(R,t,ignore=shutil.ignore_patterns(".git","__pycache__"))
  m=load(t/"manifest.yaml");m["version"]="1.44.0";s=m["primary_study"];s["drafted_units"]=s["drafted_units"][:-1];s["book_seven_drafted_chapters"]=["VII.1"];m["next_required_unit"]={"id":"XEN-PRI-RU-045","description":"Continue the independent primary reconstruction with Anabasis VII.2 using the Dakyns Project Gutenberg witness."};dump(t/"manifest.yaml",m)
  q=load(t/"studies/xenophon-anabasis-dakyns/reading-plan.yaml");q["reading_units"]=q["reading_units"][:-1];q["reading_units"][-1]["status"]="NEXT";q["remaining_sequence"]="Anabasis VII.3 through VII.8, strictly in chapter order.";dump(t/"studies/xenophon-anabasis-dakyns/reading-plan.yaml",q)
  a=load(t/"audits/founding-state.yaml");r=a["repository_state"];r["drafted_primary_units"]=44;r["book_seven_drafted_chapters"]=["VII.1"];a["documented_gaps"][1]["description"]="The primary Anabasis reconstruction remains incomplete; Books I through VI are drafted pending owner review, and Book VII has drafted coverage through VII.1.";a["next_required_action"]="Complete XEN-PRI-RU-045 for Anabasis VII.2 without importing secondary interpretation or treating translated wording as unmediated Greek evidence.";dump(t/"audits/founding-state.yaml",a)
  z=subprocess.run([sys.executable,str(t/"scripts/validate_repository_v1_44.py")],cwd=t,text=True,capture_output=True);return fail("predecessor failed: "+(z.stdout+z.stderr).strip()) if z.returncode else 0
def main():
 if predecessor():return 1
 if any(not x.exists() for x in [U,L,A,H,P,R/"manifest.yaml"]):return fail("Missing VII.2 production file")
 m=load(R/"manifest.yaml");p=load(L);a=load(A);u=load(U);ids=[f"XEN-PRI-RU-{n:03d}" for n in range(1,46)];q=p.get("reading_units",[]);s=m.get("primary_study",{});r=a.get("repository_state",{})
 if m.get("version")!="1.45.0" or m.get("state")!="PRIMARY_RECONSTRUCTION_IN_PROGRESS":return fail("Manifest VII.2 mismatch")
 if m.get("artificial_intelligence_self_certification_prohibited") is not True or m.get("minister",{}).get("registration_status")!="NOT_YET_REGISTERED_IN_SANCTUM":return fail("Governance mismatch")
 if s.get("drafted_units")!=ids or s.get("book_seven_drafted_chapters")!=["VII.1","VII.2"] or m.get("next_required_unit",{}).get("id")!="XEN-PRI-RU-046":return fail("Coverage mismatch")
 if [x.get("id") for x in q]!=ids+["XEN-PRI-RU-046"] or q[-2].get("work_locator")!="Anabasis VII.2" or q[-2].get("pdf_pages_one_based")!="141-145" or q[-2].get("status")!="DRAFTED_PENDING_OWNER_REVIEW" or q[-1].get("work_locator")!="Anabasis VII.3" or q[-1].get("pdf_pages_one_based")!="145-150" or q[-1].get("status")!="NEXT":return fail("Plan mismatch")
 if r.get("drafted_primary_units")!=45 or r.get("book_seven_drafted_chapters")!=["VII.1","VII.2"] or r.get("minister_adapter_derived") is not False or r.get("sanctum_registration_present") is not False:return fail("Audit mismatch")
 if u.get("unit_id")!="XEN-PRI-RU-045" or u.get("status")!="DRAFTED_PENDING_OWNER_REVIEW" or u.get("scope",{}).get("pdf_pages_one_based")!="141-145" or u.get("secondary_comparison_status")!="DEFERRED":return fail("Unit mismatch")
 if "Translator wording is not unmediated Greek evidence" not in u.get("jurisdiction",""):return fail("Translation safeguard missing")
 n=u.get("narrative_person_and_authorial_attribution",{})
 if n.get("xenophon_as_character_present") is not True or n.get("first_person_narrator_present") is not False or n.get("direct_authorial_self_identification_present") is not False or n.get("interior_deliberation_report_present") is not True:return fail("Narrative mismatch")
 b=u.get("bibliographic_and_witness_control",{}).get("chapter_boundary_control","")
 for x in ["Heading II begins VII.2 on PDF page 141","heading III begins VII.3 on page 145","stops before heading III","Next unit covers pages 145-150"]:
  if x not in b:return fail("Boundary safeguard missing: "+x)
 types={o.get("evidence_type") for o in u.get("documentary_observations",[])}
 need={"FIVE_GENERALS_REMAIN_OBSERVATION","GENERALS_DESTINATION_DISAGREEMENT_OBSERVATION","ARMS_SALE_DISPERSAL_OBSERVATION","ANAXIBIUS_BREAKUP_GRATIFIES_PHARNABAZUS_OBSERVATION","CLEANDER_SICK_WOUNDED_PROTECTION_OBSERVATION","ARISTARCHUS_FOUR_HUNDRED_SALE_OBSERVATION","ANAXIBIUS_REUNION_REVERSAL_OBSERVATION","THIRTY_OARED_GALLEY_AUTHORITY_LETTER_OBSERVATION","XENOPHON_INITIAL_SEUTHES_REFUSAL_OBSERVATION","NEON_EIGHT_HUNDRED_SEPARATION_OBSERVATION","ARISTARCHUS_TWO_WARSHIPS_OBSERVATION","ANAXIBIUS_NO_LONGER_ADMIRAL_SINKING_THREAT_OBSERVATION","ARREST_PHARNABAZUS_WARNING_OBSERVATION","SEUTHES_PROJECT_SACRIFICE_OBSERVATION","FAVOURABLE_VICTIMS_SAFE_PROJECT_OBSERVATION","POLYCRATES_TRUSTED_DELEGATION_SIXTY_FURLONGS_OBSERVATION","SEUTHES_COMPENSATION_REFUGE_KINSHIP_PLEDGES_OBSERVATION"}
 if need-types:return fail("VII.2 evidence types missing: "+", ".join(sorted(need-types)))
 text=" ".join(o.get("observation","") for o in u["documentary_observations"]).casefold()
 for x in ["five","cannot agree","sell or give away their arms","gratifying pharnabazus","sick and wounded","four hundred","reunited","thirty-oared galley","not open to him","eight hundred","two warships","no longer admiral","threatens to sink","delivery to pharnabazus","bring the army to seuthes","victims are interpreted as favorable","sixty furlongs","bisanthe"]:
  if x not in text:return fail("VII.2 phrase safeguard missing: "+x)
 if [len(u.get(k,[])) for k in ["documentary_observations","speeches_deeds_and_outcomes","provisional_findings","standing_unresolved_questions","downstream_textual_checks"]]!=[30,10,10,16,12]:return fail("VII.2 counts mismatch")
 if "Strauss" in json.dumps(u,ensure_ascii=False):return fail("Primary unit imports secondary interpretation")
 if "certif" in u.get("status","").casefold():return fail("Unit status improperly certifies")
 h=H.read_text(encoding="utf-8")
 for x in ["PDF pages 141–145","PDF pages 145–150","forty-five drafted primary units","Preserved validator v1.44"]:
  if x not in h:return fail("History safeguard missing: "+x)
 print("Xenophon repository validation passed");return 0
if __name__=="__main__":sys.exit(main())
