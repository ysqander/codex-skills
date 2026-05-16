---
name: project-coordination-docs
description: Create and maintain reusable Codex coordination documentation for multi-agent project work. Use when starting a new project, feature area, lab, or substantial refactor that needs canonical docs, dynamic handoff/TODO/decisions files, workstream tracking, shared interface contracts, blockers, cloud-worker prompts, and AGENTS.md instructions so multiple Codex instances can coordinate safely.
---

# Project Coordination Docs

## Overview

Use this skill to scaffold and maintain project-local coordination docs for parallel Codex work. The pattern separates stable project facts from active coordination state so separate Codex instances can share context without treating speculative WIP as canonical.

## Workflow

1. Inspect the repo first: read any existing `AGENTS.md`, `README.md`, `docs/`, and active planning files.
2. Choose a docs folder for the product, project, or lab area. Prefer `docs/<project-slug>` when the repo has multiple products, or `docs/project` for a single-purpose repo.
3. Run the scaffold script from the target repo root.
4. Review generated docs and replace TODOs with project-specific facts only when they are known.
5. For substantial implementation work, create a workstream file and add a row to `coordination/WORKSTREAMS.md` before editing code.
6. During and after work, keep `HANDOFF.md`, `TODO.md`, `DECISIONS.md`, and relevant workstream files current.

## Scaffold Command

Run from the repository root:

```bash
python3 ~/.codex/skills/project-coordination-docs/scripts/scaffold_coordination_docs.py \
  --project-name "Project Name" \
  --docs-dir docs/project-name \
  --agents AGENTS.md
```

Useful options:

```bash
--purpose "One sentence project purpose"
--start-workstream "short feature name"
--owner "Codex"
--branch "codex/example-branch"
--dry-run
--force
--no-agents
```

The script creates missing files and skips existing files unless `--force` is passed. It appends or updates a marked block in `AGENTS.md`; it does not rewrite unrelated AGENTS.md content.

## Document Model

Use canonical docs for settled facts and implemented behavior:

- `PROJECT_BRIEF.md`: purpose, audience, boundaries, and success criteria.
- `ARCHITECTURE.md`: implemented architecture, core flows, dependencies, and extension points.
- `DATA_MODEL.md`: persistent state, API shapes, event contracts, and unsafe changes.
- `EVALS.md`: verification posture, commands, fixtures, and gaps.
- `DECISIONS.md`: append-only decisions when direction changes or recurring questions are settled.

Use dynamic docs for active state:

- `HANDOFF.md`: latest manager-level snapshot and next recommended sequence.
- `TODO.md`: active follow-ups and quality gates.
- `coordination/WORKSTREAMS.md`: live dashboard of branches, owners, scope, dependencies, and status.
- `coordination/INTERFACES.md`: shared contracts that parallel workers must coordinate around.
- `coordination/BLOCKERS.md`: blockers, sequencing constraints, and resolved blockers.
- `coordination/CLOUD_WORKER_PROMPTS.md`: copy-ready prompts for other Codex/cloud workers.
- `workstreams/WS-YYYY-MM-DD-short-name.md`: one workstream brief per non-trivial branch.

## Coordination Rules

- Do not put speculative WIP into canonical docs as if it already exists.
- Put proposals, partial branch state, blockers, and unresolved questions in `coordination/` or `workstreams/`.
- Update `coordination/INTERFACES.md` before or alongside changes to shared schemas, API responses, artifact payloads, persistence events, retrieval contracts, memory contracts, or other cross-worker interfaces.
- Before starting non-trivial work, read the generated `README.md`, `coordination/WORKSTREAMS.md`, relevant workstream files, `coordination/INTERFACES.md`, and relevant canonical docs.
- When finishing or pausing work, update the workstream status and handoff log, then update `HANDOFF.md`, `TODO.md`, and `DECISIONS.md` as needed.
- Keep workstream files concrete: expected files, ownership boundaries, dependencies, acceptance evidence, and handoff notes.

## Existing Repos

If a repo already has planning docs, preserve them. Use the scaffold to create only missing coordination files, then adapt the generated docs to reference the existing canonical sources. Avoid duplicating a long architecture document if the repo already has one; link to it from the generated `README.md` and `AGENTS.md` block instead.
