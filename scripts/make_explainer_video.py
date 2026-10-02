"""
Build an understandable ActGate explainer video for LinkedIn.
Outputs:
  docs/linkedin/video/frames/*.png
  docs/linkedin/video/actgate_explainer.mp4
  docs/linkedin/video/actgate_explainer_square.mp4
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, concatenate_videoclips

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "linkedin" / "video"
FRAMES = OUT / "frames"

W, H = 1920, 1080
BG = (238, 243, 240)
INK = (15, 28, 36)
MUTED = (90, 107, 117)
ACCENT = (15, 143, 123)
ACCENT_DEEP = (10, 95, 83)
CARD = (255, 255, 255)
WARN = (184, 106, 0)
OK = (27, 127, 74)

FONT_REG = r"C:\Windows\Fonts\segoeui.ttf"
FONT_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_BOLD if bold and Path(FONT_BOLD).exists() else FONT_REG
    return ImageFont.truetype(path, size)


def new_canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), BG)
    # soft blobs
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.ellipse((-200, -300, 900, 700), fill=(200, 235, 227, 110))
    od.ellipse((1200, -100, 2100, 700), fill=(217, 228, 239, 100))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    return img, ImageDraw.Draw(img)


def wrap(draw: ImageDraw.ImageDraw, text: str, f: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        test = f"{cur} {w}".strip()
        if draw.textlength(test, font=f) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_title(draw: ImageDraw.ImageDraw, title: str, subtitle: str | None = None) -> None:
    draw.text((120, 90), "ACTGATE", font=font(36, True), fill=ACCENT_DEEP)
    draw.text((120, 160), title, font=font(72, True), fill=INK)
    if subtitle:
        y = 270
        for line in wrap(draw, subtitle, font(36), 1680):
            draw.text((120, y), line, font=font(36), fill=MUTED)
            y += 52


def card(draw: ImageDraw.ImageDraw, xyxy: tuple[int, int, int, int], radius: int = 28) -> None:
    draw.rounded_rectangle(xyxy, radius=radius, fill=CARD, outline=(15, 28, 36, 30), width=2)


def save(img: Image.Image, name: str) -> Path:
    FRAMES.mkdir(parents=True, exist_ok=True)
    path = FRAMES / name
    img.save(path, "PNG")
    return path


def slide_01_title() -> Path:
    img, d = new_canvas()
    d.text((120, 280), "ActGate", font=font(120, True), fill=INK)
    d.text((120, 440), "Decide first. Draft second.", font=font(56), fill=ACCENT_DEEP)
    for i, line in enumerate(
        [
            "Laya + Jev make typed decisions with confidence.",
            "Gemini writes a reply only after the gate opens.",
            "Your code owns risk, escalation, and timing.",
        ]
    ):
        d.text((120, 560 + i * 70), f"•  {line}", font=font(34), fill=MUTED)
    d.text((120, 920), "Product explainer  ·  60 seconds", font=font(28), fill=MUTED)
    return save(img, "01_title.png")


def slide_02_problem() -> Path:
    img, d = new_canvas()
    draw_title(d, "The usual AI mistake", "One chatbot is asked to decide AND write AND act.")
    card(d, (120, 420, 900, 860))
    d.text((160, 460), "Single LLM does everything", font=font(36, True), fill=INK)
    for i, t in enumerate(["Invented categories", "Hard to know confidence", "Risky auto-actions", "Slow + expensive"]):
        d.text((160, 540 + i * 60), f"×  {t}", font=font(32), fill=(180, 50, 40))
    card(d, (980, 420, 1800, 860))
    d.text((1020, 460), "What we want instead", font=font(36, True), fill=INK)
    for i, t in enumerate(["Typed choices only", "Calibrated confidence", "Gate before draft", "Human when unsure"]):
        d.text((1020, 540 + i * 60), f"✓  {t}", font=font(32), fill=OK)
    return save(img, "02_problem.png")


def slide_03_flow() -> Path:
    img, d = new_canvas()
    draw_title(d, "How ActGate works", "Four clear stages — easy to follow.")
    boxes = [
        (120, "1. Message", "Customer email\nor ticket arrives"),
        (560, "2. Decide", "Laya (local)\nand/or Jev"),
        (1000, "3. Gate", "Code checks\nconfidence + risk"),
        (1440, "4. Draft", "Gemini writes\nonly if allowed"),
    ]
    for x, title, body in boxes:
        card(d, (x, 420, x + 360, 820))
        d.rounded_rectangle((x + 24, 460, x + 120, 520), radius=16, fill=ACCENT)
        d.text((x + 48, 468), title.split(".")[0] + ".", font=font(28, True), fill=CARD)
        d.text((x + 24, 560), title, font=font(34, True), fill=INK)
        by = 630
        for line in body.split("\n"):
            d.text((x + 24, by), line, font=font(28), fill=MUTED)
            by += 42
    # arrows
    for x in (480, 920, 1360):
        d.polygon([(x, 600), (x + 40, 620), (x, 640)], fill=ACCENT)
    return save(img, "03_flow.png")


def slide_04_decide() -> Path:
    img, d = new_canvas()
    draw_title(
        d,
        "Step 2 — Decide (not write)",
        "System One models answer multiple-choice questions with probabilities.",
    )
    card(d, (120, 400, 1800, 900))
    rows = [
        ("Intent", "refund / shipping / bug / cancel / other"),
        ("Urgency", "yes/no probability (noul)"),
        ("Risk", "low / medium / high"),
        ("Next step", "draft_reply / ask_human / block"),
    ]
    d.text((160, 440), "Laya (your PC)  →  fast & private", font=font(34, True), fill=ACCENT_DEEP)
    d.text((980, 440), "Jev (cloud)  →  second opinion", font=font(34, True), fill=ACCENT_DEEP)
    y = 520
    for k, v in rows:
        d.text((160, y), k, font=font(32, True), fill=INK)
        d.text((480, y), v, font=font(32), fill=MUTED)
        y += 70
    d.text((160, 820), "They never write the customer email. They only judge.", font=font(30), fill=MUTED)
    return save(img, "04_decide.png")


def slide_05_gate() -> Path:
    img, d = new_canvas()
    draw_title(d, "Step 3 — The Gate (your rules)", "Confidence and risk decide what happens next.")
    outcomes = [
        (120, ACCENT, "auto_draft", "High confidence\n+ safe risk\n→ call Gemini"),
        (580, WARN, "jev_second_opinion", "Borderline\n→ ask Jev again"),
        (1040, (70, 110, 150), "ask_human", "Unsure / urgent\n→ human review"),
        (1500, (180, 50, 40), "blocked", "High risk\n→ stop pipeline"),
    ]
    for x, color, title, body in outcomes:
        card(d, (x, 420, x + 400, 860))
        d.rounded_rectangle((x + 24, 460, x + 376, 520), radius=14, fill=color)
        d.text((x + 40, 472), title, font=font(26, True), fill=CARD)
        by = 560
        for line in body.split("\n"):
            d.text((x + 36, by), line, font=font(28), fill=INK)
            by += 44
    return save(img, "05_gate.png")


def slide_06_gemini() -> Path:
    img, d = new_canvas()
    draw_title(
        d,
        "Step 4 — Gemini drafts",
        "Only after the gate says auto_draft. Categories are already locked.",
    )
    card(d, (120, 420, 900, 880))
    d.text((160, 470), "Locked decisions", font=font(36, True), fill=INK)
    for i, t in enumerate(["intent = bug", "urgency = low", "risk = low", "next = draft_reply"]):
        d.text((160, 560 + i * 55), f"•  {t}", font=font(32), fill=MUTED)
    card(d, (980, 420, 1800, 880))
    d.text((1020, 470), "Gemini output", font=font(36, True), fill=INK)
    draft = (
        "Hi — sorry about the Android white screen. "
        "We'll investigate the login issue from the latest update and follow up."
    )
    y = 560
    for line in wrap(d, draft, font(30), 740):
        d.text((1020, y), line, font=font(30), fill=INK)
        y += 48
    d.text((1020, 780), "Human can still review before send.", font=font(28), fill=OK)
    return save(img, "06_gemini.png")


def slide_07_timing() -> Path:
    img, d = new_canvas()
    draw_title(d, "Timed to a clear goal", "Goal name: decide_and_draft — every step shows milliseconds.")
    rows = [
        ("Laya decide (CPU)", "~6 s", 0.35),
        ("Jev decide", "~0.6–2 s", 0.18),
        ("Gate logic", "~0.1 ms", 0.05),
        ("Gemini draft", "~11–13 s", 0.72),
        ("Full path (Jev+Gemini)", "~12–15 s", 0.9),
    ]
    y = 420
    for label, val, frac in rows:
        d.text((140, y), label, font=font(32), fill=INK)
        d.rounded_rectangle((700, y + 8, 700 + int(900 * frac), y + 48), radius=12, fill=ACCENT)
        d.text((1620, y), val, font=font(32, True), fill=ACCENT_DEEP)
        y += 90
    return save(img, "07_timing.png")


def slide_08_example() -> Path:
    img, d = new_canvas()
    draw_title(d, "Real run example", "Live UI: Laya judged a bug ticket in ~6.1 seconds.")
    card(d, (120, 400, 900, 880))
    d.text((160, 450), "Input", font=font(34, True), fill=MUTED)
    d.text((160, 520), "Subject: App crashes on login", font=font(30), fill=INK)
    body = "Android white screen after update. Not urgent."
    y = 590
    for line in wrap(d, body, font(30), 680):
        d.text((160, y), line, font=font(30), fill=INK)
        y += 46
    card(d, (980, 400, 1800, 880))
    d.text((1020, 450), "Result", font=font(34, True), fill=MUTED)
    for i, (k, v) in enumerate(
        [
            ("Gate", "ask_human"),
            ("Intent", "bug"),
            ("Confidence", "0.42"),
            ("Laya time", "6108 ms"),
            ("Why", "Low confidence → escalate"),
        ]
    ):
        d.text((1020, 520 + i * 55), f"{k}:", font=font(28, True), fill=MUTED)
        d.text((1280, 520 + i * 55), v, font=font(28), fill=INK)
    return save(img, "08_example.png")


def slide_09_stack() -> Path:
    img, d = new_canvas()
    draw_title(d, "Stack", "Product-ready local + cloud hybrid.")
    items = [
        ("Laya", "Local System One"),
        ("Jev", "TypeSafe cloud"),
        ("Gemini", "Draft writer"),
        ("FastAPI", "API + UI"),
        ("Postgres", "Cases + timings"),
        ("Gate code", "Policy engine"),
    ]
    for i, (a, b) in enumerate(items):
        col = i % 3
        row = i // 3
        x = 120 + col * 560
        y = 420 + row * 240
        card(d, (x, y, x + 500, y + 200))
        d.text((x + 40, y + 50), a, font=font(40, True), fill=ACCENT_DEEP)
        d.text((x + 40, y + 120), b, font=font(30), fill=MUTED)
    return save(img, "09_stack.png")


def slide_10_cta() -> Path:
    img, d = new_canvas()
    d.text((120, 300), "ActGate", font=font(100, True), fill=INK)
    d.text((120, 440), "Confidence-gated AI for support workflows.", font=font(44), fill=MUTED)
    for i, t in enumerate(
        [
            "Decide with Laya / Jev",
            "Gate with your rules",
            "Draft with Gemini only when safe",
            "Measure every millisecond to the goal",
        ]
    ):
        d.text((120, 560 + i * 60), f"{i + 1}.  {t}", font=font(34), fill=INK)
    d.text((120, 880), "Build in public  ·  System One + System Two", font=font(30), fill=ACCENT_DEEP)
    return save(img, "10_cta.png")


def build_video(paths: list[Path], out_path: Path, durations: list[float], size: tuple[int, int] | None = None) -> None:
    clips = []
    for p, dur in zip(paths, durations):
        clip = ImageClip(str(p), duration=dur)
        if size:
            clip = clip.resized(new_size=size)
        clips.append(clip)
    final = concatenate_videoclips(clips, method="compose")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    final.write_videofile(
        str(out_path),
        fps=30,
        codec="libx264",
        audio=False,
        preset="medium",
        ffmpeg_params=["-pix_fmt", "yuv420p"],
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    slides = [
        (slide_01_title(), 5.0),
        (slide_02_problem(), 6.0),
        (slide_03_flow(), 7.0),
        (slide_04_decide(), 7.0),
        (slide_05_gate(), 7.0),
        (slide_06_gemini(), 6.5),
        (slide_07_timing(), 6.5),
        (slide_08_example(), 6.5),
        (slide_09_stack(), 5.5),
        (slide_10_cta(), 5.0),
    ]
    paths = [p for p, _ in slides]
    durs = [d for _, d in slides]

    landscape = OUT / "actgate_explainer.mp4"
    square = OUT / "actgate_explainer_square.mp4"
    print("Rendering landscape 16:9…")
    build_video(paths, landscape, durs)
    print("Rendering square 1:1 for LinkedIn feed…")
    build_video(paths, square, durs, size=(1080, 1080))

    # also copy a short README
    (OUT / "README.md").write_text(
        """# ActGate explainer video

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
""",
        encoding="utf-8",
    )
    print(f"Done: {landscape}")
    print(f"Done: {square}")


if __name__ == "__main__":
    main()
