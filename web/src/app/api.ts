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
  materialize: (policyRuleRefs?: string[]) =>
    request<Record<string, unknown>>("/v1/policy-materializations", {
      method: "POST",
      body: JSON.stringify(policyRuleRefs ? { policyRuleRefs } : {}),
    }),
};
