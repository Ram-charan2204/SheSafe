import { useEffect, useState } from "react";
import { fetchHotspots } from "../services/hotspotService";
import "../styles/analytics.css";

function Analytics() {
  const [hotspots, setHotspots] = useState([]);

  useEffect(() => {
    const loadHotspots = () => {
      fetchHotspots().then(setHotspots);
    };

    loadHotspots();                  // initial
    const interval = setInterval(loadHotspots, 5000); // 🔥 auto refresh

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="page">
      <h1>Hotspot Analytics</h1>
      <p className="subtitle">
        Crime-risk concentration based on historical alerts
      </p>

      {/* MAP */}
      <div className="hotspot-map">
        <iframe
          src="http://localhost:5000/api/hotspots/map"
          title="Crime Hotspot Map"
        />
      </div>

      {/* TABLE */}
      <h2 className="section-title">High-Risk Zones</h2>

      <div className="hotspot-table">
        {hotspots.length === 0 && (
          <p className="subtitle">No hotspot data available yet</p>
        )}

        {hotspots.map((h, i) => (
          <div key={i} className="hotspot-row">
            <span>Lat: {h.lat}</span>
            <span>Lon: {h.lon}</span>
            <span>Alerts: {h.alerts}</span>
            <span className="risk">Risk: {h.risk}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Analytics;
