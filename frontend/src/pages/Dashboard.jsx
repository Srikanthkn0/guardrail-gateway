import { useEffect, useState } from "react";
import StatsSummary from "../components/StatsSummary.jsx";
import DecisionBadge from "../components/DecisionBadge.jsx";
import { fetchHealth, fetchLogs, fetchMlHealth, fetchStats, getApiBaseUrl } from "../api.js";
import { formatTime } from "../utils/format.js";

export default function Dashboard({ onOpenLogs, ruleCount }) {
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
        <p>
          Gateway health, scanner status, and recent requests.
          {ruleCount != null ? ` ${ruleCount.toLocaleString()} rules loaded.` : ""}
        </p>
      </header>

      {stats && (
        <div className="stat-grid">
          <div className="stat-card">
            <div className="stat-card-label">Total requests</div>
            <div className="stat-card-value">{stats.total_requests}</div>
          </div>
          <div className="stat-card">
            <div className="stat-card-label">Block rate</div>
            <div className="stat-card-value fail">
              {(stats.block_rate * 100).toFixed(1)}%
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-card-label">Warn rate</div>
            <div className="stat-card-value warn">
              {(stats.warn_rate * 100).toFixed(1)}%
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-card-label">Avg latency</div>
            <div className="stat-card-value">
              {stats.avg_latency_ms != null ? `${Math.round(stats.avg_latency_ms)}ms` : "n/a"}
            </div>
          </div>
        </div>
      )}

      <div className="card-grid">
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
            <>
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

              {health.providers?.length > 0 && (
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
                          <td>
                            <span className={`provider-dot ${item.available ? "provider-dot-on" : ""}`}>
                              {item.available ? "online" : "offline"}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          )}
        </section>

        <section className="ml-card">
          <div className="ml-card-header">
            <span className="ml-card-title">Prompt scanner</span>
            {mlHealth && <span className={`ml-badge ${mlBadgeClass()}`}>{mlBadgeLabel()}</span>}
          </div>

          {!mlHealth && <p className="status-text">Loading ML status...</p>}

          {mlHealth && (
            <div className="ml-details">
              <div className="ml-detail">
                <div className="ml-detail-label">Backend</div>
                <div className="ml-detail-value">{mlHealth.backend}</div>
              </div>
              <div className="ml-detail">
                <div className="ml-detail-label">Block threshold</div>
                <div className="ml-detail-value">{mlHealth.block_threshold}</div>
              </div>
              <div className="ml-detail">
                <div className="ml-detail-label">Model</div>
                <div className="ml-detail-value mono">{mlHealth.model}</div>
              </div>
              <div className="ml-detail">
                <div className="ml-detail-label">Warn threshold</div>
                <div className="ml-detail-value">{mlHealth.warn_threshold}</div>
              </div>
            </div>
          )}
        </section>
      </div>

      {stats && (
        <section className="card">
          <h3>Decision breakdown</h3>
          <StatsSummary stats={stats} compact showProviders />
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
              View all logs
            </button>
          )}
        </div>

        {recentLogs.length === 0 && (
          <p className="status-text">No requests yet. Send a prompt from Chat.</p>
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