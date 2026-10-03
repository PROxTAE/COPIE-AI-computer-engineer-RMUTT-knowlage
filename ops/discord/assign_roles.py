#!/usr/bin/env python
"""Directly assign Discord roles to the 8 team members based on ops/discord/config.yaml.

Usage:
    python assign_roles.py --dry-run
    python assign_roles.py
    python assign_roles.py --remove-old
    python assign_roles.py --welcome
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import yaml

from discord_api import Discord, DiscordError, load_dotenv

HERE = Path(__file__).resolve().parent
IDS_FILE = HERE / "out" / "discord-ids.json"
OLD_ROLES = [
    "01-web", "02-api", "03-agent", "04-external-data",
    "05-data-integration", "06-risk-knowledge", "07-decision-engine", "08-recommendation"
]


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="dry run without modifying roles")
    ap.add_argument("--welcome", action="store_true", help="post welcome announcement in each member's workstream channel")
    ap.add_argument("--remove-old", action="store_true", help="remove old project (SafetyTravel) workstream roles")
    args = ap.parse_args()

    load_dotenv()
    api = Discord()
    cfg = yaml.safe_load((HERE / "config.yaml").read_text(encoding="utf-8"))
    ids = json.loads(IDS_FILE.read_text(encoding="utf-8"))
    gid = ids["guild_id"]
    roles = ids["role_ids"]
    chans = ids["channel_ids"]

    workstreams = cfg["workstreams"]
    lead_role_id = roles.get(cfg["lead_role"]["name"])

    print(f"Assigning roles for guild: {gid} (dry-run: {args.dry_run})\n")

    guild_roles = api.roles(gid)
    all_guild_roles = {r["id"]: r["name"] for r in guild_roles}
    old_role_ids = {r["id"]: r["name"] for r in guild_roles if r["name"] in OLD_ROLES}

    for ws in workstreams:
        person = ws["person"]
        name = ws.get("name", "")
        student_id = ws.get("student_id", "")
        discord_id = ws.get("discord_id")
        github = ws.get("github", "")
        role_key = ws["key"]
        role_id = roles.get(role_key)

        if not discord_id:
            print(f"[-] {person} ({name}): No discord_id configured")
            continue

        if not role_id:
            print(f"[-] {person} ({name}): Role '{role_key}' not found in discord-ids.json")
            continue

        print(f"\n==========================================")
        print(f"[{person}] {name} ({student_id})")
        print(f"    GitHub:      @{github}")
        print(f"    Discord ID:  {discord_id}")
        print(f"    Target Role: @{role_key} ({role_id})")

        # Check guild member
        try:
            member = api.get(f"/guilds/{gid}/members/{discord_id}")
        except DiscordError as e:
            print(f"    [!] Error fetching member: {e}")
            continue

        user = member["user"]
        username = user.get("username", "")
        global_name = user.get("global_name", "")
        curr_role_ids = member.get("roles", [])
        print(f"    Username:    {username} (display: {global_name or username})")
        print(f"    Current:     {[all_guild_roles.get(rid, rid) for rid in curr_role_ids]}")

        target_roles = [role_id]
        if person == "P1" and lead_role_id:
            target_roles.append(lead_role_id)

        for target_rid in target_roles:
            target_rname = all_guild_roles.get(target_rid, target_rid)
            if target_rid in curr_role_ids:
                print(f"    [=] Role '{target_rname}' already assigned.")
            else:
                print(f"    [+] Adding role '{target_rname}' ({target_rid})...")
                if not args.dry_run:
                    try:
                        api.put(f"/guilds/{gid}/members/{discord_id}/roles/{target_rid}",
                                reason=f"COPIE: Assign {person} ({ws['modules']})")
                        print(f"        -> Added!")
                    except DiscordError as err:
                        print(f"        -> Failed: {err}")
                    time.sleep(0.5)

        # Remove old roles if requested
        if args.remove_old:
            for old_rid, old_rname in old_role_ids.items():
                if old_rid in curr_role_ids:
                    print(f"    [-] Removing old project role '{old_rname}'...")
                    if not args.dry_run:
                        try:
                            api.delete(f"/guilds/{gid}/members/{discord_id}/roles/{old_rid}",
                                       reason="COPIE: Remove old project role")
                            print(f"        -> Removed!")
                        except DiscordError as err:
                            print(f"        -> Failed: {err}")
                        time.sleep(0.5)

        # Optional welcome message
        if args.welcome and not args.dry_run:
            ch_id = chans.get(role_key)
            if ch_id:
                try:
                    welcome_text = (
                        f"👋 สวัสดี <@{discord_id}> ({name})!\n"
                        f"ห้องนี้คือห้องประจำโมดูล **{', '.join(ws['modules'])}** ({person}) ของคุณ\n"
                        f"📌 เอกสารแผนงานและข้อกำหนดทั้งหมดถูกปักหมุดไว้ที่ด้านบนแล้ว สามารถเริ่มงานจาก branch `{ws['branches'][0]}` ได้เลยครับ"
                    )
                    api.send_message(ch_id, {"content": welcome_text, "allowed_mentions": {"users": [discord_id]}})
                    print(f"    [+] Sent welcome message in #{role_key}")
                except DiscordError as err:
                    print(f"    [!] Failed to send welcome in #{role_key}: {err}")

    print("\nRole assignment complete!")


if __name__ == "__main__":
    main()
