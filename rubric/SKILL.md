---
name: rubric
version: 1.0.1
description: Build a plan or specification, create a task-specific grading rubric, grade the first draft honestly, and revise it before presenting the final result. Use when the user invokes `$rubric`, asks for the rubric workflow, requests an ultrathought self-correction loop, or wants a project-tracking table evaluated and improved.
---

# Rubric

## Purpose in plain English

This skill helps you define what a good result must satisfy, assess a draft against those requirements, and improve it.

## How to explain the result

For a client-facing explanation, use ordinary words and the requested format. Explain unfamiliar abbreviations. Name what each number counts and explain its practical meaning. Keep internal identifiers out of the explanation. Keep necessary technical details in the working steps and technical references.

## Following the process

Use the process below. Preserve its conditions, commands, checks, and approval rules. Use information the user already supplied. Follow the existing questions or stopping rules when required information is missing.


Use the full self-correction loop:

1. Pre-research: read the relevant codebase and source material, and look up the topic when needed. Do not guess.
2. Produce a plan or specification.
3. Build a grading rubric for the plan. Use specific criteria for what makes it good or bad, with as many criteria as the problem warrants and no filler.
4. Grade the plan honestly and identify its weaknesses.
5. Revise the plan based on the grading.
6. Show the rubric, original grade, changes made, and final plan.

Do not skip the rubric or the self-critique.

## Project-tracking tables

When the artifact is a Deliverables, Pain Points, Decisions Log, Outcomes, or Tasks table, incorporate the following domain-specific rules into the rubric in addition to general criteria such as completeness, granularity, and maintainability.

### Scope deliverables correctly

- Treat a deliverable as a client-facing pain-point fix, including an interface, automation, schema change, integration, form, PDF template, or data migration that closes a documented pain point.
- Exclude vision, PRD, discovery documents, demo scripts, walkthrough videos, build plans, migration field references, and internal dry-run test scripts. These explain how work was done rather than what the client received.
- Count schema or library tables when they enable a pain-point fix. Treat meta-tracking tables as deliverables.

### Count and deduplicate

- Count each artifact once regardless of file format. Treat multiple formats of the same content as one row.
- Detect overlapping interfaces that may represent the same workflow viewed differently. Merge them or cross-reference the overlap in Notes.
- Detect the same workflow represented at multiple layers, such as a form, PDF template, and integration. Either combine them into one pipeline row or keep them separate and document the bundle.

### Require operational fields

- `Go-Live Critical` (checkbox): supports must-ship-by-cutover filtering.
- `Needs Revision` (checkbox): distinguishes built-but-flagged work from In Build or Planned work.
- `Status` (single select): Shipped, In Build, Planned, or Deferred.
- `Type` and `Theme` (single select): support grouping and filtering.
- `Audience`: name a human rather than using All or Team.
- `Location`: provide an openable table ID, file path, repository URL, or interface name.
- `Pain Points Addressed` and `Decisions`: use text references at minimum and linked records when the project already links related tracking tables.

### Verify status accuracy

- Distinguish as-documented from as-built status. When a status comes from project documentation rather than the live system, label it as documented and flag rows that require verification in Notes.
- Identify discrepancies between source documents, record both claims, and mark the result uncertain.

### Apply consistent granularity

Choose one principle and apply it uniformly: one row per logical workflow or one row per atomic artifact. Do not combine a large suite into one row while splitting a comparable workflow into many rows without a documented reason.

### Prefer linked relationships when established

- When the project already uses linked records between tracking tables, link the new tracking table as well.
- Interpret a `no-cross-table-links` rule as prohibiting gratuitous links, not established project-tracking relationships.
- Use an approximate rubric-grade ceiling of 75% when a tracking table lacks linked records and 85% when it includes them.
- Ask for explicit approval before adding linked fields when authority or intent is uncertain.

### Require useful views

Configure or specify at least:

- Go-Live Critical Remaining: Status is not Shipped and Critical is true.
- Shipped by Theme: grouped and filtered appropriately.
- Needs Revision: filtered to flagged records.

If the available Airtable tooling cannot create views, identify view creation as a user-interface follow-up.
