export function Tag({ children }: { children: React.ReactNode }) {
  return (
    <span className="inline-flex min-h-5 items-center rounded-[var(--napms-tag-radius)] bg-[var(--napms-color-primary-subtle)] px-2 text-[10px] font-medium text-[var(--napms-color-primary-hover)]">
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
        <span className="inline-flex min-h-5 items-center rounded-[var(--napms-tag-radius)] bg-[var(--napms-color-surface-muted)] px-2 text-[10px] text-[var(--napms-color-text-secondary)]">
          +{values.length - limit}
        </span>
      ) : null}
    </div>
  )
}
