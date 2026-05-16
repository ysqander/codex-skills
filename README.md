# Codex Skills

Reusable Codex skills for Alex Adamov's local and remote Codex instances.

## Skills

- `project-coordination-docs`: scaffolds canonical docs, coordination docs, workstream files, and an `AGENTS.md` block for multi-agent project work.

## Install

Install the coordination-docs skill on another machine with:

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo ysqander/codex-skills \
  --path skills/project-coordination-docs \
  --method git
```

Then restart Codex so the new skill is discovered.

## Update An Existing Install

The installer aborts if the destination skill already exists. To update manually:

```bash
rm -rf ~/.codex/skills/project-coordination-docs
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo ysqander/codex-skills \
  --path skills/project-coordination-docs \
  --method git
```

## Use

In a Codex session:

```text
Use $project-coordination-docs to scaffold coordination docs for this project.
```

Or run the scaffold directly from a repository root:

```bash
python3 ~/.codex/skills/project-coordination-docs/scripts/scaffold_coordination_docs.py \
  --project-name "Project Name" \
  --docs-dir docs/project-name
```
