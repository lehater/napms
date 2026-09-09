import type { ButtonHTMLAttributes } from "react"

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost"
  loading?: boolean
}

export function Button({
  variant = "primary",
  loading = false,
  disabled,
  className = "",
  children,
  ...props
}: Props) {
  const variants = {
    primary:
      "bg-[#2563EB] text-white hover:bg-[#1D4ED8] active:bg-[#1E40AF] border-transparent",
    secondary:
      "bg-white text-[#172033] hover:bg-[#F8FAFC] border-[#CBD5E1]",
    ghost:
      "bg-transparent text-[#5F6B7D] hover:bg-[#F1F5F9] border-transparent",
  }

  return (
    <button
      className={`inline-flex min-h-10 items-center justify-center gap-2 rounded-md border px-4 py-2 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-50 ${variants[variant]} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? "Working…" : children}
    </button>
  )
}
