#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyairtable>=3.3.0",
# ]
# ///
"""
Airtable schema management script.

List tables in a base, view detailed field information, create new tables, delete tables, add fields, update fields, and list views.
"""

import argparse
import json
import os
import sys

from pyairtable import Api


def get_api_token() -> str | None:
    return os.environ.get("AIRTABLE_API_TOKEN")


def list_tables(api: Api, base_id: str) -> list[dict]:
    base = api.base(base_id)
    schema = base.schema()
    tables = []
    for table_schema in schema.tables:
        tables.append({
            "id": table_schema.id,
            "name": table_schema.name,
            "field_count": len(table_schema.fields),
        })
    return tables


def describe_table(api: Api, base_id: str, table_name: str) -> dict:
    base = api.base(base_id)
    table = base.table(table_name)
    table_schema = table.schema()
    fields = []
    for field in table_schema.fields:
        fields.append({
            "id": field.id,
            "name": field.name,
            "type": field.type,
        })
    return {
        "id": table_schema.id,
        "name": table_schema.name,
        "fields": fields,
    }


TABLE_CREATION_FIELD_TYPES = {
    "singleLineText", "number", "singleSelect", "checkbox",
    "date", "dateTime", "email", "url",
}

FIELD_CREATION_FIELD_TYPES = {
    "singleLineText", "multilineText", "number", "singleSelect",
    "multipleSelects", "checkbox", "date", "dateTime", "email", "url",
    "phoneNumber", "currency", "percent", "duration", "rating", "richText",
    "multipleRecordLinks", "multipleAttachments", "multipleLookupValues", "rollup",
}

SUPPORTED_ROLLUP_FUNCTIONS = {
    "SUM", "COUNT", "AVERAGE", "MAX", "MIN", "COUNTA", "COUNTALL",
    "CONCATENATE", "ARRAYJOIN", "ARRAYUNIQUE", "ARRAYCOMPACT",
}


def validate_field_definition(field: dict, allowed_types: set[str] | None = None) -> str | None:
    if allowed_types is None:
        allowed_types = TABLE_CREATION_FIELD_TYPES
    if "name" not in field:
        return "Field must have a 'name' property"
    if "type" not in field:
        return f"Field '{field.get('name', 'unknown')}' must have a 'type' property"
    if field["type"] not in allowed_types:
        return (
            f"Field '{field['name']}' has unsupported type '{field['type']}'. "
            f"Supported types: {', '.join(sorted(allowed_types))}"
        )
    if field["type"] == "multipleRecordLinks":
        options = field.get("options", {})
        if not options.get("linkedTableId") and not options.get("linkedTableName"):
            return (
                f"Field '{field['name']}' of type 'multipleRecordLinks' requires "
                "'options.linkedTableId' or 'options.linkedTableName'"
            )
    if field["type"] == "multipleLookupValues":
        options = field.get("options", {})
        if not options.get("recordLinkFieldId") and not options.get("recordLinkFieldName"):
            return (
                f"Field '{field['name']}' of type 'multipleLookupValues' requires "
                "'options.recordLinkFieldId' or 'options.recordLinkFieldName'"
            )
        if not options.get("fieldIdInLinkedTable") and not options.get("fieldNameInLinkedTable"):
            return (
                f"Field '{field['name']}' of type 'multipleLookupValues' requires "
                "'options.fieldIdInLinkedTable' or 'options.fieldNameInLinkedTable'"
            )
    if field["type"] == "rollup":
        options = field.get("options", {})
        if not options.get("recordLinkFieldId") and not options.get("recordLinkFieldName"):
            return (
                f"Field '{field['name']}' of type 'rollup' requires "
                "'options.recordLinkFieldId' or 'options.recordLinkFieldName'"
            )
        if not options.get("fieldIdInLinkedTable") and not options.get("fieldNameInLinkedTable"):
            return (
                f"Field '{field['name']}' of type 'rollup' requires "
                "'options.fieldIdInLinkedTable' or 'options.fieldNameInLinkedTable'"
            )
        if not options.get("formula") and not options.get("aggregationFunction"):
            return (
                f"Field '{field['name']}' of type 'rollup' requires "
                "'options.formula' or 'options.aggregationFunction'"
            )
        if options.get("aggregationFunction"):
            func = options["aggregationFunction"].upper()
            if func not in SUPPORTED_ROLLUP_FUNCTIONS:
                return (
                    f"Field '{field['name']}' has unsupported aggregation function "
                    f"'{options['aggregationFunction']}'. Supported: "
                    f"{', '.join(sorted(SUPPORTED_ROLLUP_FUNCTIONS))}"
                )
    return None


def create_table(api: Api, base_id: str, name: str, fields_json: str) -> dict:
    try:
        fields = json.loads(fields_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON for fields: {e}") from e
    if not isinstance(fields, list):
        raise ValueError("Fields must be a JSON array")
    if not fields:
        raise ValueError("At least one field is required")
    for field in fields:
        error = validate_field_definition(field)
        if error:
            raise ValueError(error)
    base = api.base(base_id)
    new_table = base.create_table(name=name, fields=fields)
    table = base.table(new_table.id)
    table_schema = table.schema()
    created_fields = []
    for field in table_schema.fields:
        created_fields.append({
            "id": field.id,
            "name": field.name,
            "type": field.type,
        })
    return {
        "id": new_table.id,
        "name": new_table.name,
        "fields": created_fields,
    }


def delete_table(api: Api, base_id: str, table_name: str) -> dict:
    base = api.base(base_id)
    table = base.table(table_name)
    table_schema = table.schema()
    deleted_name = table_schema.name
    table_id = table_schema.id
    api.request(
        method="DELETE",
        url=f"https://api.airtable.com/v0/meta/bases/{base_id}/tables/{table_id}",
    )
    return {"deleted": True, "name": deleted_name}


def resolve_linked_table_name(api: Api, base_id: str, table_name: str) -> str:
    base = api.base(base_id)
    schema = base.schema()
    for table_schema in schema.tables:
        if table_schema.name == table_name:
            return table_schema.id
    raise ValueError(f"Table '{table_name}' not found in base '{base_id}'")


def resolve_field_name(api: Api, base_id: str, table_name: str, field_name: str) -> str:
    base = api.base(base_id)
    table = base.table(table_name)
    table_schema = table.schema()
    for field in table_schema.fields:
        if field.name == field_name:
            return field.id
    raise ValueError(f"Field '{field_name}' not found in table '{table_name}'")


def _resolve_linked_field(api, base_id, table_name, record_link_field_id, field_name):
    base = api.base(base_id)
    table_for_schema = base.table(table_name)
    table_schema = table_for_schema.schema()
    linked_table_id = None
    for fld in table_schema.fields:
        if fld.id == record_link_field_id:
            if hasattr(fld, "options") and fld.options:
                linked_table_id = getattr(fld.options, "linked_table_id", None)
            break
    if not linked_table_id:
        raise ValueError(
            f"Could not determine linked table for record link field '{record_link_field_id}'"
        )
    return resolve_field_name(api, base_id, linked_table_id, field_name)


def create_field(api: Api, base_id: str, table_name: str, field_json: str) -> dict:
    try:
        field = json.loads(field_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON for field: {e}") from e
    if not isinstance(field, dict):
        raise ValueError("Field must be a JSON object")
    error = validate_field_definition(field, allowed_types=FIELD_CREATION_FIELD_TYPES)
    if error:
        raise ValueError(error)

    name = field["name"]
    field_type = field["type"]
    description = field.get("description")
    options = field.get("options")

    if field_type == "multipleRecordLinks" and options:
        if options.get("linkedTableName") and not options.get("linkedTableId"):
            linked_table_name = options.pop("linkedTableName")
            options["linkedTableId"] = resolve_linked_table_name(api, base_id, linked_table_name)

    if field_type == "multipleLookupValues" and options:
        if options.get("recordLinkFieldName") and not options.get("recordLinkFieldId"):
            record_link_field_name = options.pop("recordLinkFieldName")
            options["recordLinkFieldId"] = resolve_field_name(api, base_id, table_name, record_link_field_name)
        if options.get("fieldNameInLinkedTable") and not options.get("fieldIdInLinkedTable"):
            field_name_in_linked_table = options.pop("fieldNameInLinkedTable")
            options["fieldIdInLinkedTable"] = _resolve_linked_field(
                api, base_id, table_name, options["recordLinkFieldId"], field_name_in_linked_table
            )

    if field_type == "rollup" and options:
        if options.get("recordLinkFieldName") and not options.get("recordLinkFieldId"):
            record_link_field_name = options.pop("recordLinkFieldName")
            options["recordLinkFieldId"] = resolve_field_name(api, base_id, table_name, record_link_field_name)
        if options.get("fieldNameInLinkedTable") and not options.get("fieldIdInLinkedTable"):
            field_name_in_linked_table = options.pop("fieldNameInLinkedTable")
            options["fieldIdInLinkedTable"] = _resolve_linked_field(
                api, base_id, table_name, options["recordLinkFieldId"], field_name_in_linked_table
            )
        if options.get("aggregationFunction") and not options.get("formula"):
            func = options.pop("aggregationFunction").upper()
            options["formula"] = f"{func}(values)"

    base = api.base(base_id)
    table = base.table(table_name, validate=True)
    created_field = table.create_field(
        name=name,
        field_type=field_type,
        description=description,
        options=options,
    )

    result = {
        "id": created_field.id,
        "name": created_field.name,
        "type": created_field.type,
    }

    if field_type == "multipleRecordLinks" and options:
        result["options"] = {}
        if options.get("linkedTableId"):
            result["options"]["linkedTableId"] = options["linkedTableId"]
        if options.get("prefersSingleRecordLink"):
            result["options"]["prefersSingleRecordLink"] = options["prefersSingleRecordLink"]

    if field_type == "multipleLookupValues" and options:
        result["options"] = {}
        if options.get("recordLinkFieldId"):
            result["options"]["recordLinkFieldId"] = options["recordLinkFieldId"]
        if options.get("fieldIdInLinkedTable"):
            result["options"]["fieldIdInLinkedTable"] = options["fieldIdInLinkedTable"]

    if field_type == "rollup" and options:
        result["options"] = {}
        if options.get("recordLinkFieldId"):
            result["options"]["recordLinkFieldId"] = options["recordLinkFieldId"]
        if options.get("fieldIdInLinkedTable"):
            result["options"]["fieldIdInLinkedTable"] = options["fieldIdInLinkedTable"]
        if options.get("formula"):
            result["options"]["formula"] = options["formula"]

    return result


def update_field(api, base_id, table_name, field_id, name=None, description=None):
    if name is None and description is None:
        raise ValueError("At least one of --name or --description must be provided")
    base = api.base(base_id)
    table = base.table(table_name)
    table_schema = table.schema()
    field = None
    for f in table_schema.fields:
        if f.id == field_id:
            field = f
            break
    if field is None:
        raise ValueError(f"Field with ID '{field_id}' not found in table '{table_name}'")
    if name is not None:
        field.name = name
    if description is not None:
        field.description = description
    field.save()
    result = {"id": field.id, "name": field.name, "type": field.type}
    if field.description:
        result["description"] = field.description
    return result


def list_views(api: Api, base_id: str, table_name: str) -> list[dict]:
    base = api.base(base_id)
    table = base.table(table_name)
    table_schema = table.schema()
    views = []
    for view in table_schema.views:
        views.append({"id": view.id, "name": view.name, "type": view.type})
    return views


def format_tables_table(tables):
    if not tables:
        return "No tables found."
    id_width = max(len("Table ID"), max(len(t["id"]) for t in tables))
    name_width = max(len("Table Name"), max(len(t["name"]) for t in tables))
    count_width = max(len("Field Count"), max(len(str(t["field_count"])) for t in tables))
    lines = []
    lines.append(f"{'Table ID':<{id_width}}  {'Table Name':<{name_width}}  {'Field Count':>{count_width}}")
    lines.append(f"{'-' * id_width}  {'-' * name_width}  {'-' * count_width}")
    for t in tables:
        lines.append(f"{t['id']:<{id_width}}  {t['name']:<{name_width}}  {t['field_count']:>{count_width}}")
    return "\n".join(lines)


def format_fields_table(table_info):
    lines = [f"Table: {table_info['name']} ({table_info['id']})", ""]
    fields = table_info["fields"]
    if not fields:
        lines.append("No fields found.")
        return "\n".join(lines)
    name_width = max(len("Field Name"), max(len(f["name"]) for f in fields))
    type_width = max(len("Field Type"), max(len(f["type"]) for f in fields))
    id_width = max(len("Field ID"), max(len(f["id"]) for f in fields))
    lines.append(f"{'Field Name':<{name_width}}  {'Field Type':<{type_width}}  {'Field ID':<{id_width}}")
    lines.append(f"{'-' * name_width}  {'-' * type_width}  {'-' * id_width}")
    for f in fields:
        lines.append(f"{f['name']:<{name_width}}  {f['type']:<{type_width}}  {f['id']:<{id_width}}")
    return "\n".join(lines)


def format_views_table(views):
    if not views:
        return "No views found."
    id_width = max(len("View ID"), max(len(v["id"]) for v in views))
    name_width = max(len("View Name"), max(len(v["name"]) for v in views))
    type_width = max(len("Type"), max(len(v["type"]) for v in views))
    lines = []
    lines.append(f"{'View ID':<{id_width}}  {'View Name':<{name_width}}  {'Type':<{type_width}}")
    lines.append(f"{'-' * id_width}  {'-' * name_width}  {'-' * type_width}")
    for v in views:
        lines.append(f"{v['id']:<{id_width}}  {v['name']:<{name_width}}  {v['type']:<{type_width}}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Airtable schema management")
    subparsers = parser.add_subparsers(dest="command", required=True)

    tables_parser = subparsers.add_parser("tables")
    tables_sub = tables_parser.add_subparsers(dest="tables_command", required=True)

    tl = tables_sub.add_parser("list")
    tl.add_argument("--base-id", required=True)
    tl.add_argument("--json", action="store_true")

    td = tables_sub.add_parser("describe")
    td.add_argument("--base-id", required=True)
    td.add_argument("--table", required=True)
    td.add_argument("--json", action="store_true")

    tc = tables_sub.add_parser("create")
    tc.add_argument("--base-id", required=True)
    tc.add_argument("--name", required=True)
    tc.add_argument("--fields", required=True)
    tc.add_argument("--json", action="store_true")

    tdel = tables_sub.add_parser("delete")
    tdel.add_argument("--base-id", required=True)
    tdel.add_argument("--table", required=True)
    tdel.add_argument("--json", action="store_true")

    fields_parser = subparsers.add_parser("fields")
    fields_sub = fields_parser.add_subparsers(dest="fields_command", required=True)

    fc = fields_sub.add_parser("create")
    fc.add_argument("--base-id", required=True)
    fc.add_argument("--table", required=True)
    fc.add_argument("--field", required=True)
    fc.add_argument("--json", action="store_true")

    fu = fields_sub.add_parser("update")
    fu.add_argument("--base-id", required=True)
    fu.add_argument("--table", required=True)
    fu.add_argument("--field-id", required=True)
    fu.add_argument("--name")
    fu.add_argument("--description")
    fu.add_argument("--json", action="store_true")

    views_parser = subparsers.add_parser("views")
    views_sub = views_parser.add_subparsers(dest="views_command", required=True)

    vl = views_sub.add_parser("list")
    vl.add_argument("--base-id", required=True)
    vl.add_argument("--table", required=True)
    vl.add_argument("--json", action="store_true")

    args = parser.parse_args()

    token = get_api_token()
    if not token:
        print("Error: AIRTABLE_API_TOKEN environment variable is not set.", file=sys.stderr)
        return 1
    api = Api(token)

    try:
        if args.command == "tables":
            if args.tables_command == "list":
                tables = list_tables(api, args.base_id)
                if args.json:
                    print(json.dumps(tables, indent=2))
                else:
                    print(format_tables_table(tables))
            elif args.tables_command == "describe":
                info = describe_table(api, args.base_id, args.table)
                if args.json:
                    print(json.dumps(info, indent=2))
                else:
                    print(format_fields_table(info))
            elif args.tables_command == "create":
                result = create_table(api, args.base_id, args.name, args.fields)
                if args.json:
                    print(json.dumps(result, indent=2))
                else:
                    print(f"Created table '{result['name']}' with ID: {result['id']}")
                    print(f"Fields created: {len(result['fields'])}")
            elif args.tables_command == "delete":
                result = delete_table(api, args.base_id, args.table)
                if args.json:
                    print(json.dumps(result, indent=2))
                else:
                    print(f"Deleted table '{result['name']}'")
        elif args.command == "fields":
            if args.fields_command == "create":
                result = create_field(api, args.base_id, args.table, args.field)
                if args.json:
                    print(json.dumps(result, indent=2))
                else:
                    print(f"Created field '{result['name']}' with ID: {result['id']}")
                    print(f"Type: {result['type']}")
            elif args.fields_command == "update":
                result = update_field(api, args.base_id, args.table, args.field_id, args.name, args.description)
                if args.json:
                    print(json.dumps(result, indent=2))
                else:
                    print(f"Updated field '{result['name']}' (ID: {result['id']})")
                    print(f"Type: {result['type']}")
                    if result.get("description"):
                        print(f"Description: {result['description']}")
        elif args.command == "views":
            if args.views_command == "list":
                views = list_views(api, args.base_id, args.table)
                if args.json:
                    print(json.dumps(views, indent=2))
                else:
                    print(format_views_table(views))
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
