<div align="center">
  <img src="https://img.shields.io/badge/version-1.0-blue?style=for-the-badge&labelColor=black" alt="Version">
  <img src="https://img.shields.io/badge/python-3.8%2B-yellow?style=for-the-badge&labelColor=black" alt="Python">
  <img src="https://img.shields.io/badge/GitHub%20Actions-enabled-brightgreen?style=for-the-badge&labelColor=black" alt="Actions">
  <br>
  <h1>📊 GitHubWall</h1>
  <p><strong>Personal GitHub README Stats Generator</strong> — Auto-updating SVG banners for your profile</p>
</div>

---

## 📋 Overview

GitHubWall generates beautiful, self-updating SVG banners for your GitHub profile README. It fetches your real GitHub data via API, generates clean visual banners, and automatically updates them daily via GitHub Actions — no manual re-runs needed.

**What it generates:**

| Banner | Content |
|--------|---------|
| `languages.svg` | Bar chart of your most-used programming languages |
| `stats.svg` | Metric cards: repos, stars, forks, followers |
| `streak.svg` | Contribution streak: longest, current, total |
| `top-repos.svg` | Grid of your top starred repos with descriptions |
| `activity.svg` | Recent GitHub events feed |
| `combined.svg` | All banners stacked into one wall |

---

## ✨ Features

- **Auto-updating** — GitHub Actions workflow runs daily, updates everything
- **3 themes** — Dark, Light, Spotify (matches Spotium's design)
- **Zero configuration** — Works out of the box with your GitHub username
- **No tokens required** — Public data works, token gives higher rate limits
- **Minimal dependencies** — Only needs `requests` library
- **Clean SVG output** — Ready to embed in Markdown README files

---

## 🚀 Getting Started

### Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/GitHubWall.git
cd GitHubWall

# 2. Edit config.json with your username
#    Change "username" to your GitHub username

# 3. Install dependencies
pip install -r requirements.txt

# 4. Generate your stats
python generate.py
```

Your stats will be in the `output/` folder. Open the `.svg` files in your browser to see them.

### Configuration

Edit `config.json`:

```json
{
    "username": "your-github-username",
    "token": "",
    "theme": "dark",
    "show_languages": true,
    "show_streak": true,
    "show_stats": true,
    "show_top_repos": true,
    "show_activity": true,
    "max_repos": 6,
    "max_activity": 5,
    "output_dir": "output",
    "combined": true
}
```

| Option | Description | Default |
|--------|-------------|---------|
| `username` | Your GitHub username | — |
| `token` | GitHub personal access token (optional, higher rate limit) | `""` |
| `theme` | Color theme: `dark`, `light`, or `spotify` | `dark` |
| `show_*` | Toggle individual banners on/off | `true` |
| `max_repos` | Number of repos in the top-repos grid | `6` |
| `max_activity` | Number of recent events to show | `5` |
| `combined` | Generate the combined wall SVG | `true` |

---

## 🎨 Themes

| Dark | Light | Spotify |
|------|-------|---------|
| Default GitHub-dark style | Clean white background | Green accent (matches Spotium) |
| `--theme dark` | `--theme light` | `--theme spotify` |

```bash
python generate.py --theme spotify    # Spotify green theme
python generate.py --theme light      # Light mode
```

---

## 🤖 GitHub Actions (Auto-Update)

This project includes a GitHub Actions workflow that:
- **Runs daily** at midnight (UTC)
- **Generates fresh stats** from your GitHub profile
- **Auto-commits** and pushes the updated SVGs

### Setup

1. Push the repo to GitHub
2. GitHub Actions is automatically enabled for public repos
3. That's it — stats update every 24 hours

No manual steps needed. The workflow uses `${{ secrets.GITHUB_TOKEN }}` which GitHub provides automatically to every workflow run.

---

## 📖 Using in Your Profile README

Once the SVGs are generated and pushed to your GitHubWall repo, reference them in your profile README:

```markdown
## My GitHub Stats

![Stats](https://raw.githubusercontent.com/YOUR_USERNAME/GitHubWall/main/output/combined.svg)
```

For side-by-side layout:
```markdown
<p align="center">
  <img src="https://raw.githubusercontent.com/YOUR_USERNAME/GitHubWall/main/output/stats.svg" width="49%">
  <img src="https://raw.githubusercontent.com/YOUR_USERNAME/GitHubWall/main/output/languages.svg" width="49%">
</p>
```

**Important:** Use `raw.githubusercontent.com` URLs so the images render on other people's profiles and in the GitHub README viewer.

---

## 🖼️ Output Examples

### Combined Wall
```
┌─────────────────────────────────────────────────┐
│  Most Used Languages                            │
│  ████████████████████████████ Python    72.3%   │
│  ██████████                       JavaScript 18.1%│
│  ███                              HTML       5.2%│
├─────────────────────────────────────────────────┤
│  GitHub Statistics                              │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐    │
│  │   12   │ │  384   │ │   52   │ │  128   │    │
│  │ Repos  │ │ Stars  │ │ Forks  │ │ Follow │    │
│  └────────┘ └────────┘ └────────┘ └────────┘    │
├─────────────────────────────────────────────────┤
│  Contribution Streak                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────┐ │
│  │   45 days    │ │   12 days    │ │  1,234   │ │
│  │ Longest      │ │ Current      │ │ Total     │ │
│  └──────────────┘ └──────────────┘ └──────────┘ │
├─────────────────────────────────────────────────┤
│  Top Repositories                                │
│  ┌─────────────────┐ ┌─────────────────┐        │
│  │ project-1       │ │ project-2       │        │
│  │ ⭐ 142 · Python │ │ ⭐ 89 · JS     │        │
│  └─────────────────┘ └─────────────────┘        │
└─────────────────────────────────────────────────┘
```

---

## 🛠️ CLI Reference

```bash
python generate.py                                   # Default (uses config.json)
python generate.py --username your-username           # Override username
python generate.py --theme spotify                    # Spotify green theme
python generate.py --token ghp_xxx                    # Provide API token
python generate.py --output ./my-stats                # Custom output directory
python generate.py --no-cache                         # Skip cached data
```

---

## 🛠️ Built With

- **Python 3.8+** — Core logic and SVG generation
- **GitHub REST API v3** — Data fetching (user, repos, events, languages)
- **GitHub Actions** — Scheduled auto-updates
- **SVG** — Pure XML vector graphics (no image libraries needed)

---

## 📄 License

This project is open source. Use it, modify it, share it.

---

<div align="center">
  <p><strong>GitHubWall</strong> — Stats that update themselves.</p>
  <p>
    <a href="https://github.com/AbinashKerketta">GitHub</a>
  </p>
</div>
