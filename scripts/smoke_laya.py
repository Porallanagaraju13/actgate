"""Time Laya local decide (downloads/loads model on first run)."""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from app.clients import laya_client
from app.gate import DECISION_QUESTIONS


def main() -> int:
    state = {
        "subject": "Charged twice",
        "body": "I was charged twice for order #4421. Please refund today.",
        "document": "Subject: Charged twice\n\nI was charged twice for order #4421. Please refund today.",
    }
    print("Loading Laya (first run may download weights)...")
    t0 = time.perf_counter()
    try:
        laya_client.get_laya_agent()
    except Exception as exc:  # noqa: BLE001
        print(f"LOAD FAILED: {exc}")
        return 1
    load_ms = (time.perf_counter() - t0) * 1000
    print(f"laya_load: {load_ms:.2f} ms")

    t1 = time.perf_counter()
    answers = laya_client.decide_with_laya(state, DECISION_QUESTIONS)
    decide_ms = (time.perf_counter() - t1) * 1000
    print(f"laya_decide: {decide_ms:.2f} ms")
    print(json.dumps(answers, indent=2, default=str)[:2000])

    Path(ROOT / "scripts" / "last_laya_timing.json").write_text(
        json.dumps({"load_ms": round(load_ms, 2), "decide_ms": round(decide_ms, 2), "answers": answers}, indent=2, default=str),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
