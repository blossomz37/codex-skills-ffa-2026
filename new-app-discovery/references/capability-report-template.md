# App Capability Report Template

Use this template after testing whether an AI agent can safely work with a local app, writing app, document format, project bundle, or GUI workflow. Replace placeholders with evidence, not guesses.

## Target

- App:
- Version:
- Platform:
- Test project/file:
- Test copy or scratch file:
- Date:
- Discovery goal:
- Agent/tools used:

## Executive Summary

One paragraph covering:

- what is proven
- what is not proven
- safest recommended automation path
- whether this app is ready for real work, copy-only work, or read-only use

## Capability Matrix

| Capability | Status | Evidence | Validation | Risk | Next Step |
| --- | --- | --- | --- | --- | --- |
| Read UI state | Unknown | | | | |
| Navigate UI | Unknown | | | | |
| Select/open app items | Unknown | | | | |
| Read files | Unknown | | | | |
| Write via UI | Unknown | | | | |
| Write via disk | Unknown | | | | |
| Export/import | Unknown | | | | |
| Compile/render/publish | Unknown | | | | |
| Batch automation | Unknown | | | | |

Status options: `Proven`, `Likely`, `Unknown`, `Unsafe`.

Risk options: `Low`, `Medium`, `High`.

## UI Capabilities

| UI Action | Result | Evidence | Notes |
| --- | --- | --- | --- |
| Open app/document | Unknown | | |
| Read visible structure | Unknown | | |
| Select item/sidebar row | Unknown | | |
| Edit text/content | Unknown | | |
| Use menus/toolbars | Unknown | | |
| Import file | Unknown | | |
| Export file | Unknown | | |
| Run compile/render/publish flow | Unknown | | |
| Undo/restore change | Unknown | | |

## Disk Model

### Storage Map

- Artifact type:
- Source-of-truth files:
- Cache/index files:
- Metadata files:
- Media/assets:
- Files changed by UI marker:
- Files ignored by agent:
- Validation commands:

### Identifier Map

If the UI uses stable IDs, UUIDs, database keys, or filenames, document them here.

| UI Item | Disk Identifier | Source File | Notes |
| --- | --- | --- | --- |
| | | | |

## Round-Trip Findings

### UI To Disk

- Marker:
- UI action:
- Save/flush action:
- Disk evidence:
- Reopen result:
- Status:

### Disk To UI

- Edited file:
- Edit made:
- Validation command:
- Reopen result:
- App save result:
- Status:

### Persistence After App Save

- Final app save action:
- Files changed after save:
- Automation edit preserved:
- Cache/index behavior:
- Status:

## Safe Operations

List operations that were proven end-to-end on a scratch file or copy.

- Proven safe:
- Safe only on closed copy:
- Safe read-only:

## Unsafe Or Unproven Operations

List operations that are unsafe, untested, or require fresh approval.

- Do not attempt:
- Needs user confirmation:
- Needs disposable copy first:
- Needs app-specific docs/API:

## Failure Modes Observed

- Autosave/sync delay:
- UI mismatch:
- Disk mismatch:
- Format validation issue:
- App repair/migration behavior:
- Other:

## Future-Agent Quick Commands

Use relative paths or caller-supplied variables. Do not include personal absolute paths.

```bash
APP_FILE="path/to/test-project-or-copy"
find "$APP_FILE" -maxdepth 4 -type f | sort
rg -n "KNOWN_MARKER|known text" "$APP_FILE"
file "$APP_FILE"
```

Format-specific examples:

```bash
jq . path/to/file.json
plutil -lint path/to/file.plist
xmllint --noout path/to/file.xml
sqlite3 path/to/database.sqlite 'PRAGMA integrity_check;'
```

## Recommended Agent Workflow

1. 
2. 
3. 

## Human Review Notes

- What the user should inspect manually:
- What the agent can repeat confidently:
- What should become a script, skill, or app-specific reference:

## Recommended Next Workflow

- 
