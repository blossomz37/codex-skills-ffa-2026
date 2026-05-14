# Scrivener Verification Commands

Use these commands to verify Scrivener work from disk. Set `PROJECT` and `SCRIVX` to the target project, then replace UUIDs for the target Binder item.

Bundled smoke-test fixture, relative to the skill root:

```bash
PROJECT="references/TEST_PROJECT.scriv"
SCRIVX="$PROJECT/TEST_PROJECT.scrivx"
```

Generic project variables:

```bash
PROJECT="Project.scriv"
SCRIVX="$PROJECT/Project.scrivx"
```

## Locate Project

Prefer app/document-local paths when known. If you need to locate a project by name, use `mdfind` over broad filesystem crawls:

```bash
mdfind 'kMDItemFSName == "Project.scriv"'
```

List package files from the project root:

```bash
find "$PROJECT" -maxdepth 3 -type f | sort | head -80
```

## Map Binder Titles To UUIDs

Find titles and nearby Binder nodes:

```bash
rg -n "Known Title|<Title>" "$SCRIVX"
nl -ba "$SCRIVX" | sed -n '205,335p'
```

Search for known body text:

```bash
rg -n "Known phrase from document body" "$PROJECT"
```

## Read Body, Notes, And Synopsis

Body:

```bash
textutil -convert txt -stdout "$PROJECT/Files/Data/<UUID>/content.rtf"
```

Notes:

```bash
textutil -convert txt -stdout "$PROJECT/Files/Data/<UUID>/notes.rtf"
```

Synopsis:

```bash
sed -n '1,80p' "$PROJECT/Files/Data/<UUID>/synopsis.txt"
```

## Verify Snapshots

List snapshot files:

```bash
find "$PROJECT/Snapshots/<UUID>.snapshots" -type f -name '*.rtf' -print
```

Read a snapshot:

```bash
textutil -convert txt -stdout "$PROJECT/Snapshots/<UUID>.snapshots/<timestamp>.rtf"
```

## Validate XML

Use `xmllint`, not `plutil`:

```bash
xmllint --noout "$SCRIVX"
```

`.scrivx` files are XML project files, not Apple plists.

## Verify Exported RTF

```bash
textutil -convert txt -stdout output/scrivener-tests/exported-file.rtf
```

## Verify Compile Output

```bash
sed -n '1,120p' output/scrivener-tests/compiled-output.txt
wc -w output/scrivener-tests/compiled-output.txt
```

Remember that compile output depends on Scrivener's current compile scope.

## Roundtrip Harness

The Scrivener roundtrip harness is expected at:

```text
scripts/scrivener_roundtrip.py
```

Do not create or edit it from this skill. When present, use it for repeatable validation of package mapping, import/export flows, and regression checks.

Before running a harness against production work:

1. Confirm whether it mutates the target project.
2. Prefer a copied `.scriv` package.
3. Capture the exact command and output artifact paths.
4. Verify resulting `.scrivx`, body text, notes, synopsis, export, or compile artifacts with the commands above.

Suggested command shape, subject to the harness help text:

```bash
python scripts/scrivener_roundtrip.py --help
python scripts/scrivener_roundtrip.py --project "$PROJECT" validate
```

Read the script's help before assuming flags.

## Stale Sync Check

If the package is under Google Drive and state looks stale:

```bash
sleep 5
rg -n "Known Title|Known body phrase" "$SCRIVX" "$PROJECT/Files/Data"
```

For important changes, run a second verification pass before reporting failure.
