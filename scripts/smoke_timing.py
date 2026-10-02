"""Live smoke tests against Jev + Gemini (+ optional Laya).

Run: python scripts/smoke_timing.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from app.config import get_settings
from app.db import SessionLocal, init_db
from app.services.pipeline import run_pipeline


SAMPLES = [
    {
        "name": "urgent_refund",
        "subject": "Charged twice",
        "body": "I was charged twice for order #4421. Please refund the duplicate today. Urgent.",
        "force_jev": True,
        "skip_draft": False,
    },
    {
        "name": "calm_bug",
        "subject": "Login white screen",
        "body": "Android login shows a white screen after the update. Not urgent; whenever you can.",
        "force_jev": True,
        "skip_draft": False,
    },
    {
        "name": "decision_only_jev",
        "subject": "Cancel plan",
        "body": "Please cancel my subscription at the end of this billing cycle.",
        "force_jev": True,
        "skip_draft": True,
    },
]


def main() -> int:
    settings = get_settings()
    print("=== ActGate smoke + timing ===")
    print(f"DB: {settings.database_url}")
    print(f"Jev key set: {bool(settings.typesafe_api_key)}")
    print(f"Gemini key set: {bool(settings.gemini_api_key)}")
    print(f"Laya enabled: {settings.laya_enabled}")
    print()

    init_db()
    results = []
    db = SessionLocal()
    try:
        for sample in SAMPLES:
            print(f"--- {sample['name']} ---")
            out = run_pipeline(
                db,
                subject=sample["subject"],
                body=sample["body"],
                force_jev=sample["force_jev"],
                skip_draft=sample["skip_draft"],
            )
            timing = out["timing"]
            print(f"gate={out['gate_decision']} goal={timing['goal_reached']} total_ms={timing['total_ms']}")
            for step in timing["steps"]:
                print(f"  {step['step']}: {step['duration_ms']} ms ok={step['ok']} {step.get('detail') or ''}")
            print(f"message: {out['message']}")
            if out.get("draft"):
                print(f"draft preview: {out['draft'][:160].replace(chr(10), ' ')}...")
            print()
            results.append(
                {
                    "name": sample["name"],
                    "gate": out["gate_decision"],
                    "goal_reached": timing["goal_reached"],
                    "total_ms": timing["total_ms"],
                    "steps": timing["steps"],
                    "intent": out.get("intent"),
                    "confidence": out.get("confidence"),
                }
            )
    finally:
        db.close()

    out_path = ROOT / "scripts" / "last_timing_report.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")

    # Fail if all errored
    if all(r["gate"] == "error" for r in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
