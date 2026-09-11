import { Field, Select } from "@/design-system/components/Field"
import {
  CatalogueInteractionSelector,
  catalogueOptionLabel,
} from "@/features/catalogues/components/CatalogueInteractionSelector"
import type { ProposalInteraction } from "@/features/catalogues/model/interaction"

export function RequirementInteractionSelector({
  scope,
  scopes,
  loadingScopes,
  onScopeChange,
  interactions,
  searchInput,
  onSearchInputChange,
  loadingInteractions,
  source,
  onSourceChange,
  destination,
  onDestinationChange,
  dcs,
  onDcsChange,
  dependent,
  selectedInteraction,
  onDependentChange,
}: {
  scope: string
  scopes: string[]
  loadingScopes: boolean
  onScopeChange: (value: string) => void
  interactions: ProposalInteraction[]
  searchInput: string
  onSearchInputChange: (value: string) => void
  loadingInteractions: boolean
  source: string
  onSourceChange: (value: string) => void
  destination: string
  onDestinationChange: (value: string) => void
  dcs: string
  onDcsChange: (value: string) => void
  dependent: string
  selectedInteraction: ProposalInteraction | null
  onDependentChange: (value: string) => void
}) {
  return (
    <>
      <Field label="Requirement Governance Scope">
        <Select
          value={scope}
          onChange={(event) => onScopeChange(event.target.value)}
          disabled={loadingScopes}
          required
        >
          <option value="">
            {loadingScopes ? "Loading scopes…" : "Select scope"}
          </option>
          {scopes.map((value) => (
            <option key={value} value={value}>{value}</option>
          ))}
        </Select>
      </Field>

      <CatalogueInteractionSelector
        interactions={interactions}
        searchInput={searchInput}
        onSearchInputChange={onSearchInputChange}
        searchDisabled={!scope}
        searchLabel="Search required interaction"
        searchPlaceholder="Orders, Checkout, HTTPS…"
        loading={loadingInteractions}
        disabled={!scope}
        source={source}
        onSourceChange={onSourceChange}
        destination={destination}
        onDestinationChange={onDestinationChange}
        dcs={dcs}
        onDcsChange={onDcsChange}
      />

      <Field
        label="Dependent Component Deployment"
        hint="Whose operational/business concern requires this interaction?"
      >
        <Select
          value={dependent}
          onChange={(event) => onDependentChange(event.target.value)}
          disabled={!selectedInteraction}
          required
        >
          <option value="">Select dependent participant</option>
          {selectedInteraction ? (
            <>
              <option value={selectedInteraction.sourceComponentDeploymentId}>
                {catalogueOptionLabel(
                  selectedInteraction.catalogue?.sourceDisplayName,
                  selectedInteraction.sourceComponentDeploymentId,
                )}
              </option>
              {selectedInteraction.destinationComponentDeploymentId !==
              selectedInteraction.sourceComponentDeploymentId ? (
                <option value={selectedInteraction.destinationComponentDeploymentId}>
                  {catalogueOptionLabel(
                    selectedInteraction.catalogue?.destinationDisplayName,
                    selectedInteraction.destinationComponentDeploymentId,
                  )}
                </option>
              ) : null}
            </>
          ) : null}
        </Select>
      </Field>
    </>
  )
}
