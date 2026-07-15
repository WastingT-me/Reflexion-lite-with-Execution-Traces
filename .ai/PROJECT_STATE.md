# Project State

Updated: 2026-07-15

## Confirmed
- Repository entry point: `run.py`.
- Implemented methods: `baseline`, `reflexion-lite`.
- Declared but unimplemented method: `reflexion+trace`.
- Dataset: `openai/openai_humaneval` test split.
- Default model: `mistralai/Mistral-7B-Instruct-v0.3`.
- Selected benchmark: 30 tasks in easy, medium, and bug-prone groups.
- Trace pilot: five tasks from `TRACE_TASK_IDS`.

## Current stage
`agent-ready-infrastructure`

## Blocking decisions
1. Exact source and invocation interface of Transformer-VM.
2. Exact semantic trace representation consumed by the reflection prompt.
3. Whether the final reproduction target must match an existing experimental table/log and, if so, where that reference is stored.

## Next backlog candidates
1. Add dependency metadata and lightweight CI.
2. Add deterministic unit tests around existing pure functions.
3. Introduce structured result/config schemas.
4. Extract generator and executor protocols.
5. Implement trace-provider contract and fixtures.
6. Implement real Transformer-VM adapter after blocking decisions are resolved.
7. Add reproducible benchmark/report generation.

## Agent notes
Do not invent answers to blocking decisions. Infrastructure, tests, refactoring, and interface design may proceed without them. Real `reflexion+trace` implementation may not be marked complete until they are resolved.
