export function Surface({
  children,
  className = "",
}: {
  children: React.ReactNode
  className?: string
}) {
  return (
    <section
      className={`rounded-[var(--napms-surface-radius)] border border-[var(--napms-color-border)] bg-[var(--napms-color-surface)] shadow-[var(--napms-surface-shadow)] ${className}`}
    >
      {children}
    </section>
  )
}
