# Style — Puritans

The established look for the **Puritans** scenes specifically (this directory),
derived from `arrival/`. Match this for any new scene added under
`scenes/puritans/`. This guide is scoped to this project only — other project
directories (other visual worlds, e.g. `scenes/viking-invasion/`, `scenes/inferno/`,
`scenes/infographic/`) have their own separate style guide; don't apply this
palette/aesthetic outside `puritans/`, and don't assume another project's style
guide applies here.

For universal, project-agnostic technical requirements and FCP/XML methodology that
apply regardless of visual style, see `../../context/requirements.md` and
`../../context/methodology.md`.

## Visual style: Hudson River School wilderness + comical caricature figures

Two deliberately contrasting registers in one frame:

- **Background (the "American wilderness"): Hudson River School painting.**
  Reference Thomas Cole / Frederic Church — dramatic golden/atmospheric light,
  sweeping romanticized vista (forest, coastline, cliffs, big sky), rich painterly
  detail, a sense of vast untouched nature. Played straight, not comically — the
  humor in this scene comes entirely from the human figures, not the landscape.
- **Figures (the Puritans): exaggerated caricature.** Tall black hats with big
  buckles, stiff rigid stick-straight posture, oversized white collars, stern/dour
  expressions, muted black-grey-white palette that visually clashes against the
  colorful, warm wilderness — the joke is these severe, rigid little figures
  awkwardly arriving into a vast, wild, indifferent landscape. Comedy is in
  silhouette and posture (small, stiff, comically uniform), not in the wilderness
  painting itself.
- **The ship**: wooden sailing vessel (period-appropriate, e.g. Mayflower-like),
  painted with more texture/detail than the flat-caricature figures — it should
  read as "a real wooden ship the comical little Puritans are riding in," not
  itself a joke object.

## Color palette

- **Wilderness background**: warm golden-hour Hudson River School palette —
  deep greens and blue-greens for forest, warm ochre/gold for atmospheric light
  (especially near a horizon or break in cloud), soft blue-grey distant hills,
  dramatic sky (soft clouds catching warm light, cooler blue above). Rich and
  inviting — this is the landscape as beautiful and vast, not foreboding.
- **Ship**: warm aged wood browns, weathered grey-brown sails, small warm
  highlights (lanterns, brass fittings) for a lived-in, crafted feel.
  Sits at a natural mid-value against the background — not overly dark contrast.
- **Puritans**: strict black/charcoal coats and hats, stark white collars/cuffs,
  pale skin tones, occasional single muted accent (dull brass buckle, dull red-brown
  sash) — kept flat and graphic, deliberately less painterly than the background so
  they read as the comic foreground element.

## Depth cueing

- **Background**: soft atmospheric perspective — distant elements (far hills, sky)
  hazier/cooler/lower-contrast, nearer elements (foreground shoreline, rocks, trees)
  more saturated and detailed. This is what sells the painting depth, not blur.
- **Ship + figures**: sharp, in focus — the clear subject and focal point of the
  scene, should never be the blurriest thing on screen.
- A light, subtle blur is acceptable on the very immediate foreground (e.g. shore
  rocks/grass closest to camera, if used) but keep it minimal — this scene favors a
  painterly-sharp read over the Viking scene's shallow-depth-of-field look.

## Motion language

- **Wilderness background**: mostly static, or an extremely slow/subtle pan —
  it's a painting being "looked at," not a fast-parallax game backdrop.
- **Ship arrival**: the ship sails in from one side of frame toward the shore,
  moderate/slow speed (this is a sailing ship, not a speedboat — motion should
  read as stately, heavy, deliberate), settling into a resting position near shore
  rather than exiting frame.
- **Puritan figures**: minimal independent motion — a very slight sway/bob in
  time with the ship's motion is enough; avoid busy individual animation, since
  the comedy is in their rigid stillness, not activity. If any are disembarking,
  keep that motion stiff and deliberate, not naturalistic.
- **Water**: gentle wave motion under/around the ship, consistent with a calm
  coastal arrival, not a storm (unlike viking-invasion's dramatic dusk/storm
  default — this scene wants a calmer, warmer mood).
- **Atmospheric touch**: optional very slow drifting cloud or mist in the
  background for subtle life, matching the "painting slowly breathing" feel used
  in `inferno/` rather than viking-invasion's fast camera-rock language.

## Layer plan

1. **Background**: wilderness landscape painting (sky, distant hills, forest,
   coastline) as one continuous painterly composite — opaque.
2. **Water/shore midground**: coastal water surface with the shoreline the ship is
   arriving at; gentle wave motion.
3. **Ship + Puritans**: painted/composited together as the subject layer (alpha),
   sailing in from frame edge to a resting position near shore. Puritans can be
   part of this same layer unless independent subtle motion is wanted, in which
   case break them out as their own alpha layer riding with the ship.
4. **Foreground** (optional): nearest shoreline detail (rocks, grass, reeds) for
   a touch of depth framing — keep restrained per the depth cueing note above.
5. **Universal paper-texture overlay**: per `../../context/requirements.md`, above
   the background, `multiply` blend — reinforces the "this is a painting" read.

## Audio style

- **Ambience bed**: coastal wind + gentle waves, continuous, mixed low
  (~-12dB relative to other layers, matching the established convention).
- **Event layer**: creaking wooden ship timbers, seagull calls, intermittent —
  present enough to feel tactile without competing with the visual comedy.
- Music optional, added by ear in FCP UI, not a hard requirement.

## Reference implementation

`arrival/` is the first scene in this project and establishes the pattern above.
When starting a new puritans scene, reuse its overall structure (painterly
wilderness background + water midground + ship/figures subject layer + paper
overlay) rather than importing another project's architecture (avoid
viking-invasion's fast multi-tile parallax or inferno's fire/smoke-driven motion
language — this project's "aliveness" comes from the ship's slow arrival motion,
not atmospheric overlays).
