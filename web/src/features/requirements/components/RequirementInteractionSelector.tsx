import { Search } from "lucide-react"

import { Field, Select } from "@/design-system/components/Field"
import {
  catalogueDcsLabel,
  catalogueOptionLabel,
} from "@/features/catalogues/components/CatalogueInteractionSelector"
import type { ProposalInteraction } from "@/features/catalogues/model/interaction"

export function RequirementInteractionSelector({
  scope,
  scopes,
  loadingScopes,
  onScopeChange,
  searchInput,
  onSearchInputChange,
  loadingInteractions,
  source,
  sourceOptions,
  onSourceChange,
  destination,
  destinationOptions,
  onDestinationChange,
  dcs,
  dcsOptions,
  onDcsChange,
  dependent,
  selectedInteraction,
  onDependentChange,
}: {
  scope: string
  scopes: string[]
  loadingScopes: boolean
  onScopeChange: (value: string) => void
  searchInput: string
  onSearchInputChange: (value: string) => void
  loadingInteractions: boolean
  source: string
  sourceOptions: Array<[string, string | null | undefined]>
  onSourceChange: (value: string) => void
  destination: string
  destinationOptions: Array<[string, string | null | undefined]>
  onDestinationChange: (value: string) => void
  dcs: string
  dcsOptions: ProposalInteraction[]
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

      <Field label="Search required interaction">
        <div className="relative">
          <Search
            className="pointer-events-none absolute left-3 top-3 size-4 text-[#94A3B8]"
            aria-hidden="true"
          />
          <input
            type="search"
            value={searchInput}
            maxLength={256}
            onChange={(event) => onSearchInputChange(event.target.value)}
            disabled={!scope}
            placeholder="Orders, Checkout, HTTPS…"
            className="min-h-10 w-full rounded-md border border-[#CBD5E1] py-2 pl-9 pr-3 text-sm disabled:bg-[#F8FAFC]"
          />
        </div>
      </Field>

      <Field label="Source Component Deployment">
        <Select
          value={source}
          onChange={(event) => onSourceChange(event.target.value)}
          disabled={!scope || loadingInteractions}
          required
        >
          <option value="">Select source</option>
          {sourceOptions.map(([id, name]) => (
            <option key={id} value={id}>{catalogueOptionLabel(name, id)}</option>
          ))}
        </Select>
      </Field>

      <Field label="Destination Component Deployment">
        <Select
          value={destination}
          onChange={(event) => onDestinationChange(event.target.value)}
          disabled={!source}
          required
        >
          <option value="">Select destination</option>
          {destinationOptions.map(([id, name]) => (
            <option key={id} value={id}>{catalogueOptionLabel(name, id)}</option>
          ))}
        </Select>
      </Field>

      <Field label="Directed Communication Specification">
        <Select
          value={dcs}
          onChange={(event) => onDcsChange(event.target.value)}
          disabled={!destination}
          required
        >
          <option value="">Select DCS</option>
          {dcsOptions.map((item) => (
            <option
              key={item.dcsContractRevisionId}
              value={item.dcsContractRevisionId}
            >
              {catalogueDcsLabel(item)}
            </option>
          ))}
        </Select>
      </Field>

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
