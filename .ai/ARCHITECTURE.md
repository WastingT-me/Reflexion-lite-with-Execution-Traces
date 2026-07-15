# Target Architecture

## Current state

`run.py` owns CLI orchestration. `task_registry.py` defines the 30 selected HumanEval tasks and the five trace pilot tasks. `utils.py` currently combines dataset loading, model loading, prompting, generation, execution, metrics, and result serialization. `reflexion+trace` is declared but raises `NotImplementedError`.

## Target modules

```text
run.py                     CLI only
reflexion_lite/config.py   validated experiment configuration
reflexion_lite/tasks.py    dataset and task selection
reflexion_lite/models.py   model/generator protocol and HF adapter
reflexion_lite/prompts.py  prompt construction
reflexion_lite/execution.py isolated code execution
reflexion_lite/traces.py   trace-provider protocol and Transformer-VM adapter
reflexion_lite/agents.py   baseline/reflexion loops
reflexion_lite/results.py  schemas, JSONL persistence, summaries
reflexion_lite/evals.py    comparison metrics
```

Migration must be incremental; behavior-preserving refactors require tests before moving code.

## Core interfaces

### Generator
Accepts a prompt and generation configuration and returns generated text plus metadata. Tests use a deterministic fake implementation.

### Executor
Accepts a HumanEval problem and candidate code. Returns a structured execution result with pass/fail, exception, stdout, duration, and timeout status. Production execution must be isolated and resource-bounded.

### TraceProvider
Accepts the problem, candidate code, and execution result. Returns structured semantic trace feedback and provenance. The exact Transformer-VM integration is a blocking product decision documented in `PRODUCT_SPEC.md`.

### Solver
Runs one method for one task and emits immutable attempt records. Reflexion stops on pass or after `max_iters`.

## Data flow

```text
CLI config -> task loader -> generator -> executor
                                  ^          |
                                  |          v
                         reflection prompt <- feedback
                                  ^
                                  |
                     trace provider (trace method only)
```

## Dependency rules
- Core schemas and protocols must not import Torch or Transformers.
- Hugging Face dependencies belong in the model adapter.
- Trace integration is behind an interface and must be replaceable by a fixture in tests.
- Result records are versioned to permit future schema changes.
- No module may read secrets except the CLI/config boundary.
