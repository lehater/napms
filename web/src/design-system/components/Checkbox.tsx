import { useEffect, useRef } from "react"
import type { InputHTMLAttributes } from "react"

type Props = Omit<InputHTMLAttributes<HTMLInputElement>, "type"> & {
  indeterminate?: boolean
}

export function Checkbox({
  indeterminate = false,
  className = "",
  ...props
}: Props) {
  const ref = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (ref.current) ref.current.indeterminate = indeterminate
  }, [indeterminate])

  return (
    <input
      ref={ref}
      type="checkbox"
      className={`size-[var(--napms-checkbox-size)] cursor-pointer rounded-[4px] border border-[var(--napms-color-border-strong)] accent-[var(--napms-color-primary)] disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
      {...props}
    />
  )
}
