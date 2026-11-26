# Field schemas (writable fields only)

Source base: `appExample0000004` ("Projects & Tasks at XRAY"). Read this when constructing record bodies for create or PATCH.

## Projects (`tblExample0000023`)

| Field | Type | Notes |
|---|---|---|
| `Project name` | singleLineText | Primary. Use format `[Client]: [Workstream]`. |
| `Project Description` | richText | 1-3 sentences. |
| `Status` | singleSelect | `Backlog`, `Active`, `On Hold`, `Done`, `Cancelled`. Use `Active` on creation. |
| `Priority` | singleSelect | `Low`, `Standard`, `High`. |
| `XRay's Client` | linked records | One client record ID. |
| `Project/Account Manager` | singleCollaborator | `{"id": "usrXXX"}`. Set to Rachael (`usrExample0000179`) by default. |
| `Project Type` | singleSelect | Use `Consulting Solution Sprints` for typical client work. |
| `Start date`, `End date` | date | Optional. ISO `YYYY-MM-DD`. |

### Minimum-viable project body

```python
body = {"fields": {
    "Project name": "Client X: Workstream Y",
    "Status": "Active",
    "Priority": "High",
    "XRay's Client": [client_id],
    "Project Description": "Brief.",
    "Project/Account Manager": {"id": "usrExample0000179"},
    "Project Type": "Consulting Solution Sprints",
}}
# Send as records[0] via mcp__airtable__create_records_for_table
# baseId=appExample0000004, tableId=tblExample0000023
```

## Objectives (`tblExample0000162`)

This table appears in client planning bases as `Outcomes`.

| Field | Type | Notes |
|---|---|---|
| `Title` | multilineText | Primary. The outcome statement. |
| `Description` | richText | Use the user story: "As [role], I want [capability] so that [outcome]." |
| `Status` | singleSelect | `Backlog`, `Blocked`, `Ready to Start`, `In Progress`, `In Testing`. Use `Backlog`. |
| `Priority` | singleSelect | `Low`, `Medium`, `High`, `On Fire`. |
| `Visibility` | singleSelect | `Internal (XRay) Only` or `Visible to public`. Default to internal. |
| `Projects` | linked records | One or more project record IDs. |
| `XRay's Clients` | linked records | One client record ID. |
| `Owner` | singleCollaborator | `{"id": "usrXXX"}`. Rachael: `usrExample0000179`. |
| `Parent Objective` | linked records | Self-link for hierarchy if needed. |

### Minimum-viable objective body

```python
body = {"fields": {
    "Title": "Outcome statement",
    "Description": "User story",
    "Status": "Backlog",
    "Priority": "High",
    "Projects": [project_id],
    "XRay's Clients": [client_id],
    "Visibility": "Internal (XRay) Only",
    "Owner": {"id": "usrExample0000179"},
}}
# Send as records[0] via mcp__airtable__create_records_for_table
# baseId=appExample0000004, tableId=tblExample0000162
```

## Tasks (`tblExample0000010`)

141 fields total; many are formulas/rollups and not writable. Use only the fields below.

| Field | Type | Notes |
|---|---|---|
| `Task` | singleLineText | Primary. Action-oriented title. |
| `Description` | richText | Optional. Keep under ~480 chars or the API 502s. |
| `Status` | singleSelect | `Backlog`, `Blocked`, `Ready to Start`, `In Progress`, `Done`. Use `Backlog`. |
| `Priority` | singleSelect | **Strict read-format**: `P0: Urgent & Critical`, `P1: Top Priority`, `P2: Medium Priority`, `P3: Low Priority`, `P4: Lowest Priority`. |
| `Triage Status` | singleSelect | `New`, `Accepted`, `Rejected`, `Needs More Info`. Set to `New` on creation. |
| `Origin` | singleSelect | Use `AI Agent` when Claude creates the task. |
| `Origin Detail` | singleLineText | Free text. Use `Claude Code — [Client] build batch [date]`. |
| `Type` | singleSelect | Use `Task` for build-doc tasks. |
| `Project` | linked records | **Singular field name**, but accepts an array of project record IDs. |
| `Outcomes` | linked records | One or more objective record IDs. |
| `Assigned To` | singleCollaborator | Defaults to API key owner. |

### Priority gotcha

Sending `"High"` to the Tasks `Priority` field returns 201 OK and stores the literal string `"High"` outside any valid select option. The task becomes invisible to `/tasks/mine` and any priority-aware filter. Always use the full read-format string.

Sending invented values like `"P2: High"` returns `502 Failed to update task in Airtable`.

### Minimum-viable task body

```python
body = {"fields": {
    "Task": "Action title",
    "Description": "Brief context",
    "Priority": "P1: Top Priority",
    "Status": "Backlog",
    "Triage Status": "New",
    "Project": [project_id],
    "Outcomes": [objective_id],
    "Origin": "AI Agent",
    "Origin Detail": "Claude Code — [Client] build batch [date]",
    "Type": "Task",
}}
# For a Task, the tasks.xray.tech route is preferred:
# POST https://tasks.xray.tech/api/tasks with X-Api-Key header,
# passing the "fields" object's keys as top-level body params (title, priority, project, etc.).
# See references/api-field-guide.md in the create-task skill for the exact translation.
# The MCP path (mcp__airtable__create_records_for_table with tableId=tblExample0000010)
# also works but bypasses tasks.xray.tech's server-side validation.
```

### Linking an existing task to an outcome

The tasks.xray.tech `PATCH /api/tasks/:id` accepts `project` and `priority` but does **not** accept `Outcomes`. So the write splits:

```
# 1. Project + priority via tasks.xray.tech
PATCH https://tasks.xray.tech/api/tasks/{task_id}
  header: X-Api-Key: <key>
  body: {"project": "<project_id>", "priority": "High"}

# 2. Outcomes link via MCP (only route that accepts it)
mcp__airtable__update_records_for_table
  baseId: appExample0000004
  tableId: tblExample0000010
  records: [{id: "<task_id>", fields: {Outcomes: ["<objective_id>"]}}]
```

## XRay's Clients (`tblExample0000012`)

Only the fields needed during set-up:

| Field | Type | Notes |
|---|---|---|
| `Name` | singleLineText | Primary. Match exactly when filtering. |
| `Status` | singleSelect | Use `Active`. |
| `Phase` | singleSelect | Use `Discovery` for new client builds. |
| `Client Description` | richText | Brief summary lifted from discovery findings. |

### Find-or-create pattern (MCP)

```
mcp__airtable__list_records_for_table
  baseId: appExample0000004
  tableId: tblExample0000012
  filters: {operator: "=", operands: ["Name", "Example Agency"]}
  fieldIds: ["Name", "Status", "Phase"]
```

If empty:

```
mcp__airtable__create_records_for_table
  baseId: appExample0000004
  tableId: tblExample0000012
  records: [{fields: {Name: "[Client]", Status: "Active", Phase: "Discovery"}}]
```

Or read via `GET https://tasks.xray.tech/api/clients` and match client-side by `Name`.

## Reading the source schema

```
mcp__airtable__get_table_schema
  baseId: appExample0000004
  tables: [{tableId: "tblExample0000023"}, {tableId: "tblExample0000162"}, {tableId: "tblExample0000010"}]
```

Cache this response. Field options can change; re-pull before setting up a new client to confirm the select-option strings haven't shifted. Do **not** try to read the schema via curl — the PAT that used to power that call has been deleted; MCP is the route.
