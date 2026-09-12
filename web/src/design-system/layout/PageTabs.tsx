export function PageTabs({ children }: { children: React.ReactNode }) {
  return (
    <div
      className="flex min-w-0 gap-1 overflow-x-auto border-b border-[var(--napms-color-border)]"
      role="tablist"
    >
      {children}
    </div>
  )
}

export function PageTab({
  active,
  children,
  onClick,
}: {
  active: boolean
  children: React.ReactNode
  onClick: () => void
}) {
  return (
    <button
      type="button"
      role="tab"
      aria-selected={active}
      className={`shrink-0 border-b-2 px-4 py-3 text-sm font-semibold transition ${
        active
          ? "border-[var(--napms-color-primary)] text-[var(--napms-color-primary-hover)]"
          : "border-transparent text-[var(--napms-color-text-secondary)] hover:text-[var(--napms-color-text-primary)]"
      }`}
      onClick={onClick}
    >
      {children}
    </button>
  )
}
