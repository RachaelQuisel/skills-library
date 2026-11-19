# System map: GoL Acuity to Airtable sync

Checked live on 2026-10-28 with `mcp__airtable__list_automations` on GoL Base `appcxLcvRF7dWQOHH`. Re-check before relying on any status below.

Source folder: `/Users/rachaelquisel/Claude-Work/CLIENTS/Guardians_of_Love_Jessica_Peoples/Automations/acuity-signups-airtable-automation/`

## Automations

| Automation | ID | Trigger | Script file | Status on 2026-10-28 |
|---|---|---|---|---|
| Acuity Sync - Booking Received (LIVE) | `wflDJq9zlDn2BOAOw` | Webhook `wtrKIWaljWqT5EaGq`. Acuity sends scheduled, rescheduled, canceled, and changed events. | `acuity-webhook-sync.script.js` (v7.6) | On, live mode |
| Acuity Sync - Class Zoom Details (LIVE) | `wflPJFT1XVMKzRt1J` | Every 15 minutes | `acuity-class-zoom-details.script.js` (v3) | On, live mode. Books at most 3 "GOL Zoom Seed" placeholder bookings per run. |
| Acuity Sync - Attendance Changed (DRAFT) | `wflwdnMXLUdD2ZwDO` | Training Event Status changes | none on disk | Off. Read-only placeholder. |
| GoL Weekly Sign-in Sheet vs Acuity Report (DRAFT) | `wflL97gPtcudkaJN6` | Daily schedule | none on disk | Off |
| Class Seed Reservation | not created in Airtable | Planned: hourly | `acuity-class-seed-reservation.script.js` (v6) | Written on disk only. Class Zoom Details now books seeds for new virtual classes. |
| Daily Recheck | not created in Airtable | Planned: daily 6am Pacific | `acuity-recent-bookings-reconciliation.script.js` (v1) | Written on disk only. Needs the `ACUITY_SYNC_WEBHOOK_URL` secret first. |

Docs in the source folder: `GOL-HowItWorks-2026-10-28-acuity-sync-booking-received.md`, `GOL-HowItWorks-2026-10-28-acuity-sync-class-zoom-details.md`, the `GOL-Design-*` files, `GOL-Rubric-2026-10-27-acuity-webhook-sync.md`, and `README.md`. The README is dated 2026-10-27 and still says Booking Received is off and G9 is live. Both are no longer true.

## Secrets (Airtable secret store)

- `ACUITY_USER_ID`: `eaceNgssGpEVtGbRk`
- `ACUITY_API_KEY`: `eacp4M7F6wVt4lxES`

Never print secret values.

## Tables

| Table | ID |
|---|---|
| Training Tracking | `tblIwxbi0ZJiw6Tc4` |
| Training Schedule | `tbly3vByUnxXcMzXh` |
| Training Module | `tblolTEXM40ehFbWp` |
| Applicant | `tblZsYxi9G7MVI7p5` |
| Automation Log | `tblprCx6rMOrVNhrf` |
| Automation Inventory | `tblIrEObjqmmqzAHb` |

## Key fields

Training Tracking (`tblIwxbi0ZJiw6Tc4`)
- Name `fld4kKkB5PKNeWVCk`; Schedule (link) `fldvdldkNoLSVJn3J`; Applicant (link) `fldcW9RkTnallmk9m`; Training Module (link) `fldYgQhudzyBY3aG3`
- Registration Status `fldlG55653Z5Wj0AQ`; Training Event Status (attendance, Pending on create only) `fldsf0Wh8mbAhjyGx`
- Acuity Appointment ID `fld7fdHcORqzNA6k9`; Acuity Sync Review Needed `fldFoNn8deelD2abp`; Training Notes `fldgEMeGa27QG4SJ7`
- Raw Acuity copies: Email `fldVtzvXr59BlYjJP`, Display Name `fldUYmXcQrdxkWwzu`, Phone `fld1fcwh8hbHHfB11`, Client Type `flddeAAjDSwjan8Cu`

Training Schedule (`tbly3vByUnxXcMzXh`)
- Name `fldHJJ8tVl3cRmIg4`; Date (Pacific date) `fldemWB5fh2mRSOxn`; Start Date/Time `fldEC91sPPHhBU8Jh`; End Date/Time `fldv7UvMeYyTqxBqd`
- Module (link) `fldeqvqriflxXbtij`; Language `fldcxMakosRycjzbi`; Modality `fldwNzmirv9vAtXUi`; Location `fldolYTgZUaHKHwDO`
- Source System `fldcoe1lIIsHfqWU4`; Source Session ID (Acuity classID or derived key) `fldF90pI8qCy532IZ`; Session Status `fldjt11YNHRM3d18D`; Source Notes `fldaYegHgmOek2uHB`
- Zoom Meeting ID `fldIXZdGuB2lzi3Tz`; Zoom Join URL `fldy5mIojAFuM4GVX`; Meeting Password `fldJXifWowcTuZhyy`; Training Calendar URL `fldHhuDUitfIzeqbg`

Training Module (`tblolTEXM40ehFbWp`): Name `fld0Bq7Rw4BoapPZD`; Pre/Post `fldTfMbT8KmhLsPFz`; Acuity Appointment Type IDs `fld0R4mP0EItO2fkY`

Applicant (`tblZsYxi9G7MVI7p5`): First `fldXILWlFm3Fs6lV1`; Last `fldv90LoKbXZkLuQL`; Phone `fldCQT4fpRLOknGVe`; Email `fldrFb3uVRV06GvAn`; Phase (formula) `fldxo8PJcmMYpR8KC`

Automation Log (`tblprCx6rMOrVNhrf`): Automation Name `fldAzRb77rplNPN3G`; Outcome `fldsCGDfbvYjABDfH`; Source Record ID `fld79z7iaYG77JgwT`; Skip Reason `fldSsceMXWxLvwJVq`; Fields Written `fldKsjhYflTPoXoMb`; Notes `fldCcStYHWTB6jg9x`; Logged At `fldyuXhJGpLkZ6Twh`; Sync Technical Details `fldh7enGFnpqoO8Np`; Script Error `fldqmT2HnWYzL0vvr`

These IDs come from the script constants. Re-pull the live schema before writing code against them.

## Retired and must stay off

- GitHub workflow `gol-acuity-sync.yml` in `XRAY-INC/GUARDIANS-OF-LOVE` (workflow ID `337453020`). Disabled manually 2026-10-28 01:03 Pacific. Last run 2026-10-28 00:42 Pacific, failed.
- Claude cloud routine `trig_01VJaM1cogMuBSF8gHnpk5JJ` "GoL Acuity sync - hourly start". It started that workflow with apply=true every hour at :41. Disabled 2026-10-28 00:57 Pacific.
