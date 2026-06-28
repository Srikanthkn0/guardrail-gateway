import DecisionBadge from "./DecisionBadge.jsx";
import ScanPanel from "./ScanPanel.jsx";

const STEPS = [
  { key: "input", label: "Input scan", icon: "input" },
  { key: "llm", label: "LLM call", icon: "llm" },
  { key: "output", label: "Output scan", icon: "output" },
  { key: "final", label: "Final", icon: "final" },
];

function FlowIcon({ name }) {
  const icons = {
    input: (
      <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
        <path d="M10 4V16" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
        <path d="M6 8L10 4L14 8" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
    llm: (
      <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
        <rect x="3" y="5" width="14" height="10" rx="2" stroke="currentColor" strokeWidth="1.5" />
        <path d="M7 9H13M7 12H10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      </svg>
    ),
    output: (
      <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
        <path d="M10 16V4" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
        <path d="M6 12L10 16L14 12" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
    final: (
      <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
        <circle cx="10" cy="10" r="7" stroke="currentColor" strokeWidth="1.5" />
        <path d="M7 10L9 12L13 8" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  };
  return <span className="flow-step-icon">{icons[name]}</span>;
}

function stepStatus(stepKey, result) {
  if (!result) return "pending";

  if (stepKey === "input") {
    return result.input_scan?.decision || "pending";
  }
  if (stepKey === "llm") {
    if (!result.forwarded) return "skipped";
    return result.llm_called ? "done" : "pending";
  }
  if (stepKey === "output") {
    if (!result.forwarded) return "skipped";
    return result.output_scan?.decision || "pending";
  }
  if (stepKey === "final") {
    return result.final_decision || "pending";
  }
  return "pending";
}

function statusClass(status) {
  if (status === "allow" || status === "done") return "flow-step-allow";
  if (status === "warn") return "flow-step-warn";
  if (status === "block") return "flow-step-block";
  if (status === "skipped") return "flow-step-skipped";
  return "";
}

export default function GatewayFlow({ result }) {
  if (!result) return null;

  return (
    <div className="gateway-flow">
      <div className="flow-steps">
        {STEPS.map((step, index) => {
          const status = stepStatus(step.key, result);
          return (
            <div key={step.key} style={{ display: "contents" }}>
              <div className={`flow-step ${statusClass(status)}`}>
                <FlowIcon name={step.icon} />
                <span className="flow-step-label">{step.label}</span>
                <span className="flow-step-status">
                  {step.key === "llm" && status === "done" && (
                    <>
                      {result.provider}/{result.model}
                      {result.latency_ms != null && ` · ${Math.round(result.latency_ms)}ms`}
                    </>
                  )}
                  {step.key === "llm" && status === "skipped" && "not called"}
                  {step.key === "input" && status !== "pending" && (
                    <DecisionBadge decision={result.input_scan.decision} />
                  )}
                  {step.key === "output" && status !== "pending" && status !== "skipped" && (
                    <DecisionBadge decision={result.output_scan.decision} />
                  )}
                  {step.key === "final" && status !== "pending" && (
                    <DecisionBadge decision={result.final_decision} />
                  )}
                </span>
              </div>
              {index < STEPS.length - 1 && (
                <span className="flow-arrow" aria-hidden="true">
                  <svg viewBox="0 0 16 16" fill="none">
                    <path d="M3 8H13M13 8L9 4M13 8L9 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </span>
              )}
            </div>
          );
        })}
      </div>

      <div className="flow-details">
        <ScanPanel title="Input scan" scan={result.input_scan} />

        {result.llm_called && (
          <div className="llm-call-card">
            <div className="llm-call-header">
              <span>LLM response</span>
              <span className="mono">
                {result.provider} · {result.model}
              </span>
            </div>
            {result.response_text ? (
              <div className="chat-bubble assistant">{result.response_text}</div>
            ) : result.response_redacted ? (
              <div className="chat-bubble blocked">
                <strong>Response redacted.</strong> The model returned text that failed output
                scanning ({result.output_scan?.hits?.length || 0} rule hit
                {(result.output_scan?.hits?.length || 0) === 1 ? "" : "s"}). Raw text is not
                shown to prevent leaking sensitive content.
              </div>
            ) : null}
          </div>
        )}

        {!result.llm_called && result.input_scan?.decision === "block" && (
          <div className="chat-bubble blocked">
            <strong>Request blocked before LLM.</strong> Input scanning flagged this prompt as
            malicious. No provider call was made.
          </div>
        )}

        {result.output_scan && <ScanPanel title="Output scan" scan={result.output_scan} />}

        {result.reasons?.length > 0 && (
          <div className="flow-reasons">
            <span className="flow-reasons-label">Gateway reasons</span>
            <ul className="plain-list">
              {result.reasons.map((reason) => (
                <li key={reason}>{reason}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}