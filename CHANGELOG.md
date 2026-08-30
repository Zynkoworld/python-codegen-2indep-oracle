# Changelog

## 0.1.0 — 2026-08-30
- Initial release: deterministic decider for two-independent-implementation codegen attestations.
- 22-case discriminating probe corpus (19 VALID + 3 planted-INVALID), non-degenerate.
- `verify.py` CI gate: recall=1.000, false_positives=0 → PASS. Stdlib only, no network.
- Attestation-only (no solution source). Apache-2.0 oracle code.
