const API_ORIGIN =
  process.env.GUARDRAIL_API_ORIGIN || "https://guardrail-gateway-api.onrender.com";

function resolveTargetPath(req) {
  const rawPath = req.query.path;
  if (rawPath) {
    const segments = Array.isArray(rawPath) ? rawPath : [rawPath];
    const joined = segments.map((part) => String(part)).join("/");
    if (joined) return joined;
  }

  const host = req.headers.host || "localhost";
  const url = new URL(req.url || "/", `https://${host}`);
  const prefix = "/api/";
  if (url.pathname.startsWith(prefix)) {
    return url.pathname.slice(prefix.length);
  }
  return "";
}

export default async function handler(req, res) {
  const targetPath = resolveTargetPath(req);
  const targetUrl = new URL(
    targetPath ? `${API_ORIGIN}/${targetPath}` : `${API_ORIGIN}/`,
  );

  const host = req.headers.host || "localhost";
  const requestUrl = new URL(req.url || "/", `https://${host}`);
  requestUrl.searchParams.forEach((value, key) => {
    if (key !== "path") {
      targetUrl.searchParams.append(key, value);
    }
  });

  const headers = {
    Accept: "application/json",
  };
  if (req.headers["content-type"]) {
    headers["Content-Type"] = req.headers["content-type"];
  }
  if (req.headers["x-api-key"]) {
    headers["X-API-Key"] = req.headers["x-api-key"];
  }

  let body;
  if (req.method !== "GET" && req.method !== "HEAD" && req.body != null) {
    body = typeof req.body === "string" ? req.body : JSON.stringify(req.body);
  }

  try {
    const upstream = await fetch(targetUrl.toString(), {
      method: req.method,
      headers,
      body,
    });
    const text = await upstream.text();
    res.status(upstream.status);
    const contentType = upstream.headers.get("content-type");
    if (contentType) {
      res.setHeader("Content-Type", contentType);
    }
    res.send(text);
  } catch (err) {
    res.status(502).json({
      detail:
        "Proxy could not reach the Render API. The service may be waking up - retry shortly.",
    });
  }
}