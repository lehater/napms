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
        <h1>NAPMS</h1>
        {links.map(([path, label]) => (
          <a
            key={path}
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
      </nav>
      <main className="content">
        <h1>Network Access Policy Management</h1>
        {children}
      </main>
    </div>
  );
}
