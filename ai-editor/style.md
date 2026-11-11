# SteadiDay reel style

Claude reads this before every edit. Edit it freely: it is your taste, written down.

Seeded from one reference (a 9:16 "1-minute setup" explainer reel, 88s). One
reference is a thin sample. Add 2–4 reels you like to `references/` and run
Prompt 2 again to refine this file.

## Format
- 1080x1920 (9:16), 30 fps, H.264 + AAC, -14 LUFS loudness.
- Length 45–90s. One idea per video.

## Structure
1. **Hook (0–3s):** a bold promise on screen in the first frame ("1:00 — the whole setup"). No intro, no logo.
2. **Numbered steps:** each beat gets a pill tag top-left, e.g. `01 · App`, `02 · Folder`. Steps are short, under 8s each.
3. **Payoff:** a recap card listing every step as a checklist.
4. **CTA:** one line ("Follow — next up: …"), then end. No long outro.

## Layout (top to bottom)
- **Top 55%:** a graphic panel (dark UI card, app screenshot, list, folder diagram) illustrating what's being said *right now*.
- **Middle:** captions.
- **Bottom 30%:** the speaker in a rounded-corner card (radius ~24px, subtle shadow), centred, about 45% of the frame width. Never full-screen except the first 1–2s.

## Captions
- Serif display face, large (~64px at 1080w), one short phrase at a time (2–5 words).
- Karaoke style: spoken words white, **the current word in brand green and italic**, upcoming words dim gray.
- Captions come from Whisper word timestamps and must match the speech exactly. Fix misheard brand words: "SteadiDay" (not "Steady Day").

## Graphics
- Background: near-black `#111111` with a soft radial vignette.
- Cards: `#1C1C1C`, 1px `#2A2A2A` border, 16px radius, macOS-style window dots when showing an app.
- Accent: SteadiDay green `#4A9D7E` (replaces the reference's yellow) for pills, highlights, selected rows, check marks.
- Fonts: Poppins SemiBold/Bold for UI/labels, Source Sans 3 for body (both in `promo-video/public/fonts`).
- Motion: elements ease and slide in 6–10 frames; list items highlight one by one as they're mentioned. No spins, no bounces, no stock transitions.

## Pacing and cuts
- Remove every silence over 0.3s, plus filler words ("um", "uh", "so yeah") and restarts.
- Keep the speaker's energy: never cut mid-word; leave 2–3 frames of breathing room.
- The graphic changes on every new idea, roughly every 2–4s.

## Audience fit (SteadiDay specific)
- Viewers are often 60+ or adult children of aging parents: keep captions large and high-contrast, and hold each caption at least 0.8s.
- Use plain words, no jargon. Show the real app UI (screenshots in `promo-video/public/`) instead of mock UI where possible.
- No medical claims beyond what the app does.

## Don'ts
- Don't copy a reference's exact words, layout, or handle. Take the structure, not the content.
- No music louder than -20 dB under speech. No watermarks.
