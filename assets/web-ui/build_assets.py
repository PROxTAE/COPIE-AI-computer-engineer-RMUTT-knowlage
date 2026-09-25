"""Build reusable COPIE web UI vectors and collect source mascot assets."""

from __future__ import annotations

import json
import shutil
from pathlib import Path


OUT = Path(__file__).resolve().parent
PROJECT = OUT.parents[1]


def write(relative: str, content: str) -> None:
    target = OUT / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.strip() + "\n", encoding="utf-8")


VECTORS = {
    "brand/copie-mark.svg": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none">
  <path d="M12 27 18 9l12 10h4L46 9l6 18v17c0 9-8 16-20 16S12 53 12 44V27Z" fill="#fff" stroke="#1E3159" stroke-width="2"/>
  <path d="M16 22c3-10 29-10 32 0" stroke="#12274D" stroke-width="5" stroke-linecap="round"/>
  <rect x="8" y="25" width="8" height="18" rx="4" fill="#155FF2"/>
  <rect x="48" y="25" width="8" height="18" rx="4" fill="#155FF2"/>
  <path d="M52 42c0 7-4 9-9 9" stroke="#12274D" stroke-width="3" stroke-linecap="round"/>
  <ellipse cx="24" cy="35" rx="3" ry="5" fill="#155FF2"/>
  <ellipse cx="40" cy="35" rx="3" ry="5" fill="#155FF2"/>
  <circle cx="43" cy="51" r="2.5" fill="#12274D"/>
</svg>
""",
    "brand/favicon.svg": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none">
  <rect width="64" height="64" rx="15" fill="#155FF2"/>
  <path d="M11 28 17 11l12 10h6l12-10 6 17v15c0 10-8 16-21 16S11 53 11 43V28Z" fill="#fff"/>
  <path d="M14 25c3-10 33-10 36 0" stroke="#12274D" stroke-width="5" stroke-linecap="round"/>
  <ellipse cx="23" cy="37" rx="3" ry="5" fill="#155FF2"/>
  <ellipse cx="41" cy="37" rx="3" ry="5" fill="#155FF2"/>
  <path d="M52 39c0 7-2 10-8 11" stroke="#12274D" stroke-width="3" stroke-linecap="round"/>
  <circle cx="44" cy="50" r="2.5" fill="#12274D"/>
</svg>
""",
    "backgrounds/grid-light.svg": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" fill="none">
  <defs>
    <pattern id="grid" width="80" height="80" patternUnits="userSpaceOnUse">
      <path d="M80 0H0V80" stroke="#3078D4" stroke-opacity=".11" stroke-width="1"/>
    </pattern>
    <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
      <stop stop-color="white" stop-opacity=".62"/>
      <stop offset=".55" stop-color="white" stop-opacity=".92"/>
      <stop offset="1" stop-color="white" stop-opacity=".32"/>
    </linearGradient>
    <mask id="grid-mask"><rect width="1600" height="900" fill="url(#fade)"/></mask>
  </defs>
  <rect width="1600" height="900" fill="url(#grid)" mask="url(#grid-mask)"/>
  <g stroke="#2475DA" stroke-opacity=".35" stroke-width="1">
    <path d="M39 0v24M27 12h24M1561 0v24M1549 12h24M39 876v24M27 888h24M1561 876v24M1549 888h24"/>
  </g>
</svg>
""",
    "backgrounds/floor-perspective.svg": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 360" fill="none">
  <defs>
    <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
      <stop stop-color="#84C9F1" stop-opacity="0"/>
      <stop offset="1" stop-color="#84C9F1" stop-opacity=".35"/>
    </linearGradient>
  </defs>
  <path d="M0 360 800 0 1600 360" fill="url(#fade)" opacity=".14"/>
  <g stroke="#1685DE" stroke-opacity=".16" stroke-width="1">
    <path d="M800 0 0 360M800 0 200 360M800 0 400 360M800 0 600 360M800 0 1000 360M800 0 1200 360M800 0 1400 360M800 0 1600 360"/>
    <path d="M0 320h1600M0 250h1600M0 190h1600M0 138h1600M0 94h1600M0 58h1600"/>
  </g>
  <path d="M0 0h1600" stroke="#1685DE" stroke-opacity=".12"/>
</svg>
""",
    "backgrounds/mascot-halo.svg": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 720" fill="none">
  <defs>
    <radialGradient id="soft"><stop stop-color="#63D6F1" stop-opacity=".1"/><stop offset="1" stop-color="#63D6F1" stop-opacity="0"/></radialGradient>
  </defs>
  <circle cx="360" cy="360" r="342" fill="url(#soft)"/>
  <circle cx="360" cy="360" r="300" stroke="#47C8EA" stroke-opacity=".28" stroke-width="2" stroke-dasharray="2 12"/>
  <circle cx="360" cy="360" r="274" stroke="#1578D7" stroke-opacity=".19" stroke-width="1.5"/>
  <circle cx="360" cy="360" r="250" stroke="#7EDCF0" stroke-opacity=".24" stroke-width="1"/>
  <path d="M117 190a285 285 0 0 1 90-93M510 99a285 285 0 0 1 92 92M602 529a285 285 0 0 1-90 92M210 622a285 285 0 0 1-93-91" stroke="#155CF2" stroke-opacity=".5" stroke-width="3" stroke-linecap="round"/>
  <g fill="#1D80DC" fill-opacity=".5"><circle cx="112" cy="360" r="3"/><circle cx="608" cy="360" r="3"/><circle cx="360" cy="112" r="3"/><circle cx="360" cy="608" r="3"/></g>
</svg>
""",
    "backgrounds/cyan-wash.svg": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 400" fill="none">
  <defs>
    <linearGradient id="wash" x1="0" y1="0" x2="0" y2="1">
      <stop stop-color="#E7F9FF" stop-opacity="0"/>
      <stop offset="1" stop-color="#D7F4FE" stop-opacity=".65"/>
    </linearGradient>
  </defs>
  <rect width="1600" height="400" fill="url(#wash)"/>
</svg>
""",
    "frames/corner-accent.svg": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 56 56" fill="none">
  <path d="M55 1H12A11 11 0 0 0 1 12v43" stroke="#185FF1" stroke-width="1.5"/>
  <path d="M33 1h22" stroke="#46CFEA" stroke-width="2"/>
  <circle cx="1" cy="55" r="2" fill="#185FF1"/>
</svg>
""",
    "frames/response-rule.svg": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 16" fill="none">
  <defs><linearGradient id="line"><stop stop-color="#165DF2"/><stop offset=".35" stop-color="#51D5EF" stop-opacity=".8"/><stop offset="1" stop-color="#51D5EF" stop-opacity="0"/></linearGradient></defs>
  <rect y="7" width="640" height="1" fill="url(#line)"/>
  <rect y="4" width="28" height="7" fill="#155FF2"/>
  <rect x="35" y="5" width="9" height="5" fill="#44D2E9"/>
</svg>
""",
    "frames/side-rail.svg": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 720" fill="none">
  <path d="M12 0v720" stroke="#1B75D7" stroke-opacity=".24"/>
  <path d="M12 65v105M12 400v94" stroke="#0F65F0" stroke-width="2"/>
  <rect x="9" y="58" width="6" height="6" fill="#0F65F0"/>
  <circle cx="12" cy="514" r="3" fill="#42D3EA"/>
</svg>
""",
    "effects/data-streak.svg": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 64" fill="none">
  <defs><linearGradient id="streak"><stop stop-color="#54D8ED" stop-opacity=".85"/><stop offset="1" stop-color="#54D8ED" stop-opacity="0"/></linearGradient></defs>
  <path d="M0 14h480M28 27h386M0 42h450M90 54h302" stroke="url(#streak)" stroke-width="2"/>
  <rect x="0" y="10" width="46" height="8" fill="#42CEE9" fill-opacity=".35"/>
  <rect x="54" y="39" width="20" height="6" fill="#1768F0" fill-opacity=".2"/>
</svg>
""",
    "effects/signal-dots.svg": """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96" fill="none">
  <defs><pattern id="dots" width="16" height="16" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.5" fill="#1578E0" fill-opacity=".42"/></pattern></defs>
  <rect width="96" height="96" fill="url(#dots)"/>
</svg>
""",
}


ICON_SHAPES = {
    "profile": '<circle cx="12" cy="8" r="3.5"/><path d="M5 20a7 7 0 0 1 14 0"/>',
    "history": '<path d="M3 12a9 9 0 1 0 2.6-6.4"/><path d="M3 4v4h4M12 7v5l3.5 2"/>',
    "send": '<path d="m3 11 18-8-8 18-2.5-7.5L3 11Z"/><path d="m10.5 13.5 5-5"/>',
    "search": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
    "close": '<path d="M5 5 19 19M19 5 5 19"/>',
    "arrow-left": '<path d="M19 12H5m6-6-6 6 6 6"/>',
    "chevron-right": '<path d="m9 5 7 7-7 7"/>',
    "document": '<path d="M6 2h8l4 4v16H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2Z"/><path d="M14 2v5h5M8 12h8M8 16h7"/>',
    "book-open": '<path d="M12 6c-2.5-2-5.5-2-9-1v14c3.5-1 6.5-1 9 1 2.5-2 5.5-2 9-1V5c-3.5-1-6.5-1-9 1Z"/><path d="M12 6v14"/>',
    "chart-bars": '<path d="M3 21h18M5 21v-6h3v6M11 21V9h3v12M17 21V4h3v17"/>',
    "graduation-cap": '<path d="m2 9 10-5 10 5-10 5L2 9Z"/><path d="M6 12v5c3.5 3 8.5 3 12 0v-5M22 9v7"/>',
    "copy": '<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h3"/>',
    "thumb-up": '<path d="M7 10v11H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3ZM7 10l5-7a2 2 0 0 1 3.5 1.4L15 8h4a3 3 0 0 1 2.9 3.8l-2.1 7A3 3 0 0 1 17 21H7"/>',
    "thumb-down": '<path d="M7 14V3H4a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h3ZM7 14l5 7a2 2 0 0 0 3.5-1.4L15 16h4a3 3 0 0 0 2.9-3.8l-2.1-7A3 3 0 0 0 17 3H7"/>',
    "eye-off": '<path d="M3 3 21 21M10.5 5.2c.5-.1 1-.2 1.5-.2 5 0 8.5 4 10 7-1 2.1-2.6 4-4.6 5.2M6.2 6.3C4.3 7.6 3 9.6 2 12c1.5 3 5 7 10 7 1.4 0 2.6-.3 3.7-.8"/><path d="M9.6 9.6a3.4 3.4 0 0 0 4.8 4.8"/>',
    "refresh": '<path d="M20 7a8 8 0 0 0-14-2L4 7M4 3v4h4M4 17a8 8 0 0 0 14 2l2-2M20 21v-4h-4"/>',
    "menu": '<path d="M4 6h16M4 12h16M4 18h16"/>',
    "spark": '<path d="M12 2 14 10l8 2-8 2-2 8-2-8-8-2 8-2 2-8Z"/>',
    "filter": '<path d="M3 4h18l-7 8v6l-4 2v-8L3 4Z"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 2v6M17 2v6M3 10h18"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7h.01"/>',
}


def build() -> None:
    for path, svg in VECTORS.items():
        write(path, svg)

    for name, shape in ICON_SHAPES.items():
        write(
            f"icons/{name}.svg",
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
            'fill="none" stroke="currentColor" stroke-width="1.8" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            + shape
            + "</svg>",
        )

    source_states = PROJECT / "assets" / "mascot" / "states"
    state_names = (
        "copie-front-laptop",
        "copie-idle",
        "copie-listening",
        "copie-thinking",
        "copie-responding",
        "copie-success",
        "copie-no-answer",
        "copie-skill-guide",
    )
    state_dir = OUT / "mascot" / "states"
    state_dir.mkdir(parents=True, exist_ok=True)
    for name in state_names:
        shutil.copy2(source_states / f"{name}.png", state_dir / f"{name}.png")

    model_source = PROJECT / "frontend" / "public" / "models" / "copie-mascot-web.glb"
    model_target = OUT / "mascot" / "3d" / model_source.name
    model_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(model_source, model_target)

    manifest = {
        "name": "COPIE white cyberism web UI assets",
        "version": 1,
        "brand": sorted(path for path in VECTORS if path.startswith("brand/")),
        "backgrounds": sorted(path for path in VECTORS if path.startswith("backgrounds/")),
        "frames": sorted(path for path in VECTORS if path.startswith("frames/")),
        "effects": sorted(path for path in VECTORS if path.startswith("effects/")),
        "icons": [f"icons/{name}.svg" for name in sorted(ICON_SHAPES)],
        "mascot_states": [f"mascot/states/{name}.png" for name in state_names],
        "mascot_3d": "mascot/3d/copie-mascot-web.glb",
        "styles": ["styles/tokens.css", "styles/copie-ui.css", "styles/motion.css"],
        "guide": "ASSET_GUIDE.md",
        "preview": "preview.html",
    }
    write("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    build()
