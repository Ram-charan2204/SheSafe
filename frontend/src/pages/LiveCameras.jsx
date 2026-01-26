import { useEffect, useState, useRef } from "react";
import { fetchCameras } from "../services/cameraService";
import "../styles/camera.css";

function LiveCameras() {
  const [cameras, setCameras] = useState([]);
  const [activeCam, setActiveCam] = useState(null);

  // zoom / pan state
  const [scale, setScale] = useState(1);
  const [pos, setPos] = useState({ x: 0, y: 0 });
  const last = useRef({ x: 0, y: 0 });
  const dragging = useRef(false);

  /* ---------------- AUTO REFRESH ---------------- */
  useEffect(() => {
    const load = async () => {
      try {
        const data = await fetchCameras();
        setCameras(data || []);
      } catch {
        setCameras([]);
      }
    };

    load();
    const id = setInterval(load, 3000);
    return () => clearInterval(id);
  }, []);

  /* ---------------- ZOOM / PAN ---------------- */
  const onWheel = (e) => {
    e.preventDefault();
    setScale((s) => Math.min(Math.max(1, s - e.deltaY * 0.001), 3));
  };

  const onDown = (e) => {
    dragging.current = true;
    last.current = { x: e.clientX, y: e.clientY };
  };

  const onMove = (e) => {
    if (!dragging.current) return;
    setPos((p) => ({
      x: p.x + e.clientX - last.current.x,
      y: p.y + e.clientY - last.current.y
    }));
    last.current = { x: e.clientX, y: e.clientY };
  };

  const resetView = () => {
    setScale(1);
    setPos({ x: 0, y: 0 });
  };

  const stopDrag = () => {
    dragging.current = false;
  };

  /* ---------------- MAP IMAGE ---------------- */
  const mapImage = (lat, lon) =>
    lat && lon
      ? `https://staticmap.openstreetmap.de/staticmap.php?center=${lat},${lon}&zoom=15&size=500x500&markers=${lat},${lon},red`
      : "/placeholder.png";

  /* ---------------- RENDER ---------------- */
  return (
    <div className="page">
      <h1>Live Cameras</h1>

      <div className="camera-grid">
        {cameras.map((cam) => {
          const status = cam.status || "INACTIVE";

          return (
            <div
              key={cam.id}
              className="camera-card"
              onClick={() => setActiveCam(cam)}
            >
              <div className="camera-feed">
                {status === "ACTIVE" ? (
                  <img
                    src={`http://localhost:5000/video/${cam.id}`}
                    className="camera-stream"
                    alt={cam.id}
                  />
                ) : (
                  <iframe
  src="http://localhost:5000/api/hotspots/map"
  className="camera-stream"
  title="map"
/>

                )}
              </div>

              <div className="camera-info">
                <span className="camera-name">{cam.id}</span>
                <span className={`camera-status ${status.toLowerCase()}`}>
                  {status}
                </span>
              </div>

              <div className="camera-location">
                {cam.location || "Unknown location"}
              </div>
            </div>
          );
        })}
      </div>

      {/* ---------------- MODAL ---------------- */}
      {activeCam && (
        <div className="camera-modal" onClick={() => setActiveCam(null)}>
          <div
            className="camera-modal-content"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="modal-header">
              <span>
                {activeCam.id} — {activeCam.location || "Unknown"}
              </span>
              <span
                className={`camera-status ${
                  (activeCam.status || "INACTIVE").toLowerCase()
                }`}
              >
                {activeCam.status || "INACTIVE"}
              </span>
              <button onClick={() => setActiveCam(null)}>✕</button>
            </div>

            <div
              className="modal-video"
              onWheel={onWheel}
              onMouseDown={onDown}
              onMouseMove={onMove}
              onMouseUp={stopDrag}
              onMouseLeave={stopDrag}
              onDoubleClick={resetView}
            >
              {activeCam.status === "ACTIVE" ? (
                <img
                  src={`http://localhost:5000/video/${activeCam.id}`}
                  className="camera-modal-stream"
                  style={{
                    transform: `translate(${pos.x}px, ${pos.y}px) scale(${scale})`
                  }}
                  alt={activeCam.id}
                />
              ) : (
                <iframe
  src="http://localhost:5000/api/hotspots/map"
  className="camera-stream"
  title="map"
/>

              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default LiveCameras;
