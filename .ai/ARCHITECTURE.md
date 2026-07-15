# Target Architecture

## Current state

`run.py` owns CLI orchestration. `task_registry.py` defines the selected HumanEval tasks. `utils.py` combines dataset loading, prompting, Hugging Face generation, generated-code execution, metrics, and result serialization.

The modular CLI path currently raises `NotImplementedError` for `reflexion+trace`. This does not mean the method has never been implemented: the historical implementation exists in a draft notebook and is described in `paper.pdf`. It used manual Python-to-C translation and manual raw-trace compression around Percepta Transformer-VM.

The immediate architecture task is recovery and controlled extraction, not a clean-room rewrite.

## Target modules

```text
run.py                         CLI only
reflexion_lite/config.py       validated experiment configuration
reflexion_lite/tasks.py        dataset and task selection
reflexion_lite/models.py       generator protocol and Hugging Face adapter
reflexion_lite/prompts.py      baseline, execution-feedback, and trace prompts
reflexion_lite/execution.py    isolated Python candidate execution
reflexion_lite/agents.py       three bounded attempt loops
reflexion_lite/results.py      attempt schemas and persistence
reflexion_lite/evals.py        comparison metrics

reflexion_lite/trace_pipeline/
  interfaces.py                translator/compiler/VM/compressor protocols
  artifacts.py                 provenance and artifact schemas
  translator.py                Python -> supported C or other intermediate form
  compiler.py                  C -> WASM adapter
  transformer_vm.py            Percepta Transformer-VM adapter
  compressor.py                raw trace -> Python-friendly feedback
  historical.py                compatibility with manual notebook artifacts
```

Migration must be incremental. First add tests around observable notebook/current-code behavior, then extract one stage at a time.

## Core interfaces

### Generator
Accepts a prompt and generation configuration and returns generated text plus metadata. CI uses a deterministic fake.

### PythonExecutor
Executes the generated Python candidate against a HumanEval task in a resource-bounded environment and returns structured execution feedback.

### ProgramTranslator
Converts the failed Python candidate and relevant test input into the representation supported by the downstream compiler/VM. It may initially consume a historical manual C artifact.

### WasmCompiler
Produces a WASM artifact with command, tool versions, stdout, stderr, and checksums recorded.

### TransformerVMRunner
Runs the WASM artifact through `Percepta-Core/transformer-vm` and persists the raw trace or an external artifact reference. It must not load millions of trace rows into prompts.

### TraceCompressor
Converts a raw low-level trace plus the original Python candidate and failure context into concise Python-friendly feedback. Historical manual summaries and automated LLM summaries must be distinguishable by provenance.

### Solver
Runs exactly one of three policies:
- baseline: one attempt;
- reflexion-lite: execution-feedback retries;
- reflexion+trace: execution-feedback plus compressed-trace retries.

## Data flow

```text
                         +---------------- execution feedback ----------------+
                         |                                                    |
task -> generator -> Python candidate -> PythonExecutor -> pass? ------------+
                         |
                         +-> ProgramTranslator -> WasmCompiler
                             -> TransformerVMRunner -> raw trace artifact
                             -> TraceCompressor -> trace feedback
                                                  |
                                                  +-> next prompt
```

The trace branch is invoked only after a failed Python attempt.

## Recovery strategy

1. Inventory notebook cells, local paths, commands, and embedded artifacts.
2. Identify the smallest five-task path that previously produced results.
3. Write characterization tests and fixtures for each stage.
4. Extract historical/manual adapters without changing outputs.
5. Add automated adapters behind the same interfaces.
6. Compare artifacts and feedback before replacing historical stages.

## Dependency rules
- Core schemas and protocols must not import Torch, Transformers, or Transformer-VM.
- Heavy dependencies belong in adapters.
- Raw traces are artifacts, not inline result fields.
- Every stage records provenance and failure status.
- Test doubles must be explicitly marked and cannot be reported as real experiments.
- Generated code and compiler/VM processes must be resource-bounded.
