# Cosmic Seal Protocol (CSP) — Crisp and Testable

**Version:** CSP-A1/2025-09  \
**Maintainer:** Matthew R. LaBarre  \
**Variants:** CSL-Min, CSL-Plus

This document captures the tightened one-pager for the Cosmic Seal Protocol. It
locks in deterministic hashing, an offline verification loop, and a demo vector
bundle ready for tooling or documentation reuse.

---

## Essence

* Interval-based seals (`t_in`, `t_out`, `Δt`) witnessed by the public sky.
* Canonical JSON (RFC 8785) for every structured record.
* Authority-free verification: only ephemerides + hashes.

CSP binds an artifact digest to the tuple `{t_in, t_out, Δt}` and a celestial
anchor derived from public ephemerides. Two compatible flavors are supported:

* **CSL-Min** — times, duration, optional location metadata.
* **CSL-Plus** — CSL-Min plus a `cosmic_base` environment snapshot at `t_in`.

---

## Core Fields

The following fields are pinned for every CSL variant:

* `S1` — SHA-384 digest of the artifact (`H(P)`).
* `S2` — SHA-384 digest of `canonical_json || raw_bytes(S1)`.
* `canonical_json` — RFC 8785 canonical form (sorted keys, minimal numbers,
  UTF-8, LF line endings).

`S2` **must** hash the canonical JSON bytes **followed by** the raw byte string
represented by `S1`. Do not hash the ASCII hex form of `S1`.

Durations are expressed as integer milliseconds: `duration_ms = round(Δt_ms)`.
Optionally expose `clock_grace_ms` when ledger accuracy limits apply.

---

## Anchor Determinism (CSP-A1/2025-09)

To reproduce an anchor without any external network calls, quantize
ephemeris data and hash the packed integers:

| Field            | Allowed Values                            |
| ---------------- | ----------------------------------------- |
| `anchor.model`   | `"VSOP87"`, `"DE440"`, `"DE441"`, `"DEMO"` |
| `anchor.timescale` | `"TT"`, `"TDB"`, `"UTC"`                |
| `anchor.frame`   | `"ECLIPJ2000"`, `"ICRF"`                 |
| `anchor.bodies`  | Small ordered list, e.g., `["Sun","Jupiter"]` |
| `anchor.quant`   | `microrad` (angles), `microau` (ranges)    |

Deterministic hashing steps:

1. Sample ephemerides at `t_in` using the declared model, frame, and timescale.
2. Quantize each longitude, latitude, and radius to the declared precision.
3. Encode every quantized value as a big-endian signed 64-bit integer.
4. Concatenate in body order with the field order `(lon, lat, r)`.
5. Hash with SHA-384 → `anchor.hash`.

Declare the result with:

```
"anchor": {
  "bodies": ["Sun","Jupiter"],
  "frame": "ECLIPJ2000",
  "hash": "<hex>",
  "model": "DE440",
  "precision": "microrad|microau",
  "timescale": "TT"
}
```

State both the CSL timescale (`UTC`) and the anchor timescale (e.g., `TT`) so
library conversions are explicit.

---

## Canonical Header Templates

### CSL-Min

```
{"alg":{"anchor":"CSP-A1/2025-09","s1":"sha384","s2":"sha384"},"anchor":{"bodies":["Sun","Jupiter"],"frame":"ECLIPJ2000","hash":"<hex>","model":"DE440","precision":"microrad|microau","timescale":"TT"},"csp":"1","duration_ms":43182,"location":{"type":"logical"},"rpp":{"filename":"artifact.ext","sha384":"<S1-hex>","size":123456},"t_in":"2025-09-30T12:00:00Z","t_out":"2025-09-30T12:00:43.182Z","timescale":"UTC","variant":"CSL-Min"}
```

### CSL-Plus

```
{"alg":{"anchor":"CSP-A1/2025-09","s1":"sha384","s2":"sha384"},"anchor":{"bodies":["Sun","Jupiter"],"frame":"ECLIPJ2000","hash":"<hex>","model":"DE440","precision":"microrad|microau","timescale":"TT"},"cosmic_base":{"env":{"os":"Linux","python":"3.12.3"},"rand64":"base64url:...","seed":"hex:..."},"csp":"1","duration_ms":43182,"location":{"type":"logical"},"rpp":{"filename":"artifact.ext","sha384":"<S1-hex>","size":123456},"t_in":"2025-09-30T12:00:00Z","t_out":"2025-09-30T12:00:43.182Z","timescale":"UTC","variant":"CSL-Plus"}
```

---

## 60-Second Verification Loop (Offline)

1. **Compute the artifact digest (`S1`).**
   * Linux — `sha384sum artifact.ext | cut -d' ' -f1`
   * macOS — `shasum -a 384 artifact.ext | awk '{print $1}'`
   * Windows — `CertUtil -hashfile artifact.ext SHA384 | findstr /R "^[0-9A-F]"`

2. **Recompute the celestial anchor at `t_in`.**
   Use the deterministic ephemeris routine:

   ```bash
   python verify_csl.py --tin 2025-09-30T12:00:00Z \
     --model VSOP87 --timescale TT --frame ECLIPJ2000 \
     --bodies Sun,Jupiter --quant microrad,microau --print-hash
   ```

3. **Rebuild `S2` from canonical JSON + raw `S1` bytes.**

   ```bash
   cat csl.json | python - <<'PY' S1_HEX
   import sys, json, hashlib
   csl = json.load(sys.stdin)
   cj = json.dumps(csl, separators=(',',':'), sort_keys=True).encode('utf-8')
   s1 = bytes.fromhex(sys.argv[1])
   print(hashlib.sha384(cj + s1).hexdigest())
   PY
   ```

4. **Compare digests.**
   * Does your `S1` match the record? ✔️
   * Does your `S2` match the recorded value (or BangCheck block)? ✔️

Canonicalization pitfalls:

* Always encode JSON as UTF-8 (no BOM) with `\n` line endings.
* Normalize all Unicode strings with NFC.
* Text payloads end with a single trailing LF; binary payloads hash raw bytes.
* Refrain from pretty-printing the canonical JSON before hashing.

---

## Demo Vectors (DEMO Anchor)

Artifacts shipped in `demos/` allow a copy-paste verification run. Key
digests:

* `S1` (`demos/csp-demo.txt`) —
  `c7095972fbf517cbe79c90bf15de19c32133da544af5c3086c9df6e94b10b21c18e325726da0c5930df745724d4a971e`
* `S2` (canonical CSL + raw `S1`) —
  `d7306710d175b2cd76af87d2558395c5d275cf1af109be371580579ce9d0ecce20e7eb6d9c74f612474c35c009ffd620`
* BangCheck block (`demos/csp-demo.bangcheck.txt`) —
  `ca6eb6461ae97f679940837e60bbc28e55adc2acd84e8ab4519c5119e18fbb6000f561cafe53b61b64cf8a082d5b9939`

The canonical CSL JSON (single line) stored at
`demos/csp-demo.csl.json` reads:

```
{"alg":{"anchor":"CSP-A1/DEMO-2025-09","s1":"sha384","s2":"sha384"},"anchor":{"bodies":["Sun","Jupiter"],"frame":"ECLIPJ2000","hash":"156927861546c6352717a958a955a080eaf0709f1529be83be646db8e4f6cfac129db018b0a71c15c523bb1c4850d239","model":"DEMO","precision":"microrad|microau","timescale":"UTC"},"csp":"1","duration_ms":5000,"location":{"hint":"demo","type":"logical"},"rpp":{"filename":"demo.txt","sha384":"c7095972fbf517cbe79c90bf15de19c32133da544af5c3086c9df6e94b10b21c18e325726da0c5930df745724d4a971e","size":11},"t_in":"2025-09-30T12:00:00Z","t_out":"2025-09-30T12:00:05Z","timescale":"UTC","variant":"CSL-Min"}
```

BangCheck block:

```
!BEGIN CSP-DEMO
!RPP sha384=c7095972fbf517cbe79c90bf15de19c32133da544af5c3086c9df6e94b10b21c18e325726da0c5930df745724d4a971e size=11 filename=demo.txt
!CSL {"alg":{"anchor":"CSP-A1/DEMO-2025-09","s1":"sha384","s2":"sha384"},"anchor":{"bodies":["Sun","Jupiter"],"frame":"ECLIPJ2000","hash":"156927861546c6352717a958a955a080eaf0709f1529be83be646db8e4f6cfac129db018b0a71c15c523bb1c4850d239","model":"DEMO","precision":"microrad|microau","timescale":"UTC"},"csp":"1","duration_ms":5000,"location":{"hint":"demo","type":"logical"},"rpp":{"filename":"demo.txt","sha384":"c7095972fbf517cbe79c90bf15de19c32133da544af5c3086c9df6e94b10b21c18e325726da0c5930df745724d4a971e","size":11},"t_in":"2025-09-30T12:00:00Z","t_out":"2025-09-30T12:00:05Z","timescale":"UTC","variant":"CSL-Min"}
!S1_CONTENT c7095972fbf517cbe79c90bf15de19c32133da544af5c3086c9df6e94b10b21c18e325726da0c5930df745724d4a971e
!S2_SHA384 d7306710d175b2cd76af87d2558395c5d275cf1af109be371580579ce9d0ecce20e7eb6d9c74f612474c35c009ffd620
!ANCHORS model=DEMO timescale=UTC frame=ECLIPJ2000 bodies=Sun,Jupiter precision=microrad|microau algo=CSP-A1/DEMO-2025-09
!NOTES demo vectors for harness; S2 uses raw S1 bytes per spec
!END
!SHA384-BLOCK ca6eb6461ae97f679940837e60bbc28e55adc2acd84e8ab4519c5119e18fbb6000f561cafe53b61b64cf8a082d5b9939
```

---

## Licensing

* Spec & figures — © 2025 Matthew R. LaBarre (CC BY 4.0).
* Verifier CLI — Apache-2.0 (with NOTICE file).
* Library (optional) — MPL-2.0 (file-level reciprocity).
* Mark — "Cosmic Seal Protocol (CSP)" is an unregistered mark of Matthew R.
  LaBarre. Compatibility claims allowed; no implied endorsement. See
  `TRADEMARKS.md` for usage examples.

---

## Contact & Stewardship

Contributions and protocol questions are welcome (no SLA). Security disclosures
should follow the guidance in `SECURITY.md`; add a PGP key for sealed reports as
needed.

### Protocol Haiku

> Seal the sky to time,  \
> Digits hum with planets’ drift—  \
> Proof without a king.

---

## Next Steps

* Publish 2–3 deterministic test vectors per anchor model (`VSOP87`, `DE440`).
* Expand the verifier CLI (`verify_csl.py`) to ship alongside these vectors.
* Mirror the BangCheck harness wherever ledgers or exhibits are stored.

