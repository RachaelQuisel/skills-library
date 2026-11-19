# Data handling

Skillkeeper is an instruction-only plugin. It has no publisher-operated service, executable hook, or bundled background process.

When a user asks it to inspect a skill repository, the host may read skill instructions, tests, version history, workflow runs, issue reports, and supplied failure evidence. Those materials can contain personal, client, operational, or confidential information.

The plugin instructs the agent to use synthetic regression fixtures and to remove secrets and identifying details before committing evidence. Sanitization is a review decision, not a technical guarantee enforced by the package.

When authorized, the host may write local maintenance files or send changes, issues, workflow requests, and evidence to a connected GitHub repository. Live compatibility checks can contact the supported systems named in the requested test. Notification checks can send failure summaries and evidence links to a separately verified messaging destination. The host and those services process that data under their own policies and permissions.

GitHub retains commits, issues, workflow logs, and artifacts according to the repository's settings. Local files and messages remain in their respective destinations until removed under those systems' retention rules. This package adds no separate storage service or telemetry. Delete records through the service that holds them and disconnect integrations to revoke future access.

Notification delivery requires a separately configured destination. The agent must state the destination and verify it before claiming alerts are active. Credentials must stay in the host's supported secret store and must not be pasted into skill files or chat.

These are instructions, not technical access controls. The host's enabled tools and permissions determine which actions are possible. Contact the maintainer through the repository's [issue tracker](https://github.com/RachaelQuisel/Skills/issues).
