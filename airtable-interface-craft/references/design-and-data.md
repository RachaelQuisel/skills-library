# Design and data

## Preserve personality with a coherent visual language

Use the existing source and user feedback to identify what makes this interface recognizable. Keep its metaphor when it helps the job. Do not replace a loved scene with a generic dashboard just because cards are easier to code.

Share palette, type sizes, spacing, borders, shadows and motion across the scene and functional controls. Readability is a separate check: enlarge important text and touch targets, strengthen contrast, and test truncation/wrapping with realistic long names. Decorative SVG/CSS can keep a paste-ready interface self-contained when suitable.

Plan the geometry and layers. Reserve space for labels, objects and paths; keep text out of the road or action area. Put decorative layers behind actionable objects and disable their pointer events. Keep essential controls reachable even when a scene is large. Scope SVG IDs so multiple rendered instances do not collide.

Color needs an explicit meaning and a text key. Selection should add a ring/glow or other indicator without erasing status. Validate precedence against actual statuses; a phase named Completed, a Hold status or an unchecked Active flag may not mean the case is closed.

Tie motion to selection or a confirmed milestone. Clean up animations/canvases and account for reduced motion. Choose what works for this interface rather than making houses, cars or confetti mandatory in every product.

## Show a little detail at the right time

Use progressive disclosure: choose a family/application, then its relevant tabs, then expandable subtasks or document details. Keep names, assignments, dates and linked indicators near the action they explain.

Offer a practical list/search route alongside a visual scene. Both must select the same stable record. Include all relevant people's full names in search. Sorting and filtering should help locate work without silently changing independently defined running totals.

Use native semantic controls, explicit accessible labels, keyboard focus, pressed/expanded states and live save messages. Inspect all tabs and actions at mobile widths; scrolling belongs inside large calendars/scenes rather than forcing the whole page sideways. Check dark mode if supported. These targeted checks are not a full accessibility certification.

## Model relationships before rendering

Use verified table and field IDs in mappings and API payloads. For reusable interfaces, keep configurable mappings where useful; verified IDs can be defaults for an intentionally fixed base. Check the field belongs to its table and has the required type. SDK calls still need the correct field-type payload.

Describe templates, instances and self-linked parents separately. Validate application membership, parent relationships, task/template agreement and linked indicators before enabling actions. Deduplicate by record ID, not approximate names. Preserve verified legacy mappings where needed; do not silently invent a name-match fallback.

Staff-specific subtasks may need a parent owned by someone else for context. A contextual heading does not grant authority to complete that parent. Keep actions restricted to the eligibility rule the user actually approved. Preserve role exceptions and history without turning historical/context rows into actionable work.

Person-specific training, certificates and document evidence belong to the selected person. Show primary/co-applicant or other ordering only where the project's relationships establish it. A scheduled class alone is not attendance or completion.

## Use data honestly

Saved deadlines and completion evidence take precedence over display-only planning notes. If calculated notes are requested, label their start event, units and counting rule; do not overwrite stored dates or change automations outside scope. Missing anchors, holiday coverage and ambiguous dates remain pending.

Do not add obligation propagation, a deadline engine or extra tables merely because a linked indicator exists. Keep the smallest connected experience that handles the user's job.

Missing/excluded tables, fields or unsupported types need an actionable configuration message, not a misleading empty-success state. Distinguish no assigned work, finished work, no matching filters, loading and broken data. Keep hooks unconditional within mounted components; guard required tables before mounting data-hook children.
