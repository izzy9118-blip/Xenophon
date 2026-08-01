from pathlib import Path
import json, sys, yaml, subprocess
R=Path(__file__).resolve().parents[1]
P=R/'scripts/validate_repository_v1_61.py'
COR=R/'governance/corrections/2026-07-31-xenophon-authorial-revelation-direction.yaml'
OWN=R/'governance/owner-reviews/2026-07-31-xenophon-authorial-revelation-direction.yaml'
CTL=R/'studies/comparisons/anabasis-primary-strauss/synthesis-controls/xenophon-authorial-revelation.yaml'
H=R/'history/2026-07-31-xenophon-authorial-revelation-direction-correction.md'
M=R/'manifest.yaml';A=R/'audits/founding-state.yaml'
def load(p):
    with p.open(encoding='utf-8') as f:return yaml.safe_load(f)
def fail(x):print(x);return 1
def main():
    if not P.exists():return fail('Frozen v1.61 validator missing')
    z=subprocess.run([sys.executable,str(P)],cwd=R,text=True,capture_output=True)
    if z.returncode:return fail('v1.61 predecessor failed: '+(z.stdout+z.stderr).strip())
    for p in [COR,OWN,CTL,H,M,A]:
        if not p.exists():return fail('Authorial-revelation correction file missing: '+str(p))
    cor=load(COR);own=load(OWN);ctl=load(CTL);m=load(M);a=load(A)
    if cor.get('correction_id')!='XEN-COR-003' or cor.get('status')!='OWNER_DIRECTED_INTERPRETIVE_CORRECTION':return fail('Correction identity mismatch')
    g=cor.get('governing_correction',{})
    if 'Xenophon supplies the presentation of the older Cyrus' not in g.get('required_direction',''):return fail('Required direction missing')
    if 'Strauss uncovers the concealed order' not in g.get('strauss_role',''):return fail('Strauss recovery direction missing')
    if own.get('status')!='OWNER_ADOPTED_INTERPRETIVE_DIRECTION_CORRECTION' or own.get('ruling',{}).get('adoption_status')!='OWNER_ADOPTED':return fail('Owner correction adoption mismatch')
    if ctl.get('status')!='ACTIVE_OWNER_ADOPTED_CONTROL' or ctl.get('governing_correction')!=str(COR.relative_to(R)):return fail('Synthesis control mismatch')
    text=' '.join(json.dumps(x,ensure_ascii=False) for x in [cor,own,ctl]).casefold()
    for phrase in ['xenophon is the revealing author','xenophon reveals','older cyrus','deliberate concealment','strauss uncovers','must not make xenophon the passive recipient','do not collapse']:
        if phrase not in text:return fail('Authorial-revelation safeguard missing: '+phrase)
    prohibited=['the older cyrus supplies xenophon with a standard','strauss imposes the socrates-cyrus opposition upon xenophon from outside']
    if any(x not in text for x in prohibited):return fail('Prohibited-direction safeguard missing')
    if m.get('version')!='1.61.0' or m.get('state')!='CONTROLLED_COMPARISON_R3_OWNER_ADOPTED':return fail('Immutable adopted manifest state changed unexpectedly')
    if m.get('next_required_action',{}).get('id')!='XEN-STRAUSS-GUIDED-CONTROLLED-SYNTHESIS-001':return fail('Synthesis next action changed')
    rs=a.get('repository_state',{})
    if rs.get('minister_adapter_derived') is not False or rs.get('sanctum_registration_present') is not False:return fail('Governance gate mismatch')
    hist=H.read_text(encoding='utf-8').casefold()
    for phrase in ['xenophon supplies the presentation of the older cyrus','xenophon is the revealing author','r3 and its adoption records remain immutable']:
        if phrase not in hist:return fail('History safeguard missing: '+phrase)
    print('Xenophon repository validation passed');return 0
if __name__=='__main__':sys.exit(main())
