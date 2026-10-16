import asyncio

from {{package}}.approver import Approver, describe_permission


def test_describe():
    assert describe_permission("MCP", {"resource": 'mcp__kb__make\nInput: {"a": 1}'}, "mcp__kb__") == ("make", '{"a": 1}')
    assert describe_permission("Bash", {"resource": "ls"}) == ("Bash", "ls")


def test_serialized_and_whole():
    seen, active, peak = [], [0], [0]

    async def ask(title, detail):
        active[0] += 1
        peak[0] = max(peak[0], active[0])
        seen.append(detail)
        await asyncio.sleep(0.02)
        active[0] -= 1
        return "y"

    a = Approver(ask)
    long = "echo ok; " * 500 + "rm -rf ~/x"

    async def go():
        return await asyncio.gather(a("Bash", {"resource": long}, None), a("Bash", {"resource": "ls"}, None))

    assert all(r.behavior == "allow" for r in asyncio.run(go()))
    assert peak[0] == 1 and seen[0].endswith("rm -rf ~/x")


def test_only_explicit_answers():
    answers = iter(["", " ", "sure", "n"])

    async def ask(t, d):
        return next(answers)

    assert asyncio.run(Approver(ask)("Bash", {"resource": "x"}, None)).behavior == "deny"


def test_draft_covers_only_exact_calls():
    asked = []

    async def ask(t, d):
        asked.append(d)
        return "n"

    a = Approver(ask, prefix="mcp__kb__", draft_tool="make", ignore=("version",))
    a.draft = {"name": "x", "purpose": "p"}
    same = {"resource": 'mcp__kb__make\nInput: {"name": "x", "purpose": "p", "version": 2}'}
    assert asyncio.run(a("MCP", same, None)).behavior == "allow" and not asked
    a.draft = {"name": "x", "purpose": "p"}
    changed = {"resource": 'mcp__kb__make\nInput: {"name": "x", "purpose": "invented"}'}
    assert asyncio.run(a("MCP", changed, None)).behavior == "deny" and "purpose" in asked[0]
