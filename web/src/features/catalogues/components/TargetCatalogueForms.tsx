import { useState } from "react"

import { Button } from "@/design-system/components/Button"
import { Field, Input } from "@/design-system/components/Field"
import { Surface } from "@/design-system/primitives/Surface"
import {
  createApplicationComponent,
  createApplicationDefinition,
  createApplicationDeployment,
  type ApplicationComponentDto,
  type ApplicationDefinitionDto,
  type ApplicationDeploymentDto,
} from "@/features/catalogues/api/targetCatalogue"
import { ApiError } from "@/lib/api"

function errorFrom(caught: unknown, fallback: string) {
  return caught instanceof ApiError
    ? caught
    : new ApiError(500, "InternalError", fallback)
}

function optional(value: string) {
  const normalized = value.trim()
  return normalized || undefined
}

function Actions({
  saving,
  canSave,
  onCancel,
}: {
  saving: boolean
  canSave: boolean
  onCancel: () => void
}) {
  return (
    <div className="flex justify-end gap-2">
      <Button type="button" variant="secondary" onClick={onCancel}>Cancel</Button>
      <Button type="submit" loading={saving} disabled={!canSave}>Create</Button>
    </div>
  )
}

export function CreateDefinitionPanel({
  onCreated,
  onCancel,
}: {
  onCreated: (definition: ApplicationDefinitionDto) => void
  onCancel: () => void
}) {
  const [name, setName] = useState("")
  const [domain, setDomain] = useState("")
  const [owner, setOwner] = useState("")
  const [description, setDescription] = useState("")
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<ApiError | null>(null)

  return (
    <Surface>
      <form
        className="grid gap-4 p-5"
        onSubmit={(event) => {
          event.preventDefault()
          if (!name.trim()) return
          setSaving(true)
          setError(null)
          void createApplicationDefinition({
            displayName: name.trim(),
            domain: optional(domain),
            ownerReference: optional(owner),
            description: optional(description),
          })
            .then(onCreated)
            .catch((caught) => setError(errorFrom(caught, "Application Definition could not be created.")))
            .finally(() => setSaving(false))
        }}
      >
        <div>
          <h2 className="font-semibold text-[var(--napms-color-text-primary)]">New application</h2>
          <p className="mt-1 text-sm text-[var(--napms-color-text-secondary)]">Create the Definition first; Components and Deployments can be added incrementally.</p>
        </div>
        <div className="grid gap-3 md:grid-cols-2">
          <Field label="Name"><Input value={name} onChange={(event) => setName(event.target.value)} maxLength={256} /></Field>
          <Field label="Domain"><Input value={domain} onChange={(event) => setDomain(event.target.value)} maxLength={256} /></Field>
          <Field label="Owner"><Input value={owner} onChange={(event) => setOwner(event.target.value)} maxLength={2048} /></Field>
          <Field label="Description"><Input value={description} onChange={(event) => setDescription(event.target.value)} maxLength={4096} /></Field>
        </div>
        {error ? <p className="text-sm text-[var(--napms-color-danger)]">{error.message}</p> : null}
        <Actions saving={saving} canSave={Boolean(name.trim())} onCancel={onCancel} />
      </form>
    </Surface>
  )
}

export function CreateComponentPanel({
  applicationId,
  onCreated,
  onCancel,
}: {
  applicationId: string
  onCreated: (component: ApplicationComponentDto) => void
  onCancel: () => void
}) {
  const [name, setName] = useState("")
  const [type, setType] = useState("")
  const [description, setDescription] = useState("")
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<ApiError | null>(null)

  return (
    <form
      className="my-3 grid gap-4 rounded-[var(--napms-control-radius)] bg-[var(--napms-color-surface-subtle)] p-4"
      onSubmit={(event) => {
        event.preventDefault()
        if (!name.trim()) return
        setSaving(true)
        setError(null)
        void createApplicationComponent(applicationId, {
          displayName: name.trim(),
          componentType: optional(type),
          description: optional(description),
        })
          .then(onCreated)
          .catch((caught) => setError(errorFrom(caught, "Component could not be created.")))
          .finally(() => setSaving(false))
      }}
    >
      <div className="grid gap-3 md:grid-cols-3">
        <Field label="Name"><Input value={name} onChange={(event) => setName(event.target.value)} maxLength={256} /></Field>
        <Field label="Type"><Input value={type} onChange={(event) => setType(event.target.value)} maxLength={256} /></Field>
        <Field label="Description"><Input value={description} onChange={(event) => setDescription(event.target.value)} maxLength={4096} /></Field>
      </div>
      {error ? <p className="text-sm text-[var(--napms-color-danger)]">{error.message}</p> : null}
      <Actions saving={saving} canSave={Boolean(name.trim())} onCancel={onCancel} />
    </form>
  )
}

export function CreateDeploymentPanel({
  applicationId,
  onCreated,
  onCancel,
}: {
  applicationId: string
  onCreated: (deployment: ApplicationDeploymentDto) => void
  onCancel: () => void
}) {
  const [company, setCompany] = useState("")
  const [environment, setEnvironment] = useState("")
  const [scope, setScope] = useState("")
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<ApiError | null>(null)
  const canSave = Boolean(company.trim() && environment.trim() && scope.trim())

  return (
    <form
      className="my-3 grid gap-4 rounded-[var(--napms-control-radius)] bg-[var(--napms-color-surface-subtle)] p-4"
      onSubmit={(event) => {
        event.preventDefault()
        if (!canSave) return
        setSaving(true)
        setError(null)
        void createApplicationDeployment({
          applicationId,
          companyReference: company.trim(),
          environment: environment.trim(),
          scopeReference: scope.trim(),
        })
          .then(onCreated)
          .catch((caught) => setError(errorFrom(caught, "Application Deployment could not be created.")))
          .finally(() => setSaving(false))
      }}
    >
      <div className="grid gap-3 md:grid-cols-3">
        <Field label="Company"><Input value={company} onChange={(event) => setCompany(event.target.value)} maxLength={2048} /></Field>
        <Field label="Environment"><Input value={environment} onChange={(event) => setEnvironment(event.target.value)} maxLength={256} /></Field>
        <Field label="Scope"><Input value={scope} onChange={(event) => setScope(event.target.value)} maxLength={2048} /></Field>
      </div>
      {error ? <p className="text-sm text-[var(--napms-color-danger)]">{error.message}</p> : null}
      <Actions saving={saving} canSave={canSave} onCancel={onCancel} />
    </form>
  )
}
