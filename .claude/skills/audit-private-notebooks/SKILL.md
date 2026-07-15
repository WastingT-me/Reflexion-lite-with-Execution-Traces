---
name: audit-private-notebooks
description: Statically inspect private draft notebooks, recover intended behavior, and produce a safe refactoring plan without publishing or trusting draft code.
---

# Audit Private Notebooks

## Inputs

- Paths to all private notebooks.
- `paper.pdf` and public repository code.
- `.ai/PRIVATE_ARTIFACTS.md` and `.ai/PRODUCT_SPEC.md`.

## Procedure

1. Confirm every private path is outside Git tracking or ignored.
2. Parse notebook JSON and inspect all source cells and outputs without executing cells.
3. Build a cell-level inventory containing notebook, cell index, purpose, dependencies, inputs, outputs, side effects, and status.
4. Group code into baseline, reflexion-lite, Python-to-C, C-to-WASM, Transformer-VM, trace processing, compression, evaluation, visualization, setup, or unused.
5. Detect duplicated functions, conflicting implementations, undefined variables, missing files, hard-coded paths, leaked secrets, unsafe execution, stale outputs, and unreachable cells.
6. Compare notebook behavior with `source`, current `main`, and the paper.
7. Mark each component as reusable concept, requires correction, obsolete, unsafe, or unclear.
8. Produce a public-safe report using paraphrases and function/interface names only; do not reproduce substantial private source.
9. Propose bounded GitHub issues in dependency order. Each issue must define tests and identify whether behavior is inherited, recovered, agent-designed, or owner-directed.

## Constraints

- Never execute notebook cells during the audit.
- Never add private files to Git, PRs, CI artifacts, or agent logs.
- Never assume notebook outputs were produced by the current code.
- Never perform a bulk notebook-to-module copy.
- Stop when a scientific decision cannot be resolved from the paper, source snapshot, notebooks, or owner instructions.

## Required output

- notebook summary table;
- duplicate/conflict map;
- defect and risk register;
- recovered end-to-end pipeline;
- proposed target modules;
- ordered issue backlog;
- unresolved owner questions.
