# Computer Use Field Guide For Authors

## How To Prove Whether An AI Agent Can Safely Work With Your Writing App

AI agents can now interact with desktop apps in two different ways:

1. They can use the app visually, like a careful assistant clicking menus, selecting sidebar items, typing text, and reading what is on screen.
2. They can inspect files on disk, like a technical assistant checking the document package, database, export folder, or project files behind the app.

The safest workflows use both. The app is used for live changes. The files are used to verify what really happened.

This guide explains how to test a writing app before trusting an agent with real work.

## The Core Question

Do not start with: "Can the agent use this app?"

Start with: "What can the agent prove?"

A useful app test should prove:

- what the agent can see in the interface
- what it can safely change through the app
- where the app stores content
- whether UI changes appear on disk
- whether disk changes can round-trip back into the app
- what operations are still unsafe or unknown

## Why This Matters For Writers

Writing apps often hide complexity behind a clean interface. A project may look like one file but actually contain folders, XML, RTF, databases, snapshots, cached indexes, images, compile settings, and app-specific metadata.

That matters because a bad automation path can:

- overwrite a draft
- corrupt a project package
- miss content stored outside the visible manuscript
- edit a cache instead of the real source
- create sync conflicts
- lose notes, snapshots, comments, labels, or metadata

A successful discovery test turns "I think it works" into "we know exactly which operations work and how to verify them."

## The Safe Testing Pattern

Use a practice project or copy. Do not use your active manuscript for first tests.

1. Open the app and identify the visible project.
2. Ask the agent to read the UI state.
3. Create or select a harmless test document.
4. Add a unique marker through the app.
5. Save or wait for autosave.
6. Search the project files for that marker.
7. Map the visible app item to the file or identifier on disk.
8. Close the test copy.
9. Make one tiny disk edit in the safest source file.
10. Reopen the copy and verify the app displays the disk edit.
11. Save again and confirm the app preserves the edit.
12. Write down the result in a capability report.

If any step fails, stop and document the failure. A failed test is still useful because it tells future agents where not to improvise.

## What Counts As Proof

The strongest proof is a round trip:

```text
UI change -> disk evidence -> disk change on closed copy -> app shows change -> app saves without discarding it
```

Each arrow should have evidence.

Examples of good evidence:

- The app visibly shows the created item.
- A project XML file contains the item title and identifier.
- A text/RTF file contains the marker phrase.
- A database query returns the expected row.
- A validator reports valid XML, JSON, plist, or SQLite integrity.
- The app reopens without repair warnings.
- The final save preserves the agent-created change.

## What To Test First

Start with low-risk capabilities.

### UI Reading

Can the agent:

- identify the active app and document
- read the sidebar or project structure
- read the editor text
- see selected items
- identify menus, toolbars, inspectors, and export controls

### UI Writing

Can the agent:

- create a test item
- rename it
- type harmless text
- use undo
- save
- export a selected item
- import a small test file

### Disk Reading

Can the agent:

- locate the project file or package
- identify the source-of-truth files
- distinguish source files from caches
- extract plain text from encoded formats
- map visible UI items to file identifiers

### Disk Writing On A Closed Copy

Can the agent:

- edit a copied project while the app is closed
- validate the changed file
- reopen the copy in the app
- see the change in the UI
- save without the app deleting or repairing the change

## Scrivener Case Study

Scrivener is a good example because a `.scriv` project is a package, not a single flat document.

In the tested workflow, the agent proved it could:

- read the Binder and editor through Computer Use
- create and rename Binder items
- import Markdown and RTF
- export a selected Binder item
- run compile/export flows
- set label and status values
- move a Binder item to Scrivener Trash and verify the move in the project XML
- restore a trashed item with undo
- map Binder titles to UUIDs
- read body text from `Files/Data/<UUID>/content.rtf`
- read notes and synopsis files
- read snapshots from `Snapshots/<UUID>.snapshots/`
- edit a closed copied project and verify Scrivener displayed the changed content

The key lesson was not "always edit Scrivener files directly." The key lesson was:

Use Scrivener for live writes. Use package inspection to verify. Use direct package edits only on a closed copy until the exact operation is proven.

## Safe And Unsafe Operations

### Usually Safe During Discovery

- reading the UI
- creating a scratch project
- typing a harmless marker into a scratch document
- saving a practice file
- exporting to a test folder
- reading project files from disk
- editing a copied project while the app is closed

### Needs Explicit Approval

- editing the real manuscript
- deleting app items
- emptying trash
- changing sync settings
- running publish/share/send actions
- applying direct disk edits to the original project
- modifying binary databases
- repairing, compacting, or migrating a project

### Treat As Unsafe Until Proven

- writing into a live/open project package
- editing cache or index files
- changing opaque binary files
- changing multiple linked metadata files by hand
- assuming visible item names are unique
- trusting cloud-synced files immediately after a save

## The Capability Report

Every useful app test should end with a short report. The report should answer:

- app/version
- test project/file
- UI capabilities
- disk model
- round-trip findings
- safe operations
- unsafe or unproven operations
- future-agent quick commands

Use `capability-report-template.md` as the reusable format.

## What Authors Should Ask An Agent

Good prompts:

```text
Use a practice project to discover what you can safely do with this app. Document UI capabilities, disk model, round-trip findings, and safe/unsafe operations.
```

```text
Before touching my real manuscript, create or use a disposable copy and prove UI-to-disk and disk-to-UI round trips.
```

```text
Turn the results into a future-agent reference with exact commands and failure modes.
```

Avoid prompts like:

```text
Edit my whole project directly and figure it out as you go.
```

```text
Delete the test files and clean up the app package manually.
```

## Teaching Takeaway

The author is not asking the agent to be magical. The author is asking the agent to be accountable.

A good agent workflow leaves evidence:

- what it touched
- what it avoided
- what it verified
- what remains unproven
- what the next agent can repeat without guessing

That evidence is what turns local app automation from a stunt into a usable writing workflow.
