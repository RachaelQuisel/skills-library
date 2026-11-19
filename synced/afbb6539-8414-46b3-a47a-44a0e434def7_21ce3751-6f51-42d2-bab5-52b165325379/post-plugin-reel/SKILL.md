---
name: "post-plugin-reel"
description: "Build and post a 6-second Instagram reel announcing a new plugin on @agentic_ai_sb. Use when Rachael says \"post [plugin] to IG\" with a repo link and tagline."
---

# Post a plugin reel to Instagram

Builds the locked-style announcement reel for one plugin and posts it to @agentic_ai_sb with a full description below it, tagging @the_rachael_review. Every reel must look identical in style, so use the canonical script and do not rebuild the format from scratch. Full reference: https://github.com/RachaelQuisel/reel-builder

## Where plugin details come from

Every plugin's details, including its name, tagline, and icon, come from Rachael's personal GitHub: https://github.com/RachaelQuisel. Each plugin has its own repo there. If the plugin is not under RachaelQuisel, stop and ask Rachael where it lives.

## Locked style (October 4, 2026)

- 1080x1350 (4:5 portrait), 6 seconds, 30fps
- Tagline at the top, "NEW PLUGIN" eyebrow, plugin icon in the center, plugin name typing out at the bottom
- Icon: the repo's own icon only
- A full description below each post
- Music rules:
  - A real, recognizable classical composition (Satie, Debussy, Chopin, Bach, and so on)
  - The composition must be public domain
  - The recording must be public domain, or CC BY with a credit in the description
  - No synth pads, no generic stock music, no ambient beds
  - A different piece for each plugin. Do not repeat a piece from the music table.

## Inputs to collect

- Plugin repo link (github.com/RachaelQuisel/<repo>)
- One-line tagline (if not given, take it from the repo README and show it to Rachael)
- Music piece (if not given, pick an unused piece in Step 3 and show it to Rachael)

## Step 1: Get the plugin details

```bash
cd ~/workspace/plugins
git clone --depth 1 https://github.com/RachaelQuisel/<repo>.git
head -40 <repo>/README.md    # plugin name, tagline, and what it does
find <repo> -name "*.png"    # icon
```

If the repo has no icon, stop and ask Rachael. Do not generate an icon.

## Step 2: Build the reel

```bash
python3 ~/workspace/ig-plugins/build_plugin_reel.py <plugin-slug>
```

This writes `~/workspace/ig-plugins/<plugin-slug>-reel-final.mp4` and a cover PNG. If the script is missing, stop and tell Rachael. Do not recreate it.

## Step 3: Add the music (every reel)

The script's default track (Satie, Gymnopedie No. 1) has already been used, so every new reel needs a new piece.

1. Check the music table below and pick a recognizable classical piece that is not on it.
2. Find a recording on archive.org or Musopen. Confirm the recording's license, not just the composition's. Use only public domain or CC BY recordings.
3. Download the MP3, then layer a 6-second clip under the reel:

```bash
ffmpeg -i <reel>.mp4 -t 6 -i <track>.mp3 \
  -map 0:v -map 1:a -c:v copy -c:a aac -shortest <reel>-music.mp4
```

4. After posting, add the piece to the music table in the reel-builder README so it is not reused.

Music used so far:

| Piece | Recording by | Recording license | Credit in description? |
|---|---|---|---|
| Satie, Gymnopedie No. 1 | Kevin MacLeod | CC BY 4.0 | Yes |
| Debussy, Clair de Lune | Caela Harrison | Public domain | No |

## Step 4: Write the description

Model every description on the Questions Worth Asking post from October 2, 2026 (https://www.instagram.com/reel/DeAsm-rCa1I/). One short paragraph per part, with a blank line between parts:

1. Hook: one line, second person, a moment the reader recognizes. It must work on its own, because Instagram cuts the description off after the first line or two.
2. Pain: one or two sentences on why the problem keeps happening.
3. What it does: "<Plugin name> <does what>." plus one short line on why it matters.
4. Credibility: "Built by me at XRAY, an official Anthropic partner."
5. Call to action: "What plugin do you wish existed? Drop it below. I'll pick one, build it, and share it here."
6. Tag: @the_rachael_review
7. Music credit, only if the recording is CC BY
8. Hashtags: #AItools #ClaudePlugins #buildinpublic

Rules: short sentences, plain words, no em-dashes. The hook and pain lines are new for each plugin; parts 4 through 8 stay the same.

Example:

```
You left the meeting. Then the real question hit you in the car.

It happens every week. The question that would have changed the whole conversation, arriving ten minutes too late.

Questions Worth Asking replays your meetings and finds the questions you didn't ask. Before the moment passes.

Built by me at XRAY, an official Anthropic partner.

What plugin do you wish existed? Drop it below. I'll pick one, build it, and share it here.

@the_rachael_review
#AItools #ClaudePlugins #buildinpublic
```

Music credit format for a CC BY recording:
`Music: "<Piece>" by <Performer> (<source>), CC BY 4.0`

## Step 5: Show Rachael before posting

Posting is public and cannot be quietly undone. Show Rachael the reel file, the cover, the music piece and its recording license, and the full description. Wait for a clear yes before Step 6.

## Step 6: Post to Instagram

Save the approved description to `<reel>-caption.txt`, then:

```bash
instagram-cli post-feed --account-id 17841439052023842 \
  --file <reel>.mp4 \
  --cover <reel>-cover.png \
  --caption "$(cat <reel>-caption.txt)" \
  --mentions '[{"user_fbid":"17841401896333226","x":0.5,"y":0.5}]'
```

- `17841439052023842` is @agentic_ai_sb (the posting account)
- `17841401896333226` is @the_rachael_review (tagged in the center of the frame)

## Step 7: Check that it posted

- Success: the CLI returns `{"media_fbid":"..."}`. Tell Rachael it posted and give her the media_fbid.
- Failure: show Rachael the exact error.
- HTTP 429: Instagram's daily posting limit was hit. Tell Rachael and suggest posting tomorrow. Do not retry in a loop.