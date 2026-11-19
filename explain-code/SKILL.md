---
name: explain-code
version: 1.0.1
description: Explain how code works using an analogy, an ASCII diagram, a step-by-step walkthrough, and one gotcha. Use when the user says "how does this work", "explain this code", "walk me through", "teach me", or is onboarding to an unfamiliar codebase. The four-part structure is the point — analogy anchors intuition, diagram anchors structure, walkthrough anchors behavior, gotcha anchors what surprises people.
tags:
  - skill
---

# Explain Code

## Purpose in plain English

This skill helps you explain how a piece of code works through an example, a walkthrough, and a practical caution.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


When explaining code, always include all four parts:

1. **Analogy.** Compare the code to something from everyday life. Pick something the reader has hands-on experience with (mail sorting, a restaurant kitchen, a thermostat) — not another piece of code.
2. **Diagram.** ASCII art showing flow, structure, or relationships. The diagram should be readable at a glance; if it isn't, simplify.
3. **Walkthrough.** Step-by-step what happens when the code runs. Tie each step back to a line or function — concrete, not generic.
4. **Gotcha.** One common mistake or misconception about this code. What does someone trip on the first time they read it?

Keep it conversational. For complex concepts, layer multiple analogies — one for the high-level shape, another for the tricky part.

## Example: explaining a debounce function

**Analogy.** Debounce is like the elevator door. Every time someone walks through, the timer resets. The door only closes when nobody's been through for a few seconds.

**Diagram.**

```
keystrokes:   k--k-k----k------|----------> fires
timer:        [3s][3s][3s][3s reset to 0]
                                ^^^^^^^^^^ silence period
```

**Walkthrough.**
1. Caller invokes `debounced(x)`.
2. The function clears any existing timeout (`clearTimeout(timer)`).
3. It sets a fresh timeout that will run the actual callback after `delay` ms.
4. Every call resets the timer. The callback only fires when calls stop for `delay` ms.

**Gotcha.** Debounce delays the *first* call too — it never fires synchronously on the first invocation. If you need "fire immediately, then ignore for N ms", that's throttle, not debounce.
