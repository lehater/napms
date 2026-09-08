export function StatusBadge({
  value,
}: {
  value: "Active" | "Inactive" | "Permitted" | "Denied" | "Unknown"
}) {
  const classes = {
    Active: "border-green-200 bg-green-50 text-green-800",
    Inactive: "border-slate-200 bg-slate-100 text-slate-700",
    Permitted: "border-green-200 bg-green-50 text-green-800",
    Denied: "border-red-200 bg-red-50 text-red-800",
    Unknown: "border-amber-200 bg-amber-50 text-amber-800",
  }[value]

  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${classes}`}
    >
      {value}
    </span>
  )
}
