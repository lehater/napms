import type { ResourceView } from "../../app/api";

export type ResourceDetailScreenModel = {
  resourceRef: string;
  displayName: string;
  authorityScopeRef: string;
  version: number;
  siteRef: string | null;
  endpoints: readonly {
    endpointRef: string;
    addressSummary: string;
  }[];
  responsibilities: readonly {
    role: string;
    organizationRef: string;
  }[];
  history: ResourceView["history"];
};

export function toResourceDetailScreenModel(
  resource: ResourceView,
): ResourceDetailScreenModel {
  return {
    resourceRef: resource.resourceRef,
    displayName: resource.displayName,
    authorityScopeRef: resource.authorityScopeRef,
    version: resource.version,
    siteRef: resource.current.siteRef,
    endpoints: resource.current.endpoints.map((endpoint) => ({
      endpointRef: endpoint.endpointRef,
      addressSummary: endpoint.address
        ? `${endpoint.address.kind} ${endpoint.address.value}`
        : "No address",
    })),
    responsibilities: resource.current.responsibilities.map((item) => ({
      role: item.role,
      organizationRef: item.organizationRef,
    })),
    history: resource.history,
  };
}

export function hasEmptyCurrent(model: ResourceDetailScreenModel): boolean {
  return (
    model.siteRef === null ||
    model.endpoints.length === 0 ||
    model.responsibilities.length === 0
  );
}
