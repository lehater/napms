import { useEffect, useState } from "react"
import { ChevronDown, Plus } from "lucide-react"

import { Button } from "@/design-system/components/Button"
import { Input, Select, Textarea } from "@/design-system/components/Field"
import { Tag } from "@/design-system/components/Tag"
import { DetailRow, DetailSection } from "@/design-system/patterns/detail/Detail"
import { Surface } from "@/design-system/primitives/Surface"
import {
  createCatalogueResourceRealization,
  createCatalogueResourceResponsibility,
  createCatalogueResourceScopeAffiliation,
  endCatalogueResourceResponsibility,
  endCatalogueResourceScopeAffiliation,
  replaceCatalogueResourceRealization,
  type ResourceDetailDto,
  type ResourceResponsibilityDto,
  type ResourceScopeAffiliationDto,
} from "@/features/catalogues/api/catalogue"
import { renameCatalogueResource, retireCatalogueResource } from "@/features/catalogues/api/resourceWorkspace"
import { formatResourceDate } from "@/features/catalogues/components/ResourceDetailSections"
import { ApiError } from "@/lib/api"

function errorFrom(caught: unknown, fallback: string) { return caught instanceof ApiError ? caught : new ApiError(500, "InternalError", fallback) }
function roleLabel(role: ResourceResponsibilityDto["role"]) { return { TechnicalOwner: "Technical owner", ServiceOwner: "Service owner", OperationsContact: "Operations contact", BusinessOwner: "Business owner" }[role] }

export function ResourceLifecycleActions({ detail, onChanged }: { detail: ResourceDetailDto; onChanged: () => Promise<void> }) {
  const [actionsOpen, setActionsOpen] = useState(false)
  const [editingName, setEditingName] = useState(false)
  const [nameDraft, setNameDraft] = useState(detail.resource.displayName ?? "")
  const [saving, setSaving] = useState<"rename" | "retire" | null>(null)
  const [error, setError] = useState<string | null>(null)
  const active = detail.resource.lifecycle === "Active"
  useEffect(() => { if (!editingName) setNameDraft(detail.resource.displayName ?? "") }, [detail.resource.displayName, editingName])

  async function rename(event: React.FormEvent) {
    event.preventDefault(); const nextName = nameDraft.trim(); if (!nextName || nextName === (detail.resource.displayName ?? "")) return
    setSaving("rename"); setError(null)
    try { await renameCatalogueResource(detail.resource, nextName); setEditingName(false); await onChanged() } catch (caught) { setError(errorFrom(caught, "Resource could not be renamed.").message) } finally { setSaving(null) }
  }
  async function retire() {
    setActionsOpen(false)
    if (!window.confirm("Retire this resource? Current scope affiliations and responsibilities must be ended first. Historical references will be preserved.")) return
    setSaving("retire"); setError(null)
    try { await retireCatalogueResource(detail.resource); await onChanged() } catch (caught) { const failure = errorFrom(caught, "Resource could not be retired."); setError(failure.code === "CatalogueRetirementBlocked" ? "End current scope affiliations and responsibilities before retiring this resource." : failure.message) } finally { setSaving(null) }
  }

  return <>
    <div className="relative"><Button variant="secondary" onClick={() => setActionsOpen((value) => !value)}>Actions <ChevronDown className="size-4" aria-hidden="true" /></Button>{actionsOpen ? <div className="absolute right-0 z-20 mt-2 w-44 overflow-hidden rounded-[var(--napms-control-radius)] border border-[var(--napms-color-border)] bg-[var(--napms-color-surface)] py-1 shadow-lg">{active ? <button type="button" className="block w-full px-3 py-2 text-left text-sm hover:bg-[var(--napms-color-surface-subtle)]" onClick={() => { setActionsOpen(false); setEditingName(true) }}>Rename</button> : null}{active ? <button type="button" className="block w-full px-3 py-2 text-left text-sm text-[var(--napms-color-danger)] hover:bg-[var(--napms-color-danger-bg)]" onClick={() => void retire()}>Retire resource</button> : null}</div> : null}</div>
    {editingName ? <Surface className="col-span-full p-4"><form className="flex flex-col gap-3 sm:flex-row sm:items-end" onSubmit={rename}><label className="grid min-w-0 flex-1 gap-1 text-xs font-medium text-[var(--napms-color-text-body)]">Display name<Input value={nameDraft} onChange={(event) => setNameDraft(event.target.value)} /></label><div className="flex gap-2"><Button type="button" variant="secondary" onClick={() => setEditingName(false)}>Cancel</Button><Button type="submit" loading={saving === "rename"}>Save</Button></div></form></Surface> : null}
    {error ? <div role="alert" className="col-span-full rounded-[var(--napms-control-radius)] border border-[var(--napms-color-danger)] bg-[var(--napms-color-danger-bg)] p-3 text-sm text-[var(--napms-color-danger)]">{error}</div> : null}
  </>
}

export function ResourceOverviewEditors({ detail, resourceReference, onChanged }: { detail: ResourceDetailDto; resourceReference: string; onChanged: () => Promise<void> }) {
  const active = detail.resource.lifecycle === "Active"
  const currentRealization = detail.effectiveRealizations[0]
  const [editingAddresses, setEditingAddresses] = useState(false)
  const [addresses, setAddresses] = useState("")
  const [savingRealization, setSavingRealization] = useState(false)
  const [realizationError, setRealizationError] = useState<string | null>(null)
  const [addingScope, setAddingScope] = useState(false)
  const [responsibilityScope, setResponsibilityScope] = useState("")
  const [creatingAffiliation, setCreatingAffiliation] = useState(false)
  const [endingAffiliationReference, setEndingAffiliationReference] = useState<string | null>(null)
  const [affiliationError, setAffiliationError] = useState<string | null>(null)
  const [addingResponsibility, setAddingResponsibility] = useState(false)
  const [partyReference, setPartyReference] = useState("")
  const [partyKind, setPartyKind] = useState<"Person" | "Team">("Team")
  const [responsibilityRole, setResponsibilityRole] = useState<ResourceResponsibilityDto["role"]>("TechnicalOwner")
  const [responsibilityDisplayName, setResponsibilityDisplayName] = useState("")
  const [responsibilityContact, setResponsibilityContact] = useState("")
  const [creatingResponsibility, setCreatingResponsibility] = useState(false)
  const [endingResponsibilityReference, setEndingResponsibilityReference] = useState<string | null>(null)
  const [responsibilityError, setResponsibilityError] = useState<string | null>(null)

  async function saveRealization(event: React.FormEvent) { event.preventDefault(); const values = addresses.split(/[\n,]+/).map((value) => value.trim()).filter(Boolean); if (!values.length) return; setSavingRealization(true); setRealizationError(null); try { if (currentRealization) await replaceCatalogueResourceRealization(currentRealization, values, new Date().toISOString()); else await createCatalogueResourceRealization(resourceReference, values, new Date().toISOString()); setAddresses(""); setEditingAddresses(false); await onChanged() } catch (caught) { setRealizationError(errorFrom(caught, "Resource realization could not be saved.").message) } finally { setSavingRealization(false) } }
  async function addScope(event: React.FormEvent) { event.preventDefault(); const reference = responsibilityScope.trim(); if (!reference) return; setCreatingAffiliation(true); setAffiliationError(null); try { await createCatalogueResourceScopeAffiliation(resourceReference, reference, new Date().toISOString()); setResponsibilityScope(""); setAddingScope(false); await onChanged() } catch (caught) { setAffiliationError(errorFrom(caught, "Scope affiliation could not be created.").message) } finally { setCreatingAffiliation(false) } }
  async function endScope(item: ResourceScopeAffiliationDto) { if (!window.confirm(`End scope affiliation ${item.responsibilityScope} now?`)) return; setEndingAffiliationReference(item.affiliationReference); setAffiliationError(null); try { await endCatalogueResourceScopeAffiliation(item, new Date().toISOString()); await onChanged() } catch (caught) { setAffiliationError(errorFrom(caught, "Scope affiliation could not be ended.").message) } finally { setEndingAffiliationReference(null) } }
  async function addResponsibility(event: React.FormEvent) { event.preventDefault(); const reference = partyReference.trim(); const displayName = responsibilityDisplayName.trim(); if (!reference || !displayName) return; setCreatingResponsibility(true); setResponsibilityError(null); try { await createCatalogueResourceResponsibility(resourceReference, { partyReference: reference, partyKind, role: responsibilityRole, displayName, contact: responsibilityContact.trim() || null, validFrom: new Date().toISOString() }); setPartyReference(""); setResponsibilityDisplayName(""); setResponsibilityContact(""); setAddingResponsibility(false); await onChanged() } catch (caught) { setResponsibilityError(errorFrom(caught, "Resource responsibility could not be created.").message) } finally { setCreatingResponsibility(false) } }
  async function endResponsibility(item: ResourceResponsibilityDto) { if (!window.confirm(`End ${roleLabel(item.role)} responsibility for ${item.displayName} now?`)) return; setEndingResponsibilityReference(item.assignmentReference); setResponsibilityError(null); try { await endCatalogueResourceResponsibility(item, new Date().toISOString()); await onChanged() } catch (caught) { setResponsibilityError(errorFrom(caught, "Resource responsibility could not be ended.").message) } finally { setEndingResponsibilityReference(null) } }

  return <>
    <DetailSection title="Technical realization">{currentRealization ? <><DetailRow label="Addresses"><div className="grid gap-1 font-mono text-xs">{currentRealization.technicalAddresses.map((item) => <span key={item.endpointReference}>{item.technicalAddress}</span>)}</div></DetailRow><DetailRow label="Effective since">{formatResourceDate(currentRealization.validFrom)}</DetailRow></> : <p className="text-sm text-[var(--napms-color-text-secondary)]">No current realization.</p>}{active ? <Button className="mt-3" variant="secondary" size="sm" onClick={() => setEditingAddresses(true)}>{currentRealization ? "Replace addresses" : "Add addresses"}</Button> : null}{editingAddresses ? <form className="mt-3 grid gap-2" onSubmit={saveRealization}><label className="grid gap-1 text-xs font-medium">Addresses<Textarea className="font-mono" value={addresses} onChange={(event) => setAddresses(event.target.value)} placeholder={"10.20.30.40\n10.20.30.41"} /></label>{realizationError ? <p className="text-xs text-[var(--napms-color-danger)]">{realizationError}</p> : null}<div className="flex gap-2"><Button type="button" variant="secondary" size="sm" onClick={() => setEditingAddresses(false)}>Cancel</Button><Button type="submit" size="sm" loading={savingRealization}>{currentRealization ? "Replace" : "Add"}</Button></div></form> : null}</DetailSection>
    <DetailSection title="Responsibility scopes"><div className="flex flex-wrap gap-2">{detail.effectiveScopeAffiliations.length ? detail.effectiveScopeAffiliations.map((item) => <div key={item.affiliationReference} className="flex items-center gap-2"><Tag>{item.responsibilityScope}</Tag>{active ? <button type="button" className="text-xs text-[var(--napms-color-danger)] hover:underline" disabled={endingAffiliationReference === item.affiliationReference} onClick={() => void endScope(item)}>End</button> : null}</div>) : <span className="text-sm text-[var(--napms-color-text-secondary)]">No current scope.</span>}</div>{active ? <Button className="mt-3" variant="secondary" size="sm" onClick={() => setAddingScope(true)}><Plus className="size-3.5" aria-hidden="true" />Add scope</Button> : null}{addingScope ? <form className="mt-3 flex gap-2" onSubmit={addScope}><Input value={responsibilityScope} onChange={(event) => setResponsibilityScope(event.target.value)} placeholder="payments-team" /><Button type="submit" size="sm" loading={creatingAffiliation}>Add</Button></form> : null}{affiliationError ? <p className="mt-2 text-xs text-[var(--napms-color-danger)]">{affiliationError}</p> : null}</DetailSection>
    <DetailSection title="Responsibilities"><div className="grid gap-3">{detail.effectiveResponsibilities.length ? detail.effectiveResponsibilities.map((item) => <div key={item.assignmentReference} className="grid grid-cols-[130px_minmax(0,1fr)_auto] items-start gap-3 border-b border-[var(--napms-color-border)] pb-3 last:border-0 last:pb-0"><div className="text-xs text-[var(--napms-color-text-secondary)]">{roleLabel(item.role)}</div><div><div className="text-sm font-semibold text-[var(--napms-color-primary)]">{item.displayName}</div>{item.contact ? <div className="text-xs text-[var(--napms-color-text-secondary)]">{item.contact}</div> : null}</div>{active ? <button type="button" className="text-xs text-[var(--napms-color-danger)] hover:underline" disabled={endingResponsibilityReference === item.assignmentReference} onClick={() => void endResponsibility(item)}>End</button> : null}</div>) : <span className="text-sm text-[var(--napms-color-text-secondary)]">No current responsibility.</span>}</div>{active ? <Button className="mt-3" variant="secondary" size="sm" onClick={() => setAddingResponsibility(true)}><Plus className="size-3.5" aria-hidden="true" />Add responsibility</Button> : null}{addingResponsibility ? <form className="mt-3 grid gap-2" onSubmit={addResponsibility}><div className="grid gap-2 sm:grid-cols-2"><Select value={partyKind} onChange={(event) => setPartyKind(event.target.value as "Person" | "Team")}><option value="Team">Team</option><option value="Person">Person</option></Select><Select value={responsibilityRole} onChange={(event) => setResponsibilityRole(event.target.value as ResourceResponsibilityDto["role"])}><option value="TechnicalOwner">Technical owner</option><option value="ServiceOwner">Service owner</option><option value="OperationsContact">Operations contact</option><option value="BusinessOwner">Business owner</option></Select></div><Input value={partyReference} onChange={(event) => setPartyReference(event.target.value)} placeholder="team:platform" /><Input value={responsibilityDisplayName} onChange={(event) => setResponsibilityDisplayName(event.target.value)} placeholder="Platform Team" /><Input value={responsibilityContact} onChange={(event) => setResponsibilityContact(event.target.value)} placeholder="Contact (optional)" /><div className="flex gap-2"><Button type="button" variant="secondary" size="sm" onClick={() => setAddingResponsibility(false)}>Cancel</Button><Button type="submit" size="sm" loading={creatingResponsibility}>Add</Button></div></form> : null}{responsibilityError ? <p className="mt-2 text-xs text-[var(--napms-color-danger)]">{responsibilityError}</p> : null}</DetailSection>
  </>
}
