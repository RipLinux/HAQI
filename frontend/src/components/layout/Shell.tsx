import type { ReactNode } from "react";
import Header from "./Header";
import Footer from "./Footer";
function Shell({children}: { children: ReactNode }){return <><Header/>{children}<Footer/></>}
export default Shell;
