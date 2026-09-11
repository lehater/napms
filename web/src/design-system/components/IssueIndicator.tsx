import { AlertTriangle, CheckCircle2 } from "lucide-react"

type Tone = "success" | "warning" | "danger"

const toneClasses: Record<Tone, string> = {
  success: "text-[var(--napms-color-success)]",
  warning: "text-[var(--napms-color-warning)]",
  danger: "text-[var(--napms-color-danger)]",
}

export function IssueIndicator({
  tone = "warning",
  children,
}: {
  tone?: Tone
  children: React.ReactNode
}) {
  const Icon = tone === "success" ? CheckCircle2 : AlertTriangle
  return (
    <span className={`inline-flex items-center gap-1.5 text-xs font-semibold ${toneClasses[tone]}`}>
      <Icon className="size-3.5" aria-hidden="true" />
      {children}
    </span>
  )
}
