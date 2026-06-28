function resolveApiBaseUrl() {
  const configured = import.meta.env.VITE_API_BASE_URL?.trim() || "";
  const isLocalhost =
    configured.includes("localhost") || configured.includes("127.0.0.1");

  if (import.meta.env.PROD) {
    if (configured && !isLocalhost) {
      return configured;
    }
    return "";
  }

  return configured || "http://localhost:8000";
}

const API_BASE_URL = resolveApiBaseUrl();

export function getApiBaseUrl() {
  if (API_BASE_URL) {
    return API_BASE_URL;
  }
  if (import.meta.env.PROD && typeof window !== "undefined") {
    return window.location.origin;
  }
  return "http://localhost:8000";
}

async function parseResponse(response) {
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = data.detail || `Request failed (${response.status})`;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return data;
}

function apiUrl(path) {
  return `${getApiBaseUrl()}${path}`;
}

export async function fetchHealth() {
  const response = await fetch(apiUrl("/health"));
  return parseResponse(response);
}

export async function fetchMlHealth() {
  const response = await fetch(apiUrl("/health/ml"));
  return parseResponse(response);
}

export async function fetchRules() {
  const response = await fetch(apiUrl("/rules"));
  return parseResponse(response);
}

export async function testRules(text, outputText = "") {
  const body = { text };
  if (outputText.trim()) {
    body.output_text = outputText;
  }
  const response = await fetch(apiUrl("/rules/test"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return parseResponse(response);
}

export async function gatewayChat(prompt, provider) {
  const body = { prompt };
  if (provider) {
    body.provider = provider;
  }
  const response = await fetch(apiUrl("/gateway/chat"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return parseResponse(response);
}

export async function fetchLogs({ limit = 50, offset = 0, decision, provider } = {}) {
  const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  if (decision) {
    params.set("decision", decision);
  }
  if (provider) {
    params.set("provider", provider);
  }
  const response = await fetch(`${apiUrl("/logs")}?${params}`);
  return parseResponse(response);
}

export async function fetchLogDetail(requestId) {
  const response = await fetch(apiUrl(`/logs/${requestId}`));
  return parseResponse(response);
}

export async function fetchStats() {
  const response = await fetch(apiUrl("/stats"));
  return parseResponse(response);
}