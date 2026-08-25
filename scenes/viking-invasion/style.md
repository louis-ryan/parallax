# Style — Viking Invasion

The established look for the **Viking Invasion** scenes specifically (this
directory), derived from `viking-ocean/`. Match this for any new scene added under
`scenes/viking-invasion/`. This guide is scoped to this project only — other scene
directories (other projects/worlds) have their own separate style guide living in
their own directory; don't apply this palette/aesthetic outside viking-invasion, and
don't assume another project's style guide applies here.

For universal, project-agnostic technical requirements and FCP/XML methodology that
apply regardless of visual style, see `../../context/requirements.md` and
`../../context/methodology.md`.

## Visual style: dramatic pixel art

- **Pixel art, not photorealism.** Sourced/generated art should have visible pixel
  structure — flat color regions, hard-edged shading bands, no photographic texture
  or smooth gradients within individual elements (gradients across a whole
  background/sky are fine and encouraged — see palette below).
- **Video-game adjacent, not cutesy.** Think side-scrolling game background art
  (parallax backgrounds from platformers/adventure games), not flat vector
  illustration and not chibi/kawaii pixel art. Detailed silhouettes (e.g. the Viking
  longship's dragon-head prow, shield row, rigging) read as "crafted game asset,"
  not "simple icon."
- **High drama, not neutral daylight.** The reference scene uses a dusk/storm
  palette specifically because it reads as more cinematic and tense than a plain
  blue-sky ocean. Default toward moody lighting (dusk, storm, night, dawn) over
  flat midday lighting for new scenes unless the brief calls for something calmer.
- **Readable at small scale.** Because these compose into a small final frame with
  many overlapping layers, silhouettes need to stay legible — avoid fine detail that
  will disappear under scaling, blur, or overlapping layers.

## Color palette pattern: dusk/storm gradient

The confirmed working formula for a dramatic sky background:

- **Top of frame**: deep purple-navy (`~rgb(35,25,65)`)
- **Upper-mid**: transitioning into dramatic pink/magenta (`~rgb(180,70,90)`)
- **Near horizon**: fiery warm orange (`~rgb(255,140,70)`)
- **Below horizon / water**: cools back down (`~rgb(60,50,80)`) — don't let the warm
  horizon color bleed all the way down into the water, it should feel like the water
  is reflecting/absorbing rather than glowing.

Applied as a vertical gradient blended with the original image's luminance (so cloud
/ terrain detail stays visible through the grade, not flattened by it) — roughly
80% gradient color, 20% original color, plus a slight saturation and contrast boost
(`ImageEnhance.Color` ~1.25x, `ImageEnhance.Contrast` ~1.08x) for punch.

For a different mood (e.g. a daytime scene, a colder/icier scene), keep the same
*structure* (a vertical 3-4 stop gradient, blended with original luminance rather
than flatly replacing it, plus a small saturation/contrast bump) but swap the actual
colors to match the new brief.

## Depth cueing: color + blur together

Depth in the scene is communicated two ways simultaneously, and both should point
the same direction:

1. **Blur** — sharpest at the focal subject (the ship), progressively blurrier
   toward both the foreground (closest, most out of focus — mimics shallow depth of
   field) and, to a lesser extent, the background.
2. **Desaturation/cooling with distance** — the background sky is the most
   stylized/graded layer; midground water is fairly saturated; foreground/subject
   should read as the "clearest" color.

Don't blur the subject or key atmospheric elements (lightning) — they're the
thing the eye should land on and stay sharp.

## Motion language

- **Parallax speed = depth.** Layers closer to camera (foreground) pan faster than
  layers further away (background). The reference scene's approximate ratios:
  background pan is slowest and smallest amplitude, midground moderate, foreground
  fastest/largest amplitude.
- **Secondary motion on subjects.** The ship doesn't just translate with the parallax
  pan — it also has an independent gentle rocking rotation (small amplitude, ~±9°,
  irregular/non-metronomic timing) layered on top, since a rigid object moving in
  pure lockstep with the background reads as "pasted on" rather than physically
  present in the scene.
- **Whole-scene camera motion.** A very gentle, slow, irregular rock/sway (~±1.5°,
  over the full clip duration, non-repeating timing) applied to the entire composed
  scene as one rigid unit — see ../../context/methodology.md #5 for the technical approach. This
  is what sells "camera physically present in the environment" (e.g. on a raft)
  rather than "flat layered animation." Keep the amplitude small — this is a subtle
  atmospheric touch, not a shake effect.
- **Atmospheric overlays use blend modes, not plain alpha.** Lightning/light effects
  should use `add` or `overlay` blend mode so black/dark areas of the overlay source
  disappear and only the bright parts contribute — this reads as "light in the air"
  rather than "a video pasted on top."

## Audio style

- **Ambience bed + event layer**, minimum. A continuous environmental sound (ocean
  waves, wind, rain) sits under everything; a more textured "moment" sound (thunder,
  a creak, a gust) sits on top, not necessarily looped, present throughout or
  triggered at intervals.
- **Match audio presence to visual drama.** If the visuals already commit to a
  dramatic mood (storm lighting, dark palette), the audio should match that energy —
  don't default to "distant/subtle" for a scene whose visuals are already loud. Ask
  what mood the visuals are going for before defaulting to a timid/ambient mix.
- **Ambience typically sits lower in the mix than event sounds** — the reference
  scene uses roughly -12dB on the continuous wave ambience relative to the other
  layers, so it reads as a bed rather than competing for attention.
- Music is optional and scene-dependent — added by ear/preference in the FCP UI in
  the reference project, not a hard requirement for every scene.

## Reference implementation

`viking-ocean/viking_ocean.fcpxml` is the canonical example of all of the
above applied together. When starting a new scene, it's reasonable to copy its
overall *structure* (compound-clip camera rig, layer ordering, blend modes) and
substitute new art/audio/color choices rather than designing the animation
architecture from scratch each time.
