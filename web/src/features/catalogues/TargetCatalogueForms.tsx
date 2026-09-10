import { useState } from "react"

import { ApiError } from "@/api"
import { Button } from "@/components/ui/Button"
import {
  createApplicationComponent,
  createApplicationDefinition,
  createApplicationDeployment,
  type ApplicationComponentDto,
  type ApplicationDefinitionDto,
  type ApplicationDeploymentDto,
} from "@/features/catalogues/targetCatalogueApi"

const inputClass =
  "min-h-10 w-full rounded-md border border-[#CBD5E1] bg-white px-3 py-2 text-sm text-[#172033] outline-none focus:border-[#2563EB] focus:ring-2 focus:ring-[#DBEAFE]"

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
    <form
      className="grid gap-4 rounded-lg border border-[#E2E8F0] bg-white p-5 shadow-sm"
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
        <h2 className="font-semibold text-[#172033]">New application</h2>
        <p className="mt-1 text-sm text-[#64748B]">Create the Definition first; Components and Deployments can be added incrementally.</p>
      </div>
      <div className="grid gap-3 md:grid-cols-2">
        <label className="grid gap-1 text-sm font-medium text-[#475569]">Name<input className={inputClass} value={name} onChange={(event) => setName(event.target.value)} maxLength={256} /></label>
        <label className="grid gap-1 text-sm font-medium text-[#475569]">Domain<input className={inputClass} value={domain} onChange={(event) => setDomain(event.target.value)} maxLength={256} /></label>
        <label className="grid gap-1 text-sm font-medium text-[#475569]">Owner<input className={inputClass} value={owner} onChange={(event) => setOwner(event.target.value)} maxLength={2048} /></label>
        <label className="grid gap-1 text-sm font-medium text-[#475569]">Description<input className={inputClass} value={description} onChange={(event) => setDescription(event.target.value)} maxLength={4096} /></label>
      </div>
      {error ? <p className="text-sm text-red-700">{error.message}</p> : null}
      <Actions saving={saving} canSave={Boolean(name.trim())} onCancel={onCancel} />
    </form>
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
      className="grid gap-4 border-b border-[#E2E8F0] bg-[#F8FAFC] p-5"
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
        <label className="grid gap-1 text-sm font-medium text-[#475569]">Name<input className={inputClass} value={name} onChange={(event) => setName(event.target.value)} maxLength={256} /></label>
        <label className="grid gap-1 text-sm font-medium text-[#475569]">Type<input className={inputClass} value={type} onChange={(event) => setType(event.target.value)} maxLength={256} /></label>
        <label className="grid gap-1 text-sm font-medium text-[#475569]">Description<input className={inputClass} value={description} onChange={(event) => setDescription(event.target.value)} maxLength={4096} /></label>
      </div>
      {error ? <p className="text-sm text-red-700">{error.message}</p> : null}
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
      className="grid gap-4 border-b border-[#E2E8F0] bg-[#F8FAFC] p-5"
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
        <label className="grid gap-1 text-sm font-medium text-[#475569]">Company<input className={inputClass} value={company} onChange={(event) => setCompany(event.target.value)} maxLength={2048} /></label>
        <label className="grid gap-1 text-sm font-medium text-[#475569]">Environment<input className={inputClass} value={environment} onChange={(event) => setEnvironment(event.target.value)} maxLength={256} /></label>
        <label className="grid gap-1 text-sm font-medium text-[#475569]">Scope<input className={inputClass} value={scope} onChange={(event) => setScope(event.target.value)} maxLength={2048} /></label>
      </div>
      {error ? <p className="text-sm text-red-700">{error.message}</p> : null}
      <Actions saving={saving} canSave={canSave} onCancel={onCancel} />
    </form>
  )
}
