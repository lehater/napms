import { ApplicationCatalogueScreen } from "./ApplicationCatalogueScreen";
import { ApplicationDetailScreen } from "./ApplicationDetailScreen";
import { InteractionAuthoringScreen } from "./InteractionAuthoringScreen";

export function ApplicationCatalogue({ create = false }: { create?: boolean }) {
  return <ApplicationCatalogueScreen create={create} />;
}

export function ApplicationDetail({
  applicationRef,
  createComponent = false,
}: {
  applicationRef: string;
  createComponent?: boolean;
}) {
  return (
    <ApplicationDetailScreen
      applicationRef={applicationRef}
      createComponent={createComponent}
    />
  );
}

export function InteractionAuthoring({
  interactionRef,
}: {
  interactionRef?: string;
}) {
  return <InteractionAuthoringScreen interactionRef={interactionRef} />;
}
