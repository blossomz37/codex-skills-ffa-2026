---
name: scrivener-agent
description: Use this skill whenever the user wants Codex to inspect, automate, import into, export from, compile, verify, repair, round-trip, or directly edit a Scrivener project or `.scriv` package. Trigger for Scrivener UI work, Binder reads/writes, manuscript/document imports, compile/export tasks, label/status changes, Trash/restore operations, package-level UUID mapping, `.scrivx` inspection, `content.rtf`/`notes.rtf`/`synopsis.txt` reads, snapshots, and safe closed-package edits. Use it even if the user only mentions a `.scriv` folder, `.scrivx` file, Binder item, Scrivener compile, or Scrivener roundtrip.
---

# Scrivener Agent

Work with Scrivener by combining UI automation for live project changes with package-level reads for verification. The core rule is simple: when Scrivener has the project open, write through Scrivener; inspect the `.scriv` package to verify what happened.

Bundled fixture for examples and smoke tests:

```text
references/TEST_PROJECT.scriv
```

## Start Here

1. Identify the target `.scriv` package and whether it is open in Scrivener.
2. If the project is open, use Computer Use for Binder edits, document writes, imports, exports, compile, label/status, snapshots, and Trash actions.
3. Save or wait past Scrivener autosave.
4. Verify state from disk using `.scrivx`, `content.rtf`, `notes.rtf`, `synopsis.txt`, and snapshot files.
5. Use direct package edits only when the project is closed, preferably against a copied package first.
6. Report both the Scrivener-visible result and the disk-level verification.

## Safety Rules

- Do not directly edit an open `.scriv` package.
- Prefer Scrivener UI automation for writes whenever the project is open.
- Use package inspection freely for reads and verification.
- For direct package edits, close Scrivener first and work on a copied `.scriv` package unless the user explicitly accepts the risk.
- Validate `.scrivx` with `xmllint --noout`; it is XML, not an Apple plist.
- Wait for autosave or use `File > Save` before treating disk state as final.
- If the project lives in Google Drive or another sync folder, run verification twice when files look stale.
- Do not assume Binder titles are unique. Map by UUID.
- Do not generalize direct XML edits beyond operations already verified or tested on a disposable copy.

## Read References As Needed

- Binder/UI operations: `references/ui-workflows.md`
- Package layout, UUID mapping, and direct closed-package edits: `references/package-model.md`
- Verification commands and roundtrip harness notes: `references/verification.md`

## Open Project Workflow

Use this sequence when the project is open in Scrivener:

1. Use Computer Use `get_app_state` to orient to the visible Scrivener window.
2. Select the relevant Binder item or container.
3. Perform writes through the UI:
   - create or rename Binder documents/folders
   - edit body text, synopsis, and notes
   - import Markdown or RTF
   - export selected Binder documents
   - compile
   - set Label and Status
   - create or rename snapshots
   - move items, including moves to Scrivener Trash
4. Save through `File > Save` when possible, or wait for autosave.
5. Verify using disk reads, not just UI confidence.

For detailed UI patterns, read `references/ui-workflows.md`.

## Binder And UUID Model

Scrivener Binder state lives primarily in the project `.scrivx` file. Each Binder item has a UUID. Document body, notes, synopsis, and snapshots live in package subdirectories keyed by that UUID.

Important paths:

```text
Project.scriv/
|-- Project.scrivx
|-- Files/Data/<UUID>/content.rtf
|-- Files/Data/<UUID>/notes.rtf
|-- Files/Data/<UUID>/synopsis.txt
`-- Snapshots/<UUID>.snapshots/
```

Always map titles to UUIDs before reading or writing package files. Imported files can create duplicate Binder titles, so title-only lookups are unsafe.

For package layout details and direct edit rules, read `references/package-model.md`.

## Imports, Exports, And Compile

Use Scrivener UI for import, export, and compile:

- `File > Import > Files...` for Markdown and RTF imports.
- `File > Export > Files...` for selected Binder item export.
- `File > Compile...` for manuscript or scoped compile output.

Known behavior from verified testing:

- Markdown and RTF import as Binder text documents.
- Imported Binder titles may use the source basename, creating duplicate visible titles.
- Markdown headings may be preserved as literal text depending on the import route.
- Text document export defaults to RTF.
- Compile uses the current compile scope; test items outside the compile scope are not included.

## Labels, Statuses, Snapshots, And Trash

Label and Status changes should be made through the Inspector UI, then verified in `.scrivx`.

Observed project-specific mapping in the TEST_PROJECT test project:

```xml
<LabelID>11</LabelID>   <!-- Blue -->
<StatusID>6</StatusID>  <!-- In Progress -->
```

Do not assume those IDs are universal across projects. Read the target project's settings or verify visually.

Scrivener Trash is Binder parentage, not immediate data deletion. Moving an item to Trash moves the Binder node under the `TrashFolder` in `.scrivx`; the data folder usually remains readable. For immediate controlled restore tests, `Edit > Undo Move to Trash` was verified as reliable.

Snapshots live under:

```text
Project.scriv/Snapshots/<UUID>.snapshots/
```

Snapshot content is independent from later `content.rtf` edits.

## Direct Closed-Package Edits

Direct edits are allowed only when the project is closed, ideally on a copied package first. Verified direct edits:

- Replace `Files/Data/<UUID>/content.rtf` on a closed copied project using `textutil`.
- Edit a simple Binder `<Title>` in `.scrivx` on a closed copied project.

After direct edits:

1. Validate the `.scrivx` XML.
2. Open the copied project in Scrivener.
3. Verify the Binder title or body text appears correctly.
4. Only apply the same method to the real project if the user has approved that exact risk.

## Verification Commands

Fast verification examples:

```bash
PROJECT="references/TEST_PROJECT.scriv"
SCRIVX="$PROJECT/TEST_PROJECT.scrivx"
rg -n "<Title>|Known Binder Title" "$SCRIVX"
textutil -convert txt -stdout "$PROJECT/Files/Data/<UUID>/content.rtf"
textutil -convert txt -stdout "$PROJECT/Files/Data/<UUID>/notes.rtf"
sed -n '1,80p' "$PROJECT/Files/Data/<UUID>/synopsis.txt"
xmllint --noout "$SCRIVX"
```

More commands are in `references/verification.md`.

## Roundtrip Harness

A deterministic harness may be available at:

```text
scripts/scrivener_roundtrip.py
```

Reference it when the task calls for repeatable Scrivener roundtrip checks, package mapping, import/export validation, or regression testing. Do not create, edit, or overwrite that script from this skill; it is owned separately.

When using the harness, prefer a copied `.scriv` package unless the user explicitly asks to test the live project. For bundled smoke tests, run it from the skill root against `references/TEST_PROJECT.scriv`. Report the command run, target package, artifacts created, and verification result.

## Reporting Standard

When finished, summarize:

- target project path
- whether the project was open or closed
- actions performed through UI vs direct package edits
- UUIDs touched
- verification commands run
- outputs created, exported, compiled, or restored
- any unverified assumptions or stale sync concerns
