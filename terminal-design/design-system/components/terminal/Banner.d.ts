import * as React from "react";
/**
 * The startup banner: mascot, facts, path.
 * @startingPoint section="Terminal" subtitle="The startup banner: mascot, facts, path." viewport="640x330"
 */
export interface BannerProps { version?: string; tagline?: string; facts?: [string, string][]; hints?: string[]; path?: string }
export declare function Banner(props: BannerProps): JSX.Element;
