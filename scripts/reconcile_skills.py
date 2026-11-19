#!/usr/bin/env python3
"""Reconcile every copy of each skill and pick the best version.

Copies are gathered from:
  canonical   <repo>/<skill>/SKILL.md            (the release source of truth)
  bundled     <repo>/plugins/<plugin>/skills/<skill>/SKILL.md  (generated exports)
  account     <repo>/synced/<id>/<skill>/SKILL.md (claude.ai account snapshot;
              only skills whose manifest source is "plugin", i.e. ones Rachael made)
  extra       any --account-dir given on the command line (same layout as synced/)

Dry run (default) writes a decision report and changes nothing.
--write applies the decisions to canonical folders only; run
scripts/release_sync.py --write afterwards to regenerate bundled copies.

Choosing the best version, in order:
  1. Same instructions once house boilerplate and frontmatter are ignored -> keep canonical.
  2. Only one copy exists outside bundled exports -> that copy.
  3. Copy with the higher semantic version wins (missing version ranks lowest).
  4. Otherwise the most recently updated copy wins (account manifest updatedAt
     vs. the last Git commit that touched the canonical file).
  5. If the losing copy also changed since the two last matched, mark CONFLICT:
     the script will not write it; a person picks.
Bundled copies never win: they are regenerated from canonical.
"""
import argparse, datetime as dt, hashlib, json, pathlib, re, subprocess, sys

RENAMES = {  # old skill name -> current canonical name
    "artifact": "build-page-publisher-local",
    "auto": "automation-explainer-local",
    "education": "how-it-works-doc-writer-local",
}
BOILERPLATE = ("Purpose in plain English", "How to explain the result", "Following the process")
SKIP_SOURCES = {"anthropic", "anthropic-example"}


def split_frontmatter(text):
    text = text.replace("\r\n", "\n")
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    return (m.group(1), m.group(2)) if m else ("", text)


def field(front, key):
    m = re.search(rf"^{key}:\s*[\"']?([^\"'\n]+)", front, re.M)
    return m.group(1).strip() if m else None


def body_key(text):
    """Instructions only: no frontmatter, no house boilerplate sections, normalized whitespace."""
    _, body = split_frontmatter(text)
    out, skip = [], False
    for line in body.split("\n"):
        h = re.match(r"^#{1,6}\s+(.*)", line)
        if h:
            skip = h.group(1).strip() in BOILERPLATE
            if skip:
                continue
        if not skip:
            out.append(line)
    norm = re.sub(r"\s+", " ", "\n".join(out)).strip()
    return hashlib.sha256(norm.encode()).hexdigest()[:12]


def semver(v):
    m = re.match(r"(\d+)\.(\d+)\.(\d+)", v or "")
    return tuple(map(int, m.groups())) if m else (-1, -1, -1)


def git_date(repo, rel):
    try:
        out = subprocess.run(["git", "-C", str(repo), "log", "-1", "--format=%cI", "--", rel],
                             capture_output=True, text=True, timeout=30).stdout.strip()
        return dt.datetime.fromisoformat(out) if out else None
    except Exception:
        return None


def git_body_history(repo, rel, limit=200):
    """Body keys of every committed revision of a canonical file (to detect two-sided edits)."""
    try:
        revs = subprocess.run(["git", "-C", str(repo), "log", f"-{limit}", "--format=%H", "--", rel],
                              capture_output=True, text=True, timeout=60).stdout.split()
        keys = set()
        for r in revs:
            t = subprocess.run(["git", "-C", str(repo), "show", f"{r}:{rel}"],
                               capture_output=True, text=True, timeout=30).stdout
            if t:
                keys.add(body_key(t))
        return keys
    except Exception:
        return set()


def account_copies(snapshot_root, label):
    found = []
    for manifest in pathlib.Path(snapshot_root).glob("*/manifest.json"):
        meta = {s["name"]: s for s in json.loads(manifest.read_text()).get("skills", [])}
        for skill_md in manifest.parent.glob("*/SKILL.md"):
            name = skill_md.parent.name
            info = meta.get(name, {})
            if info.get("source") in SKIP_SOURCES:
                continue
            ts = info.get("updatedAt")
            found.append(dict(kind=label, name=name, path=skill_md,
                              when=dt.datetime.fromisoformat(ts.replace("Z", "+00:00")) if ts else None))
    return found


def gather(repo, extra_dirs):
    copies = []
    for p in repo.glob("*/SKILL.md"):
        if p.parts[-2] in ("plugins", "synced", "archive", ".trash"):
            continue
        rel = str(p.relative_to(repo))
        copies.append(dict(kind="canonical", name=p.parent.name, path=p, when=git_date(repo, rel)))
    reg = repo / "release-registry.json"
    sources = {s["source"] for s in json.loads(reg.read_text()).get("skills", [])} if reg.exists() else set()
    for p in repo.glob("plugins/*/skills/*/SKILL.md"):
        rel = str(p.relative_to(repo))
        if rel in sources:  # the registry says this plugin copy IS the source
            copies.append(dict(kind="canonical", name=p.parent.name, path=p, when=git_date(repo, rel)))
        else:
            copies.append(dict(kind="bundled", name=p.parent.name, path=p, when=None, plugin=p.parts[-4]))
    if (repo / "synced").exists():
        copies += account_copies(repo / "synced", "account")
    for d in extra_dirs:
        copies += account_copies(d, "extra")
    for c in copies:
        text = c["path"].read_text(errors="replace")
        front, _ = split_frontmatter(text)
        c.update(text=text, version=field(front, "version"), key=body_key(text))
    return copies


def decide(repo, name, group):
    canons = [c for c in group if c["kind"] == "canonical"]
    canon = canons[0] if canons else None
    sources = [c for c in group if c["kind"] != "bundled"]
    bundled = [c for c in group if c["kind"] == "bundled"]
    d = dict(skill=name, canonical=bool(canon), copies=len(group))
    if len(canons) > 1 and len({c["key"] for c in canons}) > 1:
        top = max(canons, key=lambda c: semver(c["version"]))
        d.update(action="conflict", winner=top["kind"], winner_path=str(top["path"]),
                 note="Two registered sources differ: " + ", ".join(f"{c['path'].parent.relative_to(repo)} v{c['version']}" for c in canons))
        return d
    if not sources:
        d.update(action="bundled-only", winner=bundled[0]["kind"], note="No canonical folder; promote bundled copy to canonical")
        d["winner_path"] = str(bundled[0]["path"])
        return d
    if len({c["key"] for c in sources}) == 1:
        d.update(action="in-sync" if canon else "add", winner=(canon or sources[0])["kind"],
                 winner_path=str((canon or sources[0])["path"]),
                 note="Same instructions everywhere" if canon else "Only in account snapshot; add to repo")
        if bundled and canon and any(b["key"] != canon["key"] for b in bundled):
            d.update(action="regen-bundled", note="Bundled export is stale; regenerate from canonical")
        return d
    others = [c for c in sources if c is not canon]
    if canon and all(not c["version"] for c in others):
        # Account copies carry no version, so versions can't decide. Use history instead.
        history = git_body_history(repo, str(canon["path"].relative_to(repo)))
        new = [c for c in others if c["key"] not in history]
        if not new:
            d.update(action="keep-canonical", winner="canonical", winner_path=str(canon["path"]),
                     note="Account copy matches an earlier repo revision; repo is ahead")
        else:
            w = max(new, key=lambda c: c["when"] or dt.datetime.min.replace(tzinfo=dt.timezone.utc))
            d.update(action="review", winner=w["kind"], winner_path=str(w["path"]),
                     note=f"Account copy (updated {w['when']:%Y-%m-%d}) has instructions never in the repo; compare and merge" if w["when"] else "Account copy has instructions never in the repo; compare and merge")
        return d
    best = sorted(sources, key=lambda c: (semver(c["version"]),
                                          c["when"] or dt.datetime.min.replace(tzinfo=dt.timezone.utc),
                                          c["kind"] == "canonical"), reverse=True)[0]
    d.update(winner=best["kind"], winner_path=str(best["path"]))
    if best is canon:
        d.update(action="keep-canonical", note="Canonical is newer or higher version")
        return d
    history = git_body_history(repo, str(canon["path"].relative_to(repo))) if canon else set()
    if canon and best["key"] in history:
        d.update(action="keep-canonical", winner="canonical", winner_path=str(canon["path"]),
                 note="Account copy matches an older canonical revision; canonical is ahead")
    elif canon and history and canon["key"] not in history:
        d.update(action="conflict", note="Both copies changed independently; a person must choose")
    else:
        d.update(action="take-account", note="Account copy is newer; merge its instructions into canonical")
    return d


def merge_into_canonical(canon_text, winner_text, new_version):
    """Winner's instructions, canonical's frontmatter and house sections, bumped version."""
    c_front, c_body = split_frontmatter(canon_text)
    w_front, w_body = split_frontmatter(winner_text)
    front = c_front or w_front
    if re.search(r"^version:", front, re.M):
        front = re.sub(r"^version:.*$", f"version: {new_version}", front, flags=re.M)
    else:
        front += f"\nversion: {new_version}"
    desc = field(w_front, "description")
    if desc and not re.search(r"^description:\s*[>|]", front, re.M):
        front = re.sub(r"^description:.*$", lambda _: f"description: {desc}", front, flags=re.M)
    house = []
    for title in BOILERPLATE:
        m = re.search(rf"(## {re.escape(title)}\n.*?)(?=\n## |\Z)", c_body, re.S)
        if m and f"## {title}" not in w_body:
            house.append(m.group(1).rstrip())
    title_line = re.match(r"(# [^\n]+\n)", w_body.lstrip())
    rest = w_body.lstrip()[len(title_line.group(1)):] if title_line else w_body
    head = title_line.group(1) if title_line else ""
    return f"---\n{front}\n---\n{head}\n" + ("\n\n".join(house) + "\n\n" if house else "") + rest.lstrip()


def bump(v):
    a, b, c = semver(v)
    return f"{a}.{b}.{c + 1}" if a >= 1 else "1.0.0"


def apply(repo, decisions, copies_by_name):
    changed = []
    for d in decisions:
        group = copies_by_name[d["skill"]]
        canon = next((c for c in group if c["kind"] == "canonical"), None)
        if d["action"] == "take-account" and canon:
            winner = next(c for c in group if str(c["path"]) == d["winner_path"])
            new_v = bump(max(canon["version"] or "0.0.0", winner["version"] or "0.0.0", key=semver))
            canon["path"].write_text(merge_into_canonical(canon["text"], winner["text"], new_v))
            changed.append((d["skill"], new_v))
        elif d["action"] in ("add", "bundled-only"):
            src = pathlib.Path(d["winner_path"]).parent
            dest = repo / d["skill"]
            if dest.exists():
                continue
            subprocess.run(["cp", "-r", str(src), str(dest)], check=True)
            md = dest / "SKILL.md"
            front, body = split_frontmatter(md.read_text())
            if not field(front, "version"):
                md.write_text(f"---\n{front}\nversion: 1.0.0\n---\n{body}" if front else md.read_text())
            changed.append((d["skill"], field(split_frontmatter(md.read_text())[0], "version")))
    # Point old skill names at their current names in canonical files only.
    for p in repo.glob("*/SKILL.md"):
        if p.parts[-2] in ("plugins", "synced", "archive", ".trash"):
            continue
        t = p.read_text()
        n = t
        for old, new in RENAMES.items():
            n = re.sub(rf"(?<![\w-])/{old}(?![\w-])", f"/{new}", n)
            n = re.sub(rf"`{old}`", f"`{new}`", n)
        if n != t:
            p.write_text(n)
            changed.append((p.parent.name + " (renamed refs)", None))
    return changed


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=pathlib.Path(__file__).resolve().parents[1], type=pathlib.Path)
    ap.add_argument("--account-dir", action="append", default=[], type=pathlib.Path,
                    help="Another account skills snapshot (folder holding <id>/manifest.json)")
    ap.add_argument("--report", default="reconcile-report.md", type=pathlib.Path)
    ap.add_argument("--write", action="store_true", help="Apply decisions to canonical folders")
    a = ap.parse_args()

    copies = gather(a.repo, a.account_dir)
    by_name = {}
    for c in copies:
        by_name.setdefault(RENAMES.get(c["name"], c["name"]), []).append(c)
    decisions = [decide(a.repo, n, g) for n, g in sorted(by_name.items())]

    counts = {}
    for d in decisions:
        counts[d["action"]] = counts.get(d["action"], 0) + 1
    lines = ["# Skill reconcile report", "", f"Generated {dt.datetime.now().isoformat(timespec='seconds')}", "",
             "| Action | Count |", "|---|---|"] + [f"| {k} | {v} |" for k, v in sorted(counts.items())]
    lines += ["", "| Skill | Action | Winner | Copies | Note |", "|---|---|---|---|---|"]
    for d in decisions:
        if d["action"] != "in-sync":
            lines.append(f"| {d['skill']} | {d['action']} | {d.get('winner','')} | {d['copies']} | {d['note']} |")
    a.report.write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:6 + len(counts)]))
    print(f"\nReport: {a.report}")

    if a.write:
        changed = apply(a.repo, decisions, by_name)
        print(f"\nWrote {len(changed)} change(s). Conflicts left untouched: {counts.get('conflict', 0)}.")
        print("Next: register new skills, bump plugin versions, then run scripts/release_sync.py --write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
