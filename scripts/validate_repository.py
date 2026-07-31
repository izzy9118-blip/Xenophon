from pathlib import Path
import sys,yaml,tempfile,shutil,subprocess,json
R=Path(__file__).resolve().parents[1]
P=R/"scripts/validate_repository_v1_52.py"
M=R/"manifest.yaml"
A=R/"audits/founding-state.yaml"
C=R/"studies/xenophon-anabasis-dakyns/cumulative/XEN-PRIMARY-CUMULATIVE-001.yaml"
H=R/"history/2026-07-31-anabasis-primary-cumulative-reconstruction.md"
L=R/"studies/xenophon-anabasis-dakyns/reading-plan.yaml"
def load(p):
 with p.open(encoding="utf-8") as f:return yaml.safe_load(f)
def dump(p,x):
 with p.open("w",encoding="utf-8") as f:yaml.safe_dump(x,f,sort_keys=False,allow_unicode=True)
def fail(x):print(x);return 1
def predecessor():
 if not P.exists():return fail("Frozen v1.52 validator missing")
 with tempfile.TemporaryDirectory() as d:
  t=Path(d)/"r";shutil.copytree(R,t,ignore=shutil.ignore_patterns(".git","__pycache__"))
  for p in [t/C.relative_to(R),t/H.relative_to(R)]:
   if p.exists():p.unlink()
  m=load(t/"manifest.yaml");m["version"]="1.52.0";m["state"]="PRIMARY_RECONSTRUCTION_OWNER_ADOPTED";m["current_phase"]["completion_status"]="AUTHORIZED_NOT_STARTED";m["primary_study"].pop("cumulative_reconstruction",None);m["next_required_action"]={"id":"XEN-PRIMARY-CUMULATIVE-001","description":"Produce a primary-only cumulative reconstruction across the owner-adopted fifty-one-unit Dakyns Anabasis study before secondary comparison or minister derivation."};dump(t/"manifest.yaml",m)
  a=load(t/"audits/founding-state.yaml");r=a["repository_state"];r["primary_only_cumulative_reconstruction_started"]=False;r.pop("primary_only_cumulative_reconstruction_draft_complete",None);r.pop("cumulative_reconstruction_record",None);a["resolved_items"]=a["resolved_items"][:-1];a["documented_gaps"][1]={"id":"GAP-006","description":"No primary-only cumulative reconstruction has yet been produced from the owner-adopted fifty-one-unit study.","blocks":["work-level primary synthesis","controlled comparison with Strauss","minister derivation"]};a["next_required_action"]="Produce the primary-only cumulative reconstruction from the owner-adopted fifty-one-unit study before secondary comparison, minister adapter construction, or Sanctum registration.";dump(t/"audits/founding-state.yaml",a)
  z=subprocess.run([sys.executable,str(t/"scripts/validate_repository_v1_52.py")],cwd=t,text=True,capture_output=True)
  return fail("predecessor failed: "+(z.stdout+z.stderr).strip()) if z.returncode else 0
def main():
 if predecessor():return 1
 if any(not p.exists() for p in [P,M,A,C,H,L]):return fail("Missing cumulative-reconstruction production file")
 m=load(M);a=load(A);c=load(C);p=load(L);s=m.get("primary_study",{});r=a.get("repository_state",{})
 ids=[f"XEN-PRI-RU-{i:03d}" for i in range(1,52)]
 if m.get("version")!="1.53.0" or m.get("state")!="PRIMARY_CUMULATIVE_RECONSTRUCTION_DRAFT_COMPLETE_PENDING_OWNER_REVIEW":return fail("Manifest cumulative state mismatch")
 if m.get("current_phase",{}).get("id")!="XEN-PHASE-003" or m.get("current_phase",{}).get("completion_status")!="DRAFT_COMPLETE_PENDING_OWNER_REVIEW":return fail("Phase completion mismatch")
 q=s.get("cumulative_reconstruction",{})
 if q.get("id")!="XEN-PRIMARY-CUMULATIVE-001" or q.get("status")!="DRAFTED_PENDING_OWNER_REVIEW" or q.get("source_unit_count")!=51:return fail("Manifest cumulative record mismatch")
 if q.get("record")!=str(C.relative_to(R)) or q.get("secondary_comparison_status")!="DEFERRED_PENDING_OWNER_REVIEW":return fail("Manifest cumulative gate mismatch")
 if m.get("next_required_action",{}).get("id")!="XEN-PRIMARY-CUMULATIVE-OWNER-REVIEW-001":return fail("Next action mismatch")
 if any(x.get("status")!="DRAFTED_PENDING_OWNER_REVIEW" for x in p.get("reading_units",[])):return fail("Unit production statuses were rewritten")
 if r.get("primary_only_cumulative_reconstruction_started") is not True or r.get("primary_only_cumulative_reconstruction_draft_complete") is not True:return fail("Audit cumulative state mismatch")
 if r.get("cumulative_reconstruction_record")!=str(C.relative_to(R)):return fail("Audit cumulative record mismatch")
 if a.get("resolved_items",[])[-1].get("id")!="RES-012" or a.get("documented_gaps",[])[1].get("id")!="GAP-007":return fail("Audit transition mismatch")
 if c.get("record_id")!="XEN-PRIMARY-CUMULATIVE-001" or c.get("status")!="DRAFTED_PENDING_OWNER_REVIEW":return fail("Cumulative identity mismatch")
 b=c.get("derivation_basis",{})
 if b.get("source_unit_count")!=51 or b.get("source_unit_coverage")!=ids:return fail("Cumulative source coverage mismatch")
 counts=c.get("counts",{})
 expected={"source_units":51,"book_level_movements":7,"major_transformations":8,"recurring_problem_patterns":14,"narrative_person_phases":5,"speech_deed_outcome_findings":10,"provisional_work_level_findings":12,"unresolved_work_level_questions":20,"secondary_comparison_prompts":12}
 if counts!=expected:return fail("Cumulative counts mismatch")
 if len(c.get("book_level_movements",[]))!=7 or [x.get("book") for x in c.get("book_level_movements",[])]!=["I","II","III","IV","V","VI","VII"]:return fail("Book movement mismatch")
 all_anchors=set()
 for section in ["major_transformations","recurring_problem_patterns","narrative_person_development","speech_deed_outcome_findings","provisional_work_level_findings","unresolved_work_level_questions"]:
  for x in c.get(section,[]):
   all_anchors.update(x.get("evidence_units",x.get("units",[])))
 if not set(ids).issubset(all_anchors):return fail("Not all source units participate in cumulative evidence anchors")
 text=json.dumps(c,ensure_ascii=False,default=str).casefold()
 for x in ["cyrus's concealed bid for kingship","project of survival and return","mobile political community","speech tested by deed and outcome","piety, divination, and deliberation","founding, settlement, and the limits of the return project","transfer of the troops to another war","thibron","homecoming","translation adjudication"]:
  if x not in text:return fail("Cumulative safeguard missing: "+x)
 if "strauss" in text:return fail("Primary cumulative record imports secondary interpretation")
 if c.get("secondary_comparison_status")!="DEFERRED_PENDING_OWNER_REVIEW":return fail("Secondary comparison gate mismatch")
 if m.get("artificial_intelligence_self_certification_prohibited") is not True or r.get("minister_adapter_derived") is not False or r.get("sanctum_registration_present") is not False:return fail("Governance gate mismatch")
 h=H.read_text(encoding="utf-8")
 for x in ["fifty-one owner-adopted chapter reconstructions","14 recurring problem-patterns","20 unresolved work-level questions","pending owner review","Secondary comparison remains deferred"]:
  if x not in h:return fail("History safeguard missing: "+x)
 print("Xenophon repository validation passed");return 0
if __name__=="__main__":sys.exit(main())
