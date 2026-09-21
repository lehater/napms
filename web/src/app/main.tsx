import { StrictMode, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { AppShell } from "../components/AppShell";
import {
  ApplicationCatalogue,
  ApplicationDetail,
  InteractionAuthoring,
} from "../features/applications/ApplicationScreens";
import { BusinessConnectivity } from "../features/business-connectivity/BusinessConnectivity";
import { DeploymentScreens } from "../features/deployments/DeploymentScreens";
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
  } else if (route.id === "applications") {
    screen = <ApplicationCatalogue />;
  } else if (route.id === "application-new") {
    screen = <ApplicationCatalogue create />;
  } else if (route.id === "application-detail") {
    screen = <ApplicationDetail applicationRef={route.applicationRef} />;
  } else if (route.id === "component-new") {
    screen = (
      <ApplicationDetail
        applicationRef={route.applicationRef}
        createComponent
      />
    );
  } else if (route.id === "interaction-new") {
    screen = <InteractionAuthoring />;
  } else if (route.id === "revision-new") {
    screen = <InteractionAuthoring interactionRef={route.interactionRef} />;
  } else if (route.id === "deployments") {
    screen = <DeploymentScreens />;
  } else if (route.id === "deployment-new") {
    screen = <DeploymentScreens create />;
  } else if (route.id === "processes") {
    screen = <BusinessConnectivity />;
  } else if (route.id === "process-new") {
    screen = <BusinessConnectivity create />;
  } else if (route.id === "process-detail") {
    screen = <BusinessConnectivity processRef={route.processRef} />;
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
