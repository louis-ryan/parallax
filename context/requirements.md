# Requirements — Parallax Scene Projects

This document captures what a "scene" in this project actually needs to satisfy,
derived from building the first scene (`scenes/viking-ocean/`). Use it as a checklist
when starting a new scene.

## What a scene is

A short (default: 20 second), looping-feel, layered parallax animation assembled as a
single `.fcpxml` file that opens directly in Final Cut Pro. Each scene lives in its own
directory under `scenes/<scene-name>/` and is self-contained: source images, encoded
video assets, audio, and the FCPXML all travel together.

## Baseline technical requirements

- **Frame size**: 1920x1080.
- **Frame rate**: 29.97fps (`FFVideoFormat1080p30`, `frameDuration="1001/30030s"`, or FCP's
  own `100/3000s` / `1001/30000s` variants — FCP will rewrite these on export, don't fight it).
- **Duration**: 20 seconds is the default scene length used so far. Keep all layers'
  `duration` values consistent with the sequence duration.
- **Every visual asset must be a video file (`.mov`), never a raw image.** FCP's importer
  on this machine cannot reliably load `asset-clip`s that reference still images — see
  `methodology.md` for why. PNGs are only ever source material; the last step for every
  visual layer is always "encode to ProRes .mov."
- **Alpha-channel layers** (anything meant to composite over other layers — foreground,
  midground, character/object sprites, overlays) must be encoded as **ProRes 4444**
  (`-profile:v 4444 -pix_fmt yuva444p10le`) to preserve transparency.
- **Opaque background layers** can use ProRes 422 HQ (`-profile:v 3 -pix_fmt yuv420p /
  yuv422p10le`) — smaller files, no alpha needed.

## What every scene needs (the layer checklist)

Based on the ocean scene, a typical layered parallax scene wants:

1. **A background layer** — sky/horizon/distant environment. Static or very slow pan.
   Fully opaque.
2. **One or more midground layers** — the main environmental texture (e.g. ocean
   surface). Usually tiled (see methodology) and panning at a moderate speed.
3. **A foreground layer** — closest-to-camera environmental texture (e.g. waves/spray).
   Pans fastest (parallax), usually also tiled, and is the layer most likely to want a
   blur applied (shallow depth-of-field, closest-to-camera = most out of focus).
4. **A subject/character asset** — the thing the scene is "about" (e.g. the Viking
   ship). Should stay in sharp focus if using depth-of-field blur. Moves with the
   midground it's sitting on (same pan direction/speed), plus its own secondary motion
   (e.g. rocking rotation).
5. **An atmospheric overlay** — something like lightning, rain, dust, embers. Usually
   wants a blend mode (`add` or `overlay`) rather than plain alpha compositing, so it
   reads as "light in front of the scene" rather than "an object in front of the scene."
6. **Whole-scene camera motion** — a gentle rock/sway/zoom applied to everything at
   once, simulating a handheld or physically-grounded camera (e.g. "camera on a raft").
   This must be built as a **compound clip wrapper**, not applied per-layer — see
   methodology for why.
7. **Audio** — at minimum an ambience bed (continuous environmental sound) and one
   "event" or texture layer (e.g. thunder, wind gusts). Mix so the ambience sits
   underneath (lower volume) and the event layer is present/felt, not distant/muted,
   if the visuals already convey drama (a storm-lit scene doesn't want timid thunder).

## Style requirement

Each project directory under `scenes/` (e.g. `scenes/viking-invasion/`) has its own
`style.md` scoped to that project's visual world — check for one there before
starting a new scene in an existing project directory, and create one for a brand
new project directory if the user is establishing a new visual style. Don't assume
one project's style guide (palette, aesthetic, motion language) applies to another.

## Universal overlay layer: paper texture

There is a shared, cross-project asset at `universal-assets/paper_background.mp4`
(1280x720 H.264, 60s, has an audio track that should be ignored/muted — only the
video is used). Unlike everything under `scenes/*/`, this is not scoped to one
project — it's meant to be applied to **every scene in every project**, regardless
of that project's own style guide.

**Compositing instruction**: this layer sits directly **above the background layer**
(i.e. the very next thing composited on top of sky/background, below every other
layer — mid-ground, subject, foreground, atmospheric overlays), using the
**multiply** blend mode. Multiply darkens/textures whatever is beneath it without
fully obscuring it, so it should read as a subtle paper/grain texture laid over the
sky rather than a distinct visual element of its own.

As of the viking-invasion scenes, this layer has only been added manually in the FCP
UI, not wired into any scene's FCPXML by hand — when building a **new** scene's
FCPXML from scratch (any project), add it explicitly: reference
`universal-assets/paper_background.mp4` as a new asset, place its `asset-clip`
immediately above the background layer in stacking order (next lane up), and set
`<adjust-blend mode="multiply">` (confirm the exact mode string FCP expects the same
way the `Gaussian` blur syntax was confirmed in `methodology.md` — export a quick
test clip with multiply applied in the FCP UI if the literal string isn't already
known to be `"multiply"` vs. e.g. `"6 (Multiply)"`, the way `adjust-blend mode`
values have shown up oddly formatted elsewhere in this project, e.g.
`"14 (Overlay)"`). Since the source video is 60s and scenes are 20s, trim/loop as
needed — an untrimmed reference will just play its first 20s, which is fine unless a
specific starting point in the texture is wanted.

## Licensing requirement

Every sourced asset (images, audio) must come from a free/open license
(CC0, CC-BY, OGA-BY) or the user's own uploads. **Track the license and attribution
requirement for every third-party asset** — see the Asset Sourcing Log pattern in
`methodology.md`. Don't source from itch.io or Pixabay directly (both block automated
fetching); OpenGameArt.org, SoundBible, and Pexels (for video) have worked reliably.

## Open questions to ask the user before building a new scene

These were implicit asks in the ocean scene that had to be inferred or clarified
mid-build. Ask them up front next time:

- What's the subject/focal object, and should it be in sharp focus (implies other
  layers get blurred)?
- Roughly how many parallax layers, and should any tile (pan indefinitely) vs. just
  pan-and-stop?
- Time of day / color mood (affects the background palette and grade)?
- Any specific atmospheric effects (weather, particles)?
- Audio: ambience only, or ambience + event layer + music?
- Scene duration, if not the 20s default.
