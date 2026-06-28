import { useEffect, useState } from "react";
import StatsSummary from "../components/StatsSummary.jsx";
import DecisionBadge from "../components/DecisionBadge.jsx";
import { fetchHealth, fetchLogs, fetchMlHealth, fetchStats, getApiBaseUrl } from "../api.js";
import { formatTime } from "../utils/format.js";

const PIPELINE_STEPS = [
  { key: "input", label: "Input", desc: "User prompt" },
  { key: "scan", label: "Rules + ML", desc: "Hybrid scan", active: true },
  { key: "provider", label: "Provider", desc: "LLM call" },
  { key: "output", label: "Output", desc: "Response scan" },
  { key: "log", label: "Log", desc: "SQLite store" },
];

const FEATURES = [
  {
    title: "Hybrid guard engine",
    desc: "Deterministic rules layered with ML cascade — Grok judge, sklearn, and HuggingFace fallback.",
    tag: "Core",
  },
  {
    title: "Multi-provider proxy",
    desc: "Routes through Grok, Gemini, and OpenAI with automatic failover and mock mode for testing.",
    tag: "LLM",
  },
  {
    title: "Production hardening",
    desc: "API key auth, rate limiting, security headers, structured logging, and health probes.",
    tag: "Ops",
  },
];

const TECH_STACK = [
  "FastAPI",
  "React",
  "SQLite",
  "scikit-learn",
  "Grok",
  "Gemini",
  "Vercel",
  "Render",
];

function PipelineIcon({ name }) {
  const icons = {
    input: (
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M12 5V19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        <path d="M7 10L12 5L17 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
    scan: (
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M12 4L19 7.5V13C19 17.2 15.8 20.2 12 21.5C8.2 20.2 5 17.2 5 13V7.5L12 4Z"
          stroke="currentColor"
          strokeWidth="1.75"
          strokeLinejoin="round"
        />
        <path d="M9.5 12L11 13.5L14.5 10" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
    provider: (
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <rect x="4" y="6" width="16" height="12" rx="2" stroke="currentColor" strokeWidth="1.75" />
        <path d="M9 10H15M9 14H12" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
      </svg>
    ),
    output: (
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M12 19V5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        <path d="M7 14L12 19L17 14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
    log: (
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M7 8H17M7 12H17M7 16H13" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
        <rect x="5" y="5" width="14" height="14" rx="2" stroke="currentColor" strokeWidth="1.75" />
      </svg>
    ),
  };
  return <span className="pipeline-icon">{icons[name]}</span>;
}

export default function Dashboard({ onOpenLogs, onOpenChat, ruleCount }) {
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

  const availableProviders = health?.providers?.filter((p) => p.available).length ?? 0;

  return (
    <div className="stack">
      <section className="hero" aria-label="Project overview">
        <div className="hero-content">
          <p className="hero-eyebrow">Open-source LLM safety gateway</p>
          <h2 className="hero-title">
            Inspect every prompt.
            <br />
            <span className="hero-title-accent">Enforce every decision.</span>
          </h2>
          <p className="hero-desc">
            A production-ready proxy that scans inputs and outputs with hybrid rules + ML,
            routes to real LLM providers, and logs every request for audit and debugging.
          </p>
          <div className="hero-actions">
            {onOpenChat && (
              <button type="button" className="btn btn-primary" onClick={onOpenChat}>
                Open live chat
              </button>
            )}
            <a
              href="https://github.com/Srikanthkn0/guardrail-gateway"
              target="_blank"
              rel="noreferrer"
              className="btn btn-secondary"
            >
              View on GitHub
            </a>
          </div>
        </div>
        <div className="hero-metrics">
          <div className="hero-metric hero-metric-highlight">
            <span className="hero-metric-value accent">
              {ruleCount != null ? ruleCount.toLocaleString() : "—"}
            </span>
            <span className="hero-metric-label">Guardrail rules</span>
          </div>
          <div className="hero-metric">
            <span className="hero-metric-value">{availableProviders || "—"}</span>
            <span className="hero-metric-label">Providers live</span>
          </div>
          <div className="hero-metric">
            <span className="hero-metric-value">{stats?.total_requests ?? "—"}</span>
            <span className="hero-metric-label">Requests logged</span>
          </div>
          <div className="hero-metric">
            <span className={`hero-metric-value ${mlHealth?.loaded ? "accent" : ""}`}>
              {mlHealth?.loaded ? "Active" : mlHealth ? "Idle" : "—"}
            </span>
            <span className="hero-metric-label">ML scanner</span>
          </div>
        </div>
      </section>

      <section className="feature-grid" aria-label="Capabilities">
        {FEATURES.map((feature) => (
          <article key={feature.title} className="feature-card">
            <span className="feature-tag">{feature.tag}</span>
            <h3>{feature.title}</h3>
            <p>{feature.desc}</p>
          </article>
        ))}
      </section>

      <div className="tech-stack" aria-label="Tech stack">
        {TECH_STACK.map((item) => (
          <span key={item} className="tech-pill">
            {item}
          </span>
        ))}
      </div>

      <section className="pipeline" aria-label="Gateway pipeline">
        <div className="pipeline-header">
          <h3>Request pipeline</h3>
          <span className="pipeline-hint">Every message flows through five stages</span>
        </div>
        <div className="pipeline-track">
          {PIPELINE_STEPS.map((step, index) => (
            <div key={step.label} style={{ display: "contents" }}>
              <div className={`pipeline-step ${step.active ? "pipeline-step-active" : ""}`}>
                <PipelineIcon name={step.key} />
                <span className="pipeline-label">{step.label}</span>
                <span className="pipeline-desc">{step.desc}</span>
              </div>
              {index < PIPELINE_STEPS.length - 1 && (
                <span className="pipeline-arrow" aria-hidden="true">
                  <svg viewBox="0 0 16 16" fill="none">
                    <path d="M3 8H13M13 8L9 4M13 8L9 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </span>
              )}
            </div>
          ))}
        </div>
      </section>

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
            <div className="stat-card-value accent">
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
            <span className="ml-card-title">Prompt Scanner</span>
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