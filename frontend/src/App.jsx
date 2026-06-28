import { useEffect, useState } from "react";
import Logo from "./components/Logo.jsx";
import NavIcon from "./components/NavIcon.jsx";
import Chat from "./pages/Chat.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Logs from "./pages/Logs.jsx";
import Rules from "./pages/Rules.jsx";
import { fetchLiveness } from "./api.js";

const NAV_ITEMS = [
  {
    id: "dashboard",
    label: "Overview",
    icon: "dashboard",
    description: "System health, pipeline metrics, and live status",
  },
  {
    id: "rules",
    label: "Rules",
    icon: "rules",
    description: "Test prompt and output guardrails in isolation",
  },
  {
    id: "chat",
    label: "Chat",
    icon: "chat",
    description: "Live LLM proxy with full gateway inspection",
  },
  {
    id: "logs",
    label: "Logs",
    icon: "logs",
    description: "Audit trail for every request and decision",
  },
];

const GITHUB_URL = "https://github.com/Srikanthkn0/guardrail-gateway";

export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [logsFocusId, setLogsFocusId] = useState(null);
  const [apiOnline, setApiOnline] = useState(null);

  function openLogs(requestId = null) {
    setLogsFocusId(requestId);
    setActiveTab("logs");
  }

  useEffect(() => {
    let cancelled = false;

    async function check() {
      try {
        await fetchLiveness();
        if (!cancelled) setApiOnline(true);
      } catch {
        if (!cancelled) setApiOnline(false);
      }
    }

    check();
    const interval = setInterval(check, 30_000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  const activeItem = NAV_ITEMS.find((item) => item.id === activeTab) ?? NAV_ITEMS[0];

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <Logo size={40} showWordmark />
        </div>

        <nav className="sidebar-nav" aria-label="Main">
          {NAV_ITEMS.map((item) => (
            <button
              key={item.id}
              type="button"
              className={`sidebar-link ${activeTab === item.id ? "sidebar-link-active" : ""}`}
              onClick={() => setActiveTab(item.id)}
            >
              <NavIcon name={item.icon} />
              {item.label}
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <a href={GITHUB_URL} target="_blank" rel="noreferrer" className="sidebar-github">
            <NavIcon name="github" />
            Source
            <NavIcon name="external" className="nav-icon-external" />
          </a>
          <span className="sidebar-version">v1.0</span>
        </div>
      </aside>

      <div className="app-body">
        <header className="topbar">
          <div className="topbar-title">
            <div className="topbar-heading">
              <h1>{activeItem.label}</h1>
              <p className="topbar-subtitle">{activeItem.description}</p>
            </div>
            <div className="topbar-actions">
              <span className="topbar-status">
                <span
                  className={`status-dot ${apiOnline === false ? "status-dot-offline" : ""}`}
                />
                {apiOnline === null && "Checking API…"}
                {apiOnline === true && "API online"}
                {apiOnline === false && "API unreachable"}
              </span>
              {activeTab !== "chat" && (
                <button
                  type="button"
                  className="btn btn-primary btn-sm-inline"
                  onClick={() => setActiveTab("chat")}
                >
                  Try live chat
                </button>
              )}
            </div>
          </div>
        </header>

        <main className="main-content">
          {activeTab === "dashboard" && (
            <Dashboard onOpenLogs={openLogs} onOpenChat={() => setActiveTab("chat")} />
          )}
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