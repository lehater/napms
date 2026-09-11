import { useState } from "react"

import { Button } from "@/design-system/components/Button"
import { Field, Input } from "@/design-system/components/Field"
import {
  Dialog,
  DialogActions,
  DialogBody,
  DialogHeader,
} from "@/design-system/patterns/dialog/Dialog"

export function CreateResourceDialog({
  open,
  onClose,
  onCreate,
}: {
  open: boolean
  onClose: () => void
  onCreate: (displayName: string | null) => Promise<string | null>
}) {
  const [displayName, setDisplayName] = useState("")
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    setCreating(true)
    setError(null)
    try {
      const failure = await onCreate(displayName.trim() || null)
      if (failure) {
        setError(failure)
        return
      }
      setDisplayName("")
      onClose()
    } finally {
      setCreating(false)
    }
  }

  function close() {
    if (creating) return
    setError(null)
    onClose()
  }

  return (
    <Dialog
      open={open}
      labelledBy="create-resource-title"
      busy={creating}
      onClose={close}
    >
      <DialogHeader
        titleId="create-resource-title"
        title="New resource"
        description="Create the Resource identity first. Current facts can be added from its detail page."
        busy={creating}
        onClose={close}
      />
      <form onSubmit={submit}>
        <DialogBody className="grid gap-5">
          <Field label="Display name">
            <Input
              autoFocus
              value={displayName}
              onChange={(event) => setDisplayName(event.target.value)}
              placeholder="Optional resource name"
              maxLength={256}
            />
          </Field>

          {error ? (
            <p className="text-sm text-[var(--napms-color-danger)]" role="alert">
              {error}
            </p>
          ) : null}

          <DialogActions>
            <Button type="button" variant="secondary" disabled={creating} onClick={close}>
              Cancel
            </Button>
            <Button type="submit" loading={creating}>
              Create resource
            </Button>
          </DialogActions>
        </DialogBody>
      </form>
    </Dialog>
  )
}
