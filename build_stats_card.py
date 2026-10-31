import json
import subprocess
import sys

ACCENT = "#F9A826"
TEXT = "#FFFFFF"
MUTED = "#8B949E"
BG = "#0D1117"
BORDER = "#30363D"
FONT = "'Segoe UI', Ubuntu, sans-serif"


def gh_json(path):
    out = subprocess.run(["gh", "api", path], capture_output=True, text=True, check=True, encoding="utf-8")
    return json.loads(out.stdout)


def totals():
    repos = [r for r in gh_json("users/kua8/repos?type=owner&per_page=100") if not r["fork"]]
    downloads = 0
    for r in repos:
        releases = gh_json(f"repos/kua8/{r['name']}/releases?per_page=100")
        downloads += sum(a["download_count"] for rel in releases for a in rel["assets"])
    return {
        "stars": sum(r["stargazers_count"] for r in repos),
        "forks": sum(r["forks_count"] for r in repos),
        "repos": len(repos),
        "downloads": downloads,
    }


def text(x, y, value, size, fill, weight=400):
    return (
        f'<text x="{x}" y="{y}" text-anchor="middle" font-family="{FONT}" '
        f'font-size="{size}" font-weight="{weight}" fill="{fill}">{value}</text>'
    )


def card(s):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="495" height="195" viewBox="0 0 495 195" role="img" aria-label="{s['downloads']:,} downloads, {s['stars']} stars, {s['forks']} forks across {s['repos']} public repositories">
<rect x="0.5" y="0.5" width="494" height="194" rx="8" fill="{BG}" stroke="{BORDER}"/>
<line x1="165" y1="28" x2="165" y2="170" stroke="{ACCENT}" opacity="0.5"/>
<line x1="330" y1="28" x2="330" y2="170" stroke="{ACCENT}" opacity="0.5"/>
{text(82.5, 79, s['stars'], 28, TEXT, 700)}
{text(82.5, 112, 'Total Stars', 14, TEXT)}
{text(82.5, 141, f"{s['repos']} repositories", 12, MUTED)}
<circle cx="247.5" cy="72" r="40" fill="none" stroke="{ACCENT}" stroke-width="5"/>
<rect x="237.5" y="24" width="20" height="16" fill="{BG}"/>
<path d="M247.5 22v12m-5-5 5 6 5-6" fill="none" stroke="{ACCENT}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
{text(247.5, 79, f"{s['downloads']:,}", 20, TEXT, 700)}
{text(247.5, 138, 'Total Downloads', 14, ACCENT, 700)}
{text(247.5, 159, 'All releases', 12, MUTED)}
{text(412.5, 79, s['forks'], 28, TEXT, 700)}
{text(412.5, 112, 'Total Forks', 14, TEXT)}
{text(412.5, 141, 'All repositories', 12, MUTED)}
</svg>
"""


if __name__ == "__main__":
    with open(sys.argv[1], "w", encoding="utf-8") as f:
        f.write(card(totals()))
