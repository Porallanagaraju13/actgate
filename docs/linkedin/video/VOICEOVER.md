# ActGate — voice-over script (~62 seconds)

Use with `actgate_explainer.mp4` (mute the video or speak over slides).

---

**[0–5s · Title]**  
Hi — I built ActGate. The idea is simple: decide first, draft second.

**[5–11s · Problem]**  
Most AI support demos ask one LLM to classify, decide, and write. That invents actions and hides uncertainty.

**[11–18s · Flow]**  
ActGate uses four stages: message in, decide, gate, then draft.

**[18–25s · Decide]**  
Laya runs locally and Jev in the cloud. They answer typed questions — intent, urgency, risk, next step — with confidence scores. They don’t write the email.

**[25–32s · Gate]**  
Your code is the gate. High confidence and low risk becomes auto-draft. Borderline calls Jev. Unsure escalates to a human. High risk blocks.

**[32–38s · Gemini]**  
Only after the gate opens does Gemini write a short reply — categories already locked.

**[38–45s · Timing]**  
Every step is timed to one goal: decide_and_draft. On my machine, decide is about one to six seconds; drafting is about twelve.

**[45–52s · Example]**  
In a real run, Laya labeled a login bug in about six seconds. Confidence was low, so ActGate asked a human instead of drafting — that’s the product working.

**[52–57s · Stack]**  
Stack: Laya, TypeSafe Jev, Gemini, FastAPI, Postgres.

**[57–62s · Close]**  
System One for judgment. System Two for writing. Code for safety. That’s ActGate.
