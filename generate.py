#!/usr/bin/env python3
"""GitHubWall - Personal GitHub README Stats Generator.

Usage:
    python generate.py                          # Uses config.json
    python generate.py --username your-username # Override username
    python generate.py --theme spotify          # Use Spotify theme
    python generate.py --token ghp_xxx          # Provide API token
    python generate.py --all                    # Generate all banners
    python generate.py --combined               # Generate combined wall
"""

import argparse
import json
import os
import sys
sys.dont_write_bytecode = True

from githubwall.api import GitHubAPI
from githubwall.renderer import Renderer
from githubwall.stats import compute_streak
from githubwall.themes import THEMES


def load_config(path="config.json"):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def main():
    parser = argparse.ArgumentParser(description="GitHubWall - README Stats Generator")
    parser.add_argument("--username", help="GitHub username")
    parser.add_argument("--token", help="GitHub personal access token", default="")
    parser.add_argument("--theme", choices=list(THEMES.keys()), default="dark", help="Color theme")
    parser.add_argument("--output", default="output", help="Output directory")
    parser.add_argument("--combined", action="store_true", help="Generate combined wall SVG")
    parser.add_argument("--all", action="store_true", default=True, help="Generate all banners")
    parser.add_argument("--no-cache", action="store_true", help="Skip caching")
    args = parser.parse_args()

    config = load_config()

    username = args.username or config.get("username") or os.environ.get("GITHUB_USERNAME")
    token = args.token or config.get("token") or os.environ.get("GITHUB_TOKEN") or ""
    theme_name = args.theme or config.get("theme", "dark")
    output_dir = os.path.abspath(args.output or config.get("output_dir", "output"))
    do_combined = args.combined or config.get("combined", True)

    if not username:
        print("[!] No GitHub username provided.")
        print("    Set --username, config.json 'username', or GITHUB_USERNAME env var.")
        sys.exit(1)

    print(f"[*] GitHubWall v1.0")
    print(f"[*] Username: {username}")
    print(f"[*] Theme: {theme_name}")
    print(f"[*] Output: {output_dir}")
    print(f"[*] Token: {'Provided' if token else 'Not provided (60 req/hr limit)'}")
    print()

    api = GitHubAPI(username, token)
    renderer = Renderer(theme_name)

    try:
        user = api.get_user()
        if not user:
            print(f"[X] User '{username}' not found.")
            sys.exit(1)
        print(f"[+] User found: {user.get('name', username)} ({user.get('public_repos', 0)} repos)")
    except Exception as e:
        print(f"[X] API error: {e}")
        sys.exit(1)

    generated = []

    # --- Languages ---
    if config.get("show_languages", True):
        print("[*] Fetching language data (this may take a moment)...")
        try:
            langs = api.get_combined_languages()
            if langs:
                svg = renderer.render_languages(langs)
                path = renderer.save_svg(svg, "languages.svg", output_dir)
                generated.append(("languages.svg", path))
                print(f"  [+] languages.svg ({len(langs)} languages)")
            else:
                print("  [-] No language data")
        except Exception as e:
            print(f"  [X] Languages failed: {e}")

    # --- Stats ---
    if config.get("show_stats", True):
        print("[*] Fetching statistics...")
        try:
            stats = api.get_total_stats()
            svg = renderer.render_stats(stats)
            path = renderer.save_svg(svg, "stats.svg", output_dir)
            generated.append(("stats.svg", path))
            print(f"  [+] stats.svg ({stats['total_stars']} stars, {stats['followers']} followers)")
        except Exception as e:
            print(f"  [X] Stats failed: {e}")

    # --- Streak ---
    if config.get("show_streak", True):
        print("[*] Computing contribution streak...")
        try:
            events = api.get_events()
            streak = compute_streak(events)
            svg = renderer.render_streak(streak)
            path = renderer.save_svg(svg, "streak.svg", output_dir)
            generated.append(("streak.svg", path))
            print(f"  [+] streak.svg (longest: {streak['longest_streak']}d, current: {streak['current_streak']}d)")
        except Exception as e:
            print(f"  [X] Streak failed: {e}")

    # --- Top Repos ---
    if config.get("show_top_repos", True):
        print("[*] Fetching top repositories...")
        try:
            max_repos = config.get("max_repos", 6)
            repos = api.get_top_repos(max_repos)
            if repos:
                svg = renderer.render_top_repos(repos)
                path = renderer.save_svg(svg, "top-repos.svg", output_dir)
                generated.append(("top-repos.svg", path))
                print(f"  [+] top-repos.svg ({len(repos)} repos)")
            else:
                print("  [-] No repositories")
        except Exception as e:
            print(f"  [X] Top repos failed: {e}")

    # --- Activity ---
    if config.get("show_activity", True):
        print("[*] Fetching recent activity...")
        try:
            max_activity = config.get("max_activity", 5)
            events = api.get_recent_activity(max_activity)
            if events:
                svg = renderer.render_activity(events)
                path = renderer.save_svg(svg, "activity.svg", output_dir)
                generated.append(("activity.svg", path))
                print(f"  [+] activity.svg ({len(events)} events)")
            else:
                print("  [-] No recent activity")
        except Exception as e:
            print(f"  [X] Activity failed: {e}")

    # --- Combined ---
    if do_combined and generated:
        print("[*] Generating combined wall...")
        try:
            svgs = []
            for name, path in generated:
                with open(path) as f:
                    svgs.append(f.read())
            combined = renderer.render_combined(svgs)
            path = renderer.save_svg(combined, "combined.svg", output_dir)
            generated.append(("combined.svg", path))
            print(f"  [+] combined.svg")
        except Exception as e:
            print(f"  [X] Combined failed: {e}")

    print()
    print(f"[+] Generated {len(generated)} file(s) in {output_dir}:")
    for name, path in generated:
        size = os.path.getsize(path)
        print(f"     {name} ({size} bytes)")
    print()
    print("[*] To use in your README:")
    print(f'    <img src="output/combined.svg" width="100%" alt="GitHub Stats">')
    print(f'    <img src="output/stats.svg" width="49%" alt="Stats">')
    print(f'    <img src="output/languages.svg" width="49%" alt="Languages">')


if __name__ == "__main__":
    main()
