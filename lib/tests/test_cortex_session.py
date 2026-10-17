import asyncio

from cortex_agent_sdk.cortexcode import tool

from canon_lib.cortex_session import CortexSession, TurnStalled, error_result


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


class FakeClient:
    """Connects, answers one message, then goes quiet, recording which task did what."""

    def __init__(self, options):
        self.events = []

    async def connect(self):
        self.events.append(("connect", asyncio.current_task()))

    async def query(self, prompt):
        pass

    async def receive_response(self):
        yield type("M", (), {"session_id": "s1"})()
        await asyncio.sleep(3600)

    async def interrupt(self):
        self.events.append(("interrupt", asyncio.current_task()))

    async def disconnect(self):
        self.events.append(("disconnect", asyncio.current_task()))


def test_a_stalled_turn_is_interrupted_not_waited_on(tmp_path, monkeypatch):
    import canon_lib.cortex_session as mod
    clients = []
    monkeypatch.setattr(mod, "CortexCodeSDKClient", lambda o: clients.append(FakeClient(o)) or clients[-1])
    s = CortexSession(tmp_path, [], "kb", set())

    async def go():
        got = []
        try:
            async for m in s.turn("hi", idle_timeout=0.2):
                got.append(m)
        except TurnStalled:
            return got, asyncio.current_task()
        raise AssertionError("did not stall")

    got, task = asyncio.run(asyncio.wait_for(go(), 5))
    assert len(got) == 1
    assert [e for e, _ in clients[0].events] == ["connect", "interrupt", "disconnect"]
    assert {t for _, t in clients[0].events} == {task}                 # one task, start to finish
    assert s.connected is False and s.options().resume == "s1"          # the next turn resumes


def test_no_stall_while_a_person_is_deciding(tmp_path, monkeypatch):
    import canon_lib.cortex_session as mod

    async def slow_person(name, inp, ctx):
        await asyncio.sleep(0.6)                 # three times the idle timeout
        return "allowed"

    s = CortexSession(tmp_path, [], "kb", set(), ask=slow_person)

    class Asks(FakeClient):
        async def receive_response(self):
            yield type("M", (), {"session_id": "s1"})()
            await s.permit("Bash", {"resource": "ls"}, None)    # Cortex waits on the approval
            yield type("M", (), {"session_id": "s1"})()

    monkeypatch.setattr(mod, "CortexCodeSDKClient", lambda o: Asks(o))

    async def go():
        return [m async for m in s.turn("hi", idle_timeout=0.2)]

    assert len(asyncio.run(asyncio.wait_for(go(), 5))) == 2


def test_reads_inside_the_working_directory_do_not_ask(tmp_path):
    asked = []

    async def ask(name, inp, ctx):
        asked.append(name)
        return "asked"

    (tmp_path / "src").mkdir()
    s = CortexSession(tmp_path, [], "kb", set(), ask=ask)

    def permit(kind, resource):
        return asyncio.run(s.permit(kind, {"action": "read", "resource": resource}, None))

    assert permit("Read", str(tmp_path / "src" / "a.py")).behavior == "allow"
    assert permit("Read", "src/a.py").behavior == "allow"
    assert permit("Glob", f"**/*.py in {tmp_path}").behavior == "allow"
    assert permit("Grep", f"TODO in {tmp_path / 'src'}").behavior == "allow"
    assert asked == []
    assert permit("Read", "/etc/hosts") == "asked"
    assert permit("Read", str(tmp_path / ".." / "elsewhere.txt")) == "asked"
    assert permit("Glob", f"../**/* in {tmp_path}") == "asked"
    assert permit("Grep", "secret in /Users") == "asked"
    assert permit("Write", str(tmp_path / "a.py")) == "asked"
    assert permit("Edit", str(tmp_path / "a.py")) == "asked"
