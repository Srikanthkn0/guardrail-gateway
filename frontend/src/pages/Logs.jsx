import { useCallback, useEffect, useState } from "react";
import StatsSummary from "../components/StatsSummary.jsx";
import DecisionBadge from "../components/DecisionBadge.jsx";
import HitTable from "../components/HitTable.jsx";
import { fetchLogDetail, fetchLogs, fetchStats } from "../api.js";
import { formatTime } from "../utils/format.js";

const PAGE_SIZE = 20;

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

  async function handleDecisionChange(event) {
    await applyFilters(event.target.value, providerFilter);
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
    <div className="stack">
      <header className="page-header">
        <p>Gateway requests stored in SQLite. Click a row for rule hits.</p>
      </header>

      <section className="card">
        <div className="toolbar">
          <h3>Stats</h3>
          <button
            type="button"
            className="btn btn-secondary btn-sm-inline"
            onClick={() => loadLogs({ nextOffset: offset })}
            disabled={loading}
          >
            Refresh
          </button>
        </div>
        <StatsSummary stats={stats} showProviders={false} />
      </section>

      <section className="card">
        <div className="toolbar">
          <h3>
            Requests ({total})
            {total > 0 && (
              <span className="status-text toolbar-meta">
                page {page} of {totalPages}
              </span>
            )}
          </h3>
          <div className="filter-row">
            <label className="field field-inline">
              <span>Decision</span>
              <select value={decisionFilter} onChange={handleDecisionChange}>
                <option value="">All</option>
                <option value="allow">allow</option>
                <option value="warn">warn</option>
                <option value="block">block</option>
              </select>
            </label>
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
        </div>

        {loading && <p className="status-text">Loading logs...</p>}

        {error && (
          <div className="alert alert-error">
            <strong>Error.</strong> {error}
          </div>
        )}

        {!loading && logs.length === 0 && (
          <p className="status-text">No requests match the current filters.</p>
        )}

        {!loading && logs.length > 0 && (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Decision</th>
                  <th>Provider</th>
                  <th>Prompt</th>
                  <th>Hits</th>
                  <th>Forwarded</th>
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
                    <td>
                      {log.input_hit_count}/{log.output_hit_count}
                    </td>
                    <td>{log.forwarded ? "yes" : "no"}</td>
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
              {offset + 1}-{Math.min(offset + PAGE_SIZE, total)} of {total}
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

        {selectedId && (
          <div className="result-block">
            <div className="result-header">
              <span>Log detail</span>
              <span className="mono">{selectedId}</span>
            </div>
            {loadingDetail && <p className="status-text">Loading detail...</p>}
            {detail && (
              <>
                <div className="status-list">
                  <div className="status-list-item">
                    <span className="label">Input decision</span>
                    <span className="value">{detail.input_decision}</span>
                  </div>
                  <div className="status-list-item">
                    <span className="label">Output decision</span>
                    <span className="value">{detail.output_decision || "n/a"}</span>
                  </div>
                  <div className="status-list-item">
                    <span className="label">Latency</span>
                    <span className="value">
                      {detail.latency_ms != null ? `${Math.round(detail.latency_ms)} ms` : "n/a"}
                    </span>
                  </div>
                  <div className="status-list-item">
                    <span className="label">Redacted</span>
                    <span className="value">{detail.response_redacted ? "yes" : "no"}</span>
                  </div>
                </div>

                <ul className="plain-list">
                  {detail.reasons.map((reason) => (
                    <li key={reason}>{reason}</li>
                  ))}
                </ul>

                {detail.response_text ? (
                  <div className="response-box">
                    <span className="label">Stored response</span>
                    <pre className="response-text">{detail.response_text}</pre>
                  </div>
                ) : (
                  detail.response_redacted && (
                    <p className="status-text">Response redacted at gateway.</p>
                  )
                )}

                <HitTable hits={detail.input_hits} phaseLabel="input" />
                <HitTable hits={detail.output_hits} phaseLabel="output" />
              </>
            )}
          </div>
        )}
      </section>
    </div>
  );
}