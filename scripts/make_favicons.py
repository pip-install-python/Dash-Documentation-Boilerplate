"""Regenerate the full favicon set from one source image.

    python scripts/make_favicons.py assets/ddb.png

Every satellite runs this against ITS OWN identity image (the wave keeps
source art at https://cdn.2plot.ai/github_assets/favicons/<app>.png) and
gets the exact file set the template wires in templates/index.html and
run.py's configure_seo(icons=[...]) — same names, same sizes, so neither
head needs editing:

    assets/favicon.ico                          16+32+48 multi-size ICO
    assets/favicon/favicon.ico                  (same, the redirect target)
    assets/favicon/favicon-16x16.png
    assets/favicon/favicon-32x32.png
    assets/favicon/favicon-96x96.png
    assets/favicon/apple-touch-icon.png         180x180
    assets/favicon/android-chrome-192x192.png
    assets/favicon/android-chrome-512x512.png

The source is padded to a centred square on a transparent canvas first, so
a non-square logo (the template's own is 784x741) never ships stretched.
Remember the OTHER half of identity: assets/favicon/site.webmanifest's
name/short_name/description are per-app text — this script deliberately
does not touch them.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

SIZES = {
    "favicon-16x16.png": 16,
    "favicon-32x32.png": 32,
    "favicon-96x96.png": 96,
    "apple-touch-icon.png": 180,
    "android-chrome-192x192.png": 192,
    "android-chrome-512x512.png": 512,
}


def make(source: str | Path, repo_root: str | Path = ".") -> list[Path]:
    root = Path(repo_root)
    src = Image.open(source).convert("RGBA")
    side = max(src.size)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(src, ((side - src.width) // 2, (side - src.height) // 2))

    out_dir = root / "assets" / "favicon"
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name, px in SIZES.items():
        path = out_dir / name
        resized = canvas.resize((px, px), Image.LANCZOS)
        if name == "apple-touch-icon.png":
            # iOS composites the icon's alpha channel onto ITS OWN
            # background (black on some surfaces, white on others), so a
            # transparent apple-touch icon renders differently everywhere
            # it appears. Flatten onto opaque white — iOS rounds the
            # corners itself. Every OTHER size keeps its transparency;
            # browsers and Android handle alpha correctly.
            # tests/test_seo_icons.py pins the opacity by reading the PNG
            # colour type out of the file header.
            flat = Image.new("RGB", (px, px), (255, 255, 255))
            flat.paste(resized, mask=resized.getchannel("A"))
            flat.save(path, optimize=True)
        else:
            resized.save(path, optimize=True)
        written.append(path)

    ico_base = canvas.resize((48, 48), Image.LANCZOS)
    for path in (out_dir / "favicon.ico", root / "assets" / "favicon.ico"):
        ico_base.save(path, sizes=[(16, 16), (32, 32), (48, 48)])
        written.append(path)
    return written


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python scripts/make_favicons.py <source-image.png>")
    for path in make(sys.argv[1]):
        print(f"  wrote {path}")
    print("Done. site.webmanifest name/short_name is yours to edit by hand.")
