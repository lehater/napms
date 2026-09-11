import { Search } from "lucide-react"
import type { InputHTMLAttributes } from "react"

import { Input } from "@/design-system/components/Field"

export function SearchInput({
  className = "",
  ...props
}: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <div className={`relative ${className}`}>
      <Search
        className="pointer-events-none absolute left-4 top-1/2 size-[var(--napms-icon-size-control)] -translate-y-1/2 text-[var(--napms-color-text-muted)]"
        aria-hidden="true"
      />
      <Input className="pl-11" {...props} />
    </div>
  )
}
