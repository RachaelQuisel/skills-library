# Canonical arcade sprites (v6, 2026-11-26)

40-50 sprites per long page. Variable sizes, clearly visible motion, no piling. Behind content, `z-index: 0`; `.wrap` sits above with `z-index: 1; position: relative;`.

## Animation CSS

Scale lives INSIDE every keyframe step so `--scale` composes with drift transforms (if it were on `.sprite`, the keyframe `transform` would override it).

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

/* Size variants */
.sz-xs { --scale: 0.6; }
.sz-sm { --scale: 0.8; }
.sz-md { --scale: 1; }
.sz-lg { --scale: 1.5; }
.sz-xl { --scale: 2; }

/* Motion paths */
.sprite.a-a   { animation: drift-a-s 5s ease-in-out infinite; }
.sprite.a-b   { animation: drift-b-s 6s ease-in-out infinite; }
.sprite.a-c   { animation: drift-c-s 4.5s ease-in-out infinite; }
.sprite.a-d   { animation: drift-d-s 7s ease-in-out infinite; }
.sprite.a-bob { animation: bob-s 4s ease-in-out infinite; }

@media (prefers-reduced-motion: reduce) { .sprite { animation: none !important; } }
@media (max-width: 600px) { .sprite { opacity: 0.4 !important; } }
```

## Position pattern (v6)

40-50 `.pN` classes down the page. Rules:
- Alternate sides: left column, right column, plus mid-column at 48-68% for center inhabitation
- Minimum 60-70px vertical spacing between same-side neighbors
- Cycle size variants so no two adjacent sprites match size (e.g., xs → lg → sm → xl → md → sm → ...)
- Cycle motion classes (`a-a`, `a-b`, `a-c`, `a-d`, `a-bob`) so no two neighbors share a path
- Vary `animation-delay` 0-3s so sprites don't pulse together
- Vary `--r` rotation ±10deg for organic feel

```css
.sprite.p1  { top:  90px; left:   3%; --r: -6deg; animation-delay: 0s;   }
.sprite.p2  { top: 160px; right:  6%; --r:  4deg; animation-delay: 1.2s; }
.sprite.p3  { top: 240px; left:  58%; --r:  0deg; animation-delay: 2.1s; }
.sprite.p4  { top: 320px; left:   4%; --r: -3deg; animation-delay: 0.7s; }
.sprite.p5  { top: 400px; right:  4%; --r:  8deg; animation-delay: 1.8s; }
.sprite.p6  { top: 480px; left:  48%; --r:  5deg; animation-delay: 0.4s; }
.sprite.p7  { top: 560px; left:   5%; --r: -8deg; animation-delay: 2.5s; }
.sprite.p8  { top: 640px; right:  7%; --r:  2deg; animation-delay: 1.0s; }
/* ... continue to ~p49, maintaining 60-70px gaps and 3-column alternation */
```

HTML example combining all classes:

```html
<svg class="sprite inv a-a sz-lg p1" ...>
<svg class="sprite gho a-c sz-sm p2" ...>
<svg class="sprite heart sz-xl p3" ...>  <!-- no motion class; twinkle on .heart handles it -->
<svg class="sprite star sz-md p4" ...>
<svg class="sprite inv a-b sz-xs p5" ...>
```

## Sprite palette

Mix at least 4 hues per page:

| Color | Hex |
|---|---|
| Pink | `#E76B8A` |
| Blue | `#4A7DD4` |
| Green | `#6BAE5F` |
| Orange | `#E89146` |
| Purple | `#B968D9` |
| Red | `#F56565` |

## Space Invader (wide, 11×8 viewBox)

```html
<svg class="sprite inv a-a sz-md pN" viewBox="0 0 11 8" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><g fill="HEX"><rect x="2" y="0" width="1" height="1"/><rect x="8" y="0" width="1" height="1"/><rect x="3" y="1" width="1" height="1"/><rect x="7" y="1" width="1" height="1"/><rect x="2" y="2" width="7" height="1"/><rect x="1" y="3" width="2" height="1"/><rect x="4" y="3" width="3" height="1"/><rect x="8" y="3" width="2" height="1"/><rect x="0" y="4" width="11" height="1"/><rect x="0" y="5" width="1" height="1"/><rect x="2" y="5" width="7" height="1"/><rect x="10" y="5" width="1" height="1"/><rect x="0" y="6" width="1" height="1"/><rect x="2" y="6" width="1" height="1"/><rect x="8" y="6" width="1" height="1"/><rect x="10" y="6" width="1" height="1"/><rect x="3" y="7" width="2" height="1"/><rect x="6" y="7" width="2" height="1"/></g></svg>
```

## Pacman ghost (8×8 viewBox)

```html
<svg class="sprite gho a-b sz-md pN" viewBox="0 0 8 8" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><g fill="HEX"><rect x="2" y="0" width="4" height="1"/><rect x="1" y="1" width="6" height="1"/><rect x="0" y="2" width="2" height="1"/><rect x="3" y="2" width="2" height="1"/><rect x="6" y="2" width="2" height="1"/><rect x="0" y="3" width="8" height="1"/><rect x="0" y="4" width="8" height="1"/><rect x="0" y="5" width="8" height="1"/><rect x="0" y="6" width="1" height="1"/><rect x="2" y="6" width="1" height="1"/><rect x="4" y="6" width="1" height="1"/><rect x="6" y="6" width="1" height="1"/><rect x="0" y="7" width="1" height="1"/><rect x="2" y="7" width="1" height="1"/><rect x="5" y="7" width="1" height="1"/><rect x="7" y="7" width="1" height="1"/></g></svg>
```

## Heart (7×6 viewBox)

```html
<svg class="sprite heart sz-md pN" viewBox="0 0 7 6" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><g fill="#E76B8A"><rect x="1" y="0" width="2" height="1"/><rect x="4" y="0" width="2" height="1"/><rect x="0" y="1" width="7" height="1"/><rect x="0" y="2" width="7" height="1"/><rect x="1" y="3" width="5" height="1"/><rect x="2" y="4" width="3" height="1"/><rect x="3" y="5" width="1" height="1"/></g></svg>
```

## Star (5×5 viewBox)

```html
<svg class="sprite star sz-md pN" viewBox="0 0 5 5" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><g fill="HEX"><rect x="2" y="0" width="1" height="1"/><rect x="1" y="1" width="3" height="1"/><rect x="0" y="2" width="5" height="1"/><rect x="1" y="3" width="3" height="1"/><rect x="0" y="4" width="2" height="1"/><rect x="3" y="4" width="2" height="1"/></g></svg>
```

## Music note (5×6 viewBox)

```html
<svg class="sprite note a-bob sz-md pN" viewBox="0 0 5 6" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><g fill="HEX"><rect x="3" y="0" width="1" height="4"/><rect x="2" y="3" width="1" height="1"/><rect x="1" y="4" width="3" height="2"/></g></svg>
```
