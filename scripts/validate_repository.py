from pathlib import Path
import sys,yaml,tempfile,shutil,subprocess,json
R=Path(__file__).resolve().parents[1]
P=R/"scripts/validate_repository_v1_53.py"
M=R/"manifest.yaml"
A=R/"audits/founding-state.yaml"
C=R/"studies/xenophon-anabasis-dakyns/cumulative/XEN-PRIMARY-CUMULATIVE-001.yaml"
O=R/"governance/owner-reviews/2026-07-31-primary-cumulative-reconstruction-review.yaml"
H=R/"history/2026-07-31-anabasis-primary-cumulative-owner-adoption.md"
L=R/"studies/xenophon-anabasis-dakyns/reading-plan.yaml"
def load(p):
 with p.open(encoding="utf-8") as f:return yaml.safe_load(f)
def dump(p,x):
 with p.open("w",encoding="utf-8") as f:yaml.safe_dump(x,f,sort_keys=False,allow_unicode=True)
def fail(x):print(x);return 1
def predecessor():
 if not P.exists():return fail("Frozen v1.53 validator missing")
 with tempfile.TemporaryDirectory() as d:
  t=Path(d)/"r";shutil.copytree(R,t,ignore=shutil.ignore_patterns(".git","__pycache__"))
  for p in [t/O.relative_to(R),t/H.relative_to(R)]:
   if p.exists():p.unlink()
  m=load(t/"manifest.yaml");m["version"]="1.53.0";m["state"]="PRIMARY_CUMULATIVE_RECONSTRUCTION_DRAFT_COMPLETE_PENDING_OWNER_REVIEW";m["owner_reviews"]=m["owner_reviews"][:-1];m["current_phase"]={"id":"XEN-PHASE-003","name":"Primary-only cumulative reconstruction of Xenophon's Anabasis","completion_status":"DRAFT_COMPLETE_PENDING_OWNER_REVIEW"};q=m["primary_study"]["cumulative_reconstruction"];q["status"]="DRAFTED_PENDING_OWNER_REVIEW";q["secondary_comparison_status"]="DEFERRED_PENDING_OWNER_REVIEW";q.pop("adoption_record",None);q.pop("immutable_draft_record",None);m["next_required_action"]={"id":"XEN-PRIMARY-CUMULATIVE-OWNER-REVIEW-001","description":"Owner review of the primary-only cumulative Anabasis reconstruction before controlled comparison with the adopted secondary reconstruction or minister derivation."};dump(t/"manifest.yaml",m)
  a=load(t/"audits/founding-state.yaml");r=a["repository_state"];r.pop("primary_cumulative_reconstruction_owner_adopted",None);r.pop("primary_cumulative_adoption_record",None);r.pop("controlled_comparison_authorized",None);r.pop("controlled_comparison_started",None);a["resolved_items"]=a["resolved_items"][:-1];a["resolved_items"][-1]["description"]="A primary-only cumulative reconstruction was derived across all fifty-one owner-adopted chapter units and remains pending owner review.";a["documented_gaps"][1]={"id":"GAP-007","description":"The primary-only cumulative reconstruction is draft-complete but has not received owner review.","blocks":["controlled comparison with the adopted secondary reconstruction","work-level owner adoption","minister derivation"]};a["next_required_action"]="Conduct owner review of XEN-PRIMARY-CUMULATIVE-001 before controlled secondary comparison, minister adapter construction, or Sanctum registration.";dump(t/"audits/founding-state.yaml",a)
  z=subprocess.run([sys.executable,str(t/"scripts/validate_repository_v1_53.py")],cwd=t,text=True,capture_output=True)
  return fail("predecessor failed: "+(z.stdout+z.stderr).strip()) if z.returncode else 0
def main():
 if predecessor():return 1
 if any(not p.exists() for p in [P,M,A,C,O,H,L]):return fail("Missing cumulative owner-review production file")
 m=load(M);a=load(A);c=load(C);o=load(O);p=load(L);s=m.get("primary_study",{});r=a.get("repository_state",{});q=s.get("cumulative_reconstruction",{})
 if m.get("version")!="1.54.0" or m.get("state")!="PRIMARY_CUMULATIVE_RECONSTRUCTION_OWNER_ADOPTED":return fail("Manifest cumulative adoption mismatch")
 phase=m.get("current_phase",{})
 if phase.get("id")!="XEN-PHASE-004" or phase.get("completion_status")!="AUTHORIZED_NOT_STARTED" or "Controlled comparison" not in phase.get("name",""):return fail("Controlled comparison phase mismatch")
 if m.get("owner_reviews",[])[-1]!=str(O.relative_to(R)):return fail("Owner-review registry mismatch")
 if q.get("id")!="XEN-PRIMARY-CUMULATIVE-001" or q.get("status")!="OWNER_ADOPTED_PRIMARY_CUMULATIVE_RECONSTRUCTION":return fail("Cumulative adoption status mismatch")
 if q.get("adoption_record")!=str(O.relative_to(R)) or q.get("immutable_draft_record") is not True or q.get("secondary_comparison_status")!="AUTHORIZED_NOT_STARTED":return fail("Cumulative adoption controls mismatch")
 if m.get("next_required_action",{}).get("id")!="XEN-CONTROLLED-COMPARISON-001":return fail("Next action mismatch")
 if c.get("record_id")!="XEN-PRIMARY-CUMULATIVE-001" or c.get("status")!="DRAFTED_PENDING_OWNER_REVIEW":return fail("Cumulative production record was rewritten")
 if any(x.get("status")!="DRAFTED_PENDING_OWNER_REVIEW" for x in p.get("reading_units",[])):return fail("Chapter production statuses were rewritten")
 counts=c.get("counts",{})
 expected={"source_units":51,"book_level_movements":7,"major_transformations":8,"recurring_problem_patterns":14,"narrative_person_phases":5,"speech_deed_outcome_findings":10,"provisional_work_level_findings":12,"unresolved_work_level_questions":20,"secondary_comparison_prompts":12}
 if counts!=expected:return fail("Cumulative counts changed during adoption")
 if o.get("review_id")!="XEN-OWNER-REVIEW-004" or o.get("status")!="OWNER_ADOPTED_PRIMARY_CUMULATIVE_RECONSTRUCTION":return fail("Owner ruling identity mismatch")
 scope=o.get("scope",{})
 if scope.get("cumulative_record_id")!="XEN-PRIMARY-CUMULATIVE-001" or scope.get("source_unit_count")!=51 or scope.get("book_level_movements")!=7 or scope.get("unresolved_work_level_questions")!=20:return fail("Owner ruling scope mismatch")
 ruling=o.get("owner_ruling",{})
 if ruling.get("cumulative_status")!="OWNER_ADOPTED_PRIMARY_CUMULATIVE_RECONSTRUCTION" or ruling.get("immutable_draft_rule") is None or ruling.get("controlled_comparison_authorization") is None:return fail("Owner ruling controls missing")
 findings=o.get("review_findings",{})
 if any(v!="PASS" for v in findings.values()) or len(findings)!=12:return fail("Owner review findings mismatch")
 if r.get("primary_cumulative_reconstruction_owner_adopted") is not True or r.get("primary_cumulative_adoption_record")!=str(O.relative_to(R)):return fail("Audit cumulative adoption mismatch")
 if r.get("controlled_comparison_authorized") is not True or r.get("controlled_comparison_started") is not False:return fail("Audit comparison authorization mismatch")
 if a.get("resolved_items",[])[-1].get("id")!="RES-013" or a.get("documented_gaps",[])[1].get("id")!="GAP-008":return fail("Audit transition mismatch")
 sec=m.get("secondary_study",{})
 if sec.get("status")!="OWNER_ADOPTED_SECONDARY_RECONSTRUCTION" or sec.get("immutable_unit_records") is not True:return fail("Secondary reconstruction independence mismatch")
 text=json.dumps(o,ensure_ascii=False,default=str).casefold()
 for x in ["owner-adopted primary cumulative reconstruction","immutable production records","controlled comparison","neither source may absorb","twenty unresolved work-level questions remain open","does not authenticate","artificial-intelligence self-certification remains prohibited"]:
  if x not in text:return fail("Owner-review safeguard missing: "+x)
 ctext=json.dumps(c,ensure_ascii=False,default=str).casefold()
 if "strauss" in ctext:return fail("Primary cumulative record imports secondary interpretation")
 if m.get("artificial_intelligence_self_certification_prohibited") is not True or r.get("minister_adapter_derived") is not False or r.get("sanctum_registration_present") is not False:return fail("Governance gate mismatch")
 h=H.read_text(encoding="utf-8")
 for x in ["fifty-one owner-adopted chapter reconstructions","immutable production records","XEN-OWNER-REVIEW-004","XEN-CONTROLLED-COMPARISON-001","agreement, divergence, silence, and unresolved uncertainty"]:
  if x not in h:return fail("History safeguard missing: "+x)
 print("Xenophon repository validation passed");return 0
if __name__=="__main__":sys.exit(main())
