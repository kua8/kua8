import json
import os
import random
import subprocess
import sys

os.environ["GIFOS_GENERAL_COLOR_SCHEME"] = "gruvbox-dark"
os.environ["GIFOS_GRUVBOX-DARK_DEFAULT_COLORS_BG"] = "#0d1117"

import gifos
import imageio_ffmpeg

AMBER = "\x1b[93m"
GREEN = "\x1b[92m"
RED = "\x1b[91m"
CYAN = "\x1b[96m"
GREY = "\x1b[90m"
RESET = "\x1b[0m"

LOGO = [
    "##  ##   #### ",
    "## ##   ##  ##",
    "####     #### ",
    "####     #### ",
    "## ##   ##  ##",
    "##  ##   #### ",
]


def gh_json(path):
    out = subprocess.run(["gh", "api", path], capture_output=True, text=True, check=True, encoding="utf-8")
    return json.loads(out.stdout)


def nectar_stats():
    stars = gh_json("repos/kua8/Nectar")["stargazers_count"]
    releases = gh_json("repos/kua8/Nectar/releases?per_page=100")
    downloads = sum(a["download_count"] for r in releases for a in r["assets"])
    return stars, f"{downloads / 1000:.0f}k"


def boot(t):
    t.toggle_show_cursor(False)
    t.gen_text(f"{AMBER}K8 Modular BIOS v17.0{RESET}", 1)
    t.gen_text("Vienna Works, Austria", 2)
    t.gen_text("Press DEL to enter SETUP", t.num_rows)
    for kb in range(0, 65537, 16384):
        t.delete_row(4)
        t.gen_text(f"Memory Test: {kb}K", 4, count=1, contin=True)
    t.delete_row(4)
    t.gen_text(f"Memory Test: 64K {GREEN}OK{RESET}", 4, count=3, contin=True)
    t.gen_text("Detecting drives...", 6, count=2, contin=True)
    t.gen_text(f"  Primary Master : {RED}None{RESET}", 7, count=2, contin=True)
    t.gen_text(f"  Trades         : {GREEN}All{RESET}", 8, count=8, contin=True)
    t.clear_frame()


def login(t):
    t.gen_text(f"{AMBER}K8 OS v17.0 (tty1){RESET}", 1, count=2)
    t.gen_text("login: ", 3, count=2)
    t.toggle_show_cursor(True)
    t.gen_typing_text("kua8", 3, contin=True)
    t.toggle_show_cursor(False)
    t.gen_text("password: ", 4, count=2)
    t.toggle_show_cursor(True)
    t.gen_typing_text("********", 4, contin=True)
    t.toggle_show_cursor(False)
    t.gen_text(f"{GREY}Welcome back.{RESET}", 6, count=4)


def fetch(t, stars, downloads):
    t.clear_frame()
    t.set_prompt(f"{GREEN}kua8{RESET}@{AMBER}homelab{RESET} ~> ")
    t.gen_prompt(1, count=3)
    col = t.curr_col
    t.toggle_show_cursor(True)
    t.gen_typing_text(f"{RED}neofet", 1, contin=True)
    t.delete_row(1, col)
    t.gen_text(f"{GREEN}neofetch{RESET}", 1, count=3, contin=True)
    t.toggle_show_cursor(False)

    for i, line in enumerate(LOGO):
        t.gen_text(f"{AMBER}{line}{RESET}", 5 + i, 3)

    rows = [
        ("Role", "System Engineer"),
        ("Roots", "Front-End Developer"),
        ("Uptime", "17 years"),
        ("Location", "Vienna, Austria"),
        ("Homelab", "Proxmox VE, 20+ self-hosted services"),
        ("Security", "OPNsense, CrowdSec, PBS backups"),
        ("Languages", "TypeScript, Rust, C#, Lua"),
        ("Nectar", f"{stars} stars, {downloads} downloads"),
        ("Nexus Mods", "90k downloads"),
        ("Master of", "None"),
    ]
    t.gen_text(f"{AMBER}kua8{RESET}@{AMBER}homelab{RESET}", 3, 24, count=2, contin=True)
    t.gen_text("-" * 12, 4, 24, count=2, contin=True)
    for i, (key, value) in enumerate(rows):
        t.gen_text(f"{CYAN}{key + ':':<12}{RESET}{value}", 5 + i, 24, count=3, contin=True)


def projects(t):
    t.gen_prompt(16, count=3)
    t.toggle_show_cursor(True)
    t.gen_typing_text(f"{GREEN}ls{RESET} projects/", 16, contin=True)
    t.toggle_show_cursor(False)
    t.gen_text(f"{CYAN}nectar/{RESET}      notch and dock for Windows, in Rust and Tauri", 17, count=3)
    t.gen_text(f"{CYAN}homelab/{RESET}     20+ services on Proxmox, see HOMELAB.md", 18, count=3)
    t.gen_text(f"{CYAN}nexus-mods/{RESET}  C# mods for Unity games", 19, count=3)
    t.gen_prompt(21)
    t.toggle_show_cursor(True)
    t.clone_frame(60)


def main():
    output = os.path.abspath(sys.argv[1])
    stars, downloads = nectar_stats()
    random.seed(17)
    t = gifos.Terminal(750, 405, 15, 15)
    t.set_fps(15)
    boot(t)
    login(t)
    fetch(t, stars, downloads)
    projects(t)

    subprocess.run(
        [
            imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error",
            "-r", "15", "-i", "frames/frame_%d.png",
            "-filter_complex", "[0:v] split [a][b];[a] palettegen [p];[b][p] paletteuse",
            output,
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
