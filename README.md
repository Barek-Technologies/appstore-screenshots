# App Store Screenshots — an agent skill

A [Claude Code](https://claude.com/claude-code) skill that turns raw app screens
into caption-led, conversion-focused App Store and Google Play screenshots at the
exact pixel sizes the stores accept.

It does two separate jobs:

1. **Decide** which screens go in which slots, and what caption sits on each.
   This is where installs are won or lost, so the skill makes the agent read
   your app, plan the sequence and show you the captions as plain text before
   anything is rendered.
2. **Render** those decisions into upload-ready PNGs: a gradient background,
   a headline caption and your screen inside a device frame.

## What's inside

| File | Purpose |
| --- | --- |
| `SKILL.md` | The workflow the agent follows: target size, screen choice, captions, capture, compose, verify |
| `references/conversion-psychology.md` | Slot-by-slot framework for ordering screenshots and writing captions |
| `scripts/capture.sh` | Captures the booted iOS simulator or an attached Android device/emulator |
| `scripts/compose.py` | Renders a JSON spec into store-sized PNGs (Pillow only) |

## Install

Clone into your skills folder, either for one project or for every project:

```bash
# this project only
git clone https://github.com/Barek-Technologies/appstore-screenshots .claude/skills/appstore-screenshots

# all projects
git clone https://github.com/Barek-Technologies/appstore-screenshots ~/.claude/skills/appstore-screenshots
```

Then ask Claude for "app store screenshots" or "Play Store listing images", or
run `/appstore-screenshots`.

Requirements: Python 3 with Pillow (`python3 -m pip install Pillow`). Capturing
needs Xcode (`xcrun simctl`) for iOS and `adb` for Android.

## Use the scripts directly

```bash
scripts/capture.sh ios out/raw/01-home.png
scripts/capture.sh android out/raw/01-home.png
```

```json
{
  "theme": {
    "background": ["#FAEFEF", "#E3C4C9"],
    "caption_color": "#400911",
    "subcaption_color": "#6B4D55",
    "frame": "iphone"
  },
  "panels": [
    {
      "screenshot": "out/raw/01-home.png",
      "caption": "Never blank on what to say",
      "subcaption": "A new question every morning"
    }
  ]
}
```

```bash
python3 scripts/compose.py spec.json --preset 6.9 --out out/final
```

Run `python3 scripts/compose.py --help` for the full spec schema.

### Size presets

| Preset | Pixels | Store slot |
| --- | --- | --- |
| `6.9` | 1320 × 2868 | iPhone 6.9" |
| `6.7` | 1290 × 2796 | iPhone 6.7" |
| `6.5` | 1284 × 2778 | iPhone 6.5" |
| `6.5alt` | 1242 × 2688 | iPhone 6.5" (older) |
| `ipad13` | 2064 × 2752 | iPad 13" |
| `play` | 1080 × 1920 | Google Play phone |

Always confirm the size against your own App Store Connect or Play Console upload
box. The composer refuses to write a panel at the wrong size.

### Fonts

Set `caption_font` and `subcaption_font` in the theme to `.ttf` paths, ideally
your app's own typeface. Without them the composer uses Inter if your project
has `@expo-google-fonts/inter` installed, otherwise Arial from macOS. On Linux
or Windows, set the font paths explicitly.

## Rules the skill enforces

- No invented ratings, reviews, download counts or press logos.
- No competitor trademarks or real people's likenesses.
- Only UI that exists in the build being submitted.
- Captions localized per storefront.

## License

MIT © 2026 Barek Technologies Limited. See [LICENSE](LICENSE).
