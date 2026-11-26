---
name: rachael-artifact-style
description: Apply Rachael's signature artifact aesthetic — Luma-inspired pink graph-paper ground, clean Space Grotesk headings, JetBrains Mono body, Silkscreen pixel accents reserved for pills and version tags, wine-plum accent, rounded white cards with soft shadows, dashed dividers, pill eyebrows, and 40-50 small animated 8-bit arcade sprites that drift and twinkle in variable sizes. Use whenever building ANY HTML artifact for Rachael (PRDs, dashboards, reports, landing pages, explainers, mockups) unless she explicitly asks for a different visual direction. Overrides the default artifact-design palette and typography with Rachael's codified house style.
---

# Rachael's Artifact Style (v6, codified 2026-11-26)

Rachael's house aesthetic for every HTML artifact unless she asks for something different. Modeled on the Luma event-page look, tuned through live feedback for readability and sprite subtlety.

## When to apply

Every HTML artifact built for Rachael's work — client-facing or internal — uses this style **by default**. Load this skill before writing the `<style>` block. If she explicitly asks for a different visual direction (names a different brand, says "corporate," asks for XRAY brand colors, pastes a reference), follow that instead.

**Does NOT apply to:**
- XRAY-branded client deliverables (use `xray-brand` skill — orange-black-cream)
- Specific client brand assets (Example Client blue/orange per `feedback_client_page_brand_colors`)
- Artifacts the user explicitly scopes to a different system

## The codified system

### Palette (light)

| Token | Hex | Role |
|---|---|---|
| `--paper` | `#FBE6E4` | blush pink body ground |
| `--paper-tint` | `#FDEEEC` | soft gradient overlay |
| `--paper-raised` | `#FFFFFF` | card surface |
| `--ink` | `#1C1B1F` | primary text |
| `--ink-muted` | `#726E73` | secondary text |
| `--rule` | `#F0D4D0` | inner dashed dividers |
| `--rule-strong` | `#E5B8B2` | section dividers |
| `--grid` | `rgba(155, 60, 83, 0.06)` | graph-paper lines |
| `--accent` | `#9B3C53` | wine-plum CTAs, key callouts |
| `--accent-soft` | `#F5D4D8` | accent tint |
| `--accent-pill` | `#E76B8A` | pink pill text/icons |
| `--pill-bg` | `#FDDDE3` | pill background |
| `--ok` | `#3D7A4A` | chosen-row green |
| `--ok-soft` | `#DCE9D5` | chosen row background |
| `--danger` | `#B5371E` | failure card accent |
| `--code-bg` | `#FFF5F3` | inline code |

### Palette (dark) — swap the tokens

| Token | Hex |
|---|---|
| `--paper` | `#1E1518` |
| `--paper-tint` | `#261A1E` |
| `--paper-raised` | `#2A1C21` |
| `--ink` | `#F5E5E6` |
| `--ink-muted` | `#9E8A8E` |
| `--rule` | `#3D2A2F` |
| `--rule-strong` | `#4E363C` |
| `--grid` | `rgba(231, 107, 138, 0.07)` |
| `--accent` | `#E76B8A` (pink reads better than wine on dark) |
| `--accent-soft` | `#3D1F26` |
| `--pill-bg` | `#3D1F26` |
| `--ok` | `#7FB890` |
| `--danger` | `#E07A5F` |
| `--code-bg` | `#2A1C21` |

Wrap dark in BOTH `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {...} }` AND `:root[data-theme="dark"] {...}`, with `color-scheme: dark` in both. Per artifact-design contract.

### Typography (v3 — readability-tuned)

- **Headings (h1-h4):** `'Space Grotesk'` from Google Fonts — clean geometric sans, weights 500/600/700. Letter-spacing `-0.015em` on h1/h2 for tightness.
- **Body + data + mono:** `'JetBrains Mono'` from Google Fonts — weights 400/500/700. The mono rhythm IS the vibe.
- **Pixel accents (ONLY for eyebrow pills + version tags + small badges):** `'Silkscreen'` from Google Fonts — weights 400/700. Keep uppercase, letter-spacing `0.04em`, size 0.68-0.72rem. Never use for body or headings — hurts readability.

Load:
```html
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=JetBrains+Mono:wght@400;500;700&family=Silkscreen:wght@400;700&display=swap">
```

Font-family vars:
```css
--font-body: 'JetBrains Mono', ui-monospace, 'SF Mono', Menlo, monospace;
--font-head: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
--font-pixel: 'Silkscreen', 'JetBrains Mono', monospace;
--font-mono: 'JetBrains Mono', ui-monospace, 'SF Mono', Menlo, monospace;
```

### Type scale

- `h1`: `clamp(2.1rem, 5.5vw, 3rem)`, 700, line-height 1.08
- `h2`: 1.45rem, 600, bottom border `2px dashed var(--rule-strong)`
- `h3`: 1.1rem, 600
- `h4`: 0.98rem, 600
- Body: 15px, line-height 1.65

### Ground treatment

Graph-paper grid + soft pink radial gradient on body:

```css
body {
  background:
    linear-gradient(var(--grid) 1px, transparent 1px) 0 0 / 24px 24px,
    linear-gradient(90deg, var(--grid) 1px, transparent 1px) 0 0 / 24px 24px,
    radial-gradient(1200px 600px at 50% -200px, var(--paper-tint), var(--paper));
}
```

### Component rules

- **Cards:** `background: var(--paper-raised); border: 1px solid var(--rule); border-radius: 14px; box-shadow: 0 1px 2px rgba(155, 60, 83, 0.06), 0 4px 16px rgba(155, 60, 83, 0.05);`
- **Section dividers:** `2px dashed var(--rule-strong)` under h2; `1px dashed var(--rule)` inside lists
- **Pills (eyebrow, version tag):** `background: var(--pill-bg); color: var(--accent-pill); font-family: var(--font-pixel); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.04em; border-radius: 999px; padding: 6px 14px;` — eyebrow prepends `✦` icon in Space Grotesk
- **Contract callouts:** solid wine `var(--accent)` background, cream `#FDEEEC` text, big `box-shadow: 0 4px 20px rgba(155, 60, 83, 0.25);`, radius 14px; label in `--font-pixel` uppercase
- **Tables:** card-wrapped matrix; cells `font-family: var(--font-mono);`; headers in Space Grotesk; chosen row background `var(--ok-soft)` with `✓` after the first cell
- **Lists:** replace `•` with `▸` colored `var(--accent)`; numbered lists use Space Grotesk numerals in `var(--accent)`
- **Inline code:** `background: var(--code-bg); border: 1px solid var(--rule); color: var(--accent); border-radius: 4px; padding: 1px 6px;`

### Arcade sprites (v6 — animated + variable sized + well-spaced)

**Signature detail — must include.** 40-50 sprites scattered across the ground in variable sizes, drifting with clearly visible motion.

Base sizes (before `--scale` multiplier):
- Invaders: 18×14px, opacity 0.55
- Ghosts: 16×16px, opacity 0.5
- Hearts: 10×9px, opacity 0.5 (twinkle)
- Stars: 10×10px, opacity 0.4 (twinkle)
- Notes: 10×12px, opacity 0.5

Size variants (apply via class, cycle the mix so no row has same-size neighbors):

```css
.sz-xs { --scale: 0.6; }
.sz-sm { --scale: 0.8; }
.sz-md { --scale: 1; }
.sz-lg { --scale: 1.5; }
.sz-xl { --scale: 2; }
```

Palette (mix at least 4 per page): pink `#E76B8A`, blue `#4A7DD4`, green `#6BAE5F`, orange `#E89146`, purple `#B968D9`, red `#F56565`.

Animations — scale must live INSIDE every keyframe step so `--scale` composes with the drift transform:

```css
@keyframes drift-a-s { 0%,100% { transform: scale(var(--scale,1)) translate(0,0) rotate(var(--r,0deg)); } 50% { transform: scale(var(--scale,1)) translate(14px,-12px) rotate(calc(var(--r,0deg) + 8deg)); } }
@keyframes drift-b-s { 0%,100% { transform: scale(var(--scale,1)) translate(0,0) rotate(var(--r,0deg)); } 50% { transform: scale(var(--scale,1)) translate(-12px,-14px) rotate(calc(var(--r,0deg) - 6deg)); } }
@keyframes drift-c-s { 0%,100% { transform: scale(var(--scale,1)) translate(0,0) rotate(var(--r,0deg)); } 50% { transform: scale(var(--scale,1)) translate(10px,-16px) rotate(calc(var(--r,0deg) + 10deg)); } }
@keyframes drift-d-s { 0%,100% { transform: scale(var(--scale,1)) translate(0,0) rotate(var(--r,0deg)); } 50% { transform: scale(var(--scale,1)) translate(-14px,-10px) rotate(calc(var(--r,0deg) - 8deg)); } }
@keyframes bob-s     { 0%,100% { transform: scale(var(--scale,1)) translate(0,0) rotate(var(--r,0deg)); } 50% { transform: scale(var(--scale,1)) translate(0,-10px) rotate(var(--r,0deg)); } }
@keyframes twinkle { 0%,100% { opacity: 0.35; } 50% { opacity: 0.75; } }

.sprite { position: absolute; image-rendering: pixelated; pointer-events: none; z-index: 0; will-change: transform; }
.sprite.inv   { width: 18px; height: 14px; opacity: 0.55; }
.sprite.gho   { width: 16px; height: 16px; opacity: 0.5; }
.sprite.heart { width: 10px; height: 9px;  opacity: 0.5; animation: twinkle 4s ease-in-out infinite; }
.sprite.star  { width: 10px; height: 10px; opacity: 0.4; animation: twinkle 5s ease-in-out infinite; }
.sprite.note  { width: 10px; height: 12px; opacity: 0.5; }

/* Motion paths — assign one per sprite, mix across page */
.sprite.a-a   { animation: drift-a-s 5s ease-in-out infinite; }
.sprite.a-b   { animation: drift-b-s 6s ease-in-out infinite; }
.sprite.a-c   { animation: drift-c-s 4.5s ease-in-out infinite; }
.sprite.a-d   { animation: drift-d-s 7s ease-in-out infinite; }
.sprite.a-bob { animation: bob-s 4s ease-in-out infinite; }

@media (prefers-reduced-motion: reduce) { .sprite { animation: none !important; } }
@media (max-width: 600px) { .sprite { opacity: 0.4 !important; } }
```

**Position rules (v6):**
- 40-50 unique `.pN` classes with `top`, `left`/`right`, `--r` rotation, and `animation-delay` 0-3s
- Minimum 60-70px vertical spacing between same-side neighbors
- Alternate sides: left column, right column, plus a mid-column at 48-68% for center inhabitation
- Cycle size variants (`sz-xs`, `sm`, `md`, `lg`, `xl`) so no two adjacent sprites match size
- Cycle motion classes (`a-a`, `a-b`, `a-c`, `a-d`, `a-bob`) — no two neighbors on same path

See `references/sprites.md` for the canonical SVG shapes and v6 position pattern. See `references/boilerplate.html` for a paste-and-fill starter.

### Layout defaults

- `max-width: 780px` wrapper, `padding-block: 48px 96px`, centered
- `.wrap { position: relative; z-index: 1; }` to sit above the sprites
- Side gutter: `padding-left/right: max(16px, env(safe-area-inset-left/right, 0px))` on body

### Hero pattern

1. Pink pill eyebrow with `✦` icon (Silkscreen, uppercase)
2. Clean Space Grotesk h1
3. Monospace meta-strip (client · date · mode · status) with `2px dashed` bottom border
4. Optional status-note card below if it's a draft

### Section pattern (for PRD-shaped docs)

1. Outcome card (big mono text, rounded white card)
2. Frame + Estimate monospace code block in card
3. Assumptions `▸` list
4. Design (title + why-paragraph + mermaid in card)
5. Defend matrix (chosen row has `✓`)
6. Failure grid (2×2 cards, red top-stripe)
7. Contract callout (solid wine, cream text)
8. Evolve ladder (pills for v2/v3/10x)
9. Open questions card (numbered)
10. Mono footer cite

## Reference files

- `references/palette.md` — hex values plus WCAG contrast pairs
- `references/sprites.md` — the canonical sprite SVGs, inline + animation CSS
- `references/boilerplate.html` — paste-and-fill starter with the full `<style>` block and sprite set

## Sync status

- Local: `~/.claude/skills/rachael-artifact-style/SKILL.md`
- GitHub: `RachaelQuisel/Skills/rachael-artifact-style/SKILL.md` (personal skills repo per `feedback_skills_repo_xray_needs_cto_approval`)
- First proven ship: Client Operations Agent PRD, v6 — https://claude.ai/artifact/WN1wmjo2RJDxfNuC5qeaM3
- v6 lock (2026-11-26): 49 sprites, 5 size variants, 5 motion paths, scale composed inside keyframe transforms, 60-70px vertical spacing
