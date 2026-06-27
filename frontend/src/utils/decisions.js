export function decisionClass(decision) {
  if (decision === "block") return "badge-block";
  if (decision === "warn") return "badge-warn";
  return "badge-allow";
}