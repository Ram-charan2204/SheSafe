export async function fetchCameras() {
  const res = await fetch("/api/cameras");
  return res.json();
}
