import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";

import Dashboard from "./pages/Dashboard";
import LiveCameras from "./pages/LiveCameras";
import Alerts from "./pages/Alerts";
import Analytics from "./pages/Analytics";

import "./styles/theme.css";

function App() {
  return (
    <Router>
      <div className="app-root">
        <Navbar />

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/cameras" element={<LiveCameras />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/analytics" element={<Analytics />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
