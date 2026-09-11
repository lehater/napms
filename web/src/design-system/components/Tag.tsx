export function Tag({ children }: { children: React.ReactNode }) {
  return (
    <span className="inline-flex min-h-6 items-center rounded-[var(--napms-tag-radius)] bg-[var(--napms-color-primary-subtle)] px-2 text-xs font-semibold text-[var(--napms-color-primary-hover)]">
      {children}
    </span>
  )
}

export function TagList({ values, limit = 2 }: { values: string[]; limit?: number }) {
  if (values.length === 0) {
    return <span className="text-[var(--napms-color-text-muted)]">—</span>
  }

  return (
    <div className="flex flex-wrap gap-1">
      {values.slice(0, limit).map((value) => (
        <Tag key={value}>{value}</Tag>
      ))}
      {values.length > limit ? (
        <span className="inline-flex min-h-6 items-center rounded-[var(--napms-tag-radius)] bg-[var(--napms-color-surface-muted)] px-2 text-xs text-[var(--napms-color-text-secondary)]">
          +{values.length - limit}
        </span>
      ) : null}
    </div>
  )
}
