import { StrictMode, useState } from "react";
import { createRoot } from "react-dom/client";
import { api, type PolicyRuleView } from "./api";
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

function Status({ children }: { children: React.ReactNode }) {
  return (
    <p role="status" className="status">
      {children}
    </p>
  );
}

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
          <button type="button" onClick={open} disabled={!ref || state === "loading"}>
            Open resource
          </button>
        </div>
      </div>
      {state === "loading" && <Status>Loading Resource…</Status>}
      {state === "not-found" && <p role="alert" className="status">Resource not found.</p>}
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
              <p>Responsibilities: {resource.current.responsibilities.length}</p>
            </div>
            <details className="panel">
              <summary>History</summary>
              <p>Site facts: {resource.history.sites.length}</p>
              <p>
                Endpoint address facts: {resource.history.endpointAddresses.length}
              </p>
              <p>Responsibility facts: {resource.history.responsibilities.length}</p>
            </details>
          </div>
        </section>
      )}
    </>
  );
}

function AccessRequests() {
  const [fields, setFields] = useState({
    sourceDeploymentRef: "",
    destinationDeploymentRef: "",
    interactionRevisionRef: "",
    needRef: "",
  });
  const [result, setResult] = useState<Awaited<
    ReturnType<typeof api.submitAccessRequest>
  > | null>(null);
  const [state, setState] = useState<"idle" | "submitting" | "rejected" | "error">("idle");

  function field(name: keyof typeof fields, label: string) {
    return (
      <label>
        {label}
        <input
          value={fields[name]}
          onChange={(event) =>
            setFields((current) => ({ ...current, [name]: event.target.value }))
          }
        />
      </label>
    );
  }

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setState("submitting");
    setResult(null);
    try {
      setResult(await api.submitAccessRequest(fields));
      setState("idle");
    } catch (error) {
      setState(error instanceof Error && error.message === "rejected" ? "rejected" : "error");
    }
  }

  return (
    <>
      <p className="eyebrow">Access requests</p>
      <h2>Submit connectivity request</h2>
      <p className="lede">
        The immutable access subject is submitted to backend authority checks.
        Visible controls do not establish authority.
      </p>
      <form className="panel form-grid" onSubmit={submit}>
        {field("sourceDeploymentRef", "Source deployment")}
        {field("destinationDeploymentRef", "Destination deployment")}
        {field("interactionRevisionRef", "Interaction revision")}
        {field("needRef", "Connectivity need")}
        <button type="submit" disabled={state === "submitting"}>
          Submit request
        </button>
      </form>
      {state === "submitting" && <Status>Submitting request…</Status>}
      {state === "rejected" && (
        <p role="alert" className="status">Request was rejected by domain validation.</p>
      )}
      {state === "error" && (
        <p role="alert" className="status">Request could not be established.</p>
      )}
      {result && (
        <div className="panel">
          <p className="eyebrow">Authoritative outcome</p>
          <h3>Request submitted</h3>
          <p>Request: {result.requestRef}</p>
          <p>Version: {result.version}</p>
        </div>
      )}
    </>
  );
}

function PolicyRules() {
  const [ref, setRef] = useState("");
  const [rule, setRule] = useState<PolicyRuleView | null>(null);
  const [state, setState] = useState<"idle" | "loading" | "saving" | "not-found" | "error">("idle");

  async function open() {
    setState("loading");
    setRule(null);
    try {
      setRule(await api.getPolicyRule(ref));
      setState("idle");
    } catch (error) {
      setState(error instanceof Error && error.message === "not-found" ? "not-found" : "error");
    }
  }

  async function toggle() {
    if (!rule) return;
    setState("saving");
    try {
      const effectState = rule.effectState === "ACTIVE" ? "INACTIVE" : "ACTIVE";
      const updated = await api.setPolicyRuleState(rule.policyRuleRef, rule.version, effectState);
      setRule({ ...rule, effectState, version: updated.version });
      setState("idle");
    } catch {
      setState("error");
    }
  }

  return (
    <>
      <p className="eyebrow">Policy rules</p>
      <h2>Desired access</h2>
      <div className="panel">
        <label htmlFor="rule-ref">Policy Rule ID</label>
        <div>
          <input id="rule-ref" value={ref} onChange={(event) => setRef(event.target.value)} />
          <button type="button" onClick={open} disabled={!ref || state === "loading"}>
            Open rule
          </button>
        </div>
      </div>
      {state === "loading" && <Status>Loading Policy Rule…</Status>}
      {state === "not-found" && <p role="alert" className="status">Policy Rule not found.</p>}
      {state === "error" && <p role="alert" className="status">Policy operation failed.</p>}
      {rule && (
        <section className="panel">
          <p className="eyebrow">Authoritative detail</p>
          <h3>{rule.effectState}</h3>
          <p>{rule.policyRuleRef}</p>
          <dl>
            <dt>Source deployment</dt><dd>{rule.sourceDeploymentRef}</dd>
            <dt>Destination deployment</dt><dd>{rule.destinationDeploymentRef}</dd>
            <dt>Interaction revision</dt><dd>{rule.interactionRevisionRef}</dd>
          </dl>
          <button type="button" onClick={toggle} disabled={state === "saving"}>
            Set {rule.effectState === "ACTIVE" ? "inactive" : "active"}
          </button>
        </section>
      )}
    </>
  );
}

function Export() {
  const [selection, setSelection] = useState("");
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState(false);

  async function run() {
    setError(false);
    try {
      const refs = selection
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean);
      setResult(await api.materialize(refs.length ? refs : undefined));
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
      <div className="panel">
        <label htmlFor="export-scope">
          Policy Rule IDs
          <span className="muted"> (comma-separated; blank selects all)</span>
        </label>
        <input id="export-scope" value={selection} onChange={(event) => setSelection(event.target.value)} />
        <button type="button" onClick={run}>Execute export</button>
      </div>
      {error && <p role="alert" className="status">Export could not be established.</p>}
      {result && (
        <div className="panel">
          <p className="eyebrow">Authoritative outcome</p>
          <h3>{String(result.status)}</h3>
          <p>Evaluation: {String(result.evaluationAt)}</p>
          <p>Rows: {Array.isArray(result.rows) ? result.rows.length : 0}</p>
          <p>Issues: {Array.isArray(result.issues) ? result.issues.length : 0}</p>
          <details>
            <summary>Diagnostics and provenance</summary>
            <pre>{JSON.stringify(result, null, 2)}</pre>
          </details>
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
        ) : workspace === "Access requests" ? (
          <AccessRequests />
        ) : workspace === "Policy rules" ? (
          <PolicyRules />
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
