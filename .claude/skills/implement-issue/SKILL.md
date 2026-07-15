---
name: implement-issue
description: Implement one agent-ready GitHub issue with bounded scope and evidence-based verification.
---

# Implement Issue

## Inputs
- One GitHub issue with goal, context, acceptance criteria, tests, non-goals, and dependencies.
- Repository instructions in `CLAUDE.md` and `.ai/`.

## Procedure
1. Restate the acceptance criteria and identify allowed files.
2. Inspect the smallest relevant code surface and existing tests.
3. Reproduce the missing behavior or failure before editing when possible.
4. Add or update a test that would fail before the implementation.
5. Make the smallest coherent implementation.
6. Run targeted tests, then repository quality gates.
7. Inspect `git diff --check`, `git status`, and the full diff.
8. Confirm every acceptance criterion with concrete evidence.
9. Produce a PR-ready summary: what changed, why, tests, limitations, and intentionally untouched files.

## Constraints
- Do not expand scope because adjacent cleanup looks useful.
- Do not change acceptance criteria.
- Do not remove tests, lower thresholds, add broad ignores, or catch exceptions merely to hide failures.
- Do not introduce a fake trace path as a production implementation.
- Stop after three materially similar failed attempts and report the blocker plus evidence.
