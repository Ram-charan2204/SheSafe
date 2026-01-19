export async function fetchStats() {
  const res = await fetch("/api/stats")
  return res.json()
}
