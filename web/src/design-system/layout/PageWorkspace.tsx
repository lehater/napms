export function PageWorkspace({
  children,
  className = "",
}: {
  children: React.ReactNode
  className?: string
}) {
  return (
    <div className={`grid w-full min-w-0 gap-[var(--napms-page-gap)] ${className}`}>
      {children}
    </div>
  )
}
