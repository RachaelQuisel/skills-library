# Example: a finished `user-stories.md`

Use this as the bar for tone, detail, and format. The client is made up (Riverside Literacy Project, repo `XRAY-INC/RIVERSIDE-LITERACY`, build `2026-09-build`).

What to copy:
- Each persona is a role the client would recognize, with a one-sentence description of their situation.
- "What they do in the system" lists only actions inside the system, verb first.
- Every story has a real "so that" outcome. If the interview didn't give one, the line is a TODO, not a guess.
- "What they can't do" appears only when a persona has a real restriction.

---

```markdown
# User Stories: 2026-09-build

**Client:** Riverside Literacy Project
**Build:** 2026-09-build
**Last updated:** 2026-09-24

## Personas

### Program coordinator
Runs tutor scheduling and reporting for all 6 school sites; the only full-time staff member on the program.

**What they do in the system**
- Assigns new tutors to a school site
- Checks the weekly hours list every Thursday
- Sends the monthly hours report to the district

**Their story**
As the program coordinator, I want to see which tutors haven't logged hours this week so that I can follow up before the Friday report closes instead of chasing paper sheets at month end.

---

### Volunteer tutor
A community volunteer who tutors 2 to 4 students at one school, usually once or twice a week.

**What they do in the system**
- Logs each tutoring session on the session form
- Picks their students from their own school's list

**Their story**
As a volunteer tutor, I want to log a session from my phone in under a minute so that I don't have to stop at the front office to sign a sheet.

**What they can't do**
- See students at other school sites
- Edit a session after the coordinator has marked it reviewed

---

### Site principal
Approves the tutoring program at their school and reads a monthly summary.

**What they do in the system**
- Reads the monthly site summary in the Sites interface

**Their story**
As a site principal, I want to see how many tutoring hours my students received this month
> TODO: What does the principal do with this number? Ask the coordinator whether it goes into a district report, a staff meeting, or a renewal decision.
```
