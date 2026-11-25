import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Services from "./pages/Services";
import ServiceDetail from "./pages/ServiceDetail";
import Assistant from "./pages/Assistant";
import DocumentCheck from "./pages/DocumentCheck";
import Sources from "./pages/Sources";

export default function App() {
  return <BrowserRouter><Routes>
    <Route path="/" element={<Home />} />
    <Route path="/services" element={<Services />} />
    <Route path="/services/:id" element={<ServiceDetail />} />
    <Route path="/assistant" element={<Assistant />} />
    <Route path="/document-check" element={<DocumentCheck />} />
    <Route path="/sources" element={<Sources />} />
    <Route path="*" element={<Home />} />
  </Routes></BrowserRouter>;
}
