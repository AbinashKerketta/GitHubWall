import os
from .themes import get_theme

LANG_COLORS = {
    "Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6",
    "Java": "#b07219", "Go": "#00ADD8", "Rust": "#dea584",
    "C": "#555555", "C++": "#f34b7d", "C#": "#178600",
    "Ruby": "#701516", "PHP": "#4F5D95", "Shell": "#89e051",
    "Swift": "#ffac45", "Kotlin": "#A97BFF", "Dart": "#00B4AB",
    "Scala": "#c22d40", "Lua": "#000080", "Perl": "#0298c3",
    "Haskell": "#5e5086", "R": "#198CE7", "HTML": "#e34c26",
    "CSS": "#563d7c", "Vue": "#41b883", "Svelte": "#ff3e00",
    "PowerShell": "#012456", "Batchfile": "#C1F12E", "Dockerfile": "#384d54",
    "Makefile": "#427819", "Markdown": "#083fa1", "TeX": "#3D6117",
    "Assembly": "#6E4C13", "Elixir": "#6e4a7e", "Clojure": "#db5855",
    "Objective-C": "#438eff", "Solidity": "#AA6746", "Terraform": "#623ce4",
    "Vim Script": "#199f4b", "Jupyter Notebook": "#DA5B0B",
}


class Renderer:
    def __init__(self, theme="dark"):
        self.t = get_theme(theme)
        self.W = 800
        self.PAD = 32

    def _wrap(self, content, h):
        t = self.t
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.W}" height="{h}" viewBox="0 0 {self.W} {h}">'
            f'<defs>'
            f'<filter id="sh" x="-4%" y="-4%" width="108%" height="108%">'
            f'<feDropShadow dx="0" dy="1" stdDeviation="3" flood-color="#000" flood-opacity="0.25"/>'
            f'</filter>'
            f'</defs>'
            f'<rect width="{self.W}" height="{h}" rx="10" fill="{t["bg_card"]}"/>'
            f'{content}'
            f'</svg>'
        )

    def _t(self, x, y, text, size=13, color=None, bold=False, anchor="start"):
        c = color or self.t["text"]
        fw = "bold" if bold else "normal"
        safe = str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return (
            f'<text x="{x}" y="{y}" fill="{c}" font-size="{size}" '
            f'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" '
            f'font-weight="{fw}" text-anchor="{anchor}">{safe}</text>'
        )

    # ── Languages ──────────────────────────────────────────
    def render_languages(self, data):
        if not data:
            return self._wrap(self._t(30, 40, "No language data", 14, self.t["text_muted"]), 80)

        total = sum(data.values())
        sorted_langs = sorted(data.items(), key=lambda x: x[1], reverse=True)
        items = []
        for lang, bc in sorted_langs[:8]:
            pct = round((bc / total) * 100, 1)
            if pct < 1:
                continue
            items.append((lang, pct, LANG_COLORS.get(lang, "#ccc")))

        bar_h = 18
        gap = 10
        title_h = 28
        pad_top = 20
        pad_bot = 16
        chart_h = len(items) * (bar_h + gap) - gap
        total_h = pad_top + title_h + 10 + chart_h + pad_bot

        title = self._t(self.PAD, pad_top + 18, "Most Used Languages", 15, self.t["text"], bold=True)
        bars = ""
        y = pad_top + title_h + 10
        bar_w = self.W - self.PAD * 2 - 120
        for lang, pct, color in items:
            w = max(4, int(bar_w * pct / 100))
            # bar
            bars += f'<rect x="{self.PAD}" y="{y}" width="{w}" height="{bar_h}" rx="4" fill="{color}" opacity="0.85"/>\n'
            # label (left, after bar)
            lx = self.PAD + w + 10
            bars += self._t(lx, y + bar_h - 4, lang, 12, self.t["text"]) + "\n"
            # percentage (right)
            bars += self._t(self.W - self.PAD, y + bar_h - 4, f"{pct}%", 12, self.t["text_muted"], anchor="end") + "\n"
            y += bar_h + gap

        return self._wrap(title + "\n" + bars, total_h)

    # ── Stats ──────────────────────────────────────────────
    def render_stats(self, stats):
        if not stats:
            return self._wrap(self._t(30, 40, "No stats available", 14, self.t["text_muted"]), 80)

        metrics = [
            ("Repositories", str(stats["public_repos"]), self.t["accent"]),
            ("Stars Earned", str(stats["total_stars"]), self.t["accent_orange"]),
            ("Total Forks", str(stats["total_forks"]), self.t["accent_purple"]),
            ("Followers", str(stats["followers"]), self.t["accent_green"]),
        ]

        card_gap = 12
        card_w = (self.W - self.PAD * 2 - card_gap * 3) // 4
        card_h = 80
        title_h = 28
        pad_top = 20
        total_h = pad_top + title_h + 14 + card_h + 20

        title = self._t(self.PAD, pad_top + 18, "GitHub Statistics", 15, self.t["text"], bold=True)
        boxes = ""
        cy = pad_top + title_h + 14
        for i, (label, value, color) in enumerate(metrics):
            x = self.PAD + i * (card_w + card_gap)
            # card background
            boxes += f'<rect x="{x}" y="{cy}" width="{card_w}" height="{card_h}" rx="8" fill="{self.t["bg"]}" opacity="0.5"/>\n'
            # value
            boxes += self._t(x + card_w // 2, cy + 38, value, 28, color, bold=True, anchor="middle") + "\n"
            # label
            boxes += self._t(x + card_w // 2, cy + 62, label, 11, self.t["text_muted"], anchor="middle") + "\n"

        return self._wrap(title + "\n" + boxes, total_h)

    # ── Streak ─────────────────────────────────────────────
    def render_streak(self, streak):
        if not streak:
            return self._wrap(self._t(30, 40, "No streak data", 14, self.t["text_muted"]), 80)

        t = self.t
        card_gap = 12
        card_w = (self.W - self.PAD * 2 - card_gap * 2) // 3
        card_h = 80
        title_h = 28
        pad_top = 20
        total_h = pad_top + title_h + 14 + card_h + 20

        title = self._t(self.PAD, pad_top + 18, "Contribution Streak", 15, t["text"], bold=True)
        metrics = [
            ("Longest Streak", f"{streak['longest_streak']} days", t["accent_orange"]),
            ("Current Streak", f"{streak['current_streak']} days", t["accent_green"]),
            ("Total Contributions", f"{streak['total_contributions']:,}", t["accent_purple"]),
        ]

        boxes = ""
        cy = pad_top + title_h + 14
        for i, (label, value, color) in enumerate(metrics):
            x = self.PAD + i * (card_w + card_gap)
            boxes += f'<rect x="{x}" y="{cy}" width="{card_w}" height="{card_h}" rx="8" fill="{t["bg"]}" opacity="0.5"/>\n'
            boxes += self._t(x + card_w // 2, cy + 38, value, 24, color, bold=True, anchor="middle") + "\n"
            boxes += self._t(x + card_w // 2, cy + 62, label, 11, t["text_muted"], anchor="middle") + "\n"

        return self._wrap(title + "\n" + boxes, total_h)

    # ── Top Repos ──────────────────────────────────────────
    def render_top_repos(self, repos):
        if not repos:
            return self._wrap(self._t(30, 40, "No repos to display", 14, self.t["text_muted"]), 80)

        cols = 2
        card_gap = 12
        card_w = (self.W - self.PAD * 2 - card_gap) // cols
        card_h = 90
        title_h = 28
        pad_top = 20
        rows = (len(repos) + cols - 1) // cols
        total_h = pad_top + title_h + 14 + rows * (card_h + card_gap) + 8

        title = self._t(self.PAD, pad_top + 18, "Top Repositories", 15, self.t["text"], bold=True)
        cards = ""
        cy = pad_top + title_h + 14
        for i, repo in enumerate(repos):
            row = i // cols
            col = i % cols
            x = self.PAD + col * (card_w + card_gap)
            y = cy + row * (card_h + card_gap)

            cards += f'<rect x="{x}" y="{y}" width="{card_w}" height="{card_h}" rx="8" fill="{self.t["bg"]}" opacity="0.5"/>\n'
            # name
            cards += self._t(x + 16, y + 26, repo["name"], 14, self.t["accent"], bold=True) + "\n"
            # description (truncated)
            desc = repo["description"][:60] + ("..." if len(repo["description"]) > 60 else "")
            if desc:
                cards += self._t(x + 16, y + 46, desc, 11, self.t["text_muted"]) + "\n"
            # stars + language
            cards += self._t(x + 16, y + 72, f"\u2605 {repo['stars']}", 12, self.t["accent_orange"]) + "\n"
            if repo["language"]:
                lc = LANG_COLORS.get(repo["language"], "#ccc")
                cards += f'<circle cx="{x + 90}" cy="{y + 67}" r="5" fill="{lc}"/>\n'
                cards += self._t(x + 100, y + 72, repo["language"], 11, self.t["text_muted"]) + "\n"

        return self._wrap(title + "\n" + cards, total_h)

    # ── Activity ───────────────────────────────────────────
    def render_activity(self, events):
        if not events:
            return self._wrap(self._t(30, 40, "No recent activity", 14, self.t["text_muted"]), 80)

        labels = {
            "PushEvent": "Pushed", "IssuesEvent": "Opened issue",
            "CreateEvent": "Created", "WatchEvent": "Starred",
            "ForkEvent": "Forked", "PullRequestEvent": "Opened PR",
            "IssueCommentEvent": "Commented", "ReleaseEvent": "Released",
        }
        colors = {
            "PushEvent": self.t["accent_green"], "IssuesEvent": self.t["accent_red"],
            "CreateEvent": self.t["accent_purple"], "WatchEvent": self.t["accent_orange"],
            "ForkEvent": self.t["accent"], "PullRequestEvent": self.t["accent_green"],
            "IssueCommentEvent": self.t["accent_purple"], "ReleaseEvent": self.t["accent_orange"],
        }

        row_h = 44
        title_h = 28
        pad_top = 20
        total_h = pad_top + title_h + 14 + len(events) * row_h + 8

        title = self._t(self.PAD, pad_top + 18, "Recent Activity", 15, self.t["text"], bold=True)
        rows = ""
        cy = pad_top + title_h + 14
        for i, ev in enumerate(events):
            y = cy + i * row_h
            dot_color = colors.get(ev["type"], self.t["text_muted"])
            repo_name = ev["repo"].split("/")[-1] if "/" in ev["repo"] else ev["repo"]
            label = labels.get(ev["type"], ev["type"])

            if ev["type"] == "PushEvent":
                detail = f"{ev.get('count', 0)} commits" + (f" - {ev.get('message', '')[:40]}" if ev.get("message") else "")
            elif ev["type"] == "IssuesEvent":
                detail = f"{ev.get('action', '')} - {ev.get('title', '')[:40]}"
            elif ev["type"] == "CreateEvent":
                detail = f"{ev.get('ref_type', '')} {ev.get('ref', '')}"
            elif ev["type"] == "WatchEvent":
                detail = repo_name
            elif ev["type"] == "ForkEvent":
                detail = ev.get("forked_repo", "")
            elif ev["type"] == "PullRequestEvent":
                detail = f"{ev.get('action', '')} - {ev.get('title', '')[:40]}"
            elif ev["type"] == "ReleaseEvent":
                detail = ev.get("tag", "")
            else:
                detail = repo_name

            # row background (subtle hover)
            rows += f'<rect x="{self.PAD}" y="{y}" width="{self.W - self.PAD * 2}" height="{row_h - 4}" rx="6" fill="{self.t["bg"]}" opacity="0.4"/>\n'
            # dot
            rows += f'<circle cx="{self.PAD + 10}" cy="{y + (row_h - 4) // 2}" r="4" fill="{dot_color}"/>\n'
            # label
            rows += self._t(self.PAD + 24, y + 18, f"{label} in {repo_name}", 12, self.t["text"]) + "\n"
            # detail
            rows += self._t(self.PAD + 24, y + 34, detail, 11, self.t["text_muted"]) + "\n"

        return self._wrap(title + "\n" + rows, total_h)

    # ── Combined ───────────────────────────────────────────
    def render_combined(self, svgs):
        import re
        gap = 16
        total_h = 0
        for svg in svgs:
            m = re.search(r'height="(\d+)"', svg.split("\n")[0])
            if m:
                total_h += int(m.group(1)) + gap

        combined = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.W}" height="{total_h}" viewBox="0 0 {self.W} {total_h}">'
            f'<rect width="{self.W}" height="{total_h}" fill="{self.t["bg"]}"/>'
        )
        y = 0
        for svg in svgs:
            lines = svg.strip().split("\n")
            clean = []
            for line in lines:
                s = line.strip()
                if s.startswith("<svg") or s.startswith("<?xml") or s.endswith("</svg>"):
                    continue
                if "<defs>" in s or "</defs>" in s:
                    continue
                clean.append(line)
            m = re.search(r'height="(\d+)"', lines[0])
            h = int(m.group(1)) if m else 100
            combined += f'<g transform="translate(0,{y})">' + "\n".join(clean) + "</g>\n"
            y += h + gap

        combined += "</svg>"
        return combined

    def save_svg(self, content, filename, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path
