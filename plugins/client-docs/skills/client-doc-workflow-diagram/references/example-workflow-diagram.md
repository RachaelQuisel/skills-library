# Example: a finished workflow diagram

The client is made up (Riverside Literacy Project, repo `XRAY-INC/RIVERSIDE-LITERACY`, build `2026-09-build`). It matches the example docs in the other `client-doc-*` skills, so you can see how each canonical doc feeds the diagram.

Where each part came from:
- Lanes: the 5 in-scope items in `vision-and-scope.md`
- Who receives each deliverable: the personas in `user-stories.md`
- Branch rules: `decisions.md` (leave unmatched tutors unassigned; remind on Thursdays)
- Live versus planned: `changelog.md` (the district report is not shipped yet)
- Volumes: estimates from the discovery transcript, flagged in the gaps list

---

## Mermaid source (`workflow-diagram.mmd`)

```mermaid
%% Riverside Literacy Project, 2026-09-build
%% ---
flowchart LR
    subgraph L1["Session log"]
        A1[/Tutor logs a session on the phone form/] --> A2[(Save the session in Airtable)]
        A2 --> A3[Session counts toward this week's hours]
    end

    subgraph L2["Tutor site assignment"]
        B1((Tutor signs up)) --> B2{Site answer matches a partner school?}
        B2 -->|yes| B3[(Link the tutor to the school site)]
        B2 -->|no| B4[Add the tutor to the Needs a site list]
        B4 --> B5[Coordinator assigns the site by hand]
    end

    subgraph L3["Weekly hours reminder"]
        C1((Thursday 9 a.m.)) --> C2[(Read this week's sessions)]
        C2 --> C3{Tutor under 2 hours?}
        C3 -->|yes| C4>Email the tutor a reminder]
        C3 -->|no| C5[No email sent]
        C4 --> C6[(Stamp Reminder sent on)]
    end

    subgraph L4["Coordinator weekly check"]
        D1((Thursday morning)) --> D2[Coordinator opens the Weekly Tutor Hours board]
        D2 --> D3[Coordinator follows up with tutors who have no hours]
    end

    subgraph L5["Monthly district report"]
        E1((First of the month)) --> E2[(Total hours per site from Sessions)]
        E2 --> E3[\"Fill the district report hours table (planned)"\]
        E3 --> E4>"Send the report to the district (planned)"]
    end

    A3 -.-> C2
    A3 -.-> E2

%% atlas: A1 executor=human runs=300 minutes=1 note="Estimate: 50 tutors, about 6 sessions each per month"
%% atlas: A2 executor=system runs=300 minutes=0
%% atlas: A3 executor=system runs=300 minutes=0
%% atlas: B1 executor=human runs=15 minutes=5 note="Estimate from discovery: about 15 new tutors a month"
%% atlas: B2 executor=system runs=15 minutes=0
%% atlas: B3 executor=system runs=13 minutes=0
%% atlas: B4 executor=system runs=2 minutes=0
%% atlas: B5 executor=human runs=2 minutes=5
%% atlas: C1 executor=system runs=4 minutes=0
%% atlas: C2 executor=system runs=4 minutes=0
%% atlas: C3 executor=system runs=200 minutes=0
%% atlas: C4 executor=system runs=40 minutes=0 note="Estimate: about 10 reminders a week"
%% atlas: C5 executor=system runs=160 minutes=0
%% atlas: C6 executor=system runs=40 minutes=0
%% atlas: D1 executor=human runs=4 minutes=0
%% atlas: D2 executor=human runs=4 minutes=10
%% atlas: D3 executor=human runs=4 minutes=30
%% atlas: E1 executor=system runs=1 minutes=0
%% atlas: E2 executor=system runs=1 minutes=0
%% atlas: E3 executor=system runs=1 minutes=0 type=document
%% atlas: E4 executor=human runs=1 minutes=15

classDef trigger fill:#1566b9,stroke:#0f4185,color:#fffaf0
classDef system fill:#fffaf0,stroke:#0e1c2d,color:#0e1c2d
classDef human fill:#e1ded8,stroke:#686f76,color:#0e1c2d
classDef deliverable fill:#0e1c2d,stroke:#0e1c2d,color:#fffaf0
classDef planned fill:#fffaf0,stroke:#868b8e,color:#686f76,stroke-dasharray:4 3
class B1,C1,D1,E1 trigger
class A1,B5,D2 human
class A2,B2,B4,C2,C3,C5,E1,E2 system
class A3,B3,C4,C6,D3 deliverable
class E3,E4 planned
```

## Deliverables table

| Deliverable | Who receives it | How often | Produced by | Status |
|---|---|---|---|---|
| A saved session record | Program coordinator | About 300 a month | Fillout form into Airtable | Live |
| Tutor linked to their school | Program coordinator, site principal | About 15 a month | Airtable automation | Live |
| Reminder email | Volunteer tutors under 2 hours | About 40 a month | Airtable automation | Live |
| Weekly follow-up list | Program coordinator | Weekly | Weekly Tutor Hours board | Live |
| District hours report | The school district | Monthly | Airtable, then the coordinator sends it | Planned |

## Questions for Riverside Literacy Project

1. About how many tutoring sessions are logged in a typical month? The diagram uses 300 as an estimate.
2. About how many new tutors sign up each month? The diagram uses 15.
3. Who sends the district report once it's filled in: the coordinator, or should it go automatically?

---

What a weak diagram looks like, and why it fails:

```mermaid
flowchart TD
    A[Forms] --> B[Airtable] --> C[Automations] --> D[Reports]
```

The boxes are systems, not steps, so nobody can tell what happens or who receives anything. There are no decisions, no triggers, and no way to tell live work from planned work.
