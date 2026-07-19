# Recovery Plan

Derived from `current_repository.md`, `notebook_inventory.md`, and `defects.md`. No production
code is changed by this issue; this is the proposed backlog for subsequent bounded issues, in
dependency order. Each entry states attribution category per `.ai/PROVENANCE.md` (Inherited /
Recovered / Agent-designed / Owner-directed) and a minimal test.

## Recovered end-to-end pipeline (as it actually exists today, not as designed)

```text
task -> build_baseline_prompt -> Mistral generate -> extract_python_code
     -> run_code_with_tests (pass/fail + traceback)
     -> [reflexion-lite only] retry with raw error text folded into next prompt, up to max_iters
     -> [reflexion+trace, NOT WIRED] would need: previous failing candidate + concrete
        assert-derived test cases (utils.py::extract_humaneval_tests_for_tasks, currently dead)
        -> (manual, outside this repo, evidence only) Python->C -> WASM -> Transformer-VM -> raw trace
        -> (manual, outside this repo, evidence only) GPT-5 compression -> semantic_trace/feedback_text
        -> build_trace_reflection_prompt / solve_task_reflexion_trace (both dead code today)
```

The manual stage in the middle is not missing code we haven't found — it is evidenced to not exist
in any inspected artifact (D4). It is a human-in-the-loop process whose only surviving output is
`results/pilot5_semantic_feedback.jsonl`.

## Target modules (restating `.ai/ARCHITECTURE.md`, annotated with current evidence)

```text
reflexion_lite/config.py       new — validated CLI/experiment config (currently argparse only)
reflexion_lite/tasks.py        mostly inherited from task_registry.py, already correct
reflexion_lite/models.py       inherited generation logic from utils.py, but must resolve D9's
                                chat-template and reflection-step divergences first
reflexion_lite/prompts.py      inherited from utils.py + notebook, must decide D9 items explicitly
reflexion_lite/execution.py    inherited concept, two divergent implementations to reconcile (D9)
reflexion_lite/agents.py       baseline/reflexion-lite inherited and working end-to-end;
                                reflexion+trace exists as dead code (D3), needs wiring only
reflexion_lite/results.py      inherited save_jsonl/load_jsonl, straightforward
reflexion_lite/evals.py        inherited compute_group_metrics/print_method_comparison_table

reflexion_lite/trace_pipeline/interfaces.py    new — no notebook equivalent exists
reflexion_lite/trace_pipeline/artifacts.py     new — no notebook equivalent exists
reflexion_lite/trace_pipeline/translator.py    new — genuinely unimplemented anywhere (D4)
reflexion_lite/trace_pipeline/compiler.py      new — genuinely unimplemented anywhere (D4)
reflexion_lite/trace_pipeline/transformer_vm.py new — genuinely unimplemented anywhere (D4)
reflexion_lite/trace_pipeline/compressor.py    new — genuinely unimplemented anywhere (D4)
reflexion_lite/trace_pipeline/historical.py    recovered — schema known exactly from
                                                results/pilot5_semantic_feedback.jsonl
```

## Ordered issue backlog

1. **DONE — Fix the `utils`/`utills` import mismatch so the CLI runs at all.**
   Category: Agent-designed (bug fix, no notebook recovery involved).
   Test: `python -m py_compile run.py task_registry.py utils.py` succeeds; `python run.py --method
   baseline --help` runs without a module-name `ModuleNotFoundError`.
   Fixed on `main` by commit `70880ed` (PR #4, merged 2026-07-19), outside this audit issue's
   scope. No longer blocks the rest of this backlog — see `defects.md` D1.

2. **DONE — Resolve the tracked-`results/`-vs-CI-gate conflict (owner-directed decision required).**
   Option (a) was chosen: the three named historical files are explicitly allow-listed in the CI
   grep; everything else under `results/`/`__pycache__/` is still rejected. Category: Owner-directed.
   Test: `.github/workflows/agent-readiness.yml`'s tracked-output step passes.
   Fixed on `main` by commit `47169de` (PR #6, Issue #5, merged 2026-07-19), outside this audit
   issue's scope — see `defects.md` D2.

3. **Add dependency metadata and a minimal deterministic test suite.**
   Cover: task selection (`task_registry.py`), `extract_python_code`, `save_jsonl`/`load_jsonl`,
   `take_last_attempt_per_task`, `run_code_with_tests` timeout and pass/fail behavior, using a fake
   generator (no model download). Category: Agent-designed.
   Test: `pytest` green in CI.

4. **Reconcile the duplicated execution/prompt/extraction helpers (D9) with characterization
   tests before consolidating into `reflexion_lite/execution.py` and `prompts.py`.** Decide,
   explicitly and owner-visible: chat-template vs. raw f-string prompts; single-shot vs. two-step
   reflection generation (the paper's described loop uses the two-step form; current `utils.py`
   does not). Category: Recovered + Owner-directed (behavioral choice).
   Test: characterization tests pinning current `run.py` behavior, then updated tests for the
   chosen behavior.

5. **Wire the already-recovered `solve_task_reflexion_trace`/`build_trace_reflection_prompt`
   into `run.py`, sourced from a `historical.py` adapter that loads
   `results/pilot5_semantic_feedback.jsonl`-shaped data with explicit `provenance="historical-manual"`
   tagging.** This removes the blanket `NotImplementedError` for the 5-task `--trace-only` path
   without fabricating any new trace data. Category: Recovered.
   Test: contract test asserting historical-mode results are tagged as historical, not as a live
   Transformer-VM run; end-to-end fixture reproducing the 5-task pilot's baseline/reflexion-lite
   numbers (13→20/30 scale numbers don't apply here, use the 3/5, 4/5 pilot numbers from
   `notebook_inventory.md` §3 as the fixture target).

6. **Add `trace_pipeline/interfaces.py` and `artifacts.py`** (protocols + provenance schema) so
   historical vs. automated stages are distinguishable in results, per `.ai/ARCHITECTURE.md`.
   Category: Agent-designed.
   Test: schema/contract tests only, no model or VM dependency.

7. **Investigate the D8 paper-vs-evidence discrepancy on `intersperse` before treating either the
   paper's Table 2 or the notebooks' recorded 4/5 as ground truth for regression tests.**
   Category: Owner-directed. No test until resolved — this is a data question, not a code question.

8. **Only after 5–7 land: begin automating `translator.py` (Python→C) and `compressor.py`
   (raw trace→feedback) behind the interfaces from step 6**, per `PRODUCT_SPEC.md`'s milestone
   ordering ("reproducible pragmatic baseline... before an ambitious rewrite"). Category:
   Agent-designed, pending owner sign-off on translation/compression model choice (see open
   question below).

9. **Harden `PythonExecutor` to add resource limits (D10)**, matching
   `.ai/DEFINITION_OF_DONE.md`'s safety bar. Category: Agent-designed. Independent of the trace work;
   can be scheduled anytime after step 3's test scaffold exists.

## Unresolved owner questions

1. **ANSWERED (Issue #5, PR #6):** yes — `results/pilot5_humaneval_tests.jsonl`,
   `pilot5_python_solutions.jsonl`, and `pilot5_semantic_feedback.jsonl` remain tracked as
   intentional historical evidence, in place under `results/`. The CI gate was updated to
   explicitly allow-list these three exact paths rather than relocating them.
2. Between the notebooks' two divergent `reflexion+trace` designs — single-shot
   `run_single_semantic_repair` vs. iterative `run_reflection_with_trace` with a static trace reused
   every retry — which should `reflexion_lite/agents.py`'s Solver implement?
3. Why does `MAX_ITERS` differ (2 in `EEML3` vs. 3 in `EEML`/`EEML2`/the paper) for the same 5-task
   pilot cell (D6)? Which run's stored numbers, if either, should be treated as authoritative?
4. Does `paper.pdf` Table 2's "reflexion+trace passes `intersperse`" reflect a run not present in
   the supplied notebooks, or should the paper's table be corrected to 4/5 (D8)?
5. Is a raw Transformer-VM trace file (the `trace_file` field, e.g. `below_zero_ref.txt`, referenced
   inside `pilot5_semantic_feedback.jsonl`) available anywhere, or is `semantic_trace`/
   `feedback_text` the only surviving evidence of the VM stage?
6. Restated from `.ai/PRODUCT_SPEC.md` (still open, not addressed by this audit): preferred
   translation/compression model and whether paid APIs are acceptable; hardware target for full
   30-task and 5-task experiments.
