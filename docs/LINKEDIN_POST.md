# LinkedIn post — ActGate

## Try it

Public demo:

https://actgate.onrender.com

Visitors pick a sample ticket and run it. Custom messages are blocked. Eight runs per person per hour.

## Caption (copy-paste)

Built a small product I’m calling **ActGate**.

Most “AI support” demos dump everything into one LLM and hope for the best.  
I split the job:

🧠 **Laya** (local) + **Jev** (TypeSafe) → typed decisions with confidence  
✍️ **Gemini** → writes the reply **only if** the gate opens  
🛡️ Plain code → risk thresholds, escalate-to-human, never freestyle actions  
⏱️ Every step timed until the goal `decide_and_draft` is reached  
🗄️ Cases + timings land in **Postgres**

Flow: message → decide → gate → draft (or ask a human).

Stack: Python FastAPI · Laya · TypeSafe Jev · Gemini · PostgreSQL

Happy to share the architecture if you’re exploring System One / System Two patterns for production agents.

#AI #BuildInPublic #FastAPI #Gemini #PostgreSQL #LLMOps #SystemOne

---

## Video (recommended for LinkedIn)

Folder: `docs/linkedin/video/`

| File | Format | Use |
|------|--------|-----|
| `actgate_explainer.mp4` | 16:9 ~62s | LinkedIn / YouTube main video |
| `actgate_explainer_square.mp4` | 1:1 ~62s | LinkedIn feed square |
| `VOICEOVER.md` | script | Speak over the silent video |
| `frames/` | PNG slides | Reuse in carousels |

Story order (easy to follow): Problem → 4-step flow → Decide → Gate → Gemini → Timing → Real example → Stack → Close.

Post tip: upload the **square** video + attach still images 01–03; paste caption from above; put the voice-over in a comment if you record audio later.
