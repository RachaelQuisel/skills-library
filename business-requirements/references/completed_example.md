# Vision and Scope: Example Client Grant Distribution System (GrantPoint)

---

## 1. Business Requirements

### 1.1 Background
Example Client allocates approximately $1 million annually in grants to roughly 125 community partners, non-profits, and school districts. The current process is highly manual, involving downloadable PDFs, email/physical mail submissions, and dual entry into Excel and FileMaker. This creates a severe administrative bottleneck in April, as Sharon (Office Manager) must compile data for board approval within a two-week window. The lack of structured data also makes post-grant reporting and impact storytelling difficult.

### 1.2 Business Opportunity
By implementing "GrantPoint," a digital grant management portal, Example Client can eliminate paper-based workflows and manual data entry. This system will centralize applications, automate internal scoring rubrics, and provide real-time status updates to applicants. It also provides a structured repository for "impact stories" (photos, testimonials) that can be leveraged for marketing and future fundraising, while ensuring financial reconciliation with QuickBooks remains seamless.

### 1.3 Business Objectives
- **BO-1:** Reduce the time required to compile the annual board report from 2 weeks to 2 days within the first grant cycle.
- **BO-2:** Achieve a 100% digital submission rate for both initial applications and final impact reports in the first year.
- **BO-3:** Standardize grant evaluation through a multi-user internal rubric, reducing subjective bias in funding recommendations.
- **BO-4:** Eliminate the $150k+ annual "unclaimed" grant liability by automating 30/60/90-day reminders for final reports and site visits.

### 1.4 Success Metrics
- **SM-1:** 95% of applicants report the system is "easy" or "very easy" to use during the pilot phase.
- **SM-2:** 100% of awarded grants are assigned a unique, trackable grant number automatically upon submission.
- **SM-3:** zero physical grant applications accepted after the Phase 1 launch.

### 1.5 Vision Statement
**For** Example Client administrators and community grant applicants, **who** are burdened by manual, paper-intensive funding processes, **the** GrantPoint System **is a** digital grant management platform **that** automates the entire lifecycle from application to impact reporting. **Unlike** the current mix of PDFs and filing cabinets, **our product** provides real-time transparency, objective scoring tools, and automated compliance tracking to maximize community impact.

![GrantPoint Context Diagram](../diagrams/context.png)

### 1.6 Business Risks
- **RI-1:** Accessibility Compliance: Failure to meet WCAG standards could prevent some school district employees from successfully applying.
- **RI-2:** Data Migration: Mapping historical FileMaker data to the new schema may reveal inconsistencies that delay the "year-over-year" comparison features.
- **RI-3:** User Error: Applicants may struggle with digital document uploads (e.g., 990s or financial audits) if the instructions are not explicit.

### 1.7 Business Assumptions and Dependencies
- **AS-1:** Applicants have access to basic digital tools (browser, PDF scanner).
- **DE-1:** The system depends on Airtable for data storage and Softr for the front-end user interface.
- **DE-2:** Site visit scheduling depends on internal Example Client staff availability and manual coordination in Phase 1.

![GrantPoint Ecosystem Map](../diagrams/ecosystem.png)

---

## 2. Scope and Limitations

### 2.1 Major Features

![GrantPoint Feature Tree](../diagrams/feature-tree.png)

- **FE-1: Applicant Portal (Softr)**
    - Secure sign-up/login with email verification.
    - Conditional application forms (Non-Profit vs. School District requirements).
    - Real-time application status tracking (e.g., "In Review," "Awarded," "Reporting Pending").
- **FE-2: Internal Grant Management (Airtable)**
    - Centralized dashboard for Sharon to review submissions and manage documents.
    - Automated grant numbering and fiscal year tagging.
    - Financial tracking (50% initial payment vs. 50% final payment reconciliation).
- **FE-3: Evaluation Rubric**
    - Internal voting/scoring system for board members and executives.
    - Automated averaging of scores to rank funding priorities.
- **FE-4: Compliance & Reporting**
    - Automated email triggers for final report deadlines (12-18 month window).
    - Digital site visit log for capturing notes, photos, and outcome data.

### 2.2 Scope of Initial Release (The "Skateboard")
- Basic Softr portal for new applications.
- Airtable backend for document storage and status management.
- Manual email notifications for award letters.
- Basic "How did you hear about us?" data capture.

![GrantPoint Event List](../diagrams/event-list.png)

### 2.3 Scope of Subsequent Releases
- **Phase 2:** Automated PDF generation of submitted applications.
- **Phase 3:** Integration with QuickBooks Online for payment tracking.
- **Phase 4:** Social media "Story Queue" for automated marketing of grant outcomes.

### 2.4 Limitations and Exclusions
- The system will NOT process external grant applications *from* Example Client to other foundations (grant seeking).
- Direct ACH/Wire transfers will not be initiated from the portal (remains in banking/QuickBooks).

---

## 3. Business Context

### 3.1 Stakeholder Profiles
- **Sharon (Office Manager):** Values data integrity and report speed. Primary user of the administrative backend.
- **Grant Applicants:** Value clarity, ease of submission, and status transparency.
- **Example Client Board Members:** Value high-level summaries, outcome data, and community impact stories.
- **Noel Harper (Executive Director):** Values organizational visibility and branding.

### 3.2 Project Priorities
- **Quality:** **Constraint.** The system must accurately track financial liabilities and meet legal reporting standards.
- **Features:** **Driver.** Digital transformation of the PDF process is the primary goal.
- **Schedule:** **Driver.** Target launch is mid-February to align with the January-March application window.
- **Cost:** **Constraint.** Part of the established monthly retainer.

### 3.3 Deployment Considerations
- **User Training:** Simple training for Sharon on managing the Airtable backend.
- **Public Launch:** Website updates needed to redirect from PDF downloads to the GrantPoint URL.
- **WCAG Compliance:** Ensure color contrast and alt-text meet accessibility standards before final launch.
