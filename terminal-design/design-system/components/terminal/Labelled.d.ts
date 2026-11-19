import * as React from "react";
/**
 * A label + value row on the 12-column label grid.
 */
export interface LabelledProps { label: string; required?: boolean; focused?: boolean; indent?: number; children?: React.ReactNode }
export declare function Labelled(props: LabelledProps): JSX.Element;
