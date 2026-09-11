import type { ReactNode } from "react"

type Tone = "positive" | "warning" | "critical" | "neutral" | "unknown"

const tones: Record<Tone, string> = {
  positive:
    "border-[var(--napms-color-success-dot)] bg-[var(--napms-color-success-bg)] text-[var(--napms-color-success)]",
  warning:
    "border-[var(--napms-color-warning-dot)] bg-[var(--napms-color-warning-bg)] text-[var(--napms-color-warning)]",
  critical:
    "border-[var(--napms-color-danger-dot)] bg-[var(--napms-color-danger-bg)] text-[var(--napms-color-danger)]",
  neutral:
    "border-[var(--napms-color-border)] bg-[var(--napms-color-surface-muted)] text-[var(--napms-color-text-body)]",
  unknown:
    "border-[var(--napms-color-unknown-border)] bg-[var(--napms-color-unknown-bg)] text-[var(--napms-color-unknown)]",
}

export function StatusBadge({
  tone = "neutral",
  title,
  children,
}: {
  tone?: Tone
  title?: string
  children: ReactNode
}) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${tones[tone]}`}
      title={title}
    >
      {children}
    </span>
  )
}
