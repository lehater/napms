export function PageHeader({
  title,
  description,
  actions,
}: {
  title: React.ReactNode
  description?: React.ReactNode
  actions?: React.ReactNode
}) {
  return (
    <header className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
      <div className="min-w-0">
        <h1 className="text-xl font-bold leading-6 text-[var(--napms-color-text-primary)]">
          {title}
        </h1>
        {description ? (
          <p className="mt-0.5 text-sm leading-5 text-[var(--napms-color-text-secondary)]">
            {description}
          </p>
        ) : null}
      </div>
      {actions ? <div className="shrink-0">{actions}</div> : null}
    </header>
  )
}
