type Tone = "positive" | "neutral" | "critical"

const dots: Record<Tone, string> = {
  positive: "bg-[var(--napms-color-success-dot)]",
  neutral: "bg-[var(--napms-color-text-muted)]",
  critical: "bg-[var(--napms-color-danger-dot)]",
}

export function StatusIndicator({
  tone = "neutral",
  children,
}: {
  tone?: Tone
  children: React.ReactNode
}) {
  return (
    <span className="inline-flex items-center gap-1.5 whitespace-nowrap text-[11px] font-medium text-[var(--napms-color-text-body)]">
      <span className={`size-2 rounded-full ${dots[tone]}`} aria-hidden="true" />
      {children}
    </span>
  )
}
