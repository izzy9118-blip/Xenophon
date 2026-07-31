from pathlib import Path
import sys,yaml,tempfile,shutil,subprocess
R=Path(__file__).resolve().parents[1];P=R/"scripts/validate_repository_v1_34.py";U=R/"studies/xenophon-anabasis-dakyns/units/XEN-PRI-RU-035.yaml";L=R/"studies/xenophon-anabasis-dakyns/reading-plan.yaml";A=R/"audits/founding-state.yaml";H=R/"history/2026-07-30-anabasis-v6-sea-counsel-colony-rumor.md"
def load(p):
 with p.open(encoding="utf-8") as f:return yaml.safe_load(f)
def dump(p,x):
 with p.open("w",encoding="utf-8") as f:yaml.safe_dump(x,f,sort_keys=False,allow_unicode=True)
def fail(x):print(x);return 1
def predecessor():
 if not P.exists():return fail("Frozen v1.34 validator missing")
 with tempfile.TemporaryDirectory() as d:
  t=Path(d)/"r";shutil.copytree(R,t,ignore=shutil.ignore_patterns(".git","__pycache__"));m=load(t/"manifest.yaml");m["version"]="1.34.0";m["primary_study"]["drafted_units"]=m["primary_study"]["drafted_units"][:-1];m["primary_study"]["book_five_drafted_chapters"]=["V.1","V.2","V.3","V.4","V.5"];m["next_required_unit"]={"id":"XEN-PRI-RU-035","description":"Continue the independent primary reconstruction with Anabasis V.6 using the Dakyns Project Gutenberg witness."};dump(t/"manifest.yaml",m);p=load(t/"studies/xenophon-anabasis-dakyns/reading-plan.yaml");p["reading_units"]=p["reading_units"][:-1];p["reading_units"][-1].pop("record",None);p["reading_units"][-1]["status"]="NEXT";p["remaining_sequence"]="Anabasis V.6 through VII.8, strictly in chapter order.";dump(t/"studies/xenophon-anabasis-dakyns/reading-plan.yaml",p);a=load(t/"audits/founding-state.yaml");a["repository_state"]["drafted_primary_units"]=34;a["repository_state"]["book_five_drafted_chapters"]=["V.1","V.2","V.3","V.4","V.5"];a["documented_gaps"][1]["description"]="The primary Anabasis reconstruction remains incomplete; Books I through IV are drafted pending owner review, and Book V has drafted coverage through V.5.";a["next_required_action"]="Complete XEN-PRI-RU-035 for Anabasis V.6 without importing Strauss or treating translated wording as unmediated Greek evidence.";dump(t/"audits/founding-state.yaml",a);q=subprocess.run([sys.executable,str(t/"scripts/validate_repository_v1_34.py")],cwd=t,text=True,capture_output=True);return fail("predecessor failed: "+(q.stdout+q.stderr).strip()) if q.returncode else 0
def main():
 if predecessor():return 1
 if any(not x.exists() for x in [U,L,A,H,P,R/"manifest.yaml"]):return fail("Missing V.6 file")
 m=load(R/"manifest.yaml");a=load(A);p=load(L);u=load(U);ids=[f"XEN-PRI-RU-{n:03d}" for n in range(1,36)];ch=["V.1","V.2","V.3","V.4","V.5","V.6"]
 if m.get("version")!="1.35.0" or m.get("state")!="PRIMARY_RECONSTRUCTION_IN_PROGRESS":return fail("Manifest mismatch")
 if m.get("artificial_intelligence_self_certification_prohibited") is not True or m.get("minister",{}).get("registration_status")!="NOT_YET_REGISTERED_IN_SANCTUM":return fail("Governance mismatch")
 s=m.get("primary_study",{});z=p.get("reading_units",[]);r=a.get("repository_state",{})
 if s.get("drafted_units")!=ids or s.get("book_five_drafted_chapters")!=ch or m.get("next_required_unit",{}).get("id")!="XEN-PRI-RU-036":return fail("Coverage mismatch")
 if [x.get("id") for x in z]!=ids+["XEN-PRI-RU-036"] or z[-2].get("pdf_pages_one_based")!="107-111" or z[-1].get("pdf_pages_one_based")!="111-114" or z[-1].get("status")!="NEXT":return fail("Plan mismatch")
 if r.get("drafted_primary_units")!=35 or r.get("book_five_drafted_chapters")!=ch or r.get("minister_adapter_derived") is not False or r.get("sanctum_registration_present") is not False:return fail("Audit mismatch")
 if u.get("unit_id")!="XEN-PRI-RU-035" or u.get("status")!="DRAFTED_PENDING_OWNER_REVIEW" or u.get("scope",{}).get("pdf_pages_one_based")!="107-111" or u.get("secondary_comparison_status")!="DEFERRED":return fail("Unit mismatch")
 if "Translator wording is not unmediated Greek evidence" not in u.get("jurisdiction",""):return fail("Translation safeguard missing")
 n=u.get("narrative_person_and_authorial_attribution",{})
 if n.get("xenophon_as_character_present") is not True or n.get("first_person_narrator_present") is not False or n.get("direct_authorial_self_identification_present") is not False or n.get("interior_deliberation_report_present") is not True:return fail("Narrative mismatch")
 t={o.get("evidence_type") for o in u.get("documentary_observations",[])}
 for x in ["ROUTE_COUNSEL","COLONY_THOUGHT","PRIVATE_INDUCEMENT","FORCE_MAXIM","ANTI_DESERTION","PHASIS_PROPOSAL","PARATEXT","BOUNDARY"]:
  if x not in t:return fail("Evidence missing: "+x)
 if [len(u.get(k,[])) for k in ["documentary_observations","speeches_deeds_and_outcomes","provisional_findings","standing_unresolved_questions","downstream_textual_checks"]]!=[15,4,5,8,6]:return fail("Count mismatch")
 print("Xenophon repository validation passed");return 0
if __name__=="__main__":sys.exit(main())
