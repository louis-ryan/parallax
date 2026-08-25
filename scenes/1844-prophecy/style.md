# Style — 1844 Prophecy

The established look for the **1844 Prophecy** scenes specifically (this
directory), derived from `awakening-reading/`. Match this for any new scene added
under `scenes/1844-prophecy/`. This guide is scoped to this project only — other
project directories (other visual worlds, e.g. `scenes/great-awakening/`,
`scenes/puritans/`, `scenes/inferno/`, `scenes/viking-invasion/`,
`scenes/infographic/`) have their own separate style guide; don't apply this
palette/aesthetic outside `1844-prophecy/`, and don't assume another project's
style guide applies here.

**Note**: this project started life as a scene inside `scenes/infographic/` (the
paper-cutout/stop-motion project) but was deliberately pulled out into its own
top-level project — the user wanted a different visual language (geometric/
illuminated rather than paper-cutout collage) and a real camera move, which don't
fit `infographic/`'s established conventions. Don't apply `infographic/style.md`'s
paper-cutout techniques here (torn-paper card shapes, stop-motion snap-to-rest
entrances, B&W hard-cut eliminations) — this project uses smoother, more
continuous motion and no card/collage framing device at all.

For universal, project-agnostic technical requirements and FCP/XML methodology that
apply regardless of visual style, see `../../context/requirements.md` and
`../../context/methodology.md`.

## Visual style: sacred geometry + candlelit realism

The concept: a 19th-century believer's candlelit reading of the Bible, with the
mathematical/numerological logic of a prophetic calculation (the real 1844
Millerite date-setting, from Daniel 8:14 and 9:24) visibly emerging from the text
as if the reader is having a moment of terrible clarity.

- **Hero object: a real painting, not a paper cutout.** The Bible-and-candle still
  life (Van Gogh's "Still Life with Bible") is presented as a clean, softly
  feathered photographic vignette — no torn-paper edge, no card backing (unlike
  every `infographic/` scene). It should read as "a lit fragment of a real object
  glowing out of the dark," not "a scrapbook piece."
- **Backdrop: abstract sacred geometry, not environment art.** Radiating lines
  (like a halo/sunburst), concentric rings, and scattered thin-outlined triangles,
  all low-opacity warm gold on a near-black background — evokes
  numerology/mysticism/divine light without depicting anything literal (no
  clouds, no angels, no literal cathedral). Built procedurally (see
  `source_images/build_geometry.py`), not sourced imagery.
- **Text: plain glowing script, not cards.** The equation/scripture fragments
  (the real Millerite chronology — Daniel 8:14's 2300 days, the 457 BC Ezra 7
  decree, Daniel 9:24's 490 years) are rendered as warm gold hand-jittered
  lettering with a soft glow, no card or background shape behind them — they
  should look like they're materializing in light, not written on paper. See
  `source_images/build_text.py`.
- **Candle: real footage, not a painted or procedural flame.** Use actual
  flickering-candle video footage (sourced from Pexels, public/free license — see
  the scene's own header comment for the exact source), cropped tightly to just
  the flame (not the visible wax body, which would visually conflict with the
  candle already painted in the hero image), composited with `adjust-blend
  mode="add"` so the near-black footage background contributes nothing and only
  the warm flame glows onto the painting. This gives genuine organic flicker for
  free, rather than needing a stepped-variant-swap fake flicker (the technique
  used in the earlier infographic-project draft of this scene, before it was
  pulled out into its own project) — prefer real footage over a procedural
  flicker approximation whenever suitable footage exists.

## Color palette

- **Background**: near-black warm brown/charcoal (`~rgb(18,14,10)`), so the
  geometry and candlelight read as the only light sources.
- **Geometry**: warm gold (`~rgb(200-235, 150-210, 80-130)`), low alpha (40-90 out
  of 255) so it reads as a subtle halo/atmosphere, not a bold graphic overlay.
- **Text glow**: warm parchment-gold (`~rgb(250,225,170)`), matching the
  candlelight's own color temperature so the emerging text reads as "lit by the
  same candle," not an unrelated UI color.
- **Flame**: real footage's natural warm orange-yellow, used via `add` blend so it
  naturally lightens/warms whatever true-color painting is beneath it.

## Motion language: slow and continuous, not stop-motion

This is the second significant departure from `infographic/`'s established motion
language (stop-motion snap-and-hold) — 1844-prophecy scenes should read as
**smooth, continuous, reverent movement**, matching a candlelit vigil mood rather
than a hand-animated collage:

- **Camera**: a slow upward pan/drift over the full clip duration, built as a
  small transform (a few percent scale/position drift) on the outer `ref-clip`
  compound wrapper — per methodology.md bug #5, this only works for SMALL moves,
  which a slow reverent drift is well within.
- **Text**: equation fragments drift/float slowly outward and upward from the
  book over the clip's duration (`curve="smooth"` eased motion, not
  `curve="linear"` snaps) — they should look like they're rising off the page,
  not popping into a fixed collage position and holding still.
- **Flame flicker**: comes for free from the real footage (see above) — no
  keyframed flicker animation needed on the flame layer itself, only position.
- **Geometry**: can have a very slow rotation or pulse (barely perceptible) but
  doesn't need to move at all — its job is atmosphere, not a focal animation.

## Layer plan

1. **Geometry backdrop**: radiating lines + concentric rings + triangle field +
   soft central glow, all near-static, lowest layer above pure background color.
2. **Hero still life**: the Bible/candle painting, feathered vignette, roughly
   centered, largest element.
3. **Candle flame**: real footage, `add` blend, positioned to track the hero's
   own transform so it stays glued to the painted candle's wick.
4. **Equation text (x4)**: plain glowing lettering, slow continuous outward/
   upward drift from the book, staggered start times.
5. **Camera**: slow upward pan on the outer compound `ref-clip`, small amplitude.
6. **Universal paper-texture overlay**: per `../../context/requirements.md`,
   included for consistency with every other scene in the library — the user
   confirmed they want it kept even here, where the geometric backdrop already
   carries most of the "texture" role. Keep it at reduced opacity (via
   `adjust-blend amount`, same pattern as the Hessian layer in `infographic/`)
   so the paper grain doesn't compete with or muddy the candlelight glow — this
   is the one place this project borrows an `infographic/`-style opacity
   reduction, purely for practical blending reasons, not a style-language
   choice.

## Reference implementation

`awakening-reading/1844_prophecy.fcpxml` is the first and canonical scene in this
project (superseding an earlier draft built inside `scenes/infographic/`, before
the user asked for it to become its own project with a different visual
language). When starting a new 1844-prophecy scene, reuse its structure
(geometric backdrop + photoreal hero + real-footage glow element + drifting glow
text + slow camera pan) rather than importing `infographic/`'s paper-cutout/
stop-motion architecture.

**This scene has not yet been tested in FCP** — treat the specific keyframe
timings, camera pan amplitude, and text drift paths as a first draft; expect the
usual iteration (see methodology.md for the general debugging approach).
