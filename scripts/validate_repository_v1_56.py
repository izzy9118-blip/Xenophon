from pathlib import Path
from collections import Counter
import sys,yaml,tempfile,shutil,subprocess,json
R=Path(__file__).resolve().parents[1]
P=R/"scripts/validate_repository_v1_55.py"
M=R/"manifest.yaml"
A=R/"audits/founding-state.yaml"
OLD=R/"studies/comparisons/anabasis-primary-strauss/XEN-CONTROLLED-COMPARISON-001.yaml"
NEW=R/"studies/comparisons/anabasis-primary-strauss/XEN-CONTROLLED-COMPARISON-001-R1.yaml"
COR=R/"governance/corrections/2026-07-31-controlled-comparison-strauss-guiding-architecture.yaml"
CY=R/"studies/comparisons/anabasis-primary-strauss/entries/cyrus-side-elaboration.yaml"
GE=R/"studies/comparisons/anabasis-primary-strauss/entries/governing-examination.yaml"
H=R/"history/2026-07-31-controlled-comparison-strauss-guiding-correction.md"
RETAINED=[R/f"studies/comparisons/anabasis-primary-strauss/entries/{name}.yaml" for name in ["agreement","qualified-agreement","primary-silence","unresolved-relation"]]
HISTORICAL=[R/"studies/comparisons/anabasis-primary-strauss/entries/divergence.yaml",R/"studies/comparisons/anabasis-primary-strauss/entries/secondary-silence.yaml"]
def load(p):
 with p.open(encoding="utf-8") as f:return yaml.safe_load(f)
def dump(p,x):
 with p.open("w",encoding="utf-8") as f:yaml.safe_dump(x,f,sort_keys=False,allow_unicode=True)
def fail(x):print(x);return 1
def predecessor():
 if not P.exists():return fail("Frozen v1.55 validator missing")
 with tempfile.TemporaryDirectory() as d:
  t=Path(d)/"r";shutil.copytree(R,t,ignore=shutil.ignore_patterns(".git","__pycache__"))
  for p in [NEW,COR,CY,GE,H]:
   q=t/p.relative_to(R)
   if q.exists():q.unlink()
  m=load(t/"manifest.yaml")
  m["version"]="1.55.0"
  m["state"]="CONTROLLED_COMPARISON_DRAFT_COMPLETE_PENDING_OWNER_REVIEW"
  m["source_policy"]["secondary_authority"]="Later interpretation may guide questions but may not replace primary reconstruction"
  m["current_phase"]={"id":"XEN-PHASE-004","name":"Controlled comparison of the owner-adopted primary Anabasis reconstruction with Strauss's Xenophon's Anabasis","completion_status":"DRAFT_COMPLETE_PENDING_OWNER_REVIEW"}
  m["primary_study"]["cumulative_reconstruction"]["secondary_comparison_status"]="DRAFT_COMPLETE_PENDING_OWNER_REVIEW"
  m["next_required_action"]={"id":"XEN-CONTROLLED-COMPARISON-OWNER-REVIEW-001","description":"Owner review of XEN-CONTROLLED-COMPARISON-001 before any adopted interpretive synthesis, minister derivation, or Sanctum registration."}
  m["controlled_comparison"]={"id":"XEN-CONTROLLED-COMPARISON-001","status":"DRAFTED_PENDING_OWNER_REVIEW","record":"studies/comparisons/anabasis-primary-strauss/XEN-CONTROLLED-COMPARISON-001.yaml","primary_record":"studies/xenophon-anabasis-dakyns/cumulative/XEN-PRIMARY-CUMULATIVE-001.yaml","secondary_study_id":"XEN-STUDY-SEC-001","primary_prompt_count":12,"secondary_unit_count":8,"comparison_entry_count":31,"classification_counts":{"AGREEMENT":11,"QUALIFIED_AGREEMENT":9,"DIVERGENCE":2,"PRIMARY_SILENCE":4,"SECONDARY_SILENCE":2,"UNRESOLVED_RELATION":3},"owner_review_status":"PENDING","source_independence_preserved":True}
  dump(t/"manifest.yaml",m)
  a=load(t/"audits/founding-state.yaml");r=a["repository_state"]
  r["controlled_comparison_record"]="studies/comparisons/anabasis-primary-strauss/XEN-CONTROLLED-COMPARISON-001.yaml"
  for k in ["controlled_comparison_original_record","controlled_comparison_corrected","controlled_comparison_correction_record","controlled_comparison_strauss_guiding_architecture","controlled_comparison_governing_opposition"]:r.pop(k,None)
  a["resolved_items"]=a["resolved_items"][:-1]
  a["resolved_items"][-1]={"id":"RES-014","description":"A controlled comparison was drafted between the owner-adopted primary cumulative Anabasis reconstruction and the separately owner-adopted Strauss reconstruction, preserving agreement, qualified agreement, divergence, primary silence, secondary silence, and unresolved relation.","record":"studies/comparisons/anabasis-primary-strauss/XEN-CONTROLLED-COMPARISON-001.yaml"}
  a["documented_gaps"][1]={"id":"GAP-009","description":"The controlled primary-Strauss comparison is draft-complete but has not received owner review.","blocks":["owner-adopted comparative reconstruction","controlled interpretive synthesis","minister derivation"]}
  a["next_required_action"]="Conduct owner review of XEN-CONTROLLED-COMPARISON-001 before any adopted interpretive synthesis, minister adapter construction, or Sanctum registration."
  dump(t/"audits/founding-state.yaml",a)
  z=subprocess.run([sys.executable,str(t/"scripts/validate_repository_v1_55.py")],cwd=t,text=True,capture_output=True)
  return fail("predecessor failed: "+(z.stdout+z.stderr).strip()) if z.returncode else 0
def main():
 if predecessor():return 1
 required=[P,M,A,OLD,NEW,COR,CY,GE,H,*RETAINED,*HISTORICAL]
 if any(not p.exists() for p in required):return fail("Missing corrected-comparison production file")
 m=load(M);a=load(A);old=load(OLD);new=load(NEW);cor=load(COR);r=a.get("repository_state",{});q=m.get("controlled_comparison",{})
 if m.get("version")!="1.56.0" or m.get("state")!="CONTROLLED_COMPARISON_CORRECTED_DRAFT_COMPLETE_PENDING_OWNER_REVIEW":return fail("Manifest corrected-comparison state mismatch")
 phase=m.get("current_phase",{})
 if phase.get("id")!="XEN-PHASE-004" or phase.get("completion_status")!="CORRECTED_DRAFT_COMPLETE_PENDING_OWNER_REVIEW" or "Strauss-guided" not in phase.get("name",""):return fail("Corrected phase mismatch")
 if m.get("source_policy",{}).get("secondary_authority")!="Strauss may govern the interpretive question architecture after independent primary reconstruction but may not replace documentary evidence":return fail("Strauss guidance policy mismatch")
 if q.get("id")!="XEN-CONTROLLED-COMPARISON-001" or q.get("revision_id")!="XEN-CONTROLLED-COMPARISON-001-R1" or q.get("status")!="CORRECTED_DRAFT_PENDING_OWNER_REVIEW":return fail("Corrected comparison identity mismatch")
 if q.get("record")!=str(NEW.relative_to(R)) or q.get("predecessor_record")!=str(OLD.relative_to(R)) or q.get("correction_record")!=str(COR.relative_to(R)):return fail("Corrected comparison path mismatch")
 if q.get("strauss_guiding_architecture") is not True or q.get("governing_opposition")!="SOCRATES_VS_CYRUS" or q.get("historical_predecessor_preserved") is not True:return fail("Guiding architecture controls missing")
 expected_manifest={"AGREEMENT":11,"QUALIFIED_AGREEMENT":9,"PRIMARY_SILENCE":4,"UNRESOLVED_RELATION":3,"CYRUS_SIDE_ELABORATION":2,"GOVERNING_EXAMINATION":2,"DIVERGENCE_ACTIVE":0,"SECONDARY_SILENCE_ACTIVE":0}
 if q.get("classification_counts")!=expected_manifest:return fail("Corrected manifest classification counts mismatch")
 if q.get("comparison_entry_count")!=31 or q.get("owner_review_status")!="PENDING" or q.get("source_independence_preserved") is not True:return fail("Corrected comparison controls mismatch")
 if m.get("primary_study",{}).get("cumulative_reconstruction",{}).get("secondary_comparison_status")!="CORRECTED_DRAFT_COMPLETE_PENDING_OWNER_REVIEW":return fail("Primary corrected-comparison gate mismatch")
 if m.get("next_required_action",{}).get("id")!="XEN-CONTROLLED-COMPARISON-R1-OWNER-REVIEW-001":return fail("Corrected next action mismatch")
 if old.get("comparison_id")!="XEN-CONTROLLED-COMPARISON-001" or old.get("status")!="DRAFTED_PENDING_OWNER_REVIEW":return fail("Historical predecessor was rewritten")
 if new.get("comparison_id")!="XEN-CONTROLLED-COMPARISON-001" or new.get("revision_id")!="XEN-CONTROLLED-COMPARISON-001-R1" or new.get("status")!="CORRECTED_DRAFT_PENDING_OWNER_REVIEW":return fail("Corrected index identity mismatch")
 ga=new.get("governing_architecture",{})
 if ga.get("opposition")!="SOCRATES_VS_CYRUS" or ga.get("mediating_figure")!="XENOPHON" or ga.get("guide")!="LEO_STRAUSS_XENOPHONS_ANABASIS":return fail("Corrected governing architecture mismatch")
 expected_active={"AGREEMENT":11,"QUALIFIED_AGREEMENT":9,"PRIMARY_SILENCE":4,"UNRESOLVED_RELATION":3,"CYRUS_SIDE_ELABORATION":2,"GOVERNING_EXAMINATION":2}
 sets=new.get("active_entry_sets",[])
 if len(sets)!=6 or {x.get("classification"):x.get("entry_count") for x in sets}!=expected_active:return fail("Corrected active entry-set index mismatch")
 expected_paths={
  "AGREEMENT":"studies/comparisons/anabasis-primary-strauss/entries/agreement.yaml",
  "QUALIFIED_AGREEMENT":"studies/comparisons/anabasis-primary-strauss/entries/qualified-agreement.yaml",
  "PRIMARY_SILENCE":"studies/comparisons/anabasis-primary-strauss/entries/primary-silence.yaml",
  "UNRESOLVED_RELATION":"studies/comparisons/anabasis-primary-strauss/entries/unresolved-relation.yaml",
  "CYRUS_SIDE_ELABORATION":"studies/comparisons/anabasis-primary-strauss/entries/cyrus-side-elaboration.yaml",
  "GOVERNING_EXAMINATION":"studies/comparisons/anabasis-primary-strauss/entries/governing-examination.yaml"}
 if {x.get("classification"):x.get("record") for x in sets}!=expected_paths:return fail("Corrected active entry paths mismatch")
 active_paths=RETAINED+[CY,GE];entries=[]
 for ep in active_paths:
  shard=load(ep);cls=shard.get("classification");arr=shard.get("entries",[])
  if cls not in expected_active or len(arr)!=expected_active[cls] or shard.get("entry_count")!=expected_active[cls]:return fail("Corrected active shard mismatch: "+str(ep))
  if any(x.get("classification")!=cls for x in arr):return fail("Mixed corrected classification shard: "+str(ep))
  entries.extend(arr)
 if len(entries)!=31 or Counter(x.get("classification") for x in entries)!=Counter(expected_active):return fail("Corrected active comparison count mismatch")
 ids=[x.get("id") for x in entries]
 if len(set(ids))!=31 or set(ids)!={f"CMP-{i:03d}" for i in range(1,32)}:return fail("Corrected comparison ID coverage mismatch")
 byid={x.get("id"):x for x in entries}
 required_reclass={"CMP-019":"GOVERNING_EXAMINATION","CMP-023":"CYRUS_SIDE_ELABORATION","CMP-029":"GOVERNING_EXAMINATION","CMP-030":"CYRUS_SIDE_ELABORATION"}
 if any(byid[k].get("classification")!=v for k,v in required_reclass.items()):return fail("Owner-directed reclassification mismatch")
 prompts=set();sunits=set()
 for x in entries:
  ps=x.get("primary_stream",{});ss=x.get("secondary_stream",{})
  if not ps.get("position") or not ps.get("cumulative_anchors") or not ps.get("source_units") or not ss.get("position") or not ss.get("secondary_units") or not ss.get("printed_pages"):return fail("Malformed corrected comparison entry: "+str(x.get("id")))
  if not x.get("controlled_relation") or not x.get("preserved_uncertainty") or not x.get("comparison_effect"):return fail("Corrected comparison control missing: "+str(x.get("id")))
  prompts.update(y for y in ps.get("cumulative_anchors",[]) if str(y).startswith("CP-"));sunits.update(ss.get("secondary_units",[]))
 if prompts!={f"CP-{i:03d}" for i in range(1,13)} or sunits!={f"XEN-RU-{i:03d}" for i in range(1,9)}:return fail("Corrected source coverage mismatch")
 counts=new.get("counts",{})
 expected_counts={"comparison_entries":31,"agreement":11,"qualified_agreement":9,"primary_silence":4,"unresolved_relation":3,"cyrus_side_elaboration":2,"governing_examination":2,"divergence_active":0,"secondary_silence_active":0,"cross_cutting_findings":12,"unresolved_comparison_questions":16,"primary_comparison_prompts_covered":12,"secondary_units_covered":8}
 if counts!=expected_counts:return fail("Corrected aggregate counts mismatch")
 if len(new.get("cross_cutting_findings",[]))!=12 or len(new.get("unresolved_comparison_questions",[]))!=16:return fail("Corrected finding or question counts mismatch")
 if cor.get("correction_id")!="XEN-COR-001" or cor.get("status")!="OWNER_DIRECTED_CORRECTION_APPLIED_PENDING_OWNER_REVIEW":return fail("Correction record identity mismatch")
 remedy=cor.get("remedy",{})
 if remedy.get("governing_architecture")!="SOCRATES_VS_CYRUS" or remedy.get("interpretive_guide")!="LEO_STRAUSS_XENOPHONS_ANABASIS" or remedy.get("active_reclassifications")!=required_reclass:return fail("Correction remedy mismatch")
 if r.get("controlled_comparison_corrected") is not True or r.get("controlled_comparison_record")!=str(NEW.relative_to(R)) or r.get("controlled_comparison_original_record")!=str(OLD.relative_to(R)):return fail("Audit corrected comparison mismatch")
 if r.get("controlled_comparison_correction_record")!=str(COR.relative_to(R)) or r.get("controlled_comparison_strauss_guiding_architecture") is not True or r.get("controlled_comparison_governing_opposition")!="SOCRATES_VS_CYRUS":return fail("Audit guiding architecture mismatch")
 if a.get("resolved_items",[])[-1].get("id")!="RES-015" or a.get("documented_gaps",[])[1].get("id")!="GAP-010":return fail("Audit correction transition mismatch")
 text=(json.dumps(new,ensure_ascii=False,default=str)+" "+json.dumps(cor,ensure_ascii=False,default=str)+" "+json.dumps(load(CY),ensure_ascii=False,default=str)+" "+json.dumps(load(GE),ensure_ascii=False,default=str)).casefold()
 for phrase in ["strauss is the guiding interpretive architecture","socrates-cyrus","cyrus side","material governance","thibron's incorporation","heart of the examination","there are not two equal closures","false symmetry","artificial-intelligence self-certification remains prohibited"]:
  if phrase not in text:return fail("Corrected safeguard missing: "+phrase)
 if any(load(x).get("status")!="DRAFTED_PENDING_OWNER_REVIEW" for x in HISTORICAL):return fail("Historical superseded shards were rewritten")
 if m.get("artificial_intelligence_self_certification_prohibited") is not True or r.get("minister_adapter_derived") is not False or r.get("sanctum_registration_present") is not False:return fail("Governance gate mismatch")
 hist=H.read_text(encoding="utf-8")
 for phrase in ["Strauss as Guiding Architecture","Material governance across all seven books","Justice was classified as `DIVERGENCE`","The ending was divided into two equal closures","All thirty-one comparison IDs","XEN-CONTROLLED-COMPARISON-R1-OWNER-REVIEW-001"]:
  if phrase not in hist:return fail("Correction history safeguard missing: "+phrase)
 print("Xenophon repository validation passed");return 0
if __name__=="__main__":sys.exit(main())
