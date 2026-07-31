from pathlib import Path
import sys,yaml,tempfile,shutil,subprocess,json
R=Path(__file__).resolve().parents[1]
P=R/"scripts/validate_repository_v1_51.py"
M=R/"manifest.yaml"
A=R/"audits/founding-state.yaml"
O=R/"governance/owner-reviews/2026-07-31-primary-anabasis-reconstruction-review.yaml"
H=R/"history/2026-07-31-anabasis-primary-owner-adoption.md"
L=R/"studies/xenophon-anabasis-dakyns/reading-plan.yaml"
def load(p):
 with p.open(encoding="utf-8") as f:return yaml.safe_load(f)
def dump(p,x):
 with p.open("w",encoding="utf-8") as f:yaml.safe_dump(x,f,sort_keys=False,allow_unicode=True)
def fail(x):print(x);return 1
def predecessor():
 if not P.exists():return fail("Frozen v1.51 validator missing")
 with tempfile.TemporaryDirectory() as d:
  t=Path(d)/"r";shutil.copytree(R,t,ignore=shutil.ignore_patterns(".git","__pycache__"))
  for p in [t/O.relative_to(R),t/H.relative_to(R)]:
   if p.exists():p.unlink()
  m=load(t/"manifest.yaml");m["version"]="1.51.0";m["state"]="PRIMARY_RECONSTRUCTION_DRAFT_COMPLETE_PENDING_OWNER_REVIEW";m["owner_reviews"]=m["owner_reviews"][:-1];m["current_phase"]={"id":"XEN-PHASE-002","name":"Sequential primary reconstruction of Xenophon's Anabasis","completion_status":"DRAFT_COMPLETE_PENDING_OWNER_REVIEW"};s=m["primary_study"];s["status"]="SEQUENTIAL_PRIMARY_READING_DRAFT_COMPLETE_PENDING_OWNER_REVIEW";s.pop("adoption_record",None);s.pop("immutable_unit_records",None);s.pop("collective_owner_adoption",None);m["next_required_action"]={"id":"XEN-PRIMARY-OWNER-REVIEW-001","description":"Owner review of the complete fifty-one-unit Dakyns Anabasis reconstruction before primary-only cumulative derivation or secondary comparison."};dump(t/"manifest.yaml",m)
  a=load(t/"audits/founding-state.yaml");r=a["repository_state"];r.pop("primary_reconstruction_owner_adopted",None);r.pop("primary_adoption_record",None);r.pop("primary_only_cumulative_reconstruction_started",None);r["book_milestones_pending_owner_review"]=True;a["resolved_items"]=a["resolved_items"][:-1];a["documented_gaps"][1]={"id":"GAP-005","description":"The fifty-one-unit Dakyns Anabasis reconstruction is draft-complete but has not received owner review or cross-witness adjudication.","blocks":["owner-adopted primary reconstruction","primary-only cumulative derivation","secondary comparison","minister derivation"]};a["next_required_action"]="Conduct owner review of the complete fifty-one-unit primary reconstruction before cumulative derivation, secondary comparison, minister adapter construction, or Sanctum registration.";dump(t/"audits/founding-state.yaml",a)
  z=subprocess.run([sys.executable,str(t/"scripts/validate_repository_v1_51.py")],cwd=t,text=True,capture_output=True)
  return fail("predecessor failed: "+(z.stdout+z.stderr).strip()) if z.returncode else 0
def main():
 if predecessor():return 1
 if any(not p.exists() for p in [P,M,A,O,H,L]):return fail("Missing owner-adoption production file")
 m=load(M);a=load(A);o=load(O);p=load(L);s=m.get("primary_study",{});r=a.get("repository_state",{})
 if m.get("version")!="1.52.0" or m.get("state")!="PRIMARY_RECONSTRUCTION_OWNER_ADOPTED":return fail("Manifest adoption mismatch")
 if m.get("current_phase",{}).get("id")!="XEN-PHASE-003" or m.get("current_phase",{}).get("completion_status")!="AUTHORIZED_NOT_STARTED":return fail("Phase mismatch")
 if s.get("status")!="OWNER_ADOPTED_PRIMARY_TRANSLATION_RECONSTRUCTION" or s.get("collective_owner_adoption") is not True:return fail("Study adoption mismatch")
 if s.get("adoption_record")!=str(O.relative_to(R)) or len(s.get("drafted_units",[]))!=51:return fail("Adoption record or coverage mismatch")
 if o.get("review_id")!="XEN-OWNER-REVIEW-003" or o.get("status")!="OWNER_ADOPTED_PRIMARY_TRANSLATION_RECONSTRUCTION" or o.get("scope",{}).get("unit_count")!=51:return fail("Owner ruling mismatch")
 if o.get("owner_ruling",{}).get("immutable_draft_rule") is None:return fail("Immutable draft rule missing")
 if any(x.get("status")!="DRAFTED_PENDING_OWNER_REVIEW" for x in p.get("reading_units",[])):return fail("Unit production statuses were rewritten")
 if r.get("primary_reconstruction_owner_adopted") is not True or r.get("primary_only_cumulative_reconstruction_started") is not False:return fail("Audit adoption mismatch")
 if a.get("resolved_items",[])[-1].get("id")!="RES-011" or a.get("documented_gaps",[])[1].get("id")!="GAP-006":return fail("Audit transition mismatch")
 if m.get("next_required_action",{}).get("id")!="XEN-PRIMARY-CUMULATIVE-001":return fail("Next action mismatch")
 if m.get("artificial_intelligence_self_certification_prohibited") is not True or r.get("minister_adapter_derived") is not False or r.get("sanctum_registration_present") is not False:return fail("Governance gate mismatch")
 text=json.dumps(o,ensure_ascii=False,default=str).casefold()
 for x in ["admitted h. g. dakyns english translation witness","does not authenticate","provisional findings remain provisional","strauss's interpretation remains a distinct secondary reconstruction","artificial-intelligence self-certification remains prohibited"]:
  if x not in text:return fail("Owner-review safeguard missing: "+x)
 h=H.read_text(encoding="utf-8")
 for x in ["fifty-one-unit sequential reconstruction","immutable production records","primary-only cumulative reconstruction"]:
  if x not in h:return fail("History safeguard missing: "+x)
 print("Xenophon repository validation passed");return 0
if __name__=="__main__":sys.exit(main())
