import { useState } from "react";
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

export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [logsFocusId, setLogsFocusId] = useState(null);

  function openLogs(requestId = null) {
    setLogsFocusId(requestId);
    setActiveTab("logs");
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-inner">
          <div className="brand">
            <div className="brand-mark" aria-hidden="true" />
            <div>
              <h1>Guardrail Gateway</h1>
              <p className="brand-sub">LLM request inspection and logging</p>
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
        <span>Guardrail Gateway</span>
      </footer>
    </div>
  );
}