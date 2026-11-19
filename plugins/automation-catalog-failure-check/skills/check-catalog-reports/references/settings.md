# Required settings

Keep account-specific settings outside the distributed plugin. A saved task prompt or a private project configuration can supply them.

| Setting | Meaning |
| --- | --- |
| Catalog task | Stable task identifier and the scheduler that owns it. |
| Expected occurrence | Scheduled date, local time and IANA time zone. |
| Report deadline | When a missing report should trigger an alert. |
| Run key | The exact label used by the catalog's status thread. |
| Report destination | Approved service, account, workspace and channel identifiers. |
| Alert destination | Approved destination and audience for failure details. |
| Alert key | A stable label for suppressing duplicate alerts. |
| Delivery count record | Durable approved record for the alert's attempt count. |
| Fallback | Where the host should report a failed notification. |

Use the user's existing connections. Do not read credential stores, ask for passwords in chat or add a server. If the host cannot read the scheduler, mark scheduler evidence unavailable. It may still check the approved report destination. If report access fails, do not describe the catalog as healthy.

An on-demand check can ask one question for a missing setting. A scheduled check must report the missing setting and stop the dependent action. Do not wait for a live conversation.
