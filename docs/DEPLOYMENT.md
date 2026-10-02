# ActGate — Execution & Deployment

Project: `C:\Users\Nagaraju Poralla\actgate`

---

## Public try-it demo (LinkedIn)

Visitors cannot open `localhost`. They need a public URL.

The app now has sample-ticket buttons (`GET /api/samples`). Set `DEMO_MODE=true` on the public server so people can only run those tickets (8 runs per person per hour). Leave Laya off in the cloud (`LAYA_ENABLED=false`); Jev decides and Gemini drafts.

`render.yaml` is ready for a free Render web service. Render CLI on this PC is not logged in yet:

```powershell
render login
```

Then create the service from the repo and set `TYPESAFE_API_KEY` and `GEMINI_API_KEY` in the Render dashboard (do not commit them).

Until that login exists, a temporary tunnel (ngrok) can publish the local demo while this PC stays on.

## 1) Prerequisites

- Python 3.11+ (tested on 3.14)
- PostgreSQL (local database name **`act`**, user **`postgres`**, port **`5433`**)
- API keys in `.env`:
  - `TYPESAFE_API_KEY` (Jev)
  - `GEMINI_API_KEY`
- Optional: Laya local model (`LAYA_ENABLED=true`)

Install deps once:

```powershell
cd C:\Users\Nagaraju Poralla\actgate
pip install -r requirements.txt
```

---

## 2) Configure `.env`

Current Postgres URL shape:

```env
DATABASE_URL=postgresql+psycopg://postgres:PASSWORD@127.0.0.1:5433/act
TYPESAFE_API_KEY=...
GEMINI_API_KEY=...
LAYA_ENABLED=true
LAYA_PRELOAD=true
LAYA_DEVICE=cpu
APP_HOST=127.0.0.1
APP_PORT=8787
```

Never commit `.env`.

---

## 3) Execute locally (dev)

### Start the app

```powershell
cd C:\Users\Nagaraju Poralla\actgate
run.bat
```

Or:

```powershell
$env:PYTHONPATH = "C:\Users\Nagaraju Poralla\actgate"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8787
```

Open: http://127.0.0.1:8787

### Health check

```powershell
Invoke-RestMethod http://127.0.0.1:8787/api/health
```

Expect: `database: ok`, `laya: ready` (after preload), `jev/gemini: configured`.

### Manual UI test

1. Paste a sample subject/body from `data/sample_tickets.json`
2. Leave **Force Jev** unchecked to use Laya first
3. Click **Run pipeline**
4. Check Gate / Goal / Total ms / Draft / Recent cases

---

## 4) Sample data testing

Sample file: `data/sample_tickets.json` (8 tickets covering refund, bug, shipping, cancel, legal/high-risk, decision-only).

### Run all samples against the live server

```powershell
cd C:\Users\Nagaraju Poralla\actgate
$env:PYTHONPATH = "$pwd"
python scripts/run_sample_data.py
```

### Faster (skip Gemini drafts)

```powershell
python scripts/run_sample_data.py --skip-draft
```

### Only some IDs

```powershell
python scripts/run_sample_data.py --ids refund_calm,bug_android,cancel_plan
```

### In-process (no HTTP; uses `.env` + DB directly)

```powershell
python scripts/run_sample_data.py --local --skip-draft
```

Results are written to: `data/last_sample_run.json`

### One-off API call (PowerShell)

```powershell
$body = @{
  subject = "Cancel subscription"
  body = "Please cancel my plan at period end."
  force_jev = $false
  skip_draft = $false
} | ConvertTo-Json

Invoke-RestMethod -Uri http://127.0.0.1:8787/api/pipeline `
  -Method POST -ContentType "application/json" -Body $body
```

### Unit tests (no paid APIs)

```powershell
python -m pytest tests/test_gate.py -q
```

---

## 5) What “good” looks like

| Sample type | Typical gate | Goal |
|-------------|--------------|------|
| Clear low-risk bug/cancel | `auto_draft` | reached (if draft enabled) |
| Borderline | may call Jev then decide | depends |
| Low confidence | `ask_human` | not reached (by design) |
| Legal / high risk | `ask_human` or `blocked` | not reached (by design) |

Escalation is success when risk/confidence says so — not a failure.

---

## 6) Deployment process

### A. Local production-style (same machine)

1. Create Postgres DB `act` (done).
2. Put secrets only in `.env` or OS env vars.
3. Install deps: `pip install -r requirements.txt`
4. Start with a process manager (example Windows Task Scheduler / NSSM / `Start-Process`):

```powershell
cd C:\Users\Nagaraju Poralla\actgate
$env:PYTHONPATH = "$pwd"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8787 --workers 1
```

Notes:
- Use **`--workers 1`** while Laya is in-process (model is heavy / not multi-process friendly).
- First Laya load can take minutes; keep `LAYA_PRELOAD=true`.
- Open firewall for port `8787` only if you need LAN access.

### B. Deploy on a Linux VM / VPS

1. Install Python 3.11+, Postgres, git.
2. Clone/copy the project to e.g. `/opt/actgate`.
3. Create venv and install:

```bash
cd /opt/actgate
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

4. Create `/opt/actgate/.env` (same keys; point `DATABASE_URL` at Postgres).
5. Create systemd unit `/etc/systemd/system/actgate.service`:

```ini
[Unit]
Description=ActGate API
After=network.target postgresql.service

[Service]
WorkingDirectory=/opt/actgate
Environment=PYTHONPATH=/opt/actgate
EnvironmentFile=/opt/actgate/.env
ExecStart=/opt/actgate/.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8787 --workers 1
Restart=always
User=www-data

[Install]
WantedBy=multi-user.target
```

6. Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now actgate
sudo systemctl status actgate
```

7. Put Nginx in front (TLS):

```nginx
server {
  listen 443 ssl;
  server_name actgate.example.com;
  # ssl_certificate ...;
  location / {
    proxy_pass http://127.0.0.1:8787;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_read_timeout 180s;
  }
}
```

8. Smoke test:

```bash
curl https://actgate.example.com/api/health
python scripts/run_sample_data.py --base-url https://actgate.example.com --skip-draft
```

### C. Docker (API without baking Laya weights — optional)

If you containerize, prefer **Jev + Gemini** in the container and run Laya on a GPU host, or mount the Hugging Face cache.

Example `Dockerfile` pattern:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONPATH=/app
EXPOSE 8787
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8787", "--workers", "1"]
```

```bash
docker build -t actgate .
docker run --env-file .env -p 8787:8787 actgate
```

For Postgres, use docker-compose with a `db` service and set `DATABASE_URL` to that host.

---

## 7) Post-deploy checklist

- [ ] `GET /api/health` → database ok
- [ ] Jev key works (`force_jev=true` sample)
- [ ] Gemini draft works (one `skip_draft=false` sample)
- [ ] Laya ready (if enabled)
- [ ] `case_runs` rows appear in Postgres `act`
- [ ] `python scripts/run_sample_data.py --skip-draft` completes

---

## 8) Useful paths

| Item | Path |
|------|------|
| App | `app/main.py` |
| Samples | `data/sample_tickets.json` |
| Sample runner | `scripts/run_sample_data.py` |
| How it works | `docs/HOW_IT_WORKS.md` |
| LinkedIn pack | `docs/linkedin/` |

---

## 9) Stop / restart (Windows)

```powershell
# find and stop port 8787
Get-NetTCPConnection -LocalPort 8787 -ErrorAction SilentlyContinue |
  ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }

# start again
cd C:\Users\Nagaraju Poralla\actgate
run.bat
```
