import { ResourceCatalogueScreen } from "./ResourceCatalogueScreen";
import { ResourceDetailScreen } from "./ResourceDetailScreen";

export function ResourceCatalogue({ create = false }: { create?: boolean }) {
  return <ResourceCatalogueScreen create={create} />;
}

export function ResourceDetail({ resourceRef }: { resourceRef: string }) {
  return <ResourceDetailScreen resourceRef={resourceRef} />;
}
