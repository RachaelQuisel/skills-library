#!/usr/bin/env python3
"""Report exact local source equality; no SDK calls, source output or writes."""

import argparse
import hashlib
import json
import sys
from pathlib import Path


def describe(path):
    data = path.read_bytes()
    return {"path": str(path.resolve()), "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest()}, data


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--readback", type=Path)
    args = parser.parse_args(argv)
    try:
        source, source_bytes = describe(args.source)
        result = {"source": source, "comparison_performed": False,
                  "exact_match": None, "evidence": "local file receipt only"}
        code = 0
        if args.readback is not None:
            readback, readback_bytes = describe(args.readback)
            match = source_bytes == readback_bytes
            result.update(readback=readback, comparison_performed=True,
                          exact_match=match)
            code = 0 if match else 1
        print(json.dumps(result, indent=2))
        return code
    except OSError as error:
        print(json.dumps({"error": type(error).__name__,
                          "comparison_performed": False,
                          "exact_match": None}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
