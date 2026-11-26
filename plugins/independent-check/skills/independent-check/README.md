# independent-check skill

Internal notes for the skill. The user-facing README lives at the plugin root.

The skill `SKILL.md` is the one-page workflow a Claude session follows when someone asks for a check that can fail an automated job. The references/ files are only read when the matching situation comes up, to keep the main SKILL.md short.

Shipped scripts (callable from any session the plugin is loaded into):

- `../../scripts/check.py` - the gate executable.
- `../../scripts/rehearse.sh` - runs the gate against the good and bad fixtures and fails the rehearsal itself if either outcome is wrong.
- `../../scripts/verify_claim.py` - the completion-claim gate.
