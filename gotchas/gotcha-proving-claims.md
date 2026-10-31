---
id: gotcha-proving-claims
version: 1
title: Proving a claim about a tool or a knowledge base
applies_to: ["*"]
default: adopt
owner: ckoenigs
status: proposed
kind: gotcha
date: 2026-10-17
source: the knowledge-system proof of concept (ds-next REPORT.md), 2026-10-17
---

# Proving a claim about a tool or a knowledge base

Scope: any test of "X makes the agent's output better". Decision from: the first round scored
canon with checks written from canon's own lessons, and found a 19-point gain that was circular.

1. **The judge never sees the thing under test.** A separate run writes hidden tests from the
   ticket alone; nobody edits them.
2. **Validate the judge before scoring:** a reference must pass it, and planted bugs must fail it.
3. **The control must be able to fail.** A baseline at 100% cannot show improvement; it took five
   tasks to learn that the model already knew everything canon held.
4. **One mechanism per arm.** Lessons and code mixed in one arm hid that the lessons cost 2× and
   the code paid for itself.
5. **Medians and ranges**, never means over three runs; cost varied 4× run to run.
