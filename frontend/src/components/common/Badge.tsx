import type { ReactNode } from "react";
function Badge({children,kind=""}: { children: ReactNode; kind?: string }){return <span className={"badge "+kind}>{children}</span>}

export default Badge;
