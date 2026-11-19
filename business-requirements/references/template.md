# Vision and Scope Document Template

_This template is based on Chapter 5 from the book "Software Requirements, 3rd Edition" by Karl Wiegers and Joy Beatty, Chapter 5._

______________________________________________________________________

## 1. Business Requirements

_This section describes the primary business benefits the new system will provide to its sponsors, buyers, and users. It provides the "why" behind the project._

### 1.1 Background

**Explanation:** Summarize the rationale, history, and context for this project. What situation led to the decision to build this product or make changes to an existing one?

**Example:**

> Our current chemical tracking process is entirely manual, relying on paper forms and spreadsheets. This leads to ordering duplicate chemicals, increased waste from expired containers, and significant administrative overhead to comply with regulatory reporting. This project was initiated to automate and centralize the chemical tracking and ordering process.

### 1.2 Business Opportunity

**Explanation:** Describe the business problem being solved or the market opportunity being addressed. For internal systems, focus on the process being improved. For commercial products, describe the target market and competitive landscape.

**Example:**

> By creating a centralized Chemical Tracking System, we can reduce waste and purchasing costs by exploiting our existing chemical inventory. It will also streamline regulatory reporting, reducing the risk of non-compliance fines. This gives us a competitive advantage by lowering our operational costs and improving safety.

### 1.3 Business Objectives

**Explanation:** State the important business benefits the product will provide in a quantitative and measurable way. Use the SMART (Specific, Measurable, Achievable, Relevant, Time-bound) criteria.

**Example:**

> - **BO-1:** Reduce chemical purchasing costs by 25% within the first year of use.
> - **BO-2:** Reduce time spent by scientists on chemical ordering from an average of 45 minutes to less than 10 minutes per order within 6 months of deployment.
> - **BO-3:** Achieve 95% compliance with federal and state chemical reporting regulations within 3 months of deployment.

### 1.4 Success Metrics

**Explanation:** Specify the key performance indicators (KPIs) that will be used to measure the success of the project. These should be directly trackable and indicate if you are on the path to achieving the business objectives.

**Example:**

> - **SM-1:** Track 60% of commercial chemical containers and 50% of proprietary chemicals within 4 weeks of system launch.
> - **SM-2:** 80% of chemical orders are processed through the new system within 2 months of launch.
> - **SM-3:** Achieve a user satisfaction rating of at least 75% on a post-deployment survey.

### 1.5 Vision Statement

**Explanation:** A concise statement that summarizes the long-term purpose and intent of the product. Use the following template:

- **For:** [target customer]
- **Who:** [statement of the need or opportunity]
- **The:** [product name]
- **Is a:** [product category]
- **That:** [key benefit, compelling reason to use]
- **Unlike:** [primary competitive alternative or current process]
- **Our product:** [statement of primary differentiation]

**Example:**

> **For** scientists who need to request containers of chemicals, **who** spend significant time on manual ordering and tracking, **the** Chemical Tracking System **is an** information system **that** will provide a single point of access to the chemical stockroom and vendors. **Unlike** the current manual ordering processes, **our product** will generate all reports required for regulatory compliance and will reduce costs by enabling the sharing of existing chemical stock.

### 1.6 Business Risks

**Explanation:** Summarize the major business risks associated with developing (or not developing) this product. This includes market competition, user acceptance, timing issues, etc. (This is different from project risks like budget or schedule overruns).

**Example:**

> - **RI-1:** Low user adoption by scientists accustomed to the old process could prevent the realization of cost-saving objectives.
> - **RI-2:** Delays in deployment could result in fines for non-compliance with new regulations taking effect next year.

### 1.7 Business Assumptions and Dependencies

**Explanation:** List any assumptions that were made when conceiving the project. Also, list any major dependencies the project has on external factors, such as other projects, third-party vendors, or regulations.

**Example:**

> - **AS-1:** Assumes all chemical vendors can provide electronic invoices compatible with our purchasing system.
> - **DE-1:** Dependent on the successful upgrade of the corporate network infrastructure, scheduled for Q3.

______________________________________________________________________

## 2. Scope and Limitations

_This section defines the boundary of the project. It describes what the product is and is not._

### 2.1 Major Features

**Explanation:** List the major features or user capabilities of the product. This can be a simple bulleted list or a more detailed feature tree. Give each feature a unique identifier.

**Example:**

> - **FE-1:** Order Chemicals
>   - **FE-1.1:** Search for chemicals
>   - **FE-1.2:** Request a chemical container
> - **FE-2:** Inventory Management
>   - **FE-2.1:** Track container location
>   - **FE-2.2:** Update chemical quantity
> - **FE-3:** Regulatory Reporting

### 2.2 Scope of Initial Release

**Explanation:** Summarize the capabilities planned for the first release. This focuses the development effort on the most critical functionality needed to deliver immediate value.

**Example:**

> Release 1.0 will include the core functionality for ordering chemicals (FE-1) and basic inventory management (FE-2.1). The regulatory reporting features (FE-3) will be deferred to a subsequent release. The focus of the initial release is on reliability and data integrity, not on performance or advanced usability features.

### 2.3 Scope of Subsequent Releases

**Explanation:** If you envision a staged evolution, describe the major features or capabilities planned for future releases. This can be a high-level roadmap.

**Example:**

> - **Release 2.0:** Will introduce automated regulatory reporting (FE-3) and advanced search capabilities.
> - **Release 3.0:** Will include a mobile interface for inventory updates and integration with the purchasing system.

### 2.4 Limitations and Exclusions

**Explanation:** Explicitly state any capabilities that stakeholders might expect but that are NOT being built. This helps manage expectations.

**Example:**

> - The system will not provide an interface for direct purchasing from vendors.
> - Mobile platform support will not be included in the initial release.
> - The system will not manage the budget for the chemical purchasing cost center.

______________________________________________________________________

## 3. Business Context

_This section describes the project's stakeholders and the priorities that will guide project decisions._

### 3.1 Stakeholder Profiles

**Explanation:** Describe the key stakeholders involved in the project, including their values, interests, and constraints. Focus on different user classes and their needs.

**Example:**

> - **Scientist:** Values fast, easy access to chemicals to maximize time spent on research. Interested in features for searching and ordering.
> - **Health & Safety Manager:** Values compliance with regulations and accurate reporting. Interested in features for tracking and reporting hazardous materials.
> - **Purchasing Agent:** Values cost savings and efficient vendor management. Interested in data on chemical usage to negotiate bulk discounts.

### 3.2 Project Priorities

**Explanation:** Define the relative importance of the five project dimensions: Features, Quality, Schedule, Cost, and Staff. For each, identify it as a **Constraint**, a **Driver**, or a **Degree of Freedom**. This helps guide trade-off decisions.

**Example:**

> - **Schedule:** Constraint (must be deployed by Dec 31st to meet regulatory deadline)
> - **Quality:** Driver (data integrity is critical for compliance)
> - **Features:** Degree of Freedom (we can defer less critical features to meet the schedule)
> - **Cost:** Constraint (fixed budget)
> - **Staff:** Degree of Freedom (we can add contractors if needed, within budget)

### 3.3 Deployment Considerations

**Explanation:** Summarize any information or activities needed for a successful deployment. This includes user training, data migration, infrastructure changes, and business process modifications.

**Example:**

> - All existing chemical inventory data must be migrated from spreadsheets into the new system before launch.
> - All lab personnel must complete a 2-hour training session before being granted access.
> - The new system requires a dedicated server and must be accessible from all lab locations.

______________________________________________________________________
