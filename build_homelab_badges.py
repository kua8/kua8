import base64
import re
import urllib.request
from pathlib import Path

from PIL import ImageFont

ICONS = "https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons"
FONT = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 13)

SERVICES = {
    "Proxmox VE": ("proxmox", "svg"),
    "OPNsense": ("opnsense", "svg"),
    "CrowdSec": ("crowdsec", "svg"),
    "AdGuard Home": ("adguard-home", "svg"),
    "Nginx Proxy Manager": ("nginx-proxy-manager", "svg"),
    "FRITZ!Box": ("fritzbox", "svg"),
    "Netgear GS308E": ("lucide:network", "svg"),
    "Tenda RX9": ("lucide:router", "svg"),
    "Proxmox Backup Server": ("proxmox-backup-server", "svg"),
    "UrBackup": ("urbackup", "png"),
    "Nextcloud": ("nextcloud", "svg"),
    "Vaultwarden": ("vaultwarden", "svg"),
    "Samba": ("samba-server", "svg"),
    "Apache": ("apache", "svg"),
    "Jellyfin": ("jellyfin", "svg"),
    "Seerr": ("seerr", "svg"),
    "Sonarr": ("sonarr", "svg"),
    "Radarr": ("radarr", "svg"),
    "Prowlarr": ("prowlarr", "svg"),
    "Bazarr": ("bazarr", "svg"),
    "Tdarr": ("tdarr", "svg"),
    "qBittorrent": ("qbittorrent", "svg"),
    "Gluetun": ("gluetun", "svg"),
    "SABnzbd": ("sabnzbd", "svg"),
    "Beszel": ("beszel", "svg"),
    "Dynacat": ("dynacat", "svg"),
}

H, ICON, PAD = 40, 24, 12


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def fetch(icon, ext):
    if icon.startswith("lucide:"):
        url = f"https://cdn.jsdelivr.net/npm/lucide-static@0.469.0/icons/{icon[7:]}.svg"
    else:
        url = f"{ICONS}/{ext}/{icon}.{ext}"
    with urllib.request.urlopen(url, timeout=30) as r:
        data = r.read()
    if icon.startswith("lucide:"):
        data = data.replace(b"currentColor", b"#F9A826")
    return re.sub(rb"<!--[\s\S]*?-->", b"", data) if ext == "svg" else data


def badge(name, icon, ext):
    mime = "image/svg+xml" if ext == "svg" else "image/png"
    data = base64.b64encode(fetch(icon, ext)).decode()
    text_w = round(FONT.getlength(name) * 1.08)
    w = PAD + ICON + 10 + text_w + PAD
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{H}" viewBox="0 0 {w} {H}" role="img" aria-label="{name}">
<rect width="{w}" height="{H}" rx="8" fill="#27272a"/>
<image x="{PAD}" y="{(H - ICON) // 2}" width="{ICON}" height="{ICON}" href="data:{mime};base64,{data}"/>
<text x="{PAD + ICON + 10}" y="25" font-family="Inter,'Segoe UI',Helvetica,Arial,sans-serif" font-size="13" font-weight="600" fill="#fafafa">{name}</text>
</svg>
"""


if __name__ == "__main__":
    out = Path("badges")
    out.mkdir(exist_ok=True)
    for name, (icon, ext) in SERVICES.items():
        (out / f"{slug(name)}.svg").write_text(badge(name, icon, ext), encoding="utf-8")
    print(len(SERVICES), "badges")
