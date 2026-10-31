import json
import subprocess
import sys
from datetime import date

LOGIN = "kua8"
CELL, GAP = 11, 3
STEP = CELL + GAP
LEFT, TOP = 36, 56
LEVELS = {
    "NONE": "#161B22",
    "FIRST_QUARTILE": "#4A3209",
    "SECOND_QUARTILE": "#8A5E10",
    "THIRD_QUARTILE": "#C98A18",
    "FOURTH_QUARTILE": "#F9A826",
}
FONT = "'Segoe UI', Ubuntu, sans-serif"
QUERY = """query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount contributionLevel } }
      }
    }
  }
}"""


def calendar():
    out = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={QUERY}", "-f", f"login={LOGIN}"],
        capture_output=True, text=True, check=True, encoding="utf-8",
    )
    return json.loads(out.stdout)["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def label(x, y, value, anchor="start", fill="#8B949E", size=10):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" font-size="{size}" fill="{fill}">{value}</text>'


def render(cal):
    weeks = cal["weeks"]
    width = LEFT + len(weeks) * STEP + 20
    height = TOP + 7 * STEP + 40
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{cal["totalContributions"]:,} contributions in the last year">',
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="8" fill="#0D1117" stroke="#30363D"/>',
        label(LEFT, 28, f'{cal["totalContributions"]:,} contributions in the last year', fill="#FFFFFF", size=13).replace('font-size="13"', 'font-size="13" font-weight="700"'),
    ]
    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        parts.append(label(LEFT - 8, TOP + row * STEP + CELL - 1, name, anchor="end"))
    months, last_month = [], None
    for col, week in enumerate(weeks):
        first = date.fromisoformat(week["contributionDays"][0]["date"])
        if first.strftime("%b") != last_month and (col == 0 or first.day <= 7):
            months.append((col, first.strftime("%b")))
            last_month = first.strftime("%b")
    for i, (col, name) in enumerate(months):
        if i + 1 == len(months) or months[i + 1][0] - col >= 3:
            parts.append(label(LEFT + col * STEP, TOP - 8, name))
    for col, week in enumerate(weeks):
        for row, day in enumerate(week["contributionDays"]):
            fill = LEVELS[day["contributionLevel"]]
            n = day["contributionCount"]
            parts.append(
                f'<rect x="{LEFT + col * STEP}" y="{TOP + row * STEP}" width="{CELL}" height="{CELL}" rx="2.5" fill="{fill}"><title>{n} contribution{"s" if n != 1 else ""} on {day["date"]}</title></rect>'
            )
    legend_x = width - 20 - 5 * STEP - 62
    legend_y = TOP + 7 * STEP + 14
    parts.append(label(legend_x - 6, legend_y + 9, "Less", anchor="end"))
    for i, color in enumerate(LEVELS.values()):
        parts.append(f'<rect x="{legend_x + i * STEP}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{color}"/>')
    parts.append(label(legend_x + 5 * STEP + 4, legend_y + 9, "More"))
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


if __name__ == "__main__":
    with open(sys.argv[1], "w", encoding="utf-8") as f:
        f.write(render(calendar()))
