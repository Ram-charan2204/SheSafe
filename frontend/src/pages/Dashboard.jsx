import { useEffect, useState } from "react";
import "../styles/dashboard.css";

function Dashboard() {
  const [stats, setStats] = useState({
    persons: 0,
    women: 0,
    alerts: 0
  });

  useEffect(() => {
  fetch("/api/stats").then(r => r.json()).then(setStats)
}, [])


  useEffect(() => {
    const fetchStats = () => {
      fetch("/api/stats")
        .then((res) => res.json())
        .then((data) =>
          setStats((prev) => ({ ...prev, ...data }))
        );

      fetch("/api/alerts")
        .then((res) => res.json())
        .then((alerts) =>
          setStats((prev) => ({ ...prev, alerts: alerts.length }))
        );
    };

    fetchStats();
    const interval = setInterval(fetchStats, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="page">
      <h1>Dashboard</h1>
      <p className="subtitle">System overview and real-time safety metrics</p>

      <div className="kpi-grid">
        <div className="kpi-card">
          <span className="kpi-title">Current Persons</span>
          <span className="kpi-value">{stats.persons}</span>
        </div>

        <div className="kpi-card">
          <span className="kpi-title">Women Detected</span>
          <span className="kpi-value">{stats.women}</span>
        </div>

        <div className="kpi-card alert">
          <span className="kpi-title">Active Alerts</span>
          <span className="kpi-value">{stats.alerts}</span>
        </div>

        <div className="kpi-card success">
          <span className="kpi-title">System Status</span>
          <span className="kpi-value">ONLINE</span>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
