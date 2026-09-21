import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

function App() {
  return <main id="app-root" />;
}

const root = document.getElementById("root");
if (root === null) {
  throw new Error("Missing #root mount point");
}

createRoot(root).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
