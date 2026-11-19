---
name: "gol-confirm-received-date"
version: 1.0.0
description: "Sync GOL and DIUP families from Binti into the GoL Base Application table: received dates for Applying families, RFA Approval (Initial Approval) dates for In Renewal families, new Application + Applicant + Team Assignment records for anything Binti has that Airtable doesn't, and a review flag plus note for anything the two systems disagree on. Use whenever Rachael asks to confirm, check, fill, or update received dates or approval dates, says Binti is the source of truth, asks whether new families landed, says run it again, or signs in to Binti as Jessica Peoples or Dangerfield. Writes without asking, and writes only what differs."
---

# Sync Binti into the GoL Base

Binti is the source of truth. Airtable gets corrected to match it. Rachael decided on 2026-10-28 that this skill writes to the base without asking first, so run the whole thing, then report what changed. The only thing that stops for a decision is a family that moved between agencies (step 7): write the date, flag it, but do not change Client Type until Rachael says so. Anything else Binti and Airtable disagree on that no rule below covers gets the review flag and a note (step 5b), never a guessed status.

Which agency depends on who is signed in to Binti:

| Binti login | History entry to match | Client Type |
|---|---|---|
| Jessica Peoples | `Assigned to Guardians Of Love, FFA` | GOL |
| Dangerfield Training Support | `Assigned to Dangerfield Institute` | DIUP |

Each login can only open its own families. The other agency's pages come back as "You do not have permission to visit that page" and the dashboard shows only that agency's tabs, so a full sync is two runs: one per login. Rachael signs in to one, you run, she switches, you run again.

Two anchor dates, one per Binti tab:

- **Applying tab**: Date Received = date of the most recent agency assignment entry in the family's Binti history. It equals the Sent date on the "You have a new application assigned to you in Binti" email from contact@binti.com (verified on 21 families), so the rfatraining@guardiansoflove.org inbox is a cross-check, not the source.
- **In Renewal tab**: RFA Approval Date = Binti's "Initial Approval Date" column (GOL also calls it the Anniversary Date). It sets the 1-year anniversary clock: outreach at 9 months, Modules 5 & 6 registration 60 days before the anniversary (QPI #7), Modules 5 & 6 done within 1 year, and a 90-day CPR window if CPR wasn't done during initial assessment. It goes in Airtable's "Initial approval date" field.

Phase and Case Status are two fields. Phase is the lifecycle stage (Applying / Approved / Completed / Renewal); Case Status is the administrative state. "Applying" as a Case Status is only for Phase 1 intake. A record in Phase Renewal must carry one of: Confirming Minor Placement, Annual Training - Active, Annual Training - Complete, or Renewal - Discontinued, No Minor in Home. Binti has no equivalent of GOL's status model, so a record coming in from the In Renewal tab gets mapped, never left at Applying.

The team lives in the Team Assignment table: one row per staff member on a family, with a Role. The staff dashboards filter on it (Application → Team Assignment → Assigned Airtable Users), so a family with no Team Assignment is invisible to every staff member. Binti's "CBO workers assigned" is that staff member; "Approvals workers assigned" and "Support workers assigned" are county (DCFS) workers and go in text fields.

## Fixed references

- Binti host: `https://family.binti.com`. Every admin path in this skill hangs off it, so `/admin/homepage` is `https://family.binti.com/admin/homepage`; the same host serves the family portal and the staff `/admin` pages. `fosters.binti.com` and `app.binti.com` do not resolve at all (DNS_PROBE_FINISHED_NXDOMAIN, checked 2026-11-04); don't spend calls on them.
- Base `appcxLcvRF7dWQOHH`, Application table `tblle86w7gTHmBsDS`, Applicant table `tblZsYxi9G7MVI7p5`, Team Assignment table `tblmNxsRPLxsxSNbr`, Staff table `tbltuqSEdJuKk6763`
- Application fields: Name `fldCubvIKsoC1M8oL` ("Last Household — RFA"), RFA ID `fldR9l7Jjm6Gr9yJV`, Binti ID `fldsxEB5mSLl3MBK6`, Active `fld5G3LCJtl6wCvp6`, Date Received `fldWbH6PwOj8lZ703`, Manually Confirmed Received date `fldpmVlQbmxoNRine`, Initial approval date `fldG3xgk3LpkFTbdo`, Renewal due date `fldDLseqTQoWoPFdB`, Client Type `fldJjO030rVBeh6n8` (GOL `selkZu4OFILtIzpHc` / DIUP `sel5QHEDL1czk4b9i`), Case Status `fld3HrhY9xh9EWTso`, Phase `fldTdVgdBNiuBnbXW` (Renewal `selA4oR5bcNjEyJSp`, Applying `selqs93JCmLIW9weP`), SPA `fldsWPJzQeeVlabQ2` ("1"–"8"), Applicants link `fldITF9OcRYSU952a`, Team Assignment link `fldw87HpCuFHjUdiQ`, DCFS Worker Assigned `fldzn2ZCW4hzHnRSr` (Binti "Approvals workers assigned"), Support worker assigned `fldeBrc7UREwNl68x` (Binti "Support workers assigned"), Binti Sync Review Needed `fldm30eHweq3c33Eq` (checkbox, created 2026-10-28), Status Change Log `fldY2Zqr3HvowSQ6W` (append-only text; read it first and keep every existing line)
- Applicant fields: First Name `fldXILWlFm3Fs6lV1`, Last Name `fldv90LoKbXZkLuQL`, Role `fldeRCtbJzUJpdXB6` (Primary Applicant / Co-Applicant), Applications link `fldzn2PNiBshSWYW6`
- Team Assignment fields: Staff Member `fldfRK3pGhbsTwLbO`, Applications `fldi7DV1HIyOzgIY7`, Role `flddJT0pGp5fBmcOM`. Staff fields: Name `fldH5EWNdVzt3gmAt`, Role `fldpueTa2UYhkKeSb`. Role records: RHAS Specialist `recSsQxFXpqXlj5LR` (this record was named Paraprofessional until 2026-10-29; Brenda Perez, Towana Hooks, Kenia Mendez and Jennifer Powell carry it), Supervisor `recqIjAIVI3bbSfvy` (Jessica Peoples), Coordinator `recSsN1JpZcrKO7mu` (Leslie Izaguirre), Admin/QA `recjgCs0cgGZ8xiC5`, Trainer `recA9BAUTc7fmJge8`, Procurement `rec4M9ojPyZm2sfaO`. Read the staff member's Role from the Staff table on every run; names change.
- Dates: the three date fields are date-time fields in Pacific time (Rachael's choice). Write `YYYY-MM-DD`; Airtable stores midnight Pacific (`07:00:00.000Z` or `08:00:00.000Z`). Compare on the first 10 characters of what Airtable returns.
- Binti history: `/admin/applications/<Binti ID>/application_history`
- Binti tabs: `/admin/application_dashboards?scope=applying&per_page=100&page=N` and `scope=in_renewal_process`

Airtable connector limits: checkbox filters use `=` with `true`/`false` (no `!=`); an `or` filter takes at most 50 operands (use 44) and may mix fields (Binti ID and RFA ID in one filter is fine), but no nested groups inside the operands; `fieldIds` cannot repeat; link fields can't be filtered by record ID; `isEmpty` works on date fields; writes go 10 records per call; select values are written as plain names; an unchecked checkbox is simply absent from what comes back. Say "write 3 of 11" between calls so Rachael can see it's progress, not a loop, and keep browser batches to 2 pages.

Write the minimum (Rachael's rule, 2026-10-28). Before any update, read the fields you are about to write and send only the records where the value is blank or differs from Binti. Don't resend a value that already matches, and don't touch fields the step doesn't name. Keep the before-values so the report can say changed vs filled. When the sync changes Phase or Case Status on an existing record, append one dated line to Status Change Log in the base's own format (`YYYY-MM-DD — Field: old → new; ...; evidence: ...; run: Binti sync YYYY-MM-DD; written by: Claude for Rachael.`), never replacing what is there.

## Step 1: Check the Binti sign-in yourself

Load the `chrome-browser` skill, call `tabs_context_mcp` (with `createIfEmpty`), navigate a tab to `https://family.binti.com/admin/homepage`, wait for the body to render (poll up to 20 seconds; an immediate read looks like a failed sign-in) and run `(document.body.innerText.match(/Welcome, ([^!|\n]+)/) || [null,'not signed in'])[1].trim()`. The name picks the agency row. Several Chrome browsers are connected to Rachael's account and the connector resets its selection between turns; she told me to find the right one myself (2026-10-28), so call `select_browser` for each deviceId in turn, check the homepage, and only ask her to sign in when every browser shows the login page. A redirect to `/users/login` means nobody is signed in. Never type her password; when only one browser is connected there is no fallback, so ask her to sign in on the tab that is already on the login page and name which login this run needs. Then re-read `/admin/homepage` and take the name from the page, not from her message. The homepage also gives a size estimate before scraping: "Initials Case Load" is roughly the Applying count and "Renewals Case Load" the In Renewal count. A Binti session expires after a few idle hours; if a later page lands on `/users/login`, ask for the sign-in again. The display names shift between calls; go by deviceId. Sign-in has only persisted in one browser at a time. The helpers saved in `localStorage` (steps 2 and 3) live in that browser's Binti origin and survive a login switch, so the second run of the day reuses them.

## Step 2: Scrape both Binti tabs

Background fetches of the dashboard redirect to the homepage, so navigate the tab to each page and scrape. The table streams in after load: poll until the row count holds steady for 2 seconds before reading, or you get 0, 63 or 15 of 100 rows. Store each page under its own `sessionStorage` key with the date in it (`g29A1`, `g29R3`, `d29R2`), never reuse a key, and before leaving the tab check that the number of unique Binti IDs equals the "1 - 100 of N" total; one overwritten key cost a whole page once. A tab with fewer than 100 rows shows no "of N" text; the row count is the total.

```js
window.golScrape = async (key) => {
  let last=-1, stable=0;
  for (let k=0;k<60;k++){ const tb=[...document.querySelectorAll('table')].find(t=>t.querySelectorAll('thead th').length>5); const n=tb?tb.querySelectorAll(':scope > tbody > tr').length:0; if(n>0 && n===last){ if(++stable>=4) break; } else stable=0; last=n; await new Promise(r=>setTimeout(r,500)); }
  const tb=[...document.querySelectorAll('table')].find(t=>t.querySelectorAll('thead th').length>5);
  if(!tb) return key+' NO TABLE';
  const w=s=>(s||'').replace(/\s+/g,' ').trim();
  const rows=[...tb.querySelectorAll(':scope > tbody > tr')].map(tr=>{const tds=[...tr.querySelectorAll(':scope > td')]; const a=[...tr.querySelectorAll('a')].map(x=>x.getAttribute('href')||'').find(x=>/\/admin\/applications\/\d+$/.test(x)); if(!a||tds.length<5) return null; const t=tds[0].innerText||''; const n=tds.length;
    return [a.split('/').pop(), (t.match(/RFA ID:\s*([0-9A-Z]{8,10})/)||[])[1]||'', w(t).split(' (')[0].slice(0,40), tds[n-3].innerText.trim(), tds[n-2].innerText.trim(), w(tds[1].innerText).slice(0,80), w(tds[2].innerText).slice(0,80)].join('|')}).filter(Boolean);
  sessionStorage.setItem(key, JSON.stringify(rows));
  const tot=(document.body.innerText.match(/\d[\d,]*\s*-\s*\d[\d,]*\s*of\s*(\d[\d,]*)/)||[])[1]||'?';
  return key+' rows='+rows.length+' total='+tot; };
localStorage.setItem('golScrapeSrc', window.golScrape.toString());   // later pages: await (eval('('+localStorage.getItem('golScrapeSrc')+')'))('g29R2')
```

In Renewal columns from the end: Initial Approval Date is third from last, Renewal Due Date second from last ("MM/DD/YY (n days)", take the date part). `tds[1]` is county workers, `tds[2]` is CBO workers. For the Applying tab the table has only the first cell to read, so the Applying scrape is the same minus the date and worker fields. A family cell that carries "Other Adults:" text can defeat the RFA regex and come out with a blank RFA ID; match those by Binti ID, and if the Binti ID is new, read the RFA ID from the family's history page (both the old and the reissued application number carry it).

To get the rows out without truncation: convert dates to ISO in the page, write the compact rows (`id|RFA|approval|due`, Applying rows as `id|RFA` joined with `;`) into `document.body.innerHTML` as a `<pre>`, and read them with `get_page_text` (about 50,000 characters per read; 680 renewal rows plus 221 applying rows fit in one). Put checksums at the top of the same `<pre>`: for each block of 100 rows, the count and the sums of the digits in the Binti ID, RFA ID, approval date and due date columns. Then write the rows to `gol_applying_<MMDD>.txt`, `gol_renewal_<MMDD>.txt` (or `diup_...`) in the scratchpad and recompute the same sums in Python. They must match before anything else happens; a transcription slip in one digit is a wrong family. Never return `location.href` or a fetch's `r.url` from `javascript_tool`; any output containing a query string comes back as "[BLOCKED: Cookie/query string data]".

## Step 3: Match every Binti family to Airtable

First diff today's files against the previous run's files for the same login (keep them in the scratchpad; the first run of a session may have to re-pull them). Three lists come out: Binti IDs new on a tab, Binti IDs gone from a tab, and renewal rows whose approval or due date changed. Families present both days with unchanged dates were verified on the earlier run and need no lookup. Look the rest up in Airtable with one `or` filter mixing `Binti ID =` and `RFA ID =` operands (44 at most), pulling the fields the steps write plus Active, Binti Sync Review Needed and Status Change Log so you have the before-values. A Binti ID that left one tab and an RFA ID that arrived on the other tab under a new number is the same family moving (Applying → In Renewal when approved, or a renewal reissued under a new number); treat it as "found by RFA ID" below.

Without a previous run to diff against: under about 150 families, look each Binti ID up in `or` filters of 44, then look up the RFA ID for anything not found. Over that: have a helper agent fetch the whole Application table (pageSize 100, about 33 pages for 3,240 records, read-only) into a JSON file in the scratchpad and do the matching in Python. A whole-table snapshot goes stale within hours: another session may run this skill for the other login the same day, so before creating any family or writing any before-value taken from the snapshot, re-read those records from the live base by Binti ID and RFA ID (2026-11-04: six "new" DIUP families had been created by an earlier run that afternoon). Three outcomes:

- **Found by Binti ID**: the record is current.
- **Found by RFA ID with a different Binti ID**: Binti issued a new application number (renewal, or a family that reapplied). Update Binti ID to the number Binti shows now, and apply step 5 if it is now on the In Renewal tab.
- **Not found**: a new family. Navigate to `/admin/applications/<id>` and read it with the page helper below. Create an Application record (Name, RFA ID, Binti ID, Client Type from the login, SPA, DCFS Worker Assigned from "Approvals workers assigned", Support worker assigned from "Support workers assigned") plus one Applicant record per applicant and co-applicant (last word of the name is the Last Name, everything before it is the First Name, Role Primary Applicant or Co-Applicant) plus one Team Assignment per CBO worker (step 6). "Other adults" in the household do not get Applicant records.

```js
localStorage.setItem('golPageSrc', (async()=>{ for (let k=0;k<40;k++){ if(document.body && /Approvals workers assigned/.test(document.body.innerText)) break; await new Promise(r=>setTimeout(r,500)); }
  const L=document.body.innerText.replace(/\n{2,}/g,'\n').split('\n'); const pick=(re,n)=>{const i=L.findIndex(l=>re.test(l)); return i<0?'(none)':L.slice(i,i+n).join(' | ');};
  return [location.pathname, 'TITLE: '+document.title, pick(/^Primary Applicant/i,3), pick(/^Co-?applicant/i,3), pick(/^Other adult/i,2), pick(/^SPA/i,1), pick(/^This application/i,1), pick(/^RFA ID/,1), pick(/^Status\t/,1), pick(/^Status$/,2), pick(/Approvals workers assigned/,8)].join('\n').slice(0,1600); }).toString());
// on each family page: await (eval('('+localStorage.getItem('golPageSrc')+')'))()
```

The page title carries Binti's status in parentheses, for example "LA County RFA Renewal (Closed (Post Approval) 10/29/2026)" or "(Inactive)"; quote it as written in notes and reports. A page that lands on the homepage instead means "You do not have permission to visit that page" (the other agency's family). A background `fetch` of `/admin/applications/<id>` also lands on the homepage even for this login's own family, so family pages are read by navigating, never by fetch; the history page (`.../application_history`) does work by fetch and carries the status change ("Status changed to: Withdrawn (Pre-Approval) Status date changed to: 10/15/2026 Status reason changed to: ..."), which is enough for the withdrawn and inactive notes without opening each page.

## Step 4: Applying families, received dates

Read each new family's history in the page. For a handful, a plain `await` loop inside one `javascript_tool` call is fine. For more than about 10, the 45-second timeout bites: run the loop in the page and poll, and tell Rachael to leave the tab open. Set `AGENCY` from the login table.

```js
window.golRun = {done:false, out:[], i:0};
const AGENCY = /Assigned to Guardians Of Love/i;   // or /Assigned to Dangerfield/i
const list = [['856815','19R062520']];              // [Binti ID, RFA ID] pairs
(async () => {
  for (const [id, rfa] of list) {
    try {
      const r = await fetch(`/admin/applications/${id}/application_history`, {credentials:'include'});
      const h = await r.text();
      if (!r.url.includes('/application_history')) { window.golRun.out.push([id, rfa, 'cannot open', '']); }
      else {
        const d = new DOMParser().parseFromString(h, 'text/html');
        const rows = [...d.querySelectorAll('tr')].map(tr => [...tr.querySelectorAll('td')].map(c => (c.textContent||'').replace(/\s+/g,' ').trim()));
        const hit = rows.find(c => c.length >= 3 && AGENCY.test(c[2]));
        const other = rows.find(c => c.length >= 3 && /Assigned to (Guardians Of Love|Dangerfield)/i.test(c[2]) && !AGENCY.test(c[2]));
        const rfaOk = h.includes(rfa);   // match anywhere; pages can list a second ID first
        window.golRun.out.push([id, rfa, hit ? hit[0].slice(0,10) : 'no entry', (rfaOk ? '' : 'RFA MISMATCH') + (other ? ' OTHER AGENCY ' + other[0].slice(0,10) : '')]);
      }
    } catch (e) { window.golRun.out.push([id, rfa, 'error', String(e).slice(0,60)]); }
    window.golRun.i++;
  }
  window.golRun.done = true;
})();
'started ' + list.length
```

Poll with `await new Promise(r=>setTimeout(r,40000)); ({i:window.golRun.i, done:window.golRun.done})`. About 100 families takes 3 to 4 minutes, sometimes 10 when Binti is slow; a poll that times out has not killed the loop, so read `window.golRun.i` again before assuming anything. History lists newest first, so the first match is the most recent assignment. The OTHER AGENCY check only knows GOL and Dangerfield; a family that came from a third agency ("Assigned to The Community College Foundation") just shows in the assignment list, so read the first three assignment lines and mention any other agency in the report. Worker lines ("Assigned to CBO worker: ...", "Assigned to approvals worker: ...") are not agency assignments; a regex for "Assigned to" alone catches them and floods the report.

Write for every Applying family whose values differ: Date Received = Binti date, Manually Confirmed Received date checked, Active checked, Case Status Applying, Phase Applying, Client Type from the login. New families get all of that at creation.

A family that dropped off the Applying tab since the last run: open its page and quote Binti's status line. If the same RFA ID now sits on the In Renewal tab, it was approved; handle it in step 5. If Binti shows a withdrawal ("Withdrawn (Pre-Approval) 10/28/2026"), there is still no agreed Case Status mapping: flag it and write the note (step 5b), change nothing else.

"Cannot open" means Binti said "You do not have permission to visit that page." Report that wording and nothing more; those families belong to the other login.

## Step 5: In Renewal families, approval dates and status

Write for every In Renewal family whose values differ: Initial approval date = Binti's Initial Approval Date, Renewal due date = Binti's Renewal Due Date (date part only, before the parenthetical), Phase Renewal, Binti ID = the renewal application number, Client Type from the login. Active stays as it is. Binti moves a renewal due date out two years when a family renews, so a changed due date is normal. Airtable holds many Phase Renewal records Binti's tab doesn't list (closed, withdrawn, denied families); leave them alone and give the count in the report.

Case Status mapping for a record coming from the In Renewal tab:

- Already one of the four renewal statuses: leave it.
- Case Status Applying (or blank) and Active unchecked: set Confirming Minor Placement. Staff move it on from there once outreach confirms a minor is in the home.
- Case Status Applying and Active checked: set Annual Training - Active, since it is already an open caseload item (Pensamiento, 2026-10-29).
- Any other status (Withdrawn, Non-completion - Denial, Approved, Completed): leave it and list it in the report.
- New renewal family: create with Confirming Minor Placement, Phase Renewal, Initial approval date, Renewal due date, Active unchecked, and no Date Received.

A renewal family that left the In Renewal tab since the last run: open its page and quote the status. Binti "Inactive" or "Closed (Post Approval) <date>" (Rachael's rule, 2026-10-29): uncheck Active if it is checked, append a Status Change Log line saying Active was set to inactive because Binti shows the renewal as inactive or closed and that staff may need to change the Case Status, and set the review flag. Do not write Case Status; that is a staff decision. A page that lands on the homepage under this login means the family left for another agency: flag it, write the note, and leave Client Type alone until Rachael decides (step 7).

## Step 5b: The review flag

Rachael's rule (2026-10-28): when Binti and Airtable disagree and no rule above covers the case, check Binti Sync Review Needed and append one dated Status Change Log line; change nothing else. Cases seen so far: Phase Renewal with Case Status Annual Training - Active while neither In Renewal tab lists the family (65 flagged on 2026-10-28; Annual Training - Complete records off the tab are not flagged, a finished year is not a contradiction); Withdrawn in Binti while Airtable says Applying and Active (Herndon); Withdrawn in Airtable while Binti still shows an open application (Gutierrez Perez); Inactive or Closed renewals (step 5); a family Binti no longer lets this login open (Jones). The note names the Binti tab or status as written, the login and date it was checked, what Airtable has, which rule is missing, and "nothing else changed". Staff uncheck the flag after review. Report flagged records in their own group. Read the flag before writing it: a record flagged on an earlier run (Herndon, Gutierrez Perez) is left alone, not re-flagged.

## Step 6: Team links

For each CBO worker on the family's Binti page, find the Staff record whose Name matches after collapsing double spaces ("Towana  Hooks" in Staff is "Towana Hooks" in Binti). Exactly one match: create a Team Assignment with Staff Member = that record, Applications = the Application, Role = that staff member's own Role from the Staff table. Zero or two matches, or "Unassigned": create nothing and name the family in the report. This runs for every family created, and also for an existing family that has no Team Assignment at all when Binti now names a CBO worker (Ceja, 2026-10-29: Binti said Unassigned the day before). Existing Team Assignments are never edited or removed.

## Step 7: Verify, then report

After the writes, read back every record touched (by Binti ID, 44 per lookup; a separate helper for big runs) and compare Binti ID, Phase, Case Status, Active, the two dates, the flag and the linked Applicants and Team Assignments against what was planned; report the mismatch count (it should be 0). Then one CSV with a row per field: group (created, changed, filled, flagged, matched, left alone), family, RFA ID, Binti ID, field, old value, new value, note with the Binti evidence. Plain counts ("7 changed"). Send it, then a short message: what was created, changed, flagged, what was left alone and why, and the one thing that needs her decision if any. List separately: cannot open, RFA mismatch, no agency entry, withdrawn or closed, unmatched CBO worker, other-agency assignments, and OTHER AGENCY hits (a family assigned to one agency, unassigned, then assigned to the other). That last group is the one thing to hold back: write the date, flag it, but ask Rachael before changing Client Type.

Save today's four list files; tomorrow's run diffs against them. No automation creates case tasks for new Application records ("Case Tasks - New Application" is undeployed); say so when families are created. Binti is read only. Never delete Airtable records.

## Step 8: Add an Automation Log row

Every run, including one that changed nothing, ends with one row in the GoL Base Automation Log table `tblprCx6rMOrVNhrf` (Rachael's rule, 2026-11-12). Fill: Automation `fldAzRb77rplNPN3G` "Binti Sync - Received and Approval Dates"; Status `fldsCGDfbvYjABDfH` Succeeded (Failed if a write errored, Skipped if no login was available); Trigger Source `fld7kBGU38JshEtTn` "Binti (manual run by Claude for Rachael)"; Trigger ID `fld79z7iaYG77JgwT` "Binti sync YYYY-MM-DD"; Summary `fldSsceMXWxLvwJVq` one line of counts; Records Changed `fldKsjhYflTPoXoMb` one line per record touched (record ID, household, RFA, fields changed); Outcome `fldCcStYHWTB6jg9x` a plain-English paragraph covering each login, counts checked, what was created, changed, or flagged, and anything left pending and why; Run Time `fldyuXhJGpLkZ6Twh` now; Details `fldh7enGFnpqoO8Np` a compact JSON of counts and Binti IDs. If a second login runs later the same day, or a pending family gets finished, add another row; never edit an earlier one.