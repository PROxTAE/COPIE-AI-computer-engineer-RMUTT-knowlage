"""Copy the design kit (assets/web-ui) into the frontend. Owner: P1.

assets/web-ui/ stays the master copy from design. Run this after the kit changes:

    python scripts/sync_ui_assets.py

- SVGs (brand, backgrounds, frames, effects, icons) -> frontend/public/copie-ui/
- Mascot state PNGs -> WebP in frontend/public/copie-ui/mascot/ (needs Pillow)
- Mode mascot PNGs -> WebP in frontend/public/copie-ui/mascot/modes/<mode>/
- Kit CSS -> frontend/src/modules/core/theme/kit/ with URLs pointing at /copie-ui/
- brand/favicon.svg -> frontend/src/app/icon.svg
"""
import re
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / "assets" / "web-ui"
PUBLIC = ROOT / "frontend" / "public" / "copie-ui"
THEME = ROOT / "frontend" / "src" / "modules" / "core" / "theme" / "kit"
SVG_DIRS = ["brand", "backgrounds", "frames", "effects", "icons"]


def sync_svgs() -> int:
    count = 0
    for name in SVG_DIRS:
        target = PUBLIC / name
        shutil.rmtree(target, ignore_errors=True)
        target.mkdir(parents=True)
        for svg in sorted((KIT / name).glob("*.svg")):
            shutil.copy2(svg, target / svg.name)
            count += 1
    return count


def sync_mascot() -> list[str]:
    target = PUBLIC / "mascot"
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True)
    written = []
    for png in sorted((KIT / "mascot" / "states").glob("*.png")):
        out = target / f"{png.stem}.webp"
        with Image.open(png) as image:
            image.save(out, "WEBP", quality=88, method=6)
        written.append(f"{out.name} ({out.stat().st_size // 1024} KB)")
    for mode in ("devil", "developer"):
        mode_target = target / "modes" / mode
        mode_target.mkdir(parents=True, exist_ok=True)
        for png in sorted((KIT / "mascot" / "modes" / mode / "states").glob("*.png")):
            out = mode_target / f"{png.stem}.webp"
            with Image.open(png) as image:
                image.save(out, "WEBP", quality=88, method=6)
            written.append(f"{mode}/{out.name} ({out.stat().st_size // 1024} KB)")
    return written


def sync_styles() -> None:
    THEME.mkdir(parents=True, exist_ok=True)
    for css in sorted((KIT / "styles").glob("*.css")):
        text = css.read_text(encoding="utf-8")
        text = re.sub(r'url\("\.\./([a-z-]+)/', r'url("/copie-ui/\1/', text)
        header = f"/* Synced from assets/web-ui/styles/{css.name} by scripts/sync_ui_assets.py - do not edit here. */\n"
        (THEME / css.name).write_text(header + text, encoding="utf-8", newline="\n")


def main() -> None:
    svg_count = sync_svgs()
    mascots = sync_mascot()
    sync_styles()
    shutil.copy2(KIT / "brand" / "favicon.svg", ROOT / "frontend" / "src" / "app" / "icon.svg")
    print(f"svg: {svg_count} files")
    print("mascot:", ", ".join(mascots))
    print(f"styles: {THEME.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
