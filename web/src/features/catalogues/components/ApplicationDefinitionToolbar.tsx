import { Button } from "@/design-system/components/Button"
import { Input } from "@/design-system/components/Field"
import { SearchInput } from "@/design-system/components/SearchInput"
import {
  CatalogueFilterBar,
  CatalogueFilterField,
  CatalogueToolbar,
} from "@/design-system/patterns/catalogue/CataloguePage"

export type ApplicationDefinitionTab = "components" | "interactions" | "deployments"
export type ApplicationDefinitionFilters = { search: string; first: string; second: string; third: string }

export function ApplicationDefinitionToolbar({
  tab,
  draft,
  onDraft,
  onApply,
}: {
  tab: ApplicationDefinitionTab
  draft: ApplicationDefinitionFilters
  onDraft: (value: ApplicationDefinitionFilters) => void
  onApply: () => void
}) {
  return (
    <form onSubmit={(event) => { event.preventDefault(); onApply() }}>
      <CatalogueToolbar>
        <SearchInput
          value={draft.search}
          onChange={(event) => onDraft({ ...draft, search: event.target.value })}
          placeholder={`Search ${tab}`}
          aria-label={`Search ${tab}`}
        />
        <CatalogueFilterBar>
          {tab === "components" ? (
            <CatalogueFilterField label="Type" className="xl:w-[190px]">
              <Input value={draft.first} onChange={(event) => onDraft({ ...draft, first: event.target.value })} aria-label="Component type" />
            </CatalogueFilterField>
          ) : tab === "interactions" ? (
            <CatalogueFilterField label="Protocol" className="xl:w-[190px]">
              <Input value={draft.first} onChange={(event) => onDraft({ ...draft, first: event.target.value })} aria-label="Protocol" />
            </CatalogueFilterField>
          ) : (
            <>
              <CatalogueFilterField label="Company" className="xl:w-[190px]">
                <Input value={draft.first} onChange={(event) => onDraft({ ...draft, first: event.target.value })} aria-label="Company" />
              </CatalogueFilterField>
              <CatalogueFilterField label="Environment" className="xl:w-[190px]">
                <Input value={draft.second} onChange={(event) => onDraft({ ...draft, second: event.target.value })} aria-label="Environment" />
              </CatalogueFilterField>
              <CatalogueFilterField label="Scope" className="xl:w-[190px]">
                <Input value={draft.third} onChange={(event) => onDraft({ ...draft, third: event.target.value })} aria-label="Scope" />
              </CatalogueFilterField>
            </>
          )}
          <Button type="submit" variant="secondary" size="sm" className="xl:ml-auto">Apply</Button>
        </CatalogueFilterBar>
      </CatalogueToolbar>
    </form>
  )
}
