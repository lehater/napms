export type Route =
  | { id: "resources"; path: "/resources" }
  | { id: "resource-new"; path: "/resources/new" }
  | { id: "resource-detail"; path: string; resourceRef: string }
  | { id: "applications"; path: "/applications" }
  | { id: "application-new"; path: "/applications/new" }
  | { id: "application-detail"; path: string; applicationRef: string }
  | { id: "component-new"; path: string; applicationRef: string }
  | { id: "interaction-new"; path: "/interactions/new" }
  | { id: "revision-new"; path: string; interactionRef: string }
  | { id: "deployments"; path: "/deployments" }
  | { id: "deployment-new"; path: "/deployments/new" }
  | { id: "processes"; path: "/business-processes" }
  | { id: "process-new"; path: "/business-processes/new" }
  | { id: "process-detail"; path: string; processRef: string }
  | { id: "access-requests"; path: "/access-requests" }
  | { id: "access-request-new"; path: "/access-requests/new" }
  | { id: "access-request-decision"; path: string; requestRef: string }
  | { id: "policy-rules"; path: "/policy-rules" }
  | { id: "policy-rule-detail"; path: string; policyRuleRef: string }
  | { id: "policy-export"; path: "/policy-materializations/new" };

function decoded(match: RegExpMatchArray, index: number): string {
  return decodeURIComponent(match[index] ?? "");
}

export function parseRoute(pathname: string): Route {
  if (pathname === "/" || pathname === "/resources") return { id: "resources", path: "/resources" };
  if (pathname === "/resources/new") return { id: "resource-new", path: "/resources/new" };
  let match = pathname.match(/^\/resources\/([^/]+)$/);
  if (match) return { id: "resource-detail", path: pathname, resourceRef: decoded(match, 1) };
  if (pathname === "/applications") return { id: "applications", path: "/applications" };
  if (pathname === "/applications/new") return { id: "application-new", path: "/applications/new" };
  match = pathname.match(/^\/applications\/([^/]+)\/components\/new$/);
  if (match) return { id: "component-new", path: pathname, applicationRef: decoded(match, 1) };
  match = pathname.match(/^\/applications\/([^/]+)$/);
  if (match) return { id: "application-detail", path: pathname, applicationRef: decoded(match, 1) };
  if (pathname === "/interactions/new") return { id: "interaction-new", path: "/interactions/new" };
  match = pathname.match(/^\/interactions\/([^/]+)\/revisions\/new$/);
  if (match) return { id: "revision-new", path: pathname, interactionRef: decoded(match, 1) };
  if (pathname === "/deployments") return { id: "deployments", path: "/deployments" };
  if (pathname === "/deployments/new") return { id: "deployment-new", path: "/deployments/new" };
  if (pathname === "/business-processes") return { id: "processes", path: "/business-processes" };
  if (pathname === "/business-processes/new") return { id: "process-new", path: "/business-processes/new" };
  match = pathname.match(/^\/business-processes\/([^/]+)$/);
  if (match) return { id: "process-detail", path: pathname, processRef: decoded(match, 1) };
  if (pathname === "/access-requests") return { id: "access-requests", path: "/access-requests" };
  if (pathname === "/access-requests/new") return { id: "access-request-new", path: "/access-requests/new" };
  match = pathname.match(/^\/access-requests\/([^/]+)\/decision$/);
  if (match) return { id: "access-request-decision", path: pathname, requestRef: decoded(match, 1) };
  if (pathname === "/policy-rules") return { id: "policy-rules", path: "/policy-rules" };
  match = pathname.match(/^\/policy-rules\/([^/]+)$/);
  if (match) return { id: "policy-rule-detail", path: pathname, policyRuleRef: decoded(match, 1) };
  if (pathname === "/policy-materializations/new") return { id: "policy-export", path: "/policy-materializations/new" };
  return { id: "resources", path: "/resources" };
}

export function navigate(path: string): void {
  if (window.location.pathname === path) return;
  window.history.pushState({}, "", path);
  window.dispatchEvent(new PopStateEvent("popstate"));
}
