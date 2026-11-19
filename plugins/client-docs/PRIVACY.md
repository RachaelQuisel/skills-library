# Data handling

This instruction-only plugin uses the conversation and the client material the user supplies or that host tools read with the user's permission: discovery transcripts, client documents, and files in the client's GitHub repo.

Drafts are written to the user's local client folder. The push skill writes to the client's GitHub repo only after the user says "push it" in the session. The workflow diagram skill publishes a web page that stays private until the user shares it.

The publisher operates no backend for this plugin. The package includes no telemetry, hooks, credential storage, or scheduled jobs. Do not put credentials, tokens, or unrelated personal data in client documents.
