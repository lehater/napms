import type { SelectHTMLAttributes } from "react"

export function Field({
  label,
  hint,
  children,
}: {
  label: string
  hint?: string
  children: React.ReactNode
}) {
  return (
    <label className="grid gap-2 text-sm font-medium text-[#334155]">
      <span>{label}</span>
      {children}
      {hint ? <span className="text-xs font-normal text-[#5F6B7D]">{hint}</span> : null}
    </label>
  )
}

export function Select({
  className = "",
  ...props
}: SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      className={`min-h-10 w-full rounded-md border border-[#CBD5E1] bg-white px-3 py-2 text-sm text-[#172033] disabled:bg-[#F8FAFC] disabled:text-[#94A3B8] ${className}`}
      {...props}
    />
  )
}
