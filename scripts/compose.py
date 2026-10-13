#!/usr/bin/env python3
"""Compose captured app screens into store-ready marketing screenshots.

Each panel becomes one upload-ready PNG at exactly the preset's pixel size: a
caption block on top, the captured screen below inside a rounded device frame.

Pillow is the only dependency. An earlier version rendered through headless
Chrome for nicer typography, but a browser is a heavy and unreliable dependency
for what is ultimately a gradient, some centred text, and a rounded rectangle.

Spec file (JSON):

{
  "theme": {
    "background": ["#FAEFEF", "#EBD2D6"],
    "caption_color": "#400911",
    "subcaption_color": "#6B4D55",
    "caption_font": "/path/to/Bold.ttf",
    "subcaption_font": "/path/to/Regular.ttf",
    "frame_color": "#2A1116",
    "frame": "iphone"
  },
  "panels": [
    {
      "screenshot": "out/raw/01-home.png",
      "caption": "Never blank on what to say",
      "subcaption": "A new question every morning",
      "background": ["#FFFFFF", "#F0E6E8"]
    }
  ]
}

"frame" is "iphone" (default: a titanium iPhone body with buttons) or "flat" (a
plain dark rounded rectangle coloured by "frame_color").

"background" is a [top, bottom] gradient pair, or a single "#RRGGBB" for a flat
fill. Everything under "theme" is optional, as are "subcaption" and the
per-panel "background" override. Only "screenshot" and "caption" are required.

Fonts resolve in this order: the spec's explicit path, then the project's
bundled Inter, then Arial. Point caption_font at the app's own typeface when
there is one — matching the in-app type makes the store page feel continuous
with the product.
"""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
except ImportError:
    sys.exit("Pillow is required: python3 -m pip install Pillow")

# Store-required canvas sizes. Confirm against the actual upload page before
# picking one — a listing created earlier may still be asking for an older slot.
PRESETS = {
    "6.9": (1320, 2868),
    "6.7": (1290, 2796),
    "6.5": (1284, 2778),
    "6.5alt": (1242, 2688),
    "ipad13": (2064, 2752),
    "play": (1080, 1920),
}

REPO = Path(__file__).resolve().parents[4]
FONT_CANDIDATES = {
    "bold": [
        REPO / "node_modules/@expo-google-fonts/inter/Inter_700Bold.ttf",
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    ],
    "regular": [
        REPO / "node_modules/@expo-google-fonts/inter/Inter_400Regular.ttf",
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
    ],
}

DEFAULT_THEME = {
    "background": ["#F7F2F3", "#E9D6D9"],
    "caption_color": "#1F1418",
    "subcaption_color": "#5F4148",
    "caption_font": None,
    "subcaption_font": None,
    "frame_color": "#241014",
    "frame": "iphone",
}


def resolve_font(explicit: str | None, weight: str) -> Path:
    if explicit:
        path = Path(explicit).expanduser()
        if not path.is_file():
            sys.exit(f"Font not found: {path}")
        return path
    for candidate in FONT_CANDIDATES[weight]:
        if candidate.is_file():
            return candidate
    sys.exit(
        f"No {weight} font found. Set theme.{'caption' if weight == 'bold' else 'subcaption'}_font "
        "to a .ttf path in the spec."
    )


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    if len(value) == 3:
        value = "".join(c * 2 for c in value)
    if len(value) != 6:
        sys.exit(f"Invalid colour '{value}' — expected #RGB or #RRGGBB.")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def gradient(size: tuple[int, int], spec: object) -> Image.Image:
    """Vertical linear gradient, or a flat fill when given a single colour."""
    width, height = size
    if isinstance(spec, str):
        return Image.new("RGB", size, hex_to_rgb(spec))
    if not isinstance(spec, list) or len(spec) != 2:
        sys.exit('background must be "#RRGGBB" or ["#top", "#bottom"].')

    top, bottom = hex_to_rgb(spec[0]), hex_to_rgb(spec[1])
    # Build one pixel-wide column and stretch it; far cheaper than per-pixel work.
    column = Image.new("RGB", (1, height))
    draw = ImageDraw.Draw(column)
    for y in range(height):
        t = y / max(height - 1, 1)
        draw.point((0, y), tuple(round(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return column.resize(size, Image.BILINEAR)


def wrap_to_width(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> list[str]:
    """Greedy wrap. Captions are short, so simple beats balanced here."""
    words, lines, current = text.split(), [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=font) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def rounded_frame(shot: Image.Image, size: tuple[int, int], radius: int, bezel: int, colour: tuple[int, int, int]) -> Image.Image:
    """Cover-crop the capture into a rounded, bezelled frame on transparency (the flat frame)."""
    width, height = size
    inner_w, inner_h = width - bezel * 2, height - bezel * 2

    scale = max(inner_w / shot.width, inner_h / shot.height)
    resized = shot.resize((round(shot.width * scale), round(shot.height * scale)), Image.LANCZOS)
    left = (resized.width - inner_w) // 2
    top = (resized.height - inner_h) // 2
    inner = resized.crop((left, top, left + inner_w, top + inner_h))

    frame = Image.new("RGBA", size, (*colour, 255))
    frame.paste(inner.convert("RGB"), (bezel, bezel))

    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, width - 1, height - 1], radius=radius, fill=255)
    frame.putalpha(mask)
    return frame


def _vgradient(size: tuple[int, int], top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    return gradient(size, ["#%02x%02x%02x" % top, "#%02x%02x%02x" % bottom]).convert("RGBA")


def iphone_frame(shot: Image.Image, screen_w: int) -> Image.Image:
    """Draw the capture inside an iPhone-16-Pro-style body: titanium rim, black
    bezel, the device's own screen corner radius, action/volume/power buttons.
    Proportions come from the real hardware (393 pt screen in a 71.5 mm body,
    55 pt screen corners). The result is RGBA and includes the button protrusion;
    it is rendered at 3x and downsampled so every curve is anti-aliased."""
    ss = 3
    sw = screen_w * ss
    sh = round(sw * shot.height / shot.width)

    rim = round(sw * 0.013)         # visible titanium edge
    black = round(sw * 0.026)       # black bezel between rim and glass
    border = rim + black
    screen_r = round(sw * 0.140)    # 55 / 393
    body_r = screen_r + border
    protrude = round(sw * 0.013)    # how far the buttons stand out

    body_w, body_h = sw + border * 2, sh + border * 2
    canvas_w, canvas_h = body_w + protrude * 2, body_h
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    ox = protrude  # body offset inside the canvas

    titanium_top, titanium_bottom = (96, 96, 100), (58, 58, 62)

    # Buttons first, so the body overlaps their inner edge.
    def button(side: str, y0: float, y1: float) -> None:
        top_px, bot_px = round(body_h * y0), round(body_h * y1)
        depth = protrude + rim  # tucked under the body so no seam shows
        x0 = ox - protrude if side == "left" else ox + body_w - rim
        x1 = x0 + depth
        btn = _vgradient((x1 - x0, bot_px - top_px), (74, 74, 78), (44, 44, 48))
        mask = Image.new("L", btn.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, btn.width - 1, btn.height - 1], radius=round(protrude * 0.9), fill=255)
        canvas.paste(btn, (x0, top_px), mask)

    button("left", 0.175, 0.200)    # action button
    button("left", 0.228, 0.283)    # volume up
    button("left", 0.298, 0.353)    # volume down
    button("right", 0.258, 0.343)   # side (power) button

    # Titanium body.
    body = _vgradient((body_w, body_h), titanium_top, titanium_bottom)
    body_mask = Image.new("L", (body_w, body_h), 0)
    ImageDraw.Draw(body_mask).rounded_rectangle([0, 0, body_w - 1, body_h - 1], radius=body_r, fill=255)
    canvas.paste(body, (ox, 0), body_mask)

    # A polished chamfer: one light line just inside the outer edge.
    edge = ImageDraw.Draw(canvas)
    edge.rounded_rectangle([ox + 1, 1, ox + body_w - 2, body_h - 2], radius=body_r - 1,
                           outline=(150, 150, 154, 170), width=max(1, ss))

    # Black bezel.
    edge.rounded_rectangle([ox + rim, rim, ox + body_w - rim - 1, body_h - rim - 1],
                           radius=body_r - rim, fill=(8, 8, 10, 255))

    # Glass: cover-crop the capture and round its corners like the real panel.
    scale = max(sw / shot.width, sh / shot.height)
    resized = shot.resize((round(shot.width * scale), round(shot.height * scale)), Image.LANCZOS)
    left, top = (resized.width - sw) // 2, (resized.height - sh) // 2
    glass = resized.crop((left, top, left + sw, top + sh)).convert("RGBA")
    glass_mask = Image.new("L", (sw, sh), 0)
    ImageDraw.Draw(glass_mask).rounded_rectangle([0, 0, sw - 1, sh - 1], radius=screen_r, fill=255)
    canvas.paste(glass, (ox + border, border), glass_mask)

    return canvas.resize((canvas_w // ss, canvas_h // ss), Image.LANCZOS)


def build_panel(panel: dict, theme: dict, width: int, height: int, base: Path = Path(".")) -> Image.Image:
    # Screenshot paths are relative to the spec file, so a spec can live next to its raws.
    src = (base / Path(panel["screenshot"]).expanduser()).resolve()
    if not src.is_file():
        sys.exit(f"Screenshot not found: {src}")

    canvas = gradient((width, height), panel.get("background", theme["background"])).convert("RGBA")
    draw = ImageDraw.Draw(canvas)

    caption_size = round(width * 0.070)
    subcaption_size = round(width * 0.034)
    caption_font = ImageFont.truetype(str(theme["_caption_font"]), caption_size)
    subcaption_font = ImageFont.truetype(str(theme["_subcaption_font"]), subcaption_size)

    pad_x = round(width * 0.085)
    text_width = width - pad_x * 2
    y = round(height * 0.055)

    caption_lines = wrap_to_width(panel.get("caption", ""), caption_font, text_width, draw)
    line_height = round(caption_size * 1.14)
    for line in caption_lines:
        draw.text((width / 2, y), line, font=caption_font,
                  fill=hex_to_rgb(theme["caption_color"]), anchor="ma")
        y += line_height

    if panel.get("subcaption"):
        y += round(subcaption_size * 0.55)
        for line in wrap_to_width(panel["subcaption"], subcaption_font, text_width, draw):
            draw.text((width / 2, y), line, font=subcaption_font,
                      fill=hex_to_rgb(theme["subcaption_color"]), anchor="ma")
            y += round(subcaption_size * 1.35)

    with Image.open(src) as opened:
        shot = opened.convert("RGB")

    style = theme.get("frame", "iphone")
    available_h = height - y - round(height * 0.035)
    if style == "flat":
        bezel = max(3, round(width * 0.0085))
        radius = round(width * 0.062)
        frame_w = round(width * 0.76)
        frame_h = round(frame_w * (shot.height / shot.width))
        if frame_h > available_h:
            frame_h = available_h
            frame_w = round(frame_h * (shot.width / shot.height))
        frame = rounded_frame(shot, (frame_w, frame_h), radius, bezel, hex_to_rgb(theme["frame_color"]))
    else:
        # The whole body (with buttons) is 78% of the canvas; the glass is what remains.
        screen_w = round(width * 0.78 / (1 + 2 * 0.039 + 2 * 0.013))
        frame = iphone_frame(shot, screen_w)
        if frame.height > available_h:
            screen_w = round(screen_w * available_h / frame.height)
            frame = iphone_frame(shot, screen_w)
    frame_w, frame_h = frame.size
    fx = (width - frame_w) // 2
    fy = height - frame_h - round(height * 0.035)

    # Soft drop shadow: blur the frame's own alpha so it follows the rounding.
    blur = round(width * 0.020)
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shadow.paste((31, 20, 24, 110), (fx, fy + round(width * 0.012)), frame.getchannel("A"))
    canvas = Image.alpha_composite(canvas, shadow.filter(ImageFilter.GaussianBlur(blur)))

    canvas.paste(frame, (fx, fy), frame)
    return canvas.convert("RGB")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("spec", help="JSON spec file (schema in this script's docstring)")
    parser.add_argument(
        "--preset", default="6.5", choices=sorted(PRESETS),
        help="output canvas size (default: 6.5 = 1284x2778)",
    )
    parser.add_argument("--out", default="out/final", help="output directory")
    args = parser.parse_args()

    spec = json.loads(Path(args.spec).read_text())
    panels = spec.get("panels") or []
    if not panels:
        sys.exit("Spec contains no panels.")
    if len(panels) > 10:
        sys.exit(f"{len(panels)} panels — the App Store accepts at most 10 (Play: 8).")

    theme = {**DEFAULT_THEME, **spec.get("theme", {})}
    theme["_caption_font"] = resolve_font(theme["caption_font"], "bold")
    theme["_subcaption_font"] = resolve_font(theme["subcaption_font"], "regular")

    width, height = PRESETS[args.preset]
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    for index, panel in enumerate(panels, start=1):
        if "screenshot" not in panel:
            sys.exit(f"Panel {index} is missing the required 'screenshot' key.")
        image = build_panel(panel, theme, width, height, base=Path(args.spec).resolve().parent)
        if image.size != (width, height):
            sys.exit(f"Panel {index} rendered at {image.size}, expected {(width, height)}.")
        out_path = out_dir / f"{index:02d}.png"
        image.save(out_path)
        print(f"  {out_path.name}  {width}x{height}  {panel.get('caption', '')!r}")

    print(f"\n{len(panels)} screenshot(s) in {out_dir}/ at {args.preset} ({width}x{height}).")
    print("Check them at 30% zoom before uploading — that is the size search results use.")


if __name__ == "__main__":
    main()
