# Prepared inventory format

The helper prepares files and publication decisions. It does not discover sources, verify facts, approve sharing, save a repository or send messages. The agent performs those steps with connectors.

Start from `assets/example-inventory.json`, which contains only fictional data.

- Set `schema_version` to 1.
- Supply `workflows` and a nonempty `coverage` list.
- Give each workflow `business_id`, `provider`, and `source_id`. Their combined identity remains stable when a title changes. Reconcile duplicates before rendering.
- Supply title, category, type, status, checked_at, tools, sources and sections. Sources need label and HTTPS URL without embedded credentials.
- Use exactly Trigger, Inputs, What happens and Outputs as section keys. Each value is a list of complete, single-line statements. Use an explicit unknown instead of inventing missing facts.
- Set run to cloud-verified, cloud-unverified, manual-start, planned or unknown. cloud-verified also needs cloud_evidence. The agent must check that evidence; the helper only checks its presence.
- Supply coverage records with business_id, account, resource, checked_at, result, detail, pages_checked and pagination_complete. Use denied, unavailable, truncated or not_checked when appropriate. A checked or empty result requires completed pagination.
- Render each business separately unless the user approved a combined private register. Only then set combined_private_register_approved to true. The output directory and publication plan can contain sensitive cross-project metadata; keep them private.

## Optional publication planning

Key routes by business_id. Each route contains business_id, workspace_id, channel_id, posting_authorized, destination_verified, audience_reviewed and existing_messages_checked. Set true only after independently checking the fact. The workflow also needs shareable_to_route set true after its content review. Missing evidence holds publication.

Key previous_publications by the identity value from an earlier plan. Each entry needs identity, business_id, workspace_id, channel_id, message_id, content_hash and receipt_verified. Record these only after successful connector receipts and readback. Never copy an unexecuted plan into the success ledger.

The helper proposes create, edit, skip or hold. A timeout or missing receipt holds the item for checking before retry. A changed destination holds it for reconciliation. Actual sending still requires the current authorization and connector checks in SKILL.md.

Output filenames use stable hashes, not user-provided paths. These are staging files. Reconcile them into existing project guide paths instead of blindly adding new files. The helper refuses an existing output directory to protect prior work.
