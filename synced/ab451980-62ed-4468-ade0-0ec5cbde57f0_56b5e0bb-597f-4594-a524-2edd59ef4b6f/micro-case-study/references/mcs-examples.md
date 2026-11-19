# Completed MCS Examples

## Coding Clarified (Education / Workforce Development)

### MCS 1: Self-Service Caseworker Portal

| Field | Value |
|---|---|
| Client Name | Janine Mothershed |
| Client Role | CEO |
| Company Name | Coding Clarified |
| Industry | Education, Workforce Development, Nonprofit |
| MCS Headline | Hundreds of caseworkers are emailing staff for status updates because they can't access student data themselves. |
| Situation | Hundreds of caseworkers checking on student progress, but data trapped in DocuSign PDFs. Staff spent 20+ hrs/week (80+ hrs/month on caseworker emails alone) responding to status inquiries. |
| Approach | Built self-service caseworker portal with personalized tracker URLs, linked directly to student records in Airtable. |
| Analysis | Caseworkers accessed docs, status, and transcripts without emailing staff at 95%+ reliability. Portal adopted without training. |
| Value | ~20 hrs/week recovered (~$36,400/yr at $35/hr). Staff time redirected from responding to caseworker emails toward direct student support. |
| Data Confidence | High |
| Primary Tag | Self-Service Enablement |
| Secondary Tag | Time Recovery |

### MCS 2: Replace DocuSign with Structured Data Capture

| Field | Value |
|---|---|
| Client Name | Janine Mothershed |
| Client Role | CEO |
| Company Name | Coding Clarified |
| Industry | Education, Workforce Development, Nonprofit, Government Compliance |
| MCS Headline | All student data is trapped in PDFs that can't be searched or linked to student records. |
| Situation | All student data trapped in DocuSign PDFs, not parseable, not linked to student records, not accessible without manual requests. State audit data (employment, accommodations) scattered across emails. |
| Approach | Replaced DocuSign with Fillout + Airtable system. 12 database tables, 3 tracker forms, 5 state-specific enrollments. |
| Analysis | Every field became queryable and every document linked to the correct student record at 95%+ accuracy. State audit compliance achieved on first use. |
| Value | ~90% reduction in manual data entry. Student data now audit-ready, giving leadership confidence ahead of state reviews. |
| Data Confidence | High |
| Primary Tag | Vendor Replacement |
| Secondary Tag | Compliance / Risk Mitigation |

### MCS 3: CPC Certification Tracking

| Field | Value |
|---|---|
| Client Name | Janine Mothershed |
| Client Role | CEO |
| Company Name | Coding Clarified |
| Industry | Education, Workforce Development, Nonprofit, Government Compliance |
| MCS Headline | The certification rate that determines state funding isn't trackable or auditable. |
| Situation | CPC certification rate, the critical metric for continued state funding, was not trackable. No auditable record of student certification progress. |
| Approach | Built self-reporting workflow where students report registration dates and upload score reports, creating structured records in Airtable. |
| Analysis | Key funding metric became measurable and auditable for the first time. Workflow captured 95%+ of student submissions without staff involvement. |
| Value | Protects continued state funding by making the critical certification metric trackable. Leadership gained visibility into certification progress across all cohorts. |
| Data Confidence | Medium |
| Primary Tag | Process Definition |
| Secondary Tag | Compliance / Risk Mitigation |

### MCS 4: Dynamic Exam Delivery

| Field | Value |
|---|---|
| Client Name | Janine Mothershed |
| Client Role | CEO |
| Company Name | Coding Clarified |
| Industry | Education, Workforce Development, Nonprofit |
| MCS Headline | Staff have to manually track which student gets which exam and when to send it. |
| Situation | Midterm Quiz (Ch 10) and Practice Exam (Ch 20) delivery was manual; staff had to track progress and send exams at the right time. |
| Approach | Built automation that reveals exams automatically based on student progress (Blackboard chapter linking + grade sync). |
| Analysis | Exams delivered at 95%+ accuracy without staff intervention. Correct exam surfaced to the correct student at the correct milestone. |
| Value | Part of ~131 hrs/month in total recovered time across all automations. Staff time redirected from exam logistics to student coaching. |
| Data Confidence | Medium |
| Primary Tag | Process Automation |
| Secondary Tag | Time Recovery |

## Maas Verde (Landscape Construction / Restoration)

### MCS-2026-001: LMN Labor Schedule Scraper

| Field | Value |
|---|---|
| Client Name | Kris Wade |
| Client Role | CFO |
| Company Name | Maas Verde |
| Industry | Landscape, Construction, Restoration |
| MCS Headline | Future crew scheduling data exists but can't be exported or reported on. |
| Situation | Future crew scheduling data existed in LMN's Whiteboard view but couldn't be exported. No future capacity reports, no API. Admin staff spent 40 min to 3 hrs/day manually copying names and hours from the screen into spreadsheets. |
| Approach | Built a JavaScript bookmarklet that runs inside the browser on LMN's Whiteboard page. One click scrapes the DOM for date, crew, job name, address, duration, and labor hours, then copies structured tab-separated data to clipboard for direct paste into Excel or Google Sheets. |
| Analysis | Tool ran in 2 to 10 min/day vs. 40 min to 3 hrs manual, at 95%+ data accuracy. Adopted by the project coordinator for daily use. |
| Value | ~8 hrs/week recovered (~$16,640/yr at $40/hr). Team gained the ability to see committed vs. available labor hours on any future date for the first time. |
| Data Confidence | Medium |
| Primary Tag | Data Entry Automation |
| Secondary Tag | Visibility |

### MCS-2026-002: LMN PDF Estimate Parser

| Field | Value |
|---|---|
| Client Name | Kris Wade |
| Client Role | CFO |
| Company Name | Maas Verde |
| Industry | Landscape, Construction, Restoration |
| MCS Headline | Each estimate requires hours of manual re-entry from PDF to project management system. |
| Situation | Sales team needed estimate data from LMN PDFs structured into Monday.com's hierarchy (boards, groups, items, subitems). Each estimate required 2 to 6 hours of manual re-entry, and up to 4 team members were doing this regularly. |
| Approach | Built a Python script using pdfplumber and regex, hosted on PythonAnywhere as a desktop app. User drops a PDF into a folder, gets a success message, and two CSVs (items + subitems) appear on their desktop ready for Monday.com import. |
| Analysis | Parser handled 95%+ of PDF edge cases accurately, including descriptions spanning two lines. When a parsing bug surfaced months later, the client's employee reported it directly, a sign of genuine adoption. |
| Value | ~$4K to $50K/yr in recovered estimate entry time at $40/hr (2 to 6 hrs/wk/user, 1 to 4 users). CFO described the impact as "rocket ships blasting off" for the sales team. |
| Data Confidence | Medium |
| Primary Tag | Data Entry Automation |
| Secondary Tag | Time Recovery |
