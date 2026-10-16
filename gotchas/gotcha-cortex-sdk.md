---
id: gotcha-cortex-sdk
version: 2
title: Cortex Code SDK behaviour that is not in its docs
applies_to: ["cortex"]
owner: ckoenigs
status: proposed
kind: gotcha
date: 2026-10-16
source: ds-next build, 2026-10-16
---

# Cortex Code SDK behaviour that is not in its docs

Facts about driving Cortex Code 1.2.14 from Python, each found the hard way and checked live.

## Rules

1. **Use `snowflake-cortex-agent-sdk`, import `cortex_agent_sdk.cortexcode`.** It is the
   supported successor (Public Preview, 2026-10-13) to `cortex-code-agent-sdk`, with the same
   API. The old package's last release (1.0.7) declares `mcp>=1.0` with no upper bound but
   needs mcp 1.x, so a fresh install picks up mcp 2 and `create_sdk_mcp_server` raises
   `AttributeError: 'Server' object has no attribute 'list_tools'`. The new SDK caps `mcp<2`
   itself; do not pin mcp yourself.
2. **Never set `allowed_tools`.** Cortex treats it as an exclusive allowlist: every tool not on
   it is blocked before `can_use_tool` is asked, Bash and file edits included, and the model is
   told "not matched by any --allowed-tools pattern". Approve read-only tools inside the
   `can_use_tool` callback instead.
3. **`can_use_tool` is called with a kind, not the tool name.** `tool_name` is `"MCP"`, `"Bash"`,
   `"Write"`; `input` is `{"action": ..., "resource": ...}`. For MCP tools the first line of
   `resource` is the full tool name (`mcp__<server>__<tool>`) and the rest is `Input: {json}`.
   For Bash, `resource` is the command.
4. **Tool errors lose their flag.** Cortex drops `is_error` (and `isError`) from in-process tool
   results, so the model and the transcript see a success. Start every error result's text with
   `ERROR: ` so both can tell.
5. **Effort is fixed when the CLI starts.** Changing it means disconnecting and reconnecting
   with `resume=<session_id>`. A session reset must clear that resume id, or "start fresh"
   silently continues the old conversation.
6. **A first turn takes several seconds** to start the CLI; later turns reuse it. Show
   "Connecting…" and elapsed time, not a silent prompt.
7. **Connect and disconnect the client in the same task.** The SDK's connection lives in an anyio
   task group that must be exited in the task that entered it. Run the whole terminal in one
   `asyncio.run(...)` and call `connect()` directly, never inside `asyncio.gather()`,
   `create_task()`, or one `loop.run_until_complete()` per command; otherwise closing raises
   `RuntimeError: Attempted to exit cancel scope in a different task than it was entered in`.
   (Rebuild of 2026-10-16 crashed on /exit this way; ds-next then repeated it with gather().)
8. **After an interrupt, keep reading.** `interrupt()` makes the turn end early, but its remaining
   messages still arrive: keep consuming `receive_response()` until the `ResultMessage`, or they
   leak into the next turn.

## Check

- `grep -rn allowed_tools` finds nothing in code that creates options.
- A tool error test asserts the text starts with `ERROR:`.
- Accepted code: [[block-cortex-session]].
- A test connects and closes a fake client and asserts both ran in the caller's task.
