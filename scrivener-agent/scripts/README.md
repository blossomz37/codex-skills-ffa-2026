# Scrivener Roundtrip Harness

Read-only helper for inspecting and verifying Scrivener `.scriv` packages or
their internal `.scrivx` files. It uses only Python 3 standard-library modules.
If macOS `textutil` is available, RTF extraction is converted through stdout;
otherwise the script falls back to a simple in-memory RTF text cleanup.

## Examples

```bash
cd scrivener-agent
scripts/scrivener_roundtrip.py --project references/TEST_PROJECT.scriv validate
scripts/scrivener_roundtrip.py --project Project.scriv list
scripts/scrivener_roundtrip.py --project Project.scriv --json list
scripts/scrivener_roundtrip.py --project Project.scriv find "Chapter 3"
scripts/scrivener_roundtrip.py --project Project.scriv tree
scripts/scrivener_roundtrip.py --project Project.scriv tree --uuid UUID-HERE
scripts/scrivener_roundtrip.py --project Project.scriv children UUID-HERE
scripts/scrivener_roundtrip.py --project Project.scriv extract UUID-HERE body
scripts/scrivener_roundtrip.py --project Project.scriv extract UUID-HERE notes
scripts/scrivener_roundtrip.py --project Project.scriv extract UUID-HERE synopsis
scripts/scrivener_roundtrip.py --project Project.scriv extract UUID-HERE snapshots
scripts/scrivener_roundtrip.py --project Project.scriv extract UUID-HERE all
scripts/scrivener_roundtrip.py --project Project.scriv verify-parent CHILD-UUID PARENT-UUID
scripts/scrivener_roundtrip.py --project Project.scriv verify-meta UUID-HERE --label 1 --status 2
```

The `--project` value may be either the `.scriv` package directory or the
package's `.scrivx` file.

## Commands

- `validate` parses the `.scrivx` with `xml.etree.ElementTree` and runs
  `xmllint --noout` when `xmllint` is installed.
- `list` prints binder titles, UUIDs, type, and hierarchy depth.
- `find TITLE` searches binder titles by substring; add `--exact` when needed.
- `tree` prints the full binder tree; `tree --uuid UUID` prints a subtree.
- `children UUID` prints direct child binder items.
- `extract UUID FIELD` reads `body`, `notes`, `synopsis`, `snapshots`, or `all`
  from `Files/Data/<UUID>/` and `Snapshots/<UUID>.snapshots/` without writing
  into the package.
- `verify-parent CHILD PARENT` checks a direct parent-child relationship.
- `verify-meta UUID --label LABEL --status STATUS` checks `LabelID` and/or
  `StatusID` values found in binder metadata.
