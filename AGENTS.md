# AGENTS.md

This file is the operating contract for autonomous coding agents in this repository.

## Mission

Finish the reproducible research implementation described in `.ai/PRODUCT_SPEC.md` while preserving a transparent record of what was inherited from the author and what was produced by agents.

The primary engineering objective is to demonstrate disciplined use of agents, skills, a bounded harness, tests, CI feedback, and review. Scientific improvements are secondary to producing a correct, reproducible, maintainable repository.

## Repository provenance

- `source` is the immutable author-created starting point at commit `9394f7526980fa6c4ee7334a30d892ff25ebe44c`.
- `main` is the public product branch containing agent-assisted and automated engineering work after the starting point.
- Do not modify, rebase, force-push, or merge new work into `source`.
- Every material change after the source snapshot must be attributable through commits, issues, pull requests, agent logs, or generated reports.
- Read `.ai/PROVENANCE.md` before planning work.

## Required reading order

1. `AGENTS.md`
2. `.ai/PROVENANCE.md`
3. `.ai/PRODUCT_SPEC.md`
4. `.ai/ARCHITECTURE.md`
5. `.ai/DEFINITION_OF_DONE.md`
6. `.ai/PROJECT_STATE.md`
7. The selected GitHub issue
8. The relevant skill under `.claude/skills/`

## Repository facts

- `run.py` is the current CLI entry point.
- `task_registry.py` defines the selected HumanEval tasks and groups.
- `utils.py` contains most of the current implementation and may contain duplication, dead code, and defects.
- The public CLI currently contains a `NotImplementedError` for `reflexion+trace`, but a historical implementation exists in private draft notebooks.
- The private notebooks and `paper.pdf` are reference evidence, not trusted production code.
- Generated candidate code is untrusted and must be executed only inside the configured sandbox.

## Full-code inspection requirement

Before changing behavior, agents must inspect the complete relevant implementation rather than relying only on README descriptions or isolated snippets. They may use:

- all tracked repository files;
- Git history and the `source` branch for comparison;
- locally mounted private reference artifacts listed in `.ai/PRIVATE_ARTIFACTS.md`;
- tests, logs, experiment outputs, and the paper when available.

Agents are explicitly expected to identify defects, duplicated logic, dead code, inconsistent naming, incomplete implementations, unsafe execution, and deviations from the paper. Existing code must not be assumed correct merely because it is present in `source` or `main`.

## Private artifact rules

- Private notebooks may be read and analyzed locally but must never be committed, quoted extensively, uploaded as CI artifacts, or copied wholesale into public files.
- Extract behavior and interfaces, then implement clean production code with tests.
- Do not execute notebook cells until dependencies, side effects, secrets, and generated-code execution have been reviewed.
- Before every commit, verify that no private artifact is staged.

## Work rules

- `main` is the primary public development branch and final integration target.
- Use one bounded issue per implementation branch and merge it into `main` through a PR so the automated work remains reviewable and attributable.
- Direct commits to `main` are reserved for explicitly authorized repository-administration changes; normal agent implementation uses PRs.
- Prefer the smallest change satisfying all acceptance criteria.
- Add or update tests before declaring completion.
- Never remove, skip, loosen, or rewrite a failing test solely to make CI pass.
- Never edit `.ai/PRODUCT_SPEC.md` or `.ai/DEFINITION_OF_DONE.md` as part of an implementation issue unless the issue explicitly authorizes it.
- Do not force-push shared branches.
- Do not expose tokens, credentials, private local paths, prompts containing secrets, or model outputs containing secrets.
- Do not execute generated HumanEval code outside the repository sandbox.
- Record assumptions and unresolved ambiguity in the PR description.

## Mandatory checks

Run the checks defined by the current issue and repository configuration. At minimum, while the repository remains in its initial layout:

```bash
python -m py_compile run.py task_registry.py utils.py
git diff --check
```

Once dependency metadata and tests are added, `pytest`, Ruff, and type checking become mandatory according to `.ai/DEFINITION_OF_DONE.md`.

## Stop conditions

Stop and mark the issue `agent-blocked` when any condition holds:

- The same failure fingerprint remains after three materially different repair attempts.
- Product behavior cannot be inferred from the specification, paper, tests, source snapshot, or private reference artifacts.
- Completion requires credentials, external services, unavailable model weights, or hardware not supplied by the issue.
- The requested change would weaken safety boundaries around execution of generated code.
- The change exceeds the issue scope or requires modifying more than 12 files without explicit authorization.

## PR requirements

Every PR must include:

- What changed and why.
- Whether the behavior was inherited from `source`, recovered from private notebooks, or newly designed by the agent.
- Acceptance criteria mapped to evidence.
- Exact checks executed and their results.
- Evaluation artifacts or a clear reason they were not run.
- Known limitations and follow-up issues.
- Files intentionally not changed.
- Confirmation that no private artifacts were committed or uploaded.
