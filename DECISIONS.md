# Decisions

<!-- ds:local adopted 2026-10-30 -->
Local decisions for this repo, numbered local-001 upward. Team-wide decisions belong in the
canon as standards; this file links them with `[[id]]` rather than restating them.

## local-001: Keep skills-os separate from canon

- **Status** Accepted
- **Date** 2026-11-19
- **Context** Canon owns standards, scaffolds and reusable code. The private `skills-os` repository
  owns the team's operating procedures. The public canon installer brings both checkouts into the
  team stack, and `ds-next setup` registers the team skills in Claude Code, Codex and Cortex Code.
- **Options considered**
  1. **Keep the separate checkout.** Preserve the existing publication boundary and keep one setup
     command for the supported agents. Standards and procedure changes that depend on each other
     still need coordinated commits across two repositories.
  2. **Move the skills into canon.** This would reduce the team stack from four checkouts to three
     and let related policy and procedure changes land in one commit. It would also require a review
     for public release, a migration of existing agent registrations, and a new home for the skill
     build and verification checks.
- **Decision** Keep `skills-os` as the source of team procedures and `ds-next setup` as their
  installer. One fewer checkout offers limited benefit while setup already handles registration.
- **Validation** On a fresh installation, `ds-next setup` should register the team skills from the
  separate checkout. On an existing machine, `ds-next setup --check` should find the same skills
  without modifying registrations.
- **Revisit when** Standards and their corresponding procedures regularly need to change together,
  or the extra private checkout repeatedly blocks fresh installs or updates. Before moving, review
  the proposed files for public release and prove that fresh installs and upgrades work across
  all three supported agents. Keep the existing private history in its original repository.
