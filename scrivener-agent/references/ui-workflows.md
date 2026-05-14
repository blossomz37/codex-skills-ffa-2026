# Scrivener UI Workflows

Use Scrivener UI automation for writes while a project is open. Package reads are for verification.

## Orientation

1. Use Computer Use `get_app_state` before interacting with Scrivener.
2. Confirm the active project window and visible Binder selection.
3. Select the intended Binder item or destination container before making changes.
4. After any meaningful UI change, save or wait for autosave before disk verification.

## Binder Reads And Writes

Verified UI operations:

- Read visible Binder and editor state through the accessibility tree.
- Create Binder documents and folders.
- Rename Binder items.
- Edit body text in the editor.
- Edit synopsis and notes through the Inspector.
- Move Binder items by drag/drop.
- Move items to Scrivener Trash.

Drag/drop moves can be visually ambiguous. Always verify the resulting parent/child nesting in `.scrivx`.

Expected `.scrivx` nesting pattern:

```xml
<BinderItem UUID="DESTINATION-UUID" Type="Folder">
  <Title>Destination Folder</Title>
  <Children>
    <BinderItem UUID="MOVED-ITEM-UUID" Type="Text">
      <Title>Moved Document</Title>
```

## Imports

Use:

```text
File > Import > Files...
```

Verified import formats:

- Markdown
- RTF

Import behavior:

- Imported files appear under the currently selected Binder container.
- Scrivener may use the source basename as the Binder title.
- Duplicate Binder titles are possible.
- Markdown headings may remain literal text rather than becoming styled Scrivener headings.

After import, verify the new Binder node in `.scrivx`, then map its UUID and inspect `content.rtf`.

## Exports

Use:

```text
File > Export > Files...
```

Verified behavior:

- Selected Binder text documents export successfully.
- Text exports defaulted to RTF in testing.

Verify exported RTF with:

```bash
textutil -convert txt -stdout output/path/exported-file.rtf
```

## Compile

Use:

```text
File > Compile...
```

Known behavior:

- Plain-text compile worked in testing.
- Compile used the current compile scope.
- Test Binder items outside `Manuscript` were not included.

After compile, inspect the output file directly. Do not assume a compile contains a Binder item unless the compile scope includes it.

## Labels And Statuses

Use the Inspector metadata controls for Label and Status, then verify in `.scrivx`.

Observed Dead Acre test mapping:

```xml
<LabelID>11</LabelID>
<StatusID>6</StatusID>
```

In that project:

- `LabelID 11` = Blue
- `StatusID 6` = In Progress

These IDs are project-specific. Confirm mappings before relying on them elsewhere.

## Snapshots

Create and rename snapshots through Scrivener UI. Verify package files under:

```text
Project.scriv/Snapshots/<UUID>.snapshots/
```

Snapshot files are independent from current body content. A later `content.rtf` replacement does not rewrite existing snapshots.

## Trash And Restore

Moving a Binder item to Trash does not immediately delete its data folder. It moves the Binder node under the project Trash folder.

Verify by finding the `TrashFolder` node in `.scrivx`:

```xml
<BinderItem UUID="..." Type="TrashFolder">
  <Title>Trash</Title>
```

For immediate restore after a controlled move-to-Trash test, prefer:

```text
Edit > Undo Move to Trash
```

This restored the same UUID to its original parent in verified testing.
