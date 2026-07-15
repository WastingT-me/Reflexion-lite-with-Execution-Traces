# Product specification

## Purpose

Build a reproducible research codebase comparing three code-generation strategies on a controlled HumanEval subset:

1. `baseline`: single-pass generation and execution.
2. `reflexion-lite`: iterative repair using execution failures.
3. `reflexion+trace`: iterative repair using execution failures plus semantic execution-trace feedback produced by the intended Transformer-VM integration.

The repository must support installation, execution of each method, per-attempt artifacts, method comparison, and reproduction from a clean environment.

## Current confirmed scope

- Benchmark: OpenAI HumanEval loaded through Hugging Face datasets.
- Main subset: 30 tasks in `task_registry.py`, grouped as easy, medium, and bug-prone.
- Trace pilot subset: five tasks in `TRACE_TASK_IDS`.
- Default model: `mistralai/Mistral-7B-Instruct-v0.3`.
- CLI entry point: `run.py`.
- Results: JSONL with prompts, code, execution status, errors, reflections, and attempt number.

## Required capabilities

### Installation and configuration

- Documented Python version and dependency installation.
- Versioned or bounded dependencies.
- Optional Hugging Face authentication without committed secrets.
- CPU-compatible tests that do not download a large model.

### Baseline

- Select configured tasks.
- Generate one candidate per task.
- Execute it with a strict timeout in an isolated process.
- Persist one structured result per task.
- Report group and overall pass rates.

### Reflexion-lite

- Start from a baseline-style attempt.
- On failure, construct feedback from execution.
- Retry until success or `max_iters`.
- Persist every attempt.
- Report final-attempt improvement over baseline.

### Reflexion+trace

- Preserve the execution-feedback loop.
- Obtain semantic trace feedback through a replaceable trace-provider interface.
- Include semantic and concrete execution feedback in repair prompts.
- Persist raw and normalized trace feedback.
- Fail clearly when a real provider is unavailable; never fabricate traces silently.
- Provide a deterministic fake provider for tests.

### Evaluation and reproducibility

- Produce machine-readable summary metrics.
- Separate configuration from results.
- Record model, generation settings, selected tasks, revision, timestamps, and seeds.
- Provide a deterministic CI smoke evaluation.
- Preserve raw attempt-level artifacts.

## Non-goals for the first milestone

- Model training or fine-tuning.
- Reimplementing Transformer-VM from scratch without an explicit integration contract.
- Supporting arbitrary languages or benchmarks.
- Building a web UI.
- Claiming improvement without reproducible evidence.

## Scientific integrity constraints

- Compare methods with equivalent model and generation settings unless differences are recorded.
- Keep failures, timeouts, and malformed generations in results.
- Do not change task selection after inspecting results without a new configuration.
- Compute metrics from persisted artifacts.
- Never expose hidden reference solutions or test answers in trace feedback.

## Owner questions blocking final trace implementation

1. Which exact Transformer-VM implementation, checkpoint, package, repository, or API provides semantic traces?
2. What is the trace input: Python source, compiled WebAssembly, test input, or another representation?
3. What exact trace output is passed to the repair model?
4. Should `reflexion+trace` support only the five pilot tasks or all 30 tasks?
5. Which existing results are the target reproduction baseline?
6. Which hardware must the documented full experiment support?

Until answered, agents may implement interfaces, deterministic fakes, validation, tests, and documentation, but must not invent the scientific trace component.
