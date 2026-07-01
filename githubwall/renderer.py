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

STAR = "&#9733;"  # Use XML entity to avoid encoding issues


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Renderer:
    def __init__(self, theme="dark"):
        self.t = get_theme(theme)
        self.W = 1000
        self.P = 50
        self.U = self.W - self.P * 2

    def _svg(self, body, h):
        t = self.t
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="{h}" viewBox="0 0 {self.W} {h}">'
            f'<defs>'
            f'<linearGradient id="ag" x1="0%" y1="0%" x2="100%" y2="0%">'
            f'<stop offset="0%" stop-color="{t["gradient_start"]}"/>'
            f'<stop offset="100%" stop-color="{t["gradient_end"]}"/>'
            f'</linearGradient>'
            f'</defs>'
            f'<rect width="{self.W}" height="{h}" rx="14" fill="{t["bg_card"]}"/>'
            f'{body}'
            f'</svg>'
        )

    def _t(self, x, y, text, size=14, color=None, bold=False, anchor="start"):
        return (
            f'<text x="{x}" y="{y}" fill="{color or self.t["text"]}" font-size="{size}" '
            f'font-weight="{"bold" if bold else "normal"}" '
            f'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" '
            f'text-anchor="{anchor}">{esc(text)}</text>'
        )

    def _ts(self, x, y, prefix, text, size=14, color=None, anchor="start"):
        """Text with a raw XML entity prefix (e.g. star) that won't be double-escaped."""
        return (
            f'<text x="{x}" y="{y}" fill="{color or self.t["text"]}" font-size="{size}" '
            f'font-weight="normal" '
            f'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" '
            f'text-anchor="{anchor}">{prefix}{esc(text)}</text>'
        )

    def _box(self, x, y, w, h):
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{self.t["bg"]}" opacity="0.5"/>'

    def _gl(self, x, y, w):
        return f'<rect x="{x}" y="{y}" width="{w}" height="3" rx="2" fill="url(#ag)" opacity="0.8"/>'

    def _sect(self, title):
        return (
            self._t(self.P, 40, title, 22, self.t["text"], bold=True) + "\n"
            + self._gl(self.P, 52, 140) + "\n"
        )

    # ── Languages ──────────────────────────────────────────
    def render_languages(self, data):
        if not data:
            return self._svg(self._t(self.P, 60, "No language data", 16, self.t["text_muted"]), 110)
        total = sum(data.values())
        items = [(l, round((b/total)*100, 1), LANG_COLORS.get(l, "#ccc"))
                 for l, b in sorted(data.items(), key=lambda x: x[1], reverse=True)[:8]
                 if round((b/total)*100, 1) >= 1]

        bar_h, gap = 28, 14
        y0 = 100
        ch = len(items) * (bar_h + gap) - gap
        body = self._sect("Most Used Languages")
        body += self._box(self.P-8, y0-14, self.U+16, ch+28) + "\n"

        bw = self.U - 180
        y = y0
        for lang, pct, color in items:
            w = max(8, int(bw * pct / 100))
            body += f'<rect x="{self.P}" y="{y}" width="{w}" height="{bar_h}" rx="6" fill="{color}" opacity="0.9"/>\n'
            body += self._t(self.P + w + 14, y + bar_h - 7, lang, 15, self.t["text"], bold=True) + "\n"
            body += self._t(self.W - self.P, y + bar_h - 7, f"{pct}%", 15, self.t["text_muted"], anchor="end") + "\n"
            y += bar_h + gap

        return self._svg(body, y0 + ch + 36)

    # ── Stats ──────────────────────────────────────────────
    def render_stats(self, stats):
        if not stats:
            return self._svg(self._t(self.P, 60, "No stats available", 16, self.t["text_muted"]), 110)
        metrics = [("Repos", str(stats["public_repos"]), self.t["accent"]),
                   ("Stars", str(stats["total_stars"]), self.t["accent_orange"]),
                   ("Forks", str(stats["total_forks"]), self.t["accent_purple"]),
                   ("Followers", str(stats["followers"]), self.t["accent_green"])]
        g, cw, ch, cy = 16, (self.U - 48) // 4, 110, 100
        body = self._sect("GitHub Statistics")
        for i, (label, value, color) in enumerate(metrics):
            x = self.P + i * (cw + g)
            body += self._box(x, cy, cw, ch) + "\n"
            body += self._t(x + cw // 2, cy + 46, value, 38, color, bold=True, anchor="middle") + "\n"
            body += self._t(x + cw // 2, cy + 78, label, 14, self.t["text_muted"], anchor="middle") + "\n"
        return self._svg(body, cy + ch + 30)

    # ── Streak ─────────────────────────────────────────────
    def render_streak(self, streak):
        if not streak:
            return self._svg(self._t(self.P, 60, "No streak data", 16, self.t["text_muted"]), 110)
        def pl(n, w): return f"{n} {w}" + ("s" if n != 1 else "")
        g, cw, ch, cy = 16, (self.U - 32) // 3, 110, 100
        body = self._sect("Contribution Streak")
        metrics = [("Longest Streak", pl(streak["longest_streak"], "day"), self.t["accent_orange"]),
                   ("Current Streak", pl(streak["current_streak"], "day"), self.t["accent_green"]),
                   ("Contributions", str(streak["total_contributions"]), self.t["accent_purple"])]
        for i, (label, value, color) in enumerate(metrics):
            x = self.P + i * (cw + g)
            body += self._box(x, cy, cw, ch) + "\n"
            body += self._t(x + cw // 2, cy + 46, value, 30, color, bold=True, anchor="middle") + "\n"
            body += self._t(x + cw // 2, cy + 78, label, 14, self.t["text_muted"], anchor="middle") + "\n"
        return self._svg(body, cy + ch + 30)

    # ── Top Repos ──────────────────────────────────────────
    def render_top_repos(self, repos):
        if not repos:
            return self._svg(self._t(self.P, 60, "No repos to display", 16, self.t["text_muted"]), 110)
        cols, g = 3, 16
        cw = (self.U - g * (cols - 1)) // cols
        ch, cy = 120, 100
        rows = (len(repos) + cols - 1) // cols
        body = self._sect("Top Repositories")
        for i, repo in enumerate(repos):
            row, col = i // cols, i % cols
            x = self.P + col * (cw + g)
            y = cy + row * (ch + g)
            body += self._box(x, y, cw, ch) + "\n"
            body += self._t(x + 18, y + 30, repo["name"], 17, self.t["accent"], bold=True) + "\n"
            desc = repo["description"][:50] + ("..." if len(repo["description"]) > 50 else "")
            if desc:
                body += self._t(x + 18, y + 54, desc, 13, self.t["text_muted"]) + "\n"
            body += self._ts(x + 18, y + 88, "&#9733; ", str(repo["stars"]), 14, self.t["accent_orange"]) + "\n"
            if repo["language"]:
                lc = LANG_COLORS.get(repo["language"], "#ccc")
                body += f'<circle cx="{x + 80}" cy="{y + 83}" r="5" fill="{lc}"/>\n'
                body += self._t(x + 90, y + 88, repo["language"], 13, self.t["text_muted"]) + "\n"
        return self._svg(body, cy + rows * (ch + g) + 8)

    # ── Activity ───────────────────────────────────────────
    def render_activity(self, events):
        events = [e for e in events if not (e["type"] == "PushEvent" and e.get("count", 0) == 0)]
        if not events:
            return self._svg(self._t(self.P, 60, "No recent activity", 16, self.t["text_muted"]), 110)

        lbl = {"PushEvent":"Pushed","IssuesEvent":"Opened issue","CreateEvent":"Created","WatchEvent":"Starred","ForkEvent":"Forked","PullRequestEvent":"Opened PR","IssueCommentEvent":"Commented","ReleaseEvent":"Released"}
        clr = {"PushEvent":self.t["accent_green"],"IssuesEvent":self.t["accent_red"],"CreateEvent":self.t["accent_purple"],"WatchEvent":self.t["accent_orange"],"ForkEvent":self.t["accent"],"PullRequestEvent":self.t["accent_green"],"IssueCommentEvent":self.t["accent_purple"],"ReleaseEvent":self.t["accent_orange"]}

        rh, cy = 60, 100
        body = self._sect("Recent Activity")
        for i, ev in enumerate(events):
            y = cy + i * rh
            rn = ev["repo"].split("/")[-1] if "/" in ev["repo"] else ev["repo"]
            lb = lbl.get(ev["type"], ev["type"])

            if ev["type"] == "PushEvent":
                dt = f"{ev.get('count',0)} commit" + ("s" if ev.get("count",0)!=1 else "")
                m = ev.get("message","")[:50]
                if m: dt += " - " + m
            elif ev["type"] == "IssuesEvent":
                dt = ev.get("action","") + " issue"
                t = ev.get("title","")[:50]
                if t: dt += " - " + t
            elif ev["type"] == "CreateEvent":
                dt = f"{ev.get('ref_type','')} {ev.get('ref','')}"
            elif ev["type"] == "WatchEvent":
                dt = "starred this repo"
            elif ev["type"] == "ForkEvent":
                dt = "forked " + ev.get("forked_repo","").split("/")[-1]
            elif ev["type"] == "PullRequestEvent":
                dt = ev.get("action","") + " PR"
                t = ev.get("title","")[:50]
                if t: dt += " - " + t
            elif ev["type"] == "ReleaseEvent":
                dt = "released " + ev.get("tag","")
            else:
                dt = rn

            dc = clr.get(ev["type"], self.t["text_muted"])
            body += f'<rect x="{self.P}" y="{y}" width="{self.U}" height="{rh-6}" rx="8" fill="{self.t["bg"]}" opacity="0.5"/>\n'
            body += f'<circle cx="{self.P+14}" cy="{y+(rh-6)//2}" r="5" fill="{dc}"/>\n'
            body += self._t(self.P+30, y+22, f"{lb} in {rn}", 14, self.t["text"], bold=True) + "\n"
            body += self._t(self.P+30, y+42, dt, 13, self.t["text_muted"]) + "\n"

        return self._svg(body, cy + len(events) * rh + 14)

    # ── Combined ───────────────────────────────────────────
    def render_combined(self, svgs):
        import re
        gap = 28
        heights, total_h = [], 0
        for svg in svgs:
            m = re.search(r'height="(\d+)"', svg.split("\n")[0])
            h = int(m.group(1)) if m else 100
            heights.append(h)
            total_h += h + gap

        out = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="{total_h}" viewBox="0 0 {self.W} {total_h}">'
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
                if "<defs>" in s or "</defs>" in s or "linearGradient" in s or "<stop" in s:
                    continue
                clean.append(line)
            h = heights.pop(0)
            out += f'<g transform="translate(0,{y})">\n' + "\n".join(clean) + "\n</g>\n"
            y += h + gap

        out += "</svg>"
        return out

    def save_svg(self, content, filename, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        p = os.path.join(output_dir, filename)
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        return p
