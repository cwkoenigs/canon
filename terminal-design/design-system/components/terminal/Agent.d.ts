import * as React from "react";
/**
 * The agent speaking — ● then │ continuation.
 */
export interface AgentProps { lines?: React.ReactNode[]; children?: React.ReactNode }
export declare function Agent(props: AgentProps): JSX.Element;
