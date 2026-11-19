# Terminal design exports and checks, next to their canon-lib implementation.
#   make check            the canon's ui_style agrees with design-system/tokens.json
#   make sync ZIP=FILE    bring in a new export from Claude Design, print the token diff, check
#   make install          link the skill into ~/.claude/skills, ~/.codex/skills, ~/.hermes/skills
#   make uninstall        remove those links
ZIP ?=
RUN = uv run --quiet --project ../lib --locked --extra tui python

.PHONY: check sync install uninstall

check:
	$(RUN) scripts/check.py

sync:
	@test -n "$(ZIP)" || (echo "usage: make sync ZIP=~/Downloads/<export>.zip" && exit 2)
	python3 scripts/sync.py "$(ZIP)"

install:
	./install.sh

uninstall:
	./install.sh --uninstall
