#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyairtable>=3.3.0",
# ]
# ///
"""
Airtable record management script.

Create and manage records in tables.
"""

import argparse
import json
import os
import sys

from pyairtable import Api
from pyairtable.formulas import match as formula_match


def get_api_token() -> str | None:
    return os.environ.get("AIRTABLE_API_TOKEN")


def create_record(api, base_id, table_name, fields_json):
    try:
        fields = json.loads(fields_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON for fields: {e}") from e
    if not isinstance(fields, dict):
        raise ValueError("Fields must be a JSON object")
    if not fields:
        raise ValueError("At least one field is required")
    base = api.base(base_id)
    table = base.table(table_name)
    result = table.create(fields)
    return {"id": result["id"], "fields": result["fields"]}


def get_record(api, base_id, table_name, record_id):
    base = api.base(base_id)
    table = base.table(table_name)
    result = table.get(record_id)
    return {"id": result["id"], "createdTime": result["createdTime"], "fields": result["fields"]}


def parse_sort_spec(sort_spec):
    sort_list = []
    for field_spec in sort_spec.split(","):
        field_spec = field_spec.strip()
        if not field_spec:
            continue
        if field_spec.endswith(":desc"):
            sort_list.append(f"-{field_spec[:-5]}")
        else:
            sort_list.append(field_spec)
    return sort_list


def list_records(api, base_id, table_name, max_records=None, fields=None, sort=None, view=None):
    base = api.base(base_id)
    table = base.table(table_name)
    kwargs = {}
    if max_records is not None:
        kwargs["max_records"] = max_records
    if fields is not None:
        kwargs["fields"] = fields
    if sort is not None:
        kwargs["sort"] = sort
    if view is not None:
        kwargs["view"] = view
    results = table.all(**kwargs)
    return [{"id": r["id"], "fields": r["fields"]} for r in results]


def update_record(api, base_id, table_name, record_id, fields_json):
    try:
        fields = json.loads(fields_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON for fields: {e}") from e
    if not isinstance(fields, dict):
        raise ValueError("Fields must be a JSON object")
    if not fields:
        raise ValueError("At least one field is required")
    base = api.base(base_id)
    table = base.table(table_name)
    result = table.update(record_id, fields)
    return {"id": result["id"], "fields": result["fields"]}


def delete_record(api, base_id, table_name, record_id):
    base = api.base(base_id)
    table = base.table(table_name)
    result = table.delete(record_id)
    return {"id": result["id"], "deleted": result["deleted"]}


def query_records(api, base_id, table_name, formula=None, match_dict=None, view=None):
    if formula is None and match_dict is None:
        raise ValueError("Either --formula or --match must be provided")
    if formula is not None and match_dict is not None:
        raise ValueError("Cannot use both --formula and --match together")
    base = api.base(base_id)
    table = base.table(table_name)
    query_formula = formula_match(match_dict) if match_dict is not None else formula
    kwargs = {"formula": query_formula}
    if view is not None:
        kwargs["view"] = view
    results = table.all(**kwargs)
    return [{"id": r["id"], "fields": r["fields"]} for r in results]


def list_comments(api, base_id, table_name, record_id):
    base = api.base(base_id)
    table = base.table(table_name)
    comments = table.comments(record_id)
    return [
        {
            "id": c.id,
            "author": c.author.name if c.author else None,
            "text": c.text,
            "createdTime": c.created_time.isoformat(),
        }
        for c in comments
    ]


def add_comment(api, base_id, table_name, record_id, text):
    base = api.base(base_id)
    table = base.table(table_name)
    comment = table.add_comment(record_id, text)
    return {"id": comment.id, "text": comment.text}


def delete_comment(api, base_id, table_name, record_id, comment_id):
    base = api.base(base_id)
    table = base.table(table_name)
    comments = table.comments(record_id)
    target = None
    for c in comments:
        if c.id == comment_id:
            target = c
            break
    if target is None:
        raise ValueError(f"Comment '{comment_id}' not found on record '{record_id}'")
    target.delete()
    return {"id": comment_id, "deleted": True}


def print_records_table(records, empty_message):
    if not records:
        print(empty_message)
        return False
    all_field_names = set()
    for r in records:
        all_field_names.update(r["fields"].keys())
    field_names = sorted(all_field_names)
    id_header = "ID"
    id_width = max(len(id_header), max(len(r["id"]) for r in records))
    col_widths = {}
    for name in field_names:
        max_value_len = 0
        for r in records:
            value = r["fields"].get(name, "")
            value_str = str(value) if value is not None else ""
            max_value_len = max(max_value_len, len(value_str))
        col_widths[name] = max(len(name), max_value_len)
    header_parts = [id_header.ljust(id_width)]
    for name in field_names:
        header_parts.append(name.ljust(col_widths[name]))
    print("  ".join(header_parts))
    sep_parts = ["-" * id_width]
    for name in field_names:
        sep_parts.append("-" * col_widths[name])
    print("  ".join(sep_parts))
    for r in records:
        row_parts = [r["id"].ljust(id_width)]
        for name in field_names:
            value = r["fields"].get(name, "")
            value_str = str(value) if value is not None else ""
            row_parts.append(value_str.ljust(col_widths[name]))
        print("  ".join(row_parts))
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Airtable record management")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create")
    create_parser.add_argument("--base-id", required=True)
    create_parser.add_argument("--table", required=True)
    create_parser.add_argument("--fields", required=True)
    create_parser.add_argument("--json", action="store_true")

    get_parser = subparsers.add_parser("get")
    get_parser.add_argument("--base-id", required=True)
    get_parser.add_argument("--table", required=True)
    get_parser.add_argument("--record-id", required=True)
    get_parser.add_argument("--json", action="store_true")

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--base-id", required=True)
    list_parser.add_argument("--table", required=True)
    list_parser.add_argument("--max-records", type=int)
    list_parser.add_argument("--fields")
    list_parser.add_argument("--sort")
    list_parser.add_argument("--view")
    list_parser.add_argument("--json", action="store_true")

    update_parser = subparsers.add_parser("update")
    update_parser.add_argument("--base-id", required=True)
    update_parser.add_argument("--table", required=True)
    update_parser.add_argument("--record-id", required=True)
    update_parser.add_argument("--fields", required=True)
    update_parser.add_argument("--json", action="store_true")

    delete_parser = subparsers.add_parser("delete")
    delete_parser.add_argument("--base-id", required=True)
    delete_parser.add_argument("--table", required=True)
    delete_parser.add_argument("--record-id", required=True)
    delete_parser.add_argument("--json", action="store_true")

    query_parser = subparsers.add_parser("query")
    query_parser.add_argument("--base-id", required=True)
    query_parser.add_argument("--table", required=True)
    query_parser.add_argument("--formula")
    query_parser.add_argument("--match")
    query_parser.add_argument("--view")
    query_parser.add_argument("--json", action="store_true")

    comments_parser = subparsers.add_parser("comments")
    comments_parser.add_argument("--base-id", required=True)
    comments_parser.add_argument("--table", required=True)
    comments_parser.add_argument("--record-id", required=True)
    comments_parser.add_argument("--json", action="store_true")

    add_comment_parser = subparsers.add_parser("add-comment")
    add_comment_parser.add_argument("--base-id", required=True)
    add_comment_parser.add_argument("--table", required=True)
    add_comment_parser.add_argument("--record-id", required=True)
    add_comment_parser.add_argument("--text", required=True)
    add_comment_parser.add_argument("--json", action="store_true")

    delete_comment_parser = subparsers.add_parser("delete-comment")
    delete_comment_parser.add_argument("--base-id", required=True)
    delete_comment_parser.add_argument("--table", required=True)
    delete_comment_parser.add_argument("--record-id", required=True)
    delete_comment_parser.add_argument("--comment-id", required=True)
    delete_comment_parser.add_argument("--json", action="store_true")

    args = parser.parse_args()

    token = get_api_token()
    if not token:
        print("Error: AIRTABLE_API_TOKEN environment variable is not set.", file=sys.stderr)
        return 1
    api = Api(token)

    try:
        if args.command == "create":
            result = create_record(api, args.base_id, args.table, args.fields)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"Created record: {result['id']}")
                for name, value in result["fields"].items():
                    print(f"  {name}: {value}")
        elif args.command == "get":
            result = get_record(api, args.base_id, args.table, args.record_id)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"Record ID: {result['id']}")
                print(f"Created: {result['createdTime']}")
                for name, value in result["fields"].items():
                    print(f"  {name}: {value}")
        elif args.command == "list":
            fields_list = [f.strip() for f in args.fields.split(",")] if args.fields else None
            sort_list = parse_sort_spec(args.sort) if args.sort else None
            records = list_records(api, args.base_id, args.table,
                                   max_records=args.max_records, fields=fields_list,
                                   sort=sort_list, view=args.view)
            if args.json:
                print(json.dumps(records, indent=2))
            else:
                print_records_table(records, "No records found.")
        elif args.command == "update":
            result = update_record(api, args.base_id, args.table, args.record_id, args.fields)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"Updated record: {result['id']}")
                for name, value in result["fields"].items():
                    print(f"  {name}: {value}")
        elif args.command == "delete":
            result = delete_record(api, args.base_id, args.table, args.record_id)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"Deleted record: {result['id']}")
        elif args.command == "query":
            match_dict = None
            if args.match:
                match_dict = json.loads(args.match)
                if not isinstance(match_dict, dict):
                    raise ValueError("Match must be a JSON object")
            records = query_records(api, args.base_id, args.table,
                                    formula=args.formula, match_dict=match_dict, view=args.view)
            if args.json:
                print(json.dumps(records, indent=2))
            else:
                print_records_table(records, "No matching records found.")
        elif args.command == "comments":
            comments = list_comments(api, args.base_id, args.table, args.record_id)
            if args.json:
                print(json.dumps(comments, indent=2))
            else:
                if not comments:
                    print("No comments found.")
                for c in comments:
                    print(f"Comment ID: {c['id']}")
                    print(f"Author: {c['author']}")
                    print(f"Text: {c['text']}")
                    print(f"Created Time: {c['createdTime']}")
                    print()
        elif args.command == "add-comment":
            result = add_comment(api, args.base_id, args.table, args.record_id, args.text)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"Created comment: {result['id']}")
        elif args.command == "delete-comment":
            result = delete_comment(api, args.base_id, args.table, args.record_id, args.comment_id)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"Deleted comment: {result['id']}")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
