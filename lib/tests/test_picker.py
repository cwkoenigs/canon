"""browse, driven by real keystrokes through a pipe, and the filter it uses."""
import asyncio

from prompt_toolkit.application import create_app_session
from prompt_toolkit.input import create_pipe_input
from prompt_toolkit.output import DummyOutput

from canon_lib.picker import Item, _clip, _matches, browse


def drive(coro_fn, keys: str):
    async def go():
        with create_pipe_input() as inp, create_app_session(input=inp, output=DummyOutput()):
            task = asyncio.ensure_future(coro_fn())
            await asyncio.sleep(0.1)
            for ch in keys:                       # one key at a time, as a person types
                inp.send_text(ch)
                await asyncio.sleep(0.01)
            return await asyncio.wait_for(task, 3)
    return asyncio.run(go())


def ITEMS():
    return [Item("orders", "order-metrics", "daily order counts", number=1),
            Item("claims", "claims-model", "scores claims", outcome="warn", number=2, search="risk"),
            Item("site", "docs site", "the portal", number=12)]


def test_matches_every_word_across_label_detail_and_search():
    assert [i.value for i in _matches(ITEMS(), "")] == ["orders", "claims", "site"]
    assert [i.value for i in _matches(ITEMS(), "claims risk")] == ["claims"]
    assert [i.value for i in _matches(ITEMS(), "ORDER counts")] == ["orders"]
    assert _matches(ITEMS(), "nothing here") == []


def test_a_number_filters_by_the_items_number():
    assert [i.value for i in _matches(ITEMS(), "1")] == ["orders", "site"]
    assert [i.value for i in _matches(ITEMS(), "12")] == ["site"]


def test_clip_cuts_at_a_word_and_marks_it():
    assert _clip("short", 10) == "short"
    assert _clip("one two three four", 9) == "one two…"


def test_enter_chooses_the_first_match():
    assert drive(lambda: browse("t", ITEMS()), "risk\r") == "claims"


def test_arrows_move_and_wrap():
    assert drive(lambda: browse("t", ITEMS()), "\x1b[B\x1b[B\r") == "site"
    assert drive(lambda: browse("t", ITEMS()), "\x1b[A\r") == "site"


def test_escape_quits_with_nothing():
    assert drive(lambda: browse("t", ITEMS()), "ord\x1b") is None


def test_enter_on_no_match_does_nothing_until_widened():
    assert drive(lambda: browse("t", ITEMS()), "zzz\r\x7f\x7f\x7f\r") == "orders"
