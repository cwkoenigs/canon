"""Compile the cross-repo graph ([[adr-002]]) into the `repos` section of index.json.

    python scripts/build_repos.py checkouts/           # print the section's summary and report
    python scripts/build_repos.py checkouts/ --write   # and write the section into index.json

The registry is repos/<name>.toml, one file per registered repository ([repo] name, path on the
host). The checkouts directory holds a clone of each under its name: the pipeline makes it, and a
machine with the team's repos beside each other (`~/Developer`) is one already.

A clone's .ds/manifest.toml may declare [provides] (tables of strings: the commands, names and
paths other repos may run, share or read) and [uses] (one key per registered repo, the entries
it depends on). An entry is scanned for as written, less any `[optional part]` and a trailing `*`;
one that still holds a `*` or is under four characters is declared but not scanned. The scan is
`git grep` over the other clones' tracked files, less changelogs, decision logs, lock files, line-delimited
logs (*.jsonl) and the manifests themselves; a literal that names a file the mentioning repo tracks itself
(its own install.sh, its own index.json) is not a mention of another repo's. An entry is matched as text, so `index.json` matches every
index.json: declare the words other repos write when they use yours, and make them distinctive.

Written under `adoption` (adr-003): every standard against every registered repo it applies to, as
reconcile computes it from the standard's default and the repo's manifest: adopted (and who by
default), declined with reasons, pending. The org-wide view, without writing into any repo.

Written under `repos`: repos (name, path, commit, manifest, tags, provides, uses), edges (from,
to, what, declared, mentioned, count, where) and report (unused: provided, used by nobody;
undeclared: mentioned, not in the user's [uses]; unresolved: a [uses] entry naming no registered
repo or no provided entry; unscanned; unreadable: registered, not cloned; silent: registered,
declaring nothing). Rebuilt from scratch on every run. Needs Python 3.11 and git.
"""
from __future__ import annotations

import fnmatch
import json
import os
import re
import subprocess
import sys
import tomllib
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = (":!*CHANGELOG.md", ":!*DECISIONS.md", ":!*.lock", ":!*package-lock.json", ":!*.jsonl", ":!.ds/manifest.toml", ":!repos/*.toml")
MIN_LITERAL = 4
MAX_WHERE = 20


def literal(entry: str) -> str | None:
    """What the scan greps for: the entry less `[optional parts]` and a trailing `*`; None when
    what is left still holds a `*` or is shorter than MIN_LITERAL."""
    s = re.sub(r"\s*\[[^\]]*\]", "", entry)
    s = re.sub(r"\s+", " ", s).strip().removesuffix("*").rstrip()
    return s if len(s) >= MIN_LITERAL and "*" not in s else None


def registry(root: Path | None = None) -> list[dict]:
    """repos/<name>.toml, each with [repo] name (the file's stem) and path."""
    root = root or ROOT
    out = []
    for p in sorted((root / "repos").glob("*.toml")):
        repo = tomllib.loads(p.read_text()).get("repo", {})
        if repo.get("name") != p.stem or not repo.get("path"):
            raise ValueError(f'{p.relative_to(root)}: needs [repo] name = "{p.stem}" and path = "<group>/<project>"')
        out.append({"name": p.stem, "path": repo["path"]})
    return out


def manifest(clone: Path) -> dict:
    """The clone's declarations, or empty ones when it has no manifest."""
    p = clone / ".ds" / "manifest.toml"
    if not p.is_file():
        return {"manifest": False, "tags": [], "provides": {}, "uses": {}}
    data = tomllib.loads(p.read_text())
    stds = data.get("standards", {})
    return {"manifest": True, "tags": list(data.get("repo", {}).get("tags", [])),
            "provides": {k: [str(e) for e in v] for k, v in data.get("provides", {}).items()},
            "uses": {k: [str(e) for e in v] for k, v in data.get("uses", {}).items()},
            "standards": {k: dict(v) for k, v in stds.items() if isinstance(v, dict)} if isinstance(stds, dict) else {}}


def git(clone: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(clone), *args], check=False, capture_output=True, text=True)
    if r.returncode not in (0, 1):                    # grep exits 1 when nothing matches
        raise RuntimeError(f"git {args[0]} in {clone}: {r.stderr.strip()}")
    return r.stdout


def mentions(clone: Path, literals: list[str]) -> list[tuple[str, str]]:
    """(file:line, text) for every tracked line in the clone that holds one of the literals."""
    if not literals:
        return []
    args = ["grep", "-n", "-I", "-F"]
    for lit in literals:
        args += ["-e", lit]
    out = []
    for line in git(clone, *args, "--", ".", *SKIP).splitlines():
        f, _, rest = line.partition(":")
        n, _, text = rest.partition(":")
        out.append((f"{f}:{n}", text))
    return out


def tracked(clone: Path) -> set[str]:
    """The paths and basenames of the clone's tracked files: a mention of `install.sh` in a repo that has
    its own install.sh is about that one, not another repo's."""
    paths = [p for p in git(clone, "ls-files", "-z").split("\0") if p]
    return set(paths) | {p.rsplit("/", 1)[-1] for p in paths}


def resolve(entry: str, provider: dict | None) -> str | None:
    """The provided entry a [uses] entry names: the same text, or the same scan literal."""
    if provider is None:
        return None
    entries = [e for es in provider["provides"].values() for e in es]
    if entry in entries:
        return entry
    lit = literal(entry)
    return next((e for e in entries if lit is not None and literal(e) == lit), None)


def compile_graph(checkouts: Path, reg: list[dict]) -> dict:
    """The `repos` section: every registered repo as cloned under `checkouts`, the edges between
    them, and the report."""
    repos, clones, unreadable = [], {}, []
    for r in reg:
        clone = checkouts / r["name"]
        if not (clone / ".git").exists():
            unreadable.append(r["name"])
            continue
        repos.append({"name": r["name"], "path": r["path"], "commit": git(clone, "rev-parse", "--short", "HEAD").strip(),
                      **manifest(clone)})
        clones[r["name"]] = clone
    by_name = {r["name"]: r for r in repos}

    owners: dict[str, list[tuple[str, str]]] = {}     # scan literal -> (provider, entry as declared)
    unscanned = []
    for r in repos:
        for entries in r["provides"].values():
            for e in entries:
                lit = literal(e)
                if lit is None:
                    unscanned.append({"repo": r["name"], "what": e})
                else:
                    owners.setdefault(lit, []).append((r["name"], e))

    edges: dict[tuple[str, str, str], dict] = {}

    def edge(src: str, dst: str, what: str) -> dict:
        return edges.setdefault((src, dst, what), {"from": src, "to": dst, "what": what, "declared": False,
                                                   "mentioned": False, "count": 0, "where": []})

    for r in repos:
        own = tracked(clones[r["name"]])                # a literal that names a file this repo tracks is its own
        others = [lit for lit, owned in owners.items()
                  if any(o != r["name"] for o, _ in owned) and lit not in own and lit.rsplit("/", 1)[-1] not in own]
        for where, text in mentions(clones[r["name"]], others):
            hit = sorted((lit for lit in others if lit in text), key=len, reverse=True)
            for i, lit in enumerate(hit):
                if any(lit in longer for longer in hit[:i]):
                    continue                            # `ds-next` inside `ds-next setup`: the longer one counts
                for owner, entry in owners[lit]:
                    if owner == r["name"]:
                        continue
                    e = edge(r["name"], owner, entry)
                    e["mentioned"] = True
                    e["count"] += 1
                    if len(e["where"]) < MAX_WHERE:
                        e["where"].append(where)

    unresolved = []
    for r in repos:
        for target, entries in r["uses"].items():
            for u in entries:
                match = resolve(u, by_name.get(target))
                if match is None:
                    unresolved.append({"repo": r["name"], "uses": target, "what": u})
                else:
                    edge(r["name"], target, match)["declared"] = True

    edge_list = sorted(edges.values(), key=lambda e: (e["from"], e["to"], e["what"]))
    used = {(e["to"], e["what"]) for e in edge_list} | {(u["repo"], u["what"]) for u in unscanned}
    report = {
        "unused": [{"repo": r["name"], "what": e} for r in repos for es in r["provides"].values() for e in es
                   if (r["name"], e) not in used],              # an unscanned entry is reported once, as unscanned
        "undeclared": [{k: e[k] for k in ("from", "to", "what", "count", "where")} for e in edge_list
                       if e["mentioned"] and not e["declared"]],
        "unresolved": unresolved, "unscanned": unscanned, "unreadable": unreadable,
        "silent": [r["name"] for r in repos if not r["provides"] and not r["uses"]],
    }
    return {"generated": date.today().isoformat(), "built_by": os.environ.get("CI_PIPELINE_URL", "local"),
            "repos": repos, "edges": edge_list, "report": report}


def applies(std: dict, tags: list[str]) -> bool:
    return any(pat == "*" or any(fnmatch.fnmatchcase(t, pat) for t in tags) for pat in std.get("applies_to", []))


def effective(std: dict, entry: dict | None) -> tuple[str, str]:
    """(status, note) for one standard in one repo, as ds-next's reconcile computes it (adr-003): an explicit
    entry wins; a decline answers the version it was made against; otherwise the standard's default."""
    v = std["version"]
    if isinstance(entry, dict) and entry.get("status") == "declined":
        ev = entry.get("version") if isinstance(entry.get("version"), int) else 0
        return ("declined", str(entry.get("reason", ""))) if ev >= v else ("pending", f"declined at v{ev}")
    if isinstance(entry, dict) and entry.get("status") == "adopted":
        ev = entry.get("version") if isinstance(entry.get("version"), int) else 0
        if ev >= v:
            return "adopted", "explicit"
        if std.get("default", "adopt") == "adopt":
            return "adopted", f"by default; manifest says v{ev}"
        return "pending", f"adopted at v{ev}"
    return ("adopted", "by default") if std.get("default", "adopt") == "adopt" else ("pending", "")


def compile_adoption(repos: list[dict], standards: list[dict]) -> dict:
    """Every standard against every registered repo it applies to: who is adopted (and how), who declined
    (and why), who is pending. The org-wide view adr-000 promised, without writing into any repo."""
    per_std: dict[str, dict] = {}
    per_repo: dict[str, dict] = {}
    for std in standards:
        row = {"version": std["version"], "default": std.get("default", "adopt"), "adopted": [], "by_default": [],
               "declined": {}, "pending": []}
        for r in repos:
            if not r.get("manifest") or not applies(std, r.get("tags", [])):
                continue
            status, note = effective(std, r.get("standards", {}).get(std["id"]))
            mine = per_repo.setdefault(r["name"], {"adopted": 0, "declined": 0, "pending": []})
            if status == "adopted":
                row["adopted"].append(r["name"])
                mine["adopted"] += 1
                if note.startswith("by default"):
                    row["by_default"].append(r["name"])
            elif status == "declined":
                row["declined"][r["name"]] = note
                mine["declined"] += 1
            else:
                row["pending"].append(r["name"] + (f" ({note})" if note else ""))
                mine["pending"].append(std["id"])
        per_std[std["id"]] = row
    return {"generated": date.today().isoformat(), "standards": per_std, "repos": per_repo}


def summary(section: dict) -> str:
    edges = section["edges"]
    rep = section["report"]
    both = sum(e["declared"] and e["mentioned"] for e in edges)
    declared = sum(e["declared"] and not e["mentioned"] for e in edges)
    mentioned = sum(e["mentioned"] and not e["declared"] for e in edges)
    lines = [f"{len(section['repos'])} repos ({sum(r['manifest'] for r in section['repos'])} with a manifest), "
             + f"{len(edges)} edges ({both} declared and mentioned, {declared} declared only, {mentioned} mentioned only)"]
    for e in edges:
        where = f"  {', '.join(e['where'][:3])}{', …' if e['count'] > 3 else ''}" if e["where"] else ""
        lines.append(f"  {e['from']} -> {e['to']}: {e['what']}  [{'declared' if e['declared'] else 'undeclared'}"
                     f"{f', mentioned {e['count']}x' if e['mentioned'] else ', not mentioned'}]{where}")
    lines.append("report")
    for key, items in rep.items():
        if not items:
            continue
        lines.append(f"  {key} ({len(items)})")
        for it in items:
            lines.append("    " + (it if isinstance(it, str) else " ".join(f"{k}={v}" for k, v in it.items() if k != "where")))
    if not any(rep.values()):
        lines.append("  nothing to report")
    return "\n".join(lines)


def adoption_summary(adoption: dict) -> str:
    rows = adoption["standards"]
    total = sum(len(r["adopted"]) for r in rows.values())
    dflt = sum(len(r["by_default"]) for r in rows.values())
    declined = sum(len(r["declined"]) for r in rows.values())
    pending = sum(len(r["pending"]) for r in rows.values())
    head = (f"adoption: {len(rows)} standards x {len(adoption['repos'])} repos: {total} adopted ({dflt} by default), "
            f"{declined} declined, {pending} pending")
    lines = [head]
    for sid, r in rows.items():
        if r["declined"] or r["pending"]:
            why = "; ".join([*(f"{k} declined: {v}" for k, v in r["declined"].items()), *(f"{p} pending" for p in r["pending"])])
            lines.append(f"  {sid} v{r['version']}: {why}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    write = "--write" in argv
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__.split("\n\n")[0], file=sys.stderr)   # the first paragraph: what it is and how to run it
        return 2
    checkouts = Path(args[0]).expanduser().resolve()
    if not checkouts.is_dir():
        print(f"error: {checkouts} is not a directory", file=sys.stderr)
        return 2
    try:
        section = compile_graph(checkouts, registry())
    except (ValueError, RuntimeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(summary(section))
    out = ROOT / "index.json"
    index = json.loads(out.read_text()) if out.exists() else {}
    adoption = compile_adoption(section["repos"], index.get("standards", []))
    for r in section["repos"]:
        r.pop("standards", None)                     # the roll-up has what it needs; the row stays about contracts
    print(adoption_summary(adoption))
    if write:
        index["repos"] = section
        index["adoption"] = adoption
        out.write_text(json.dumps(index, indent=2) + "\n")
        print(f"wrote the repos and adoption sections of index.json ({len(section['repos'])} repos, "
              f"{len(section['edges'])} edges, {len(adoption['standards'])} standards)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
