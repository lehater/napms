import type { ReactNode } from "react";
import { navigate } from "../app/router";

const links = [
  ["/resources", "Resources"],
  ["/applications", "Applications"],
  ["/deployments", "Deployments"],
  ["/business-processes", "Business connectivity"],
  ["/access-requests", "Access requests"],
  ["/policy-rules", "Policy rules"],
  ["/policy-materializations/new", "Policy export"],
] as const;

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="shell">
      <nav className="nav" aria-label="Primary">
        <div className="nav-brand">
          <span className="nav-brand-mark" aria-hidden="true">
            N
          </span>
          <span>
            <strong>NAPMS</strong>
            <small>Policy management</small>
          </span>
        </div>
        <p className="nav-group-label">Workspaces</p>
        <div className="nav-links">
          {links.map(([path, label]) => (
            <a
              key={path}
              className="nav-link"
              href={path}
              aria-current={
                window.location.pathname.startsWith(path) ? "page" : undefined
              }
              onClick={(event) => {
                event.preventDefault();
                navigate(path);
              }}
            >
              {label}
            </a>
          ))}
        </div>
      </nav>
      <main className="content">{children}</main>
    </div>
  );
}
