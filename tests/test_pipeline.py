"""Comprehensive test suite for GitHubWall."""
import sys, os
# Ensure the parent of the tests/ dir is on the path
test_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(test_dir)
sys.path.insert(0, project_dir)

from githubwall.api import GitHubAPI
from githubwall.renderer import Renderer
from githubwall.stats import compute_streak
from githubwall.themes import get_theme

USER = "AbinashKerketta"
passed = 0
failed = 0

def test(name, fn):
    global passed, failed
    try:
        fn()
        print(f"  [PASS] {name}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")
        failed += 1

print("=== FULL PIPELINE TEST ===\n")

api = GitHubAPI(USER)
r = Renderer("dark")

# Test 1: User fetch
def t1():
    u = api.get_user()
    assert u is not None
    assert u["login"] == USER
    print(f"    Name: {u.get('name')}")
    print(f"    Repos: {u.get('public_repos')}")
test("API - Fetch user", t1)

# Test 2: Repos
def t2():
    repos = api.get_repos()
    assert len(repos) > 0
    print(f"    Found: {len(repos)} repos")
test("API - Fetch repos", t2)

# Test 3: Languages
def t3():
    langs = api.get_combined_languages()
    assert len(langs) > 0
    total = sum(langs.values())
    print(f"    Languages: {len(langs)} ({total} bytes)")
    for lang, c in sorted(langs.items(), key=lambda x: x[1], reverse=True):
        print(f"      {lang}: {c/total*100:.1f}%")
test("API - Languages", t3)

# Test 4: Stats
def t4():
    stats = api.get_total_stats()
    assert stats["public_repos"] > 0
    print(f"    Repos: {stats['public_repos']}, Stars: {stats['total_stars']}, Forks: {stats['total_forks']}")
test("API - Total stats", t4)

# Test 5: Top repos
def t5():
    top = api.get_top_repos(6)
    assert len(top) > 0
    print(f"    Top {len(top)} repos: {', '.join(r['name'] for r in top)}")
test("API - Top repos", t5)

# Test 6: Events
def t6():
    events = api.get_events()
    assert len(events) > 0
    print(f"    {len(events)} events fetched")
test("API - Events", t6)

# Test 7: Streak
def t7():
    events = api.get_events()
    s = compute_streak(events)
    print(f"    Longest: {s['longest_streak']}d, Current: {s['current_streak']}d, Total: {s['total_contributions']}")
    assert isinstance(s["longest_streak"], int)
test("Stats - Streak", t7)

# Test 8: Language SVG
def t8():
    langs = api.get_combined_languages()
    svg = r.render_languages(langs)
    assert svg.startswith("<svg")
    assert svg.endswith("</svg>")
    assert "Most Used Languages" in svg
    print(f"    Size: {len(svg)} bytes")
test("Render - Languages SVG", t8)

# Test 9: Stats SVG
def t9():
    stats = api.get_total_stats()
    svg = r.render_stats(stats)
    assert svg.startswith("<svg"), "Does not start with <svg"
    assert "GitHub Statistics" in svg
    print(f"    Size: {len(svg)} bytes")
test("Render - Stats SVG", t9)

# Test 10: Streak SVG
def t10():
    events = api.get_events()
    s = compute_streak(events)
    svg = r.render_streak(s)
    assert svg.startswith("<svg")
    assert "Contribution Streak" in svg
    print(f"    Size: {len(svg)} bytes")
test("Render - Streak SVG", t10)

# Test 11: Top repos SVG
def t11():
    repos = api.get_top_repos(6)
    svg = r.render_top_repos(repos)
    assert svg.startswith("<svg")
    assert "Top Repositories" in svg
    print(f"    Size: {len(svg)} bytes")
test("Render - Top Repos SVG", t11)

# Test 12: Activity SVG
def t12():
    events = api.get_recent_activity(5)
    svg = r.render_activity(events)
    assert svg.startswith("<svg")
    assert "Recent Activity" in svg
    print(f"    Size: {len(svg)} bytes")
test("Render - Activity SVG", t12)

# Test 13: Combined SVG
def t13():
    svgs = []
    langs = api.get_combined_languages()
    stats = api.get_total_stats()
    svgs.append(r.render_languages(langs))
    svgs.append(r.render_stats(stats))
    combined = r.render_combined(svgs)
    assert combined.startswith("<svg")
    assert "</svg>" in combined
    print(f"    Size: {len(combined)} bytes")
test("Render - Combined SVG", t13)

# Test 14: All themes
def t14():
    from githubwall.themes import THEMES
    for name in THEMES:
        t = get_theme(name)
        assert len(t) == 15, f"Theme {name} missing keys"
    print(f"    Themes: {', '.join(THEMES.keys())}")
test("Themes - All valid", t14)

# Test 15: Empty languages
def t15():
    svg = r.render_languages({})
    assert "No language data" in svg
test("Edge case - Empty languages", t15)

# Test 16: Empty repos
def t16():
    svg = r.render_top_repos([])
    assert "No repos to display" in svg
test("Edge case - Empty repos", t16)

# Test 17: Empty activity
def t17():
    svg = r.render_activity([])
    assert "No recent activity" in svg
test("Edge case - Empty activity", t17)

# Test 18: File save
def t18():
    import tempfile
    tmp = tempfile.mkdtemp()
    svg = r.render_stats(api.get_total_stats())
    path = r.save_svg(svg, "test.svg", tmp)
    assert os.path.exists(path)
    assert open(path).read().startswith("<svg")
    os.remove(path)
    os.rmdir(tmp)
    print(f"    Saved to temp dir, verified")
test("Save - File output", t18)

# Test 19: CLI without token (should work)
def t19():
    import subprocess
    result = subprocess.run(
        [sys.executable, "generate.py", "--username", USER, "--output", "test_output", "--combined"],
        capture_output=True, text=True, timeout=120, cwd=project_dir
    )
    if result.returncode != 0:
        raise Exception(f"CLI failed: {result.stderr}")
    assert "Generated" in result.stdout
    print(f"    Output lines: {len(result.stdout.split(chr(10)))}")
    # Cleanup
    import shutil
    test_out = os.path.join(project_dir, "test_output")
    if os.path.exists(test_out):
        shutil.rmtree(test_out)
test("CLI - Full run", t19)

print(f"\n=== RESULTS: {passed} passed, {failed} failed, {passed+failed} total ===")
if failed > 0:
    sys.exit(1)
