# ActGate explainer video

## Files
- `actgate_explainer.mp4` — 16:9 (~62s) for LinkedIn / YouTube
- `actgate_explainer_square.mp4` — 1:1 for LinkedIn feed
- `frames/` — individual slides (PNG)

## Story (understandable order)
1. Title — Decide first, draft second
2. Problem — one LLM does everything
3. Flow — Message → Decide → Gate → Draft
4. Decide — Laya/Jev typed judgments
5. Gate — auto_draft / Jev / human / block
6. Gemini — writes only after gate opens
7. Timing — ms to goal `decide_and_draft`
8. Real example — live run numbers
9. Stack
10. Close

## Rebuild
```bash
python scripts/make_explainer_video.py
```
