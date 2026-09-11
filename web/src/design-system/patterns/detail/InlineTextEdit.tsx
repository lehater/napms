import { useEffect, useState } from "react"
import { Pencil } from "lucide-react"

import { Button } from "@/design-system/components/Button"
import { Input } from "@/design-system/components/Field"

export function InlineTextEdit({
  value,
  allowEmpty = false,
  loading = false,
  label = "Rename",
  inputLabel = "New display name",
  onSave,
}: {
  value: string | null
  allowEmpty?: boolean
  loading?: boolean
  label?: string
  inputLabel?: string
  onSave: (value: string | null) => Promise<boolean>
}) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(value ?? "")

  useEffect(() => {
    if (!editing) setDraft(value ?? "")
  }, [editing, value])

  if (!editing) {
    return (
      <Button type="button" variant="ghost" onClick={() => setEditing(true)}>
        <Pencil className="size-4" aria-hidden="true" />
        {label}
      </Button>
    )
  }

  const normalized = draft.trim()
  const nextValue = allowEmpty && !normalized ? null : normalized
  const unchanged = nextValue === value

  return (
    <form
      className="flex min-w-64 flex-wrap items-center gap-2"
      onSubmit={(event) => {
        event.preventDefault()
        if ((!allowEmpty && !normalized) || unchanged) return
        void onSave(nextValue).then((saved) => {
          if (saved) setEditing(false)
        })
      }}
    >
      <Input
        value={draft}
        onChange={(event) => setDraft(event.target.value)}
        aria-label={inputLabel}
        maxLength={256}
        autoFocus
      />
      <Button type="submit" loading={loading} disabled={(!allowEmpty && !normalized) || unchanged}>
        Save
      </Button>
      <Button type="button" variant="ghost" disabled={loading} onClick={() => setEditing(false)}>
        Cancel
      </Button>
    </form>
  )
}
