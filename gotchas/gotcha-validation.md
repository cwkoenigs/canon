---
id: gotcha-validation
version: 1
title: Validating manifests and Markdown
applies_to: ["python"]
owner: ckoenigs
status: proposed
kind: gotcha
date: 2026-10-16
source: ds-next build, 2026-10-16
---

# Validating manifests and Markdown

## Rules

1. **A check that runs in a hook never raises on bad input.** Every malformed value becomes an
   error line: missing tables, string tags, non-integer versions, unparsable dates, a non-table
   `standards`. One uncaught exception took the terminal down.
2. **TOML `datetime` is a subclass of `date`.** `isinstance(x, date)` accepts
   `2027-01-01T00:00:00Z`, and comparing it with a date raises. Reject datetimes explicitly.
3. **Type-check required text.** A blank reason, a numeric owner, or a date given as a reason
   all passed a truthiness check.
4. **Versions only go up:** reject an adoption at a version the canon never had, or it hides
   every future update.
5. **A decline answers one version.** When the standard gets a newer version, it is pending again.
6. **Code is not a claim.** Mask fenced blocks (three or more backticks or tildes, closed by at least as
   many) and inline spans with any number of backticks before reading `[[pointers]]`; check
   every Markdown file, not three, and check pins against the versions that exist.

## Check

- Accepted code: [[block-markdown-pointers]].
