from pathlib import Path
import sys,yaml,tempfile,shutil,subprocess
R=Path(__file__).resolve().parents[1];P=R/"scripts/validate_repository_v1_37.py";U=R/"studies/xenophon-anabasis-dakyns/units/XEN-PRI-RU-038.yaml";L=R/"studies/xenophon-anabasis-dakyns/reading-plan.yaml";A=R/"audits/founding-state.yaml";H=R/"history/2026-07-30-anabasis-vi1-diplomacy-dance-command.md"
def load(p):
 with p.open(encoding="utf-8") as f:return yaml.safe_load(f)
def dump(p,x):
 with p.open("w",encoding="utf-8") as f:yaml.safe_dump(x,f,sort_keys=False,allow_unicode=True)
def fail(x):print(x);return 1
def predecessor():
 if not P.exists():return fail("Frozen v1.37 validator missing")
 with tempfile.TemporaryDirectory() as d:
  t=Path(d)/"r";shutil.copytree(R,t,ignore=shutil.ignore_patterns(".git","__pycache__"));m=load(t/"manifest.yaml");m["version"]="1.37.0";s=m["primary_study"];s["drafted_units"]=s["drafted_units"][:-1];s.pop("book_six_drafted_chapters",None);m["next_required_unit"]={"id":"XEN-PRI-RU-038","description":"Continue the independent primary reconstruction with Anabasis VI.1 using the Dakyns Project Gutenberg witness."};dump(t/"manifest.yaml",m)
  q=load(t/"studies/xenophon-anabasis-dakyns/reading-plan.yaml");q["reading_units"]=q["reading_units"][:-1];q["reading_units"][-1]["status"]="NEXT";q["remaining_sequence"]="Anabasis VI.2 through VII.8, strictly in chapter order.";dump(t/"studies/xenophon-anabasis-dakyns/reading-plan.yaml",q)
  a=load(t/"audits/founding-state.yaml");r=a["repository_state"];r["drafted_primary_units"]=37;r.pop("book_six_drafted_chapters",None);a["documented_gaps"][1]["description"]="The primary Anabasis reconstruction remains incomplete; Books I through V are drafted pending owner review, and Book VI has not yet begun.";a["next_required_action"]="Complete XEN-PRI-RU-038 for Anabasis VI.1 without importing Strauss or treating translated wording as unmediated Greek evidence.";dump(t/"audits/founding-state.yaml",a)
  z=subprocess.run([sys.executable,str(t/"scripts/validate_repository_v1_37.py")],cwd=t,text=True,capture_output=True);return fail("predecessor failed: "+(z.stdout+z.stderr).strip()) if z.returncode else 0
def main():
 if predecessor():return 1
 if any(not x.exists() for x in [U,L,A,H,P,R/"manifest.yaml"]):return fail("Missing VI.1 production file")
 m=load(R/"manifest.yaml");p=load(L);a=load(A);u=load(U);ids=[f"XEN-PRI-RU-{n:03d}" for n in range(1,39)];q=p.get("reading_units",[]);s=m.get("primary_study",{});r=a.get("repository_state",{})
 if m.get("version")!="1.38.0" or m.get("state")!="PRIMARY_RECONSTRUCTION_IN_PROGRESS":return fail("Manifest VI.1 mismatch")
 if m.get("artificial_intelligence_self_certification_prohibited") is not True or m.get("minister",{}).get("registration_status")!="NOT_YET_REGISTERED_IN_SANCTUM":return fail("Governance mismatch")
 if s.get("drafted_units")!=ids or s.get("book_six_drafted_chapters")!=["VI.1"] or m.get("next_required_unit",{}).get("id")!="XEN-PRI-RU-039":return fail("Coverage mismatch")
 if [x.get("id") for x in q]!=ids+["XEN-PRI-RU-039"] or q[-2].get("pdf_pages_one_based")!="118-121" or q[-1].get("pdf_pages_one_based")!="122-124" or q[-1].get("status")!="NEXT":return fail("Plan mismatch")
 if r.get("drafted_primary_units")!=38 or r.get("book_six_drafted_chapters")!=["VI.1"] or r.get("minister_adapter_derived") is not False or r.get("sanctum_registration_present") is not False:return fail("Audit mismatch")
 if u.get("unit_id")!="XEN-PRI-RU-038" or u.get("status")!="DRAFTED_PENDING_OWNER_REVIEW" or u.get("scope",{}).get("pdf_pages_one_based")!="118-121" or u.get("secondary_comparison_status")!="DEFERRED":return fail("Unit mismatch")
 if "Translator wording is not unmediated Greek evidence" not in u.get("jurisdiction",""):return fail("Translation safeguard missing")
 n=u.get("narrative_person_and_authorial_attribution",{})
 if n.get("xenophon_as_character_present") is not True or n.get("first_person_narrator_present") is not False or n.get("direct_authorial_self_identification_present") is not False or n.get("interior_deliberation_report_present") is not True:return fail("Narrative mismatch")
 b=u.get("bibliographic_and_witness_control",{}).get("chapter_boundary_control","")
 for x in ["heading I on PDF page 118","heading II on page 122","next unit therefore covers pages 122-124"]:
  if x not in b:return fail("Boundary safeguard missing: "+x)
 types={o.get("evidence_type") for o in u.get("documentary_observations",[])}
 need={"RECIPROCAL_FRONTIER_VIOLENCE_OBSERVATION","CORYLAS_EMBASSY_OBSERVATION","CAPTIVE_ANIMAL_FEAST_OBSERVATION","DANCING_GIRL_PYRRHIC_OBSERVATION","MUTUAL_NON_INJURY_RESOLUTION_OBSERVATION","CHEIRISOPHUS_RETURN_OBSERVATION","SINGLE_COMMAND_ARGUMENT_OBSERVATION","XENOPHON_AMBITION_AND_RISK_OBSERVATION","DIVINE_REFUSAL_SIGN_OBSERVATION","SPARTAN_HEGEMONY_ARGUMENT_OBSERVATION","AGASIAS_DINING_JOKE_OBSERVATION","CHEIRISOPHUS_ELECTION_OBSERVATION","DEXIPPUS_SLANDER_REPORT_OBSERVATION"}
 if need-types:return fail("VI.1 evidence types missing: "+", ".join(sorted(need-types)))
 text=" ".join(o.get("observation","") for o in u["documentary_observations"]).casefold()
 for x in ["seize stragglers","mutual abstention","captive cattle","dancing girl","great king","three thousand measures","single commander","desire for honor","zeus the king","neither demand nor accept","lacedaemonian","dining companions","dexippus"]:
  if x not in text:return fail("VI.1 phrase safeguard missing: "+x)
 if [len(u.get(k,[])) for k in ["documentary_observations","speeches_deeds_and_outcomes","provisional_findings","standing_unresolved_questions","downstream_textual_checks"]]!=[30,10,9,16,12]:return fail("VI.1 counts mismatch")
 print("Xenophon repository validation passed");return 0
if __name__=="__main__":sys.exit(main())
