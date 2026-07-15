# Project State

Updated: 2026-07-15

## Confirmed experiment
- `baseline`: one Hugging Face model attempt followed by execution.
- `reflexion-lite`: retry on failure using the previous candidate and execution feedback, without RL or persistent memory.
- `reflexion+trace`: the same retry loop plus compressed feedback derived from the previous Transformer-VM execution trace.
- Dataset: `openai/openai_humaneval` test split.
- Main benchmark: 30 selected tasks in three groups.
- Historical trace pilot: five tasks from `TRACE_TASK_IDS`.
- Default model: `mistralai/Mistral-7B-Instruct-v0.3`.

## Historical trace implementation
The method has previously been implemented in a draft notebook. The historical pipeline was:

```text
Mistral Python -> manual GPT-5 Python-to-C translation -> WASM
-> Percepta Transformer-VM -> raw trace
-> manual GPT-5 trace compression -> Python-friendly feedback
```

`paper.pdf` records this setup and the five-task experiment. Therefore `reflexion+trace` is not an unknown scientific component. The modular `run.py` path currently contains a `NotImplementedError`, but the project task is to recover, validate, modularize, and automate the notebook implementation.

Transformer-VM source:
https://github.com/Percepta-Core/transformer-vm

## Primary project objective
Build the autonomous engineering system around the repository. Scientific method improvements are secondary to creating a safe, testable, issue-driven workflow that can complete the repository without continuous owner intervention.

## Current stage
`agent-ready-infrastructure`

## Current blockers
- The draft notebook filename/location has not yet been identified through the connected repository index.
- Full integration may require local artifacts, external model access, Transformer-VM dependencies, and substantial trace storage.

These blockers do not prevent CI, tests, modular interfaces, notebook inventory, or the autonomous harness.

## Next backlog candidates
1. Locate and inventory all notebooks and historical trace artifacts.
2. Add dependency metadata and deterministic tests for current pure functions.
3. Reproduce known baseline/reflexion-lite behavior with fake generators.
4. Extract the notebook trace pipeline into explicitly staged modules.
5. Preserve a manual-artifact compatibility mode.
6. Add automated Python-to-C/WASM conversion behind an adapter.
7. Add automated raw-trace compression behind an adapter.
8. Build the issue-selection, worktree, bounded-retry, CI-fix, and PR-review harness.
9. Add reproducible benchmark/report generation.

## Agent notes
Do not redesign the experiment before recovering the existing implementation. Treat notebook code as potentially buggy evidence, not as trusted production code. Prefer small test-backed extraction tasks. Clearly label mocks, historical manual artifacts, and real Transformer-VM outputs.
