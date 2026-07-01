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


class Renderer:
    def __init__(self, theme="dark"):
        self.t = get_theme(theme)
        self.W = 1000
        self.P = 50  # padding
        self.U = self.W - self.P * 2  # usable inner width

    def _svg(self, body, h):
        t = self.t
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="{h}" viewBox="0 0 {self.W} {h}">'
            f'<defs>'
            f'<linearGradient id="ag" x1="0%" y1="0%" x2="100%" y2="0%">'
            f'<stop offset="0%" stop-color="{t["gradient_start"]}"/><stop offset="100%" stop-color="{t["gradient_end"]}"/>'
            f'</linearGradient>'
            f'</defs>'
            f'<rect width="{self.W}" height="{h}" rx="14" fill="{t["bg_card"]}"/>'
            f'{body}'
            f'</svg>'
        )

    def _txt(self, x, y, text, size=14, color=None, bold=False, anchor="start"):
        c = color or self.t["text"]
        fw = "bold" if bold else "normal"
        return (
            f'<text x="{x}" y="{y}" fill="{c}" font-size="{size}" '
            f'font-weight="{fw}" '
            f'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" '
            f'text-anchor="{anchor}">{esc(text)}</text>'
        )

    def _box(self, x, y, w, h):
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{self.t["bg"]}" opacity="0.5"/>'

    def _grad_bar(self, x, y, w, h):
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="url(#ag)" opacity="0.8"/>'

    # ── Languages ──────────────────────────────────────────
    def render_languages(self, data):
        if not data:
            return self._svg(self._txt(self.P, 50, "No language data", 15, self.t["text_muted"]), 100)

        total = sum(data.values())
        items = []
        for lang, bc in sorted(data.items(), key=lambda x: x[1], reverse=True)[:8]:
            pct = round((bc / total) * 100, 1)
            if pct < 1:
                continue
            items.append((lang, pct, LANG_COLORS.get(lang, "#ccc")))

        bar_h = 26
        gap = 14
        y0 = 90
        chart_h = len(items) * (bar_h + gap) - gap
        h = y0 + chart_h + 40

        body = self._txt(self.P, 36, "Most Used Languages", 20, self.t["text"], bold=True)
        body += self._grad_bar(self.P, 46, 130, 3)

        bar_w_max = self.U - 180
        y = y0
        for lang, pct, color in items:
            w = max(8, int(bar_w_max * pct / 100))
            body += f'<rect x="{self.P}" y="{y}" width="{w}" height="{bar_h}" rx="6" fill="{color}" opacity="0.9"/>\n'
            body += self._txt(self.P + w + 12, y + bar_h - 7, lang, 14, self.t["text"], bold=True)
            body += self._txt(self.W - self.P, y + bar_h - 7, f"{pct}%", 14, self.t["text_muted"], anchor="end")
            y += bar_h + gap

        body += self._box(self.P - 5, y0 - 12, self.U + 10, chart_h + 24)

        return self._svg(body, h)

    # ── Stats ──────────────────────────────────────────────
    def render_stats(self, stats):
        if not stats:
            return self._svg(self._txt(self.P, 50, "No stats", 15, self.t["text_muted"]), 100)

        metrics = [
            ("Repos", str(stats["public_repos"]), self.t["accent"]),
            ("Stars", str(stats["total_stars"]), self.t["accent_orange"]),
            ("Forks", str(stats["total_forks"]), self.t["accent_purple"]),
            ("Followers", str(stats["followers"]), self.t["accent_green"]),
        ]

        g = 16
        cw = (self.U - g * 3) // 4
        ch = 100
        cy = 90
        h = cy + ch + 30

        body = self._txt(self.P, 36, "GitHub Statistics", 20, self.t["text"], bold=True)
        body += self._grad_bar(self.P, 46, 130, 3)

        for i, (label, value, color) in enumerate(metrics):
            x = self.P + i * (cw + g)
            body += self._box(x, cy, cw, ch)
            body += self._txt(x + cw // 2, cy + 44, value, 36, color, bold=True, anchor="middle")
            body += self._txt(x + cw // 2, cy + 74, label, 13, self.t["text_muted"], anchor="middle")

        return self._svg(body, h)

    # ── Streak ─────────────────────────────────────────────
    def render_streak(self, streak):
        if not streak:
            return self._svg(self._txt(self.P, 50, "No streak data", 15, self.t["text_muted"]), 100)

        def pl(n, w):
            return f"{n} {w}" + ("s" if n != 1 else "")

        g = 16
        cw = (self.U - g * 2) // 3
        ch = 100
        cy = 90
        h = cy + ch + 30

        body = self._txt(self.P, 36, "Contribution Streak", 20, self.t["text"], bold=True)
        body += self._grad_bar(self.P, 46, 130, 3)

        metrics = [
            ("Longest Streak", pl(streak["longest_streak"], "day"), self.t["accent_orange"]),
            ("Current Streak", pl(streak["current_streak"], "day"), self.t["accent_green"]),
            ("Contributions", str(streak["total_contributions"]), self.t["accent_purple"]),
        ]
        for i, (label, value, color) in enumerate(metrics):
            x = self.P + i * (cw + g)
            body += self._box(x, cy, cw, ch)
            body += self._txt(x + cw // 2, cy + 44, value, 28, color, bold=True, anchor="middle")
            body += self._txt(x + cw // 2, cy + 74, label, 13, self.t["text_muted"], anchor="middle")

        return self._svg(body, h)

    # ── Top Repos ──────────────────────────────────────────
    def render_top_repos(self, repos):
        if not repos:
            return self._svg(self._txt(self.P, 50, "No repos", 15, self.t["text_muted"]), 100)

        cols = 3
        g = 16
        cw = (self.U - g * (cols - 1)) // cols
        ch = 110
        cy = 90
        rows = (len(repos) + cols - 1) // cols
        h = cy + rows * (ch + g) + 10

        body = self._txt(self.P, 36, "Top Repositories", 20, self.t["text"], bold=True)
        body += self._grad_bar(self.P, 46, 130, 3)

        for i, repo in enumerate(repos):
            row = i // cols
            col = i % cols
            x = self.P + col * (cw + g)
            y = cy + row * (ch + g)

            body += self._box(x, y, cw, ch)
            body += self._txt(x + 16, y + 28, repo["name"], 16, self.t["accent"], bold=True)
            desc = repo["description"][:45] + ("..." if len(repo["description"]) > 45 else "")
            if desc:
                body += self._txt(x + 16, y + 50, desc, 12, self.t["text_muted"])
            body += self._txt(x + 16, y + 82, "\u2605 " + str(repo["stars"]), 13, self.t["accent_orange"])
            if repo["language"]:
                lc = LANG_COLORS.get(repo["language"], "#ccc")
                body += f'<circle cx="{x + 80}" cy="{y + 77}" r="5" fill="{lc}"/>\n'
                body += self._txt(x + 90, y + 82, repo["language"], 12, self.t["text_muted"])

        return self._svg(body, h)

    # ── Activity ───────────────────────────────────────────
    def render_activity(self, events):
        events = [e for e in events if not (e["type"] == "PushEvent" and e.get("count", 0) == 0)]
        if not events:
            return self._svg(self._txt(self.P, 50, "No recent activity", 15, self.t["text_muted"]), 100)

        lbl = {"PushEvent":"Pushed","IssuesEvent":"Opened issue","CreateEvent":"Created","WatchEvent":"Starred","ForkEvent":"Forked","PullRequestEvent":"Opened PR","IssueCommentEvent":"Commented","ReleaseEvent":"Released"}
        clr = {"PushEvent":self.t["accent_green"],"IssuesEvent":self.t["accent_red"],"CreateEvent":self.t["accent_purple"],"WatchEvent":self.t["accent_orange"],"ForkEvent":self.t["accent"],"PullRequestEvent":self.t["accent_green"],"IssueCommentEvent":self.t["accent_purple"],"ReleaseEvent":self.t["accent_orange"]}

        rh = 56
        cy = 90
        h = cy + len(events) * rh + 14

        body = self._txt(self.P, 36, "Recent Activity", 20, self.t["text"], bold=True)
        body += self._grad_bar(self.P, 46, 130, 3)

        for i, ev in enumerate(events):
            y = cy + i * rh
            dc = clr.get(ev["type"], self.t["text_muted"])
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

            body += f'<rect x="{self.P}" y="{y}" width="{self.U}" height="{rh-6}" rx="8" fill="{self.t["bg"]}" opacity="0.5"/>\n'
            body += f'<circle cx="{self.P+14}" cy="{y+(rh-6)//2}" r="5" fill="{dc}"/>\n'
            body += self._txt(self.P+30, y+22, f"{lb} in {rn}", 14, self.t["text"], bold=True)
            body += self._txt(self.P+30, y+40, dt, 12, self.t["text_muted"])

        return self._svg(body, h)

    # ── Combined ───────────────────────────────────────────
    def render_combined(self, svgs):
        import re
        gap = 20
        heights = []
        total_h = 0
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
            out += f'<g transform="translate(0,{y})">' + "\n".join(clean) + "</g>\n"
            y += h + gap
        out += "</svg>"
        return out

    def save_svg(self, content, filename, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        p = os.path.join(output_dir, filename)
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        return p
