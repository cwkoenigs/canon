"""Approve what a model wants to do: explicit, whole, one at a time. [[gotcha-approvals]]"""
from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable
from typing import Any

from cortex_agent_sdk.cortexcode import PermissionResultAllow, PermissionResultDeny


def describe_permission(tool_name: str, inp: dict[str, Any], prefix: str = "") -> tuple[str, str]:
    """(title, detail) from Cortex's ("MCP" | "Bash" | ..., {"action", "resource"}). For MCP the
    first resource line is the tool name; `prefix` (e.g. "mcp__kb__") is stripped from it."""
    resource = str(inp.get("resource", "")) if isinstance(inp, dict) else ""
    if tool_name == "MCP":
        first, _, rest = resource.partition("\n")
        name = first.strip()
        return (name[len(prefix):] if prefix and name.startswith(prefix) else name), rest.removeprefix("Input:").strip()
    return tool_name, resource or json.dumps(inp, indent=1)


def _norm(v: Any) -> Any:
    if v in (None, "", [], {}):
        return None
    return [str(x).strip().lower() for x in v] if isinstance(v, list) else v


def changed_keys(draft: dict, args: dict, ignore: tuple[str, ...] = ()) -> list[str]:
    keys = (set(draft) | set(args)) - set(ignore)
    return sorted(k for k in keys if _norm(draft.get(k)) != _norm(args.get(k)))


class Approver:
    """A can_use_tool callback. `ask(title, detail) -> answer` shows a request and reads a line.

    Serialized (Cortex may request parallel calls), whole (never truncated), explicit (only
    y/yes, a/always, n/no; anything else asks again). A pre-approved `draft` covers a call to
    `draft_tool` only when every field matches; otherwise the change is shown and asked."""

    def __init__(self, ask: Callable[[str, str], Awaitable[str]], prefix: str = "", draft_tool: str = "",
                 ignore: tuple[str, ...] = ()):
        self.ask, self.prefix, self.draft_tool, self.ignore = ask, prefix, draft_tool, ignore
        self.always: set[str] = set()
        self.draft: dict | None = None
        self._lock = asyncio.Lock()

    def reset(self) -> None:
        self.always.clear()
        self.draft = None

    async def __call__(self, tool_name: str, inp: dict[str, Any], ctx: Any):
        async with self._lock:
            title, detail = describe_permission(tool_name, inp, self.prefix)
            if title in self.always:
                return PermissionResultAllow()
            if self.draft is not None and title == self.draft_tool:
                try:
                    args = json.loads(detail)
                except ValueError:
                    args = {}
                diff = changed_keys(self.draft, args, self.ignore)
                if not diff:
                    self.draft = None
                    return PermissionResultAllow()
                detail = "Changed from what you submitted:\n" + "\n".join(
                    f"  {k}: {self.draft.get(k, '')!r} -> {args.get(k, '')!r}" for k in diff) + "\n\n" + detail
            while True:
                answer = (await self.ask(title, detail)).strip().lower()
                if answer in ("a", "always"):
                    self.always.add(title)
                    return PermissionResultAllow()
                if answer in ("y", "yes"):
                    return PermissionResultAllow()
                if answer in ("n", "no"):
                    return PermissionResultDeny(message="The user declined this call. Ask what to do instead.")
