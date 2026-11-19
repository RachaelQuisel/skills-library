---
name: "training-video"
description: "Make a narrated how-to video of a web app from real screenshots: plain-language script, red highlights, captions, ElevenLabs voice synced to each slide. Use when Rachael types /training-video or asks for a training or walkthrough video."
---

# Training video

Build a how-to video of a web app for non-technical staff. Real screens, one idea per slide, a red box around the button being described, a caption bar, and a calm narrator. Output: an MP4 at 1280x720, 25 frames per second, usually 4 to 8 minutes.

## Before building, ask once (one AskUserQuestion call), then show the plan

1. Audience, and what they must be able to do after watching.
2. Narration: an ElevenLabs voice (uses her credits, about 4,600 credits for a 6-minute script), captions only, or her own voice recorded later.
3. Privacy: real names, phone numbers, and emails show in screenshots. Blur them, skip screens with data, or keep as is.
4. Brand: logo, colors, and a brand guide if one exists (hex codes, logo rules, colors to avoid).
5. Length target.

Show the script outline and the list of screens. Wait for a yes before building.

## Step 1: Pull facts from live sources

- Read the live app in a headless browser. Do not rely on memory or old screenshots. Apps change daily; capture the same day you deliver and say when you captured.
- If the app sits on an Airtable base, pull field options, statuses, and definitions from the live base with the Airtable connector for every fact the script states.
- If a how-to guide already exists, use it as the script source, but recheck each claim against the app.

## Step 2: Write the script as segments

Each segment is a tuple: (spoken text, caption or None, screen key, [highlight keys]). 8 to 25 words per segment. One segment maps to one screen state.

Rules:

- Plain words. One idea per sentence. Short sentences. Apply the voice-align skill if it is available.
- Speak to staff as capable coworkers. Do not use "master," "listen up," "listen closely," "pro tip," "golden rule," "boom," "I cannot stress this enough," or "you guessed it." No hype words.
- Say the one rule that matters most twice: once near the start, once where it applies.
- Do not add rules the app or the guide does not have.
- First step is "open the page," not "log in," when no password is needed.
- Pronunciation for the narrator (spoken text only; captions keep normal spelling):
  - Acronyms as letters with periods: G.O.L., D.I.U.P., S.P.A. 6
  - Web addresses letter by letter with commas: "t, 9, a, a, s, s, 6, n, 8, p, dot zite dot so"
  - Phone numbers as digit groups: "3 2 3, 5 2 4, 9 8 8 9"
  - "N slash A" for N/A
- Cards: a title card, a rule card for the key rule, an end card. Keep cards on brand: logo, brand colors, brand stripe. If blue is not in the palette, no blue anywhere.

## Step 3: Capture screens with Playwright, read-only

- Headless Chromium in the sandbox, viewport 1280x720. `require('playwright')` works as is; do not run playwright install.
- Navigate like a user: click tabs, open a module, open a record. Open dropdowns and menus to screenshot them, then press Escape.
- Change no data. If a check would save a record (for example picking a status), skip it and say so in the report.
- For every highlight target, record `boundingBox()` into boxes.json. Scroll first so the target is in view, then measure. Measure again after any scroll.
- Save frames/<key>.png and boxes.json. If a PDF export is part of the flow, download it with acceptDownloads and render page 1 with `pdftoppm -png -r 110`.

Template (cap.js):

```js
const { chromium } = require('playwright'); const fs = require('fs'); const boxes = {};
async function box(p, key, loc) { try { const b = await loc.first().boundingBox(); if (b) boxes[key] = b; } catch (e) {} }
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1280, height: 720 }, acceptDownloads: true });
  const p = await ctx.newPage();
  await p.goto(URL, { waitUntil: 'networkidle', timeout: 45000 }); await p.waitForTimeout(2500);
  await p.screenshot({ path: 'frames/home.png' });
  await box(p, 'tab_modules', p.getByRole('button', { name: 'Training Modules', exact: true }));
  // click through each screen; screenshot; box() each target
  await p.locator('[role=combobox]').first().click(); await p.waitForTimeout(900);
  await p.screenshot({ path: 'frames/statusmenu.png' }); await p.keyboard.press('Escape');
  fs.writeFileSync('boxes.json', JSON.stringify(boxes, null, 1)); await b.close();
})();
```

## Step 4: Narration

ElevenLabs (preferred):

1. `creative_list_voices` with use_cases informative_educational. Pick a calm training voice. Claire ("E-Learning & Corporate Training", voice id umwdC76NumBsGtudno3p) worked well.
2. Run a one-sentence test first with generations_count 1. If the account is blocked ("Free Tier access has been disabled"), stop and tell her. She may need to sign in to ElevenLabs or upgrade. Do not retry the same call; each call charges.
3. Join all spoken segments into one prompt. Call `creative_generate_speech` with model eleven_multilingual_v2 and generations_count 1. Poll `creative_get_flow_run_status` every 45 to 60 seconds until completed. Download content_url with curl to eleven.mp3. Record credits used.

Fallback, free and local, when ElevenLabs is blocked and she agrees:

- `pip install --break-system-packages piper-tts`. Download en_US-lessac-high.onnx and .onnx.json from huggingface.co/rhasspy/piper-voices (en/en_US/lessac/high).
- One WAV per segment: `python3 -m piper -m voice.onnx -f seg/NN.wav --length-scale 1.05 --sentence-silence 0.3` with the text on stdin. Spell "Airtable" as "Air table" for piper.

## Step 5: Build slides with PIL

- 1280x720 white canvas. Screenshot scaled to 87.5% and centered at the top. Red (#CC2222 or brand red) rounded rectangle, 4px line, 6px padding, around each highlight box from boxes.json, scaled the same way.
- Caption bar: brand near-black (#1a1a1a), full width, the bottom 90px. Caption text or the spoken text, DejaVu Sans 24px white, centered, at most 2 lines of 78 characters. Replace spelled-out forms in captions (S.P.A. 6 becomes SPA 6).
- Cards: white, 5px brand stripe at the top, logo cropped from a screenshot, red category label, bold 46px title, gray subtitle.
- Save seg/NN.png for each segment.

## Step 6: Assemble

Per-segment audio (piper): loop each PNG for its WAV length plus 0.5 seconds with ffmpeg (libx264, tune stillimage, yuv420p, 25 fps, aac mono), then concat.

One narration file (ElevenLabs): align with word timestamps.

- `pip install --break-system-packages faster-whisper`. Convert the MP3 to 16 kHz mono WAV with ffmpeg. Load it with wave and numpy and pass the array to transcribe, not the file path (the installed av version breaks decode_audio).
- Transcribe with model base.en, compute_type int8, word_timestamps True.
- Normalize words (lowercase, letters and digits only). Run difflib.SequenceMatcher between the script words and the transcript words with autojunk False. Map each segment's first word to its timestamp. Interpolate boundaries that fall in unmatched stretches. Subtract 0.15 seconds so the slide changes just before the first word.
- Write a concat list with `file` and `duration` lines (repeat the last file once at the end), then:

```
ffmpeg -f concat -safe 0 -i list.txt -i eleven.mp3 -af apad=pad_dur=0.8 -c:v libx264 -tune stillimage -pix_fmt yuv420p -r 25 -c:a aac -ar 44100 -ac 1 -t <audio seconds + 0.8> out.mp4
```

## Step 7: Verify before sending

- Transcribe the final audio and read it for mispronounced names (Airtable heard as "irritable," GOL heard as "golf"). Fix the spelling in the prompt and regenerate only the wrong part if possible.
- Pull frames at 5 timestamps with `ffmpeg -ss T -frames:v 1`, make a contact sheet, and confirm each caption and highlight matches what is spoken at that time.
- Confirm the duration. Search the script for the forbidden words above.

## Step 8: Deliver

- Copy to /mnt/user-data/outputs/<Client>-<Topic>-Video.mp4 and send it with SendUserFile, display render.
- Report in plain language: voice used, credits spent, length, what was checked, a privacy note if real data shows, confidence with the reason, what could go wrong, and one next step under two minutes (play the first 30 seconds; upload over the old Drive file with Manage versions so existing links keep working).
- If a Zite or app page links to the old video, offer a Zite prompt that swaps the link.

## Gotchas

- The Chrome extension can fail mid-session. Playwright in the sandbox works for public apps with no login. Apps behind a login need her to attach screenshots or link her computer.
- NotebookLM videos skip screenshots, add hype, and invent rules. This skill replaces that route.
- ElevenLabs charges per call. Never call creative_generate_speech a second time to retry.
- Keep each shell step under the timeout: install voice models in the background, and split long ffmpeg or whisper jobs.