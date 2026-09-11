import { useState } from "react"

import { Button } from "@/design-system/components/Button"
import { Field, Input, Select, Textarea } from "@/design-system/components/Field"

export type RequestConnectivityDraft = {
  applicabilityKind: "Ongoing" | "AbsoluteWindow"
  windowStart: string
  windowEnd: string
  justification: string
}

export function RequestConnectivityForm({
  needExists,
  loading,
  submitting,
  disabled,
  onSubmit,
}: {
  needExists: boolean
  loading: boolean
  submitting: boolean
  disabled: boolean
  onSubmit: (draft: RequestConnectivityDraft) => void
}) {
  const [applicabilityKind, setApplicabilityKind] =
    useState<"Ongoing" | "AbsoluteWindow">("Ongoing")
  const [windowStart, setWindowStart] = useState("")
  const [windowEnd, setWindowEnd] = useState("")
  const [justification, setJustification] = useState("")

  function submit(event: React.FormEvent) {
    event.preventDefault()
    onSubmit({ applicabilityKind, windowStart, windowEnd, justification })
  }

  return (
    <form
      onSubmit={submit}
      className="rounded-[var(--napms-surface-radius)] border border-[var(--napms-color-border)] bg-[var(--napms-color-surface)] p-5 shadow-[var(--napms-surface-shadow)]"
    >
      <h2 className="text-base font-semibold text-[var(--napms-color-text-primary)]">
        {needExists ? "Confirm access proposal" : "Business need"}
      </h2>

      {!needExists ? (
        <div className="mt-5 grid gap-4">
          <Field label="Applicability">
            <Select
              value={applicabilityKind}
              onChange={(event) =>
                setApplicabilityKind(
                  event.target.value as "Ongoing" | "AbsoluteWindow",
                )
              }
            >
              <option value="Ongoing">Ongoing</option>
              <option value="AbsoluteWindow">Absolute time window</option>
            </Select>
          </Field>

          {applicabilityKind === "AbsoluteWindow" ? (
            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="Start">
                <Input
                  type="datetime-local"
                  step="1"
                  value={windowStart}
                  onChange={(event) => setWindowStart(event.target.value)}
                  required
                />
              </Field>
              <Field label="End">
                <Input
                  type="datetime-local"
                  step="1"
                  value={windowEnd}
                  onChange={(event) => setWindowEnd(event.target.value)}
                  required
                />
              </Field>
            </div>
          ) : null}

          <Field
            label="Business justification"
            hint="Why does your component need this semantic connectivity?"
          >
            <Textarea
              value={justification}
              onChange={(event) => setJustification(event.target.value)}
              maxLength={4096}
              rows={4}
              required
            />
          </Field>
        </div>
      ) : (
        <p className="mt-2 text-sm text-[var(--napms-color-text-secondary)]">
          The existing current Connectivity Requirement remains the need record.
          Requesting access does not change it.
        </p>
      )}

      <div className="mt-5 flex justify-end">
        <Button
          type="submit"
          loading={submitting}
          disabled={
            loading ||
            disabled ||
            (!needExists && !justification.trim())
          }
        >
          Request access
        </Button>
      </div>
    </form>
  )
}
