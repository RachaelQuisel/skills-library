# Data handling

ADHD Task Helper contains instructions, reference text, plugin metadata, and an icon. It has no publisher-operated server, account system, telemetry, or storage endpoint. The package itself does not send conversation content to the publisher.

## What a workflow uses

The assistant uses your request, relevant conversation context available in the host, and notes, documents, or checkpoints you supply. These can contain personal information or work details. A diagnosis or medical history is not required.

The package includes no executable scripts, hooks, MCP servers, credential settings, or instructions to read credential stores or environment variables.

## Host processing and tool use

ChatGPT, Codex, or another compatible host processes the content under its own account settings and policies. This plugin does not create a separate retention policy for the host.

The skills can ask the assistant to complete useful authorized work. Depending on the task and the host's tools, this can involve reading a file, requesting a website, or using a connected service. A website receives the requested URL and normal request metadata. A connected service receives the inputs supplied to its tool. A requested save writes content to the supported destination you choose.

The instructions do not authorize sending messages, creating external task records, scheduling events, or other actions merely because those items appear in supplied notes. Quoted source instructions are not action permission. These are instructions; the host's enabled tools and permissions determine what actions are technically possible.

## Outputs and continuity

Outputs normally appear in the current conversation. A checkpoint can be provided in chat or saved to a supported destination when requested. The plugin does not automatically store a separate task list, transfer preferences between chats, create reminders, or monitor future events. Such actions require an available mechanism and evidence of completion.

Questions: [person4@example.com](mailto:person4@example.com).
