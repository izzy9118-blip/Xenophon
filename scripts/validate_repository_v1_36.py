from pathlib import Path
import sys,yaml,tempfile,shutil,subprocess
R=Path(__file__).resolve().parents[1];P=R/"scripts/validate_repository_v1_35.py";U=R/"studies/xenophon-anabasis-dakyns/units/XEN-PRI-RU-036.yaml";L=R/"studies/xenophon-anabasis-dakyns/reading-plan.yaml";A=R/"audits/founding-state.yaml";H=R/"history/2026-07-30-anabasis-v7-lawlessness-judicial-reconstitution.md"
def load(p):
 with p.open(encoding="utf-8") as f:return yaml.safe_load(f)
def dump(p,x):
 with p.open("w",encoding="utf-8") as f:yaml.safe_dump(x,f,sort_keys=False,allow_unicode=True)
def fail(x):print(x);return 1
def predecessor():
 if not P.exists():return fail("Frozen v1.35 validator missing")
 with tempfile.TemporaryDirectory() as d:
  t=Path(d)/"r";shutil.copytree(R,t,ignore=shutil.ignore_patterns(".git","__pycache__"));m=load(t/"manifest.yaml");m["version"]="1.35.0";m["primary_study"]["drafted_units"]=m["primary_study"]["drafted_units"][:-1];m["primary_study"]["book_five_drafted_chapters"]=["V.1","V.2","V.3","V.4","V.5","V.6"];m["next_required_unit"]={"id":"XEN-PRI-RU-036","description":"Continue the independent primary reconstruction with Anabasis V.7 using the Dakyns Project Gutenberg witness."};dump(t/"manifest.yaml",m);p=load(t/"studies/xenophon-anabasis-dakyns/reading-plan.yaml");p["reading_units"]=p["reading_units"][:-1];p["reading_units"][-1]["pdf_pages_one_based"]="111-114";p["reading_units"][-1]["status"]="NEXT";p["remaining_sequence"]="Anabasis V.8 through VII.8, strictly in chapter order.";dump(t/"studies/xenophon-anabasis-dakyns/reading-plan.yaml",p);a=load(t/"audits/founding-state.yaml");a["repository_state"]["drafted_primary_units"]=35;a["repository_state"]["book_five_drafted_chapters"]=["V.1","V.2","V.3","V.4","V.5","V.6"];a["documented_gaps"][1]["description"]="The primary Anabasis reconstruction remains incomplete; Books I through IV are drafted pending owner review, and Book V has drafted coverage through V.6.";a["next_required_action"]="Complete XEN-PRI-RU-036 for Anabasis V.7 without importing Strauss or treating translated wording as unmediated Greek evidence.";dump(t/"audits/founding-state.yaml",a);q=subprocess.run([sys.executable,str(t/"scripts/validate_repository_v1_35.py")],cwd=t,text=True,capture_output=True);return fail("predecessor failed: "+(q.stdout+q.stderr).strip()) if q.returncode else 0
def main():
 if predecessor():return 1
 if any(not x.exists() for x in [U,L,A,H,P,R/"manifest.yaml"]):return fail("Missing V.7 production file")
 m=load(R/"manifest.yaml");a=load(A);p=load(L);u=load(U);ids=[f"XEN-PRI-RU-{n:03d}" for n in range(1,37)];ch=[f"V.{n}" for n in range(1,8)]
 if m.get("version")!="1.36.0" or m.get("state")!="PRIMARY_RECONSTRUCTION_IN_PROGRESS":return fail("Manifest V.7 mismatch")
 if m.get("artificial_intelligence_self_certification_prohibited") is not True or m.get("minister",{}).get("registration_status")!="NOT_YET_REGISTERED_IN_SANCTUM":return fail("Governance mismatch")
 s=m.get("primary_study",{});z=p.get("reading_units",[]);r=a.get("repository_state",{})
 if s.get("drafted_units")!=ids or s.get("book_five_drafted_chapters")!=ch or m.get("next_required_unit",{}).get("id")!="XEN-PRI-RU-037":return fail("Coverage mismatch")
 if [x.get("id") for x in z]!=ids+["XEN-PRI-RU-037"] or z[-2].get("pdf_pages_one_based")!="111-115" or z[-1].get("pdf_pages_one_based")!="115-117" or z[-1].get("status")!="NEXT":return fail("Corrected plan mismatch")
 if r.get("drafted_primary_units")!=36 or r.get("book_five_drafted_chapters")!=ch or r.get("minister_adapter_derived") is not False or r.get("sanctum_registration_present") is not False:return fail("Audit mismatch")
 if u.get("unit_id")!="XEN-PRI-RU-036" or u.get("status")!="DRAFTED_PENDING_OWNER_REVIEW" or u.get("scope",{}).get("pdf_pages_one_based")!="111-115" or u.get("secondary_comparison_status")!="DEFERRED":return fail("Unit mismatch")
 if "Translator wording is not unmediated Greek evidence" not in u.get("jurisdiction",""):return fail("Translation safeguard missing")
 n=u.get("narrative_person_and_authorial_attribution",{})
 if n.get("xenophon_as_character_present") is not True or n.get("first_person_narrator_present") is not False or n.get("direct_authorial_self_identification_present") is not False or n.get("extended_first_person_speech_present") is not True:return fail("Narrative mismatch")
 b=u.get("bibliographic_and_witness_control",{}).get("chapter_boundary_control","")
 for x in ["corrected to 111-115","before heading VIII","V.8 begins beneath heading VIII on page 115","before BOOK VI on page 117"]:
  if x not in b:return fail("Boundary safeguard missing: "+x)
 t={o.get("evidence_type") for o in u.get("documentary_observations",[])}
 need={"CORRECTED_CHAPTER_BOUNDARY_OBSERVATION","RUMOR_ATTRIBUTION_OBSERVATION","PREEMPTIVE_ASSEMBLY_OBSERVATION","GEOGRAPHIC_REFUTATION_OBSERVATION","UNAUTHORIZED_FRIENDLY_SETTLEMENT_RAID_OBSERVATION","PLUNDER_AND_PRIVATE_DEPARTURE_PLAN_OBSERVATION","ELDERLY_AMBASSADOR_OBSERVATION","AMBASSADOR_STONING_OBSERVATION","MOB_INFORMATION_FAILURE_OBSERVATION","MARKET_CLERK_PURSUIT_OBSERVATION","PANIC_DROWNING_OBSERVATION","COLLECTIVE_AUTHORITY_DIAGNOSIS_OBSERVATION","NO_TRIAL_ALTERNATIVES_OBSERVATION","DIPLOMATIC_ACCESS_LOSS_OBSERVATION","CAPITAL_PROSECUTION_RESOLUTION_OBSERVATION","OFFICER_DICAST_BOARD_OBSERVATION","RITUAL_PURIFICATION_OBSERVATION"}
 if need-t:return fail("V.7 evidence types missing: "+", ".join(sorted(need-t)))
 text=" ".join(o.get("observation","") for o in u.get("documentary_observations",[])).casefold()
 for x in ["corrected to 111-115","neon says xenophon","small ominous groups","herald to summon an immediate assembly","sunsetward hellas","boreas","single ship","ten thousand armed soldiers","clearetus secretly organizes","abandon the army","three elderly inhabitants","stone the three ambassadors","do not know the cause","zelarchus","unable to swim drown","control over war, peace, and command","guilt unpunished or innocence terrorized","unsafe","capital charge","since cyrus's death","board of dicasts","performs purification"]:
  if x not in text:return fail("V.7 phrase safeguard missing: "+x)
 if [len(u.get(k,[])) for k in ["documentary_observations","speeches_deeds_and_outcomes","provisional_findings","standing_unresolved_questions","downstream_textual_checks"]]!=[29,9,9,16,12]:return fail("V.7 record counts mismatch")
 print("Xenophon repository validation passed");return 0
if __name__=="__main__":sys.exit(main())
