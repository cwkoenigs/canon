---
id: gotcha-cortex-sdk
version: 4
title: Cortex Code SDK behaviour that is not in its docs
applies_to: ["cortex"]
default: adopt
owner: ckoenigs
status: proposed
kind: gotcha
date: 2026-10-28
source: ds-next build, 2026-10-16; rule-cli build and review, 2026-10-25 and 2026-10-26
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
9. **`cortex exec` and `--print` are blocked on subscription and trial accounts** ("--print mode is
   not available for subscription/trial accounts"), whatever the output format. The stream-json
   protocol the SDK uses still works, so script Cortex through the SDK, `ds-next ask`, or
   `cortex --input-format stream-json --output-format stream-json` with one JSON user message
   (`{"type": "user", "session_id": "default", "parent_tool_use_id": null, "message": {...}}`)
   on stdin.
10. **Every turn needs a stall timeout.** A Cortex stream can stop without ending: one waited over
    two hours. Bound the wait between messages, interrupt and say so when it passes, and treat
    "Network connection was interrupted while streaming" as retryable. Pause that bound while a
    person is answering an approval (Cortex is silent then by design), and do not use
    `asyncio.timeout` around the stream: cancelling its `__anext__` finalizes the generator.
    Accepted code: [[block-cortex-session]] v2.
11. **Accounts have a request cap.** "You have reached the maximum number of requests for your
    subscription. Your limit will reset in N hours" arrives as a turn result, not an exception;
    show it as the reason, not as a failed task.

12. **A repo's hooks run, and no session option stops them.** Cortex Code 1.2.18 ran the
    `UserPromptSubmit` hooks in both `.cortex/settings.json` and `.claude/settings.json` of the working
    folder on the first prompt. `setting_sources=["user"]` left them running and stopped Cortex reading
    the repo's `AGENTS.md` and `CLAUDE.md`; `disableAllHooks` through `--config` left them running too.
    Ask first: [[gotcha-approvals]] rule 9. Checked live on 2026-10-26.
13. **A missing `cortex` CLI hangs the session without a word.** The Node SDK
    (`@snowflake/cortex-agent-sdk` 0.0.2 and 0.0.3) records the spawn error and never reports it.
    Look for the CLI where the SDK will (`CORTEX_CODE_CLI_PATH`, then `cortex` on the PATH) and say
    what is missing before starting; a timeout cannot tell a slow start from a missing CLI.

## Check

- `grep -rn allowed_tools` finds nothing in code that creates options.
- A tool error test asserts the text starts with `ERROR:`.
- Accepted code: [[block-cortex-session]].
- A test connects and closes a fake client and asserts both ran in the caller's task.
- A test opens a session in a folder whose `.cortex/settings.json` defines a hook: the person is
  asked, with the hook's command, and a no starts nothing.
