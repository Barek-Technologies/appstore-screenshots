# App Store Screenshots — an agent skill

A [Claude Code](https://claude.com/claude-code) skill that turns raw app screens
into caption-led, conversion-focused App Store and Google Play screenshots at the
exact pixel sizes the stores accept. It starts by studying what the top-ranking
apps in your category show, so the screens it picks are the ones that convert.

It does two separate jobs:

1. **Decide** which screens go in which slots, and what caption sits on each.
   This is where installs are won or lost. The agent downloads the screenshot
   sets of the top-ranking apps for your search terms and notes what they lead
   with, then ranks your own screens by conversion strength: the aha moment,
   the daily loop, the differentiator. You see the captions as plain text
   before anything is rendered. Once you're live, it sets up an A/B test of
   the first two panels.
2. **Render** those decisions into upload-ready PNGs: a gradient background,
   a headline caption and your screen inside a device frame.

## What's inside

| File | Purpose |
| --- | --- |
| `SKILL.md` | The workflow the agent follows: target size, screen choice, captions, capture, compose, verify |
| `references/conversion-psychology.md` | Slot-by-slot framework for ordering screenshots and writing captions |
| `scripts/appstore.mjs` | Searches the App Store and downloads top apps' screenshot sets for study (Node 18+) |
| `scripts/capture.sh` | Captures the booted iOS simulator or an attached Android device/emulator |
| `scripts/compose.py` | Renders a JSON spec into store-sized PNGs (Pillow only) |

## Install

With npm (Node 18+), from your project folder:

```bash
npx github:Barek-Technologies/appstore-screenshots                       # this project: ./.claude/skills/
npx github:Barek-Technologies/appstore-screenshots --global              # every project: ~/.claude/skills/
npx github:Barek-Technologies/appstore-screenshots --dir .agents/skills  # any other agent's skills folder
```

Run the same command again to update.

Or with the [skills CLI](https://www.npmjs.com/package/skills), or plain git:

```bash
npx skills add Barek-Technologies/appstore-screenshots
git clone https://github.com/Barek-Technologies/appstore-screenshots ~/.claude/skills/appstore-screenshots
```

Requirements: Python 3 with Pillow (`python3 -m pip install Pillow`) for
composing. Capturing needs Xcode (`xcrun simctl`) for iOS and `adb` for Android.

## Use the scripts directly

```bash
scripts/appstore.mjs search "habit tracker" --limit 5
scripts/appstore.mjs shots <app id> --dir research/shots/<name>
```

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

## More Barek skills

| Skill | What it does |
| --- | --- |
| [barek-competitor-watch](https://github.com/Barek-Technologies/barek-competitor-watch) | Competitor study and review mining → what to build next |
| [barek-aso](https://github.com/Barek-Technologies/barek-aso) | Store name, subtitle, keywords and descriptions, researched against what ranks |
| [appstore-screenshots](https://github.com/Barek-Technologies/appstore-screenshots) | Highest-converting screens, captioned and rendered at exact store sizes |
| [barek-landing](https://github.com/Barek-Technologies/barek-landing) | Calm app landing page: centred pill nav, gradient glow, one phone |

They share one research client (`scripts/appstore.mjs`) and hand off to each
other: the competitor study feeds the copy and the screenshot story.

## License

MIT © 2026 Barek Technologies Limited. See [LICENSE](LICENSE).
