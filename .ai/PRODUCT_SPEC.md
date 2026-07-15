# Product specification

## Primary purpose

The primary goal is to turn this repository into an agent-ready software project that an autonomous coding system can inspect, repair, test, document, and complete through bounded GitHub issues and pull requests.

Scientific perfection is not the first milestone. Agents should preserve the intended experiment, recover the existing draft implementation, and improve it incrementally rather than redesigning the research method from scratch.

## Experiment

The repository compares three inference-time code-generation methods on HumanEval using the same Hugging Face model and generation settings where possible.

### 1. Baseline
Generate one Python solution with the configured Hugging Face model, execute it, store the result, and do not retry.

### 2. Reflexion-lite
This is an intentionally simplified Reflexion variant without reinforcement learning, model training, or persistent memory.

1. Generate a Python solution.
2. Execute it against the task tests.
3. If it passes, stop.
4. If it fails, add the previous candidate and execution feedback to the next prompt.
5. Retry until success or `max_iters`.

### 3. Reflexion+trace
Use the same retry loop as Reflexion-lite, but also add feedback derived from the previous execution trace.

Reference implementation and articles:
- https://github.com/Percepta-Core/transformer-vm
- https://www.percepta.ai/blog/constructing-llm-computer
- https://www.percepta.ai/blog/can-llms-be-computers

The historical draft pipeline documented in `paper.pdf` was:

```text
Mistral Python -> manual GPT-5 translation to C -> C to WebAssembly
-> Transformer-VM execution -> raw trace -> manual GPT-5 compression
-> Python-friendly feedback -> next Mistral attempt
```

This pipeline was already used as a five-task baseline. It is imperfect because translation and compression were manual and raw traces can contain millions of low-level rows, but it is valid project state and must not be described as nonexistent.

The desired automated pipeline is:

```text
Python candidate -> automated conversion -> C/WASM artifact
-> Transformer-VM -> raw trace artifact -> automated compression
-> Python-friendly trace feedback -> next model attempt
```

The agent should first recover and modularize the notebook implementation, then automate manual stages incrementally. A reproducible pragmatic baseline is preferred over an ambitious rewrite that never runs.

## Confirmed scope
- Benchmark: OpenAI HumanEval via Hugging Face datasets.
- Main subset: 30 tasks in `task_registry.py`.
- Trace pilot: five tasks in `TRACE_TASK_IDS`.
- Default model: `mistralai/Mistral-7B-Instruct-v0.3`.
- CLI entry point: `run.py`.
- Existing modular code may contain errors.
- A draft notebook contains the previous trace implementation and is the primary recovery source when available.
- `paper.pdf` describes the experiment and historical pipeline.

## Required agent engineering
- Repository instructions and modular skills.
- Bounded issues with acceptance criteria and non-goals.
- Feature branches and PRs; no direct autonomous writes to `main`.
- Lightweight deterministic tests without a large model download.
- Failure classification, retry limits, state logging, and stop conditions.
- Independent PR review.

## Required experiment behavior
- All three methods use a consistent interface.
- Every attempt persists candidate, execution feedback, trace feedback when applicable, and configuration.
- Baseline performs exactly one attempt.
- Reflexion-lite and Reflexion+trace stop on success or attempt limit.
- Trace provenance records translation, compilation, Transformer-VM, and compression artifacts where available.
- CI may use deterministic fake model and trace adapters; these must be clearly marked as test doubles.

## Milestone priorities
1. Make the repository safe and legible for autonomous agents.
2. Inventory and test existing modules and the notebook.
3. Recover the historical trace pipeline into executable modules.
4. Automate translation and trace compression.
5. Improve scientific rigor after an end-to-end baseline exists.

## First-milestone non-goals
- Reinforcement learning or persistent Reflexion memory.
- Model training or fine-tuning.
- Reimplementing Transformer-VM.
- Publication-grade performance claims.
- Replacing the historical method only because it is imperfect.

## Integrity constraints
- Never fabricate traces or benchmark results.
- Never expose hidden HumanEval reference solutions in feedback.
- Preserve failures, timeouts, malformed generations, and conversion failures.
- Distinguish historical manual artifacts, automated outputs, mocks, and real Transformer-VM runs.

## Remaining useful owner information
These details do not block agent-infrastructure work:
1. Exact filename/location of the draft notebook.
2. Whether it contains raw traces, compressed feedback, C/WASM artifacts, or only code.
3. Preferred translation/compression model and whether paid APIs are acceptable.
4. Hardware target for full experiments.
