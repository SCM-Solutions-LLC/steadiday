# SteadiDay reel style

Claude reads this before every edit. Edit it freely: it is your taste, written down.

Originally seeded from one reference (a 9:16 "1-minute setup" explainer reel, 88s). One
reference is a thin sample. Add 2–4 reels you like to `references/` and run
Prompt 2 again to refine this file.

## Format
- 1080x1920 (9:16), 30 fps, H.264 + AAC, -14 LUFS loudness.
- Length 45–90s. One idea per video.

## Structure
No talking head. Videos are stock footage + AI voiceover (ElevenLabs) + music, built in `promo-video/` (composition `StockPromo`).
1. **Hook (0–5s):** an emotional line over a confident, positive senior shot. No intro, no logo.
2. **Feature beats (5–8s each):** stock footage that matches the line, with the real app screenshot sliding in on top.
3. **End card (~7s):** brand green, app icon, "SteadiDay. Peace of mind, every day.", App Store badge. No long outro.

## Layout (9:16)
- **Full bleed:** Pexels stock clip (`promo-video/public/stock/`), muted, cover-fit.
- **Upper 60%:** app screenshot card (white border, 48px radius, soft shadow), slow 4% push-in.
- **Bottom:** caption over a dark gradient scrim.

## Captions
- Poppins Bold ~68px at 1080w, white with a soft shadow, max two short lines, centred.
- Words match the voiceover script exactly. Brand word is always "SteadiDay" (not "Steady Day").

## Stock footage (Pexels)
- Positive framing only: active, confident seniors and connected families. **Never show a fall, injury or distress**: Pexels' license forbids showing identifiable people in a bad light, and it's off-brand.
- Prefer portrait clips, 1080p+, natural light, real homes. No obvious stock clichés (thumbs up to camera).

## Graphics
- Background: near-black `#111111` with a soft radial vignette.
- Cards: `#1C1C1C`, 1px `#2A2A2A` border, 16px radius, macOS-style window dots when showing an app.
- Accent: SteadiDay green `#4A9D7E` (replaces the reference's yellow) for pills, highlights, selected rows, check marks.
- Fonts: Poppins SemiBold/Bold for UI/labels, Source Sans 3 for body (both in `promo-video/public/fonts`).
- Motion: elements ease and slide in 6–10 frames; list items highlight one by one as they're mentioned. No spins, no bounces, no stock transitions.

## Pacing and cuts
- Time every beat to the voiceover line; cut on the pause between lines, never mid-word.
- Change the shot on every new idea, roughly every 3–5s (split long beats into two clips).

## Audience fit (SteadiDay specific)
- Viewers are often 60+ or adult children of aging parents: keep captions large and high-contrast, and hold each caption at least 0.8s.
- Use plain words, no jargon. Show the real app UI (screenshots in `promo-video/public/`) instead of mock UI where possible.
- No medical claims beyond what the app does.

## Don'ts
- Don't copy a reference's exact words, layout, or handle. Take the structure, not the content.
- Music sits at least 20 dB under the voiceover. No watermarks.
