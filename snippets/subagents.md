# Subagent Procedures


## Subagent Check

Before starting any non-trivial task, ask:

1. Can any part of this be done in parallel?
2. Can that part be assigned a clear, bounded output?
3. Can it avoid editing the same files or state as the main task?
4. Would its result reduce context load, uncertainty, or review risk?

If yes to at least 3 of 4, spawn a subagent. Keep the immediate blocking task in the main thread.


## Shorter version 1

For any task with research, multiple artifacts, large file inspection, or independent verification, consider subagents by default. Spawn only when the work has clear ownership and will not block the next main-thread step.


## Shorter version 2

Before executing a substantial request, perform a “subagent fit check.” If there are independent research, review, artifact-writing, or file-inspection tracks, spawn subagents proactively and keep the critical path local.
