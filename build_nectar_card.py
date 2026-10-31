import json
import subprocess
import sys
from datetime import datetime

ACCENT = "#F9A826"
TEXT = "#FFFFFF"
MUTED = "#8B949E"
BG = "#0D1117"
BORDER = "#30363D"
FONT = "'Segoe UI', Ubuntu, sans-serif"


def gh_json(path):
    out = subprocess.run(["gh", "api", path], capture_output=True, text=True, check=True, encoding="utf-8")
    return json.loads(out.stdout)


def nectar_stats():
    repo = gh_json("repos/kua8/Nectar")
    releases = gh_json("repos/kua8/Nectar/releases?per_page=100")
    return {
        "stars": repo["stargazers_count"],
        "forks": repo["forks_count"],
        "downloads": sum(a["download_count"] for r in releases for a in r["assets"]),
        "version": releases[0]["tag_name"],
        "released": datetime.fromisoformat(releases[0]["published_at"].replace("Z", "+00:00")),
    }


def text(x, y, value, size, fill, weight=400):
    return (
        f'<text x="{x}" y="{y}" text-anchor="middle" font-family="{FONT}" '
        f'font-size="{size}" font-weight="{weight}" fill="{fill}">{value}</text>'
    )


def card(s):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="495" height="195" viewBox="0 0 495 195" role="img" aria-label="Nectar: {s['downloads']:,} downloads, {s['stars']} stars, {s['forks']} forks, latest release {s['version']}">
<rect x="0.5" y="0.5" width="494" height="194" rx="8" fill="{BG}" stroke="{BORDER}"/>
<line x1="165" y1="28" x2="165" y2="170" stroke="{ACCENT}" opacity="0.5"/>
<line x1="330" y1="28" x2="330" y2="170" stroke="{ACCENT}" opacity="0.5"/>
{text(82.5, 79, s['stars'], 28, TEXT, 700)}
{text(82.5, 112, 'Stars', 14, TEXT)}
{text(82.5, 141, f"{s['forks']} forks", 12, MUTED)}
<circle cx="247.5" cy="72" r="40" fill="none" stroke="{ACCENT}" stroke-width="5"/>
<rect x="237.5" y="24" width="20" height="16" fill="{BG}"/>
<path d="M247.5 22v12m-5-5 5 6 5-6" fill="none" stroke="{ACCENT}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
{text(247.5, 79, f"{s['downloads']:,}", 20, TEXT, 700)}
{text(247.5, 138, 'Nectar Downloads', 14, ACCENT, 700)}
{text(247.5, 159, 'All releases', 12, MUTED)}
{text(412.5, 79, s['version'], 24, TEXT, 700)}
{text(412.5, 112, 'Latest Release', 14, TEXT)}
{text(412.5, 141, s['released'].strftime('%b %d, %Y'), 12, MUTED)}
</svg>
"""


if __name__ == "__main__":
    with open(sys.argv[1], "w", encoding="utf-8") as f:
        f.write(card(nectar_stats()))
