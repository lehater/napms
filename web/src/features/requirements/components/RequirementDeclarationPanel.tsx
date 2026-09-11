import { useEffect, useMemo, useState } from "react"
import { Plus } from "lucide-react"

import { Alert } from "@/design-system/components/Alert"
import { Button } from "@/design-system/components/Button"
import type { ProposalInteraction } from "@/features/catalogues/model/interaction"
import {
  declareConnectivityRequirement,
  listConnectivityRequirementInteractions,
  listConnectivityRequirementScopes,
  type RequirementApplicability,
} from "@/features/requirements/api"
import { RequirementApplicabilityFields } from "@/features/requirements/components/RequirementApplicabilityFields"
import { RequirementInteractionSelector } from "@/features/requirements/components/RequirementInteractionSelector"
import { ApiError } from "@/lib/api"
import { toOffsetAwareIso } from "@/lib/datetime"
import { useDebouncedValue } from "@/lib/useDebouncedValue"

export function RequirementDeclarationPanel({ onDeclared }: { onDeclared: () => Promise<void> }) {
  const [scopes, setScopes] = useState<string[]>([])
  const [ambiguousDeclareScopes, setAmbiguousDeclareScopes] = useState<string[]>([])
  const [scope, setScope] = useState("")
  const [interactions, setInteractions] = useState<ProposalInteraction[]>([])
  const [interactionPage, setInteractionPage] = useState(1)
  const [hasMoreInteractions, setHasMoreInteractions] = useState(false)
  const [searchInput, setSearchInput] = useState("")
  const search = useDebouncedValue(searchInput.trim(), 300)
  const [source, setSource] = useState("")
  const [destination, setDestination] = useState("")
  const [dcs, setDcs] = useState("")
  const [dependent, setDependent] = useState("")
  const [applicabilityKind, setApplicabilityKind] = useState<"Ongoing" | "AbsoluteWindow">("Ongoing")
  const [windowStart, setWindowStart] = useState("")
  const [windowEnd, setWindowEnd] = useState("")
  const [justification, setJustification] = useState("")
  const [loadingScopes, setLoadingScopes] = useState(true)
  const [loadingInteractions, setLoadingInteractions] = useState(false)
  const [declaring, setDeclaring] = useState(false)
  const [declareError, setDeclareError] = useState<ApiError | null>(null)
  const [declareMessage, setDeclareMessage] = useState<string | null>(null)

  useEffect(() => {
    let active = true
    setLoadingScopes(true)
    void listConnectivityRequirementScopes()
      .then((result) => {
        if (!active) return
        const values = result.scopes.map((item) => item.scope)
        setScopes(values)
        setAmbiguousDeclareScopes(result.ambiguousScopes.map((item) => item.scope))
        if (values.length === 1) setScope(values[0])
      })
      .catch((caught) => {
        if (!active) return
        setDeclareError(caught instanceof ApiError ? caught : new ApiError(500, "InternalError", "Declaration scopes could not be loaded."))
      })
      .finally(() => { if (active) setLoadingScopes(false) })
    return () => { active = false }
  }, [])

  useEffect(() => { setInteractionPage(1) }, [search])

  useEffect(() => {
    setInteractions([])
    setHasMoreInteractions(false)
    setSource("")
    setDestination("")
    setDcs("")
    setDependent("")
    if (!scope) return
    let active = true
    setLoadingInteractions(true)
    setDeclareError(null)
    void listConnectivityRequirementInteractions(scope, interactionPage, search)
      .then((result) => {
        if (!active) return
        setInteractions(result.items)
        setHasMoreInteractions(result.hasMore)
      })
      .catch((caught) => {
        if (!active) return
        setDeclareError(caught instanceof ApiError ? caught : new ApiError(500, "InternalError", "Required interactions could not be loaded."))
      })
      .finally(() => { if (active) setLoadingInteractions(false) })
    return () => { active = false }
  }, [scope, interactionPage, search])

  const sourceOptions = useMemo(() => {
    const values = new Map<string, string | null | undefined>()
    for (const item of interactions) if (!values.has(item.sourceComponentDeploymentId)) values.set(item.sourceComponentDeploymentId, item.catalogue?.sourceDisplayName)
    return [...values.entries()]
  }, [interactions])
  const destinationOptions = useMemo(() => {
    const values = new Map<string, string | null | undefined>()
    for (const item of interactions) if (item.sourceComponentDeploymentId === source && !values.has(item.destinationComponentDeploymentId)) values.set(item.destinationComponentDeploymentId, item.catalogue?.destinationDisplayName)
    return [...values.entries()]
  }, [interactions, source])
  const dcsOptions = useMemo(() => interactions.filter((item) => item.sourceComponentDeploymentId === source && item.destinationComponentDeploymentId === destination), [interactions, source, destination])
  const selectedInteraction = dcsOptions.find((item) => item.dcsContractRevisionId === dcs) ?? null

  function resetDeclaration() {
    setSource(""); setDestination(""); setDcs(""); setDependent("")
    setApplicabilityKind("Ongoing"); setWindowStart(""); setWindowEnd(""); setJustification("")
  }

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    if (!scope || !source || !destination || !dcs || !dependent) return
    let applicability: RequirementApplicability
    try {
      applicability = applicabilityKind === "Ongoing" ? { kind: "Ongoing" } : { kind: "AbsoluteWindow", start: toOffsetAwareIso(windowStart), end: toOffsetAwareIso(windowEnd) }
    } catch {
      setDeclareError(new ApiError(422, "InvalidRequirementApplicability", "Select a valid applicability start and end.")); return
    }
    setDeclaring(true); setDeclareError(null); setDeclareMessage(null)
    try {
      const result = await declareConnectivityRequirement({ authorityScope: scope, dependentComponentDeploymentId: dependent, sourceComponentDeploymentId: source, destinationComponentDeploymentId: destination, dcsContractRevisionId: dcs, applicability, justification })
      setDeclareMessage(result.outcome === "Declared" ? "Connectivity Requirement declared." : "The same Active connectivity need already exists; existing Requirement resolved.")
      resetDeclaration()
      await onDeclared()
    } catch (caught) {
      setDeclareError(caught instanceof ApiError ? caught : new ApiError(500, "InternalError", "Connectivity Requirement could not be declared."))
    } finally { setDeclaring(false) }
  }

  return (
    <form onSubmit={submit} className="self-start rounded-[var(--napms-surface-radius)] border border-[var(--napms-color-border)] bg-[var(--napms-color-surface)] p-5 shadow-[var(--napms-surface-shadow)]">
      <div className="mb-5 flex items-center gap-2"><Plus className="size-4 text-[var(--napms-color-primary)]" aria-hidden="true" /><h2 className="text-base font-semibold text-[var(--napms-color-text-primary)]">Declare Connectivity Requirement</h2></div>
      <div className="grid gap-4">
        <RequirementInteractionSelector
          scope={scope} scopes={scopes} loadingScopes={loadingScopes}
          onScopeChange={(value) => { setScope(value); setInteractionPage(1) }}
          searchInput={searchInput} onSearchInputChange={setSearchInput} loadingInteractions={loadingInteractions}
          source={source} sourceOptions={sourceOptions}
          onSourceChange={(value) => { setSource(value); setDestination(""); setDcs(""); setDependent("") }}
          destination={destination} destinationOptions={destinationOptions}
          onDestinationChange={(value) => { setDestination(value); setDcs(""); setDependent("") }}
          dcs={dcs} dcsOptions={dcsOptions}
          onDcsChange={(value) => { setDcs(value); setDependent("") }}
          dependent={dependent} selectedInteraction={selectedInteraction} onDependentChange={setDependent}
        />
        <RequirementApplicabilityFields kind={applicabilityKind} onKindChange={setApplicabilityKind} windowStart={windowStart} onWindowStartChange={setWindowStart} windowEnd={windowEnd} onWindowEndChange={setWindowEnd} justification={justification} onJustificationChange={setJustification} />
        <div className="flex items-center justify-between rounded-[var(--napms-control-radius)] border border-[var(--napms-color-border)] bg-[var(--napms-color-surface-subtle)] px-3 py-2">
          <span className="text-xs text-[var(--napms-color-text-secondary)]">Interaction page {interactionPage}</span>
          <div className="flex gap-2"><Button type="button" variant="secondary" disabled={interactionPage === 1 || loadingInteractions} onClick={() => setInteractionPage((value) => Math.max(1, value - 1))}>Previous</Button><Button type="button" variant="secondary" disabled={!hasMoreInteractions || loadingInteractions} onClick={() => setInteractionPage((value) => value + 1)}>Next</Button></div>
        </div>
        {ambiguousDeclareScopes.length > 0 ? <Alert tone="warning">{ambiguousDeclareScopes.length} declaration scope(s) remain fail-closed because authority is ambiguous.</Alert> : null}
        {declareError ? <Alert role="alert" tone="danger"><div className="font-semibold">{declareError.code}</div><div className="mt-1">{declareError.message}</div></Alert> : null}
        {declareMessage ? <Alert role="status" tone="success">{declareMessage}</Alert> : null}
        <Button type="submit" loading={declaring} disabled={!scope || !source || !destination || !dcs || !dependent || !justification.trim() || (applicabilityKind === "AbsoluteWindow" && (!windowStart || !windowEnd))}>Declare Requirement</Button>
      </div>
    </form>
  )
}
