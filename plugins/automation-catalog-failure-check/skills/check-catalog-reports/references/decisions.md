# Report decisions

Evaluate these rules in order. Verify that every piece of evidence belongs to the same task and occurrence.

| Observed evidence | Action |
| --- | --- |
| Required task or destination setting is missing | Report blocked in the host. Do not guess. |
| More than five catalog attempts | Alert that the attempt limit was exceeded. Do not retry. |
| Catalog task is disabled | Alert once for this occurrence. Leave it disabled. |
| Verified COMPLETE report | Stay quiet. |
| PARTIAL or FAILED report with blockers | Do not repeat the existing report. |
| Before the deadline with no final report | Report pending only if the user requested an on-demand result. |
| Deadline passed, start found, no final report | Alert that the report is missing. The run may still be active or unable to report. |
| Deadline passed, no start and no final report | Alert that no run evidence was found. Do not assert that it never ran. |
| Report channel cannot be read | Report verification unavailable in the host. Do not report healthy. |
| Matching alert already delivered | Skip the duplicate alert. |
| Alert write timed out | Read the destination before any retry. |
| Five alert-delivery attempts used | Stop delivery attempts. Report the delivery failure in the host. |

The catalog's five-attempt budget and the monitor's alert-delivery budget are separate. The monitor never adds a catalog attempt. These are model instructions. This package does not include a scheduler that enforces them in code.
