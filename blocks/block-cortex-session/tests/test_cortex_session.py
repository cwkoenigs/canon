import asyncio

from cortex_agent_sdk.cortexcode import tool

from {{package}}.cortex_session import CortexSession, error_result


@tool("list_things", "List", {})
async def list_things(args):
    return {"content": [{"type": "text", "text": "a"}]}


def test_never_an_allowlist_and_reads_are_auto_approved(tmp_path):
    asked = []

    async def ask(name, inp, ctx):
        asked.append(name)
        return "asked"

    s = CortexSession(tmp_path, [list_things], "kb", {"list_things"}, ask=ask)
    assert s.options().allowed_tools == []
    r = asyncio.run(s.permit("MCP", {"resource": "mcp__kb__list_things\nInput: {}"}, None))
    assert r.behavior == "allow" and asked == []
    assert asyncio.run(s.permit("Bash", {"resource": "rm x"}, None)) == "asked"
    assert asyncio.run(CortexSession(tmp_path, [], "kb", set()).permit("Bash", {}, None)).behavior == "deny"


def test_errors_say_so_in_text():
    assert error_result("boom")["content"][0]["text"] == "ERROR: boom"


def test_reset_does_not_resume(tmp_path):
    s = CortexSession(tmp_path, [], "kb", set())
    s._resume = s.session_id = "old"
    asyncio.run(s.reset())
    assert s.options().resume is None
