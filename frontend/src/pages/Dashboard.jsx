import { useEffect, useState } from "react";
import StatsSummary from "../components/StatsSummary.jsx";
import DecisionBadge from "../components/DecisionBadge.jsx";
import { fetchHealth, fetchLogs, fetchStats, getApiBaseUrl } from "../api.js";
import { formatTime } from "../utils/format.js";

export default function Dashboard({ onOpenLogs }) {
  const [health, setHealth] = useState(null);
  const [stats, setStats] = useState(null);
  const [recentLogs, setRecentLogs] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const [healthData, statsData, logsData] = await Promise.all([
          fetchHealth(),
          fetchStats().catch(() => null),
          fetchLogs({ limit: 5 }).catch(() => ({ logs: [] })),
        ]);
        if (!cancelled) {
          setHealth(healthData);
          setStats(statsData);
          setRecentLogs(logsData.logs || []);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message);
          setHealth(null);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="stack">
      <section className="hero-card">
        <div className="hero-content">
          <h2>LLM safety at the gateway layer</h2>
          <p>
            Scan inputs and outputs with rules plus ML classification, route allowed prompts to
            providers, and log every decision with full traceability.
          </p>
          <div className="pill-row">
            <span className="pill">Hybrid guard</span>
            <span className="pill pill-secondary">ML classifier</span>
            <span className="pill">Request logs</span>
          </div>
        </div>
      </section>

      <header className="page-header">
        <h2>Overview</h2>
        <p>Gateway health, decision breakdown, and recent traffic.</p>
      </header>

      <section className="card">
        <h3>Backend</h3>

        <div className="status-list">
          <div className="status-list-item">
            <span className="label">API URL</span>
            <span className="value mono">{getApiBaseUrl()}</span>
          </div>
        </div>

        {loading && <p className="status-text">Checking backend...</p>}

        {error && (
          <div className="alert alert-error">
            <strong>Backend unreachable.</strong> {error}
            <p className="hint">
              Local: start the API on port 8000 or 8010. Production uses the Vercel proxy.
            </p>
          </div>
        )}

        {health && (
          <div className="status-list">
            <div className="status-list-item">
              <span className="label">Status</span>
              <span className="value">{health.status}</span>
            </div>
            <div className="status-list-item">
              <span className="label">Environment</span>
              <span className="value">{health.environment}</span>
            </div>
            <div className="status-list-item">
              <span className="label">Default provider</span>
              <span className="value">{health.default_provider}</span>
            </div>
          </div>
        )}

        {health?.providers?.length > 0 && (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Provider</th>
                  <th>Available</th>
                </tr>
              </thead>
              <tbody>
                {health.providers.map((item) => (
                  <tr key={item.id}>
                    <td>{item.label}</td>
                    <td>{item.available ? "yes" : "no"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {stats && (
        <section className="card">
          <h3>Gateway stats</h3>
          <StatsSummary stats={stats} />
        </section>
      )}

      <section className="card">
        <div className="toolbar">
          <h3>Recent requests</h3>
          {onOpenLogs && (
            <button
              type="button"
              className="btn btn-secondary btn-sm-inline"
              onClick={() => onOpenLogs()}
            >
              Open logs
            </button>
          )}
        </div>

        {recentLogs.length === 0 && (
          <p className="status-text">No requests yet. Send a prompt from the Chat tab.</p>
        )}

        {recentLogs.length > 0 && (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Decision</th>
                  <th>Provider</th>
                  <th>Prompt</th>
                </tr>
              </thead>
              <tbody>
                {recentLogs.map((log) => (
                  <tr
                    key={log.request_id}
                    className={onOpenLogs ? "row-clickable" : undefined}
                    onClick={() => onOpenLogs?.(log.request_id)}
                  >
                    <td className="mono">{formatTime(log.created_at)}</td>
                    <td>
                      <DecisionBadge decision={log.final_decision} />
                    </td>
                    <td>{log.provider || "n/a"}</td>
                    <td className="cell-clip" title={log.prompt_preview}>
                      {log.prompt_preview}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}