---
id: gotcha-generated-text
version: 1
title: User text in generated files
applies_to: ["python"]
owner: ckoenigs
status: proposed
kind: gotcha
date: 2026-10-16
source: ds-next build, 2026-10-16
---

# User text in generated files

Answers typed by a person end up in Python, TOML, YAML and Markdown. Each of those has its own
quoting, and an unescaped value either breaks the file or changes what it says.

## Rules

1. **Insert user text as a JSON string literal** (`json.dumps(s, ensure_ascii=False)`, with DEL
   escaped). A JSON string is a valid Python string, a valid TOML basic string, and a valid YAML
   double-quoted scalar, so one function covers all three.
2. **Never `ensure_ascii=True`** for TOML: emoji become surrogate escapes (`\ud83d\ude80`),
   which TOML rejects ("not a Unicode scalar value").
3. **Never put raw text in a docstring.** `"""{purpose}"""` breaks on a trailing quote and
   lets `"""` end the string and inject statements. Use the JSON literal as the first statement.
4. **YAML plain scalars are not shell strings.** `- echo "lint: skipped"` parses as a mapping.
   Quote every command.
5. **Fill templates in one pass** (one regex over `{{name}}`), never with a loop of
   `str.replace`: a value that contains `{{other}}` would pull in another, unescaped value.
6. **Answers are one line.** Reject control characters and line or paragraph separators; a
   newline in a TOML or front-matter value ends the value.
7. **Package names must import.** `class`, `match` and names with double dashes pass a simple
   regex but cannot be imported.

## Check

- Render with `Print "hello" \ 🚀 """ end` as the purpose and `echo "lint: skipped"` as a
  command; every `.py` compiles, every `.toml` parses, the CI YAML's script items are strings.
- Accepted code: [[block-text-safety]].
