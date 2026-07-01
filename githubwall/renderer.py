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
}


def _esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


class Renderer:
    def __init__(self, theme="dark"):
        self.t = get_theme(theme)
        self.W = 1200
        self.PAD = 60
        self.INNER = self.W - self.PAD * 2

    def _wrap(self, content, h):
        t = self.t
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.W}" height="{h}" viewBox="0 0 {self.W} {h}">'
            f'<defs>'
            f'<linearGradient id="accent-grad" x1="0%" y1="0%" x2="100%" y2="0%">'
            f'<stop offset="0%" style="stop-color:{t["gradient_start"]};stop-opacity:1"/>'
            f'<stop offset="100%" style="stop-color:{t["gradient_end"]};stop-opacity:1"/>'
            f'</linearGradient>'
            f'</defs>'
            f'<rect width="{self.W}" height="{h}" rx="14" fill="{t["bg_card"]}"/>'
            f'{content}'
            f'</svg>'
        )

    def _title(self, y, text):
        return (
            f'<text x="{self.PAD}" y="{y}" fill="{self.t["text"]}" '
            f'font-size="20" font-weight="700" '
            f'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif">'
            f'{_esc(text)}</text>'
        )

    def _label(self, x, y, text, size=14, color=None, bold=False, anchor="start"):
        c = color or self.t["text_muted"]
        fw = "bold" if bold else "normal"
        return (
            f'<text x="{x}" y="{y}" fill="{c}" font-size="{size}" '
            f'font-weight="{fw}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" '
            f'text-anchor="{anchor}">{_esc(text)}</text>'
        )

    def _card(self, x, y, w, h):
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{self.t["bg"]}" opacity="0.5"/>'

    def _accent_line(self, x, y, w):
        return f'<rect x="{x}" y="{y}" width="{w}" height="3" rx="1.5" fill="url(#accent-grad)"/>'

    # ── Languages ──────────────────────────────────────────
    def render_languages(self, data):
        if not data:
            return self._wrap(self._title(40, "Most Used Languages") + "\n" + self._label(self.PAD, 70, "No data available", 15, self.t["text_muted"]), 100)

        total = sum(data.values())
        sorted_langs = sorted(data.items(), key=lambda x: x[1], reverse=True)
        items = []
        for lang, bc in sorted_langs[:8]:
            pct = round((bc / total) * 100, 1)
            if pct < 1:
                continue
            items.append((lang, pct, LANG_COLORS.get(lang, "#ccc")))

        bar_h = 28
        gap = 16
        title_y = 32
        accent_y = title_y + 12
        start_y = accent_y + 24
        chart_h = len(items) * (bar_h + gap) - gap
        total_h = start_y + chart_h + 40

        content = self._title(title_y, "Most Used Languages") + "\n"
        content += self._accent_line(self.PAD, accent_y, 140) + "\n"
        content += self._card(self.PAD - 8, start_y - 16, self.INNER + 16, chart_h + 32) + "\n"

        bar_w = self.INNER - 200
        y = start_y
        for lang, pct, color in items:
            w = max(8, int(bar_w * pct / 100))
            content += f'<rect x="{self.PAD + 4}" y="{y}" width="{w}" height="{bar_h}" rx="6" fill="{color}" opacity="0.9"/>\n'
            content += self._label(self.PAD + w + 18, y + bar_h - 8, lang, 15, self.t["text"], bold=True) + "\n"
            content += self._label(self.W - self.PAD, y + bar_h - 8, f"{pct}%", 15, self.t["text_muted"], anchor="end") + "\n"
            y += bar_h + gap

        return self._wrap(content, total_h)

    # ── Stats ──────────────────────────────────────────────
    def render_stats(self, stats):
        if not stats:
            return self._wrap(self._title(40, "GitHub Statistics") + "\n" + self._label(self.PAD, 70, "No stats available", 15, self.t["text_muted"]), 100)

        metrics = [
            ("Repos", str(stats["public_repos"]), self.t["accent"]),
            ("Stars", str(stats["total_stars"]), self.t["accent_orange"]),
            ("Forks", str(stats["total_forks"]), self.t["accent_purple"]),
            ("Followers", str(stats["followers"]), self.t["accent_green"]),
        ]

        title_y = 32
        accent_y = title_y + 12
        card_gap = 20
        card_w = (self.INNER - card_gap * 3) // 4
        card_h = 110
        cy = accent_y + 28

        content = self._title(title_y, "GitHub Statistics") + "\n"
        content += self._accent_line(self.PAD, accent_y, 140) + "\n"

        for i, (label, value, color) in enumerate(metrics):
            x = self.PAD + i * (card_w + card_gap)
            content += self._card(x, cy, card_w, card_h) + "\n"
            content += self._label(x + card_w // 2, cy + 50, value, 40, color, bold=True, anchor="middle") + "\n"
            content += self._label(x + card_w // 2, cy + 82, label, 14, self.t["text_muted"], anchor="middle") + "\n"

        total_h = cy + card_h + 30
        return self._wrap(content, total_h)

    # ── Streak ─────────────────────────────────────────────
    def _plural(self, n, word):
        return f"{n} {word}" + ("s" if n != 1 else "")

    def render_streak(self, streak):
        if not streak:
            return self._wrap(self._title(40, "Contribution Streak") + "\n" + self._label(self.PAD, 70, "No streak data", 15, self.t["text_muted"]), 100)

        t = self.t
        title_y = 32
        accent_y = title_y + 12
        card_gap = 20
        card_w = (self.INNER - card_gap * 2) // 3
        card_h = 110
        cy = accent_y + 28

        content = self._title(title_y, "Contribution Streak") + "\n"
        content += self._accent_line(self.PAD, accent_y, 140) + "\n"

        metrics = [
            ("Longest Streak", self._plural(streak["longest_streak"], "day"), t["accent_orange"]),
            ("Current Streak", self._plural(streak["current_streak"], "day"), t["accent_green"]),
            ("Contributions", str(streak["total_contributions"]), t["accent_purple"]),
        ]

        for i, (label, value, color) in enumerate(metrics):
            x = self.PAD + i * (card_w + card_gap)
            content += self._card(x, cy, card_w, card_h) + "\n"
            content += self._label(x + card_w // 2, cy + 50, value, 32, color, bold=True, anchor="middle") + "\n"
            content += self._label(x + card_w // 2, cy + 82, label, 14, t["text_muted"], anchor="middle") + "\n"

        total_h = cy + card_h + 30
        return self._wrap(content, total_h)

    # ── Top Repos ──────────────────────────────────────────
    def render_top_repos(self, repos):
        if not repos:
            return self._wrap(self._title(40, "Top Repositories") + "\n" + self._label(self.PAD, 70, "No repos to display", 15, self.t["text_muted"]), 100)

        cols = 3
        card_gap = 20
        card_w = (self.INNER - card_gap * (cols - 1)) // cols
        card_h = 120
        title_y = 32
        accent_y = title_y + 12
        cy = accent_y + 28
        rows = (len(repos) + cols - 1) // cols
        total_h = cy + rows * (card_h + card_gap) + 12

        content = self._title(title_y, "Top Repositories") + "\n"
        content += self._accent_line(self.PAD, accent_y, 140) + "\n"

        for i, repo in enumerate(repos):
            row = i // cols
            col = i % cols
            x = self.PAD + col * (card_w + card_gap)
            y = cy + row * (card_h + card_gap)

            content += self._card(x, y, card_w, card_h) + "\n"
            content += self._label(x + 18, y + 30, repo["name"], 18, self.t["accent"], bold=True) + "\n"
            desc = repo["description"][:50] + ("..." if len(repo["description"]) > 50 else "")
            if desc:
                content += self._label(x + 18, y + 54, desc, 13, self.t["text_muted"]) + "\n"
            content += self._label(x + 18, y + 88, "\u2605 " + str(repo["stars"]), 14, self.t["accent_orange"]) + "\n"
            if repo["language"]:
                lc = LANG_COLORS.get(repo["language"], "#ccc")
                content += f'<circle cx="{x + 90}" cy="{y + 83}" r="6" fill="{lc}"/>\n'
                content += self._label(x + 102, y + 88, repo["language"], 13, self.t["text_muted"]) + "\n"

        return self._wrap(content, total_h)

    # ── Activity ───────────────────────────────────────────
    def render_activity(self, events):
        # Filter out empty PushEvents
        events = [e for e in events if not (e["type"] == "PushEvent" and e.get("count", 0) == 0)]
        if not events:
            return self._wrap(self._title(40, "Recent Activity") + "\n" + self._label(self.PAD, 70, "No recent activity", 15, self.t["text_muted"]), 100)

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

        row_h = 60
        title_y = 32
        accent_y = title_y + 12
        cy = accent_y + 28
        total_h = cy + len(events) * row_h + 16

        content = self._title(title_y, "Recent Activity") + "\n"
        content += self._accent_line(self.PAD, accent_y, 140) + "\n"

        for i, ev in enumerate(events):
            y = cy + i * row_h
            dot_color = colors.get(ev["type"], self.t["text_muted"])
            repo_name = ev["repo"].split("/")[-1] if "/" in ev["repo"] else ev["repo"]
            label = labels.get(ev["type"], ev["type"])

            if ev["type"] == "PushEvent":
                detail = f"{ev.get('count', 0)} commit" + ("s" if ev.get("count", 0) != 1 else "")
                msg = ev.get("message", "")[:50]
                if msg:
                    detail += f" - {msg}"
            elif ev["type"] == "IssuesEvent":
                detail = f"{ev.get('action', '')} issue"
                title = ev.get("title", "")[:50]
                if title:
                    detail += f" - {title}"
            elif ev["type"] == "CreateEvent":
                detail = f"{ev.get('ref_type', '')} {ev.get('ref', '')}"
            elif ev["type"] == "WatchEvent":
                detail = "starred this repo"
            elif ev["type"] == "ForkEvent":
                detail = f"forked {ev.get('forked_repo', '').split('/')[-1]}"
            elif ev["type"] == "PullRequestEvent":
                detail = f"{ev.get('action', '')} PR"
                title = ev.get("title", "")[:50]
                if title:
                    detail += f" - {title}"
            elif ev["type"] == "ReleaseEvent":
                detail = f"released {ev.get('tag', '')}"
            else:
                detail = repo_name

            # row
            content += f'<rect x="{self.PAD}" y="{y}" width="{self.INNER}" height="{row_h - 6}" rx="10" fill="{self.t["bg"]}" opacity="0.5"/>\n'
            content += f'<circle cx="{self.PAD + 16}" cy="{y + (row_h - 6) // 2}" r="6" fill="{dot_color}"/>\n'
            content += self._label(self.PAD + 34, y + 24, f"{label} in {repo_name}", 15, self.t["text"], bold=True) + "\n"
            content += self._label(self.PAD + 34, y + 44, detail, 13, self.t["text_muted"]) + "\n"

        return self._wrap(content, total_h)

    # ── Combined ───────────────────────────────────────────
    def render_combined(self, svgs):
        import re
        gap = 24
        total_h = 0
        heights = []
        for svg in svgs:
            m = re.search(r'height="(\d+)"', svg.split("\n")[0])
            h = int(m.group(1)) if m else 100
            heights.append(h)
            total_h += h + gap

        combined = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.W}" height="{total_h}" viewBox="0 0 {self.W} {total_h}">'
            f'<defs>'
            f'<linearGradient id="accent-grad" x1="0%" y1="0%" x2="100%" y2="0%">'
            f'<stop offset="0%" style="stop-color:{self.t["gradient_start"]};stop-opacity:1"/>'
            f'<stop offset="100%" style="stop-color:{self.t["gradient_end"]};stop-opacity:1"/>'
            f'</linearGradient>'
            f'</defs>'
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
                if "linearGradient" in s or "<stop" in s:
                    continue
                clean.append(line)
            h = heights.pop(0)
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
