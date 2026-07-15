# Claude Code Instructions

Read these files before changing code:
1. `AGENTS.md`
2. `.ai/PRODUCT_SPEC.md`
3. `.ai/DEFINITION_OF_DONE.md`
4. `.ai/ARCHITECTURE.md`
5. `.ai/PROJECT_STATE.md`

Use the relevant skill under `.claude/skills/` for every task. Work on one GitHub issue at a time and keep changes within its acceptance criteria.

## Mandatory loop

```text
inspect -> reproduce -> test -> implement -> verify -> review diff -> report
```

Never claim success from code inspection alone. Run the checks named by the issue. Do not fabricate Transformer-VM behavior or semantic traces. Do not delete or weaken tests to make CI pass. Do not push directly to `main` or merge a PR.

Stop and mark the task blocked after three materially similar failed repair attempts, when a required secret/external artifact is absent, or when a decision listed as BLOCKING in `.ai/PROJECT_STATE.md` is required.
