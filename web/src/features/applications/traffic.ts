export type PortRange = { from: number; to: number };

export function parsePortRanges(value: string): PortRange[] {
  return value
    .split(",")
    .map((part) => part.trim())
    .filter(Boolean)
    .map((part) => {
      const rangeMatch = part.match(/^(\d+)(?:-(\d+))?$/);
      if (!rangeMatch) throw new Error("invalid port range");
      const from = Number(rangeMatch[1]);
      const to = rangeMatch[2] === undefined ? from : Number(rangeMatch[2]);
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
