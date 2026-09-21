import { StrictMode, useState } from "react";
import { createRoot } from "react-dom/client";
import { api } from "./api";
import "../design-system/base.css";

type Workspace =
  | "Resources"
  | "Applications"
  | "Deployments"
  | "Business connectivity"
  | "Access requests"
  | "Policy rules"
  | "Policy export";

const workspaces: Workspace[] = [
  "Resources",
  "Applications",
  "Deployments",
  "Business connectivity",
  "Access requests",
  "Policy rules",
  "Policy export",
];

function Placeholder({ name }: { name: Workspace }) {
  return (
    <>
      <p className="eyebrow">Workspace</p>
      <h2>{name}</h2>
      <div className="panel">
        <p className="muted">
          No records loaded. Use the supported authoring actions when backend
          data is available.
        </p>
      </div>
    </>
  );
}

function Resources() {
  const [ref, setRef] = useState("");
  const [state, setState] = useState<
    "idle" | "loading" | "not-found" | "error"
  >("idle");
  const [resource, setResource] = useState<Awaited<
    ReturnType<typeof api.getResource>
  > | null>(null);

  async function open() {
    setState("loading");
    setResource(null);
    try {
      setResource(await api.getResource(ref));
      setState("idle");
    } catch (error) {
      setState(
        error instanceof Error && error.message === "not-found"
          ? "not-found"
          : "error",
      );
    }
  }

  return (
    <>
      <p className="eyebrow">Resource catalogue</p>
      <h2>Resources</h2>
      <p className="lede">
        Locate a Resource by stable identity and inspect current facts before
        history.
      </p>
      <div className="panel">
        <label htmlFor="resource-ref">Resource ID</label>
        <div>
          <input
            id="resource-ref"
            value={ref}
            onChange={(event) => setRef(event.target.value)}
          />
          <button
            type="button"
            onClick={open}
            disabled={!ref || state === "loading"}
          >
            Open resource
          </button>
        </div>
      </div>
      {state === "loading" && (
        <p role="status" className="status">
          Loading Resource…
        </p>
      )}
      {state === "not-found" && (
        <p role="alert" className="status">
          Resource not found.
        </p>
      )}
      {state === "error" && (
        <p role="alert" className="status">
          Resource could not be loaded. Retry when the service is available.
        </p>
      )}
      {resource && (
        <section>
          <p className="eyebrow">Resource detail</p>
          <h3>{resource.displayName}</h3>
          <p className="muted">
            {resource.resourceRef} · authority {resource.authorityScopeRef}
          </p>
          <div className="grid">
            <div className="panel">
              <h4>Current facts</h4>
              <p>Site: {resource.current.siteRef ?? "Not assigned"}</p>
              <p>Endpoints: {resource.current.endpoints.length}</p>
              <p>
                Responsibilities: {resource.current.responsibilities.length}
              </p>
            </div>
            <details className="panel">
              <summary>History</summary>
              <p>Site facts: {resource.history.sites.length}</p>
              <p>
                Endpoint address facts:{" "}
                {resource.history.endpointAddresses.length}
              </p>
              <p>
                Responsibility facts: {resource.history.responsibilities.length}
              </p>
            </details>
          </div>
        </section>
      )}
    </>
  );
}

function Export() {
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState(false);

  async function run() {
    setError(false);
    try {
      setResult(await api.materialize());
    } catch {
      setError(true);
    }
  }

  return (
    <>
      <p className="eyebrow">Policy export</p>
      <h2>Materialize current policy</h2>
      <p className="lede">
        Export authority is confirmed by the backend. COMPLETE and UNRESOLVED
        outcomes remain distinct.
      </p>
      <button type="button" onClick={run}>
        Execute export
      </button>
      {error && (
        <p role="alert" className="status">
          Export could not be established.
        </p>
      )}
      {result && (
        <div className="panel">
          <h3>{String(result.status)}</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </>
  );
}

function App() {
  const [workspace, setWorkspace] = useState<Workspace>("Resources");
  return (
    <div className="shell">
      <nav className="nav" aria-label="Primary">
        <h1>NAPMS</h1>
        {workspaces.map((item) => (
          <button
            type="button"
            key={item}
            aria-current={workspace === item ? "page" : undefined}
            onClick={() => setWorkspace(item)}
          >
            {item}
          </button>
        ))}
      </nav>
      <main className="content">
        <h1>Network Access Policy Management</h1>
        {workspace === "Resources" ? (
          <Resources />
        ) : workspace === "Policy export" ? (
          <Export />
        ) : (
          <Placeholder name={workspace} />
        )}
      </main>
    </div>
  );
}

const root = document.getElementById("root");
if (root === null) throw new Error("Missing #root mount point");
createRoot(root).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
