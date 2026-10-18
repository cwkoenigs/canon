---
id: gotcha-tool-arguments
version: 1
title: Tool arguments a model will actually send
applies_to: ["mcp", "cli"]
owner: ckoenigs
status: proposed
kind: gotcha
date: 2026-10-17
source: honest test rounds 1 and 2 (ds-next bench/judge), 2026-10-17
---

# Tool arguments a model will actually send

Scope: any tool exposed to a model (MCP, SDK tools). Decision from: 10 of 17 tool errors in one
build were argument names, and every failed call cost a turn.

1. **Accept the names models mix up.** `id`, `name`, `ids`, `query` were sent to the wrong tools
   across every run. Take the aliases and say which one you meant in the description.
2. **Make optional arguments optional in the schema.** A required `tags` made an empty
   `canon_list` call fail before the handler ran.
3. **Accept lists as JSON text and as comma-separated text.** Models send both.
4. **A missing argument gets a one-line hint, not a schema error:** "pass id (block:name); code_search finds ids".
