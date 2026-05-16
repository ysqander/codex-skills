#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent


AGENTS_START = "<!-- codex-coordination-docs:start -->"
AGENTS_END = "<!-- codex-coordination-docs:end -->"


@dataclass(frozen=True)
class WriteResult:
    action: str
    path: Path


@dataclass(frozen=True)
class Workstream:
    id: str
    title: str
    slug: str
    branch: str
    owner: str
    date: str


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug or "project"


def title_from_slug(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.split("-") if part)


def resolve_under_root(root: Path, raw_path: str) -> Path:
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def rel_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def current_branch(root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError:
        return "create branch"

    branch = result.stdout.strip()
    return branch or "create branch"


def clean_block(text: str) -> str:
    return dedent(text).strip() + "\n"


def write_file(path: Path, content: str, *, force: bool, dry_run: bool, results: list[WriteResult]) -> None:
    content = clean_block(content)
    if path.exists() and not force:
        results.append(WriteResult("skipped", path))
        return

    action = "overwrote" if path.exists() else "created"
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    results.append(WriteResult(action, path))


def write_empty_file(path: Path, *, force: bool, dry_run: bool, results: list[WriteResult]) -> None:
    if path.exists() and not force:
        results.append(WriteResult("skipped", path))
        return

    action = "overwrote" if path.exists() else "created"
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    results.append(WriteResult(action, path))


def update_agents(path: Path, block: str, *, dry_run: bool, results: list[WriteResult]) -> None:
    block = clean_block(block)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if AGENTS_START in existing and AGENTS_END in existing:
        pattern = re.compile(
            re.escape(AGENTS_START) + r".*?" + re.escape(AGENTS_END),
            re.DOTALL,
        )
        updated = pattern.sub(block.strip(), existing)
        action = "updated"
    elif existing.strip():
        updated = existing.rstrip() + "\n\n" + block
        action = "updated"
    else:
        updated = "# Repository Guidelines\n\n" + block
        action = "created"

    if updated == existing:
        results.append(WriteResult("skipped", path))
        return

    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(updated, encoding="utf-8")
    results.append(WriteResult(action, path))


def readme_template(project_name: str) -> str:
    return f"""
    # {project_name} Docs

    This folder separates stable project facts from active coordination work.

    Use canonical docs for settled project direction and implemented behavior. Use coordination and workstream docs for active or messy work that may still change.

    ## Canonical Docs

    - [PROJECT_BRIEF.md](./PROJECT_BRIEF.md): product purpose, audience, boundaries, and success criteria.
    - [ARCHITECTURE.md](./ARCHITECTURE.md): implemented architecture, core flows, dependencies, and extension points.
    - [DATA_MODEL.md](./DATA_MODEL.md): persistent state, API shapes, events, storage, and shared contracts.
    - [EVALS.md](./EVALS.md): verification posture, commands, fixtures, and gaps.
    - [DECISIONS.md](./DECISIONS.md): append-only decision log.

    ## Dynamic Docs

    - [HANDOFF.md](./HANDOFF.md): latest manager-level project snapshot.
    - [TODO.md](./TODO.md): active backlog, follow-ups, and quality gates.
    - [coordination/WORKSTREAMS.md](./coordination/WORKSTREAMS.md): live dashboard of active branches and ownership.
    - [coordination/INTERFACES.md](./coordination/INTERFACES.md): shared contracts that parallel workers must coordinate around.
    - [coordination/BLOCKERS.md](./coordination/BLOCKERS.md): current blockers and sequencing constraints.
    - [coordination/CLOUD_WORKER_PROMPTS.md](./coordination/CLOUD_WORKER_PROMPTS.md): copy-ready prompts for parallel Codex workers.
    - [workstreams/](./workstreams/): one active workstream brief per non-trivial branch.

    ## Rule

    Do not put speculative work in canonical docs as if it already exists. Put proposals, partial branch state, blockers, and unresolved questions in `coordination/` or `workstreams/`.
    """


def project_brief_template(project_name: str, purpose: str) -> str:
    purpose_line = purpose or "[TODO: Describe what this project exists to do in one or two concrete sentences.]"
    return f"""
    # Project Brief

    ## Purpose

    {purpose_line}

    ## Audience

    [TODO: Name the primary users, buyers, operators, reviewers, or maintainers.]

    ## Product / System Boundary

    [TODO: State what is in scope today and what should not be implied yet.]

    ## Current Operating Model

    [TODO: Describe how {project_name} currently works from a user's or operator's perspective.]

    ## Non-Goals

    - [TODO: Add boundaries that future Codex instances must not accidentally cross.]

    ## Success Criteria

    - [TODO: Add observable outcomes that mean the project is working.]
    """


def architecture_template(project_name: str) -> str:
    return f"""
    # Architecture

    ## Current Implementation

    [TODO: Summarize the implemented architecture of {project_name}. Keep proposals in workstream docs until implemented or decided.]

    ## Core Flows

    - [TODO: Describe the main user, data, job, or agent flow.]

    ## Data And State Ownership

    [TODO: Identify source-of-truth storage, caches, derived state, background jobs, and cleanup rules.]

    ## External Dependencies

    - [TODO: List model providers, APIs, data stores, queues, SaaS services, and local tools.]

    ## Extension Points

    [TODO: Describe where future work should plug in without breaking existing behavior.]

    ## Known Constraints

    - [TODO: Note latency, cost, security, privacy, scale, migration, or compatibility constraints.]
    """


def data_model_template() -> str:
    return """
    # Data Model

    Track stable domain concepts, persistence contracts, API shapes, event payloads, and unsafe changes here.

    ## Core Concepts

    | Concept | Purpose | Owner | Status | Notes |
    | --- | --- | --- | --- | --- |
    | [TODO] | [TODO] | [TODO] | proposed | [TODO] |

    ## Persistent State

    [TODO: Describe durable state, storage paths/tables/collections, retention rules, and migration concerns.]

    ## API / Event Shapes

    [TODO: Document request/response/event payloads that multiple workstreams may touch.]

    ## Unsafe Changes

    - [TODO: List changes that require coordination before implementation.]
    """


def evals_template() -> str:
    return """
    # Evals

    Track verification posture, local commands, fixtures, expected artifacts, and known gaps here.

    ## Current Gates

    | Gate | Command | Owner | Status | Notes |
    | --- | --- | --- | --- | --- |
    | [TODO] | `[TODO]` | [TODO] | planned | [TODO] |

    ## Fixtures And Data

    [TODO: List test fixtures, datasets, sample inputs, generated outputs, and ignored local paths.]

    ## Acceptance Evidence

    [TODO: Record the evidence expected before work is considered ready.]

    ## Known Gaps

    - [TODO: Add gaps that must not be marketed or treated as solved.]
    """


def decisions_template(today: str) -> str:
    return f"""
    # Decisions

    Append decisions here when direction changes or a recurring question is settled.

    ## {today}: Coordination Docs Created

    This project now separates stable canonical docs from dynamic coordination docs. Canonical docs should contain settled facts and implemented behavior. Active plans, branch state, blockers, and unresolved questions belong in `coordination/` or `workstreams/`.
    """


def handoff_template(project_name: str, branch: str) -> str:
    return f"""
    # Handoff

    ## Current Branch

    - `{branch}`

    ## Current State

    - [TODO: Summarize the latest implemented state of {project_name}.]

    ## Next Recommended Sequence

    1. [TODO: Add the next concrete step.]
    2. [TODO: Add verification or review step.]

    ## Latest Verification

    - [TODO: Add commands run, dates, and pass/fail status.]

    ## Handoff Log

    | Date | Owner | Update |
    | --- | --- | --- |
    | [TODO] | [TODO] | [TODO] |
    """


def todo_template() -> str:
    return """
    # TODO

    ## Active

    - [TODO: Add active follow-ups.]

    ## Later

    - [TODO: Add deferred work.]

    ## Product / Quality Gates

    - [TODO: Add gates that must pass before expanding scope or claiming a capability.]
    """


def workstreams_template(workstream: Workstream | None) -> str:
    initial_row = ""
    if workstream:
        initial_row = (
            f"| {workstream.id} | active | {workstream.owner} | `{workstream.branch}` | "
            f"{workstream.title} | [TODO] | [TODO] | created with scaffold |"
        )

    return f"""
    # Workstreams

    This is the live dashboard for active project work. Keep it short and current.

    | ID | Status | Owner | Branch | Scope | Touches | Depends On | Notes |
    | --- | --- | --- | --- | --- | --- | --- | --- |
    {initial_row}

    ## Coordination Rules

    - New workers should branch from the latest coordination branch unless explicitly continuing an existing PR.
    - Shared contracts belong in [INTERFACES.md](./INTERFACES.md).
    - Blockers belong in [BLOCKERS.md](./BLOCKERS.md).
    - When a workstream completes, update this table and add a handoff entry in the workstream file.
    """


def interfaces_template() -> str:
    return """
    # Interfaces

    Track shared contracts that multiple workstreams might touch. Update this before or alongside contract-changing code.

    ## How To Use

    Add an entry when a workstream changes shared schemas, API responses, artifact payloads, persistence events, source/retrieval contracts, memory contracts, background job states, or other cross-worker boundaries.

    ## Pending Shared Contracts

    | Contract | Status | Owner | Consumers | Notes |
    | --- | --- | --- | --- | --- |
    | [TODO] | proposed | [TODO] | [TODO] | [TODO] |

    ## Contract Template

    ### ContractName

    Status: proposed / implemented / deprecated

    Owner:

    - [TODO]

    Current shape:

    - [TODO]

    Consumers:

    - [TODO]

    Unsafe changes:

    - [TODO]
    """


def blockers_template() -> str:
    return """
    # Blockers

    Track blockers and sequencing constraints here. Keep resolved blockers for historical context when they explain why branches were paused, closed, or superseded.

    ## Open

    | Blocker | Status | Owner | Affected Workstreams | Next Action |
    | --- | --- | --- | --- | --- |
    | [TODO] | open | [TODO] | [TODO] | [TODO] |

    ## Resolved

    | Blocker | Resolution | Date | Notes |
    | --- | --- | --- | --- |
    | [TODO] | [TODO] | [TODO] | [TODO] |
    """


def cloud_worker_prompts_template(project_name: str, docs_rel: str) -> str:
    return f"""
    # Cloud Worker Prompts

    Use these prompts when starting parallel Codex workers. Workers must update their workstream file and coordination docs before finishing.

    ## Starting Prompt Template

    ```text
    You are working on {project_name}. Before editing, read:

    - {docs_rel}/README.md
    - {docs_rel}/coordination/WORKSTREAMS.md
    - the relevant {docs_rel}/workstreams/*.md file
    - {docs_rel}/coordination/INTERFACES.md
    - relevant canonical docs under {docs_rel}/

    Create or update a workstream file before substantial code changes. If you change shared schemas, API responses, artifact payloads, persistence events, source/retrieval contracts, memory contracts, or job states, update {docs_rel}/coordination/INTERFACES.md before or alongside code.

    Before finishing, update the workstream status and handoff log, {docs_rel}/HANDOFF.md, {docs_rel}/TODO.md, and {docs_rel}/DECISIONS.md if a durable decision was made.
    ```
    """


def workstream_template(workstream: Workstream) -> str:
    return f"""
    # {workstream.id}

    ## Objective

    [TODO: State the concrete outcome for {workstream.title}.]

    ## Status

    active

    ## Branch

    - `{workstream.branch}`

    ## Scope

    - [TODO: Add included work.]

    ## Non-Goals

    - [TODO: Add explicit boundaries.]

    ## Expected Files

    - [TODO: List docs, source files, tests, migrations, or generated artifacts likely to change.]

    ## Interfaces Affected

    - [TODO: Name shared contracts or write none.]

    ## Acceptance Evidence

    - [TODO: Add checks, screenshots, evals, tests, or review packets required before merge.]

    ## Handoff Log

    | Date | Owner | Update |
    | --- | --- | --- |
    | {workstream.date} | {workstream.owner} | Workstream created. |
    """


def agents_block(project_name: str, docs_rel: str) -> str:
    return f"""
    {AGENTS_START}
    ## Project Coordination Docs

    This project uses coordination docs for parallel Codex work under `{docs_rel}`.

    Before starting non-trivial work, read:

    1. `{docs_rel}/README.md`
    2. `{docs_rel}/coordination/WORKSTREAMS.md`
    3. the relevant `{docs_rel}/workstreams/*.md` file
    4. `{docs_rel}/coordination/INTERFACES.md`
    5. relevant canonical docs such as `PROJECT_BRIEF.md`, `ARCHITECTURE.md`, `DATA_MODEL.md`, or `EVALS.md`

    When starting a substantial feature or refactor:

    - create a workstream file under `{docs_rel}/workstreams/` using `WS-YYYY-MM-DD-short-name.md`
    - add one row to `{docs_rel}/coordination/WORKSTREAMS.md`
    - list expected files and shared interfaces before editing code
    - if changing shared schemas, API responses, artifact payloads, persistence events, retrieval/source contracts, memory contracts, or job states, update `{docs_rel}/coordination/INTERFACES.md` before or alongside code changes

    When finishing or pausing work:

    - update the workstream status and handoff log
    - update `{docs_rel}/HANDOFF.md`
    - update durable follow-ups in `{docs_rel}/TODO.md`
    - record important decisions in `{docs_rel}/DECISIONS.md`

    Do not put speculative WIP into canonical docs as if it already exists. Use workstream and coordination docs for proposals, partial implementation notes, branch state, blockers, and unresolved questions.
    {AGENTS_END}
    """


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scaffold Codex coordination docs for a project.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--project-name", help="Human-readable project name. Defaults to root folder name.")
    parser.add_argument("--purpose", default="", help="Optional one-sentence purpose for PROJECT_BRIEF.md.")
    parser.add_argument("--docs-dir", help="Docs directory to create. Defaults to docs/<project-slug>.")
    parser.add_argument("--agents", default="AGENTS.md", help="AGENTS.md path relative to root.")
    parser.add_argument("--no-agents", action="store_true", help="Do not create or update AGENTS.md.")
    parser.add_argument("--start-workstream", help="Create an initial workstream with this short name.")
    parser.add_argument("--owner", default="Codex", help="Owner label for the initial workstream.")
    parser.add_argument("--branch", help="Branch for handoff/workstream docs. Defaults to current git branch.")
    parser.add_argument("--date", help="ISO date for generated workstream/decision entries. Defaults to today.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing generated doc files.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned writes without changing files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    project_slug = slugify(args.project_name or root.name)
    project_name = args.project_name or title_from_slug(project_slug)
    docs_dir = resolve_under_root(root, args.docs_dir or f"docs/{project_slug}")
    docs_rel = rel_path(root, docs_dir)
    branch = args.branch or current_branch(root)
    today = args.date or dt.date.today().isoformat()
    results: list[WriteResult] = []

    workstream = None
    if args.start_workstream:
        workstream_slug = slugify(args.start_workstream)
        workstream = Workstream(
            id=f"WS-{today}-{workstream_slug}",
            title=args.start_workstream,
            slug=workstream_slug,
            branch=branch,
            owner=args.owner,
            date=today,
        )

    files = {
        docs_dir / "README.md": readme_template(project_name),
        docs_dir / "PROJECT_BRIEF.md": project_brief_template(project_name, args.purpose),
        docs_dir / "ARCHITECTURE.md": architecture_template(project_name),
        docs_dir / "DATA_MODEL.md": data_model_template(),
        docs_dir / "EVALS.md": evals_template(),
        docs_dir / "DECISIONS.md": decisions_template(today),
        docs_dir / "HANDOFF.md": handoff_template(project_name, branch),
        docs_dir / "TODO.md": todo_template(),
        docs_dir / "coordination" / "WORKSTREAMS.md": workstreams_template(workstream),
        docs_dir / "coordination" / "INTERFACES.md": interfaces_template(),
        docs_dir / "coordination" / "BLOCKERS.md": blockers_template(),
        docs_dir / "coordination" / "CLOUD_WORKER_PROMPTS.md": cloud_worker_prompts_template(project_name, docs_rel),
    }

    for path, content in files.items():
        write_file(path, content, force=args.force, dry_run=args.dry_run, results=results)

    if workstream:
        path = docs_dir / "workstreams" / f"{workstream.id}.md"
        write_file(path, workstream_template(workstream), force=args.force, dry_run=args.dry_run, results=results)
    else:
        write_empty_file(docs_dir / "workstreams" / ".gitkeep", force=args.force, dry_run=args.dry_run, results=results)

    if not args.no_agents:
        agents_path = resolve_under_root(root, args.agents)
        update_agents(agents_path, agents_block(project_name, docs_rel), dry_run=args.dry_run, results=results)

    prefix = "would " if args.dry_run else ""
    for result in results:
        print(f"{prefix}{result.action}: {rel_path(root, result.path)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
