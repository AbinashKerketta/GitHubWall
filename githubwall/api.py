import requests
import time
import os


class GitHubAPI:
    BASE = "https://api.github.com"

    def __init__(self, username, token=None):
        self.username = username
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHubWall/1.0",
        })
        if token:
            self.session.headers.update({"Authorization": f"token {token}"})

    def _get(self, path, params=None):
        url = f"{self.BASE}{path}"
        resp = self.session.get(url, params=params, timeout=15)
        if resp.status_code == 403 and "rate limit" in resp.text.lower():
            raise Exception("GitHub API rate limit exceeded. Add a token to config.json.")
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    def _get_paginated(self, path, params=None, max_pages=3):
        results = []
        page = 1
        while page <= max_pages:
            p = dict(params or {})
            p["per_page"] = 100
            p["page"] = page
            data = self._get(path, p)
            if not data:
                break
            results.extend(data)
            if len(data) < 100:
                break
            page += 1
            time.sleep(0.2)
        return results

    def get_user(self):
        return self._get(f"/users/{self.username}")

    def get_repos(self):
        return self._get_paginated(f"/users/{self.username}/repos",
                                   {"sort": "updated", "direction": "desc"})

    def get_events(self):
        data = self._get(f"/users/{self.username}/events", {"per_page": 30})
        return data or []

    def get_languages(self, repo_name):
        return self._get(f"/repos/{self.username}/{repo_name}/languages")

    def get_starred(self):
        return self._get_paginated(f"/users/{self.username}/repos",
                                   {"sort": "stars", "direction": "desc"},
                                   max_pages=1)

    def get_combined_languages(self):
        repos = self.get_repos()
        combined = {}
        for repo in repos:
            if repo.get("fork"):
                continue
            langs = self.get_languages(repo["name"])
            if langs:
                for lang, bytes_count in langs.items():
                    combined[lang] = combined.get(lang, 0) + bytes_count
                time.sleep(0.1)
        return combined

    def get_total_stats(self):
        user = self.get_user()
        repos = self.get_repos()
        total_stars = sum(r.get("stargazers_count", 0) for r in repos)
        total_forks = sum(r.get("forks_count", 0) for r in repos)
        total_watchers = sum(r.get("watchers_count", 0) for r in repos)
        return {
            "public_repos": user.get("public_repos", 0),
            "total_stars": total_stars,
            "total_forks": total_forks,
            "followers": user.get("followers", 0),
            "following": user.get("following", 0),
            "created_at": user.get("created_at", ""),
            "total_watchers": total_watchers,
        }

    def get_top_repos(self, count=6):
        repos = self.get_repos()
        sorted_repos = sorted(repos,
                             key=lambda r: r.get("stargazers_count", 0),
                             reverse=True)
        top = [r for r in sorted_repos if not r.get("fork")][:count]
        result = []
        for r in top:
            result.append({
                "name": r["name"],
                "description": r.get("description") or "",
                "stars": r.get("stargazers_count", 0),
                "forks": r.get("forks_count", 0),
                "language": r.get("language") or "",
                "url": r["html_url"],
            })
        return result

    def get_recent_activity(self, count=5):
        events = self.get_events()
        filtered = []
        for e in events:
            if len(filtered) >= count:
                break
            repo = e.get("repo", {}).get("name", "")
            created = e.get("created_at", "")
            item = {"type": e["type"], "repo": repo, "date": created}
            if e["type"] == "PushEvent":
                commits = e.get("payload", {}).get("commits", [])
                item["count"] = len(commits)
                item["message"] = commits[0]["message"] if commits else ""
            elif e["type"] == "IssuesEvent":
                action = e.get("payload", {}).get("action", "")
                title = e.get("payload", {}).get("issue", {}).get("title", "")
                item["action"] = action
                item["title"] = title
            elif e["type"] == "CreateEvent":
                ref_type = e.get("payload", {}).get("ref_type", "")
                ref = e.get("payload", {}).get("ref", "")
                item["ref_type"] = ref_type
                item["ref"] = ref
            elif e["type"] == "WatchEvent":
                pass
            elif e["type"] == "ForkEvent":
                forked = e.get("payload", {}).get("forkee", {}).get("full_name", "")
                item["forked_repo"] = forked
            elif e["type"] == "PullRequestEvent":
                action = e.get("payload", {}).get("action", "")
                title = e.get("payload", {}).get("pull_request", {}).get("title", "")
                item["action"] = action
                item["title"] = title
            elif e["type"] == "IssueCommentEvent":
                action = e.get("payload", {}).get("action", "")
                item["action"] = action
            elif e["type"] == "ReleaseEvent":
                tag = e.get("payload", {}).get("release", {}).get("tag_name", "")
                item["tag"] = tag
            else:
                continue
            filtered.append(item)
        return filtered
