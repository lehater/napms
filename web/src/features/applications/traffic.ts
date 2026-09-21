export type PortRange = { from: number; to: number };

export function parsePortRanges(value: string): PortRange[] {
  return value
    .split(",")
    .map((part) => part.trim())
    .filter(Boolean)
    .map((part) => {
      if (!/^\\d+(?:-\\d+)?$/.test(part)) throw new Error("invalid port range");
      const values = part.split("-");
      const from = Number(values[0]);
      const to = values.length === 2 ? Number(values[1]) : from;
      if (
        !Number.isInteger(from) ||
        !Number.isInteger(to) ||
        from < 0 ||
        to > 65535 ||
        to < from
      ) {
        throw new Error("invalid port range");
      }
      return { from, to };
    })
    .sort((left, right) => left.from - right.from || left.to - right.to);
}

export function parseIpProtocol(value: string): number {
  const protocol = Number(value);
  if (!Number.isInteger(protocol) || protocol < 0 || protocol > 255) {
    throw new Error("invalid IP protocol");
  }
  return protocol;
}
