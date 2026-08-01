from pathlib import Path
import sys,yaml,tempfile,shutil,subprocess
R=Path(__file__).resolve().parents[1]
P=R/"scripts/validate_repository_v1_36.py"
U=R/"studies/xenophon-anabasis-dakyns/units/XEN-PRI-RU-037.yaml"
L=R/"studies/xenophon-anabasis-dakyns/reading-plan.yaml"
A=R/"audits/founding-state.yaml"
H=R/"history/2026-07-30-anabasis-v8-command-force-review.md"
def load(x):
 with x.open(encoding="utf-8") as f:return yaml.safe_load(f)
def dump(x,v):
 with x.open("w",encoding="utf-8") as f:yaml.safe_dump(v,f,sort_keys=False,allow_unicode=True)
def fail(x):print(x);return 1
def predecessor():
 if not P.exists():return fail("Frozen v1.36 validator missing")
 with tempfile.TemporaryDirectory() as d:
  t=Path(d)/"r";shutil.copytree(R,t,ignore=shutil.ignore_patterns(".git","__pycache__"))
  m=load(t/"manifest.yaml");m["version"]="1.36.0";s=m["primary_study"];s["drafted_units"]=s["drafted_units"][:-1];s.pop("book_five_draft_complete_pending_owner_review",None);s["book_five_drafted_chapters"]=[f"V.{n}" for n in range(1,8)];m["next_required_unit"]={"id":"XEN-PRI-RU-037","description":"Continue the independent primary reconstruction with Anabasis V.8 using the Dakyns Project Gutenberg witness."};dump(t/"manifest.yaml",m)
  q=load(t/"studies/xenophon-anabasis-dakyns/reading-plan.yaml");q["reading_units"]=q["reading_units"][:-1];q["reading_units"][-1]["status"]="NEXT";q["remaining_sequence"]="Anabasis VI.1 through VII.8, strictly in chapter order.";dump(t/"studies/xenophon-anabasis-dakyns/reading-plan.yaml",q)
  a=load(t/"audits/founding-state.yaml");r=a["repository_state"];r["drafted_primary_units"]=36;r.pop("book_five_primary_draft_complete",None);r["book_five_drafted_chapters"]=[f"V.{n}" for n in range(1,8)];a["resolved_items"]=[x for x in a["resolved_items"] if x.get("id")!="RES-007"];a["documented_gaps"][1]["description"]="The primary Anabasis reconstruction remains incomplete; Books I through IV are drafted pending owner review, and Book V has drafted coverage through V.7.";a["next_required_action"]="Complete XEN-PRI-RU-037 for Anabasis V.8 without importing Strauss or treating translated wording as unmediated Greek evidence.";dump(t/"audits/founding-state.yaml",a)
  z=subprocess.run([sys.executable,str(t/"scripts/validate_repository_v1_36.py")],cwd=t,text=True,capture_output=True)
  return fail("predecessor failed: "+(z.stdout+z.stderr).strip()) if z.returncode else 0
def main():
 if predecessor():return 1
 if any(not x.exists() for x in [U,L,A,H,P,R/"manifest.yaml"]):return fail("Missing V.8 production file")
 m=load(R/"manifest.yaml");p=load(L);a=load(A);u=load(U);ids=[f"XEN-PRI-RU-{n:03d}" for n in range(1,38)];ch=[f"V.{n}" for n in range(1,9)]
 if m.get("version")!="1.37.0" or m.get("state")!="PRIMARY_RECONSTRUCTION_IN_PROGRESS":return fail("Manifest V.8 mismatch")
 if m.get("artificial_intelligence_self_certification_prohibited") is not True or m.get("minister",{}).get("registration_status")!="NOT_YET_REGISTERED_IN_SANCTUM":return fail("Governance mismatch")
 s=m.get("primary_study",{});q=p.get("reading_units",[]);r=a.get("repository_state",{})
 if s.get("drafted_units")!=ids or s.get("book_five_drafted_chapters")!=ch or s.get("book_five_draft_complete_pending_owner_review") is not True or m.get("next_required_unit",{}).get("id")!="XEN-PRI-RU-038":return fail("Coverage mismatch")
 if [x.get("id") for x in q]!=ids+["XEN-PRI-RU-038"] or q[-2].get("pdf_pages_one_based")!="115-117" or q[-1].get("pdf_pages_one_based")!="118-121" or q[-1].get("status")!="NEXT":return fail("Plan mismatch")
 if r.get("drafted_primary_units")!=37 or r.get("book_five_primary_draft_complete") is not True or r.get("book_five_drafted_chapters")!=ch or r.get("minister_adapter_derived") is not False or r.get("sanctum_registration_present") is not False:return fail("Audit mismatch")
 if u.get("unit_id")!="XEN-PRI-RU-037" or u.get("status")!="DRAFTED_PENDING_OWNER_REVIEW" or u.get("scope",{}).get("pdf_pages_one_based")!="115-117" or u.get("secondary_comparison_status")!="DEFERRED":return fail("Unit mismatch")
 if "Translator wording is not unmediated Greek evidence" not in u.get("jurisdiction",""):return fail("Translation safeguard missing")
 n=u.get("narrative_person_and_authorial_attribution",{})
 if n.get("xenophon_as_character_present") is not True or n.get("first_person_narrator_present") is not False or n.get("direct_authorial_self_identification_present") is not False or n.get("extended_first_person_speech_present") is not True:return fail("Narrative mismatch")
 b=u.get("bibliographic_and_witness_control",{}).get("chapter_boundary_control","")
 for x in ["heading VIII on PDF page 115","BOOK VI heading on page 117","next unit therefore covers pages 118-121"]:
  if x not in b:return fail("Boundary safeguard missing: "+x)
 types={o.get("evidence_type") for o in u.get("documentary_observations",[])}
 need={"GENERAL_JUDICIAL_REVIEW_OBSERVATION","CARGO_DEFICIENCY_FINE_OBSERVATION","PERSONAL_OUTRAGE_INDICTMENT_OBSERVATION","FREE_MULE_DRIVER_STATUS_OBSERVATION","PREMATURE_BURIAL_ATTEMPT_OBSERVATION","GENERAL_ADMISSION_OF_FORCE_OBSERVATION","CORRECTIVE_AUTHORITY_ANALOGY_OBSERVATION","ARMED_PASSIVITY_ACQUIESCENCE_ARGUMENT_OBSERVATION","NO_EXPLICIT_VERDICT_OBSERVATION","JUDICIAL_ASYMMETRY_OBSERVATION"}
 if need-types:return fail("V.8 evidence types missing: "+", ".join(sorted(need-types)))
 text=" ".join(o.get("observation","") for o in u["documentary_observations"]).casefold()
 for x in ["twenty minae","ten minae","personal outrage with violence","although he was a free man","recognized as alive","confesses to striking","parents, masters, and surgeons","presence with swords","no explicit acquittal","financial penalties against other generals"]:
  if x not in text:return fail("V.8 phrase safeguard missing: "+x)
 if [len(u.get(k,[])) for k in ["documentary_observations","speeches_deeds_and_outcomes","provisional_findings","standing_unresolved_questions","downstream_textual_checks"]] != [33,10,10,18,12]:return fail("V.8 counts mismatch")
 print("Xenophon repository validation passed");return 0
if __name__=="__main__":sys.exit(main())
