# platform

The future-state platform, in four parts.

    docs/knowledge-system.md   the knowledge system, as the team will meet it
    docs/agent-system.md       the agent system and harness, invisible to the team
    docs/ds-cli-updates.md     the `ds` changes that deliver both
    bench/                     standards-bench: creates canon + repos, runs tasks, scores
    BUILD.md                   the overnight brief for the agent that builds all of it
    adr-000-knowledge-system.md   the original design record

Start: read BUILD.md. Hand it to the agent with:

    Read BUILD.md and do what it says. Work through D1..D8 in order.
    Write BUILD-REPORT.md before you stop for any reason.

Quick check that the bench works on this machine:

    cd bench && uv tool install . && cd .. && bench init /tmp/sb \
      && bench run /tmp/sb --runner dry --tasks-only && bench score /tmp/sb
