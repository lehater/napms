import { StrictMode, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { AppShell } from "../components/AppShell";
import {
  ResourceCatalogue,
  ResourceDetail,
} from "../features/resources/ResourceScreens";
import { parseRoute, type Route } from "./router";
import "../design-system/base.css";

function App() {
  const [route, setRoute] = useState<Route>(() =>
    parseRoute(window.location.pathname),
  );

  useEffect(() => {
    const update = () => setRoute(parseRoute(window.location.pathname));
    window.addEventListener("popstate", update);
    return () => window.removeEventListener("popstate", update);
  }, []);

  let screen: React.ReactNode;
  if (route.id === "resources") {
    screen = <ResourceCatalogue />;
  } else if (route.id === "resource-new") {
    screen = <ResourceCatalogue create />;
  } else if (route.id === "resource-detail") {
    screen = <ResourceDetail resourceRef={route.resourceRef} />;
  } else {
    screen = (
      <section className="panel">
        <h2>Workspace migration in progress</h2>
        <p className="muted">{route.id}</p>
      </section>
    );
  }

  return <AppShell>{screen}</AppShell>;
}

const root = document.getElementById("root");
if (root === null) throw new Error("Missing #root mount point");
createRoot(root).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
