---
id: testing
version: 1
title: Testing and QA
applies_to: ["*"]
default: adopt
owner: ckoenigs
status: proposed
date: 2026-10-14
source: guidebook v1.1 section 10
---

# Testing and QA

### 10.1 Risk-Based Test Mix

Use the lowest-cost reliable test for the risk:

| Test type | Purpose |
|---|---|
| Unit | Verify small logic in isolation. |
| Component | Verify module behavior with controlled dependencies. |
| Integration | Verify real boundaries such as database/API/tool calls. |
| Contract | Verify producer/consumer schema and behavior. |
| End-to-end | Verify critical user journeys. |
| Data quality | Verify accuracy, freshness, uniqueness, completeness, validity. |
| Security | Verify access control, input handling, dependency risk. |
| Accessibility | Verify keyboard and assistive technology behavior. |
| Performance | Verify latency, throughput, cost, and scaling assumptions. |
| LLM eval | Verify prompt/model behavior against expected outcomes. |

### 10.2 Required Test Considerations

Tests SHOULD cover:

- Happy path.
- Boundary values.
- Null/empty input.
- Invalid input.
- Permission failures.
- Dependency failures.
- Retry behavior.
- Duplicate input.
- Out-of-order input.
- Backfill/reprocessing.
- Migration/rollback.
- Observability evidence.

Bug fixes SHOULD include a regression test that fails before the fix and passes after the fix.
Capture the failing evidence in the decision log when practical.

### 10.3 Tests Must Assert Runnable Behavior

A test that greps for a string can pass on a comment while no working code exists. Assert the real
artifact: an executable branch, a parsed structure, an actual invocation — not a substring that
prose could satisfy.

**Prove a new test works by breaking it.** A test that has never failed has not been shown to test
anything. Temporarily remove the fix, confirm the test goes red, restore the fix.

**Run the thing before declaring it done.** A passing suite is not evidence that the workflow works
end to end. Execute the actual command, script, or interaction.

### 10.4 QA Evidence Package

For material releases, QA evidence SHOULD include:

- Test plan and results.
- Known defects.
- Risk acceptance.
- Screenshots or recordings for UX-critical flows.
- Data reconciliation outputs for data changes.
- Security review notes where applicable.
- Approval record.

