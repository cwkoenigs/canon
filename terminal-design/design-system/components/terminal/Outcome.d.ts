import * as React from "react";
/**
 * A flat ✓ ⚠ ✗ line with no rail, for local commands.
 */
export interface OutcomeProps { kind?: "ok" | "warn" | "err"; subject: string; detail?: string }
export declare function Outcome(props: OutcomeProps): JSX.Element;
