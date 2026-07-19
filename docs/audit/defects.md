# Defect and Risk Register

Severity is about impact on getting a correct, reproducible `reflexion+trace` implementation
running, not about elegance. Nothing here was fixed by this issue — this issue is audit-only.
Each item states how it was verified. D1 was subsequently fixed by an unrelated, out-of-scope PR
and is marked resolved below; that fix was not made as part of this audit.

## D1 — RESOLVED (was CRITICAL): `run.py` cannot import its own implementation module

**Status: RESOLVED on `main` as of commit `70880ed` ("fix: restore utils module name", PR #4,
merged 2026-07-19).** The implementation file was renamed `utills.py` -> `utils.py`, matching
`run.py`'s `from utils import (...)`. Re-running the exact mandatory check now succeeds:

```text
$ python -m py_compile run.py task_registry.py utils.py
$ echo $?
0
```

`import run` still raises, but now only on the unrelated, expected `ModuleNotFoundError: No
module named 'torch'` (no dependency manifest/environment exists yet at this project stage), not
on the module-name mismatch. This fix landed as a standalone bug-fix PR, outside this audit
issue's scope; this entry is updated only because the audit branch was synced with `main` after
the fix merged.

Original finding, preserved for the record: `run.py` did `from utils import (...)` while the
implementation file on disk was `utills.py` (double "l"), so the exact command `AGENTS.md` lists
as a mandatory check failed:

```text
$ python -m py_compile run.py task_registry.py utils.py
FileNotFoundError: [Errno 2] No such file or directory: 'utils.py'
```

and importing `run` directly raised `ModuleNotFoundError: No module named 'utils'`. **The CLI did
not run at all**, for any `--method`. This was not a notebook-recovery gap; it was a filename
typo in already-"working" public code.

## D2 — CRITICAL: CI's own generated-output gate fails against tracked `main`

`.github/workflows/agent-readiness.yml` fails the build if `git ls-files` matches
`(^|/)(__pycache__|results)/`. Three files are already tracked under `results/`:

```text
$ git ls-files | grep -E '(^|/)(__pycache__|results)/'
results/pilot5_humaneval_tests.jsonl
results/pilot5_python_solutions.jsonl
results/pilot5_semantic_feedback.jsonl
```

These are real historical pilot artifacts (see `notebook_inventory.md` §3) and appear intentionally
committed as evidence, but `.gitignore`'s `results/` rule and the CI gate both treat `results/` as
disposable generated output. D1 is now resolved, but CI on `main` should still be red on this gate
alone; this needs an owner decision (`recovery_plan.md`), not a silent fix.

## D3 — HIGH: `reflexion+trace` is not "unimplemented," it is "unwired"

`utils.py` already contains a complete `solve_task_reflexion_trace` and
`build_trace_reflection_prompt`, mirroring the retry-loop shape of `solve_task_reflexion_lite` plus
a trace-feedback field. Neither is imported or called from `run.py`. The reason `run.py` raises
`NotImplementedError` is that nothing in the public repo produces the `trace_feedback` string these
functions expect — the retry loop itself was already recovered before this audit; only the
upstream trace-generation stage is missing. Verified by `grep` (see `current_repository.md`).

## D4 — HIGH: no automated Python→C→WASM→Transformer-VM→compression pipeline exists anywhere

Across all four notebooks, the "Percepta" trace section only *loads* a pre-existing
`pilot5_semantic_feedback.jsonl` (cells `EEML` 47–48 / `EEML3` 10–11); it never generates it. No
cell contains C source, a compiler invocation, a `.wasm` artifact, or a call into
`Percepta-Core/transformer-vm`. This matches `paper.pdf`'s own admission ("Percepta doesn't have a
Python-to-WASM translation module yet") and its stated pipeline
(`Mistral Python → (GPT-5 manual) C → WASM → Transformer-VM → trace → (GPT-5 manual) compression →
feedback`). The manual translation/compilation/VM/compression steps happened entirely outside the
notebooks and outside this repository; only their output (the semantic-feedback JSONL) survives.
The `trace_file` field inside that JSONL (e.g. `below_zero_ref.txt`) points to a raw trace that is
not present in the supplied private reference set either.

## D5 — MEDIUM: undefined name in notebook `EEML`, cell 70

`EEML` cell 70 calls `pass_mark(...)`, which is not defined anywhere in any of the four notebooks.
Executing this cell would raise `NameError`. The cell has no stored output, consistent with it
having never completed successfully (or its output being cleared after failure). This affects only
the 8 `EEML`-only "trace-only ablation" cells (65–72), not the core baseline/reflexion-lite/trace
sections shared with `EEML1`/`EEML2`/`EEML3`.

## D6 — MEDIUM: conflicting retry budget for the same 5-task pilot cell

The cell that runs reflexion-lite over the 5-task trace pilot exists in two places with different
hard-coded values: `EEML3` uses `MAX_ITERS = 2`; `EEML`'s copy of the identical cell uses
`MAX_ITERS = 3`. `EEML2`'s standalone copy of `solve_with_reflexion` also defaults to `max_iters=3`,
and `paper.pdf` §2 states the reflexion-lite loop uses "max K = 3". This makes `EEML3` the outlier;
it's unclear whether any of the tracked `results/pilot5_*.jsonl` artifacts were produced under the
`K=2` variant. Verified with a cell-by-cell diff between `EEML` and `EEML3` (see
`notebook_inventory.md` §0).

## D7 — LOW: duplicate (not conflicting) helper definitions inside `EEML`

`normalize_feedback_field` and `pick_last_by_task` are each defined twice within `EEML` (cells
49/57 and 55/63 respectively), with identical bodies both times. Harmless at runtime (the second
definition simply shadows the first), but indicates the notebook was assembled by pasting sections
together rather than importing shared helpers — worth collapsing during extraction into
`reflexion_lite/`.

## D8 — MEDIUM: paper Table 2 is not reproduced by the notebook's own recorded output

`paper.pdf` Table 2 shows `reflexion+trace` passing all 5 pilot tasks, including `intersperse`
(baseline ✗, reflexion-lite ✗, reflexion+trace ✓), implying 5/5 = 1.0 accuracy. Both
trace-augmented implementations found in the notebooks — the single-shot `run_single_semantic_repair`
(cells 50–56) and the iterative `run_reflection_with_trace` (cells 60–64) — have **stored cell
output** showing `intersperse` still failing with `IndexError('list index out of range')` after
trace-augmented repair, giving 4/5 = 0.8 accuracy in both cases, identical to plain reflexion-lite's
4/5. This is a genuine, evidence-backed discrepancy between the published result and the private
artifact trail, not a inference from absence — the notebook literally records the failure. Flagged
for the owner in `recovery_plan.md`; not resolved here per this issue's non-goals (no experiments
were re-run).

## D9 — LOW: two independent, non-identical implementations of core helpers

- **Code-fence extraction**: notebook `extract_code` (single-fence regex) vs. `utils.py`'s
  `extract_python_code` (two-stage fallback: python-tagged fence, bare fence, raw text). The public
  version is a superset of the notebook behavior, not a regression.
- **Sandboxed execution**: notebook `_run_test_in_subprocess`/`run_humaneval_test` (two separate
  `exec()` calls sharing a dict, explicit `check(candidate)` call) vs. `utils.py`'s
  `_run_code_worker`/`run_code_with_tests` (single concatenated `exec()` of code + test +
  `check(entry_point)`). Both use `multiprocessing.Process` + timeout + queue and are conceptually
  equivalent, but not byte-for-byte the same execution strategy — worth characterizing with tests
  before consolidating into one `PythonExecutor`.
- **Prompt construction**: notebook `build_baseline_prompt` applies the tokenizer's chat template;
  `utils.py::build_baseline_prompt` returns a raw f-string with no chat template. This is a real
  behavioral difference for instruction-tuned models like Mistral-7B-Instruct and should be an
  explicit decision, not an accident, when consolidating.
- **Reflection generation**: the notebook has a distinct "generate a natural-language reflection,
  then generate a retry" two-step loop (`generate_reflection` → `build_reflexion_retry_prompt`),
  matching `paper.pdf`'s stated `feedback → reflection → regenerate` loop. `utils.py`'s
  `solve_task_reflexion_lite` skips the separate reflection-generation step and feeds the raw error
  text directly into the retry prompt. This is a simplification relative to both the notebook and
  the paper's described method, not merely a refactor.

## D10 — LOW: unsafe-execution gap (pre-existing, not notebook-specific)

Generated HumanEval code is executed via `multiprocessing.Process` with only a wall-clock timeout —
no memory/CPU limit, no filesystem or network restriction. This applies equally to the public
`utils.py` and to every notebook variant. `.ai/DEFINITION_OF_DONE.md` requires "isolated
subprocess/container with time and resource limits"; current state only satisfies the time part.

## D11 — INFO (positive finding): no hidden-solution leakage found

`canonical_solution` (HumanEval's hidden reference answer field) is printed once, only as a dataset
schema key name (`EEML` cell 8's `dict_keys([...])` output), and is never read by any prompt- or
feedback-building function in the public repo or in any of the four notebooks. No leakage path into
model-visible prompts or reflection feedback was found.

## D12 — INFO (positive finding): no leaked secrets found

Pattern search across all four notebooks for API-key-shaped strings (`sk-...`, `hf_...`, `ghp_...`,
`AKIA...`, inline `api_key=`/`token=` literals) found nothing. `HF_TOKEN` is sourced from
`os.environ` with an interactive `getpass` fallback in both the notebook and (equivalently) in
`run.py`/`utils.py` via the `--hf-token` argument — no token is hard-coded anywhere inspected.

## D13 — LOW: Colab-only hard dependencies in the notebooks

`google.colab.drive.mount(...)` and hard-coded `/content/drive/MyDrive/EEML/...` paths (including a
run-specific path baked into notebook cell `EEML` 46 / `EEML3` 9: `.../run_20260331_112352/results/`)
make the notebook code non-portable as-is. Any extraction into `reflexion_lite/` modules must
parameterize these paths; this is expected and already anticipated by `.ai/ARCHITECTURE.md`.
