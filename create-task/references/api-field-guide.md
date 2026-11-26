# Task Creation API — Field Guide

## Endpoint
`POST https://tasks.xray.tech/api/tasks`

## Authentication
```bash
API_KEY=$(cat ~/.config/xray/tasks-api-key)
# Pass as header: -H "X-Api-Key: $API_KEY"
```

## Create Fields

| Field | Type | Required | Valid Values | Gotchas |
|-------|------|----------|-------------|---------|
| title | string | yes | Max 120 chars | Short and actionable |
| assignedTo | string | no | Email (e.g. `person2@example.com`) | Defaults to API key owner |
| origin | enum | no | `"Human"`, `"AI Agent"`, `"Automation"` | Default: `"Human"` |
| originDetail | string | no | Free text | Use `"Claude Code"` when Claude creates |
| description | string | no | Max 500 chars | **Keep under ~200 chars or risk 502** |
| priority | enum | no | `"Medium"`, `"High"` | `"Normal"` and `"Urgent"` return 502. Use `"Medium"` for normal priority. |
| requestedBy | string | no | Email address | Defaults to API key owner |
| project | string | no | Airtable record ID (`recXXX`) | **NOT** `"projectId"` |

## Critical Gotchas

### Priority: Write vs Read values differ
- **Read** (GET responses): `"P0: Urgent & Critical"`, `"P1: Top Priority"`, `"P2: High"`, `"P2: Medium Priority"`, `"P3: Normal"`
- **Write** (POST/PATCH): `"Medium"`, `"High"` — these are the only two values confirmed to work
- `"Normal"` and `"Urgent"` both return 502 `"Failed to create task in Airtable"` (tested 2026-04-14)
- `"P2: Medium Priority"` also works on write (read-format exception)
- Using other values → `"Failed to create task in Airtable"`

### Project: Create vs Accept use different field names
- **Create** (`POST /api/tasks`): field is `"project"` → `"project": "recXXX"`
- **Accept** (`POST /api/tasks/:id/accept`): field is `"projectId"` → `"projectId": "recXXX"`
- Using `"projectId"` on create → silently ignored, task created without project link

### Description: Long values cause 502
- Airtable backend times out on long strings
- Keep under ~200 chars on create
- Add longer descriptions after creation via `PATCH /api/tasks/:id`

## Known Project IDs

| Project | ID |
|---------|----|
| Example Nonprofit | `recExample0000021` |

Search for others: `GET /api/projects?q=search_term`

## Post-Creation Endpoints

| Action | Method | Path | Body |
|--------|--------|------|------|
| Accept | POST | `/api/tasks/:id/accept` | `{ "projectId": "recXXX" }` |
| Reject | POST | `/api/tasks/:id/reject` | `{ "reason": "..." }` |
| Need info | POST | `/api/tasks/:id/needs-info` | `{ "note": "..." }` |
| Update fields | PATCH | `/api/tasks/:id` | Any updatable field |

### Updatable fields (PATCH)
`title`, `description`, `priority`, `dueDate`, `startDate`, `status`, `triageStatus`, `triageNotes`, `originDetail`, `hoursEstimated`, `assignedTo`, `project`

## Error Reference

| Status | Meaning | Common Cause |
|--------|---------|-------------|
| 400 | Validation failed | Missing title, invalid priority value |
| 401 | Not authenticated | Bad or revoked API key |
| 502 | Airtable backend error | Description too long, burst requests, Airtable outage |

## Response Shape

Success: `201 Created`
```json
{ "ok": true, "task": { "id": "recXXX", "title": "...", "linkToTaskInterface": "https://..." } }
```
