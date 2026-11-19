import * as React from "react";
/**
 * The slash-command menu.
 */
export interface MenuProps { items?: { name: string; desc: string; kind: string }[]; active?: number; total?: number; hint?: string }
export declare function Menu(props: MenuProps): JSX.Element;
