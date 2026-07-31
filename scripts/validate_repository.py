from pathlib import Path
import sys,yaml,tempfile,shutil,subprocess
R=Path(__file__).resolve().parents[1];P=R/"scripts/validate_repository_v1_38.py";U=R/"studies/xenophon-anabasis-dakyns/units/XEN-PRI-RU-039.yaml";L=R/"studies/xenophon-anabasis-dakyns/reading-plan.yaml";A=R/"audits/founding-state.yaml";H=R/"history/2026-07-30-anabasis-vi2-heraclea-secession-three-divisions.md"
def load(p):
 with p.open(encoding="utf-8") as f:return yaml.safe_load(f)
def dump(p,x):
 with p.open("w",encoding="utf-8") as f:yaml.safe_dump(x,f,sort_keys=False,allow_unicode=True)
def fail(x):print(x);return 1
def predecessor():
 if not P.exists():return fail("Frozen v1.38 validator missing")
 with tempfile.TemporaryDirectory() as d:
  t=Path(d)/"r";shutil.copytree(R,t,ignore=shutil.ignore_patterns(".git","__pycache__"))
  m=load(t/"manifest.yaml");m["version"]="1.38.0";s=m["primary_study"];s["drafted_units"]=s["drafted_units"][:-1];s["book_six_drafted_chapters"]=["VI.1"];m["next_required_unit"]={"id":"XEN-PRI-RU-039","description":"Continue the independent primary reconstruction with Anabasis VI.2 using the Dakyns Project Gutenberg witness."};dump(t/"manifest.yaml",m)
  q=load(t/"studies/xenophon-anabasis-dakyns/reading-plan.yaml");q["reading_units"]=q["reading_units"][:-1];q["reading_units"][-1]["status"]="NEXT";q["remaining_sequence"]="Anabasis VI.3 through VII.8, strictly in chapter order.";dump(t/"studies/xenophon-anabasis-dakyns/reading-plan.yaml",q)
  a=load(t/"audits/founding-state.yaml");r=a["repository_state"];r["drafted_primary_units"]=38;r["book_six_drafted_chapters"]=["VI.1"];a["documented_gaps"][1]["description"]="The primary Anabasis reconstruction remains incomplete; Books I through V are drafted pending owner review, and Book VI has drafted coverage through VI.1.";a["next_required_action"]="Complete XEN-PRI-RU-039 for Anabasis VI.2 without importing Strauss or treating translated wording as unmediated Greek evidence.";dump(t/"audits/founding-state.yaml",a)
  z=subprocess.run([sys.executable,str(t/"scripts/validate_repository_v1_38.py")],cwd=t,text=True,capture_output=True);return fail("predecessor failed: "+(z.stdout+z.stderr).strip()) if z.returncode else 0
def main():
 if predecessor():return 1
 if any(not x.exists() for x in [U,L,A,H,P,R/"manifest.yaml"]):return fail("Missing VI.2 production file")
 m=load(R/"manifest.yaml");p=load(L);a=load(A);u=load(U);ids=[f"XEN-PRI-RU-{n:03d}" for n in range(1,40)];q=p.get("reading_units",[]);s=m.get("primary_study",{});r=a.get("repository_state",{})
 if m.get("version")!="1.39.0" or m.get("state")!="PRIMARY_RECONSTRUCTION_IN_PROGRESS":return fail("Manifest VI.2 mismatch")
 if m.get("artificial_intelligence_self_certification_prohibited") is not True or m.get("minister",{}).get("registration_status")!="NOT_YET_REGISTERED_IN_SANCTUM":return fail("Governance mismatch")
 if s.get("drafted_units")!=ids or s.get("book_six_drafted_chapters")!=["VI.1","VI.2"] or m.get("next_required_unit",{}).get("id")!="XEN-PRI-RU-040":return fail("Coverage mismatch")
 if [x.get("id") for x in q]!=ids+["XEN-PRI-RU-040"] or q[-2].get("pdf_pages_one_based")!="122-124" or q[-2].get("status")!="DRAFTED_PENDING_OWNER_REVIEW" or q[-1].get("pdf_pages_one_based")!="124-127" or q[-1].get("status")!="NEXT":return fail("Plan mismatch")
 if r.get("drafted_primary_units")!=39 or r.get("book_six_drafted_chapters")!=["VI.1","VI.2"] or r.get("minister_adapter_derived") is not False or r.get("sanctum_registration_present") is not False:return fail("Audit mismatch")
 if u.get("unit_id")!="XEN-PRI-RU-039" or u.get("status")!="DRAFTED_PENDING_OWNER_REVIEW" or u.get("scope",{}).get("pdf_pages_one_based")!="122-124" or u.get("secondary_comparison_status")!="DEFERRED":return fail("Unit mismatch")
 if "Translator wording is not unmediated Greek evidence" not in u.get("jurisdiction",""):return fail("Translation safeguard missing")
 n=u.get("narrative_person_and_authorial_attribution",{})
 if n.get("xenophon_as_character_present") is not True or n.get("first_person_narrator_present") is not False or n.get("direct_authorial_self_identification_present") is not False or n.get("interior_deliberation_report_present") is not True:return fail("Narrative mismatch")
 b=u.get("bibliographic_and_witness_control",{}).get("chapter_boundary_control","")
 for x in ["heading II on PDF page 122","heading III on page 124","next unit therefore covers pages 124-127"]:
  if x not in b:return fail("Boundary safeguard missing: "+x)
 types={o.get("evidence_type") for o in u.get("documentary_observations",[])}
 need={"HERACLEOT_HOSPITALITY_GIFTS_OBSERVATION","THREE_THOUSAND_CYZICENE_DEMAND_OBSERVATION","FRIENDLY_CITY_NONCOMPULSION_OBSERVATION","HERACLEOT_DEFENSIVE_CLOSURE_OBSERVATION","ARCADIAN_ACHAEAN_FACTION_OBSERVATION","NARRATOR_PARTIAL_NUMERICAL_CONFIRMATION_OBSERVATION","TEN_GENERAL_MAJORITY_REGIME_OBSERVATION","CHEIRISOPHUS_MONARCHY_COLLAPSE_OBSERVATION","NEON_EXCLUSIVE_PASSAGE_MOTIVE_OBSERVATION","HERACLES_LEADER_SACRIFICE_OBSERVATION","THREE_DIVISION_FORCE_COUNT_OBSERVATION","ARCADIAN_BOOTY_VOYAGE_OBSERVATION","DIVERGENT_ROUTES_OBSERVATION","COMMENTATOR_SUMMARY_VARIANT_OBSERVATION"}
 if need-types:return fail("VI.2 evidence types missing: "+", ".join(sorted(need-types)))
 text=" ".join(o.get("observation","") for o in u["documentary_observations"]).casefold()
 for x in ["two-day coastal voyage","three thousand measures","three thousand cyzicenes","friendly hellenic city","close the gates","arcadians and achaeans","more than half","ten generals","less than a week","exclusive","heracles the leader","three divisions","four thousand five hundred","calpe haven","commentator's note"]:
  if x not in text:return fail("VI.2 phrase safeguard missing: "+x)
 if [len(u.get(k,[])) for k in ["documentary_observations","speeches_deeds_and_outcomes","provisional_findings","standing_unresolved_questions","downstream_textual_checks"]]!=[30,10,10,16,12]:return fail("VI.2 counts mismatch")
 if "Strauss" in json_text(u):return fail("Primary unit imports Strauss")
 print("Xenophon repository validation passed");return 0
def json_text(x):
 import json
 return json.dumps(x,ensure_ascii=False)
if __name__=="__main__":sys.exit(main())
