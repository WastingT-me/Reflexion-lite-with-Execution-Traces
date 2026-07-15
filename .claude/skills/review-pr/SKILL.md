---
name: review-pr
description: Independently review a proposed change against its issue, tests, architecture, and safety constraints.
---

# Review PR

1. Read the issue and acceptance criteria before the implementation summary.
2. Inspect the complete diff and changed-file list.
3. Check correctness, regressions, result-schema compatibility, reproducibility, generated-code isolation, secret handling, and scope.
4. Run or inspect the required tests; do not accept claims without evidence.
5. Look specifically for weakened tests, broad ignores, swallowed exceptions, fabricated traces, uncontrolled network access, and direct coupling of core logic to Torch/Transformers.
6. Classify findings as blocking, important, or optional.
7. Approve only when every acceptance criterion is satisfied and all blocking findings are resolved.

Return a concise report containing findings with file/line references, checks performed, residual risks, and final verdict.
