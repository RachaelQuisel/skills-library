#!/usr/bin/env bash
# Rehearsal: run scripts/check.py against the planted bad and known-good
# fixtures. The bad fixture must fail; the good fixture must pass. If either
# outcome is wrong, the rehearsal itself fails - that is the point. A check
# you have never seen fail is a decoration.
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
CHECK="$ROOT/scripts/check.py"

if [[ ! -f "$CHECK" ]]; then
  echo "rehearsal errored: cannot find scripts/check.py at $CHECK" >&2
  exit 3
fi

PASS=0
FAIL=0

run_case() {
  local label="$1"
  local config="$2"
  local expected_outcome="$3"   # "pass" or "fail"

  echo "--- $label ---"
  python3 "$CHECK" --config "$config" --no-alert
  local rc=$?

  case "$expected_outcome" in
    pass)
      if [[ $rc -eq 0 ]]; then
        echo "  rehearsal expected PASS, got PASS - ok"
        PASS=$((PASS+1))
      else
        echo "  rehearsal expected PASS, got exit $rc - REHEARSAL FAILED"
        FAIL=$((FAIL+1))
      fi
      ;;
    fail)
      if [[ $rc -eq 0 ]]; then
        echo "  rehearsal expected FAIL, got PASS - REHEARSAL FAILED"
        echo "  this means the checker wave the planted bad example through."
        FAIL=$((FAIL+1))
      else
        echo "  rehearsal expected FAIL, got exit $rc - ok (the gate caught it)"
        PASS=$((PASS+1))
      fi
      ;;
    *)
      echo "  unknown expected outcome: $expected_outcome" >&2
      FAIL=$((FAIL+1))
      ;;
  esac
  echo
}

run_case "GOOD fixture (must pass)" "$ROOT/fixtures/good/check.json" "pass"
run_case "BAD fixture (must fail)"  "$ROOT/fixtures/bad/check.json"  "fail"

echo "Rehearsal summary: $PASS case(s) matched expectation, $FAIL did not."

if [[ $FAIL -gt 0 ]]; then
  echo "Rehearsal result: FAIL. Do not trust this checker's green lights yet."
  exit 1
fi

echo "Rehearsal result: PASS. The checker has failed a planted bad example and approved a known-good one."
exit 0
