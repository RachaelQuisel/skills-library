# Nova Tips & Reference

Reference for Nova's capabilities, canvas commands, pro tips, and troubleshooting. Read this when the user needs help interacting with Nova directly or when building prompts that use specific canvas commands.

## Input Methods

- **Text Prompt** — Describe what to build. Reference field names directly for precision.
- **Image Upload** — Upload a screenshot, whiteboard sketch, or flowchart. Nova interprets and maps it.
- **CSV Upload** — Upload structured data (steps, roles, tools) for bulk creation.

## Canvases & Commands

### Workflow Canvas (core)
| Action | Commands |
|--------|----------|
| Create | `create_process`, `create_sections`, `create_steps`, `create_connections`, `add_step_roles`, `add_step_tools` |
| Find | `find_steps`, `find_sections`, `get_section_steps`, `get_steps_by_tool` |
| Update | `update_steps`, `update_sections`, `update_connections` |
| Remove | `delete_step_roles`, `delete_step_tools` |

### Team Canvas
| Action | Commands |
|--------|----------|
| Create | `create_teams`, `create_roles` |
| Find | `find_teams`, `find_roles`, `get_team_roles` |
| Update | `update_teams`, `update_roles` |

### People Canvas
| Action | Commands |
|--------|----------|
| Create | `create_people`, `create_attributes` |
| Find | workspace search |

### Tool Canvas
| Action | Commands |
|--------|----------|
| Add | `workspace_add_tool`, `create_entities` |
| Find | `workspace_find_tools`, `catalogue_find_tools`, `get_steps_by_tool` |
| Remove | `delete_step_tools` |

**Relationship chain:** People -> Role -> Step (people link to roles, not directly to steps). Tools and roles are assigned to steps from their respective canvases.

## Pro Tips

**Scope first, build second** — Tell Nova: "Don't start building yet — ask me questions to help scope out what I want first."

**Specify section count** — Without an explicit count, Nova over-creates sections. Say: "This process should have exactly [N] sections: [list them]." This is one of the highest-impact things for clean output.

**Get approval before building** — Tell Nova: "Before you generate the diagram, analyze this and give me the steps you're going to build first, then I'll approve."

**Specify layout direction** — Nova doesn't assume a direction. Say: "Lay out this process horizontally, flowing left to right." (or "top to bottom" for vertical).

**Create steps first, connect last** — Create all steps, then add connections as a separate action. Reduces diagram errors.

**Fix stacked objects** — When Nova creates multiple objects at once, they stack. Fix with: "Arrange them in a 3x3 grid." (use any grid: 2x4, 4x2, 1x6, etc.)

**Reference existing objects by exact name** — Use exact names of existing roles/teams/tools so Nova links to them instead of creating duplicates.

**Build cross-canvas in one prompt** — Nova can create and link objects across canvases in a single prompt (e.g., create a step, assign a role, add a tool).

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Too many sections | Rebuild with explicit count: "exactly N sections" |
| Objects stacked on canvas | Use a grid prompt to rearrange |
| Duplicate roles/tools | Use exact names of existing objects |
| Wrong connections | Delete connections, then reconnect as a separate step |
| Layout direction is off | State horizontal or vertical explicitly |
| Missing step data | Define all fields: name, type, status, executor, tools, notes, section |
