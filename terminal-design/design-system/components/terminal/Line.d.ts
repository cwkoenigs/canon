import * as React from "react";
/**
 * A raw terminal row for anything the named primitives don't cover.
 */
export interface LineProps { children?: React.ReactNode; color?: "text" | "muted" | "dim" | "rule" | "accent" | "ok" | "warn" | "err"; style?: React.CSSProperties }
export declare function Line(props: LineProps): JSX.Element;
