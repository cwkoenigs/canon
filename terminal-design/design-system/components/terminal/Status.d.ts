import * as React from "react";
/**
 * The single live line while the agent works.
 */
export interface StatusProps { step: string; secs?: number; frame?: 0 | 1 | 2 | 3 }
export declare function Status(props: StatusProps): JSX.Element;
