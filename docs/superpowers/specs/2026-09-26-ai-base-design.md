# AI Base Architecture — Design Spec

Date: 2026-09-26

## Goal
Create a private global AI knowledge/operations repository `guns96x/ai-base` that all agents consult before repeating research or inventing a workflow. Each project keeps its own project-specific knowledge and instructions.

## Core rule
Agents MUST NOT read the whole base.

For each task:
1. Read global `AGENTS.md` only.
2. Identify task keywords, tool, machine and project.
3. Search `ai-base` for matching tags/aliases/content.
4. Read only relevant hits.
5. If a project is involved, read that project's local entrypoint and search its local knowledge.
6. Only then research externally or invent a new workflow.
7. Persist reusable discoveries in the correct layer.

## Layers

### Global: guns96x/ai-base
Stores only reusable cross-project knowledge:
- tool usage
- machine/environment facts
- workflows/playbooks
- known failures and fixes
- agent interaction rules
- project registry and entrypoints
- reusable research methods

Must never store passwords, tokens, cookies, recovery keys or private credentials.

### Project-local
Each project remains authoritative for its own facts, decisions, current state and evidence.

Existing files remain valid:
- `golf5-ecu-system/AGENTS.md`
- `golf5-ecu-system/AI_ENTRYPOINT.md`
- `golf5-ecu-system/CLAUDE.md`
- `vcds-android/AI_CONTEXT.md`

Global instructions point to these files instead of duplicating their contents.

## Scalable discovery
Do not use one ever-growing monolithic index.

Use:
- `AGENTS.md` — tiny mandatory protocol
- `index/manifest.json` — small list of index shards/categories
- `index/*.jsonl` — searchable metadata shards
- Markdown knowledge files with a short metadata header: id, title, tags, aliases, scope, updated, source

Primary discovery method is repository/code search over tags, aliases and text. Index shards are hints, not material that must be fully loaded.

## Precedence
1. Current user request
2. Project-local current-state/ground-truth files
3. Global ai-base operational knowledge
4. Historical notes
5. External research

When records conflict, do not silently merge them. Prefer the more specific/newer authoritative record and mark the older record superseded.

## Write-back
Reusable across projects -> `ai-base`.
Specific to one project -> that project.
Temporary investigation -> project draft/research area, not global.
Failed method worth remembering -> global or project `lessons/failed-*.md`.

Every durable new record must have tags/aliases so future search can find it.

## Initial ai-base structure
```
AGENTS.md
README.md
index/
  manifest.json
  tools.jsonl
  workflows.jsonl
  machines.jsonl
  projects.jsonl
  lessons.jsonl
tools/
workflows/
machines/
lessons/
standards/
projects/
```

## Project integration
Projects receive or update a very small entrypoint that says:
- consult `guns96x/ai-base` first for reusable operational knowledge
- search, do not bulk-read
- then follow this project's own canonical entrypoint
- project-local facts override global generic notes

Do not overwrite existing project instructions; patch them minimally.

## Validation
Implementation is accepted only if:
- global bootstrap is short
- a test task can find a known tool workflow without reading unrelated files
- a project task routes to both ai-base and the correct project entrypoint
- conflicting/superseded knowledge has a defined resolution path
- no secrets are committed
- existing project agent instructions remain functional
- indexes can be regenerated automatically from metadata
