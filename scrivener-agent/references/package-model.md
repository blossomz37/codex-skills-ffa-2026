# Scrivener Package Model

Scrivener projects are package directories. Treat the package as structured project data, not a flat document.

## Typical Layout

```text
Project.scriv/
|-- Project.scrivx
|-- Files/
|   |-- Data/
|   |   `-- <UUID>/
|   |       |-- content.rtf
|   |       |-- notes.rtf
|   |       `-- synopsis.txt
|   |-- binder.autosave
|   |-- binder.backup
|   |-- docs.checksum
|   |-- search.indexes
|   `-- user.lock
|-- QuickLook/
|   `-- Preview.html
|-- Settings/
`-- Snapshots/
    `-- <UUID>.snapshots/
        |-- index.xml
        `-- <timestamp>.rtf
```

## Binder And UUIDs

The `.scrivx` file contains the Binder tree. Each Binder item has a UUID, title, type, and optional child items.

Use UUIDs for package reads and writes:

```xml
<BinderItem UUID="9C590F4B-97AF-4ABD-8B44-9B092246768A" Type="Text">
  <Title>Codex Move Test Document</Title>
```

Do not rely on Binder titles as unique IDs. Imports can create duplicate titles.

## Document Files

For a text Binder item:

- body text: `Files/Data/<UUID>/content.rtf`
- document notes: `Files/Data/<UUID>/notes.rtf`
- synopsis: `Files/Data/<UUID>/synopsis.txt`

Read RTF content with `textutil`:

```bash
textutil -convert txt -stdout "Project.scriv/Files/Data/<UUID>/content.rtf"
textutil -convert txt -stdout "Project.scriv/Files/Data/<UUID>/notes.rtf"
```

Read synopsis as plain text:

```bash
sed -n '1,80p' "Project.scriv/Files/Data/<UUID>/synopsis.txt"
```

## Direct Closed-Package Edits

Direct package edits are risky because Scrivener maintains in-memory state while open. Only direct-edit a closed project, and prefer a copied package for the first pass.

Verified direct edits on a closed copied project:

1. Replace `content.rtf` by converting plain text to RTF with `textutil`.
2. Edit a simple Binder `<Title>` in `.scrivx`.

Direct `content.rtf` replacement pattern:

```bash
textutil -convert rtf \
  -output "CopiedProject.scriv/Files/Data/<UUID>/content.rtf" \
  source-body.txt
```

Validate `.scrivx` after XML edits:

```bash
xmllint --noout CopiedProject.scriv/CopiedProject.scrivx
```

Then open the copied project in Scrivener and confirm the UI shows the edited body or Binder title.

## Direct Edit Boundaries

Safe enough when closed and copied:

- Generate replacement `content.rtf` with `textutil`.
- Change a simple Binder title in `.scrivx`.

Not proven safe:

- Direct edits to open/live packages.
- Arbitrary `.scrivx` structural edits.
- Permanent deletion or emptying Trash through package manipulation.
- Full production manuscript roundtrips without a disposable test first.

## Trash Model

Scrivener Trash is represented as a Binder folder with `Type="TrashFolder"`. Moving an item to Trash changes its parentage in `.scrivx`; it does not necessarily remove `Files/Data/<UUID>/`.

Verify Trash membership by inspecting the Binder tree under the Trash folder. Restore through UI when possible, especially immediately after a controlled move-to-Trash operation.
