---
name: appstore-screenshots
description: Produce App Store and Play Store marketing screenshots — capture app screens from a simulator or emulator, then compose them into caption-led, conversion-optimized store images at exact required pixel sizes. Use when the user asks for app store screenshots, store listing images, ASO screenshots, TestFlight/Play Console assets, or wants to improve which screens their listing shows and in what order. Covers screen selection, caption copywriting, ordering psychology, and pixel-exact rendering.
---

# App Store Screenshots

Store screenshots are the highest-leverage conversion surface an app has. Most
users decide from the first two images in search results, at roughly thumbnail
size, before ever opening the listing page. Raw unannotated app screens waste
that surface.

This skill does two separable jobs. Do not collapse them.

1. **Decide** which screens go in which slots, and what caption sits on each.
2. **Render** those decisions at the exact pixel size the store demands.

The decision work is where the conversion lives. The rendering is mechanical.

## Workflow

### 1. Establish the target size first

Ask the user, or read it off their App Store Connect / Play Console upload box —
the page states the accepted sizes verbatim. Do not guess, and do not assume the
newest size: a listing created earlier may still be asking for an older slot.

| Preset | Pixels | Where it's used |
| --- | --- | --- |
| `6.9` | 1320 × 2868 | iPhone 6.9" — current canonical iPhone set |
| `6.7` | 1290 × 2796 | iPhone 6.7" — fallback when 6.9" is absent |
| `6.5` | 1284 × 2778 | iPhone 6.5" |
| `6.5alt` | 1242 × 2688 | iPhone 6.5", older variant |
| `ipad13` | 2064 × 2752 | iPad 13" |
| `play` | 1080 × 1920 | Google Play phone |

Apple takes 1–10 images per size and downscales the largest set to fill smaller
devices. Play takes up to 8. Supplying the largest required set is enough.

### 2. Choose the screens

Read the app before choosing. Find the actual screens — route files, navigation
config, tab layout — rather than assuming a generic structure.

Pick for **narrative**, not coverage. A store listing is not a feature tour; it
is an argument that unfolds in order. See `references/conversion-psychology.md`
for the slot-by-slot framework, which is the substance of this skill. Read it
before writing a single caption.

Hard constraint: one idea per screenshot. A screenshot that says two things says
neither at thumbnail size.

### 3. Write the captions

Captions carry the message; the screen underneath is evidence. Most users read
only the caption.

- 3–7 words. If it needs 8, the idea is not sharp yet.
- Benefit, not feature. "Never run out of things to say" beats "500+ prompts".
- Second person. The reader is the protagonist.
- No period at the end. It reads as a headline, not prose.
- Every caption must survive being shrunk to 30% and still be readable.

Draft captions, then show the user the full sequence as plain text **before**
rendering anything. Ordering and wording are cheap to change at that stage and
expensive afterward.

### 4. Capture the screens

`scripts/capture.sh` wraps simulator and emulator capture. Boot the device, get
the app to the screen you want, then capture. Source screenshots do not need to
match the output size — they are scaled into the device frame during
composition, so any modern device capture works.

```bash
scripts/capture.sh ios  out/raw/01-home.png     # booted iOS simulator
scripts/capture.sh android out/raw/01-home.png  # attached device or emulator
```

Populate the app with realistic content first. Empty states, `Lorem ipsum`, and
test accounts named "asdf" all read as unfinished and cost installs. Where the
app shows personal data, use plausible invented content — never a real person's.

### 5. Compose

Write a spec file, then render. Each panel names a captured screenshot and its
caption.

```json
{
  "theme": {
    "background": ["#FAEFEF", "#E3C4C9"],
    "caption_color": "#400911",
    "subcaption_color": "#6B4D55",
    "frame_color": "#2A1116"
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
scripts/compose.py spec.json --preset 6.5 --out out/final
```

Pillow is the only dependency. Output lands at exactly the preset's pixel size,
upload-ready with no resizing step, and the script fails loudly if a panel ever
renders at the wrong dimensions.

`background` is a `[top, bottom]` gradient pair or a single `"#RRGGBB"`. Fonts
default to the project's bundled Inter, then Arial; set `caption_font` /
`subcaption_font` to a `.ttf` path to override. Point them at the app's own
typeface when it has one — matching the in-app type makes the store page feel
continuous with the product. Run `scripts/compose.py --help` for the full schema.

### 6. Verify before handing over

Non-negotiable, because these are the failure modes that actually happen:

- Confirm output dimensions match the target exactly — `sips -g pixelWidth -g pixelHeight <file>`. A one-pixel mismatch is rejected at upload.
- View the set at 30% zoom. Anything unreadable there is unreadable in search.
- Check the first two panels stand alone. They are often all a user sees.
- Confirm no real personal data, no placeholder text, no debug UI, no wrong-brand copy leaked into a captured screen.

## Rules

- Never fabricate social proof. Ratings, review quotes, download counts, and
  press logos go in a screenshot **only** when the user supplies real ones.
  Inventing them is both a conversion lie and an App Review rejection.
- Never show a competitor's trademark or a real person's likeness.
- Do not show UI the build does not have. Screenshots must depict the version
  being submitted; Apple rejects listings whose images misrepresent the app.
- Localize captions per storefront when the app ships multiple languages. A
  translated caption over an English screenshot reads as broken.
