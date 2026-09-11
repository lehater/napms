import { AlertCircle, AlertTriangle } from "lucide-react"

type Tone = "success" | "warning" | "danger"

const toneClasses: Record<Tone, string> = {
  success: "text-[var(--napms-color-text-body)]",
  warning: "text-[var(--napms-color-text-body)]",
  danger: "text-[var(--napms-color-text-body)]",
}

export function IssueIndicator({
  tone = "warning",
  children,
}: {
  tone?: Tone
  children: React.ReactNode
}) {
  let marker: React.ReactNode
  if (tone === "success") {
    marker = (
      <span
        className="size-2 rounded-full bg-[var(--napms-color-success-dot)]"
        aria-hidden="true"
      />
    )
  } else if (tone === "danger") {
    marker = (
      <AlertCircle
        className="size-3.5 text-[var(--napms-color-danger-dot)]"
        aria-hidden="true"
      />
    )
  } else {
    marker = (
      <AlertTriangle
        className="size-3.5 text-[var(--napms-color-warning-dot)]"
        aria-hidden="true"
      />
    )
  }

  return (
    <span className={`inline-flex items-center gap-1.5 whitespace-nowrap text-[11px] font-medium ${toneClasses[tone]}`}>
      {marker}
      {children}
    </span>
  )
}
