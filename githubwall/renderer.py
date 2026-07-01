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

EVENT_ICONS = {
    "PushEvent": "\u2191",
    "IssuesEvent": "\u25cf",
    "CreateEvent": "\u2728",
    "WatchEvent": "\u2605",
    "ForkEvent": "\u2442",
    "PullRequestEvent": "\u2190",
    "IssueCommentEvent": "\u2709",
    "ReleaseEvent": "\u25b6",
    "DeleteEvent": "\u2716",
    "MemberEvent": "\u2795",
    "PublicEvent": "\u1f30d",
}


class Renderer:
    def __init__(self, theme="dark"):
        self.t = get_theme(theme)
        self.width = 800

    def _svg_wrap(self, content, height):
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{height}" viewBox="0 0 {self.width} {height}">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:{self.t['gradient_start']};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{self.t['gradient_end']};stop-opacity:1" />
    </linearGradient>
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#000" flood-opacity="0.3"/>
    </filter>
  </defs>
  <rect width="{self.width}" height="{height}" rx="12" fill="{self.t['bg_card']}" filter="url(#shadow)"/>
  {content}
</svg>'''

    def _text(self, x, y, text, size=13, color=None, bold=False, anchor="start"):
        c = color or self.t["text"]
        fw = "bold" if bold else "normal"
        return f'<text x="{x}" y="{y}" fill="{c}" font-size="{size}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-weight="{fw}" text-anchor="{anchor}">{self._esc(text)}</text>'

    def _esc(self, s):
        return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

    def _bar(self, x, y, w, h, color, label, pct):
        bar = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{color}"/>'
        label_x = x + w + 10
        pct_x = self.width - 20
        label_text = self._text(label_x, y + h - 3, label, 12, self.t["text"])
        pct_text = self._text(pct_x, y + h - 3, f"{pct}%", 12, self.t["text_muted"], anchor="end")
        return f'{bar}\n{label_text}\n{pct_text}'

    def _badge(self, x, y, text, color, w=80):
        bw = w
        bh = 22
        bx = x
        by = y - bh + 4
        return f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="11" fill="{color}" opacity="0.15"/><text x="{bx + bw//2}" y="{by + 15}" fill="{color}" font-size="11" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-weight="bold" text-anchor="middle">{self._esc(text)}</text>'

    def render_languages(self, lang_data):
        if not lang_data:
            return self._svg_wrap(self._text(20, 40, "No language data available", 14, self.t["text_muted"]), 80)

        total = sum(lang_data.values())
        sorted_langs = sorted(lang_data.items(), key=lambda x: x[1], reverse=True)
        top_langs = sorted_langs[:8]
        others = sorted_langs[8:]
        if others:
            pct_others = sum(v for _, v in others)
            top_langs.append(("Other", pct_others))

        items = []
        for lang, bytes_count in top_langs:
            pct = round((bytes_count / total) * 100, 1)
            if pct < 1:
                continue
            items.append((lang, pct, LANG_COLORS.get(lang, "#ccc")))

        bar_h = 18
        gap = 8
        chart_h = len(items) * (bar_h + gap)
        pad = 30
        total_h = pad + chart_h + 20

        bars_x = 20
        bars_w = self.width - 200
        bars = ""
        y = pad + 5
        for lang, pct, color in items:
            w = max(4, int(bars_w * pct / 100))
            bars += self._bar(bars_x, y, w, bar_h, color, lang, pct) + "\n"
            y += bar_h + gap

        title = self._text(20, 22, "Most Used Languages", 15, self.t["text"], bold=True)
        return self._svg_wrap(f'{title}\n{bars}', total_h)

    def render_stats(self, stats):
        if not stats:
            return self._svg_wrap(self._text(20, 40, "No stats available", 14, self.t["text_muted"]), 80)

        metrics = [
            ("Repositories", str(stats["public_repos"]), self.t["accent"]),
            ("Stars Earned", str(stats["total_stars"]), self.t["accent_orange"]),
            ("Total Forks", str(stats["total_forks"]), self.t["accent_purple"]),
            ("Followers", str(stats["followers"]), self.t["accent_green"]),
        ]

        box_w = (self.width - 60) // 4
        boxes = ""
        for i, (label, value, color) in enumerate(metrics):
            x = 20 + i * (box_w + 10)
            boxes += f'<rect x="{x}" y="50" width="{box_w}" height="70" rx="8" fill="{self.t["bg"]}" opacity="0.6"/>\n'
            boxes += self._text(x + box_w // 2, 80, value, 26, color, bold=True, anchor="middle")
            boxes += "\n"
            boxes += self._text(x + box_w // 2, 105, label, 11, self.t["text_muted"], anchor="middle")
            boxes += "\n"

        title = self._text(20, 30, "GitHub Statistics", 15, self.t["text"], bold=True)
        return self._svg_wrap(f'{title}\n{boxes}', 150)

    def render_streak(self, streak):
        if not streak:
            return self._svg_wrap(self._text(20, 40, "No streak data", 14, self.t["text_muted"]), 80)

        t = self.t
        svg = self._text(20, 30, "Contribution Streak", 15, t["text"], bold=True) + "\n"

        boxes_w = 180
        metrics = [
            ("Longest Streak", f"{streak['longest_streak']} days", t["accent_orange"]),
            ("Current Streak", f"{streak['current_streak']} days", t["accent_green"]),
            ("Total Contributions", f"{streak['total_contributions']:,}", t["accent_purple"]),
        ]

        for i, (label, value, color) in enumerate(metrics):
            x = 20 + i * (boxes_w + 12)
            svg += f'<rect x="{x}" y="48" width="{boxes_w}" height="72" rx="8" fill="{t["bg"]}" opacity="0.6"/>\n'
            svg += self._text(x + boxes_w // 2, 78, value, 22, color, bold=True, anchor="middle") + "\n"
            svg += self._text(x + boxes_w // 2, 104, label, 11, t["text_muted"], anchor="middle") + "\n"

        return self._svg_wrap(svg, 150)

    def render_top_repos(self, repos):
        if not repos:
            return self._svg_wrap(self._text(20, 40, "No repos to display", 14, self.t["text_muted"]), 80)

        cols = 2
        card_w = (self.width - 50) // cols
        card_h = 80
        gap = 10
        rows = (len(repos) + cols - 1) // cols
        total_h = 50 + rows * (card_h + gap)

        svg = self._text(20, 30, "Top Repositories", 15, self.t["text"], bold=True) + "\n"

        for i, repo in enumerate(repos):
            row = i // cols
            col = i % cols
            x = 20 + col * (card_w + gap)
            y = 50 + row * (card_h + gap)

            svg += f'<rect x="{x}" y="{y}" width="{card_w}" height="{card_h}" rx="8" fill="{self.t["bg"]}" opacity="0.6"/>\n'
            svg += self._text(x + 14, y + 22, repo["name"], 13, self.t["accent"], bold=True) + "\n"

            desc = repo["description"][:80] + ("..." if len(repo["description"]) > 80 else "")
            if desc:
                svg += self._text(x + 14, y + 42, desc, 11, self.t["text_muted"]) + "\n"

            svg += self._text(x + 14, y + 62, f"\u2605 {repo['stars']}", 11, self.t["accent_orange"]) + "\n"
            if repo["language"]:
                lang_color = LANG_COLORS.get(repo["language"], "#ccc")
                svg += f'<circle cx="{x + 100}" cy="{y + 57}" r="5" fill="{lang_color}"/>\n'
                svg += self._text(x + 110, y + 62, repo["language"], 11, self.t["text_muted"]) + "\n"

        return self._svg_wrap(svg, total_h)

    def render_activity(self, events):
        if not events:
            return self._svg_wrap(self._text(20, 40, "No recent activity", 14, self.t["text_muted"]), 80)

        icons = {
            "PushEvent": "\u2191", "IssuesEvent": "\u25cf", "CreateEvent": "\u2728",
            "WatchEvent": "\u2605", "ForkEvent": "\u2442", "PullRequestEvent": "\u2190",
            "IssueCommentEvent": "\u2709", "ReleaseEvent": "\u25b6",
        }
        labels = {
            "PushEvent": "Pushed", "IssuesEvent": "Opened issue",
            "CreateEvent": "Created", "WatchEvent": "Starred",
            "ForkEvent": "Forked", "PullRequestEvent": "Opened PR",
            "IssueCommentEvent": "Commented", "ReleaseEvent": "Released",
        }

        item_h = 36
        pad = 20
        total_h = 50 + len(events) * item_h + 10

        svg = self._text(20, 30, "Recent Activity", 15, self.t["text"], bold=True) + "\n"
        icon_x, text_x = 35, 55

        for i, ev in enumerate(events):
            y = 48 + i * item_h
            icon = icons.get(ev["type"], "\u25cf")
            color_map = {"PushEvent": self.t["accent_green"], "IssuesEvent": self.t["accent_red"],
                         "CreateEvent": self.t["accent_purple"], "WatchEvent": self.t["accent_orange"],
                         "ForkEvent": self.t["accent"], "PullRequestEvent": self.t["accent_green"],
                         "IssueCommentEvent": self.t["accent_purple"], "ReleaseEvent": self.t["accent_orange"]}

            dot_color = color_map.get(ev["type"], self.t["text_muted"])
            repo_name = ev["repo"].split("/")[-1] if "/" in ev["repo"] else ev["repo"]

            if ev["type"] == "PushEvent":
                msg = ev.get("message", "")[:50]
                detail = f"{ev.get('count', 0)} commits" + (f" - {msg}" if msg else "")
            elif ev["type"] == "IssuesEvent":
                detail = f"{ev.get('action', '')} - {ev.get('title', '')[:40]}"
            elif ev["type"] == "CreateEvent":
                detail = f"{ev.get('ref_type', '')} {ev.get('ref', '')}"
            elif ev["type"] == "WatchEvent":
                detail = f"{repo_name}"
            elif ev["type"] == "ForkEvent":
                detail = f"{ev.get('forked_repo', '')}"
            elif ev["type"] == "PullRequestEvent":
                detail = f"{ev.get('action', '')} - {ev.get('title', '')[:40]}"
            elif ev["type"] == "ReleaseEvent":
                detail = f"{ev.get('tag', '')}"
            else:
                detail = repo_name

            label = labels.get(ev["type"], ev["type"])

            svg += f'<circle cx="{icon_x}" cy="{y + 6}" r="5" fill="{dot_color}"/>\n'
            svg += self._text(text_x, y + 11, f"{label} in {repo_name}", 12, self.t["text"]) + "\n"
            svg += self._text(text_x, y + 27, detail, 11, self.t["text_muted"]) + "\n"

        return self._svg_wrap(svg, total_h)

    def render_combined(self, svgs):
        parts = []
        total_h = 0
        for svg in svgs:
            h_line = [l for l in svg.split("\n") if 'height="' in l and l.strip().startswith("<svg")]
            if h_line:
                import re
                m = re.search(r'height="(\d+)"', h_line[0])
                if m:
                    h = int(m.group(1))
                    total_h += h + 16

        combined_w = self.width
        combined = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{combined_w}" height="{total_h}" viewBox="0 0 {combined_w} {total_h}">
  <rect width="{combined_w}" height="{total_h}" fill="{self.t['bg']}"/>
'''
        y_off = 0
        for svg in svgs:
            inner = svg.strip()
            inner = inner.replace('<?xml version="1.0" encoding="UTF-8"?>', "")
            inner_lines = inner.split("\n")
            filtered = []
            for line in inner_lines:
                if line.strip().startswith("<svg") or line.strip().startswith("<?xml"):
                    continue
                if line.strip().endswith("</svg>"):
                    continue
                if "<defs>" in line or "</defs>" in line:
                    continue
                filtered.append(line)
            inner_clean = "\n".join(filtered)

            h_line = [l for l in inner_lines if 'height="' in l and '<svg' in l]
            import re
            m = re.search(r'height="(\d+)"', inner_lines[0])
            h = int(m.group(1)) if m else 100

            combined += f'  <g transform="translate(0, {y_off})">\n'
            combined += inner_clean + "\n"
            combined += "  </g>\n"
            y_off += h + 16

        combined += "</svg>"
        return combined

    def save_svg(self, svg_content, filename, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(svg_content)
        return filepath
