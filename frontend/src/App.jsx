import { useState } from "react";
import Logo from "./components/Logo.jsx";
import Chat from "./pages/Chat.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Logs from "./pages/Logs.jsx";
import Rules from "./pages/Rules.jsx";

const NAV_ITEMS = [
  { id: "dashboard", label: "Overview", icon: "◉" },
  { id: "rules", label: "Rules", icon: "⬡" },
  { id: "chat", label: "Chat", icon: "▸" },
  { id: "logs", label: "Logs", icon: "≡" },
];

const GITHUB_URL = "https://github.com/Srikanthkn0/guardrail-gateway";

export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [logsFocusId, setLogsFocusId] = useState(null);

  function openLogs(requestId = null) {
    setLogsFocusId(requestId);
    setActiveTab("logs");
  }

  const activeLabel = NAV_ITEMS.find((item) => item.id === activeTab)?.label ?? "";

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <Logo size={32} />
          <div className="sidebar-brand-text">
            <span className="sidebar-title">Guardrail</span>
            <span className="sidebar-subtitle">Safety Gateway</span>
          </div>
        </div>

        <nav className="sidebar-nav" aria-label="Main">
          {NAV_ITEMS.map((item) => (
            <button
              key={item.id}
              type="button"
              className={`sidebar-link ${activeTab === item.id ? "sidebar-link-active" : ""}`}
              onClick={() => setActiveTab(item.id)}
            >
              <span className="sidebar-link-icon" aria-hidden="true">
                {item.icon}
              </span>
              {item.label}
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <a href={GITHUB_URL} target="_blank" rel="noreferrer" className="sidebar-github">
            GitHub
          </a>
          <span className="sidebar-version">v1.0</span>
        </div>
      </aside>

      <div className="app-body">
        <header className="topbar">
          <div className="topbar-title">
            <h1>{activeLabel}</h1>
            <span className="topbar-status">
              <span className="status-dot" />
              Gateway active
            </span>
          </div>
        </header>

        <main className="main-content">
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
      </div>
    </div>
  );
}