# Private Notebook Inventory

Inputs: four private draft notebooks supplied locally at `../reflexion-private-reference/`
(`EEML`, `EEML1`, `EEML2`, `EEML3` — valid Jupyter JSON, missing the `.ipynb` extension),
`paper.pdf`, and the public repository. All four were parsed statically as JSON and read
cell-by-cell. **No cell was executed.** This document paraphrases structure and behavior only;
it does not reproduce notebook source beyond short function/variable identifiers, consistent
with `.ai/PRIVATE_ARTIFACTS.md`.

## 0. Structural relationship between the four notebooks

`EEML` (73 cells) is effectively the author's consolidated/master notebook. Programmatic
cell-by-cell diffing against the other three shows:

| Notebook | Cells | Relationship to `EEML` |
|---|---|---|
| `EEML1` | 25 | Identical to `EEML` cells 0–24 (the "baseline" section), byte-for-byte, 0 mismatches. |
| `EEML2` | 12 | Matches `EEML` cells 25–36 (the "reflection-lite" section) in 11/12 cells. The one mismatch is the pilot driver cell: `EEML2` runs it with `max_iters=3`, `EEML` (and the function default) also uses `3` — see conflict note below. |
| `EEML3` | 28 | Matches `EEML` cells 37–64 (the "Percepta - transformer-interpreter" section) in 27/28 cells. The one mismatch: `EEML3`'s pilot driver hard-codes `MAX_ITERS = 2`, `EEML`'s equivalent cell uses `MAX_ITERS = 3` for the same 5-task reflexion-lite pilot run. |
| — | +8 | `EEML` has 8 extra trailing cells (65–72) not present in any standalone notebook: a second, separate "trace-only" ablation (`build_trace_only_feedback`, `run_reflection_with_trace_only`) plus a 4-way comparison table. Cell 70 of that block calls an undefined `pass_mark(...)` (see `defects.md` D5) and has no stored output, i.e. it never ran to completion. |

Given this, `EEML1`/`EEML2`/`EEML3` are best read as earlier, per-stage working copies, and `EEML`
as the latest consolidated version with one added (and apparently broken) ablation. The tables
below describe `EEML`'s cell ranges as the canonical source; `EEML1`/`EEML2`/`EEML3` are noted only
where they diverge.

## 1. Baseline section (`EEML` cells 0–24 ≡ `EEML1` cells 0–24)

| Cells | Purpose | Key names | Side effects / status |
|---|---|---|---|
| 0 | Markdown header "baseline" | — | — |
| 1–2 | Shell installs (`pip install transformers accelerate datasets sentencepiece bitsandbytes`, `huggingface_hub`) | — | Colab-only shell magics (`!pip`) |
| 3 | Google Drive mount + run-directory layout | `PROJECT_ROOT`, `RUN_DIR`, `DIRS` | Hard-coded `/content/drive/MyDrive/EEML` path; Colab-only (`google.colab.drive`) |
| 4 | HF auth | `HF_TOKEN` | Reads `os.environ`, falls back to interactive `getpass`; token not hard-coded — no leak found |
| 5 | Imports | `torch`, `datasets`, `transformers` | — |
| 6 | GPU smoke print | — | Requires CUDA; not portable to CI |
| 7 | Model/tokenizer load | `MODEL_NAME="mistralai/Mistral-7B-Instruct-v0.3"` | Matches `run.py`'s default model exactly |
| 8 | Dataset load, prints dataset schema | `ds` | Confirms HumanEval features include `canonical_solution`; schema is only printed, never propagated into a prompt (see integrity check in `current_repository.md`) |
| 9 | Task lists | `EASY_TASKS`, `MEDIUM_TASKS`, `BUG_PRONE_TASKS`, `SELECTED_TASK_IDS` | Byte-identical (task IDs) to `task_registry.py` — **inherited** into the public repo already |
| 10–11 | Subset indexing, prompt preview helper | `id_to_example`, `short_prompt_preview` | — |
| 12 | Prompt construction | `build_baseline_prompt` | Uses `tokenizer.apply_chat_template`; conceptually the same role as `utils.py::build_baseline_prompt`, but the notebook version applies the model's chat template while the public version returns a raw f-string — **divergent, not byte-identical** |
| 13 | Output cleaning | `extract_code` | Single-fence regex `` ```(?:python)?\n(.*?)``` ``; public `utils.py::extract_python_code` has a two-stage fallback (`python`-tagged fence, then bare fence, then raw text) — public version is strictly more permissive |
| 14 | Generation | `generate_completion` | Sampling generation wrapping `build_baseline_prompt` + `extract_code` |
| 15 | Sandboxed execution | `_run_test_in_subprocess`, `run_humaneval_test` | `multiprocessing.Process` + queue + timeout; code and test are `exec`'d as **two separate `exec()` calls** into a shared dict, then `check(candidate)` is invoked explicitly. Public `utils.py::_run_code_worker`/`run_code_with_tests` instead concatenates code + test + a `check(entry_point)` call into **one string** and execs it once. Behaviorally similar, not identical — worth reconciling when extracting `reflexion_lite/execution.py` |
| 16 | One-task smoke test | — | Interactive/manual step |
| 17 | Full 30-task baseline run | `MAX_NEW_TOKENS=512`, `TEMPERATURE=0.2`, `TOP_P=0.95`, `TIMEOUT=10` | Matches `run.py` CLI defaults exactly. Stored output records a real run: **13/30 passed, pass@1 = 0.4333** |
| 18–19 | Metrics print (overall, by category) | — | Stored output: easy 5/10, medium 6/10, bug_prone 2/10 — **this is the "Baseline" row of paper Table 1**, and it is internally consistent with the per-category numbers reported there |
| 20 | Output path constants | `BASELINE_JSONL_PATH`, `REFLEXION_JSONL_PATH`, `REFLEXION_TRACE_JSONL_PATH`, `SUBSET_PATH`, `FAILURES_PATH` | Paths under the Colab-only `DIRS` tree |
| 21–24 | Persist subset, list/persist failures | — | Writes JSONL to Drive paths; not portable as-is |

## 2. Reflexion-lite section (`EEML` cells 25–36 ≈ `EEML2` cells 0–11)

| Cells | Purpose | Key names | Status |
|---|---|---|---|
| 25 | Markdown header | — | — |
| 26 | `import time` | — | — |
| 27 | Custom-prompt generation | `generate_from_prompt` | Second, parallel implementation of "generate + decode" alongside cell 14's `generate_completion` — same underlying `model.generate` call, different signature (prompt string vs. `problem` dict) |
| 28 | Prompt builders | `build_reflexion_initial_prompt`, `build_reflexion_retry_prompt`, `build_reflection_prompt` | Three distinct prompt templates: first attempt, retry-with-feedback, and a separate "explain the bug" reflection prompt. `utils.py` only has an equivalent to the first two (`build_baseline_prompt`, `build_reflection_prompt`) — it has **no separate reflection-generation step**; the public `solve_task_reflexion_lite` bakes the error text directly into the retry prompt instead of first generating a natural-language reflection. This is a **behavioral simplification relative to the notebook and to the paper's stated `generate → execute → feedback → reflection → regenerate` loop** |
| 29 | Reflection generation | `generate_reflection` | Calls `build_reflection_prompt` then generates a short (`max_new_tokens=220`) natural-language reflection — the step missing from `utils.py` |
| 30 | Feedback text assembly | `shorten_text`, `build_feedback_text` | Truncates error/traceback/trace text to bounded lengths before it re-enters a prompt |
| 31 | Single-task reflexion loop | `solve_with_reflexion` | Iterates `max_iters` times, generates a reflection only on failure, tracks `previous_code`/`reflection_text` across iterations. **`EEML`'s copy defaults `max_iters=2`; `EEML2`'s copy of the same function defaults `max_iters=3`** — the two working copies of this exact function disagree on the retry budget (see `defects.md` D6) |
| 32 | Full 30-task reflexion-lite run | `MAX_ITERS=3` | Stored output: **task-level 20/30 passed, accuracy 0.6667**, by category easy 7/10, medium 7/10, bug_prone 6/10 — **matches paper Table 1's "R-l" row exactly** |
| 33 | Metrics helpers | `aggregate_task_success`, `print_task_level_metrics` | — |
| 34 | Print reflexion metrics | — | reprints the same numbers as cell 32's summary |
| 35 | Persist reflexion JSONL | — | — |
| 36 | `baseline_task_rows_to_metrics` | — | Unused-looking helper; not referenced elsewhere in this notebook |

## 3. Percepta / trace section (`EEML` cells 37–72 ≈ `EEML3` cells 0–27, plus 8 `EEML`-only cells)

This is the section most relevant to `reflexion+trace` recovery. It has **no code anywhere that
performs Python→C translation, C→WASM compilation, or Transformer-VM execution.** It only
*consumes* a pre-existing file.

| Cells | Purpose | Key names | Status |
|---|---|---|---|
| 37 | Markdown header "Percepta - transformer-interpeter" | — | — |
| 38 | Fixed 5-task pilot set | `TARGET_ENTRY_POINTS` | `below_zero, rolling_max, sum_product, intersperse, has_close_elements` — identical to `task_registry.py::TRACE_TASK_IDS` |
| 39 | Pilot output paths | `PILOT_BASELINE_JSONL_PATH`, `PILOT_REFLEXION_JSONL_PATH`, `PILOT_PYTHON_SOLUTIONS_JSONL_PATH`, `PILOT_TRACE_REPAIR_JSONL_PATH` | — |
| 40–41 | Run + persist baseline on the 5 pilot tasks | — | Reuses cell 14/15's `generate_completion`/`run_humaneval_test` |
| 42 | Run reflexion-lite on the 5 pilot tasks | `MAX_ITERS` | **`EEML`: `MAX_ITERS=3`; `EEML3`: `MAX_ITERS=2`** for the identical cell — direct conflict, see `defects.md` D6 |
| 43 | Persist reflexion pilot results | — | — |
| 44–45 | Build/print an intermediate "python solutions" file merging baseline + reflexion rows | `pilot_python_rows` | Written to `PILOT_PYTHON_SOLUTIONS_JSONL_PATH` — this is the file that later became the tracked `results/pilot5_python_solutions.jsonl` in the public repo (task IDs, entry points, and method labels match) |
| 46 | Standalone script: extract concrete HumanEval assert cases | `load_selected_tasks`, `load_humaneval_records`, `get_source_segment_safe`, `literal_eval_safe`, `find_candidate_call`, `extract_expected_from_assert_test`, `extract_assert_cases`, `main` | Reads `INPUT_SOLUTIONS` and writes `OUTPUT_TESTS` at a **hard-coded path** `BASE_PATH = "/content/drive/MyDrive/EEML/run_20260331_112352/results/"`. AST-parses each task's HumanEval `test` string, extracts the `candidate(...)` args and expected value per `assert`. This is the "boundary" artifact that would be handed to a Python→C translator: concrete inputs/outputs, not source translation itself. **Functionally duplicated (not byte-identical, nested vs. top-level) by `utils.py::extract_humaneval_tests_for_tasks`**, which is currently dead code in the public repo |
| 47–48 | Load `pilot5_semantic_feedback.jsonl`, select final baseline/reflexion rows | `PILOT_SEMANTIC_FEEDBACK_JSONL_PATH`, `load_jsonl`, `select_final_baseline_rows`, `select_final_reflexion_rows` | **This file is only ever read, never produced by any cell in any of the four notebooks.** It is the manually-produced trace-compression output described in `paper.pdf`'s pipeline ("(GPT-5 manual) compression"). Its schema (verified from the tracked `results/pilot5_semantic_feedback.jsonl`) is `task_id, entry_point, trace_file, trace_input, observed_output, expected_output, semantic_trace, feedback_text, python_solution_notes`. The `trace_file` field (e.g. `below_zero_ref.txt`) references a raw trace file that is **not present** anywhere in the supplied private reference set |
| 49 | Feedback normalization/merge helpers | `normalize_feedback_field`, `build_original_failure_feedback`, `build_merged_feedback_text` | First of two `normalize_feedback_field` definitions in this notebook (see D7) |
| 50 | Single-shot "Percepta-style" repair | `run_single_semantic_repair` | Takes one previous (failed) row + the matching semantic-feedback row, generates one reflection + one repaired candidate. Tags results `"{source_method}_semantic_repair"` |
| 51–53 | Run/persist/print single-shot repair over baseline-final and reflexion-final rows | `pilot_trace_repair_results` | Stored output shows, for the 5-task pilot, `intersperse` still failing after repair with `IndexError('list index out of range')` |
| 54 | Metrics for the single-shot repair results | `filter_rows_by_method` | — |
| 55–56 | Build final baseline/reflexion/"reflection+trace" comparison table (uses the **single-shot** repair as the trace column) | `pick_last_by_task` (1st def) | Stored output confirms: baseline 3/5, reflection 4/5 (`intersperse` fails with `AssertionError`, `sum_product` needs 1 retry), reflection+trace 4/5 (`intersperse` **still fails**, with `IndexError`) |
| 57–59 | Second copy of `normalize_feedback_field` (identical body to cell 49's), plus `build_code_prompt` | `normalize_feedback_field` (2nd def, duplicate), `build_code_prompt` | Duplicate definition, harmless (same body) but indicates copy-paste rather than reuse |
| 58 | `build_reflection_trace_feedback` | — | A third feedback-assembly variant: unit-test feedback + previous reflection + semantic feedback + structured semantic trace, all in one prompt block |
| 60 | Iterative "reflexion+trace" loop, second implementation | `run_reflection_with_trace` | Unlike `run_single_semantic_repair`, this repeats for `max_attempts` retries, but **reuses the same static `semantic_row` (i.e. the same pre-computed trace) on every retry** — the trace is never recomputed against the newest failing candidate. This is the implementation whose behavior most resembles `utils.py::solve_task_reflexion_trace`'s signature (it also takes trace feedback as a single static string) |
| 61–62 | Run/persist the iterative trace loop over the 5 pilot tasks (`max_attempts=5`, comment: "same as regular reflexion" — inconsistent with `MAX_ITERS` used elsewhere, which is 2 or 3) | `pilot_reflection_trace_results` | — |
| 63–64 | Second `pick_last_by_task` def (identical body), accuracy summary | `accuracy_from_task_map` | Stored output: **baseline 3/5=0.6, reflection 4/5=0.8, reflection+trace 4/5=0.8** — i.e. the iterative implementation, run in this notebook, does **not** improve over plain reflexion on this pilot, and disagrees with `paper.pdf` Table 2 (see `defects.md` D8) |
| 65–66 | Trace-only ablation (feedback with *no* unit-test error, only semantic trace) | `build_trace_only_feedback`, `run_reflection_with_trace_only` | Exists only in `EEML`, not in `EEML3` |
| 67–68 | Run/persist trace-only ablation | `pilot_reflection_trace_only_results` | — |
| 69 | `pick_last_by_task` call | — | — |
| 70 | Build 4-way comparison table | calls undefined `pass_mark(...)` | **No `pass_mark` definition exists anywhere in any of the four notebooks.** This cell has no stored output — it never ran, or its output was cleared after an error |
| 71 | 4-way accuracy summary | — | Stored output: baseline 0.6, reflection 0.8, reflection+trace 0.8, reflection+trace-only 0.6 |
| 72 | Empty trailing cell | — | — |

## 4. Grouping (per skill taxonomy)

- **Baseline**: cells 0–24 (all four notebooks agree).
- **Reflexion-lite**: cells 25–36, with one budget conflict (D6).
- **Trace processing / compression consumption**: cells 46–49, 57–59 — reads externally-produced
  trace/feedback artifacts; contains no translation, compilation, or VM-execution code.
- **Evaluation**: cells 18–19, 33–34, 54–56, 63–64, 70–71.
- **Setup**: cells 1–7 (Colab/Drive/HF/model boot).
- **Unused/obsolete**: cell 36 (`baseline_task_rows_to_metrics`, not called), cell 70 (broken,
  undefined name), the duplicate `normalize_feedback_field`/`pick_last_by_task` definitions.
- **Unclear / needs owner input**: which of the two `reflexion+trace` designs (single-shot repair
  vs. static-trace iterative retry) is the intended target behavior; whether the raw trace file
  referenced by `trace_file` exists anywhere; the Table 2 discrepancy.
- No cells were classified **unsafe** beyond the general HumanEval-code-execution sandboxing gap
  already present in the public repo (`current_repository.md`); no Python-to-C, C-to-WASM, or
  Transformer-VM code was found to review for safety because none exists in these notebooks.
