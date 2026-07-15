# Repository provenance

## Branch roles

### `source`

`source` is the immutable snapshot of the author's repository before the autonomous-agent engineering experiment.

- Snapshot commit: `9394f7526980fa6c4ee7334a30d892ff25ebe44c`
- Contents: the author's public starting implementation and README
- Purpose: permit exact comparison between the starting point and subsequent agent-produced work
- Policy: no new commits, merges, rebases, or force-pushes

### `main`

`main` is the primary public branch for the completed repository and the visible history of agent-assisted development.

All changes after the source snapshot should be attributable through one or more of:

- a GitHub issue with checkable acceptance criteria;
- an implementation branch and pull request into `main`;
- CI results;
- agent/harness logs that do not contain private artifacts or secrets;
- a commit message identifying the task and agent role.

## Attribution categories

Every implementation PR should state which category applies:

1. **Inherited** — behavior already present in `source` and preserved or tested.
2. **Recovered** — behavior reconstructed from private notebooks, paper, logs, or prior experiment artifacts.
3. **Agent-designed** — new architecture, tests, automation, or fixes created during the agent experiment.
4. **Owner-directed** — a product or scientific decision explicitly supplied by the repository owner.

A PR may contain more than one category, but the mapping should be explicit.

## Experiment start

The autonomous engineering experiment begins with the agent-readiness work introduced by PR #1. The branch used to prepare that PR is temporary; once merged, `main` becomes the integration target for all subsequent agent work.

## Comparison

To inspect all public automated work relative to the starting point:

```bash
git diff source...main
git log --oneline --decorate source..main
```

Private draft notebooks are intentionally excluded from both branches. Their role is documented in `.ai/PRIVATE_ARTIFACTS.md`.
