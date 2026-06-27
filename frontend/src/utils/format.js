export function formatTime(iso) {
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

export function percent(value, total) {
  if (!total) return 0;
  return Math.round((value / total) * 1000) / 10;
}