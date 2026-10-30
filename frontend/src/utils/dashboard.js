export function getProgressPercentage(completed, total) {
  if (!Number.isFinite(total) || total <= 0) return 0
  return Math.min(100, Math.max(0, Math.round((completed / total) * 100)))
}

export function getNonZeroStatusRows(rows) {
  return (rows || []).filter((row) => Number(row.value) > 0)
}
