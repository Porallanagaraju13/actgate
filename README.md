# ActGate

Product-ready **confidence gate**: local **Laya** and cloud **Jev** decide; **Gemini** drafts only when the gate opens. Every step is timed until the goal (`decide_and_draft`) is reached or blocked.

## Quick start

```powershell
cd C:\Users\Nagaraju Poralla\actgate
pip install -r requirements.txt
# edit .env (Postgres + API keys)
run.bat
```

Open http://127.0.0.1:8787

## Sample data testing

```powershell
python scripts/run_sample_data.py --skip-draft
python scripts/run_sample_data.py --ids refund_calm,bug_android
```

Samples live in `data/sample_tickets.json`.

## Docs

| Doc | What |
|-----|------|
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | **Execute + deploy** (local, VPS, Docker) |
| [docs/HOW_IT_WORKS.md](docs/HOW_IT_WORKS.md) | Architecture |
| [docs/LINKEDIN_POST.md](docs/LINKEDIN_POST.md) | Post + visuals |

## Stack

| Layer | Job |
|-------|-----|
| Laya (local) | System One judgments |
| Jev (TypeSafe) | Second opinion / cloud decide |
| Gate (code) | Confidence + risk policy |
| Gemini | Draft after gate opens |
| Postgres (`act`) | Case history + timings |

## Security

Never commit `.env`. Rotate keys if they were shared in chat.
