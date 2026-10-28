"""browse: a filterable picker for long lists, drawn like widgets.pick. [[gotcha-terminal-ui]] [[terminal-design]]

Inline, square frame (a frame means "needs you"), focus is ❯ in strong, the submit key is the one
filled band, and it erases itself when done. Type to filter, ↑/↓ to move, Enter chooses, Esc quits.
widgets.pick suits up to nine options picked by digit; browse suits tens or hundreds. Like every
Application here it is resize_safe: a terminal resize redraws it whole instead of stacking frames.
"""
from __future__ import annotations

from dataclasses import dataclass

from prompt_toolkit.application import Application
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import HSplit, Layout, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Frame, TextArea

from . import ui_style as S
from .ui_style import G
from .widgets import resize_safe


@dataclass
class Item:
    value: str                 # returned when chosen
    label: str                 # the name, in text
    detail: str = ""           # one line, muted
    outcome: str = ""          # "", "ok", "warn" or "err": the glyph before the label
    number: int | None = None  # shown dim before the label; typing it filters to it
    search: str = ""           # extra words the filter matches


def _clip(text: str, n: int) -> str:
    return text if len(text) <= n else text[:n].rsplit(" ", 1)[0].rstrip(",;:") + "…"


def _matches(items: list[Item], query: str) -> list[Item]:
    words = query.lower().split()
    if not words:
        return list(items)
    if len(words) == 1 and words[0].isdigit():
        return [i for i in items if i.number is not None and str(i.number).startswith(words[0])]
    return [i for i in items if all(w in f"{i.label} {i.detail} {i.search}".lower() for w in words)]


async def browse(title: str, items: list[Item], *, visible: int = 10, width: int = S.DESIGN_WIDTH) -> str | None:
    """Returns the chosen Item.value, or None on Esc / Ctrl-C."""
    state = {"i": 0, "top": 0}
    query = TextArea(multiline=False, wrap_lines=False, prompt=[("class:strong", f"{G.prompt} ")], style="class:field")
    shown = lambda: _matches(items, query.text)

    def reset(_):
        state["i"], state["top"] = 0, 0
    query.buffer.on_text_changed += reset

    kb = KeyBindings()

    def move(step: int):
        n = len(shown())
        if n:
            state["i"] = (state["i"] + step) % n
            if state["i"] < state["top"]:
                state["top"] = state["i"]
            elif state["i"] >= state["top"] + visible:
                state["top"] = state["i"] - visible + 1

    @kb.add("up", eager=True)
    @kb.add("c-p", eager=True)
    def _up(e):
        move(-1)

    @kb.add("down", eager=True)
    @kb.add("c-n", eager=True)
    @kb.add("tab", eager=True)
    def _down(e):
        move(1)

    @kb.add("enter", eager=True)
    def _enter(e):
        rows = shown()
        if rows:
            e.app.exit(result=rows[state["i"]].value)

    @kb.add("escape", eager=True)
    @kb.add("c-c", eager=True)
    def _cancel(e):
        e.app.exit(result=None)

    numbered = any(i.number is not None for i in items)
    nw = max((len(str(i.number)) for i in items if i.number is not None), default=0)

    def listing():
        rows = shown()
        out = []
        if not rows:
            out.append(("class:dim", "  nothing matches · Backspace widens it\n"))
        lw = min(max((len(i.label) for i in rows), default=10), 28) + 2
        room = width - 4 - 2 - (2 if any(i.outcome for i in items) else 0) - (nw + 2 if numbered else 0) - lw
        for n in range(state["top"], min(len(rows), state["top"] + visible)):
            it = rows[n]
            on = n == state["i"]
            out.append(("class:focus" if on else "class:field", f"{G.select if on else ' '} "))
            if it.outcome:
                out.append((f"class:{it.outcome}", getattr(G, it.outcome) + " "))
            elif any(i.outcome for i in items):
                out.append(("", "  "))
            if numbered:
                out.append(("class:dim", f"{'' if it.number is None else it.number:>{nw}}  "))
            out += [("class:focus" if on else "class:field", _clip(it.label, lw - 2).ljust(lw)),
                    ("class:muted", _clip(it.detail, max(room, 8)) + "\n")]
        if len(rows) > visible:
            out.append(("class:dim", f"  {G.fold} {len(rows)} match{G.sep}↑↓ scrolls\n"))
        out.append(("", "\n"))
        out += [("class:dim", "  type to filter · ↑↓ move · "), ("class:key", " Enter choose "), ("class:dim", " · Esc quit")]
        return FormattedText(out)

    frame = Frame(HSplit([query, Window(FormattedTextControl(listing), dont_extend_height=True)],
                         width=Dimension(max=width - 2)),
                  title=title, style="class:frame.border", width=width)
    app = resize_safe(Application(layout=Layout(VSplit([frame, Window()]), focused_element=query), key_bindings=kb,
                                  style=Style.from_dict(S.pt_style()), full_screen=False, erase_when_done=True))
    return await app.run_async()
