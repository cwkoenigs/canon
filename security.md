---
id: security
version: 1
title: Security and Privacy
applies_to: ["*"]
default: adopt
owner: ckoenigs
status: proposed
date: 2026-10-14
source: guidebook v1.1 section 9
---

# Security and Privacy

### 9.1 Secure Defaults

- Use least privilege.
- Deny by default.
- Validate untrusted input.
- Use parameterized queries.
- Protect secrets.
- Encrypt restricted data in transit and at rest according to policy.
- Maintain dependency inventory and patch vulnerable dependencies.
- Log security-relevant events without exposing secrets.
- Separate ownership identities from consumption identities; use service identities for pipelines
  and services.
- Tag restricted data and apply masking or row-level controls where the platform supports them.
- Verify object ownership and grants after any recreate operation, and verify with a **real
  invocation** using the intended executing identity — not only a compile or deploy check.

### 9.2 Secrets

Secrets MUST NOT appear in:

- Git history.
- Logs.
- Test snapshots.
- Prompt examples.
- Notebooks.
- Tickets.
- Documentation screenshots.
- Error messages.
- Generated or committed config files. Gitignoring a source config is not sufficient if a generator
  bakes the value into committed output.

If a secret is exposed, rotate it and treat the repository/history as compromised until proven
otherwise.

### 9.3 Threat Modeling

Threat model changes involving:

- New external integrations.
- New auth/authz behavior.
- New restricted-data flow.
- LLM/tool access to internal data.
- Public-facing endpoints.
- Privileged automation.
- Data export.
- Production write capability.

Threat model output SHOULD include assets, actors, trust boundaries, abuse cases, controls, residual
risks, and tests.

### 9.4 AI-Specific Security

LLM/agent workflows MUST consider:

- Prompt injection.
- Data exfiltration through tool calls.
- Overbroad tool permissions.
- Insecure generated code or queries.
- Hallucinated procedures or policies.
- Restricted-data leakage in prompts, outputs, logs, and evals.
- Over-trust in confident but unsupported output.

Controls SHOULD include tool allowlists, scoped credentials, output validation, permission-aware
retrieval, human approval for destructive actions, and audit logs.

