export async function fetchAlerts() {
  const res = await fetch("/api/alerts");
  return res.json();
}
