import { useState } from "react"

import { Button } from "@/components/ui/Button"
import { DependencyBlockPanel } from "@/features/catalogues/components/DependencyBlockPanel"
import {
  retireApplicationComponent,
  retireApplicationDefinition,
  retireApplicationDeployment,
  TargetCatalogueApiError,
  updateApplicationComponent,
  updateApplicationDefinition,
  updateApplicationDeployment,
  type DependencyGroupDto,
} from "@/features/catalogues/api/targetCommands"
import type {
  ApplicationComponentDto,
  ApplicationDefinitionDto,
  ApplicationDeploymentDto,
} from "@/features/catalogues/api/targetCatalogue"

const inputClass =
  "min-h-10 w-full rounded-md border border-[#CBD5E1] bg-white px-3 py-2 text-sm text-[#172033] outline-none focus:border-[#2563EB] focus:ring-2 focus:ring-[#DBEAFE]"

function messageFrom(caught: unknown, fallback: string) {
  return caught instanceof Error ? caught.message : fallback
}

function blockersFrom(caught: unknown): DependencyGroupDto[] | null {
  return caught instanceof TargetCatalogueApiError && caught.code === "CatalogueDependencyBlocked"
    ? (caught.details?.dependencies ?? [])
    : null
}

export function DefinitionEditPanel({
  definition,
  onChanged,
  onRetired,
  onCancel,
}: {
  definition: ApplicationDefinitionDto
  onChanged: (definition: ApplicationDefinitionDto) => void
  onRetired: () => void
  onCancel: () => void
}) {
  const [displayName, setDisplayName] = useState(definition.displayName)
  const [domain, setDomain] = useState(definition.domain ?? "")
  const [ownerReference, setOwnerReference] = useState(definition.ownerReference ?? "")
  const [description, setDescription] = useState(definition.description ?? "")
  const [saving, setSaving] = useState(false)
  const [retiring, setRetiring] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [blockers, setBlockers] = useState<DependencyGroupDto[] | null>(null)
  const [confirmRetire, setConfirmRetire] = useState(false)

  async function save() {
    if (!displayName.trim()) return
    setSaving(true)
    setError(null)
    try {
      const updated = await updateApplicationDefinition(definition, {
        displayName: displayName.trim(),
        domain: domain.trim() || null,
        ownerReference: ownerReference.trim() || null,
        description: description.trim() || null,
      })
      onChanged(updated)
    } catch (caught) {
      setError(messageFrom(caught, "Application Definition could not be updated."))
    } finally {
      setSaving(false)
    }
  }

  async function retire() {
    setRetiring(true)
    setError(null)
    setBlockers(null)
    try {
      await retireApplicationDefinition(definition)
      onRetired()
    } catch (caught) {
      const groups = blockersFrom(caught)
      if (groups) setBlockers(groups)
      else setError(messageFrom(caught, "Application Definition could not be retired."))
    } finally {
      setRetiring(false)
      setConfirmRetire(false)
    }
  }

  return (
    <div className="grid gap-4 rounded-lg border border-[#E2E8F0] bg-white p-5 shadow-sm">
      <div className="grid gap-3 md:grid-cols-2">
        <input className={inputClass} value={displayName} onChange={(event) => setDisplayName(event.target.value)} placeholder="Name" aria-label="Application name" />
        <input className={inputClass} value={domain} onChange={(event) => setDomain(event.target.value)} placeholder="Domain" aria-label="Application domain" />
        <input className={inputClass} value={ownerReference} onChange={(event) => setOwnerReference(event.target.value)} placeholder="Owner" aria-label="Application owner" />
        <input className={inputClass} value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Description" aria-label="Application description" />
      </div>
      {error ? <div className="text-sm text-red-700">{error}</div> : null}
      {blockers ? (
        <DependencyBlockPanel groups={blockers} subjectKind="application-definition" subjectId={definition.applicationId} onClose={() => setBlockers(null)} />
      ) : null}
      <div className="flex flex-wrap justify-between gap-2">
        <div>
          {confirmRetire ? (
            <div className="flex items-center gap-2">
              <span className="text-sm text-[#64748B]">Retire this Definition?</span>
              <Button variant="secondary" onClick={() => setConfirmRetire(false)}>Cancel</Button>
              <Button loading={retiring} onClick={() => void retire()}>Retire</Button>
            </div>
          ) : (
            <Button variant="ghost" onClick={() => setConfirmRetire(true)}>Retire</Button>
          )}
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={onCancel}>Close</Button>
          <Button loading={saving} disabled={!displayName.trim()} onClick={() => void save()}>Save</Button>
        </div>
      </div>
    </div>
  )
}

export function ComponentEditPanel({
  component,
  onChanged,
  onRetired,
  onCancel,
}: {
  component: ApplicationComponentDto
  onChanged: (component: ApplicationComponentDto) => void
  onRetired: () => void
  onCancel: () => void
}) {
  const [displayName, setDisplayName] = useState(component.displayName)
  const [componentType, setComponentType] = useState(component.componentType ?? "")
  const [description, setDescription] = useState(component.description ?? "")
  const [saving, setSaving] = useState(false)
  const [retiring, setRetiring] = useState(false)
  const [confirmRetire, setConfirmRetire] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [blockers, setBlockers] = useState<DependencyGroupDto[] | null>(null)

  async function save() {
    if (!displayName.trim()) return
    setSaving(true)
    setError(null)
    try {
      const updated = await updateApplicationComponent(component, {
        displayName: displayName.trim(),
        componentType: componentType.trim() || null,
        description: description.trim() || null,
      })
      onChanged(updated)
    } catch (caught) {
      setError(messageFrom(caught, "Component could not be updated."))
    } finally {
      setSaving(false)
    }
  }

  async function retire() {
    setRetiring(true)
    setError(null)
    setBlockers(null)
    try {
      await retireApplicationComponent(component)
      onRetired()
    } catch (caught) {
      const groups = blockersFrom(caught)
      if (groups) setBlockers(groups)
      else setError(messageFrom(caught, "Component could not be retired."))
    } finally {
      setRetiring(false)
      setConfirmRetire(false)
    }
  }

  return (
    <div className="grid gap-3 border-b border-[#E2E8F0] bg-[#F8FAFC] p-4">
      <div className="grid gap-2 md:grid-cols-3">
        <input className={inputClass} value={displayName} onChange={(event) => setDisplayName(event.target.value)} placeholder="Name" aria-label="Component name" />
        <input className={inputClass} value={componentType} onChange={(event) => setComponentType(event.target.value)} placeholder="Type" aria-label="Component type" />
        <input className={inputClass} value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Description" aria-label="Component description" />
      </div>
      {error ? <div className="text-sm text-red-700">{error}</div> : null}
      {blockers ? <DependencyBlockPanel groups={blockers} subjectKind="component" subjectId={component.componentId} onClose={() => setBlockers(null)} /> : null}
      <div className="flex flex-wrap justify-between gap-2">
        {confirmRetire ? (
          <div className="flex items-center gap-2"><span className="text-sm text-[#64748B]">Retire Component?</span><Button variant="secondary" onClick={() => setConfirmRetire(false)}>Cancel</Button><Button loading={retiring} onClick={() => void retire()}>Retire</Button></div>
        ) : <Button variant="ghost" onClick={() => setConfirmRetire(true)}>Retire</Button>}
        <div className="flex gap-2"><Button variant="secondary" onClick={onCancel}>Close</Button><Button loading={saving} disabled={!displayName.trim()} onClick={() => void save()}>Save</Button></div>
      </div>
    </div>
  )
}

export function DeploymentEditPanel({
  deployment,
  onChanged,
  onRetired,
  onCancel,
}: {
  deployment: ApplicationDeploymentDto
  onChanged: (deployment: ApplicationDeploymentDto) => void
  onRetired: () => void
  onCancel: () => void
}) {
  const [companyReference, setCompanyReference] = useState(deployment.companyReference)
  const [environment, setEnvironment] = useState(deployment.environment)
  const [scopeReference, setScopeReference] = useState(deployment.scopeReference)
  const [saving, setSaving] = useState(false)
  const [retiring, setRetiring] = useState(false)
  const [confirmRetire, setConfirmRetire] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [blockers, setBlockers] = useState<DependencyGroupDto[] | null>(null)

  async function save() {
    if (!companyReference.trim() || !environment.trim() || !scopeReference.trim()) return
    setSaving(true)
    setError(null)
    try {
      const updated = await updateApplicationDeployment(deployment, {
        companyReference: companyReference.trim(),
        environment: environment.trim(),
        scopeReference: scopeReference.trim(),
      })
      onChanged(updated)
    } catch (caught) {
      setError(messageFrom(caught, "Application Deployment could not be updated."))
    } finally {
      setSaving(false)
    }
  }

  async function retire() {
    setRetiring(true)
    setError(null)
    setBlockers(null)
    try {
      await retireApplicationDeployment(deployment)
      onRetired()
    } catch (caught) {
      const groups = blockersFrom(caught)
      if (groups) setBlockers(groups)
      else setError(messageFrom(caught, "Application Deployment could not be retired."))
    } finally {
      setRetiring(false)
      setConfirmRetire(false)
    }
  }

  return (
    <div className="grid gap-3 rounded-lg border border-[#E2E8F0] bg-white p-5 shadow-sm">
      <div className="grid gap-2 md:grid-cols-3">
        <input className={inputClass} value={companyReference} onChange={(event) => setCompanyReference(event.target.value)} placeholder="Company" aria-label="Company" />
        <input className={inputClass} value={environment} onChange={(event) => setEnvironment(event.target.value)} placeholder="Environment" aria-label="Environment" />
        <input className={inputClass} value={scopeReference} onChange={(event) => setScopeReference(event.target.value)} placeholder="Scope" aria-label="Scope" />
      </div>
      {error ? <div className="text-sm text-red-700">{error}</div> : null}
      {blockers ? <DependencyBlockPanel groups={blockers} subjectKind="application-deployment" subjectId={deployment.applicationDeploymentId} onClose={() => setBlockers(null)} /> : null}
      <div className="flex flex-wrap justify-between gap-2">
        {confirmRetire ? (
          <div className="flex items-center gap-2"><span className="text-sm text-[#64748B]">Retire Deployment?</span><Button variant="secondary" onClick={() => setConfirmRetire(false)}>Cancel</Button><Button loading={retiring} onClick={() => void retire()}>Retire</Button></div>
        ) : <Button variant="ghost" onClick={() => setConfirmRetire(true)}>Retire</Button>}
        <div className="flex gap-2"><Button variant="secondary" onClick={onCancel}>Close</Button><Button loading={saving} disabled={!companyReference.trim() || !environment.trim() || !scopeReference.trim()} onClick={() => void save()}>Save</Button></div>
      </div>
    </div>
  )
}
