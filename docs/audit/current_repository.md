# Current Repository Audit

Scope: complete tracked repository as of branch `agent/issue-2-audit-repo-and-notebooks`
(base `main` at commit `23aa442`). No production code was modified while writing this
document. This inventory feeds `notebook_inventory.md`, `defects.md`, and `recovery_plan.md`.

## Tracked files

```text
.ai/ARCHITECTURE.md            target module layout, dependency rules
.ai/DEFINITION_OF_DONE.md      release gate checklist
.ai/permissions.yaml           agent write policy, allowed commands, limits
.ai/PRIVATE_ARTIFACTS.md       private-notebook handling rules
.ai/PRODUCT_SPEC.md            experiment definition and milestones
.ai/PROJECT_STATE.md           living status notes
.ai/PROVENANCE.md              source/main branch roles, attribution categories
.claude/skills/*.md            agent skills (audit, implement, review, diagnose)
.github/ISSUE_TEMPLATE/agent-task.yml
.github/workflows/agent-readiness.yml   CI: compile check, contract-file check, tracked-output check
AGENTS.md, CLAUDE.md           operating contract / instructions entry points
paper.pdf                      author's preprint describing the experiment and pipeline
readme.md                      user-facing quick start
run.py                         CLI entry point (argparse; baseline / reflexion-lite / reflexion+trace / all)
task_registry.py               EASY/MEDIUM/BUG_PRONE task lists, TRACE_TASK_IDS, get_group()
utils.py                       ~680 lines: dataset, prompting, generation, execution, metrics, persistence
results/pilot5_humaneval_tests.jsonl       tracked historical pilot artifact
results/pilot5_python_solutions.jsonl      tracked historical pilot artifact
results/pilot5_semantic_feedback.jsonl     tracked historical pilot artifact
```

No `tests/` directory, no dependency manifest (`requirements.txt`/`pyproject.toml`), no lint/type
config exist yet, consistent with `.ai/PROJECT_STATE.md`'s `agent-ready-infrastructure` stage.

## Entry point and data flow (as implemented)

`run.py` parses `--method {baseline, reflexion-lite, reflexion+trace, all}` plus generation/exec
parameters, loads the HumanEval `test` split, filters it to either `SELECTED_TASK_IDS` (30 tasks)
or `TRACE_TASK_IDS` (5 tasks, via `--trace-only`), loads the Hugging Face model, then dispatches to
`solve_task_baseline` / `solve_task_reflexion_lite` in `utils.py` (see Defect D1, resolved — this
file was `utills.py` at audit time and has since been renamed to match the `from utils import`
statement in `run.py`). Results are written as JSONL under `--results-dir`.

`task_registry.py`'s `EASY_TASKS` / `MEDIUM_TASKS` / `BUG_PRONE_TASKS` / `TRACE_TASK_IDS` were
cross-checked against the private notebooks' equivalent lists (`EASY_TASKS`/`MEDIUM_TASKS`/
`BUG_PRONE_TASKS` in the baseline section, `TARGET_ENTRY_POINTS` in the trace section) and are
byte-identical in content, only reformatted with a `get_group()` helper and per-task comments
added. This part is cleanly **inherited** from the notebooks.

`utils.py` already contains more than `run.py` uses:
- `solve_task_baseline`, `solve_task_reflexion_lite` — wired into `run.py`, functional.
- `solve_task_reflexion_trace`, `build_trace_reflection_prompt` — fully implemented but **never
  imported or called anywhere**. They expect a pre-computed `trace_feedback` string; nothing in the
  tracked repository produces that string. This is why `run.py`'s `reflexion+trace` path is a
  hard-coded `NotImplementedError`, not because the retry loop is unwritten — the loop exists, only
  the upstream trace-generation stage is missing.
- `extract_humaneval_tests_for_tasks` — a nested-function AST-based extractor of concrete
  `candidate(...)` call arguments/expected values from HumanEval `test` source. Unused by `run.py`,
  but functionally equivalent to logic recovered from the private notebooks (see
  `notebook_inventory.md`). This is evidence that partial recovery already happened before the
  autonomous-agent experiment began.

## CI and mandatory checks (verified by running them locally, not by inspection)

`AGENTS.md`'s minimum checks and `.github/workflows/agent-readiness.yml` were executed exactly as
specified:

```text
$ python -m py_compile run.py task_registry.py utils.py
FileNotFoundError: [Errno 2] No such file or directory: 'utils.py'
```

```text
$ git ls-files | grep -E '(^|/)(__pycache__|results)/'
results/pilot5_humaneval_tests.jsonl
results/pilot5_python_solutions.jsonl
results/pilot5_semantic_feedback.jsonl
```

Both commands are the literal steps CI runs (`.github/workflows/agent-readiness.yml` lines 20 and
36). Both failed against `main` as inspected when this audit was originally written. See
`defects.md` D1 and D2 for detail and impact.

**Re-verified 2026-07-19, after syncing this branch with `main`:** the compile check now passes
(`utills.py` was renamed to `utils.py` by PR #4, outside this audit issue's scope — D1 is
resolved). The tracked-`results/`-files check still fails identically (D2 remains open,
unresolved, owner decision pending per `recovery_plan.md`).

## Safety posture of generated-code execution

`utils.py::run_code_with_tests` (and its notebook counterparts, see `notebook_inventory.md`) run
generated HumanEval candidates via `multiprocessing.Process` with a wall-clock `timeout` and
`terminate()` on expiry. There is no memory/CPU bound, no filesystem restriction, and no network
denial at the process level — weaker than `.ai/DEFINITION_OF_DONE.md`'s "isolated subprocess/
container with time and resource limits" requirement. Documented here as a gap, not fixed, per this
issue's non-goals.

## HumanEval integrity check

The HumanEval dataset row includes a `canonical_solution` field (the hidden reference answer).
Every prompt-building and feedback-building function reachable from `run.py`/`utils.py` was
inspected; none of them reference `canonical_solution`. The same check was run against all four
private notebooks (see `notebook_inventory.md`) with the same result. No leakage path was found.
