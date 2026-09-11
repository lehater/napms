import { useState } from "react"

import { Button } from "@/design-system/components/Button"
import { Input } from "@/design-system/components/Field"
import { Surface } from "@/design-system/primitives/Surface"
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
import { DependencyBlockPanel } from "@/features/catalogues/components/DependencyBlockPanel"

function messageFrom(caught: unknown, fallback: string) {
  return caught instanceof Error ? caught.message : fallback
}

function blockersFrom(caught: unknown): DependencyGroupDto[] | null {
  return caught instanceof TargetCatalogueApiError && caught.code === "CatalogueDependencyBlocked"
    ? (caught.details?.dependencies ?? [])
    : null
}

function EditorActions({
  confirmLabel,
  confirming,
  retiring,
  saving,
  canSave,
  onStartRetire,
  onCancelRetire,
  onRetire,
  onCancel,
  onSave,
}: {
  confirmLabel: string
  confirming: boolean
  retiring: boolean
  saving: boolean
  canSave: boolean
  onStartRetire: () => void
  onCancelRetire: () => void
  onRetire: () => void
  onCancel: () => void
  onSave: () => void
}) {
  return (
    <div className="flex flex-wrap justify-between gap-2">
      {confirming ? (
        <div className="flex items-center gap-2">
          <span className="text-sm text-[var(--napms-color-text-secondary)]">{confirmLabel}</span>
          <Button variant="secondary" size="sm" onClick={onCancelRetire}>Cancel</Button>
          <Button size="sm" loading={retiring} onClick={onRetire}>Retire</Button>
        </div>
      ) : <Button variant="ghost" size="sm" onClick={onStartRetire}>Retire</Button>}
      <div className="flex gap-2">
        <Button variant="secondary" size="sm" onClick={onCancel}>Close</Button>
        <Button size="sm" loading={saving} disabled={!canSave} onClick={onSave}>Save</Button>
      </div>
    </div>
  )
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
      onChanged(await updateApplicationDefinition(definition, {
        displayName: displayName.trim(),
        domain: domain.trim() || null,
        ownerReference: ownerReference.trim() || null,
        description: description.trim() || null,
      }))
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
    <Surface className="p-5">
      <div className="grid gap-4">
        <div className="grid gap-3 md:grid-cols-2">
          <Input value={displayName} onChange={(event) => setDisplayName(event.target.value)} placeholder="Name" aria-label="Application name" />
          <Input value={domain} onChange={(event) => setDomain(event.target.value)} placeholder="Domain" aria-label="Application domain" />
          <Input value={ownerReference} onChange={(event) => setOwnerReference(event.target.value)} placeholder="Owner" aria-label="Application owner" />
          <Input value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Description" aria-label="Application description" />
        </div>
        {error ? <div className="text-sm text-[var(--napms-color-danger)]">{error}</div> : null}
        {blockers ? <DependencyBlockPanel groups={blockers} subjectKind="application-definition" subjectId={definition.applicationId} onClose={() => setBlockers(null)} /> : null}
        <EditorActions confirmLabel="Retire this Definition?" confirming={confirmRetire} retiring={retiring} saving={saving} canSave={Boolean(displayName.trim())} onStartRetire={() => setConfirmRetire(true)} onCancelRetire={() => setConfirmRetire(false)} onRetire={() => void retire()} onCancel={onCancel} onSave={() => void save()} />
      </div>
    </Surface>
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
      onChanged(await updateApplicationComponent(component, {
        displayName: displayName.trim(),
        componentType: componentType.trim() || null,
        description: description.trim() || null,
      }))
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
    <div className="my-3 grid gap-3 rounded-[var(--napms-control-radius)] bg-[var(--napms-color-surface-subtle)] p-4">
      <div className="grid gap-2 md:grid-cols-3">
        <Input value={displayName} onChange={(event) => setDisplayName(event.target.value)} placeholder="Name" aria-label="Component name" />
        <Input value={componentType} onChange={(event) => setComponentType(event.target.value)} placeholder="Type" aria-label="Component type" />
        <Input value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Description" aria-label="Component description" />
      </div>
      {error ? <div className="text-sm text-[var(--napms-color-danger)]">{error}</div> : null}
      {blockers ? <DependencyBlockPanel groups={blockers} subjectKind="component" subjectId={component.componentId} onClose={() => setBlockers(null)} /> : null}
      <EditorActions confirmLabel="Retire Component?" confirming={confirmRetire} retiring={retiring} saving={saving} canSave={Boolean(displayName.trim())} onStartRetire={() => setConfirmRetire(true)} onCancelRetire={() => setConfirmRetire(false)} onRetire={() => void retire()} onCancel={onCancel} onSave={() => void save()} />
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
      onChanged(await updateApplicationDeployment(deployment, {
        companyReference: companyReference.trim(),
        environment: environment.trim(),
        scopeReference: scopeReference.trim(),
      }))
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

  const canSave = Boolean(companyReference.trim() && environment.trim() && scopeReference.trim())

  return (
    <Surface className="p-5">
      <div className="grid gap-3">
        <div className="grid gap-2 md:grid-cols-3">
          <Input value={companyReference} onChange={(event) => setCompanyReference(event.target.value)} placeholder="Company" aria-label="Company" />
          <Input value={environment} onChange={(event) => setEnvironment(event.target.value)} placeholder="Environment" aria-label="Environment" />
          <Input value={scopeReference} onChange={(event) => setScopeReference(event.target.value)} placeholder="Scope" aria-label="Scope" />
        </div>
        {error ? <div className="text-sm text-[var(--napms-color-danger)]">{error}</div> : null}
        {blockers ? <DependencyBlockPanel groups={blockers} subjectKind="application-deployment" subjectId={deployment.applicationDeploymentId} onClose={() => setBlockers(null)} /> : null}
        <EditorActions confirmLabel="Retire Deployment?" confirming={confirmRetire} retiring={retiring} saving={saving} canSave={canSave} onStartRetire={() => setConfirmRetire(true)} onCancelRetire={() => setConfirmRetire(false)} onRetire={() => void retire()} onCancel={onCancel} onSave={() => void save()} />
      </div>
    </Surface>
  )
}
