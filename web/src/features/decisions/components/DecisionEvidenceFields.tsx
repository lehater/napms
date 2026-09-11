import { Trash2 } from "lucide-react"

import { Input } from "@/design-system/components/Field"

export type DecisionEvidenceDraft = {
  kind: string
  reference: string
}

export function DecisionEvidenceFields({
  evidence,
  onChange,
}: {
  evidence: DecisionEvidenceDraft[]
  onChange: (evidence: DecisionEvidenceDraft[]) => void
}) {
  function update(
    index: number,
    field: keyof DecisionEvidenceDraft,
    value: string,
  ) {
    onChange(
      evidence.map((item, itemIndex) =>
        itemIndex === index ? { ...item, [field]: value } : item,
      ),
    )
  }

  return (
    <div className="grid gap-3">
      <div>
        <div className="text-sm font-medium text-[var(--napms-color-text-body)]">
          Evidence references
        </div>
        <div className="mt-1 text-xs text-[var(--napms-color-text-secondary)]">
          Optional references only. Evidence content remains outside this workspace.
        </div>
      </div>
      {evidence.map((item, index) => (
        <div
          key={index}
          className="grid gap-2 rounded-[var(--napms-control-radius)] border border-[var(--napms-color-border)] p-3"
        >
          <Input
            value={item.kind}
            maxLength={256}
            onChange={(event) => update(index, "kind", event.target.value)}
            placeholder="Kind"
            aria-label={`Evidence ${index + 1} kind`}
          />
          <Input
            value={item.reference}
            maxLength={2048}
            onChange={(event) => update(index, "reference", event.target.value)}
            placeholder="Reference"
            aria-label={`Evidence ${index + 1} reference`}
          />
          {evidence.length > 1 ? (
            <button
              type="button"
              className="inline-flex items-center gap-1 justify-self-start text-xs font-semibold text-[var(--napms-color-text-secondary)] hover:text-[var(--napms-color-text-primary)]"
              onClick={() =>
                onChange(evidence.filter((_, itemIndex) => itemIndex !== index))
              }
            >
              <Trash2 className="size-3.5" aria-hidden="true" />
              Remove
            </button>
          ) : null}
        </div>
      ))}
      <button
        type="button"
        className="justify-self-start text-xs font-semibold text-[var(--napms-color-primary)] hover:text-[var(--napms-color-primary-hover)]"
        onClick={() => onChange([...evidence, { kind: "", reference: "" }])}
      >
        Add evidence reference
      </button>
    </div>
  )
}
