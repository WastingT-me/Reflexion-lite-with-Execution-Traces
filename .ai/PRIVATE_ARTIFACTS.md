# Private reference artifacts

## Purpose

Private artifacts provide historical implementation context to local agents without publishing draft code. They may contain duplicated code, dead cells, defects, manual experiment steps, raw traces, outputs, credentials, or local paths.

Expected local references include:

- four draft Jupyter notebooks from the original experiment;
- `paper.pdf`;
- optional historical logs and raw Transformer-VM traces.

## Recommended layout

Keep private files outside the Git checkout whenever possible:

```text
workspace/
├── Reflexion-lite-with-Execution-Traces/
└── reflexion-private-reference/
    ├── notebooks/
    ├── paper.pdf
    └── traces/
```

A locally ignored `private_reference/` directory inside the checkout is acceptable when tool permissions require it.

## Agent access

Agents may:

- read all notebook source cells and outputs;
- compare duplicated implementations;
- identify errors, unused code, manual stages, dependencies, and intended data flow;
- extract behavioral requirements and small necessary algorithms;
- write an inventory report that paraphrases findings without reproducing private source.

Agents must not:

- commit the notebooks, ZIP, raw traces, or paper unless the owner separately authorizes publication;
- paste notebook source wholesale into public modules;
- quote long private passages in issues, commits, PRs, logs, or CI output;
- upload private files as GitHub Actions artifacts;
- execute notebook cells before reviewing side effects, credentials, external commands, and generated-code execution;
- treat notebook behavior as correct without tests.

## Refactoring workflow

1. Perform a static inventory of every notebook.
2. Map cells to baseline, reflexion-lite, trace generation, translation, compression, evaluation, or unused/obsolete code.
3. Identify duplicate and conflicting implementations.
4. Derive public interfaces and acceptance tests.
5. Reimplement the smallest coherent component in production code.
6. Verify it independently.
7. Record only provenance and a paraphrased summary in the public PR.

## Pre-commit check

Before every commit:

```bash
git status --short
git diff --cached --name-only
git check-ignore private_reference/ || true
```

No path containing private notebooks, archives, raw trace dumps, or local credentials may be staged.
