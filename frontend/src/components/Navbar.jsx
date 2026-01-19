import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { fetchCameras } from "../services/cameraService";
import { fetchAlerts } from "../services/alertService";
import "../styles/navbar.css";

function Navbar() {
  const [cameraCount, setCameraCount] = useState(0);
  const [alertCount, setAlertCount] = useState(0);

  useEffect(() => {
    fetchCameras().then((cams) => setCameraCount(cams.length));
    fetchAlerts().then((alerts) => setAlertCount(alerts.length));
  }, []);

  return (
    <header className="navbar">
      {/* LEFT */}
      <div className="nav-left">
        <span className="brand">SheSafe</span>

        <nav className="nav-links">
          <NavLink to="/">Dashboard</NavLink>
          <NavLink to="/cameras">Live Cameras</NavLink>
          <NavLink to="/alerts">Alerts</NavLink>
          <NavLink to="/analytics">Analytics</NavLink>
        </nav>
      </div>

      {/* RIGHT */}
      <div className="nav-right">
        <span className="nav-badge">
          🎥 {cameraCount} Cameras
        </span>

        <span className="nav-badge alert">
          🚨 {alertCount} Alerts
        </span>

        <span className="nav-status">
          ● System Active
        </span>
      </div>
    </header>
  );
}

export default Navbar;
