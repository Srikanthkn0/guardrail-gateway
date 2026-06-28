import DecisionBadge from "./DecisionBadge.jsx";
import ScanPanel from "./ScanPanel.jsx";

const STEPS = [
  { key: "input", label: "Input scan", icon: "↓" },
  { key: "llm", label: "LLM call", icon: "▸" },
  { key: "output", label: "Output scan", icon: "↑" },
  { key: "final", label: "Final", icon: "✓" },
];

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
                <div className="flow-step-icon">{step.icon}</div>
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
                  →
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