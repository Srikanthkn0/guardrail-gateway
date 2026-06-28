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
const API_KEY = import.meta.env.VITE_GATEWAY_API_KEY?.trim() || "";
const REQUEST_TIMEOUT_MS = 90_000;

export function getApiBaseUrl() {
  if (API_BASE_URL) {
    return API_BASE_URL;
  }
  if (import.meta.env.PROD && typeof window !== "undefined") {
    return window.location.origin;
  }
  return "http://localhost:8000";
}

function apiHeaders(extra = {}) {
  const headers = { ...extra };
  if (API_KEY) {
    headers["X-API-Key"] = API_KEY;
  }
  return headers;
}

async function fetchWithTimeout(url, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } catch (err) {
    if (err.name === "AbortError") {
      throw new Error("Request timed out. The gateway may be waking up - retry in a moment.");
    }
    throw err;
  } finally {
    clearTimeout(timeout);
  }
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
  const response = await fetchWithTimeout(apiUrl("/health"), {
    headers: apiHeaders(),
  });
  return parseResponse(response);
}

export async function fetchLiveness() {
  const response = await fetchWithTimeout(apiUrl("/health/live"), {
    headers: apiHeaders(),
  });
  return parseResponse(response);
}

export async function fetchMlHealth() {
  const response = await fetchWithTimeout(apiUrl("/health/ml"), {
    headers: apiHeaders(),
  });
  return parseResponse(response);
}

export async function fetchRules() {
  const response = await fetchWithTimeout(apiUrl("/rules"), {
    headers: apiHeaders(),
  });
  return parseResponse(response);
}

export async function testRules(text, outputText = "") {
  const body = { text };
  if (outputText.trim()) {
    body.output_text = outputText;
  }
  const response = await fetchWithTimeout(apiUrl("/rules/test"), {
    method: "POST",
    headers: apiHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(body),
  });
  return parseResponse(response);
}

export async function gatewayChat(prompt, provider, model) {
  const body = { prompt };
  if (provider) {
    body.provider = provider;
  }
  if (model) {
    body.model = model;
  }
  const response = await fetchWithTimeout(apiUrl("/gateway/chat"), {
    method: "POST",
    headers: apiHeaders({ "Content-Type": "application/json" }),
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
  const response = await fetchWithTimeout(`${apiUrl("/logs")}?${params}`, {
    headers: apiHeaders(),
  });
  return parseResponse(response);
}

export async function fetchLogDetail(requestId) {
  const response = await fetchWithTimeout(apiUrl(`/logs/${requestId}`), {
    headers: apiHeaders(),
  });
  return parseResponse(response);
}

export async function fetchStats() {
  const response = await fetchWithTimeout(apiUrl("/stats"), {
    headers: apiHeaders(),
  });
  return parseResponse(response);
}