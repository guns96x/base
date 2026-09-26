# Global AI Base Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `guns96x/ai-base` as a global searchable operational knowledge layer and connect existing/new projects to it without duplicating project knowledge.

**Architecture:** `ai-base` stores cross-project workflows, tools, machines, lessons and a registry of project entrypoints. Each project keeps its own knowledge base and current-state files. Agents search first and read only relevant hits.

**Tech Stack:** GitHub Markdown, JSONL metadata shards, GitHub code search, optional Python index generator.

**Spec:** `guns96x/base/docs/superpowers/specs/2026-09-26-ai-base-design.md`

## Global Constraints
- Do not bulk-read the knowledge base.
- Project-local facts override global generic notes.
- Never store secrets, tokens, cookies, passwords or recovery keys.
- Existing project instructions must remain functional.
- Every new project gets its own knowledge layer plus a small pointer to `ai-base`.

## Review Focus
- Search miss must fall back to project-local search before web research.
- Conflicting records must preserve provenance and supersession.
- New projects must be registrable without editing a giant file.
- Missing/unavailable `ai-base` must not block project-local work.
- Index generation must not ingest secret files.

---

### Task 1: Create private `guns96x/ai-base`
**Files:** create `AGENTS.md`, `README.md`, `index/manifest.json`, shard files, base directories.

- [ ] Create repository as private.
- [ ] Add minimal mandatory bootstrap in `AGENTS.md`.
- [ ] Add search-first routing rules and precedence.
- [ ] Verify repository can be searched without reading all files.
- [ ] Commit.

### Task 2: Add metadata/index generator
**Files:** create `scripts/reindex.py`, metadata headers in knowledge files.

- [ ] Define metadata fields: id, title, tags, aliases, scope, updated, source, supersedes.
- [ ] Generate JSONL shards by category.
- [ ] Exclude secret/config patterns.
- [ ] Run generator and validate deterministic output.
- [ ] Commit.

### Task 3: Seed global operational knowledge
**Files:** `tools/`, `machines/`, `workflows/`, `lessons/`, `projects/`.

- [ ] Add known Remote Desktop Commander workflow.
- [ ] Add ASUS / Antigravity / AGY paths and non-secret usage.
- [ ] Add GitHub workflow.
- [ ] Add delegation/research playbooks.
- [ ] Register existing project entrypoints.
- [ ] Reindex and commit.

### Task 4: Integrate existing projects minimally
**Files:** existing entrypoints only.

- [ ] Patch `golf5-ecu-system/AGENTS.md` with global search-first pointer.
- [ ] Patch `vcds-android` entrypoint with global search-first pointer.
- [ ] Add small entrypoint to `desktop-commander-fast` if absent.
- [ ] Do not copy project knowledge into `ai-base`.
- [ ] Verify each project routes global -> local.
- [ ] Commit per repository.

### Task 5: New-project standard
**Files:** `standards/new-project.md`, template entrypoint, project registry workflow.

- [ ] Define mandatory local structure for new projects.
- [ ] Define how a new project registers its entrypoint in `ai-base`.
- [ ] Define local knowledge/search/write-back rules.
- [ ] Add template that agents can copy into a new repository.
- [ ] Reindex and commit.

### Task 6: End-to-end validation
- [ ] Test a global tool question resolves only relevant global files.
- [ ] Test an ECU task routes to `golf5-ecu-system` local knowledge.
- [ ] Test a VCDS task routes to `vcds-android`.
- [ ] Test unknown topic falls through to external research.
- [ ] Test superseded record handling.
- [ ] Check no secret-like material is tracked.
- [ ] Document final validation result.
