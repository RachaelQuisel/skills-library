#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyairtable>=3.3.0",
# ]
# ///
"""
Airtable webhook management script.

Create and manage webhooks for receiving notifications of changes.
"""

import argparse
import json
import os
import sys

from pyairtable import Api


def get_api_token() -> str | None:
    return os.environ.get("AIRTABLE_API_TOKEN")


def list_webhooks(api: Api, base_id: str) -> list[dict]:
    base = api.base(base_id)
    webhooks = base.webhooks()
    return [
        {
            "id": w.id,
            "notification_url": w.notification_url,
            "expiration_time": w.expiration_time.isoformat() if w.expiration_time else None,
            "is_active": w.is_hook_enabled,
        }
        for w in webhooks
    ]


def get_webhook(api: Api, base_id: str, webhook_id: str) -> dict:
    base = api.base(base_id)
    webhook = base.webhook(webhook_id)
    spec = webhook.specification
    spec_dict = {
        "options": {
            "filters": {
                "dataTypes": spec.options.filters.data_types,
            }
        }
    }
    filters = spec.options.filters
    if filters.record_change_scope:
        spec_dict["options"]["filters"]["recordChangeScope"] = filters.record_change_scope
    if filters.change_types:
        spec_dict["options"]["filters"]["changeTypes"] = filters.change_types
    if filters.from_sources:
        spec_dict["options"]["filters"]["fromSources"] = filters.from_sources
    if filters.watch_data_in_field_ids:
        spec_dict["options"]["filters"]["watchDataInFieldIds"] = filters.watch_data_in_field_ids
    if filters.watch_schemas_of_field_ids:
        spec_dict["options"]["filters"]["watchSchemasOfFieldIds"] = filters.watch_schemas_of_field_ids
    if filters.source_options:
        source_opts = {}
        if filters.source_options.form_submission:
            source_opts["formSubmission"] = {"viewId": filters.source_options.form_submission.view_id}
        if filters.source_options.form_page_submission:
            source_opts["formPageSubmission"] = {"pageId": filters.source_options.form_page_submission.page_id}
        if source_opts:
            spec_dict["options"]["filters"]["sourceOptions"] = source_opts
    if spec.options.includes:
        includes = spec.options.includes
        includes_dict = {}
        if includes.include_cell_values_in_field_ids is not None:
            includes_dict["includeCellValuesInFieldIds"] = includes.include_cell_values_in_field_ids
        if includes.include_previous_cell_values:
            includes_dict["includePreviousCellValues"] = True
        if includes.include_previous_field_definitions:
            includes_dict["includePreviousFieldDefinitions"] = True
        if includes_dict:
            spec_dict["options"]["includes"] = includes_dict

    return {
        "id": webhook.id,
        "notification_url": webhook.notification_url,
        "is_hook_enabled": webhook.is_hook_enabled,
        "are_notifications_enabled": webhook.are_notifications_enabled,
        "cursor_for_next_payload": webhook.cursor_for_next_payload,
        "expiration_time": webhook.expiration_time.isoformat() if webhook.expiration_time else None,
        "last_successful_notification_time": (
            webhook.last_successful_notification_time.isoformat()
            if webhook.last_successful_notification_time else None
        ),
        "specification": spec_dict,
    }


def delete_webhook(api: Api, base_id: str, webhook_id: str) -> None:
    base = api.base(base_id)
    webhook = base.webhook(webhook_id)
    webhook.delete()


def get_webhook_payloads(api: Api, base_id: str, webhook_id: str, cursor: int | None = None) -> dict:
    base = api.base(base_id)
    webhook = base.webhook(webhook_id)
    payloads = []
    last_cursor = cursor
    might_have_more = False
    for payload in webhook.payloads(cursor=cursor or 1):
        payload_dict = {
            "cursor": payload.cursor,
            "timestamp": payload.timestamp.isoformat() if payload.timestamp else None,
        }
        if payload.action_metadata:
            payload_dict["action_metadata"] = {
                "source": payload.action_metadata.source,
                "source_metadata": payload.action_metadata.source_metadata,
            }
        if payload.payloads:
            payload_dict["changes"] = payload.payloads
        payloads.append(payload_dict)
        last_cursor = payload.cursor
        might_have_more = payload.might_have_more or False
    return {
        "payloads": payloads,
        "cursor": last_cursor,
        "might_have_more": might_have_more,
    }


def create_webhook(api: Api, base_id: str, notify_url: str, spec_json: str) -> dict:
    try:
        spec = json.loads(spec_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON for spec: {e}") from e
    if not isinstance(spec, dict):
        raise ValueError("Spec must be a JSON object")
    if "options" not in spec:
        raise ValueError("Spec must contain 'options' key")
    if "filters" not in spec.get("options", {}):
        raise ValueError("Spec options must contain 'filters' key")
    base = api.base(base_id)
    result = base.add_webhook(notify_url, spec)
    return {
        "id": result.id,
        "mac_secret_base64": result.mac_secret_base64,
        "expiration_time": result.expiration_time.isoformat() if result.expiration_time else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Airtable webhook management")
    subparsers = parser.add_subparsers(dest="command", required=True)

    lp = subparsers.add_parser("list")
    lp.add_argument("--base-id", required=True)
    lp.add_argument("--json", action="store_true")

    gp = subparsers.add_parser("get")
    gp.add_argument("--base-id", required=True)
    gp.add_argument("--webhook-id", required=True)
    gp.add_argument("--json", action="store_true")

    cp = subparsers.add_parser("create")
    cp.add_argument("--base-id", required=True)
    cp.add_argument("--url", required=True)
    cp.add_argument("--spec", required=True)
    cp.add_argument("--json", action="store_true")

    dp = subparsers.add_parser("delete")
    dp.add_argument("--base-id", required=True)
    dp.add_argument("--webhook-id", required=True)
    dp.add_argument("--json", action="store_true")

    pp = subparsers.add_parser("payloads")
    pp.add_argument("--base-id", required=True)
    pp.add_argument("--webhook-id", required=True)
    pp.add_argument("--cursor", type=int)
    pp.add_argument("--json", action="store_true")

    args = parser.parse_args()

    token = get_api_token()
    if not token:
        print("Error: AIRTABLE_API_TOKEN environment variable is not set.", file=sys.stderr)
        return 1
    api = Api(token)

    try:
        if args.command == "list":
            webhooks = list_webhooks(api, args.base_id)
            if args.json:
                print(json.dumps(webhooks, indent=2))
            else:
                if not webhooks:
                    print("No webhooks found.")
                for w in webhooks:
                    print(f"Webhook ID: {w['id']}")
                    print(f"  Notification URL: {w['notification_url']}")
                    print(f"  Expiration Time: {w['expiration_time']}")
                    print(f"  Is Active: {w['is_active']}")
                    print()
        elif args.command == "get":
            webhook = get_webhook(api, args.base_id, args.webhook_id)
            if args.json:
                print(json.dumps(webhook, indent=2))
            else:
                print(f"Webhook ID: {webhook['id']}")
                print(f"Notification URL: {webhook['notification_url']}")
                print(f"Is Hook Enabled: {webhook['is_hook_enabled']}")
                print(f"Are Notifications Enabled: {webhook['are_notifications_enabled']}")
                print(f"Cursor for Next Payload: {webhook['cursor_for_next_payload']}")
                print(f"Expiration Time: {webhook['expiration_time']}")
                if webhook["last_successful_notification_time"]:
                    print(f"Last Successful Notification: {webhook['last_successful_notification_time']}")
                spec = webhook["specification"]
                filters = spec["options"]["filters"]
                print(f"Data Types: {', '.join(filters['dataTypes'])}")
                if filters.get("recordChangeScope"):
                    print(f"Record Change Scope: {filters['recordChangeScope']}")
                if filters.get("changeTypes"):
                    print(f"Change Types: {', '.join(filters['changeTypes'])}")
                if filters.get("fromSources"):
                    print(f"From Sources: {', '.join(filters['fromSources'])}")
                if filters.get("watchDataInFieldIds"):
                    print(f"Watch Data In Fields: {', '.join(filters['watchDataInFieldIds'])}")
                if filters.get("watchSchemasOfFieldIds"):
                    print(f"Watch Schemas Of Fields: {', '.join(filters['watchSchemasOfFieldIds'])}")
        elif args.command == "create":
            result = create_webhook(api, args.base_id, args.url, args.spec)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"Created webhook: {result['id']}")
                print(f"Expiration: {result['expiration_time']}")
                print(f"\nSave this secret — it cannot be retrieved again!")
                print(f"MAC Secret (base64): {result['mac_secret_base64']}", file=sys.stderr)
        elif args.command == "delete":
            delete_webhook(api, args.base_id, args.webhook_id)
            if args.json:
                print(json.dumps({"id": args.webhook_id, "deleted": True}, indent=2))
            else:
                print(f"Deleted webhook: {args.webhook_id}")
        elif args.command == "payloads":
            result = get_webhook_payloads(api, args.base_id, args.webhook_id, args.cursor)
            if args.json:
                print(json.dumps(result["payloads"], indent=2))
            else:
                if not result["payloads"]:
                    print("No payloads found.")
                for p in result["payloads"]:
                    print(f"Cursor: {p['cursor']}")
                    print(f"  Timestamp: {p['timestamp']}")
                    if p.get("action_metadata"):
                        print(f"  Source: {p['action_metadata']['source']}")
                    if p.get("changes"):
                        print(f"  Changes: {len(p['changes'])} item(s)")
                    print()
                print(f"Last Cursor: {result['cursor']}")
                if result["might_have_more"]:
                    print("(More payloads may be available)")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyError:
        print(f"Error: Webhook not found", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
