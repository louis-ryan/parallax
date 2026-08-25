# Style — Infographic

The established look for the **Infographic** scenes specifically (this directory),
derived from `three-threats/`. Match this for any new scene added under
`scenes/infographic/`. This guide is scoped to this project only — other project
directories (other visual worlds, e.g. `scenes/viking-invasion/`) have their own
separate style guide; don't apply this aesthetic outside `infographic/`, and don't
assume another project's style guide applies here.

For universal, project-agnostic technical requirements and FCP/XML methodology that
apply regardless of visual style, see `../../context/requirements.md` and
`../../context/methodology.md` — including the universal paper-texture background
layer rule, which this project uses as its literal base layer (not just an overlay).

## Visual style: paper-cutout stop-motion

- **Hand-cut paper, not flat vector/UI icons.** Every element is a solid-color
  silhouette shape with a soft drop shadow (blurred, offset black shape behind the
  main fill) to read as a physical piece of paper sitting on the background, not a
  flat digital graphic. Built as: draw shape twice (once as a blurred black
  "shadow" pass, once as the real fill), composite shadow first, then fill on top.
- **Icons sit on their own paper card.** Each concept gets its own irregular,
  hand-torn/cut card shape (an off-white/cream polygon with jittered vertices, not a
  clean rectangle) behind the icon silhouette, so it reads as a separate cut piece
  placed on the paper background — not painted directly onto it.
- **Bold, simple, iconic silhouettes.** One clear read per icon (a mushroom cloud,
  a smoking factory, a robot head) — no fine detail, since paper-cutout shapes read
  as flat color blocks. Favor a few large blobby/geometric shapes over intricate
  linework.
- **Muted, distinct paper tones per icon**, not pure black — e.g. warm rust-brown
  for nuclear, olive-green for climate, cool slate for AI. Keeps a hand-colored-paper
  feel and gives each icon its own identity even before any explicit color coding is
  added.

## Background layering: Hessian base + multiply paper texture

Confirmed correct via the user's manual fix in FCP on `three-threats` and
`religious-hysteria` (both originally built without these three points, all three
were wrong until corrected by hand in FCP) — **apply all three from the start on
every future infographic scene**:

- **True base layer**: `scenes/infographic/assets/hessian.jpg`, a burlap/hessian
  weave texture, shared across every infographic scene (project-scoped, sits
  alongside each scene's own `assets/`, not under `universal-assets/` since it's
  specific to this project's look). Encode opaque (ProRes 422 HQ).
  - **Must be encoded/scaled large enough to fill the frame horizontally.** The
    source `hessian.jpg` is only 956x1000 (near-square, smaller than 1920x1080) —
    a naive `ffmpeg -vf scale=1920:1080` stretch was NOT sufficient in practice
    (the two existing scenes both shipped with the Hessian not filling the frame
    horizontally until manually fixed in FCP). Don't just force-stretch the small
    source to frame size; scale it up generously (e.g. render well above 1920px
    wide, or tile/repeat the weave texture) so it reads as a large sheet of
    material filling the shot, not a stretched small photo. If in doubt, err on
    the side of oversizing the encode and letting `adjust-transform scale` bring
    it down, rather than encoding at exactly 1920x1080.
  - **Set to 70% opacity**, via `<adjust-blend amount="0.7"/>` on the Hessian's own
    `asset-clip` (no `mode` needed — normal blend, just at reduced opacity). This
    `amount` attribute is confirmed-working FCPXML syntax, already verified via
    real FCP export elsewhere in this project (see
    `../viking-invasion/church-on-the-hill/church_on_the_hill.fcpxml`'s
    `<adjust-blend amount="0.5" mode="add"/>` on its lightning layer — same
    attribute, different mode). Remember DTD ordering: `adjust-transform` must
    come before `adjust-blend` inside the `asset-clip` (methodology.md bug #6c).
- **Paper texture layer**: the universal `paper_background.mp4` texture (crumpled
  cream/off-white paper, subtle moving light — see requirements.md) sits directly
  above the Hessian layer, composited with `mode="multiply"`.
  - **This must actually be `mode="multiply"` on `adjust-blend`, not left at
    normal/default blend** — both existing scenes shipped with the paper texture
    sitting over the Hessian at normal blend (fully obscuring it, "just sits over
    the top") until the user fixed it manually. Double check the `<adjust-blend
    mode="multiply">` element is actually present on the paper-texture clip, not
    just intended in a comment.
  - The exact `mode="multiply"` string is still technically unverified via a
    controlled manual-export test (unlike `amount`, above) — it's now confirmed to
    at least be accepted and do something correct-looking per the user's live fix,
    but if a future scene's multiply doesn't look right, re-derive the exact
    string via manual FCP export per methodology.md's guidance rather than
    assuming this project's prior usage was pixel-perfect.
- Everything else (cards, icons, cross marks, collage pieces) sits above both of
  these.

## Color palette pattern: warm cream paper + muted icon tones

- **Background**: Hessian weave (base) + `paper_background.mp4` (multiply layer
  above it) — see "Background layering" above.
- **Cards**: off-white/cream (`~rgb(250,246,235)`), matching the background's paper
  tone family so cards read as "more of the same paper," not a jarring different
  material.
- **Icon fills**: muted, darker, desaturated tones distinct per icon — avoid bright
  saturated colors; this is a paper/ink aesthetic, not a flat-design app icon set.
- **Elimination mark**: a hand-drawn-looking thick red-brown stroke (grease-pencil
  crossing-out feel) — built as a wobbly multi-segment line (random per-point jitter
  along the stroke path) rather than a perfectly straight geometric line, to match
  the hand-made feel.

## The "eliminated" state: hard cut to black-and-white, not a filter animation

When a concept is "crossed off," don't animate a saturation/color filter on the
clip — **pre-render two static versions of every card** (full color, and a
grayscale desaturation of the exact same art) as separate video assets, then hard-
swap between them at the moment of elimination (color card's scale keyframes go to
0 at that timestamp, B&W card's scale keyframes jump from 0 to full at the same
timestamp). This was a deliberate choice to avoid needing to discover/verify a new
FCP color/saturation filter's exact XML syntax the way Gaussian blur and Color
Adjustments were confirmed via manual FCP export in the viking-invasion project —
a pre-rendered swap is simpler and has no filter-syntax risk. If a smoother
color-to-B&W transition is wanted later, confirm a desaturation filter's exact
syntax via a manual FCP export first (see methodology.md's guidance on this), don't
guess it.

## Motion language: stop-motion, not smooth easing

This is the one significant departure from the viking-invasion project's motion
language (which uses smooth eased curves throughout) — infographic scenes should
read as **hand-animated stop-motion**, not fluid digital animation:

- **Snap, don't ease.** Build motion as `curve="linear"` keyframes packed close
  together in time (e.g. a value held flat for a while, then two keyframes ~0.02s
  apart jumping straight to a new value) rather than spread-out eased curves. FCP
  interpolates linearly between any two keyframes regardless of spacing, so keeping
  the "from" and "to" keyframes very close in time is what produces a snap/jump-cut
  rather than a visible tween.
- **Overshoot-bounce on entrances.** An element popping into frame should briefly
  scale slightly past its resting size (e.g. rest 0.85 → overshoot ~0.90 → settle
  back to 0.85) rather than arrive at exactly its final size — this single-bounce
  read as physical/tactile "stop motion puppet" motion, not a digital scale-up.
- **Idle jitter.** Even while "at rest," elements should get small stepped position/
  scale nudges every second or so (not continuous smooth motion) — mimics the
  natural micro-inconsistency of physical stop-motion (a puppet/cutout never sits
  perfectly still between frames, even when "not moving").
- **Stagger entrances.** Multiple elements shouldn't enter simultaneously — offset
  each by a beat (e.g. ~1s apart) so the eye can track each arrival distinctly,
  reinforcing the frame-by-frame handmade feel.

## Layout: side-by-side comparison cards

For a "present N options, then eliminate them" structure (as in `three-threats/`),
lay the cards out side-by-side at equal spacing (not stacked/overlapping) so all
items stay simultaneously visible and comparable throughout — the elimination
sequence then happens as a left-to-right (or otherwise ordered) beat across the
already-visible set, not one item at a time hiding the others.

## Layout: collage cluster

For an atmospheric/mood scene with no compare-and-eliminate structure (as in
`religious-hysteria/`), scatter pieces across the frame at varied positions,
scales, and slight rotations (a few degrees, not dramatic tilts) like a scrapbook
page, rather than a fixed grid — pieces can overlap slightly. Stagger entrances
(~0.8s apart) same as the card layout, but there's no need for a hard second
"event" beat (no crossing-off/B&W swap) — just entrance, idle jitter, and a long
atmospheric hold to the end of the clip. This layout also introduces rotation
jitter (small keyframed wobble, ±2-6°) alongside position/scale jitter, which
`three-threats` didn't use — same `curve="linear"` snap technique applies to
rotation keyframes as to scale/position (methodology.md bug #3).

For collage pieces sourced from photographic/painted source art (not flat
silhouette icons), build each piece as: crop the source image to the desired
aspect ratio, generate an irregular torn-paper mask (jittered polygon), composite
the cropped photo through that mask, blend a soft cream edge in near the tear line
(so the torn edge reads as paper, not a hard photo crop), then add the same
blurred-offset drop shadow as the flat-icon technique. This keeps photographic
material consistent with the paper-cutout aesthetic instead of looking like a
pasted screenshot.

## Reference implementations

`three-threats/three_threats.fcpxml` — the canonical side-by-side card layout:
paper background base layer, three side-by-side cutout cards with stop-motion
entrances, staggered cross-off/B&W-swap sequence.

`religious-hysteria/religious_hysteria.fcpxml` — the canonical collage-cluster
layout: four torn-paper photographic cutouts (public-domain paintings; see the
file's own header comment for attribution) scattered across the frame with
staggered stop-motion entrances, position/scale/rotation idle jitter, and a long
atmospheric hold — no elimination beat. Also demonstrates reusing the shared
Hessian + paper-texture background assets **across scenes** (not just within one
scene) — see its note on matching `uid` strings below.

`romantic-dream/romantic_dream.fcpxml` — a "hero subject + thought-bubble chain"
layout: one larger torn-paper hero figure (Carl Spitzweg's "Der Zeitungsleser," a
man standing in his garden) plus a rising diagonal chain of four smaller collage
pieces, each set inside a scalloped cream paper-cutout "cloud" shape (built the
same way as the torn-photo pieces: jittered polygon mask, cream edge blend,
drop shadow — see `source_images/build_bubble.py` in that scene folder for the
cloud-shape generator), with small trailing connector circles between the
figure's head and the nearest bubble. Same staggered stop-motion entrance /
idle-jitter / hold pattern as the other two scenes. This is also the first
infographic scene built with the corrected Hessian sizing (oversized + cropped,
not naively stretched) and the `<adjust-blend amount="0.7"/>` 70%-opacity fix
applied from the start, per the "Background layering" section above.

**Superseded scene, moved out of this project**: an earlier draft of a "candlelit
Bible + emerging equations" scene was built here as `1844-prophecy/`, but the user
asked for it to become its own top-level project with a different visual language
(geometric/illuminated realism, real camera pan, no paper-cutout framing) —
it now lives at `../1844-prophecy/` (top-level, sibling to this `infographic/`
directory) with its own `style.md`. The stop-motion-flicker and `add`-blend-glow
techniques explored in the abandoned draft are documented in that project's
`style.md` instead (the final scene actually uses real flickering candle footage
rather than the stepped-variant-swap fake flicker, but the fake-flicker technique
remains documented there as a fallback approach for future scenes that don't have
suitable footage available).

**Note on the cross-off mark asset**: the same `cross_mark.mov` file is used for all
three eliminations, but each card gets its OWN `<asset>` resource entry pointing at
that file (three separate `id`s, same underlying video) rather than all three
sibling clips sharing one `ref` — this avoids methodology.md bug #6 (duplicate `ref`
across sibling connected clips corrupts position values on the second/later
instances). **Critically, all three `<asset>` entries share the exact same `uid`**
(only `id` differs) — giving them distinct invented `uid` strings caused an outright
import rejection ("media already exists in the library with a different unique
identifier"), since FCP tracks media identity by content/uid across the whole
import, not scoped per-`<asset>` entry. See methodology.md bug #6b. If a future scene
reuses one video asset across multiple sibling positions, follow this same pattern:
one `<asset>` entry per usage (distinct `id`), but copy the identical `uid` on every
one of them.

**Note on reusing the Hessian/paper-texture background across scenes**:
`religious-hysteria/religious_hysteria.fcpxml` re-encodes its own copies of
`hessian_background.mov` and `paper_background.mov` (separate files on disk from
`three-threats`' copies, since each scene keeps its own `video/` folder), but its
`<asset>` entries for them use the exact same `uid` strings as `three-threats`'
entries (`three_threats_hessian_bg_mov_uid` / `three_threats_paper_bg_mov_uid`) —
required because `three-threats` had already been imported into the FCP library,
so a mismatched uid on the same underlying source content would be rejected at
import (methodology.md bug #6b). If `three-threats` had NOT yet been imported when
`religious-hysteria` was built, fresh uids would have been safe instead — check
import status before assuming either way.

**Neither scene has yet been fully tested in FCP** — treat the specific keyframe
timings and stop-motion "snap" values in both reference files as a first draft;
expect the usual iteration (see methodology.md for the general debugging approach:
build isolated test files, verify exact values via Inspector, don't guess-and-check
inside the full scene).
