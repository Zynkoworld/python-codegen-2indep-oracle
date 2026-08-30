#!/usr/bin/env python3
"""codegen_2indep.py — a deterministic decider for two-independent-implementation codegen attestations.

An **oracle** *deterministically decides* the truth of a case — it doesn't guess, it decides. This one decides,
for a given codegen **two-independent-implementation attestation**, whether it is a valid record of a coding task
solved by TWO IMPLEMENTATION-INDEPENDENT solutions that BOTH pass the task's own non-Claude test-suite.

TWO-INDEP (Janos doctrine #15436/#15490): a single run — or N same-lab runs — is NOT proof; a cell is proven iff
two IMPLEMENTATION-INDEPENDENT solutions both pass the task's own test-suite (the test-suite is the non-Claude judge).
The attestation is VALID iff:
  - verdict == 'pass', and
  - arm1_pass AND arm2_pass (both independent solutions passed), and
  - arm2 is a genuinely DIFFERENT-LAB LLM (deepseek / mistral / kimi / glm / glm-flash / yi — NOT qwen/claude/self), and
  - arm1 != arm2 (the two arms are distinct), and
  - judge names a 'testsuite' (an executed test-suite is the decider, not a self-assertion).
"""
import json
import os
import sys

_DIFF_LAB_ARM2 = {"deepseek", "mistral", "kimi", "glm", "glm-flash", "yi"}


def decide(att):
    """Deterministic verdict for one attestation: 'VALID' | 'INVALID'. No guessing, no network."""
    if att.get("verdict") != "pass":
        return "INVALID"
    if not (att.get("arm1_pass") and att.get("arm2_pass")):
        return "INVALID"
    arm1 = str(att.get("arm1") or "")
    arm2 = str(att.get("arm2") or "")
    if arm2 not in _DIFF_LAB_ARM2:
        return "INVALID"
    if not arm1 or arm1 == arm2:
        return "INVALID"
    if "testsuite" not in str(att.get("judge") or ""):
        return "INVALID"
    return "VALID"


def _run_probes(path):
    """Run the oracle over the labelled DISCRIMINATING probe corpus. Exit 0 IFF recall==1.0 AND false_positives==0
    AND the corpus is non-degenerate (has both VALID and INVALID). Same contract as the zynko-oracle CWE deciders."""
    probes = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                probes.append(json.loads(line))
    have_valid = any(p.get("expected_verdict") == "VALID" for p in probes)
    have_invalid = any(p.get("expected_verdict") == "INVALID" for p in probes)
    if not (have_valid and have_invalid):
        print("DEGENERATE corpus (need both VALID and INVALID) — FAIL")
        return 1
    tp = fp = fn = 0
    for p in probes:
        verdict = decide(p)
        exp = p.get("expected_verdict")
        if exp == "VALID" and verdict == "VALID":
            tp += 1
        elif exp == "VALID" and verdict == "INVALID":
            fn += 1
        elif exp == "INVALID" and verdict == "VALID":
            fp += 1
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    ok = (recall == 1.0 and fp == 0)
    print("codegen-2indep oracle: probes=%d | recall=%.3f | false_positives=%d | verdict=%s"
          % (len(probes), recall, fp, "PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default = os.path.join(base, "probes", "probes.jsonl")
    sys.exit(_run_probes(sys.argv[1] if len(sys.argv) > 1 else default))
