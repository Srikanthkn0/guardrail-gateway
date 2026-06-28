import { useEffect, useState } from "react";
import StatsSummary from "../components/StatsSummary.jsx";
import DecisionBadge from "../components/DecisionBadge.jsx";
import { fetchHealth, fetchLogs, fetchMlHealth, fetchStats, getApiBaseUrl } from "../api.js";
import { formatTime } from "../utils/format.js";

export default function Dashboard({ onOpenLogs }) {
  const [health, setHealth] = useState(null);
  const [mlHealth, setMlHealth] = useState(null);
  const [stats, setStats] = useState(null);
  const [recentLogs, setRecentLogs] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const [healthData, mlData, statsData, logsData] = await Promise.all([
          fetchHealth(),
          fetchMlHealth().catch(() => null),
          fetchStats().catch(() => null),
          fetchLogs({ limit: 5 }).catch(() => ({ logs: [] })),
        ]);
        if (!cancelled) {
          setHealth(healthData);
          setMlHealth(mlData);
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

  function mlBadgeClass() {
    if (!mlHealth?.enabled) return "ml-badge-off";
    if (mlHealth.loaded) return "ml-badge-ready";
    return "ml-badge-error";
  }

  function mlBadgeLabel() {
    if (!mlHealth?.enabled) return "disabled";
    if (mlHealth.loaded) return "ready";
    return "not loaded";
  }

  return (
    <div className="stack">
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
              Local: <code>cd backend && PORT=8010 ./run.sh</code>. Production:
              {" "}
              <a href="https://guardrail-gateway-api.onrender.com/health" target="_blank" rel="noreferrer">
                guardrail-gateway-api.onrender.com
              </a>
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

      {mlHealth && (
        <section className="card">
          <div className="toolbar">
            <h3>Prompt scanner</h3>
            <span className={`ml-badge ${mlBadgeClass()}`}>{mlBadgeLabel()}</span>
          </div>
          <div className="status-list">
            <div className="status-list-item">
              <span className="label">Backend</span>
              <span className="value">{mlHealth.backend}</span>
            </div>
            <div className="status-list-item">
              <span className="label">Model</span>
              <span className="value mono">{mlHealth.model || "n/a"}</span>
            </div>
            <div className="status-list-item">
              <span className="label">Block threshold</span>
              <span className="value">{mlHealth.block_threshold}</span>
            </div>
            <div className="status-list-item">
              <span className="label">Warn threshold</span>
              <span className="value">{mlHealth.warn_threshold}</span>
            </div>
          </div>
        </section>
      )}

      <section className="card">
        <h3>Gateway stats</h3>
        {stats ? (
          <StatsSummary stats={stats} />
        ) : (
          <p className="status-text">No stats yet. Stats appear after the API is online and requests are logged.</p>
        )}
      </section>

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