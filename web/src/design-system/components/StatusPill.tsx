type Tone = "positive" | "neutral" | "warning" | "critical"

const tones: Record<Tone, string> = {
  positive:
    "bg-[var(--napms-color-success-bg)] text-[var(--napms-color-success)]",
  neutral:
    "bg-[var(--napms-color-surface-muted)] text-[var(--napms-color-text-secondary)]",
  warning:
    "bg-[var(--napms-color-warning-bg)] text-[var(--napms-color-warning)]",
  critical:
    "bg-[var(--napms-color-danger-bg)] text-[var(--napms-color-danger)]",
}

const dots: Record<Tone, string> = {
  positive: "bg-[var(--napms-color-success-dot)]",
  neutral: "bg-[var(--napms-color-text-muted)]",
  warning: "bg-[var(--napms-color-warning-dot)]",
  critical: "bg-[var(--napms-color-danger-dot)]",
}

export function StatusPill({
  tone = "neutral",
  children,
}: {
  tone?: Tone
  children: React.ReactNode
}) {
  return (
    <span
      className={`inline-flex min-h-[25px] items-center gap-1.5 rounded-full px-2.5 text-xs font-semibold ${tones[tone]}`}
    >
      <span className={`size-1.5 rounded-full ${dots[tone]}`} aria-hidden="true" />
      {children}
    </span>
  )
}
