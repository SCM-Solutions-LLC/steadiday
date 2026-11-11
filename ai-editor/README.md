# AI Editor

Drop a talking-head recording into `raw/`, ask Claude Code to edit it, and get a captioned 9:16 reel in `done/`.

```
ai-editor/
  raw/         your recordings (gitignored)
  references/  reels whose editing you like (gitignored, except notes .md)
  done/        finished renders (gitignored)
  style.md     your taste, written down. Claude follows it on every edit.
```

Graphics are made with the Remotion project in `../promo-video` (already set up for SteadiDay fonts, colors and screenshots).

## One-time setup (Mac)

```sh
brew install ffmpeg yt-dlp
pipx install openai-whisper      # or: pip install -U openai-whisper
cd ../promo-video && npm i
```

Then open Claude Code **locally** with this repo as the folder (run it on your Mac, not a cloud session: cloud sessions are wiped).

## The 3 prompts

**Prompt 1: tools.** Run once on a new machine.

> You're my video editor. We work in `ai-editor/`: raw, references, done. Verify ffmpeg, yt-dlp, whisper and the Remotion project in `promo-video/` all work. Install anything missing.

**Prompt 2: taste.** Run whenever you find new reels you like.

> Here are reels whose editing I like: [link 1] [link 2] [link 3]. Download them into `ai-editor/references/` with yt-dlp. Study each one frame by frame and by ear: pacing, subtitles, colors, music, first 3 seconds. Take inspiration, but don't copy. Update `ai-editor/style.md` with my style.

**Prompt 3: edit.** Run for every video.

> My new recording is in `ai-editor/raw/`. Edit it using `ai-editor/style.md`. Transcribe with whisper (word timestamps), cut silences and filler, build the graphics and captions in Remotion, and export to `ai-editor/done/`.

Then give notes in plain words ("make the hook punchier", "slow the captions down") and Claude revises.

## Notes
- Shoot vertical, at eye level, in good light. Clean audio matters more than the camera.
- Raw footage and references are gitignored because this repo is public (GitHub Pages). Back them up elsewhere.
- The reference workflow also installs HyperFrames. It's skipped here because Remotion already covers the graphics.
