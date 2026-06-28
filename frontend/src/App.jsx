import { useState } from "react";
import Logo from "./components/Logo.jsx";
import Chat from "./pages/Chat.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Logs from "./pages/Logs.jsx";
import Rules from "./pages/Rules.jsx";

const TABS = [
  { id: "dashboard", label: "Overview" },
  { id: "rules", label: "Rules" },
  { id: "chat", label: "Chat" },
  { id: "logs", label: "Logs" },
];

const GITHUB_URL = "https://github.com/Srikanthkn0/guardrail-gateway";

export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [logsFocusId, setLogsFocusId] = useState(null);

  function openLogs(requestId = null) {
    setLogsFocusId(requestId);
    setActiveTab("logs");
  }

  return (
    <div className="app">
      <div className="app-glow" aria-hidden="true" />

      <header className="app-header">
        <div className="header-inner">
          <div className="brand">
            <Logo size={36} />
            <div className="brand-text">
              <span className="brand-name">Guardrail Gateway</span>
              <span className="brand-tagline">Rules · ML classifier · Request inspection</span>
            </div>
          </div>
          <nav className="nav-tabs" aria-label="Main">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                type="button"
                className={`nav-tab ${activeTab === tab.id ? "nav-tab-active" : ""}`}
                onClick={() => setActiveTab(tab.id)}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      <main className="app-main">
        {activeTab === "dashboard" && <Dashboard onOpenLogs={openLogs} />}
        {activeTab === "rules" && <Rules />}
        {activeTab === "chat" && <Chat onViewLog={openLogs} />}
        {activeTab === "logs" && (
          <Logs
            focusRequestId={logsFocusId}
            onFocusHandled={() => setLogsFocusId(null)}
          />
        )}
      </main>

      <footer className="app-footer">
        <div className="footer-inner">
          <div className="footer-brand">
            <Logo size={20} />
            <span>LLM safety gateway — open source</span>
          </div>
          <div className="footer-links">
            <a href={GITHUB_URL} target="_blank" rel="noreferrer">
              GitHub
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}