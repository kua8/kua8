import json
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone

LOGIN = "kua8"
ACCENT = "#F9A826"
TEXT = "#FFFFFF"
MUTED = "#8B949E"
BG = "#0D1117"
BORDER = "#30363D"
FONT = "'Segoe UI', Ubuntu, sans-serif"
FLAME = "M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"


def gh(query, **variables):
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for k, v in variables.items():
        cmd += ["-f", f"{k}={v}"]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding="utf-8")
    return json.loads(out.stdout)["data"]["user"]


def daily_counts():
    created = datetime.fromisoformat(gh("query($l:String!){user(login:$l){createdAt}}", l=LOGIN)["createdAt"].replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    counts = {}
    for year in range(created.year, now.year + 1):
        start = max(created, datetime(year, 1, 1, tzinfo=timezone.utc))
        end = min(now, datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc))
        user = gh(
            "query($l:String!,$f:DateTime!,$t:DateTime!){user(login:$l){contributionsCollection(from:$f,to:$t){contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}",
            l=LOGIN, f=start.isoformat(), t=end.isoformat(),
        )
        for week in user["contributionsCollection"]["contributionCalendar"]["weeks"]:
            for day in week["contributionDays"]:
                counts[date.fromisoformat(day["date"])] = day["contributionCount"]
    return counts, created.date()


def streaks(counts):
    today = max(counts)
    longest = (0, None, None)
    run_start, run = None, 0
    day = min(counts)
    while day <= today:
        if counts.get(day, 0) > 0:
            run_start = run_start or day
            run += 1
            if run > longest[0]:
                longest = (run, run_start, day)
        else:
            run_start, run = None, 0
        day += timedelta(days=1)
    end = today if counts.get(today, 0) > 0 else today - timedelta(days=1)
    cur_len, day = 0, end
    while counts.get(day, 0) > 0:
        cur_len += 1
        day -= timedelta(days=1)
    current = (cur_len, end - timedelta(days=cur_len - 1) if cur_len else None, end if cur_len else None)
    return current, longest


def span(start, end, today):
    if not start:
        return "No streak yet"
    if start == end:
        return f"{start:%b} {start.day}"
    return f"{start:%b} {start.day} - {end:%b} {end.day}"


def text(x, y, value, size, fill, weight=400):
    return (
        f'<text x="{x}" y="{y}" text-anchor="middle" font-family="{FONT}" '
        f'font-size="{size}" font-weight="{weight}" fill="{fill}">{value}</text>'
    )


def card(counts, since):
    today = max(counts)
    (cur, cs, ce), (lng, ls, le) = streaks(counts)
    total = sum(counts.values())
    since_text = f"{since:%b} {since.day}, {since.year} - Present"
    longest_span = span(ls, le, today)
    if ls and ls.year != today.year:
        longest_span = f"{ls:%b} {ls.day}, {ls.year} - {le:%b} {le.day}, {le.year}"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="495" height="195" viewBox="0 0 495 195" role="img" aria-label="{total:,} total contributions, current streak {cur} days, longest streak {lng} days">
<rect x="0.5" y="0.5" width="494" height="194" rx="8" fill="{BG}" stroke="{BORDER}"/>
<line x1="165" y1="28" x2="165" y2="170" stroke="{ACCENT}" opacity="0.5"/>
<line x1="330" y1="28" x2="330" y2="170" stroke="{ACCENT}" opacity="0.5"/>
{text(82.5, 79, f"{total:,}", 28, TEXT, 700)}
{text(82.5, 112, 'Total Contributions', 14, TEXT)}
{text(82.5, 141, since_text, 11, MUTED)}
<circle cx="247.5" cy="72" r="40" fill="none" stroke="{ACCENT}" stroke-width="5"/>
<rect x="235.5" y="24" width="24" height="20" fill="{BG}"/>
<path transform="translate(237.5 20) scale(0.85)" d="{FLAME}" fill="none" stroke="{ACCENT}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>
{text(247.5, 80, cur, 28, TEXT, 700)}
{text(247.5, 138, 'Current Streak', 14, ACCENT, 700)}
{text(247.5, 159, span(cs, ce, today), 11, MUTED)}
{text(412.5, 79, lng, 28, TEXT, 700)}
{text(412.5, 112, 'Longest Streak', 14, TEXT)}
{text(412.5, 141, longest_span, 11, MUTED)}
</svg>
"""


if __name__ == "__main__":
    counts, since = daily_counts()
    with open(sys.argv[1], "w", encoding="utf-8") as f:
        f.write(card(counts, since))
