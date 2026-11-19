import * as React from "react";
/**
 * A square frame — it always means "needs you".
 * @startingPoint section="Terminal" subtitle="A square frame — it always means "needs you"." viewport="640x200"
 */
export interface FrameProps { title?: React.ReactNode; kind?: "input" | "approval"; keys?: React.ReactNode; onRail?: boolean; children?: React.ReactNode }
export declare function Frame(props: FrameProps): JSX.Element;
