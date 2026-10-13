---
name: appstore-screenshots
description: Produce App Store and Play Store marketing screenshots — capture app screens from a simulator or emulator, pick the highest-converting screens by studying what the top-ranking apps in the category show, then compose them into caption-led, conversion-optimized store images at exact required pixel sizes. Use when the user asks for app store screenshots, store listing images, ASO screenshots, TestFlight/Play Console assets, or wants to improve which screens their listing shows and in what order. Covers screen selection, caption copywriting, ordering psychology, and pixel-exact rendering.
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

### 2. Study what the top apps in the category show

Before choosing your own screens, look at what already converts in your
category. The apps ranking at the top of the searches you want to win have
usually tested their screenshot sets; their choices are evidence.

```bash
scripts/appstore.mjs search "<your main search term>" --limit 10
scripts/appstore.mjs top --genre <category> --limit 25
scripts/appstore.mjs shots <id> --dir research/shots/<short-name>   # store order
```

Download the sets for the top 3–5 apps and look at them in order. For each,
note: what slot 1 promises, which screen is in slot 2, caption length and
tone, whether people/faces appear, background style, how many panels, and
whether they lead with the product or with an outcome. Write a short table.
What all of them do is the category's baseline, so do it too. What none of
them do is your chance to stand out in the search grid. Never copy their
captions or art; study the pattern only.

If a competitor study exists (`docs/COMPETITORS.md` from
`barek-competitor-watch`), read its "edge" section. Screens that answer the
category's top complaints ("free means usable", "no ads") make strong slot 2–3
panels.

### 3. Choose the highest-converting screens

Read the app before choosing. Find the actual screens — route files, navigation
config, tab layout — rather than assuming a generic structure.

Rank every candidate screen by how strongly it shows the reason people
install. Signals, strongest first:

1. **The aha moment.** The screen where a new user first gets the value. That's usually slot 1 or 2.
2. **The daily loop.** What retained users open the app for. If the app has analytics, the most-visited screen by week-2 users is the answer.
3. **The differentiator.** The one thing the top apps don't show (from step 2).
4. **Content-rich over empty.** A full, plausible screen beats a sparse one, every time.

Drop settings, sign-up, paywalls, onboarding and anything that reads as a form.

Pick for **narrative**, not coverage. A store listing is not a feature tour; it
is an argument that unfolds in order. See `references/conversion-psychology.md`
for the slot-by-slot framework, which is the substance of this skill. Read it
before writing a single caption.

Hard constraint: one idea per screenshot. A screenshot that says two things says
neither at thumbnail size.

### 4. Write the captions

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

### 5. Capture the screens

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

### 6. Compose

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

### 7. Verify before handing over

Non-negotiable, because these are the failure modes that actually happen:

- Confirm output dimensions match the target exactly — `sips -g pixelWidth -g pixelHeight <file>`. A one-pixel mismatch is rejected at upload.
- View the set at 30% zoom. Anything unreadable there is unreadable in search.
- Check the first two panels stand alone. They are often all a user sees.
- Confirm no real personal data, no placeholder text, no debug UI, no wrong-brand copy leaked into a captured screen.

### 8. Test, then keep the winner

Your best guess is still a guess. Once the listing is live, A/B test the
first two panels: Apple's **Product Page Optimization** (App Store Connect →
your app → Product Page Optimization, up to 3 variants) and Google Play's
**Store listing experiments** (Play Console → Grow → Store presence). Change
one thing per test, usually slot 1. Run it until the console reports
significance, then make the winner the default.

## Rules

- Never fabricate social proof. Ratings, review quotes, download counts, and
  press logos go in a screenshot **only** when the user supplies real ones.
  Inventing them is both a conversion lie and an App Review rejection.
- Never show a competitor's trademark or a real person's likeness.
- Do not show UI the build does not have. Screenshots must depict the version
  being submitted; Apple rejects listings whose images misrepresent the app.
- Localize captions per storefront when the app ships multiple languages. A
  translated caption over an English screenshot reads as broken.
