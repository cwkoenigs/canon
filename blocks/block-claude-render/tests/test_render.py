from cortex_agent_sdk.cortexcode import (
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ThinkingBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
)
from rich.console import Console

from {{package}}.render import asks, render


def test_renders_like_claude_code():
    con = Console(record=True, width=100, color_system=None)
    state = {}
    render(con, AssistantMessage([ThinkingBlock("private"), TextBlock("Here **it** is."),
                                  ToolUseBlock("1", "mcp__kb__get", {"id": "x"}), ToolUseBlock("2", "bash", {"command": "ls"})],
                                 "m"), state, prefix="mcp__kb__")
    render(con, UserMessage([ToolResultBlock("1", [{"type": "text", "text": "ERROR: nope\nmore"}])]), state)
    render(con, ResultMessage("success", 1500, 1000, False, 2, "s"), state)
    out = con.export_text()
    assert "private" not in out
    assert "⏺ Here it is." in out and "⏺ get(x)" in out and "⏺ Bash(ls)" in out
    assert "⎿  ERROR: nope … +1 lines" in out and "2 turns · 1.5s" in out


def test_asks():
    assert asks('What does it do? One line (e.g. "x").') and not asks("Done.")
