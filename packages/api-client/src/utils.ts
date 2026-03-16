/** Converts a params object into a URL query string, omitting null/undefined values. */
export function buildQueryString(params: Record<string, unknown>): string {
  const entries = Object.entries(params).filter(
    ([, v]) => v !== null && v !== undefined && v !== ""
  );
  if (!entries.length) return "";
  return "?" + entries.map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`).join("&");
}
