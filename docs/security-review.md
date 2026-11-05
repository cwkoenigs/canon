# Security review: the Data Science knowledge system on a work Mac

One page for a security team. It describes the **work-safe** install, which is the only way it
should be installed on a managed machine: `ds-system --work-safe`, or plain `ds-system` run from a
canon cloned from the team's GitLab, which chooses work-safe by itself. The machine remembers the
mode, so later updates stay work-safe without anyone remembering a flag.

## What it is

Five internal git repositories and the command-line tools built from them. They give the team's
coding agent (Cortex Code, the approved agent) the team's written standards, project templates
and code-navigation tools. There is no server and no background service.

| Repository | What it adds |
|---|---|
| canon | The team's standards (Markdown), project templates, a small Python library, the install scripts |
| ds-next | The `ds-next` command: a terminal for the agent, and a local tool server the agent starts |
| skills-os | Written procedures (Markdown) the agent follows |
| docs-ds | A documentation site generator (Docusaurus), run locally on demand |
| ds-code | A local code-navigation tool server (TypeScript and Pyright language servers) |

## Where everything comes from

- **Source code:** only the team's GitLab group. github.com and any other source are refused.
- **Programs:** none downloaded. git, uv (Python package manager), Python 3.12, Node.js and the
  agent CLI must already be installed through Self Service or IT. If one is missing the install
  stops. uv is told never to download a Python (`UV_PYTHON_DOWNLOADS=never`), since it would
  otherwise fetch one from github.com.
- **Third-party packages:** only the exact versions in the committed lockfiles (`uv.lock`,
  `package-lock.json`), through whatever package mirror uv and npm are configured to use
  (`UV_DEFAULT_INDEX`, `.npmrc`). npm checks every package against the SHA-512 recorded in its
  lockfile, and npm install scripts are switched off. Python packages for canon's library are
  checked against the hashes in `uv.lock`. Python packages for ds-next are pinned to the lockfile's
  versions, but their hashes are not yet enforced.
- **Nothing is piped from the internet into a shell.** The install is: clone with git, read, run.

## What it changes on the machine

All changes are inside the user's home folder. No admin rights or `sudo`, no launch agents or
daemons, no system settings, no global npm or pip installs.

| Location | Change |
|---|---|
| `~/Developer/<repo>` | The five clones, each with its own Python or Node dependencies inside it |
| `~/.local/bin` | Two symlinks: `ds-next` and `ds-code` |
| `~/.ds/config.toml` | Where the team's repos live, and the name (not the value) of the GitLab token variable |
| Agent settings (`~/.snowflake/cortex/settings.json`, and Claude Code or Codex settings if installed) | Registers the two local tool servers, links the skills, and pre-approves the read-only tools (a `.json.bak` backup is kept) |

`canon/uninstall.sh` reverses all of it. It keeps any clone with unsaved or unpushed work.

## Network use when running

- ds-next, ds-code and canon's library make **no network calls of their own**. Their tool servers
  talk to the agent over stdin/stdout on the same machine.
- The **agent CLI** (Cortex Code) talks to its own provider (Snowflake), as it does without this
  system.
- One read-only tool, `snowflake_search`, runs `cortex search` (Snowflake documentation, object
  names, table details) through the Cortex CLI with the user's own Snowflake connection and
  permissions. It returns metadata, not table rows.
- **docs-ds** serves the docs on `localhost:3333` while a user has `/docs` open.
- **Captures** (`/so-capture`) open a merge request in the team's GitLab, using the user's own
  `glab` login or token, and only when the user runs the command. A person reviews the merge
  request before anything is published.

## Controls on the agent

- Only read-only tools are pre-approved. Every tool that writes (creating a project, adopting a
  standard, saving a capture) still asks the user each time.
- Secrets are never written to config, logs or git. The `security` standard in canon governs the
  projects the agent creates.

## What it does not do

- It does not read, copy or move company or customer data. It handles code, Markdown standards
  and project templates.
- It does not add an AI model or provider. It works through the agent CLI the company already
  approved.
- It does not update itself. Updates happen only when a user runs `bootstrap.sh`, which pulls from
  the team's GitLab and reinstalls from the lockfiles.

## Contact

Owner: ckoenigs. Source: the canon, ds-next, skills-os, docs-ds and ds-code repositories in the
team's GitLab group.
