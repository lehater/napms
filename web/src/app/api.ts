export type ApiErrorKind =
  | "not-found"
  | "rejected"
  | "conflict"
  | "unauthorized"
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

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: { "Content-Type": "application/json", ...init.headers },
  });
  if (!response.ok) {
    const kind: ApiErrorKind =
      response.status === 404
        ? "not-found"
        : response.status === 401 || response.status === 403
          ? "unauthorized"
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
};

export type AccessRequestResult = {
  requestRef: string;
  version: number;
  result?: "ALLOWED" | "DENIED" | null;
  policyRuleRef?: string | null;
};

export const api = {
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
  materialize: (policyRuleRefs?: string[]) =>
    request<Record<string, unknown>>("/v1/policy-materializations", {
      method: "POST",
      body: JSON.stringify(policyRuleRefs ? { policyRuleRefs } : {}),
    }),
};
