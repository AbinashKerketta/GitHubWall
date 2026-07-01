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


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


FONT = 'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif"'


class Renderer:
    def __init__(self, theme="dark"):
        self.t = get_theme(theme)
        self.W = 1000
        self.P = 50
        self.U = self.W - self.P * 2

    # ── SVG wrapper ───────────────────────────────────
    def _svg(self, inner, h):
        t = self.t
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="{h}" viewBox="0 0 {self.W} {h}">'
            f'<defs>'
            f'<linearGradient id="ag" x1="0" y1="0" x2="100%" y2="0">'
            f'<stop offset="0" stop-color="{t["gradient_start"]}"/>'
            f'<stop offset="100%" stop-color="{t["gradient_end"]}"/>'
            f'</linearGradient>'
            f'<linearGradient id="ag2" x1="0" y1="0" x2="0" y2="100%">'
            f'<stop offset="0" stop-color="{t["gradient_start"]}" stop-opacity="0.15"/>'
            f'<stop offset="100%" stop-color="{t["gradient_end"]}" stop-opacity="0"/>'
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
        """Text with a raw XML prefix (e.g. &#9733;) that won't be double-escaped."""
        return f'<text x="{x}" y="{y}" fill="{color or self.t["text"]}" font-size="{size}" font-weight="normal" {FONT} text-anchor="{anchor}">{prefix}{esc(text)}</text>'

    def _box(self, x, y, w, h):
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{self.t["bg"]}" opacity="0.6"/>'

    def _pct_badge(self, x, y, text):
        c = self.t["text_muted"]
        return (
            f'<rect x="{x-46}" y="{y-13}" width="46" height="22" rx="11" fill="{c}" opacity="0.12"/>'
            f'{self._t(x-2, y+4, text, 12, c, bold=True, anchor="end")}'
        )

    def _header(self, title):
        return (
            f'{self._t(self.P, 40, title, 22, self.t["text"], bold=True)}'
            f'<rect x="{self.P}" y="52" width="140" height="3" rx="1.5" fill="url(#ag)"/>'
        )

    def _top_fade(self, h):
        return f'<rect x="4" y="0" width="{self.W-4}" height="80" rx="0" fill="url(#ag2)"/>'

    # ═══════════════════════════════════════════════════
    # 1. LANGUAGES
    # ═══════════════════════════════════════════════════
    def render_languages(self, data):
        if not data:
            return self._svg(self._t(self.P, 60, "No language data available", 16, self.t["text_muted"]), 120)
        total = sum(data.values())
        items = []
        for lang, bc in sorted(data.items(), key=lambda x: x[1], reverse=True)[:8]:
            pct = round((bc / total) * 100, 1)
            if pct >= 1:
                items.append((lang, pct, LANG_COLORS.get(lang, "#ccc")))

        bar_h, gap = 30, 14
        y0 = 100
        ch = len(items) * (bar_h + gap) - gap
        body = self._header("Most Used Languages")
        body += self._top_fade(ch + 140)
        body += self._box(self.P - 6, y0 - 14, self.U + 12, ch + 28)

        bw = self.U - 200
        y = y0
        for lang, pct, color in items:
            w = max(8, int(bw * pct / 100))
            # bar
            body += f'<rect x="{self.P}" y="{y}" width="{w}" height="{bar_h}" rx="6" fill="{color}" opacity="0.85"/>\n'
            # shadow under bar
            body += f'<rect x="{self.P+2}" y="{y+bar_h-2}" width="{w}" height="4" rx="2" fill="{color}" opacity="0.15"/>\n'
            # language colored dot
            body += f'<circle cx="{self.P+w+18}" cy="{y+bar_h//2}" r="5" fill="{color}"/>\n'
            # language name
            body += self._t(self.P + w + 30, y + bar_h - 7, lang, 14, self.t["text"], bold=True) + "\n"
            # percentage badge
            body += self._pct_badge(self.W - self.P, y + bar_h // 2, f"{pct}%") + "\n"
            y += bar_h + gap

        return self._svg(body, y0 + ch + 36)

    # ═══════════════════════════════════════════════════
    # 2. STATS
    # ═══════════════════════════════════════════════════
    def render_stats(self, stats):
        if not stats:
            return self._svg(self._t(self.P, 60, "No statistics available", 16, self.t["text_muted"]), 120)

        icons = {
            "Repos": '<rect x="8" y="6" width="14" height="18" rx="3" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M8 10h14M12 6v2" stroke="currentColor" stroke-width="1.5"/>',
            "Stars": '<path d="M15 3l2.5 5.5L23 9.5l-4.5 4.5 1 6L15 16.5 9.5 20l1-6L7 9.5l5.5-1L15 3z" fill="none" stroke="currentColor" stroke-width="1.5"/>',
            "Forks": '<path d="M10 9a3 3 0 100-6 3 3 0 000 6zM20 9a3 3 0 100-6 3 3 0 000 6zM10 21a3 3 0 100-6 3 3 0 000 6zM10 12v3M17 7l-4 3.5M17 17l-4-3.5" stroke="currentColor" stroke-width="1.5" fill="none"/>',
            "Followers": '<path d="M17 19v2H3v-2a4 4 0 014-4h6a4 4 0 014 4zM10 9a3 3 0 100-6 3 3 0 000 6zM20 15v3M21.5 16.5h-3" stroke="currentColor" stroke-width="1.5" fill="none"/>',
        }
        metrics = [
            ("Repos", str(stats["public_repos"]), self.t["accent"], icons["Repos"]),
            ("Stars", str(stats["total_stars"]), self.t["accent_orange"], icons["Stars"]),
            ("Forks", str(stats["total_forks"]), self.t["accent_purple"], icons["Forks"]),
            ("Followers", str(stats["followers"]), self.t["accent_green"], icons["Followers"]),
        ]

        g, cw, ch, cy = 16, (self.U - 48) // 4, 120, 100
        body = self._header("GitHub Statistics")
        body += self._top_fade(ch + 50)

        for i, (label, value, color, icon_svg) in enumerate(metrics):
            x = self.P + i * (cw + g)
            body += self._box(x, cy, cw, ch)
            # icon
            body += (
                f'<svg x="{x+cw//2-12}" y="{cy+8}" width="24" height="24" viewBox="0 0 24 24" color="{color}">'
                f'{icon_svg}'
                f'</svg>'
            )
            # value
            body += self._t(x + cw // 2, cy + 62, value, 38, color, bold=True, anchor="middle") + "\n"
            # label
            body += self._t(x + cw // 2, cy + 90, label, 13, self.t["text_muted"], anchor="middle") + "\n"

        return self._svg(body, cy + ch + 30)

    # ═══════════════════════════════════════════════════
    # 3. STREAK
    # ═══════════════════════════════════════════════════
    def render_streak(self, streak):
        if not streak:
            return self._svg(self._t(self.P, 60, "No streak data available", 16, self.t["text_muted"]), 120)

        def pl(n, w):
            return f"{n} {w}" + ("s" if n != 1 else "")

        g, cw, ch, cy = 16, (self.U - 32) // 3, 120, 100
        body = self._header("Contribution Streak")
        body += self._top_fade(ch + 50)

        metrics = [
            ("Longest Streak", pl(streak["longest_streak"], "day"), self.t["accent_orange"]),
            ("Current Streak", pl(streak["current_streak"], "day"), self.t["accent_green"]),
            ("Contributions", str(streak["total_contributions"]), self.t["accent_purple"]),
        ]

        fire = '<path d="M12 23c-3-2-5-5-5-8 0-3 2.5-5.5 5-9 2.5 3.5 5 6 5 9 0 3-2 6-5 8z" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M12 23c-2-1.5-3-3.5-3-5.5 0-2 1.5-3.5 3-5.5 1.5 2 3 3.5 3 5.5 0 2-1 4-3 5.5z" fill="currentColor" opacity="0.2"/>'

        for i, (label, value, color) in enumerate(metrics):
            x = self.P + i * (cw + g)
            body += self._box(x, cy, cw, ch)
            if i == 0:
                body += f'<svg x="{x+cw//2-12}" y="{cy+8}" width="24" height="24" viewBox="0 0 24 24" color="{self.t["accent_orange"]}">{fire}</svg>'
            body += self._t(x + cw // 2, cy + 62, value, 30, color, bold=True, anchor="middle") + "\n"
            body += self._t(x + cw // 2, cy + 90, label, 13, self.t["text_muted"], anchor="middle") + "\n"

        return self._svg(body, cy + ch + 30)

    # ═══════════════════════════════════════════════════
    # 4. TOP REPOS
    # ═══════════════════════════════════════════════════
    def render_top_repos(self, repos):
        if not repos:
            return self._svg(self._t(self.P, 60, "No repositories to display", 16, self.t["text_muted"]), 120)

        cols, g = 3, 16
        cw = (self.U - g * (cols - 1)) // cols
        ch, cy = 130, 100
        rows = (len(repos) + cols - 1) // cols
        body = self._header("Top Repositories")
        body += self._top_fade(rows * (ch + g) + 30)

        for i, repo in enumerate(repos):
            row, col = i // cols, i % cols
            x = self.P + col * (cw + g)
            y = cy + row * (ch + g)

            body += self._box(x, y, cw, ch)
            # repo name
            body += self._t(x + 16, y + 30, repo["name"], 17, self.t["accent"], bold=True) + "\n"
            # description
            desc = repo["description"][:45] + ("..." if len(repo["description"]) > 45 else "")
            if desc:
                body += self._t(x + 16, y + 54, desc, 12, self.t["text_muted"]) + "\n"
            # divider
            body += f'<rect x="{x+16}" y="{y+68}" width="{cw-32}" height="1" fill="{self.t["border"]}"/>\n'
            # stars with star entity
            body += self._ts(x + 16, y + 94, "&#9733; ", str(repo["stars"]), 14, self.t["accent_orange"]) + "\n"
            # language pill
            if repo["language"]:
                lc = LANG_COLORS.get(repo["language"], "#ccc")
                body += f'<circle cx="{x+80}" cy="{y+89}" r="5" fill="{lc}"/>\n'
                body += self._t(x + 90, y + 94, repo["language"], 12, self.t["text_muted"]) + "\n"
            # fork count
            if repo.get("forks", 0) > 0:
                body += self._t(x + cw - 16, y + 94, f"\u2442 {repo['forks']}", 12, self.t["text_muted"], anchor="end") + "\n"

        return self._svg(body, cy + rows * (ch + g) + 12)

    # ═══════════════════════════════════════════════════
    # 5. ACTIVITY
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
        ev_icon = {"PushEvent": "\u2191", "IssuesEvent": "!", "CreateEvent": "+",
                   "WatchEvent": "\u2605", "ForkEvent": "\u2442", "PullRequestEvent": "\u2190",
                   "IssueCommentEvent": "\u2709", "ReleaseEvent": "\u25b6"}

        rh, cy = 58, 100
        body = self._header("Recent Activity")
        body += self._top_fade(len(events) * rh + 30)

        for i, ev in enumerate(events):
            y = cy + i * rh
            rn = ev["repo"].split("/")[-1] if "/" in ev["repo"] else ev["repo"]
            lb = lbl.get(ev["type"], ev["type"])
            dc = clr.get(ev["type"], self.t["text_muted"])
            ic = ev_icon.get(ev["type"], "\u25cf")

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

            # activity row card
            body += f'<rect x="{self.P}" y="{y}" width="{self.U}" height="{rh-6}" rx="8" fill="{self.t["bg"]}" opacity="0.5"/>\n'
            # event type accent bar on left
            body += f'<rect x="{self.P}" y="{y}" width="4" height="{rh-6}" rx="2" fill="{dc}"/>\n'
            # event icon circle
            body += f'<circle cx="{self.P+18}" cy="{y+(rh-6)//2}" r="14" fill="{dc}" opacity="0.12"/>\n'
            body += self._t(self.P+18, y+(rh-6)//2+5, ic, 13, dc, bold=True, anchor="middle") + "\n"
            # event label
            body += self._t(self.P+46, y+22, f"{lb} in {rn}", 14, self.t["text"], bold=True) + "\n"
            # event detail
            body += self._t(self.P+46, y+42, dt, 12, self.t["text_muted"]) + "\n"

        return self._svg(body, cy + len(events) * rh + 14)

    # ═══════════════════════════════════════════════════
    # 6. COMBINED WALL
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
            f'<stop offset="100" stop-color="{self.t["gradient_end"]}"/>'
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
            out += f'\n<g transform="translate(0,{y})">\n' + "\n".join(clean) + "\n</g>\n"
            y += h + gap

        out += "</svg>"
        return out

    def save_svg(self, content, filename, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        p = os.path.join(output_dir, filename)
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        return p
