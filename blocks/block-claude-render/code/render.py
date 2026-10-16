"""Print Cortex Code SDK messages the way Claude Code does. [[gotcha-terminal-ui]]

    state = {}
    status = console.status(status_label(state, started), spinner="dots")
    async for msg in session.turn(prompt):
        render(console, msg, state, prefix="mcp__kb__")
        status.update(status_label(state, started))
"""
from __future__ import annotations

import json
import time
from typing import Any

from cortex_agent_sdk.cortexcode import (AssistantMessage, ResultMessage, SystemMessage, TextBlock,
                                         ThinkingBlock, ToolResultBlock, ToolUseBlock, UserMessage)
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from rich.text import Text

ACCENT, DIM = "#d97757", "grey50"


def short_name(name: str, prefix: str = "") -> str:
    if prefix and name.startswith(prefix):
        return name[len(prefix):]
    return name[:1].upper() + name[1:]


def arg_summary(inp: dict[str, Any], width: int = 70) -> str:
    for key in ("command", "file_path", "path", "pattern", "id", "name", "query", "url", "title"):
        if isinstance(inp.get(key), str):
            v = inp[key].replace("\n", " ")
            return v if len(v) <= width else v[: width - 1] + "…"
    s = json.dumps(inp, ensure_ascii=False)
    return "" if s == "{}" else (s if len(s) <= width else s[: width - 1] + "…")


def bullet(body, style: str = "white") -> Table:
    t = Table.grid(padding=(0, 1))
    t.add_column(width=1, no_wrap=True)
    t.add_column()
    t.add_row(Text("⏺", style=style), body)
    return t


def asks(text: str) -> bool:
    """Whether a reply ends by asking something, even with an example after the question mark."""
    return any("?" in line for line in text.strip().splitlines()[-3:])


def result_text(block: ToolResultBlock) -> str:
    c = block.content
    if isinstance(c, list):
        c = "\n".join(p.get("text", "") for p in c if isinstance(p, dict))
    return (c or "").strip()


def render(console: Console, msg: Any, state: dict, prefix: str = "") -> None:
    """Text as ⏺ Markdown, tool calls as ⏺ Name(arg), results as ⎿ first line (+N lines), errors red
    (by flag or an ERROR: prefix), thinking hidden. Updates state: step, asked, model."""
    if isinstance(msg, AssistantMessage):
        for b in msg.content:
            if isinstance(b, TextBlock) and b.text.strip():
                console.print(bullet(Markdown(b.text.strip())))
                state["asked"] = asks(b.text)
            elif isinstance(b, ThinkingBlock):
                state["step"] = "Thinking"
            elif isinstance(b, ToolUseBlock):
                state["step"] = f"Running {short_name(b.name, prefix)}"
                head = Text(short_name(b.name, prefix), style="bold")
                if arg := arg_summary(b.input):
                    head.append(f"({arg})")
                console.print(bullet(head, style="green"))
    elif isinstance(msg, UserMessage) and isinstance(msg.content, list):
        for b in msg.content:
            if isinstance(b, ToolResultBlock):
                state["step"] = "Thinking"
                text = result_text(b)
                lines = text.splitlines() or ["(no output)"]
                more = f" … +{len(lines) - 1} lines" if len(lines) > 1 else ""
                style = "red" if b.is_error or text.startswith("ERROR:") else DIM
                console.print(Text(f"  ⎿  {lines[0][:100]}{more}", style=style))
    elif isinstance(msg, SystemMessage) and msg.subtype == "init":
        state["model"] = msg.data.get("model")
    elif isinstance(msg, ResultMessage):
        parts = [f"{msg.num_turns} turn{'s' if msg.num_turns != 1 else ''}", f"{msg.duration_ms / 1000:.1f}s"]
        if msg.is_error or msg.subtype != "success":
            console.print(Text(f"  ⎿  {msg.subtype}: {'; '.join(msg.errors or [])}", style="red"))
        console.print(Text("  " + " · ".join(parts), style=DIM))


def status_label(state: dict, started: float) -> str:
    """'✻ Running scaffold_get… 7s · ctrl-c to interrupt' for console.status()."""
    return (f"[{ACCENT}]✻[/] {state.get('step', 'Thinking')}… "
            f"[{DIM}]{int(time.monotonic() - started)}s · ctrl-c to interrupt[/]")
