# AGENTS.md

This file is the operating contract for autonomous coding agents in this repository.

## Mission

Finish the reproducible research implementation described in `.ai/PRODUCT_SPEC.md`, one GitHub issue at a time, without changing the scientific claim or weakening evaluation criteria.

## Required reading order

1. `AGENTS.md`
2. `.ai/PRODUCT_SPEC.md`
3. `.ai/ARCHITECTURE.md`
4. `.ai/DEFINITION_OF_DONE.md`
5. The selected GitHub issue
6. The relevant skill under `.ai/skills/`

## Repository facts

- `run.py` is the current CLI entry point.
- `task_registry.py` defines the selected HumanEval tasks and groups.
- `utills.py` contains the current implementation utilities. The misspelling is legacy technical debt.
- `reflexion+trace` is currently not implemented.
- Generated candidate code is executed locally; treat it as untrusted code.

## Work rules

- Work on exactly one issue per branch and PR.
- Prefer the smallest change satisfying all acceptance criteria.
- Add or update tests before declaring completion.
- Never remove, skip, loosen, or rewrite a failing test solely to make CI pass.
- Never edit `.ai/PRODUCT_SPEC.md` or `.ai/DEFINITION_OF_DONE.md` as part of an implementation issue unless the issue explicitly authorizes it.
- Do not push directly to `main`.
- Do not force-push shared branches.
- Do not expose tokens, credentials, local paths, prompts containing secrets, or model outputs containing secrets.
- Do not execute generated HumanEval code outside the repository sandbox.
- Record assumptions and unresolved ambiguity in the PR description.

## Mandatory checks

Run the commands defined in `.ai/commands.yaml`. At minimum:

```bash
python -m compileall -q run.py task_registry.py utills.py utils.py
pytest -q
ruff check .
ruff format --check .
```

Type checking becomes mandatory when the corresponding Definition of Done item is enabled.

## Stop conditions

Stop and mark the issue `agent-blocked` when any condition holds:

- The same failure fingerprint remains after three materially different repair attempts.
- Product behavior cannot be inferred from the specification, paper, tests, or existing code.
- Completion requires credentials, external services, unavailable model weights, or hardware not supplied by the issue.
- The requested change would weaken safety boundaries around execution of generated code.
- The change exceeds the issue scope or requires modifying more than 12 files without explicit authorization.

## PR requirements

Every PR must include:

- What changed and why.
- Acceptance criteria mapped to evidence.
- Exact checks executed and their results.
- Evaluation artifacts or a clear reason they were not run.
- Known limitations and follow-up issues.
- Files intentionally not changed.
