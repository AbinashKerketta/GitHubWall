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
    "PowerShell": "#012456", "Batchfile": "#C1F12E",
}

# SVG icon paths (explicit fill/stroke, no currentColor dependency)
ICONS = {
    "repo": '<path d="M6 7v10a2 2 0 002 2h8a2 2 0 002-2V7" fill="none" stroke="{c}" stroke-width="1.5"/><path d="M6 7l6-3 6 3" fill="none" stroke="{c}" stroke-width="1.5"/><path d="M6 11h12M9 7v10" fill="none" stroke="{c}" stroke-width="1.5"/>',
    "star": '<path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14l-5-4.87 6.91-1.01L12 2z" fill="none" stroke="{c}" stroke-width="1.5"/>',
    "fork": '<path d="M12 7a3 3 0 100-6 3 3 0 000 6zM12 7a3 3 0 100-6 3 3 0 000 6zM12 17a3 3 0 100-6 3 3 0 000 6z" fill="none" stroke="{c}" stroke-width="1.5"/><path d="M12 10v3M17 4.5l-5 3M17 12.5l-5-3" fill="none" stroke="{c}" stroke-width="1.5"/>',
    "user": '<path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" fill="none" stroke="{c}" stroke-width="1.5"/><circle cx="9" cy="7" r="4" fill="none" stroke="{c}" stroke-width="1.5"/>',
    "fire": '<path d="M12 23c-4-2.5-6-6-6-10 0-4 3-7 6-11 3 4 6 7 6 11 0 4-2 7.5-6 11z" fill="none" stroke="{c}" stroke-width="1.5"/><path d="M12 23c-2.5-1.5-4-4-4-7 0-3 2-5 4-8 2 3 4 5 4 8 0 3-1.5 5.5-4 7z" fill="{c}" opacity="0.2"/>',
    "arrow-up": '<path d="M12 19V5M5 12l7-7 7 7" fill="none" stroke="{c}" stroke-width="2"/>',
    "star-fill": '<path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14l-5-4.87 6.91-1.01L12 2z" fill="{c}" opacity="0.8"/>',
    "plus": '<path d="M12 5v14M5 12h14" fill="none" stroke="{c}" stroke-width="2"/>',
    "create": '<path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z" fill="none" stroke="{c}" stroke-width="1.5"/><path d="M14 2v6h6" fill="none" stroke="{c}" stroke-width="1.5"/>',
}


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

FONT = 'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif"'
STAR = "&#9733;"
ARROW = "&#8593;"
PLUS = "+"

class Renderer:
    def __init__(self, theme="dark"):
        self.t = get_theme(theme)
        self.W = 1000
        self.P = 50
        self.U = self.W - self.P * 2

    def _svg(self, inner, h):
        t = self.t
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="{h}" viewBox="0 0 {self.W} {h}">'
            f'<defs>'
            f'<linearGradient id="ag" x1="0" y1="0" x2="100%" y2="0">'
            f'<stop offset="0" stop-color="{t["gradient_start"]}"/>'
            f'<stop offset="100%" stop-color="{t["gradient_end"]}"/>'
            f'</linearGradient>'
            f'</defs>'
            f'<rect width="{self.W}" height="{h}" rx="14" fill="{t["bg_card"]}"/>'
            f'<rect x="0" y="0" width="4" height="{h}" rx="2" fill="url(#ag)"/>'
            f'{inner}'
            f'</svg>'
        )

    def _t(self, x, y, text, size=14, color=None, bold=False, anchor="start"):
        return f'<text x="{x}" y="{y}" fill="{color or self.t["text"]}" font-size="{size}" font-weight="{"bold" if bold else "normal"}" {FONT} text-anchor="{anchor}">{esc(text)}</text>'

    def _ts(self, x, y, prefix, text, size=14, color=None, anchor="start"):
        return f'<text x="{x}" y="{y}" fill="{color or self.t["text"]}" font-size="{size}" font-weight="normal" {FONT} text-anchor="{anchor}">{prefix}{esc(text)}</text>'

    def _box(self, x, y, w, h):
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{self.t["bg"]}" opacity="0.6"/>'

    def _gl(self, x, y, w):
        return f'<rect x="{x}" y="{y}" width="{w}" height="3" rx="1.5" fill="url(#ag)"/>'

    def _icon(self, x, y, name, color, size=24):
        svg = ICONS.get(name, "").replace("{c}", color)
        return f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="0 0 24 24">{svg}</svg>'

    def _sect(self, title):
        return self._t(self.P, 40, title, 22, self.t["text"], bold=True) + self._gl(self.P, 52, 140)

    def _pct(self, x, y, text):
        return (
            f'<rect x="{x-46}" y="{y-12}" width="46" height="22" rx="11" fill="{self.t["text_muted"]}" opacity="0.12"/>'
            f'{self._t(x-2, y+4, text, 12, self.t["text_muted"], bold=True, anchor="end")}'
        )

    # ═══════════════════════════════════════════════════
    # LANGUAGES — backgrounds FIRST, content LAST
    # ═══════════════════════════════════════════════════
    def render_languages(self, data):
        if not data:
            return self._svg(self._t(self.P, 60, "No language data available", 16, self.t["text_muted"]), 120)

        total = sum(data.values())
        items = [(l, round((b / total) * 100, 1), LANG_COLORS.get(l, "#ccc"))
                 for l, b in sorted(data.items(), key=lambda x: x[1], reverse=True)[:8]
                 if round((b / total) * 100, 1) >= 1]

        bar_h, gap = 28, 12
        y0 = 96
        ch = len(items) * (bar_h + gap) - gap
        bw = self.U - 190

        # Layer 1: backgrounds
        body = self._box(self.P - 6, y0 - 12, self.U + 12, ch + 24)

        # Layer 2: bars, shadows, dots (behind text)
        y = y0
        for lang, pct, color in items:
            w = max(8, int(bw * pct / 100))
            body += f'<rect x="{self.P}" y="{y}" width="{w}" height="{bar_h}" rx="6" fill="{color}" opacity="0.85"/>\n'
            body += f'<rect x="{self.P+1}" y="{y+bar_h}" width="{w}" height="4" rx="2" fill="{color}" opacity="0.15"/>\n'
            body += f'<circle cx="{self.P+w+16}" cy="{y+bar_h//2}" r="5" fill="{color}"/>\n'
            y += bar_h + gap

        # Layer 3: text (on top of everything)
        y = y0
        for lang, pct, color in items:
            w = max(8, int(bw * pct / 100))
            body += self._t(self.P + w + 28, y + bar_h - 8, lang, 14, self.t["text"], bold=True)
            body += self._pct(self.W - self.P, y + bar_h // 2, f"{pct}%")
            y += bar_h + gap

        # Layer 4: title (always on top)
        return self._svg(self._sect("Most Used Languages") + body, y0 + ch + 36)

    # ═══════════════════════════════════════════════════
    # STATS — backgrounds FIRST, content LAST
    # ═══════════════════════════════════════════════════
    def render_stats(self, stats):
        if not stats:
            return self._svg(self._t(self.P, 60, "No statistics available", 16, self.t["text_muted"]), 120)

        metrics = [
            ("Repos", str(stats["public_repos"]), self.t["accent"], "repo"),
            ("Stars", str(stats["total_stars"]), self.t["accent_orange"], "star"),
            ("Forks", str(stats["total_forks"]), self.t["accent_purple"], "fork"),
            ("Followers", str(stats["followers"]), self.t["accent_green"], "user"),
        ]

        g, cw, ch, cy = 16, (self.U - 48) // 4, 120, 96

        # Layer 1: card backgrounds
        body = ""
        for i, (label, value, color, icon_name) in enumerate(metrics):
            x = self.P + i * (cw + g)
            body += self._box(x, cy, cw, ch)

        # Layer 2: icons (on top of cards)
        for i, (label, value, color, icon_name) in enumerate(metrics):
            x = self.P + i * (cw + g)
            body += self._icon(x + cw // 2 - 12, cy + 10, icon_name, color)

        # Layer 3: text (on top of everything)
        for i, (label, value, color, icon_name) in enumerate(metrics):
            x = self.P + i * (cw + g)
            body += self._t(x + cw // 2, cy + 62, value, 38, color, bold=True, anchor="middle")
            body += self._t(x + cw // 2, cy + 90, label, 13, self.t["text_muted"], anchor="middle")

        # Layer 4: title
        return self._svg(self._sect("GitHub Statistics") + body, cy + ch + 30)

    # ═══════════════════════════════════════════════════
    # STREAK — backgrounds FIRST, content LAST
    # ═══════════════════════════════════════════════════
    def render_streak(self, streak):
        if not streak:
            return self._svg(self._t(self.P, 60, "No streak data available", 16, self.t["text_muted"]), 120)

        def pl(n, w):
            return f"{n} {w}" + ("s" if n != 1 else "")

        g, cw, ch, cy = 16, (self.U - 32) // 3, 120, 96
        metrics = [
            ("Longest Streak", pl(streak["longest_streak"], "day"), self.t["accent_orange"], "fire"),
            ("Current Streak", pl(streak["current_streak"], "day"), self.t["accent_green"], None),
            ("Contributions", str(streak["total_contributions"]), self.t["accent_purple"], None),
        ]

        # Layer 1: backgrounds
        body = ""
        for i, (label, value, color, icon_name) in enumerate(metrics):
            x = self.P + i * (cw + g)
            body += self._box(x, cy, cw, ch)

        # Layer 2: icons
        for i, (label, value, color, icon_name) in enumerate(metrics):
            x = self.P + i * (cw + g)
            if icon_name:
                body += self._icon(x + cw // 2 - 12, cy + 10, icon_name, color)

        # Layer 3: text
        for i, (label, value, color, icon_name) in enumerate(metrics):
            x = self.P + i * (cw + g)
            body += self._t(x + cw // 2, cy + 62, value, 30, color, bold=True, anchor="middle")
            body += self._t(x + cw // 2, cy + 90, label, 13, self.t["text_muted"], anchor="middle")

        return self._svg(self._sect("Contribution Streak") + body, cy + ch + 30)

    # ═══════════════════════════════════════════════════
    # TOP REPOS — backgrounds FIRST, content LAST
    # ═══════════════════════════════════════════════════
    def render_top_repos(self, repos):
        if not repos:
            return self._svg(self._t(self.P, 60, "No repositories to display", 16, self.t["text_muted"]), 120)

        cols, g = 3, 16
        cw = (self.U - g * (cols - 1)) // cols
        ch, cy = 130, 96
        rows = (len(repos) + cols - 1) // cols

        # Layer 1: card backgrounds
        body = ""
        for i, repo in enumerate(repos):
            row, col = i // cols, i % cols
            x = self.P + col * (cw + g)
            y = cy + row * (ch + g)
            body += self._box(x, y, cw, ch)

        # Layer 2: divider lines
        for i, repo in enumerate(repos):
            row, col = i // cols, i % cols
            x = self.P + col * (cw + g)
            y = cy + row * (ch + g)
            body += f'<rect x="{x+16}" y="{y+68}" width="{cw-32}" height="1" fill="{self.t["border"]}"/>\n'

        # Layer 3: language dots
        for i, repo in enumerate(repos):
            if not repo["language"]:
                continue
            row, col = i // cols, i % cols
            x = self.P + col * (cw + g)
            y = cy + row * (ch + g)
            lc = LANG_COLORS.get(repo["language"], "#ccc")
            body += f'<circle cx="{x+80}" cy="{y+89}" r="5" fill="{lc}"/>\n'

        # Layer 4: text (always on top)
        for i, repo in enumerate(repos):
            row, col = i // cols, i % cols
            x = self.P + col * (cw + g)
            y = cy + row * (ch + g)
            body += self._t(x + 16, y + 30, repo["name"], 17, self.t["accent"], bold=True)
            desc = repo["description"][:45] + ("..." if len(repo["description"]) > 45 else "")
            if desc:
                body += self._t(x + 16, y + 54, desc, 12, self.t["text_muted"])
            body += self._ts(x + 16, y + 94, STAR + " ", str(repo["stars"]), 14, self.t["accent_orange"])
            if repo["language"]:
                body += self._t(x + 90, y + 94, repo["language"], 12, self.t["text_muted"])
            if repo.get("forks", 0) > 0:
                body += self._t(x + cw - 16, y + 94, f"&#8764; {repo['forks']}", 12, self.t["text_muted"], anchor="end")

        return self._svg(self._sect("Top Repositories") + body, cy + rows * (ch + g) + 12)

    # ═══════════════════════════════════════════════════
    # ACTIVITY — backgrounds FIRST, content LAST
    # ═══════════════════════════════════════════════════
    def render_activity(self, events):
        events = [e for e in events if not (e["type"] == "PushEvent" and e.get("count", 0) == 0)]
        if not events:
            return self._svg(self._t(self.P, 60, "No recent activity", 16, self.t["text_muted"]), 120)

        lbl = {"PushEvent": "Pushed", "IssuesEvent": "Opened issue", "CreateEvent": "Created",
               "WatchEvent": "Starred", "ForkEvent": "Forked", "PullRequestEvent": "Opened PR",
               "IssueCommentEvent": "Commented", "ReleaseEvent": "Released"}
        clr = {"PushEvent": self.t["accent_green"], "IssuesEvent": self.t["accent_red"],
               "CreateEvent": self.t["accent_purple"], "WatchEvent": self.t["accent_orange"],
               "ForkEvent": self.t["accent"], "PullRequestEvent": self.t["accent_green"],
               "IssueCommentEvent": self.t["accent_purple"], "ReleaseEvent": self.t["accent_orange"]}
        ev_icon = {"PushEvent": "arrow-up", "IssuesEvent": "plus", "CreateEvent": "create",
                   "WatchEvent": "star-fill", "ForkEvent": "fork", "PullRequestEvent": "arrow-up",
                   "IssueCommentEvent": "plus", "ReleaseEvent": "create"}

        rh, cy = 58, 96

        # Layer 1: row backgrounds + accent bars
        body = ""
        for i, ev in enumerate(events):
            y = cy + i * rh
            dc = clr.get(ev["type"], self.t["text_muted"])
            body += f'<rect x="{self.P}" y="{y}" width="{self.U}" height="{rh-6}" rx="8" fill="{self.t["bg"]}" opacity="0.5"/>\n'
            body += f'<rect x="{self.P}" y="{y}" width="4" height="{rh-6}" rx="2" fill="{dc}"/>\n'

        # Layer 2: icon circles
        for i, ev in enumerate(events):
            y = cy + i * rh
            dc = clr.get(ev["type"], self.t["text_muted"])
            body += f'<circle cx="{self.P+20}" cy="{y+(rh-6)//2}" r="14" fill="{dc}" opacity="0.12"/>\n'

        # Layer 3: icons (SVG, no currentColor)
        for i, ev in enumerate(events):
            y = cy + i * rh
            dc = clr.get(ev["type"], self.t["text_muted"])
            iname = ev_icon.get(ev["type"], "star-fill")
            body += self._icon(self.P + 8, y + (rh - 6) // 2 - 12, iname, dc, 24)

        # Layer 4: text (always on top)
        for i, ev in enumerate(events):
            y = cy + i * rh
            rn = ev["repo"].split("/")[-1] if "/" in ev["repo"] else ev["repo"]
            lb = lbl.get(ev["type"], ev["type"])

            if ev["type"] == "PushEvent":
                dt = f"{ev.get('count',0)} commit" + ("s" if ev.get("count",0) != 1 else "")
                m = ev.get("message", "")[:50]
                if m: dt += " - " + m
            elif ev["type"] == "IssuesEvent":
                dt = ev.get("action", "") + " issue"
                t = ev.get("title", "")[:50]
                if t: dt += " - " + t
            elif ev["type"] == "CreateEvent":
                dt = f"{ev.get('ref_type','')} {ev.get('ref','')}"
            elif ev["type"] == "WatchEvent":
                dt = "starred this repo"
            elif ev["type"] == "ForkEvent":
                dt = "forked " + ev.get("forked_repo", "").split("/")[-1]
            elif ev["type"] == "PullRequestEvent":
                dt = ev.get("action", "") + " PR"
                t = ev.get("title", "")[:50]
                if t: dt += " - " + t
            elif ev["type"] == "ReleaseEvent":
                dt = "released " + ev.get("tag", "")
            else:
                dt = rn

            body += self._t(self.P + 46, y + 22, f"{lb} in {rn}", 14, self.t["text"], bold=True)
            body += self._t(self.P + 46, y + 42, dt, 12, self.t["text_muted"])

        return self._svg(self._sect("Recent Activity") + body, cy + len(events) * rh + 14)

    # ═══════════════════════════════════════════════════
    # COMBINED WALL
    # ═══════════════════════════════════════════════════
    def render_combined(self, svgs):
        import re
        gap = 20
        heights, total_h = [], 0
        for svg in svgs:
            m = re.search(r'height="(\d+)"', svg.split("\n")[0])
            h = int(m.group(1)) if m else 100
            heights.append(h)
            total_h += h + gap

        out = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="{total_h}" viewBox="0 0 {self.W} {total_h}">'
            f'<defs>'
            f'<linearGradient id="ag" x1="0" y1="0" x2="100%" y2="0">'
            f'<stop offset="0" stop-color="{self.t["gradient_start"]}"/>'
            f'<stop offset="100%" stop-color="{self.t["gradient_end"]}"/>'
            f'</linearGradient>'
            f'</defs>'
            f'<rect width="{self.W}" height="{total_h}" fill="{self.t["bg"]}"/>'
        )

        y = 0
        for svg in svgs:
            # Strip the <svg> wrapper and </svg> closing tag using regex
            inner = re.sub(r'^<svg[^>]*>', '', svg)
            inner = re.sub(r'</svg>\s*$', '', inner)
            # Remove defs section (we have our own in combined)
            inner = re.sub(r'<defs>.*?</defs>', '', inner, flags=re.DOTALL)
            h = heights.pop(0)
            out += f'\n<g transform="translate(0,{y})">\n{inner}\n</g>\n'
            y += h + gap

        out += "</svg>"
        return out

    def save_svg(self, content, filename, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        p = os.path.join(output_dir, filename)
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        return p
