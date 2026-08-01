# Xenophon Minister Adapter — In-Depth Review 001

**Date:** 2026-08-01  
**Reviewed head:** `689e222ddf0debe24119769a6d9b15552f20c685`  
**Disposition:** `RETURN_FOR_TARGETED_R1_REVISION`  
**Adoption:** not granted

## Governing question

Does `XEN-MINISTER-ADAPTER-001` convert the owner-adopted Xenophon inquiry into a genuine Sanctum minister interface without flattening Xenophon, corrupting evidence status, weakening uncertainty, or claiming authority it does not possess?

## What passes

The adapter's intellectual architecture is sound.

Its four registers preserve the movement from deed and material governance, through Socratic apprehension and the Cyrus-side problem of political rule, to Xenophon's authorial ordering and indirect revelation. They do not reduce Xenophon to a generic commander or convert Strauss's questions into settled doctrine.

Its three guards also pass. The adapter distinguishes author, narrator, remembered speaker, and historical actor; preserves primary showing, Strauss's explicit argument, controlled inference, and unresolved question as separate layers; and prohibits final teaching, Greek overreach, uncertainty erasure, impersonation, and artificial-intelligence self-certification.

The proving answer is genuinely Xenophontic in form. It begins from concrete command, provision, punishment, election, defense, and restraint; tests those deeds through the Socrates-Cyrus opposition; and reaches a committed but limited judgment: competence does not certify its own justice or legitimacy.

## Why adoption is refused

The adapter does not yet satisfy the live federation contract.

### 1. Report-schema failure

Sanctum's live `ministerial-report.schema.json` requires every evidence item to carry `witness_id`, `source_id`, `repository_commit`, and `path`. The adapter emits `ref`, `path`, `repository_commit`, and `evidence_layer` instead. The schema also requires uncertainties to be strings, while the adapter emits mappings, and it permits `PENDING_OWNER_CERTIFICATION`, not `PENDING_OWNER_REVIEW`.

The existing tests prove the adapter's own expected shape, not the governing federation schema.

### 2. Witness-identity incompatibility

The live schema accepts witness identifiers matching `CORPUS-WIT-###`. Xenophon's admitted witness is `XEN-WIT-PRI-001`. No controlled alias or approved schema extension currently connects them. An unregistered alias may not be invented merely to make validation pass.

### 3. False repository pin

The proving request declares repository commit `b71a6a171fd2467cb712e9f9203d05791268bab4` together with manifest version `1.67.0`. That commit contains manifest `1.66.0` and predates the adapter. The report therefore states provenance that is formally well-shaped but materially false.

### 4. Placeholder hashes

The inquiry-envelope and briefing hashes are repeated placeholder characters. The briefing itself says its declared hash is not byte-certified. The adapter checks only that a hash has the correct number of characters; it does not calculate the bytes of the referenced record or compare them with the declaration.

### 5. Authorization collapse

The candidate report identifies the R1 synthesis owner review as its `authorization_ref`. That record authorizes the synthesis as a source of derivation. It does not authorize the adapter as an operational minister interface. Derivation authority and operational authority must remain distinct.

## Controlled R1 scope

`XEN-MINISTER-ADAPTER-001-R1` may correct only federation and provenance defects:

1. validate against the live Sanctum report schema;
2. resolve Xenophon witness-ID compatibility through an explicit federation decision;
3. pin a commit that actually contains the declared adapter and manifest;
4. create and verify real envelope and briefing hashes;
5. separate synthesis derivation authority from adapter operational authority.

The four registers, three guards, R1 synthesis, nineteen unresolved questions, direct proving judgment, English-witness jurisdiction, and deferred Greek phase are not reopened.

## Final ruling

- **Pass:** 9
- **Pass with limitation:** 1
- **Blocking revision:** 5
- **Adapter owner-adopted:** no
- **Operational minister authority:** no
- **Sanctum registration:** not authorized
- **Assembly dispatch:** not authorized

The next production unit is `XEN-MINISTER-ADAPTER-001-R1`, with an explicit federation dependency for Xenophon witness-identifier compatibility.