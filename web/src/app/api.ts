import { authSession } from "./auth-session";

export type ApiErrorKind =
  | "not-found"
  | "rejected"
  | "conflict"
  | "unauthenticated"
  | "forbidden"
  | "unavailable"
  | "technical";

export class ApiError extends Error {
  constructor(
    readonly kind: ApiErrorKind,
    readonly status: number,
  ) {
    super(kind);
  }
}

export async function request<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const accessToken = authSession.accessToken();
  const response = await fetch(path, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...init.headers,
    },
  });
  if (!response.ok) {
    const kind: ApiErrorKind =
      response.status === 404
        ? "not-found"
        : response.status === 401
          ? "unauthenticated"
          : response.status === 403
            ? "forbidden"
            : response.status === 409
              ? "conflict"
              : response.status === 422
                ? "rejected"
                : response.status === 503
                  ? "unavailable"
                  : "technical";
    throw new ApiError(kind, response.status);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export type ResourceView = {
  resourceRef: string;
  displayName: string;
  authorityScopeRef: string;
  version: number;
  current: {
    siteRef: string | null;
    endpoints: Array<{
      endpointRef: string;
      address: { kind: string; value: string } | null;
    }>;
    responsibilities: Array<{ role: string; organizationRef: string }>;
  };
  history: {
    sites: unknown[];
    endpointAddresses: unknown[];
    responsibilities: unknown[];
  };
};

export type PolicyRuleView = {
  policyRuleRef: string;
  version: number;
  effectState: "ACTIVE" | "INACTIVE";
  effectiveWindow: {
    effectiveFrom: string | null;
    effectiveUntil: string | null;
  };
  sourceDeploymentRef: string;
  destinationDeploymentRef: string;
  interactionRevisionRef: string;
  authorizationEvidence: Array<Record<string, unknown>>;
  justifications: Array<Record<string, unknown>>;
  operationalHistory: Array<Record<string, unknown>>;
};

export type AccessRequestView = {
  requestRef: string;
  version: number;
  sourceDeploymentRef: string;
  destinationDeploymentRef: string;
  interactionRevisionRef: string;
  needRef: string;
  submittedAt: string;
  decisionResult: "ALLOWED" | "DENIED" | null;
  externalDecisionRef?: string | null;
  decidedBySubject?: string | null;
  decidedAt?: string | null;
};

export type AccessRequestResult = {
  requestRef: string;
  version: number;
  result?: "ALLOWED" | "DENIED" | null;
  policyRuleRef?: string | null;
};

export type TrafficClauseView = {
  ipProtocol: number;
  sourcePorts: Array<{ from: number; to: number }>;
  destinationPorts: Array<{ from: number; to: number }>;
};

export type InteractionView = {
  interactionRef: string;
  sourceComponentRef: string;
  destinationComponentRef: string;
  purpose: string | null;
  version: number;
  revisions: Array<{
    interactionRevisionRef: string;
    revisionNo: number;
    trafficClauses: TrafficClauseView[];
    createdBySubject: string;
  }>;
};

export type ApplicationView = {
  applicationRef: string;
  name: string;
  version: number;
  components: Array<{ componentRef: string; name: string }>;
  interactions?: InteractionView[];
};
export type DeploymentView = {
  deploymentRef: string;
  componentRef: string;
  resourceRef: string;
};
export type ProcessView = {
  processRef: string;
  name: string;
  description: string | null;
  criticalityLabel: string | null;
  version: number;
  needs: Array<{
    needRef: string;
    interactionRef: string;
    participantComponentRef: string;
    businessBasis: string;
    status: string;
  }>;
};

export const api = {
  listResources: () => request<ResourceView[]>("/v1/resources"),
  getResource: (ref: string) => request<ResourceView>(`/v1/resources/${ref}`),
  createResource: (body: {
    displayName: string;
    authorityScopeRef: string;
    siteRef?: string;
  }) =>
    request<ResourceView>("/v1/resources", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  listAccessRequests: () => request<AccessRequestView[]>("/v1/access-requests"),
  getAccessRequest: (ref: string) =>
    request<AccessRequestView>(`/v1/access-requests/${ref}`),
  addResourceEndpoint: (ref: string, version: number) =>
    request<ResourceView>(`/v1/resources/${ref}/endpoints`, {
      method: "POST",
      headers: { "If-Match": String(version) },
    }),
  setResourceSite: (ref: string, version: number, siteRef: string | null) =>
    request<ResourceView>(`/v1/resources/${ref}/site`, {
      method: "PUT",
      headers: { "If-Match": String(version) },
      body: JSON.stringify({ siteRef }),
    }),
  setResourceAddress: (
    ref: string,
    endpointRef: string,
    version: number,
    address: { kind: string; value: string },
  ) =>
    request<ResourceView>(
      `/v1/resources/${ref}/endpoints/${endpointRef}/address`,
      {
        method: "PUT",
        headers: { "If-Match": String(version) },
        body: JSON.stringify(address),
      },
    ),
  setResourceResponsibility: (
    ref: string,
    role: string,
    version: number,
    organizationRef: string | null,
  ) =>
    request<ResourceView>(`/v1/resources/${ref}/responsibilities/${role}`, {
      method: "PUT",
      headers: { "If-Match": String(version) },
      body: JSON.stringify({ organizationRef }),
    }),
  submitAccessRequest: (body: {
    sourceDeploymentRef: string;
    destinationDeploymentRef: string;
    interactionRevisionRef: string;
    needRef: string;
  }) =>
    request<AccessRequestResult>("/v1/access-requests", {
      method: "POST",
      headers: { "Idempotency-Key": crypto.randomUUID() },
      body: JSON.stringify(body),
    }),
  listApplications: () => request<ApplicationView[]>("/v1/applications"),
  getApplication: (ref: string) =>
    request<ApplicationView>(`/v1/applications/${ref}`),
  createApplication: (name: string) =>
    request<{ applicationRef: string; version: number }>("/v1/applications", {
      method: "POST",
      body: JSON.stringify({ name }),
    }),
  addComponent: (applicationRef: string, version: number, name: string) =>
    request<{ applicationRef: string; componentRef: string; version: number }>(
      `/v1/applications/${applicationRef}/components`,
      {
        method: "POST",
        headers: { "If-Match": String(version) },
        body: JSON.stringify({ name }),
      },
    ),
  createInteraction: (body: {
    sourceComponentRef: string;
    destinationComponentRef: string;
    purpose?: string;
  }) =>
    request<{ interactionRef: string; version: number }>("/v1/interactions", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  publishRevision: (
    interactionRef: string,
    version: number,
    trafficClauses: Array<{
      ipProtocol: number;
      sourcePorts?: Array<{ from: number; to: number }>;
      destinationPorts?: Array<{ from: number; to: number }>;
    }>,
  ) =>
    request<{
      interactionRef: string;
      interactionRevisionRef: string;
      version: number;
    }>(`/v1/interactions/${interactionRef}/revisions`, {
      method: "POST",
      headers: { "If-Match": String(version) },
      body: JSON.stringify({ trafficClauses }),
    }),
  listDeployments: () => request<DeploymentView[]>("/v1/deployments"),
  createDeployment: (componentRef: string, resourceRef: string) =>
    request<{
      deploymentRef: string;
      componentRef: string;
      resourceRef: string;
    }>("/v1/deployments", {
      method: "POST",
      body: JSON.stringify({ componentRef, resourceRef }),
    }),
  listProcesses: () => request<ProcessView[]>("/v1/processes"),
  getProcess: async (ref: string) => {
    const items = await request<ProcessView[]>("/v1/processes");
    const value = items.find((item) => item.processRef === ref);
    if (!value) throw new ApiError("not-found", 404);
    return value;
  },
  createProcess: (body: {
    name: string;
    description?: string;
    criticalityLabel?: string;
  }) =>
    request<{ processRef: string; version: number }>("/v1/processes", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  declareNeed: (
    processRef: string,
    version: number,
    body: {
      interactionRef: string;
      participantComponentRef: string;
      businessBasis: string;
    },
  ) =>
    request<{ processRef: string; needRef: string; version: number }>(
      `/v1/processes/${processRef}/needs`,
      {
        method: "POST",
        headers: { "If-Match": String(version) },
        body: JSON.stringify(body),
      },
    ),
  listPolicyRules: () => request<PolicyRuleView[]>("/v1/policy-rules"),
  getPolicyRule: (ref: string) =>
    request<PolicyRuleView>(`/v1/policy-rules/${ref}`),
  setPolicyRuleState: (
    ref: string,
    version: number,
    effectState: "ACTIVE" | "INACTIVE",
  ) =>
    request<{ policyRuleRef: string; version: number }>(
      `/v1/policy-rules/${ref}/operational-state`,
      {
        method: "PUT",
        headers: { "If-Match": String(version) },
        body: JSON.stringify({ effectState, effectiveWindow: null }),
      },
    ),
  decideAccessRequest: (
    ref: string,
    version: number,
    result: "ALLOWED" | "DENIED",
    externalDecisionRef?: string,
  ) =>
    request<{
      requestRef: string;
      version: number;
      result: "ALLOWED" | "DENIED";
      policyRuleRef?: string | null;
    }>(`/v1/access-requests/${ref}/decision`, {
      method: "POST",
      headers: {
        "If-Match": String(version),
        "Idempotency-Key": crypto.randomUUID(),
      },
      body: JSON.stringify({
        result,
        ...(externalDecisionRef ? { externalDecisionRef } : {}),
      }),
    }),
  materialize: (policyRuleRefs?: string[]) =>
    request<Record<string, unknown>>("/v1/policy-materializations", {
      method: "POST",
      body: JSON.stringify(policyRuleRefs ? { policyRuleRefs } : {}),
    }),
};
