from pathlib import Path
from collections import Counter
import sys,yaml,tempfile,shutil,subprocess,json
R=Path(__file__).resolve().parents[1]
P=R/"scripts/validate_repository_v1_54.py"
M=R/"manifest.yaml"
A=R/"audits/founding-state.yaml"
C=R/"studies/comparisons/anabasis-primary-strauss/XEN-CONTROLLED-COMPARISON-001.yaml"
E=[R/f"studies/comparisons/anabasis-primary-strauss/entries/{name}.yaml" for name in ["agreement","qualified-agreement","divergence","primary-silence","secondary-silence","unresolved-relation"]]
H=R/"history/2026-07-31-anabasis-controlled-comparison-strauss.md"
PC=R/"studies/xenophon-anabasis-dakyns/cumulative/XEN-PRIMARY-CUMULATIVE-001.yaml"
PO=R/"governance/owner-reviews/2026-07-31-primary-cumulative-reconstruction-review.yaml"
SO=R/"governance/owner-reviews/2026-07-30-strauss-witness-review.yaml"
L=R/"studies/xenophon-anabasis-dakyns/reading-plan.yaml"
S=[R/f"studies/strauss-xenophons-anabasis/units/XEN-RU-{i:03d}.yaml" for i in range(1,9)]
def load(p):
 with p.open(encoding="utf-8") as f:return yaml.safe_load(f)
def dump(p,x):
 with p.open("w",encoding="utf-8") as f:yaml.safe_dump(x,f,sort_keys=False,allow_unicode=True)
def fail(x):print(x);return 1
def predecessor():
 if not P.exists():return fail("Frozen v1.54 validator missing")
 with tempfile.TemporaryDirectory() as d:
  t=Path(d)/"r";shutil.copytree(R,t,ignore=shutil.ignore_patterns(".git","__pycache__"))
  for p in [t/C.relative_to(R),t/H.relative_to(R),*[t/x.relative_to(R) for x in E]]:
   if p.exists():p.unlink()
  m=load(t/"manifest.yaml");m["version"]="1.54.0";m["state"]="PRIMARY_CUMULATIVE_RECONSTRUCTION_OWNER_ADOPTED";m["current_phase"]["completion_status"]="AUTHORIZED_NOT_STARTED";m.pop("controlled_comparison",None);m["primary_study"]["cumulative_reconstruction"]["secondary_comparison_status"]="AUTHORIZED_NOT_STARTED";m["next_required_action"]={"id":"XEN-CONTROLLED-COMPARISON-001","description":"Compare the owner-adopted primary cumulative Anabasis reconstruction with the separately owner-adopted Strauss reconstruction while preserving source independence, disagreement, silence, and unresolved uncertainty."};dump(t/"manifest.yaml",m)
  a=load(t/"audits/founding-state.yaml");r=a["repository_state"];r["controlled_comparison_started"]=False;r.pop("controlled_comparison_draft_complete",None);r.pop("controlled_comparison_record",None);r.pop("controlled_comparison_owner_reviewed",None);a["resolved_items"]=a["resolved_items"][:-1];a["documented_gaps"][1]={"id":"GAP-008","description":"No controlled comparison has yet been produced between the owner-adopted primary cumulative reconstruction and the separately owner-adopted Strauss reconstruction.","blocks":["primary-secondary agreement map","primary-secondary divergence map","controlled interpretive synthesis","minister derivation"]};a["next_required_action"]="Produce XEN-CONTROLLED-COMPARISON-001 while preserving primary and secondary source independence, explicit agreement, divergence, silence, and unresolved uncertainty before minister adapter construction or Sanctum registration.";dump(t/"audits/founding-state.yaml",a)
  z=subprocess.run([sys.executable,str(t/"scripts/validate_repository_v1_54.py")],cwd=t,text=True,capture_output=True)
  return fail("predecessor failed: "+(z.stdout+z.stderr).strip()) if z.returncode else 0
def main():
 if predecessor():return 1
 required=[P,M,A,C,H,PC,PO,SO,L,*S,*E]
 if any(not p.exists() for p in required):return fail("Missing controlled-comparison production file")
 m=load(M);a=load(A);c=load(C);pc=load(PC);p=load(L);r=a.get("repository_state",{});q=m.get("controlled_comparison",{})
 if m.get("version")!="1.55.0" or m.get("state")!="CONTROLLED_COMPARISON_DRAFT_COMPLETE_PENDING_OWNER_REVIEW":return fail("Manifest comparison state mismatch")
 phase=m.get("current_phase",{})
 if phase.get("id")!="XEN-PHASE-004" or phase.get("completion_status")!="DRAFT_COMPLETE_PENDING_OWNER_REVIEW" or "Controlled comparison" not in phase.get("name",""):return fail("Comparison phase mismatch")
 if q.get("id")!="XEN-CONTROLLED-COMPARISON-001" or q.get("status")!="DRAFTED_PENDING_OWNER_REVIEW" or q.get("record")!=str(C.relative_to(R)):return fail("Manifest comparison record mismatch")
 if q.get("primary_prompt_count")!=12 or q.get("secondary_unit_count")!=8 or q.get("comparison_entry_count")!=31 or q.get("owner_review_status")!="PENDING" or q.get("source_independence_preserved") is not True:return fail("Manifest comparison controls mismatch")
 expected_classes={"AGREEMENT":11,"QUALIFIED_AGREEMENT":9,"DIVERGENCE":2,"PRIMARY_SILENCE":4,"SECONDARY_SILENCE":2,"UNRESOLVED_RELATION":3}
 if q.get("classification_counts")!=expected_classes:return fail("Manifest classification counts mismatch")
 if m.get("primary_study",{}).get("cumulative_reconstruction",{}).get("secondary_comparison_status")!="DRAFT_COMPLETE_PENDING_OWNER_REVIEW":return fail("Primary comparison gate mismatch")
 if m.get("next_required_action",{}).get("id")!="XEN-CONTROLLED-COMPARISON-OWNER-REVIEW-001":return fail("Next action mismatch")
 if r.get("controlled_comparison_authorized") is not True or r.get("controlled_comparison_started") is not True or r.get("controlled_comparison_draft_complete") is not True or r.get("controlled_comparison_owner_reviewed") is not False:return fail("Audit comparison state mismatch")
 if r.get("controlled_comparison_record")!=str(C.relative_to(R)):return fail("Audit comparison record mismatch")
 if a.get("resolved_items",[])[-1].get("id")!="RES-014" or a.get("documented_gaps",[])[1].get("id")!="GAP-009":return fail("Audit comparison transition mismatch")
 if c.get("comparison_id")!="XEN-CONTROLLED-COMPARISON-001" or c.get("status")!="DRAFTED_PENDING_OWNER_REVIEW":return fail("Comparison identity mismatch")
 inputs=c.get("inputs",{});pri=inputs.get("primary_stream",{});sec=inputs.get("secondary_stream",{})
 if pri.get("record_id")!="XEN-PRIMARY-CUMULATIVE-001" or pri.get("source_unit_count")!=51 or pri.get("comparison_prompt_ids")!=[f"CP-{i:03d}" for i in range(1,13)]:return fail("Primary comparison input mismatch")
 if sec.get("study_id")!="XEN-STUDY-SEC-001" or sec.get("secondary_units")!=[f"XEN-RU-{i:03d}" for i in range(1,9)] or sec.get("printed_pages")!="105-136" or sec.get("pdf_pages_one_based")!="109-140":return fail("Secondary comparison input mismatch")
 vocab=c.get("classification_vocabulary",{})
 if set(vocab)!=set(expected_classes):return fail("Classification vocabulary mismatch")
 sets=c.get("entry_sets",[])
 expected_files={
  "AGREEMENT":"studies/comparisons/anabasis-primary-strauss/entries/agreement.yaml",
  "QUALIFIED_AGREEMENT":"studies/comparisons/anabasis-primary-strauss/entries/qualified-agreement.yaml",
  "DIVERGENCE":"studies/comparisons/anabasis-primary-strauss/entries/divergence.yaml",
  "PRIMARY_SILENCE":"studies/comparisons/anabasis-primary-strauss/entries/primary-silence.yaml",
  "SECONDARY_SILENCE":"studies/comparisons/anabasis-primary-strauss/entries/secondary-silence.yaml",
  "UNRESOLVED_RELATION":"studies/comparisons/anabasis-primary-strauss/entries/unresolved-relation.yaml"}
 if len(sets)!=6 or {x.get("classification"):x.get("record") for x in sets}!=expected_files or {x.get("classification"):x.get("entry_count") for x in sets}!=expected_classes:return fail("Comparison entry-set index mismatch")
 entries=[]
 for ep in E:
  shard=load(ep);cls=shard.get("classification");arr=shard.get("entries",[])
  if shard.get("comparison_id")!="XEN-CONTROLLED-COMPARISON-001" or shard.get("status")!="DRAFTED_PENDING_OWNER_REVIEW" or cls not in expected_classes or shard.get("entry_count")!=expected_classes[cls] or len(arr)!=expected_classes[cls]:return fail("Comparison shard mismatch: "+str(ep))
  if any(x.get("classification")!=cls for x in arr):return fail("Mixed classification shard: "+str(ep))
  entries.extend(arr)
 if len(entries)!=31 or Counter(x.get("classification") for x in entries)!=Counter(expected_classes):return fail("Comparison entry count mismatch")
 prompts=set();sunits=set()
 for x in entries:
  if not x.get("id") or not x.get("topic") or x.get("classification") not in expected_classes:return fail("Malformed comparison entry")
  ps=x.get("primary_stream",{});ss=x.get("secondary_stream",{})
  if not ps.get("position") or not ps.get("cumulative_anchors") or not ps.get("source_units"):return fail("Primary stream missing in comparison entry "+x.get("id",""))
  if not ss.get("position") or not ss.get("secondary_units") or not ss.get("printed_pages"):return fail("Secondary stream missing in comparison entry "+x.get("id",""))
  if not x.get("controlled_relation") or not x.get("preserved_uncertainty") or not x.get("comparison_effect"):return fail("Comparison control missing in "+x.get("id",""))
  prompts.update(y for y in ps.get("cumulative_anchors",[]) if str(y).startswith("CP-"));sunits.update(ss.get("secondary_units",[]))
 if prompts!={f"CP-{i:03d}" for i in range(1,13)}:return fail("Not all primary comparison prompts are represented")
 if sunits!={f"XEN-RU-{i:03d}" for i in range(1,9)}:return fail("Not all Strauss units are represented")
 counts=c.get("counts",{})
 expected_counts={"comparison_entries":31,"agreement":11,"qualified_agreement":9,"divergence":2,"primary_silence":4,"secondary_silence":2,"unresolved_relation":3,"cross_cutting_findings":12,"unresolved_comparison_questions":16,"primary_comparison_prompts_covered":12,"secondary_units_covered":8}
 if counts!=expected_counts:return fail("Comparison aggregate counts mismatch")
 if len(c.get("cross_cutting_findings",[]))!=12 or len(c.get("unresolved_comparison_questions",[]))!=16:return fail("Comparison finding or question counts mismatch")
 text=(json.dumps(c,ensure_ascii=False,default=str)+" "+" ".join(json.dumps(load(x),ensure_ascii=False,default=str) for x in E)).casefold()
 for phrase in ["agreement is not certification","divergence is not error","primary and secondary claims are stored in separate fields","without merging their evidence streams","themistogenes","socrates","thibron","material governance","manly and socratic justice","owner_review_required","artificial-intelligence self-certification remains prohibited"]:
  if phrase not in text:return fail("Comparison safeguard missing: "+phrase)
 if pc.get("record_id")!="XEN-PRIMARY-CUMULATIVE-001" or pc.get("status")!="DRAFTED_PENDING_OWNER_REVIEW":return fail("Primary cumulative record was rewritten")
 if any(load(x).get("status")!="DRAFTED_PENDING_OWNER_REVIEW" for x in S):return fail("Secondary unit production status was rewritten")
 if any(x.get("status")!="DRAFTED_PENDING_OWNER_REVIEW" for x in p.get("reading_units",[])):return fail("Primary chapter production status was rewritten")
 if m.get("secondary_study",{}).get("status")!="OWNER_ADOPTED_SECONDARY_RECONSTRUCTION" or m.get("primary_study",{}).get("cumulative_reconstruction",{}).get("status")!="OWNER_ADOPTED_PRIMARY_CUMULATIVE_RECONSTRUCTION":return fail("Adopted input state mismatch")
 if m.get("artificial_intelligence_self_certification_prohibited") is not True or r.get("minister_adapter_derived") is not False or r.get("sanctum_registration_present") is not False:return fail("Governance gate mismatch")
 hist=H.read_text(encoding="utf-8")
 for phrase in ["31 entries","11 `AGREEMENT`","9 `QUALIFIED_AGREEMENT`","All twelve primary comparison prompts and all eight Strauss units","Agreement is not certification","XEN-CONTROLLED-COMPARISON-OWNER-REVIEW-001"]:
  if phrase not in hist:return fail("History safeguard missing: "+phrase)
 print("Xenophon repository validation passed");return 0
if __name__=="__main__":sys.exit(main())
