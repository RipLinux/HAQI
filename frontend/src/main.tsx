import React from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

function App() {
  return <main dir="rtl"><h1>حقي | HAQI</h1><p>واجهة المشروع الأساسية قيد التطوير.</p></main>;
}

createRoot(document.getElementById("root")!).render(<React.StrictMode><App /></React.StrictMode>);
