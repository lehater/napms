type AlertTone = "info" | "success" | "warning" | "danger"

const toneClass: Record<AlertTone, string> = {
  info: "border-[var(--napms-color-primary-border)] bg-[var(--napms-color-primary-subtle)] text-[var(--napms-color-text-body)]",
  success: "border-[var(--napms-color-success-border)] bg-[var(--napms-color-success-bg)] text-[var(--napms-color-success)]",
  warning: "border-[var(--napms-color-warning-border)] bg-[var(--napms-color-warning-bg)] text-[var(--napms-color-warning)]",
  danger: "border-[var(--napms-color-danger-border)] bg-[var(--napms-color-danger-bg)] text-[var(--napms-color-danger)]",
}

export function Alert({
  children,
  tone = "info",
  className = "",
  role,
}: {
  children: React.ReactNode
  tone?: AlertTone
  className?: string
  role?: React.AriaRole
}) {
  return (
    <div
      role={role}
      className={`rounded-[var(--napms-control-radius)] border px-4 py-3 text-sm ${toneClass[tone]} ${className}`}
    >
      {children}
    </div>
  )
}
