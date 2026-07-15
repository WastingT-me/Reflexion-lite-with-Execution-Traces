---
name: diagnose-failure
description: Diagnose a failed test, CI job, experiment, or agent attempt without blind retries.
---

# Diagnose Failure

1. Capture the exact command, exit code, relevant output, environment, and changed files.
2. Classify the failure as environment, dependency, syntax, type, unit, integration, timeout, resource, nondeterminism, model output, trace provider, or specification ambiguity.
3. Form one falsifiable root-cause hypothesis.
4. Run the smallest diagnostic that distinguishes that hypothesis from alternatives.
5. Apply one bounded fix and rerun the narrow check before the full suite.
6. Record a normalized failure fingerprint. Do not repeat an equivalent unsuccessful fix.
7. Stop after three materially similar attempts or when required external information is missing.

Never solve a failure by deleting tests, weakening assertions, silently skipping required behavior, or replacing real trace data with invented output.
