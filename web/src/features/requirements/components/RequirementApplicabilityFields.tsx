import { Field, Input, Select, Textarea } from "@/design-system/components/Field"

export function RequirementApplicabilityFields({
  kind,
  onKindChange,
  windowStart,
  onWindowStartChange,
  windowEnd,
  onWindowEndChange,
  justification,
  onJustificationChange,
}: {
  kind: "Ongoing" | "AbsoluteWindow"
  onKindChange: (value: "Ongoing" | "AbsoluteWindow") => void
  windowStart: string
  onWindowStartChange: (value: string) => void
  windowEnd: string
  onWindowEndChange: (value: string) => void
  justification: string
  onJustificationChange: (value: string) => void
}) {
  return (
    <>
      <Field label="Applicability">
        <Select
          value={kind}
          onChange={(event) =>
            onKindChange(event.target.value as "Ongoing" | "AbsoluteWindow")
          }
        >
          <option value="Ongoing">Ongoing</option>
          <option value="AbsoluteWindow">Absolute time window</option>
        </Select>
      </Field>

      {kind === "AbsoluteWindow" ? (
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1 2xl:grid-cols-2">
          <Field label="Start">
            <Input
              type="datetime-local"
              step="1"
              value={windowStart}
              onChange={(event) => onWindowStartChange(event.target.value)}
              required
            />
          </Field>
          <Field label="End">
            <Input
              type="datetime-local"
              step="1"
              value={windowEnd}
              onChange={(event) => onWindowEndChange(event.target.value)}
              required
            />
          </Field>
        </div>
      ) : null}

      <Field
        label="Business justification"
        hint="Why is this semantic connectivity required?"
      >
        <Textarea
          value={justification}
          onChange={(event) => onJustificationChange(event.target.value)}
          maxLength={4096}
          rows={4}
          required
        />
      </Field>
    </>
  )
}
