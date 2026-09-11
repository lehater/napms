type PageWorkspaceWidth = "fluid" | "content" | "narrow"

const widthClass: Record<PageWorkspaceWidth, string> = {
  fluid: "w-full",
  content: "mx-auto w-full max-w-[var(--napms-page-width-content)]",
  narrow: "mx-auto w-full max-w-[var(--napms-page-width-narrow)]",
}

export function PageWorkspace({
  children,
  className = "",
  width = "fluid",
}: {
  children: React.ReactNode
  className?: string
  width?: PageWorkspaceWidth
}) {
  return (
    <div className={`grid min-w-0 gap-[var(--napms-page-gap)] ${widthClass[width]} ${className}`}>
      {children}
    </div>
  )
}
