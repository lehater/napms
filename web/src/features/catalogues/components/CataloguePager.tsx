import { Button } from "@/design-system/components/Button"

export function CataloguePager({
  page,
  pageSize,
  total,
  loading = false,
  onPageChange,
}: {
  page: number
  pageSize: number
  total: number
  loading?: boolean
  onPageChange: (page: number) => void
}) {
  const first = total === 0 ? 0 : (page - 1) * pageSize + 1
  const last = Math.min(page * pageSize, total)
  return (
    <div className="flex items-center justify-between border-t border-[#E2E8F0] px-4 py-3">
      <Button
        variant="secondary"
        disabled={page <= 1 || loading}
        onClick={() => onPageChange(page - 1)}
      >
        Previous
      </Button>
      <span className="text-xs font-medium text-[#64748B]">
        {first}–{last} of {total}
      </span>
      <Button
        variant="secondary"
        disabled={last >= total || loading}
        onClick={() => onPageChange(page + 1)}
      >
        Next
      </Button>
    </div>
  )
}
