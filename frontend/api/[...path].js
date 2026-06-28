const API_ORIGIN =
  process.env.GUARDRAIL_API_ORIGIN || "https://guardrail-gateway-api.onrender.com";

export default async function handler(req, res) {
  const rawPath = req.query.path;
  const segments = Array.isArray(rawPath) ? rawPath : rawPath ? [rawPath] : [];
  const targetPath = segments.map((part) => String(part)).join("/");
  const targetUrl = new URL(`${API_ORIGIN}/${targetPath}`);

  for (const [key, value] of Object.entries(req.query)) {
    if (key === "path") continue;
    if (Array.isArray(value)) {
      value.forEach((entry) => targetUrl.searchParams.append(key, String(entry)));
    } else if (value != null) {
      targetUrl.searchParams.set(key, String(value));
    }
  }

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