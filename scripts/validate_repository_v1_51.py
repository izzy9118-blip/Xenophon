from pathlib import Path
import sys,yaml,tempfile,shutil,subprocess,json
R=Path(__file__).resolve().parents[1];P=R/"scripts/validate_repository_v1_50.py";U=R/"studies/xenophon-anabasis-dakyns/units/XEN-PRI-RU-051.yaml";L=R/"studies/xenophon-anabasis-dakyns/reading-plan.yaml";A=R/"audits/founding-state.yaml";H=R/"history/2026-07-31-anabasis-vii8-poverty-sacrifice-asidates-thibron.md";B=R/"history/2026-07-31-anabasis-book-vii-draft-completion.md";C=R/"history/2026-07-31-anabasis-primary-sequential-draft-completion.md"
def load(p):
 with p.open(encoding="utf-8") as f:return yaml.safe_load(f)
def dump(p,x):
 with p.open("w",encoding="utf-8") as f:yaml.safe_dump(x,f,sort_keys=False,allow_unicode=True)
def fail(x):print(x);return 1
def predecessor():
 if not P.exists():return fail("Frozen v1.50 validator missing")
 with tempfile.TemporaryDirectory() as d:
  t=Path(d)/"r";shutil.copytree(R,t,ignore=shutil.ignore_patterns(".git","__pycache__"))
  for p in [t/"studies/xenophon-anabasis-dakyns/units/XEN-PRI-RU-051.yaml",t/"history/2026-07-31-anabasis-vii8-poverty-sacrifice-asidates-thibron.md",t/"history/2026-07-31-anabasis-book-vii-draft-completion.md",t/"history/2026-07-31-anabasis-primary-sequential-draft-completion.md"]:
   if p.exists():p.unlink()
  m=load(t/"manifest.yaml");m["version"]="1.50.0";m["state"]="PRIMARY_RECONSTRUCTION_IN_PROGRESS";m["current_phase"]["completion_status"]="IN_PROGRESS";s=m["primary_study"];s["status"]="SEQUENTIAL_PRIMARY_READING_IN_PROGRESS_PENDING_OWNER_REVIEW";s["drafted_units"]=s["drafted_units"][:-1];s["book_seven_drafted_chapters"]=[f"VII.{i}" for i in range(1,8)];s.pop("book_seven_draft_complete_pending_owner_review",None);s.pop("all_books_draft_complete_pending_owner_review",None);m["next_required_unit"]={"id":"XEN-PRI-RU-051","description":"Complete the independent primary reconstruction with Anabasis VII.8 using the Dakyns Project Gutenberg witness."};m.pop("next_required_action",None);dump(t/"manifest.yaml",m)
  q=load(t/"studies/xenophon-anabasis-dakyns/reading-plan.yaml");q["status"]="SEQUENTIAL_PRIMARY_READING_IN_PROGRESS_PENDING_OWNER_REVIEW";q.pop("completion_status",None);q["reading_units"][-1]["status"]="NEXT";q["remaining_sequence"]="Anabasis VII.8, strictly in chapter order.";q["comparison_gate"]={"strauss_comparison":"DEFERRED","rule":"Primary sequence first."};dump(t/"studies/xenophon-anabasis-dakyns/reading-plan.yaml",q)
  a=load(t/"audits/founding-state.yaml");r=a["repository_state"];r["drafted_primary_units"]=50;r["book_seven_drafted_chapters"]=[f"VII.{i}" for i in range(1,8)];r.pop("book_seven_primary_draft_complete",None);r.pop("primary_sequential_draft_complete",None);a["resolved_items"]=a["resolved_items"][:8];a["documented_gaps"][1]={"id":"GAP-005","description":"The primary Anabasis reconstruction remains incomplete; Books I through VI are drafted pending owner review, and Book VII has drafted coverage through VII.7.","blocks":["complete primary argument map","systematic deed extraction","speech-register derivation","operational capacity derivation"]};a["next_required_action"]="Complete XEN-PRI-RU-051 for Anabasis VII.8 without importing secondary interpretation or treating translated wording as unmediated Greek evidence.";dump(t/"audits/founding-state.yaml",a)
  z=subprocess.run([sys.executable,str(t/"scripts/validate_repository_v1_50.py")],cwd=t,text=True,capture_output=True);return fail("predecessor failed: "+(z.stdout+z.stderr).strip()) if z.returncode else 0
def main():
 if predecessor():return 1
 if any(not x.exists() for x in [U,L,A,H,B,C,P,R/"manifest.yaml"]):return fail("Missing VII.8 completion production file")
 m=load(R/"manifest.yaml");p=load(L);a=load(A);u=load(U);ids=[f"XEN-PRI-RU-{n:03d}" for n in range(1,52)];q=p.get("reading_units",[]);s=m.get("primary_study",{});r=a.get("repository_state",{})
 if m.get("version")!="1.51.0" or m.get("state")!="PRIMARY_RECONSTRUCTION_DRAFT_COMPLETE_PENDING_OWNER_REVIEW" or m.get("current_phase",{}).get("completion_status")!="DRAFT_COMPLETE_PENDING_OWNER_REVIEW":return fail("Manifest completion mismatch")
 if m.get("artificial_intelligence_self_certification_prohibited") is not True or m.get("minister",{}).get("registration_status")!="NOT_YET_REGISTERED_IN_SANCTUM":return fail("Governance mismatch")
 if s.get("drafted_units")!=ids or s.get("book_seven_drafted_chapters")!=[f"VII.{i}" for i in range(1,9)] or s.get("book_seven_draft_complete_pending_owner_review") is not True or s.get("all_books_draft_complete_pending_owner_review") is not True:return fail("Primary completion mismatch")
 if m.get("next_required_unit") is not None or m.get("next_required_action",{}).get("id")!="XEN-PRIMARY-OWNER-REVIEW-001":return fail("Next action mismatch")
 if [x.get("id") for x in q]!=ids or any(x.get("status")!="DRAFTED_PENDING_OWNER_REVIEW" for x in q) or q[-1].get("work_locator")!="Anabasis VII.8" or q[-1].get("pdf_pages_one_based")!="164-168" or p.get("completion_status")!="DRAFT_COMPLETE_PENDING_OWNER_REVIEW":return fail("Plan completion mismatch")
 if "None. All fifty-one numbered chapters" not in p.get("remaining_sequence","") or p.get("comparison_gate",{}).get("strauss_comparison")!="DEFERRED":return fail("Plan gate mismatch")
 if r.get("drafted_primary_units")!=51 or r.get("book_seven_primary_draft_complete") is not True or r.get("primary_sequential_draft_complete") is not True or r.get("book_seven_drafted_chapters")!=[f"VII.{i}" for i in range(1,9)] or r.get("minister_adapter_derived") is not False or r.get("sanctum_registration_present") is not False:return fail("Audit completion mismatch")
 if [x.get("id") for x in a.get("resolved_items",[])[-2:]]!=["RES-009","RES-010"] or "owner review" not in a.get("documented_gaps",[])[1].get("description","").casefold():return fail("Audit milestone mismatch")
 if u.get("unit_id")!="XEN-PRI-RU-051" or u.get("status")!="DRAFTED_PENDING_OWNER_REVIEW" or u.get("scope",{}).get("pdf_pages_one_based")!="164-168" or u.get("secondary_comparison_status")!="DEFERRED":return fail("Unit mismatch")
 if "Translator wording is not unmediated Greek evidence" not in u.get("jurisdiction",""):return fail("Translation safeguard missing")
 if [len(u.get(k,[])) for k in ["documentary_observations","speeches_deeds_and_outcomes","provisional_findings","standing_unresolved_questions","downstream_textual_checks"]]!=[30,10,10,16,12]:return fail("VII.8 counts mismatch")
 if "Strauss" in json.dumps(u,ensure_ascii=False):return fail("Primary unit imports secondary interpretation")
 print("Xenophon repository validation passed");return 0
if __name__=="__main__":sys.exit(main())
