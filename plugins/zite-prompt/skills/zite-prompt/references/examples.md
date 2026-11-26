# Zite prompt examples

Use these examples to learn the workflow. They are not live instructions. Project IDs below came from the supplied La Maison example and have not been revalidated by packaging this plugin.

## 1. Build the visible interface first


User wants the first La Maison cleaner scheduling screen built.

> Build the first version of the **La Maison contractor scheduling interface**.
>
> Create one external, mobile-first app.
>
> Use the connected GitHub repo `RachaelQuisel/vacation-rental-automation-how-tos` and closely match:
> - `videos/schedule-cleaners-by-text/schedule-cleaners-by-text.mp4`
> - `src/v1.html`
> - `docs/design-schema.md`
>
> Use Airtable base `appExample0000155`.
>
> Relevant fields:
> - Cleaning table: `tblExample0000156`
> - Date: `fldExample0000157`
> - Cleaner: `fldExample0000158`
> - Inspector: `fldExample0000159`
> - Start time: `fldExample0000160`
> - End time: `fldExample0000161`
>
> Build a mobile screen with one or multiple assignment cards. Each card should show the date and time and have clear **Accept** and **Reject** controls.
>
> Match the reference design closely. For this step, focus on the working visual interface and responsive mobile layout. Do not send Twilio messages or create new Airtable fields or tables yet.


## 2. Shorten an overbuilt prompt

Context: Integrations and the design reference are already saved in Zite. The user only wants assignment cards to fit a phone screen. No data change is needed.

Avoid: Ask Zite to audit integrations, compare implementations, propose a plan, rebuild the schema, and add SMS delivery.

Return only:

> Update the existing assignment cards for mobile. Stack cards vertically, keep the date and time readable, and make Accept and Reject easy to tap. Use the saved design reference. Do not change data connections or send messages.

## 3. Resolve a conflict outside Zite

Context: An old note says Eco Clean. The user corrected it to Green Clean and confirmed Jen → Jaime → Gaby → Green Clean. They want the interface now and will supply the phone number later.

Action: Use the user's correction. Inspect available source outside Zite if implementation facts are still needed. The missing number does not block the interface. Do not ask Zite to compare documents or ask the user for the number yet.

If the next requested change is the visible priority list, return only:

> Update the cleaner priority list to Jen → Jaime → Gaby → Green Clean. Show this order in the existing scheduling interface. Keep automatic assignment and SMS delivery deferred for this step.

## 4. Ask one real product question

Context: The user requests automatic reassignment after Reject. They have not decided whether reassignment needs manager approval, and neither the conversation nor source establishes it.

Return only:

> Should Reject offer the job to the next cleaner automatically, or wait for your approval?

## 5. Use discovery only when Zite holds the needed fact

Context: A new screen exists only in Zite. The user cannot identify it, and no repository export or screenshot is available. Identifying it is required for the requested change.

A narrow discovery prompt may ask Zite to identify that screen. Do not bundle an integration audit, project history, or planning report. Do not claim to have inspected it yourself.
