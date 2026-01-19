export async function fetchHotspots() {
  const res = await fetch("/api/hotspots");
  return res.json();
}
