---
name: business-requirements
version: 1.0.1
description: Assist in eliciting, defining, and capturing business requirements for software projects. Use when starting a new project, defining product vision, establishing project scope, or creating a Vision and Scope document based on the Wiegers/Beatty "Software Requirements" framework.
tags:
  - skill
---

# Business Requirements

## Purpose in plain English

This skill helps you explain a project's purpose, the people it serves, and the work it should include.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Establish the "why" and the "value" of a project before functional requirements are drafted. This skill uses the framework from Karl Wiegers and Joy Beatty's *Software Requirements, 3rd Edition*.

## Your Goal

Collaboratively define the foundational business requirements:
- **Business Opportunity**: The problem or opportunity being addressed.
- **Business Objectives**: Measurable, SMART goals for the project.
- **Success Metrics**: KPIs to track if objectives are being met.
- **Vision Statement**: A concise "elevator pitch" for the product.
- **Project Scope**: Delineation of what is in and out for the current release.

## Prerequisites

This skill requires:
1.  **Python 3** and libraries (we **strongly recommend** using a virtual environment).

### Recommended Setup

```bash
# 1. Setup Python Environment
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux

# 2. Install dependencies
pip install -r business-requirements/scripts/requirements.txt
```

## How to Get There

**1. Elicit Core Components**
Start by asking the user about their business problem and high-level goals. Use [references/elicitation-questions.md](references/elicitation-questions.md) for targeted questions to help stakeholders articulate their vision.

**2. Push for Measurability**
Avoid vague objectives. Guide the user to turn "improve efficiency" into "reduce order time by 30%". See [references/concepts.md](references/concepts.md) for core definitions and examples of SMART objectives.

**3. Define the Vision and Scope**
Draft a Vision and Scope document using the [references/template.md](references/template.md). This includes:
- **Vision Statement**: Use the "For/Who/The/Is/That/Unlike/Our product" template in Section 1.5 of the template.
- **Project Priorities**: Classify Features, Quality, Schedule, Cost, and Staff as a **Constraint**, **Driver**, or **Degree of Freedom**.

**4. Represent Scope Visually**
Suggest appropriate techniques based on the project's complexity. Refer to [references/scope-techniques.md](references/scope-techniques.md) for details on:
- **Context Diagram**: For system boundaries and external entities.
- **Ecosystem Map**: For interactions with other systems.
- **Feature Tree**: For hierarchical organization of capabilities.
- **Event List**: For naming external triggers.

**5. Iterate and Refine**
Do not treat the first draft as final. Proactively improve the requirements by engaging the user in refinement:
- **Critique the Draft**: Highlight sections with "low confidence" or those needing stakeholder validation. Call out vague terms like "seamless," "easy," or "efficient" and propose measurable alternatives.
- **Targeted Elicitation**: Propose 2-3 specific questions from [references/elicitation-questions.md](references/elicitation-questions.md) to fill identified gaps.
- **Measurement Sharpening**: For every Business Objective, ask: "How will we measure this?" and suggest specific data points or KPIs that could serve as Success Metrics.

**6. Standardize and Validate**
Before delivering final documentation or converting it to a branded format, ensure the Markdown is standardized and error-free:
- **Format & Lint**: Run the standardizing script on your generated markdown to ensure it adheres to professional standards and will convert smoothly to HTML:
  `source .venv/bin/activate && python3 business-requirements/scripts/format_md.py <path-to-markdown-file>`
- **Address Warnings**: Correct any linting issues reported by the script (e.g., missing blank lines around headings, duplicate headings) to guarantee a high-quality final product.

## Behavior Rules

- **Context First**: Always check if the current request is "in scope" based on the established business objectives.
- **No Vagueness**: Challenge any objective that isn't SMART (Specific, Measurable, Achievable, Relevant, Time-bound).
- **Conflict Awareness**: Be alert for conflicting business requirements among different stakeholders.
- **Agile Alignment**: In agile contexts, use business objectives to prioritize the product backlog and define iteration scope.
