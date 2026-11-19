#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyairtable>=3.3.0",
# ]
# ///
"""Airtable batch operations script.

Create, update, upsert, or delete multiple records at once.
"""

import argparse
import json
import os
import sys

from pyairtable import Api


def get_api_token() -> str | None:
    return os.environ.get("AIRTABLE_API_TOKEN")


def batch_create_records(api, base_id, table_name, records_json):
    try:
        records = json.loads(records_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON for records: {e}") from e
    if not isinstance(records, list):
        raise ValueError("Records must be a JSON array")
    if not records:
        raise ValueError("At least one record is required")
    for i, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"Record at index {i} must be an object")
        if not record:
            raise ValueError(f"Record at index {i} must have at least one field")
    base = api.base(base_id)
    table = base.table(table_name)
    results = table.batch_create(records)
    return [{"id": r["id"], "fields": r["fields"]} for r in results]


def batch_update_records(api, base_id, table_name, records_json):
    try:
        records = json.loads(records_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON for records: {e}") from e
    if not isinstance(records, list):
        raise ValueError("Records must be a JSON array")
    if not records:
        raise ValueError("At least one record is required")
    for i, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"Record at index {i} must be an object")
        if "id" not in record:
            raise ValueError(f"Record at index {i} must have an 'id' field")
        if not isinstance(record["id"], str) or not record["id"]:
            raise ValueError(f"Record at index {i} must have a non-empty string 'id'")
        if "fields" not in record:
            raise ValueError(f"Record at index {i} must have a 'fields' object")
        if not isinstance(record["fields"], dict):
            raise ValueError(f"Record at index {i} 'fields' must be an object")
        if not record["fields"]:
            raise ValueError(f"Record at index {i} 'fields' must have at least one field")
    base = api.base(base_id)
    table = base.table(table_name)
    results = table.batch_update(records)
    return [{"id": r["id"], "fields": r["fields"]} for r in results]


def batch_upsert_records(api, base_id, table_name, records_json, key_fields):
    try:
        records = json.loads(records_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON for records: {e}") from e
    if not isinstance(records, list):
        raise ValueError("Records must be a JSON array")
    if not records:
        raise ValueError("At least one record is required")
    for i, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"Record at index {i} must be an object")
        if not record:
            raise ValueError(f"Record at index {i} must have at least one field")
    fields = [f.strip() for f in key_fields.split(",") if f.strip()]
    if not fields:
        raise ValueError("At least one key field is required")
    for i, record in enumerate(records):
        for field in fields:
            if field not in record:
                raise ValueError(f"Record at index {i} must contain key field '{field}'")
    upsert_records = [{"fields": r} for r in records]
    base = api.base(base_id)
    table = base.table(table_name)
    result = table.batch_upsert(upsert_records, key_fields=fields)
    return {
        "created": result.get("createdRecords", []),
        "updated": result.get("updatedRecords", []),
        "records": [{"id": r["id"], "fields": r["fields"]} for r in result.get("records", [])],
    }


def batch_delete_records(api, base_id, table_name, record_ids):
    ids = [rid.strip() for rid in record_ids.split(",") if rid.strip()]
    if not ids:
        raise ValueError("At least one record ID is required")
    base = api.base(base_id)
    table = base.table(table_name)
    return table.batch_delete(ids)


def main() -> int:
    parser = argparse.ArgumentParser(description="Airtable batch operations")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for cmd in ("create", "update", "upsert", "delete"):
        p = subparsers.add_parser(cmd)
        p.add_argument("--base-id", required=True)
        p.add_argument("--table", required=True)
        p.add_argument("--json", action="store_true")
        if cmd in ("create", "update", "upsert"):
            p.add_argument("--records", required=True)
        if cmd == "upsert":
            p.add_argument("--key-fields", required=True)
        if cmd == "delete":
            p.add_argument("--record-ids", required=True)

    args = parser.parse_args()
    token = get_api_token()
    if not token:
        print("Error: AIRTABLE_API_TOKEN environment variable is not set.", file=sys.stderr)
        return 1
    api = Api(token)

    try:
        if args.command == "create":
            results = batch_create_records(api, args.base_id, args.table, args.records)
            if args.json:
                print(json.dumps(results, indent=2))
            else:
                print(f"Created {len(results)} record(s):")
                for r in results:
                    print(f"  {r['id']}")
        elif args.command == "update":
            results = batch_update_records(api, args.base_id, args.table, args.records)
            if args.json:
                print(json.dumps(results, indent=2))
            else:
                print(f"Updated {len(results)} record(s):")
                for r in results:
                    print(f"  {r['id']}")
        elif args.command == "upsert":
            results = batch_upsert_records(api, args.base_id, args.table, args.records, args.key_fields)
            if args.json:
                print(json.dumps(results, indent=2))
            else:
                print(f"Upserted {len(results['records'])} record(s): "
                      f"created={len(results['created'])}, updated={len(results['updated'])}")
        elif args.command == "delete":
            results = batch_delete_records(api, args.base_id, args.table, args.record_ids)
            if args.json:
                print(json.dumps(results, indent=2))
            else:
                print(f"Deleted {len(results)} record(s)")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
