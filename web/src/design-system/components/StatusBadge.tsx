import type { ReactNode } from "react"

type Tone = "positive" | "warning" | "critical" | "neutral" | "unknown"

const tones: Record<Tone, string> = {
  positive:
    "border-emerald-200 bg-[var(--napms-color-success-bg)] text-[var(--napms-color-success)]",
  warning:
    "border-amber-200 bg-[var(--napms-color-warning-bg)] text-[var(--napms-color-warning)]",
  critical:
    "border-red-200 bg-[var(--napms-color-danger-bg)] text-[var(--napms-color-danger)]",
  neutral:
    "border-[var(--napms-color-border)] bg-[var(--napms-color-surface-muted)] text-[var(--napms-color-text-body)]",
  unknown:
    "border-orange-200 bg-orange-50 text-orange-800",
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
