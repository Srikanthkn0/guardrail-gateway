import { useCallback, useEffect, useState } from "react";
import DecisionBadge from "../components/DecisionBadge.jsx";
import HitTable from "../components/HitTable.jsx";
import { fetchLogDetail, fetchLogs, fetchStats } from "../api.js";
import { formatTime } from "../utils/format.js";

const PAGE_SIZE = 20;

const DECISION_FILTERS = [
  { value: "", label: "All" },
  { value: "allow", label: "Passed" },
  { value: "warn", label: "Warning" },
  { value: "block", label: "Blocked" },
];

export default function Logs({ focusRequestId, onFocusHandled }) {
  const [stats, setStats] = useState(null);
  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [decisionFilter, setDecisionFilter] = useState("");
  const [providerFilter, setProviderFilter] = useState("");
  const [selectedId, setSelectedId] = useState(null);
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [error, setError] = useState(null);

  const loadDetail = useCallback(async (requestId) => {
    setSelectedId(requestId);
    setLoadingDetail(true);
    try {
      const data = await fetchLogDetail(requestId);
      setDetail(data);
    } catch (err) {
      setError(err.message);
      setDetail(null);
    } finally {
      setLoadingDetail(false);
    }
  }, []);

  const loadLogs = useCallback(
    async ({
      nextOffset = offset,
      decision = decisionFilter,
      provider = providerFilter,
      keepSelection = false,
    } = {}) => {
      setLoading(true);
      setError(null);
      try {
        const [statsData, logsData] = await Promise.all([
          fetchStats(),
          fetchLogs({
            limit: PAGE_SIZE,
            offset: nextOffset,
            decision: decision || undefined,
            provider: provider || undefined,
          }),
        ]);
        setStats(statsData);
        setLogs(logsData.logs);
        setTotal(logsData.count);
        setOffset(nextOffset);
        if (!keepSelection) {
          setSelectedId(null);
          setDetail(null);
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    },
    [offset, decisionFilter, providerFilter],
  );

  useEffect(() => {
    loadLogs({ nextOffset: 0 });
  }, []);

  useEffect(() => {
    if (!focusRequestId) return;
    loadLogs({ nextOffset: 0, keepSelection: true }).then(() => {
      loadDetail(focusRequestId);
      onFocusHandled?.();
    });
  }, [focusRequestId]);

  async function applyFilters(decision, provider) {
    setDecisionFilter(decision);
    setProviderFilter(provider);
    await loadLogs({
      nextOffset: 0,
      decision,
      provider,
    });
  }

  async function handleDecisionFilter(value) {
    await applyFilters(value, providerFilter);
  }

  async function handleProviderChange(event) {
    await applyFilters(decisionFilter, event.target.value);
  }

  async function handleSelect(requestId) {
    if (selectedId === requestId) {
      setSelectedId(null);
      setDetail(null);
      return;
    }
    await loadDetail(requestId);
  }

  const page = Math.floor(offset / PAGE_SIZE) + 1;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const providerOptions = stats?.by_provider?.map((row) => row.provider) || [];

  return (
    <div className="stack logs-page">
      {stats && (
        <div className="logs-stats">
          <div className="logs-stat-card">
            <span className="logs-stat-value">{stats.total_requests}</span>
            <span className="logs-stat-label">Total requests</span>
          </div>
          <div className="logs-stat-card logs-stat-pass">
            <span className="logs-stat-value">{stats.allow_count}</span>
            <span className="logs-stat-label">Passed</span>
          </div>
          <div className="logs-stat-card logs-stat-warn">
            <span className="logs-stat-value">{stats.warn_count}</span>
            <span className="logs-stat-label">Warnings</span>
          </div>
          <div className="logs-stat-card logs-stat-block">
            <span className="logs-stat-value">{stats.block_count}</span>
            <span className="logs-stat-label">Blocked</span>
          </div>
          <div className="logs-stat-card">
            <span className="logs-stat-value">
              {stats.avg_latency_ms != null ? `${Math.round(stats.avg_latency_ms)}ms` : "n/a"}
            </span>
            <span className="logs-stat-label">Avg latency</span>
          </div>
        </div>
      )}

      <div className="logs-layout">
        <section className="card logs-list-panel">
          <div className="toolbar">
            <h3>
              Requests
              <span className="toolbar-meta">({total})</span>
            </h3>
            <button
              type="button"
              className="btn btn-secondary btn-sm-inline"
              onClick={() => loadLogs({ nextOffset: offset })}
              disabled={loading}
            >
              Refresh
            </button>
          </div>

          <div className="filter-row logs-filters">
            <div className="pill-group" role="group" aria-label="Decision filter">
              {DECISION_FILTERS.map((opt) => (
                <button
                  key={opt.value || "all"}
                  type="button"
                  className={`pill ${decisionFilter === opt.value ? "pill-active" : ""}`}
                  onClick={() => handleDecisionFilter(opt.value)}
                >
                  {opt.label}
                </button>
              ))}
            </div>
            <label className="field field-inline">
              <span>Provider</span>
              <select value={providerFilter} onChange={handleProviderChange}>
                <option value="">All</option>
                {providerOptions.map((provider) => (
                  <option key={provider} value={provider}>
                    {provider}
                  </option>
                ))}
              </select>
            </label>
          </div>

          {loading && <p className="status-text">Loading logs...</p>}

          {error && (
            <div className="alert alert-error">
              <strong>Error.</strong> {error}
            </div>
          )}

          {!loading && logs.length === 0 && (
            <p className="status-text">No requests yet. Send a message from Chat.</p>
          )}

          {!loading && logs.length > 0 && (
            <div className="table-wrap logs-table-wrap">
              <table className="table logs-table">
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Decision</th>
                    <th>Provider</th>
                    <th>Prompt</th>
                    <th>Hits</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log) => (
                    <tr
                      key={log.request_id}
                      className={selectedId === log.request_id ? "row-selected" : "row-clickable"}
                      onClick={() => handleSelect(log.request_id)}
                    >
                      <td className="mono">{formatTime(log.created_at)}</td>
                      <td>
                        <DecisionBadge decision={log.final_decision} />
                      </td>
                      <td>{log.provider || "n/a"}</td>
                      <td className="cell-clip" title={log.prompt_preview}>
                        {log.prompt_preview}
                      </td>
                      <td className="mono logs-hits">
                        {log.input_hit_count}/{log.output_hit_count}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {total > PAGE_SIZE && (
            <div className="pagination">
              <button
                type="button"
                className="btn btn-secondary btn-sm-inline"
                disabled={offset === 0 || loading}
                onClick={() => loadLogs({ nextOffset: Math.max(0, offset - PAGE_SIZE) })}
              >
                Previous
              </button>
              <span className="status-text">
                Page {page} of {totalPages} | {offset + 1}-{Math.min(offset + PAGE_SIZE, total)} of {total}
              </span>
              <button
                type="button"
                className="btn btn-secondary btn-sm-inline"
                disabled={offset + PAGE_SIZE >= total || loading}
                onClick={() => loadLogs({ nextOffset: offset + PAGE_SIZE })}
              >
                Next
              </button>
            </div>
          )}
        </section>

        <section className="card logs-detail-panel">
          <div className="toolbar">
            <h3>Request detail</h3>
            {selectedId && (
              <span className="mono logs-detail-id">{selectedId.slice(0, 8)}...</span>
            )}
          </div>

          {!selectedId && !loadingDetail && (
            <div className="logs-detail-empty">
              <p className="status-text">
                Select a request to inspect input/output decisions, rule hits, and stored responses.
              </p>
            </div>
          )}

          {loadingDetail && <p className="status-text">Loading detail...</p>}

          {detail && (
            <div className="logs-detail-content">
              <div className="logs-detail-hero">
                <DecisionBadge decision={detail.final_decision} />
                <span className="logs-detail-time mono">{formatTime(detail.created_at)}</span>
              </div>

              <div className="status-list logs-detail-grid">
                <div className="status-list-item">
                  <span className="label">Input</span>
                  <span className="value">
                    <DecisionBadge decision={detail.input_decision} />
                  </span>
                </div>
                <div className="status-list-item">
                  <span className="label">Output</span>
                  <span className="value">
                    <DecisionBadge decision={detail.output_decision || "allow"} />
                  </span>
                </div>
                <div className="status-list-item">
                  <span className="label">Provider</span>
                  <span className="value">{detail.provider || "n/a"}</span>
                </div>
                <div className="status-list-item">
                  <span className="label">Latency</span>
                  <span className="value">
                    {detail.latency_ms != null ? `${Math.round(detail.latency_ms)} ms` : "n/a"}
                  </span>
                </div>
                <div className="status-list-item">
                  <span className="label">Forwarded</span>
                  <span className="value">{detail.forwarded ? "yes" : "no"}</span>
                </div>
                <div className="status-list-item">
                  <span className="label">Redacted</span>
                  <span className="value">{detail.response_redacted ? "yes" : "no"}</span>
                </div>
              </div>

              {detail.reasons?.length > 0 && (
                <div className="logs-reasons">
                  <span className="flow-reasons-label">Reasons</span>
                  <ul className="plain-list">
                    {detail.reasons.map((reason) => (
                      <li key={reason}>{reason}</li>
                    ))}
                  </ul>
                </div>
              )}

              {detail.response_text ? (
                <div className="response-box">
                  <span className="label">Stored response</span>
                  <pre className="response-text">{detail.response_text}</pre>
                </div>
              ) : (
                detail.response_redacted && (
                  <p className="status-text logs-redacted-note">Response redacted at gateway.</p>
                )
              )}

              <HitTable hits={detail.input_hits} phaseLabel="input" />
              <HitTable hits={detail.output_hits} phaseLabel="output" />
            </div>
          )}
        </section>
      </div>
    </div>
  );
}