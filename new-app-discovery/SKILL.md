---
name: new-app-discovery
description: "Use this skill whenever the user wants Codex to investigate, automate, integrate with, reverse-engineer, or safely test a new local desktop app, document-based app, macOS app, GUI workflow, or app file format. Trigger aggressively before writing scripts or making assumptions about an unfamiliar app: first discover the UI, storage model, file/package format, safe write paths, round-trip behavior, and automation limits."
---

# New App Discovery

Use this workflow to learn how an unfamiliar local app behaves before building tooling around it. The goal is an evidence-backed capability report: what Codex can safely read, write, automate, validate, and where it must stop.

This is app-agnostic. Scrivener is a useful example of the pattern: orient with Computer Use, perform safe UI actions, inspect local project/package files, verify UI writes from disk, then test closed-copy round-trips from disk back into the app.

## Core Rule

Do not start by editing app files. Start by observing the app, identifying its storage model, and creating disposable copies for tests.

## When To Use

Use when:

- The user names a local app that has not been mapped yet.
- The user wants automation for a GUI app.
- The app stores work in local files, bundles, databases, packages, or project folders.
- The user asks whether Codex can safely manipulate app data outside the app.
- A prior workflow worked for one app and needs to be generalized to another.

Do not use when:

- The task is a normal codebase inspection with no GUI app or app-owned document format.
- Official API documentation already covers the operation and the user only needs API usage.
- The user asks for a one-off UI action and no discovery is needed.

## Safety Rules

- Work on copies until the write path is proven safe.
- Never modify the user's original app document/package during discovery unless explicitly authorized.
- Prefer reversible UI actions: create a scratch document, type harmless marker text, toggle non-destructive preferences only if needed.
- Before editing on disk, close the app document or use a copied project. Do not write into a live package unless the format explicitly supports it and the user accepts the risk.
- Do not delete, overwrite, compact, repair, migrate, sync, publish, export, send, or share through the app without confirmation.
- Treat cloud-synced app folders as asynchronous. Verify file presence twice before assuming something is missing.
- If the app uses a binary database, proprietary package, or sync engine, assume direct writes are unsafe until round-trip tested on a copy.
- Keep credentials, private account data, and license keys out of reports.
- Capture enough evidence to repeat the result: paths, commands, app version, document type, UI route, and validation outcome.

## Required Tools

- Use Computer Use when the task involves a local GUI app. Start with app state/orientation before acting.
- Use shell commands for file inspection: `file`, `find`, `rg`, `plutil`, `sqlite3`, `jq`, `strings`, `mdls`, `ls -la`, checksums, and timestamps as appropriate.
- Use app-specific CLIs or official docs only after discovering whether they exist.
- Use web or current docs if app behavior, file format, or automation support is uncertain or version-sensitive.

## Workflow Phases

### 1. Frame The Discovery

Establish:

- App name and version if available.
- User goal: read, write, export, automate UI, sync, convert, inspect, or validate.
- Document/project location.
- Whether the user permits creating a scratch file and working copy.
- Risk tolerance: read-only, copy-write, or original-write after proof.

Ask before proceeding if you do not know which file/document is safe to use.

### 2. Orient In The UI

Use Computer Use to inspect the app:

- Confirm the active app and document.
- Identify visible document title, sidebar structure, editor areas, save state, and available export/import surfaces.
- Determine whether the UI exposes automation-friendly controls.
- Perform only safe UI actions unless authorized.

Record observations as evidence, not assumptions.

### 3. Create Or Identify A Test Artifact

Prefer a disposable scratch document created by the app. If the user provides a real file, create a closed copy:

- Copy the whole package/folder/file, preserving structure and metadata.
- Work only in the copy.
- Record original and copy paths.
- If cloud sync is involved, wait for files to settle and verify with `ls` or checksums.

### 4. Inspect The Storage Model

Determine what the app actually stores:

- Single file, directory, macOS package, SQLite database, plist, JSON, XML, Markdown, RTF, binary blobs, media assets, index/cache files, or hybrid.
- Which files change after UI edits.
- Whether identifiers link UI objects to disk files.
- Which files are source-of-truth versus cache/index/export.
- Whether content is encoded, compressed, encrypted, or database-backed.

Useful inspection sequence:

```bash
find "$TARGET" -maxdepth 4 -type f | sort
file "$TARGET"
mdls "$TARGET"
rg -n "DISCOVERY_MARKER|known text from UI" "$TARGET"
find "$TARGET" -type f -print0 | xargs -0 ls -lt
```

Adapt commands to the target. For huge folders, limit depth and scope.

### 5. Verify UI To Disk

Prove that UI actions map to disk changes:

1. Create a unique marker string in the app, such as `DISCOVERY_MARKER_2026_05_14_001`.
2. Save using the app's normal mechanism.
3. Close or defocus if needed to flush writes.
4. Search the artifact on disk for the marker.
5. Identify every changed file and timestamp.
6. Reopen the app and confirm the marker appears in the UI.

If the marker is not found, check for compression, database storage, autosave delay, external caches, or cloud sync delay.

### 6. Verify Disk To UI On A Closed Copy

Only after UI-to-disk is understood:

1. Close the copied document in the app.
2. Back up the copied artifact or make a second copy.
3. Edit the smallest plausible source file on disk.
4. Reopen the copy in the app.
5. Confirm the UI reflects the disk edit.
6. Confirm the app does not repair, discard, duplicate, or corrupt the edit.

Do not count this as successful unless the app reads the changed content from disk after a fresh open.

### 7. Test Round-Trip Integrity

A closed-copy round trip proves whether automation can safely participate:

- UI write -> disk inspection -> disk write -> app reopen -> UI confirmation -> app save -> disk inspection again.
- Compare relevant files before and after the final app save.
- Confirm the app preserves the automation edit rather than normalizing it away.
- Note whether indexes/caches regenerate automatically.

For structured files, validate syntax before reopening:

- JSON: `jq . file.json`
- XML/plist: `plutil -lint file.plist` or XML parser
- SQLite: `.schema`, `PRAGMA integrity_check;`
- Markdown/text: encoding and line endings

### 8. Identify Automation Paths

Map each possible path:

- UI automation with Computer Use.
- Scripted file manipulation.
- Native scripting, AppleScript, Shortcuts, CLI, plug-in API, URL scheme, or official SDK.
- Export/import route.
- Database route.
- Unsupported/manual-only route.

Score each path for safety, repeatability, speed, and validation strength.

### 9. Produce Capability Report

Use the report format in `references/capability-report-template.md` when the user wants an artifact or when discovery findings will be reused.

Use `references/computer-use-field-guide-for-authors.md` when the user wants a human-facing explanation, lesson handout, or FFA-style teaching artifact about how authors can safely test AI agents against writing apps.

The report must include:

- App/version and tested document type.
- Read capabilities.
- Write capabilities.
- UI automation capabilities.
- File/package map.
- Validated round trips.
- Known unsafe operations.
- Failure modes.
- Recommended next workflow.

## Capability Matrix

Use this table in chat or reports:

| Capability | Status | Evidence | Validation | Risk | Next Step |
| --- | --- | --- | --- | --- | --- |
| Read UI state | Proven / Likely / Unknown / Unsafe | UI observations | Repeated orientation | Low/Med/High | |
| Read files | Proven / Likely / Unknown / Unsafe | Paths + commands | Marker search/parser | Low/Med/High | |
| Write via UI | Proven / Likely / Unknown / Unsafe | Safe UI action | Reopen + inspect disk | Low/Med/High | |
| Write via disk | Proven / Likely / Unknown / Unsafe | Edited copy | Fresh reopen + save | Low/Med/High | |
| Export/import | Proven / Likely / Unknown / Unsafe | Menu/CLI/docs | File comparison | Low/Med/High | |
| Batch automation | Proven / Likely / Unknown / Unsafe | Repeatable steps | Multi-item test | Low/Med/High | |

Status definitions:

- Proven: tested end-to-end on a copy.
- Likely: observed but not round-trip tested.
- Unknown: no evidence yet.
- Unsafe: evidence of corruption, data loss, live-write risk, sync conflict, or unvalidated proprietary behavior.

## Validation Checklist

Before claiming write support:

- The test ran on a copy or scratch artifact.
- The app was closed or safely flushed before disk edits.
- A unique marker was created.
- Disk search or parser found the expected change.
- The app reopened and displayed the disk edit.
- The app saved again without discarding the edit.
- The artifact passed format-specific validation.
- The result can be repeated with documented steps.

Before claiming batch support:

- Test at least two separate items.
- Confirm identifiers are stable and not position-only.
- Confirm ordering, metadata, and links survive.
- Confirm caches/indexes regenerate or can be updated safely.

## Failure Modes To Watch

- App autosaves later than expected.
- Cloud sync hides or delays file changes.
- UI content is stored in compressed or encoded blobs.
- Disk files are caches, not source-of-truth.
- App rewrites IDs or checksums after reopen.
- Direct disk edits appear once but are removed on next save.
- Binary databases require coordinated index updates.
- App keeps document state in memory and overwrites disk edits when closing.
- Multiple files must change together.
- Package contains absolute paths, bookmarks, or machine-local metadata.
- UI automation is brittle because labels, focus, or accessibility nodes shift.
- The app performs migration/repair on open.
- File locking or sandbox permissions prevent reliable writes.

## When To Stop And Ask

Stop and ask when:

- Only the user's real document is available and a write test is needed.
- The next step could overwrite, migrate, repair, compact, delete, publish, sync, or externally share data.
- You cannot tell which file is canonical.
- The app stores data in an encrypted/proprietary binary format and no safe API exists.
- The app is connected to external accounts or team/shared workspaces.
- The user goal requires destructive cleanup.
- The evidence conflicts: the UI and disk disagree after repeated checks.
- A copy behaves differently from the original because of licensing, cloud sync, paths, or package metadata.

When stopping, report:

- What is already proven.
- What remains unknown.
- The specific risk.
- The smallest safe next test.
- The exact approval needed.

## Output Standards

Keep reports practical. Avoid theory unless it changes the next action.

Good final discovery outputs include:

- "Safe to automate via disk on closed copies; original-write requires confirmation."
- "UI automation is viable for export, but direct file writes are unsafe."
- "Read-only indexing is proven; write-back needs an app-level import path."
- "The app package is a hybrid: text bodies are editable, indexes regenerate, binary metadata should not be touched."

## Minimal Discovery Loop

When time is short:

1. Orient in UI.
2. Create scratch/copy.
3. Add marker in UI.
4. Find marker on disk.
5. Edit marker on disk while closed.
6. Reopen and verify in UI.
7. Save and confirm persistence.
8. Report matrix with risks.
