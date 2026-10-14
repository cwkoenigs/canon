---
id: error-handling
version: 1
title: Error Handling
applies_to: ["service", "package"]
owner: ckoenigs
status: proposed
date: 2026-10-14
source: guidebook v1.1 section 12
---

# Error Handling

### 12.1 Error Categories

Standardize errors into categories:

- Validation.
- Authentication.
- Authorization.
- Not found.
- Conflict.
- Rate limited.
- Dependency failure.
- Timeout.
- Data quality failure.
- Internal error.

### 12.2 User-Facing Errors

User-facing errors SHOULD:

- Explain what happened.
- Explain what the user can do next.
- Avoid exposing internals.
- Preserve user input.
- Provide a correlation ID for support.
- Avoid blame language.

### 12.3 Internal Errors

Internal errors SHOULD include:

- Correlation ID.
- Error category.
- Component.
- Operation.
- Relevant non-sensitive context.
- Stack trace where appropriate and protected.
- Retryability.

