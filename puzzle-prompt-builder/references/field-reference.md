# Puzzle Field Reference

Use these exact field names and valid values when building Nova prompts.

## Step Fields
| Field | Description | Valid Values |
|-------|-------------|-------------|
| name | Label on the canvas | Free text |
| type | Step type | task, conditional, signal, form |
| status | Current state | Draft, In Progress, Done, Blocked |
| executor | Role responsible | Must match a role name |
| tools | Software/systems used | Must match tool names |
| notes | Context or instructions | Free text |
| section | Which section it belongs to | Must match a section name |

## Role Fields
| Field | Description |
|-------|-------------|
| name | Role title (e.g., "Compliance Officer") |
| team | Which team this role belongs to |
| description | What this role is responsible for |

## Team Fields
| Field | Description |
|-------|-------------|
| name | Team name (e.g., "Operations", "Legal") |
| description | Function or department |
| roles | List of roles belonging to this team |

## Tool Fields
| Field | Description |
|-------|-------------|
| name | Tool/software name (e.g., "Salesforce", "Notion") |
| description | What the tool does in this context |
| steps | Which steps this tool is assigned to |

## Section Fields
| Field | Description |
|-------|-------------|
| name | Section label (e.g., "Intake", "Approval") |
| order | Position within the process |
| steps | Steps belonging to this section |

## People Fields
| Field | Description |
|-------|-------------|
| name | Full name |
| role | Their role |
| team | Their team |
| attributes | Custom key-value properties (location, seniority, etc.) |

## Entity Fields
| Field | Description |
|-------|-------------|
| name | Entity name (e.g., "Contract", "Invoice", "Client") |

## Attribute Fields
| Field | Description |
|-------|-------------|
| name | Attribute label (e.g., "Contract Value", "Due Date") |
| field_type | Multi-line text, Single-line text, Number, Date |
| options | For select/dropdown: list of choices |
| description | What this attribute captures |
| api_name | Programmatic identifier for integrations |
