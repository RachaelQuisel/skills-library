#!/bin/bash
# scripts/write_prd.sh — Step 9 disk-write helper for the five-signals-prd skill.
#
# Usage:
#   ./write_prd.sh <client_key> <feature_slug> <prd_source_file>
#
# Example:
#   ./write_prd.sh EMG contract-auto-renewal /tmp/prd.md
#   → copies /tmp/prd.md → ~/Claude-Work/CLIENTS/Example Media_Rowan_Ellis/Project Documentation/prd-contract-auto-renewal-YYYY-MM-DD.md
#
# What it does:
#   - mkdir -p the destination folder if missing (logs but doesn't fail)
#   - cp the PRD into the canonical location with date stamp
#   - print the destination path (so the calling skill can echo it back)
#
# What it does NOT do:
#   - touch ~/Claude-Work/ABOUT-ME/shipping-queue.md (skill handles that separately)
#   - push to GitHub
#   - overwrite an existing file without confirmation (idempotency check below)

set -euo pipefail

CLIENT="${1:?missing client key (EMG|CC|EA|other)}"
FEATURE="${2:?missing feature slug (kebab-case)}"
PRD_SOURCE="${3:?missing PRD source file path}"

if [[ ! -f "$PRD_SOURCE" ]]; then
    echo "ERROR: source file does not exist: $PRD_SOURCE" >&2
    exit 1
fi

# Resolve client folder. Add new clients here as needed.
case "$CLIENT" in
    EMG)   FOLDER="$HOME/Claude-Work/CLIENTS/Example Media_Rowan_Ellis/Project Documentation" ;;
    CC)     FOLDER="$HOME/Claude-Work/CLIENTS/Example_Nonprofit_Dana_Whitfield/Project Documentation" ;;
    EA)    FOLDER="$HOME/Claude-Work/CLIENTS/Example_Agency_Pat_Okafor/Project Documentation" ;;
    *)      FOLDER="$HOME/Claude-Work/PROJECTS/prds" ;;
esac

DATE=$(date +%Y-%m-%d)
DEST="$FOLDER/prd-$FEATURE-$DATE.md"

mkdir -p "$FOLDER"

if [[ -f "$DEST" ]]; then
    echo "WARNING: destination already exists, not overwriting: $DEST" >&2
    echo "         To replace, rm the existing file first." >&2
    exit 2
fi

cp "$PRD_SOURCE" "$DEST"
echo "$DEST"
