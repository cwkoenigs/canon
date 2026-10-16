"""One Cortex Code session with in-process tools, the way that actually works. [[gotcha-cortex-sdk]]

    tools = [my_tool, ...]                      # made with cortex_agent_sdk.cortexcode.tool
    s = CortexSession(cwd, tools, server="kb", read_only={"list_things"}, ask=approver)
    async for msg in s.turn("hello"):
        ...
"""
from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable
from pathlib import Path
from typing import Any

from cortex_agent_sdk.cortexcode import (
    CortexCodeAgentOptions,
    CortexCodeSDKClient,
    Message,
    PermissionResultAllow,
    PermissionResultDeny,
    create_sdk_mcp_server,
)

ERROR_PREFIX = "ERROR: "
Ask = Callable[[str, dict[str, Any], Any], Awaitable[Any]]


def text_result(text: str) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": text}]}


def error_result(text: str) -> dict[str, Any]:
    """Cortex drops is_error for in-process tools, so the text says ERROR first as well."""
    return {"content": [{"type": "text", "text": ERROR_PREFIX + text}], "is_error": True}


class CortexSession:
    """Connects on the first turn. Never sets allowed_tools (Cortex treats it as an exclusive
    allowlist); read-only tools are approved in the permission callback, everything else goes
    to `ask`, and with no `ask` it is denied."""

    def __init__(self, cwd: Path, tools: list, server: str, read_only: set[str], ask: Ask | None = None,
                 system_prompt: str = "", model: str | None = None, connection: str | None = None,
                 effort: str | None = "low"):
        self.cwd, self.tools, self.server = Path(cwd).resolve(), tools, server
        self.read_only = {f"mcp__{server}__{t}" for t in read_only}
        self.ask, self.system_prompt = ask, system_prompt
        self.model, self.connection, self.effort = model, connection, effort
        self.session_id: str | None = None
        self._resume: str | None = None
        self._client: CortexCodeSDKClient | None = None

    def options(self) -> CortexCodeAgentOptions:
        return CortexCodeAgentOptions(
            cwd=str(self.cwd),
            mcp_servers={self.server: create_sdk_mcp_server(self.server, tools=self.tools)},
            append_system_prompt=self.system_prompt or None,
            can_use_tool=self.permit,
            model=self.model, connection=self.connection, effort=self.effort, resume=self._resume)

    async def permit(self, tool_name: str, inp: dict[str, Any], ctx: Any):
        """Cortex passes a kind ("MCP", "Bash", ...) and {"action", "resource"}; for MCP the first
        line of resource is the full tool name."""
        resource = str(inp.get("resource", "")) if isinstance(inp, dict) else ""
        if tool_name == "MCP" and resource.split("\n", 1)[0].strip() in self.read_only:
            return PermissionResultAllow()
        if self.ask is None:
            return PermissionResultDeny(message="No one is here to approve this call.")
        return await self.ask(tool_name, inp, ctx)

    @property
    def connected(self) -> bool:
        return self._client is not None

    async def turn(self, prompt: str) -> AsyncIterator[Message]:
        if self._client is None:
            client = CortexCodeSDKClient(self.options())
            await client.connect()
            self._client = client
        await self._client.query(prompt)
        async for msg in self._client.receive_response():
            if getattr(msg, "session_id", None):
                self.session_id = msg.session_id
            yield msg

    async def interrupt(self) -> None:
        if self._client is not None:
            await self._client.interrupt()

    async def set_effort(self, effort: str | None) -> None:
        """Effort is fixed when the CLI starts: reconnect, resuming the same conversation."""
        self.effort = effort
        if self._client is not None:
            resume = self.session_id
            await self.close()
            self._resume = resume

    async def close(self) -> None:
        if self._client is not None:
            client, self._client = self._client, None
            await client.disconnect()

    async def reset(self) -> None:
        await self.close()
        self.session_id = None
        self._resume = None
