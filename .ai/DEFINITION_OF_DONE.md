# Definition of Done

The repository is complete only when all mandatory checks below are satisfied.

## Product
- `baseline`, `reflexion-lite`, and `reflexion+trace` execute through the same CLI.
- `reflexion+trace` uses real semantic trace feedback, not a stub or fabricated data.
- The selected HumanEval subsets are configurable and reproducible.
- Results contain task id, method, attempt, generated code, execution result, reflection, trace payload or reference, timing, model configuration, and seed.

## Correctness
- Unit tests cover task selection, code extraction, result serialization, retry behavior, timeout behavior, and metrics.
- Integration tests cover baseline and reflexion-lite without downloading a large model by using a deterministic fake generator.
- Trace integration has contract tests and at least one end-to-end fixture.
- Existing tests are never weakened merely to obtain a passing build.

## Reproducibility
- Dependencies are declared and installable in a clean environment.
- Random seeds and model generation settings are persisted.
- A smoke experiment can be reproduced from README commands.
- Benchmark outputs are saved as machine-readable JSONL/JSON plus a summary table.

## Quality
- Ruff formatting and linting pass.
- Pyright or mypy passes for maintained modules.
- Pytest passes.
- Public functions have useful type annotations and docstrings where behavior is non-obvious.

## Safety
- Generated code executes in an isolated subprocess/container with time and resource limits.
- No secrets are written to logs or results.
- CI does not execute untrusted generated code with broad repository or network permissions.

## Documentation
- README contains installation, quick start, methods, result format, architecture, limitations, and reproduction instructions.
- `.ai/PRODUCT_SPEC.md` contains no unresolved product decisions marked `BLOCKING`.
- `.ai/ARCHITECTURE.md` matches the implemented system.

## Release gate
A final clean-clone audit must install dependencies, run quality checks, run tests, and execute the smoke benchmark successfully. Full GPU benchmarks may remain manual but their command and expected artifacts must be documented.
