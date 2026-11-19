import * as React from "react";
/**
 * The folded first line of a tool result.
 */
export interface ResultProps { children?: React.ReactNode; more?: number; error?: boolean; foldKey?: string }
export declare function Result(props: ResultProps): JSX.Element;
