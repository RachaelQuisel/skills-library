# Palette — hex + contrast notes

## Light theme

| Token | Hex | Role |
|---|---|---|
| `--paper` | `#FBE6E4` | body background (blush pink) |
| `--paper-tint` | `#FDEEEC` | soft gradient overlay |
| `--paper-raised` | `#FFFFFF` | card surface |
| `--ink` | `#1C1B1F` | primary text (AAA on paper, AAA on raised) |
| `--ink-muted` | `#726E73` | secondary text (AA Large on paper) |
| `--rule` | `#F0D4D0` | inner dashed dividers |
| `--rule-strong` | `#E5B8B2` | section dividers, strong borders |
| `--grid` | `rgba(155, 60, 83, 0.06)` | graph-paper lines |
| `--accent` | `#9B3C53` | wine-plum CTAs, key callouts, link color (AA on paper, AAA on white) |
| `--accent-soft` | `#F5D4D8` | accent tint for boxed callouts |
| `--accent-pill` | `#E76B8A` | pink pill text |
| `--pill-bg` | `#FDDDE3` | pill background |
| `--ok` | `#3D7A4A` | chosen/approved green |
| `--ok-soft` | `#DCE9D5` | chosen row background |
| `--danger` | `#B5371E` | failure card accent |
| `--danger-soft` | `#F7D7CE` | failure soft background |
| `--code-bg` | `#FFF5F3` | inline code |

## Dark theme

| Token | Hex | Role |
|---|---|---|
| `--paper` | `#1E1518` | body background (plum-black) |
| `--paper-tint` | `#261A1E` | gradient overlay |
| `--paper-raised` | `#2A1C21` | card surface |
| `--ink` | `#F5E5E6` | primary text |
| `--ink-muted` | `#9E8A8E` | secondary text |
| `--rule` | `#3D2A2F` | inner dividers |
| `--rule-strong` | `#4E363C` | section dividers |
| `--grid` | `rgba(231, 107, 138, 0.07)` | graph-paper lines |
| `--accent` | `#E76B8A` | pink accent (reads better on dark than wine) |
| `--accent-soft` | `#3D1F26` | accent tint |
| `--ok` | `#7FB890` | chosen green |
| `--danger` | `#E07A5F` | failure red |

## Signature contrast pairs

- `--ink` on `--paper`: 15.2:1 (AAA)
- `--ink` on `--paper-raised`: 16.8:1 (AAA)
- `--accent` on `--paper-raised`: 7.1:1 (AAA)
- `#FDEEEC` on `--accent`: 8.9:1 (AAA) — this is why contract callouts work

## Never do

- No tan-on-tan (Rachael's rule, per `feedback_client_page_brand_colors`)
- No orange accents (reserved for XRAY brand and Example Client)
- No blue accents (reserved for Example Client)
- No pure black backgrounds — use `#1E1518` plum-black
- No bright reds — `--danger` is muted `#B5371E`
