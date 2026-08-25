# Style — Great Awakening

The established look for the **Great Awakening** scenes specifically (this
directory), derived from `fire-and-brimstone/`. Match this for any new scene added
under `scenes/great-awakening/`. This guide is scoped to this project only — other
project directories (other visual worlds, e.g. `scenes/puritans/`, `scenes/inferno/`,
`scenes/viking-invasion/`, `scenes/infographic/`) have their own separate style
guide; don't apply this palette/aesthetic outside `great-awakening/`, and don't
assume another project's style guide applies here.

For universal, project-agnostic technical requirements and FCP/XML methodology that
apply regardless of visual style, see `../../context/requirements.md` and
`../../context/methodology.md`.

## Visual style: dramatic/ominous 19th-century tent revival

Unlike `puritans/` (comical caricature) this project plays it straight — the goal is
an intense, slightly unsettling "heyday of American Protestantism" mood, not comedy.
The cult-like read comes from **uniformity and fervor**, not exaggerated silhouette
comedy.

- **Setting**: an outdoor tent revival / camp meeting at dusk — a large canvas
  revival tent (or open framework of one) or open-air meeting ground, a wooden
  preaching platform/pulpit, packed crowd of congregants on benches or standing.
  Reference the actual Second Great Awakening camp-meeting tradition.
- **Preacher**: elevated above the crowd on the pulpit/platform, one arm raised
  mid-gesture (pointing, fist, or open hand thrust upward), captured mid-shout —
  dramatically lit (torchlight/lantern glow from below/side), larger and more
  dominant in the frame than any individual congregant.
- **Crowd**: dense, packed, uniform — many figures with arms raised, faces turned
  up toward the preacher, a few kneeling in the front rows. The uniformity of pose
  and the density of the crowd is what should read as "cult-like," not grotesque or
  comic exaggeration. Figures can be relatively simple/silhouetted rather than
  individually detailed — the crowd reads as a mass, not a set of individuals.
- **Lighting**: dusk sky darkening toward night, warm torchlight/lantern glow
  cutting through the gathering dark — this is the primary dramatic device (same
  functional role fire plays in `inferno/`, but here it's warm/campfire-like rather
  than infernal).

## Color palette

- **Sky**: dusk gradient — deep blue-violet at the top fading to warm amber/orange
  near the horizon, echoing both puritans/'s golden hour and inferno's warm-to-dark
  transition, but here the warmth comes from a setting sun AND torchlight, not fire
  from below.
- **Crowd/tent/ground**: mostly dark silhouetted values (charcoal, deep brown,
  near-black) so that torchlit rim-light and upturned lit faces read clearly against
  the dark mass — apply the same rim-lighting lesson learned in `inferno/`: dark
  figures on a dark background are illegible without deliberate backlight/rim glow
  from the torches.
- **Torchlight/lantern glow**: warm orange-gold, used both as literal light sources
  in the scene and as the main "aliveness"/flicker driver, same functional pattern
  as inferno's fire layer.
- **Preacher**: slightly higher contrast/more warmly lit than the crowd — he should
  be the clear focal point via lighting, not just position.

## Depth cueing

- Torchlight rim-lighting is the primary depth/legibility device (per the inferno
  lesson: dark-on-dark reads as an empty void, always back-light figures against a
  darker background layer with a warm glow).
- The preacher, as the focal point, should be the most clearly lit and highest
  contrast element in the frame — crowd figures further from a torch can be dimmer/
  more silhouetted, crowd figures nearer a torch more legible, giving some depth
  variation across the crowd itself.

## Motion language

- **No whole-scene camera rock** (unlike viking-invasion) — this scene favors a
  steadier, more tableau-like presentation, similar to inferno's approach.
- **Crowd slides in from the sides.** Rather than a fully static tableau, the
  congregation enters from the left and right edges of frame and settles into its
  packed position in front of the pulpit — similar in spirit to how the ship arrives
  in `puritans/arrival`, but here it's a crowd converging from both sides rather
  than a single object entering from one side.
- **Torchlight flicker** is the main secondary-motion/"aliveness" layer — brightness
  and slight scale variation over time, same technique as `inferno/`'s fire layer
  (additive blend, animated via `adjust-transform` scale keyframes rather than
  pre-rendered animated frames).
- **Preacher**: subtle animated gesture on the raised arm/robe is a nice-to-have but
  not required — a static dramatic pose reads fine given the lighting is doing the
  work. Keep any motion here minimal and intense, not busy.

## Layer plan

1. **Background**: dusk sky + distant treeline/field + tent structure, opaque,
   mostly static.
2. **Torchlight/glow layer**: alpha, additive blend, flickering — the scene's main
   animated element, same pattern as `inferno/`'s fire layer.
3. **Crowd layer(s)**: congregation figures, alpha, sliding in from left/right edges
   to their resting packed position in front of the pulpit.
4. **Preacher layer**: alpha, on the pulpit, sharpest focal point, dramatically lit.
5. **Universal paper-texture overlay**: per `../../context/requirements.md`, above
   the background, `multiply` blend.

## Audio style

- **Ambience bed**: low crowd murmur + night wind, continuous, mixed low (~-12dB
  relative to other layers, matching the established convention).
- **Event layer**: the preacher's shouted cadence (rhythmic, sermon-like vocal
  bursts — synthesized/abstracted, not literal words), crowd call-and-response
  bursts ("Amen"-like swells), and torch crackle — intermittent, present enough to
  feel the fervor without becoming literal/comedic.
- Music optional, added by ear in FCP UI, not a hard requirement.

## Reference implementation

`fire-and-brimstone/` is the first scene in this project and establishes the
pattern above. When starting a new great-awakening scene, reuse its overall
structure (dark silhouetted crowd + torchlight rim-lighting + edges-inward crowd
entrance + preacher as lit focal point) rather than importing another project's
architecture — don't reuse puritans/'s comical caricature approach or
viking-invasion's fast camera-rock parallax here.
