# Data handling

Airtable Interface Builder is a package of instructions, reference text, images and one offline Python helper. It has no publisher-operated backend, account, telemetry endpoint or content store. The package does not send content to its publisher. Content you choose to include in a support issue is handled by GitHub.

## What it reads

The assistant may read the source, package files, SDK declarations, screenshots and feedback you provide. With connected tools, it may inspect Airtable schema, permission settings, interface pages and records relevant to your request. Those records can contain staff names, applicants, assignments, training, deadlines and document attachments. Browser inspection can expose visible account content.

The bundled `source_receipt.py` helper reads only the local files explicitly passed to `--source` and, optionally, `--readback`. It prints resolved file paths, byte counts, SHA-256 hashes and the comparison result. It does not print source contents. It makes no writes or network requests and does not read environment variables or credential stores.

## Who processes the data

Your AI host processes the content supplied to the assistant under that host's terms and settings. Enabled connectors and browser tools may send requests to Airtable, GitHub or another service used for your task. Browsing documentation sends the requested URL and normal request information to the website. Authorized record saves, source publication or native attachment uploads send the relevant content to the destination service under your connected account.

The plugin bundles no MCP servers, hooks, authentication configuration or automatic data-transfer service. Credentials used by existing connectors or browser sessions are handled by those tools, not by the offline helper.

## What it saves

The workflow may write revised source, fictional test fixtures and verification notes to the file locations you request. Authorized live work may save source or records in Airtable, upload files through native attachment controls or push files to your chosen GitHub repository. The skill instructs the assistant to keep real client screenshots, private identifiers, signed attachment URLs and credentials out of distributable packages and public Git history.

Files and records remain in their chosen destinations until managed there. The package has no independent retention system; the host and connected services determine their own retention. No claims are made about their deletion or storage settings.

## Permissions

The skill distinguishes source editing, installation, publication and live record actions. It instructs the assistant to stay within the authorized task and avoid unrelated writes or public sharing. These are instructions; the host's enabled tools and permissions determine what actions are technically possible.

For questions about the package, use the [repository issue tracker](https://github.com/RachaelQuisel/airtable-interface-builder/issues). Do not include credentials or private client records in a public issue.
