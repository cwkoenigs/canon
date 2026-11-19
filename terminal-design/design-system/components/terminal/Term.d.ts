import * as React from "react";
/**
 * The terminal pane every other primitive renders inside.
 * @startingPoint section="Terminal" subtitle="The terminal pane every other primitive renders inside." viewport="640x120"
 */
export interface TermProps { theme?: "dark" | "light"; cols?: number; children?: React.ReactNode; style?: React.CSSProperties }
export declare function Term(props: TermProps): JSX.Element;
