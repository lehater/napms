export function toLocalDateTimeInput(value: string | null): string {
  if (!value) return ""
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ""
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60_000)
  return local.toISOString().slice(0, 16)
}

export function nowLocalDateTimeInput(): string {
  return toLocalDateTimeInput(new Date().toISOString())
}

export function toOffsetAwareIso(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    throw new Error("Invalid date/time")
  }
  return date.toISOString()
}
