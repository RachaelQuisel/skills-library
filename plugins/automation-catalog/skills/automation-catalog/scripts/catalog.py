"""Validate and render an inventory. Never connect to a service or publish."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

SECTIONS = ("Trigger", "Inputs", "What happens", "Outputs")
RESULTS = {"checked", "empty", "denied", "unavailable", "truncated", "not_checked"}
RUNS = {"cloud-verified", "cloud-unverified", "manual-start", "planned", "unknown"}


def required_text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be nonempty text")
    return value


def identity(workflow):
    parts = [required_text(workflow.get(k), k) for k in ("business_id", "provider", "source_id")]
    return hashlib.sha256(json.dumps(parts, ensure_ascii=False).encode()).hexdigest()[:24]


def tag(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def validate(data):
    if data.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    if not isinstance(data.get("workflows"), list) or not isinstance(data.get("coverage"), list):
        raise ValueError("workflows and coverage must be lists")
    if not data["coverage"]:
        raise ValueError("Record source coverage, even when access was unavailable")
    seen = set()
    businesses = set()
    for w in data["workflows"]:
        key = identity(w)
        if key in seen:
            raise ValueError("Duplicate workflow identity; reconcile before rendering")
        seen.add(key)
        businesses.add(w["business_id"])
        for field in ("title", "category", "type", "status", "checked_at"):
            required_text(w.get(field), field)
        if w.get("run") not in RUNS:
            raise ValueError("Unknown run label")
        if w["run"] == "cloud-verified" and not w.get("cloud_evidence"):
            raise ValueError("Cloud verified requires evidence")
        if not isinstance(w.get("tools"), list) or any(not isinstance(t, str) or not t.strip() for t in w["tools"]):
            raise ValueError("tools must be a list of source tool names")
        if set(w.get("sections", {})) != set(SECTIONS):
            raise ValueError("Exactly four /auto sections are required")
        for heading, lines in w["sections"].items():
            if not isinstance(lines, list) or not lines:
                raise ValueError(f"{heading} needs at least one fact or explicit unknown")
            for line in lines:
                required_text(line, heading)
                if "\n" in line or "\r" in line or "—" in line:
                    raise ValueError("Use single-line plain-English statements without em dashes")
        if not isinstance(w.get("sources"), list) or not w["sources"]:
            raise ValueError("At least one source is required")
        for source in w["sources"]:
            required_text(source.get("label"), "source label")
            parsed = urlparse(required_text(source.get("url"), "source URL"))
            if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
                raise ValueError("Source URLs must be HTTPS without embedded credentials")
    for c in data["coverage"]:
        for field in ("business_id", "account", "resource", "checked_at", "detail"):
            required_text(c.get(field), field)
        if c.get("result") not in RESULTS:
            raise ValueError("Unknown coverage result")
        if not isinstance(c.get("pages_checked"), int) or isinstance(c["pages_checked"], bool) or c["pages_checked"] < 0:
            raise ValueError("pages_checked must be a nonnegative integer")
        if c["result"] in {"checked", "empty"} and c.get("pagination_complete") is not True:
            raise ValueError("Incomplete pagination must be marked truncated")
    for business in businesses:
        if not any(c["business_id"] == business for c in data["coverage"]):
            raise ValueError("Every business needs a coverage record")
    if len(businesses) > 1 and data.get("combined_private_register_approved") is not True:
        raise ValueError("Render businesses separately unless a combined private register is approved")
    return data


def render(w):
    tags = list(dict.fromkeys(tag(x) for x in [w["category"], w["type"], *w["tools"], w["run"]]))
    lines = [f'# {w["title"]}', "", f'Status: {w["status"]}. Checked: {w["checked_at"]}.', "",
             f'Category: {w["category"]} | Type: {w["type"]}', "",
             'Tools named in sources: ' + (", ".join(w["tools"]) or "Unknown") + '. This does not confirm live connections.', "",
             f'Runs: {w["run"]}.', "", 'Tags: ' + ' '.join(f'`#{t}`' for t in tags), ""]
    for heading in SECTIONS:
        lines += [f"## {heading}", ""]
        for i, item in enumerate(w["sections"][heading], 1):
            lines.append(f'{i}. {item}' if heading == "What happens" else f'- {item}')
        if heading == "Inputs":
            for source in w["sources"]:
                lines.append(f'- Source: {source["label"]} ({source["url"]})')
        lines.append("")
    return "\n".join(lines)


def publication_action(w, digest, route, prior):
    """Evidence fields must be verified by the agent; this function grants no authority."""
    if not isinstance(route, dict) or route.get("posting_authorized") is not True:
        return "hold", "Posting is not authorized."
    if route.get("business_id") != w["business_id"]:
        return "hold", "The destination belongs to a different business."
    if not all(route.get(k) is True for k in ("destination_verified", "audience_reviewed")):
        return "hold", "Verify the destination and its audience."
    if not all(isinstance(route.get(k), str) and route[k].strip() for k in ("workspace_id", "channel_id")):
        return "hold", "Workspace or channel ID is missing."
    if w.get("shareable_to_route") is not True:
        return "hold", "Review this guide for the destination's audience."
    if prior:
        if prior.get("identity") != identity(w) or prior.get("business_id") != w["business_id"]:
            return "hold", "The previous publication belongs to a different workflow."
        if any(prior.get(k) != route.get(k) for k in ("workspace_id", "channel_id")):
            return "hold", "The previous publication has a different destination."
        if not prior.get("message_id") or prior.get("receipt_verified") is not True:
            return "hold", "Check the previous send before retrying."
        if prior.get("content_hash") == digest:
            return "skip", "The saved content is unchanged."
        return "edit", "Update the existing message after reading its current contents."
    if route.get("existing_messages_checked") is not True:
        return "hold", "Search for an existing guide before creating a message."
    return "create", "Create in the approved existing index thread or resolve an index first."


def prepare(data):
    validate(data)
    guides, plan, grouped = {}, [], {}
    routes = data.get("routes", {})
    prior = data.get("previous_publications", {})
    if not isinstance(routes, dict) or not isinstance(prior, dict):
        raise ValueError("routes and previous_publications must be objects")
    for w in data["workflows"]:
        key = identity(w)
        business_path = hashlib.sha256(w["business_id"].encode()).hexdigest()[:16]
        path = f"{business_path}/{key}.md"
        body = render(w)
        digest = hashlib.sha256(body.encode()).hexdigest()
        action, reason = publication_action(w, digest, routes.get(w["business_id"]), prior.get(key))
        guides[path] = body
        grouped.setdefault((w["business_id"], business_path), []).append((w, key))
        plan.append({"identity": key, "business_id": w["business_id"], "guide_path": path,
                     "content_hash": digest, "action": action, "reason": reason,
                     "posted": False, "message_id": (prior.get(key) or {}).get("message_id")})
    for (business, directory), items in grouped.items():
        text = [f"# Automation catalog: {business}", "", "Found in checked sources. This is not proof of exhaustive coverage or live operation.", ""]
        for category in sorted({w["category"] for w, _ in items}):
            text += [f"## {category}", ""]
            for w, key in items:
                if w["category"] == category:
                    text.append(f'- [{w["title"]}]({key}.md): {w["type"]}. Status: {w["status"]}. Runs: {w["run"]}.')
            text.append("")
        text += ["## Search coverage", ""]
        for c in data["coverage"]:
            if c["business_id"] == business:
                text.append(f'- {c["resource"]}: {c["result"]}. {c["detail"]}')
        guides[f"{directory}/index.md"] = "\n".join(text) + "\n"
    return guides, {"schema_version": 1, "publication_performed": False, "items": plan,
                    "coverage": data["coverage"], "coverage_has_gaps": any(c["result"] not in {"checked", "empty"} for c in data["coverage"])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        guides, plan = prepare(json.loads(args.input.read_text()))
        args.output.mkdir(parents=True, exist_ok=False)
        for path, body in guides.items():
            target = args.output / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(body)
        (args.output / "publication-plan.json").write_text(json.dumps(plan, indent=2) + "\n")
    except (ValueError, TypeError, KeyError, OSError) as exc:
        parser.exit(2, f"Not completed: {exc}\n")
    print(f"Prepared {len(plan['items'])} guides. Nothing was posted. Review publication-plan.json.")


if __name__ == "__main__":
    main()
