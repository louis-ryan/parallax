# Style — Inferno

The established look for the **Inferno** scenes specifically (this directory),
derived from `satan-bound/`. Match this for any new scene added under
`scenes/inferno/`. This guide is scoped to this project only — other project
directories (other visual worlds, e.g. `scenes/viking-invasion/`,
`scenes/infographic/`) have their own separate style guide; don't apply this
palette/aesthetic outside `inferno/`, and don't assume another project's style
guide applies here.

For universal, project-agnostic technical requirements and FCP/XML methodology that
apply regardless of visual style, see `../../context/requirements.md` and
`../../context/methodology.md`.

## Visual style: Bosch-inspired painterly cross-section

- **Painting, not game art.** Reference Hieronymus Bosch's hell scenes (the right
  panel of *The Garden of Earthly Delights*, *The Last Judgment*) — dense, painterly,
  surreal detail, hybrid human/animal/machine grotesques, muted earthy underpainting
  with hot glowing fire accents punched through dark values. No flat vector shapes,
  no pixel-art structure, no clean hard-edged silhouettes — this is the opposite
  aesthetic to `viking-invasion/`.
- **Densely detailed, not iconic/simplified.** Unlike the infographic project's bold
  simple silhouettes, this style wants cluttered, nightmarish detail rewarding close
  looking — small grotesque figures, tiny tortures and sub-scenes scattered through
  the frame, in the Bosch tradition. Still needs a clear primary focal point (Satan,
  bound, center) that reads instantly even with all the surrounding clutter.
- **Cross-section composition.** The frame is a vertical cutaway through the earth:
  a thin strip of sky and land at the very top, a visible ground-level boundary line,
  then a long descent through earth/rock strata, opening into a cavernous hell at the
  bottom third of the frame. Satan is bound (chained/roped) at the center of the hell
  cavern, surrounded by demons and fire.

## Color palette

- **Sky/land (top sliver)**: pale, washed-out daylight — a deliberate contrast to
  the hell below, so the transition into darkness reads as a real descent. Muted
  blue sky, dull green-brown land, nothing saturated or dramatic up here.
- **Earth strata (the descent)**: layered dark browns, ochres, and greys, each
  stratum a slightly different muddy tone, getting warmer and darker as it
  approaches hell — the palette itself should signal "getting hotter/closer to fire"
  well before the fire is visible.
- **Hell cavern**: dominant Bosch fire palette — deep black-browns and charcoal
  shadow, punched through with hot orange/red/yellow glowing fire, sickly sulfur
  yellow-green accents on smoke and demon flesh. Satan and the demons read as
  dark silhouetted/shadowed forms lit from below/behind by the fire glow, not
  flatly lit.

## Depth cueing

Depth is communicated by the strata themselves (each layer a different value/tone
as established above), not by blur — this is a mostly static painterly composite,
not a fast-parallax scene, so blur-based depth-of-field is used sparingly if at all
(a very slight softness on the topmost sky layer is enough).

## Motion language: painterly stillness, not game parallax

This project deliberately does **not** use viking-invasion's fast multi-layer
parallax + secondary rocking motion language — that reads as "game background," which
works against the painting reference. Instead:

- **The composite is mostly a static painted image.** No whole-scene camera rock,
  no fast panning layers.
- **Minimal, slow parallax only**: at most a very slow, subtle drift on the
  sky/cloud layer (barely perceptible) to avoid the frame feeling like a dead photo.
- **Fire flicker is the main motion carrier.** The fire/glow layer(s) in the hell
  cavern should flicker/animate (brightness and slight shape variation over time) —
  this is where the scene's "aliveness" comes from, not camera or layer movement.
- **Smoke drift.** Smoke rising from the hell cavern toward the strata above can
  drift slowly upward — a second, slower source of motion, blended with `add` or
  `screen` so it reads as translucent haze rather than an opaque object.
- Any subtle secondary motion on Satan/demons (e.g. a very slight breathing/writhing
  shift) should be minimal and slow — this is a bound, suffering tableau, not an
  action scene.

## Layer plan (adapting the standard checklist to this style)

1. **Background**: sky + land sliver + earth strata + hell cavern back wall, painted
   as one continuous graded cross-section image (this can be a single background
   layer rather than separate sky/midground/foreground, since the whole point is one
   continuous painterly descent, not a multi-plane game diorama).
2. **Fire/glow layer**: separate alpha layer for the flickering fire in the hell
   cavern, blended with `add` so it brightens the background rather than sitting as
   flat orange shapes on top of it.
3. **Smoke layer**: separate alpha layer, slow upward drift, `screen` or `add` blend,
   low opacity.
4. **Satan + demons**: painted into the background composite directly if static, OR
   as a separate alpha layer if any independent subtle motion is wanted on them.
5. **Universal paper-texture overlay**: per `../../context/requirements.md`, applied
   above the background, `multiply` blend — this still applies here despite the
   painterly style; it should read as canvas/paper grain over the whole painting,
   which actually reinforces the "this is a painting" read rather than working
   against it.

## Audio style

- **Ambience bed**: continuous deep earth rumble layered with a low fire-crackle
  texture, mixed low (roughly -12dB relative to other layers, matching
  viking-invasion's ambience convention) so it sits underneath rather than
  competing for attention.
- **Event layer**: distant tormented groans/moans and chain rattle, intermittent
  (not constantly looping), present enough in the mix to be felt — the visuals are
  already dramatic/dark, so per the universal requirement, don't default to a timid
  mix.
- Music is optional, scene-dependent, added by ear in the FCP UI — not a hard
  requirement.

## Reference implementation

`satan-bound/` is the first scene in this project and establishes the pattern above.
When starting a new inferno scene, reuse its overall structure (single painterly
background composite + fire/smoke alpha overlays + paper texture) rather than
importing viking-invasion's multi-plane parallax architecture.
