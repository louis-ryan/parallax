# Methodology — Building FCPXML Parallax Scenes

Everything in this document was learned the hard way while building
`scenes/viking-ocean/`. Read this before writing a new scene's FCPXML by hand —
it will save you from repeating hours of trial and error.

## The core pipeline

1. **Source or generate art** for each layer as PNG (transparent where needed).
2. **Encode every visual layer to video** (`.mov`) with ffmpeg — never reference a
   raw image from `asset-clip`. See "Still images crash this FCP build" below.
3. **Write the FCPXML by hand**, referencing the encoded `.mov` files.
4. **Validate against the real FCP DTD**, not just well-formedness. Well-formedness
   (`python3 -c "import xml.dom.minidom as m; m.parse('file.fcpxml')"`) only catches
   malformed XML — it does NOT catch DTD ordering violations (e.g. `adjust-blend`
   appearing before `adjust-transform` inside an `asset-clip`, which the DTD requires
   in the opposite order). That kind of error passes well-formedness cleanly but fails
   FCP's real import with a DTD validation error. Instead validate against the actual
   DTD shipped with FCP on this machine:
   ```
   cd "/Applications/Final Cut Pro.app/Contents/Frameworks/Interchange.framework/Versions/A/Resources/"
   xmllint --dtdvalid "FCPXMLv1_14.dtd" --noout /path/to/file.fcpxml
   ```
   Must `cd` into that directory first — running `xmllint` with an absolute/relative
   path to the DTD from elsewhere fails with `xmlSAX2ResolveEntity` / "Could not parse
   DTD" (the DTD pulls in sibling files via relative paths). Exit code 0 and no output
   means valid. Do this before ever asking the user to import a hand-written FCPXML.
5. **Import in FCP and iterate.** Assume the first import will surface at least one
   surprise — this FCP build has several undocumented quirks (below). Build small
   isolated test files to diagnose, don't guess-and-check inside the full scene file.

## Critical, confirmed bugs/quirks in this FCP build

These cost the most time. They are specific to the FCP version installed on this
machine (12.3, running under macOS 26.5.2) and may not reproduce elsewhere — but
assume they apply until proven otherwise on a new machine.

### 1. Still-image `asset-clip`s crash FCP on import

Any `<asset-clip>` whose underlying `<asset>` is a still image (PNG, even a trivial
1x1 solid color) crashes FCP's importer (`FFXMLImporter`) with a SIGABRT inside
`addAssetClip:toObject:parentFormatID:`. This is **not** about asset attributes,
`duration="0s"` modeling, permissions, or DTD-correctness — it reproduces with a
minimal, DTD-valid file. A `<gap>` clip imports fine; swapping the same file for a
real video (`.mov`) asset also imports fine.

**Fix**: convert every visual layer to video before referencing it in FCPXML.
`ffmpeg -y -loop 1 -i layer.png -t 20 -r 30000/1001 -c:v prores_ks -profile:v 4444
-pix_fmt yuva444p10le layer.mov` (see `style.md` for exact profile choices per layer type).

### 2. `adjust-transform` position values render at 10.8x the stated number

Empirically confirmed (not theoretical) across multiple isolated tests: a `position`
value of `9000` on an `adjust-transform` `param` renders in FCP's Inspector as
`~97200` (ratio 10.8, exactly `1080/100` — consistent with FCP reading the value as
a percentage of frame height rather than raw pixels, though this is inferred, not
confirmed from source). This affects **both X and Y** components equally.

**Fix**: divide every intended true-pixel value by `10.8` before writing it into the
XML. E.g. to move something 200px down, write `-200/10.8 = -18.5185` as the Y value.
Always leave a comment in the XML noting which values are pre-divided, so a future
edit doesn't accidentally apply the correction twice or forget it.

**This is NOT specific to how the file is hand-authored — always apply the /10.8
correction to hand-written position values, full stop.** An earlier version of this
doc theorized that because FCP-native *exports* (e.g. `viking_ocean.fcpxml`, built by
tweaking the project inside the FCP UI) show plain, un-scaled numbers (`138.889`, not
`10.8x` anything), the quirk might only affect hand-authored files, and that FCP's own
export convention should be trusted instead. **This theory was tested and disproved**
while building `church_on_the_hill.fcpxml`: a hand-written position value of `1209`
was confirmed via Inspector to render at `13057.2` — exactly 10.8x, reproducing the
bug precisely. The likely explanation for the earlier confusion: FCP's own UI stores
transform values in a *different internal unit* than the FCPXML `position` attribute
expects on import, and FCP's exporter writes out that internal representation
directly — the exported numbers only *look* like plain un-scaled pixels; they aren't
being run through the same import-time interpretation your hand-written values are.
Do not use an FCP export's raw numbers as a "this proves the correction isn't needed"
signal — always test any new hand-authored value with an isolated Inspector check
before trusting it, and default to applying /10.8 to every hand-written position
value unless you've just re-verified otherwise on the current machine.

### 3. Rotation keyframes need `curve`, not `interp`

`<keyframe>` elements support both an `interp` attribute (`linear | ease | easeIn |
easeOut`) and a `curve` attribute (`linear | smooth`) per the DTD. For `adjust-transform`
params (`position`, `rotation`), only `curve` is honored — `interp` is silently
ignored (or in one observed case, produced an explicit "not supported" warning on
import). Use `curve="linear"` for constant-speed motion, `curve="smooth"` for eased
motion.

### 4. `param` elements need a `value` attribute seeded to match the first keyframe

A `<param name="position">` with only a `keyframeAnimation` child (no `value`
attribute on the `param` itself) may get silently corrupted or ignored, especially
when a sibling `param` on the same `adjust-transform` also has keyframes. Real FCP
exports always include `value="<first keyframe's value>"` on the param. Always set it.

### 5. Connected (lane) clips do NOT inherit their parent's `adjust-transform`

Confirmed by isolated test: rotating a parent `asset-clip`'s `adjust-transform` does
**not** rotate its lane-connected children — they remain visually static/independent.
This means you cannot "rock the whole scene" by rotating the top-level background
clip; each connected clip's transform is fully independent.

**Fix for whole-scene motion (e.g. camera rock)**: pre-compose the entire scene as a
`<media>` resource (a compound clip containing its own `<sequence>`/`<spine>`), then
reference it once via a single `<ref-clip>` in the outer sequence. The outer
`ref-clip` supports its own `adjust-transform`, which rotates/scales/pans the
**flattened, rendered composite** as one rigid unit — this is the only reliable way
to apply a single transform across many layers at once. See `viking_ocean.fcpxml`'s
`<media id="r2">` / `<ref-clip ref="r2">` structure for the working pattern.

**This outer-`ref-clip`-transform trick only works for SMALL transforms that stay
within the compound's own rendered canvas** (e.g. viking-ocean's ~±1.6° rock, or a
few percent of zoom). It breaks down for large/dramatic moves like a big zoom-out or
pull-back reveal: the compound clip flattens to a single 1920x1080 image, and scaling
or panning *that* image exposes its own canvas edges as black/empty space — you get
"a fixed picture sliding/zooming into a static viewfinder," not "a camera moving
through a scene." This was discovered building `church-on-the-hill`'s bell-tower
pull-out reveal, where a large scale-out (3.6x → 1.0x) on the outer `ref-clip`
produced exactly that broken "mostly black, picture slides in" symptom.

**Fix for large/dramatic whole-scene camera moves (zoom-out reveals, big pans)**:
don't put the animation on the outer `ref-clip` at all — animate each individual
layer's own `adjust-transform` instead, with every layer's `scale`/`position`
keyframes computed to move in lockstep (see the math below). Each layer's source
canvas already extends well past the frame at its resting scale (1.15-1.2x), so
zooming further into that oversized canvas reveals more of its own real content
instead of empty compound-clip edges. The outer `ref-clip` in this case carries no
transform at all — it's just a structural wrapper for consistency with the other
scenes (and a place to attach audio clips). See `church_on_the_hill.fcpxml` for the
working pattern.

**Math for keeping a focal point fixed while every layer zooms out in sync**: pick a
point on screen to hold steady (e.g. the church tower), expressed as `(dx, dy)` offset
from frame center in FCP's y-up coordinate system. For a layer zooming from
`start_scale` down to its resting `base_scale`, its position keyframe at the
zoomed-in extreme is `(-dx * (start_scale/base_scale - 1), -dy * (start_scale/base_scale - 1))`,
easing linearly to `(0, 0)` at the resting frame. Apply the *same relative ratio*
(`start_scale/base_scale`) to every layer even though their absolute `start_scale`
values differ (since each layer's resting `base_scale` differs) — this keeps the
focal point aligned across all layers throughout the zoom, not just at the two
endpoints.

### 6. Duplicate `ref` across sibling connected clips corrupts position values

Using the same asset `ref` for multiple sibling `asset-clip`s (e.g. three tiles all
referencing the same tile video, for seamless tiling) causes FCP to apply an
unpredictable multiplier (observed: both ~10x and ~10.8x depending on the specific
value) to position on the *second and later* clips referencing that asset — but not
the first. This is a **different bug** from #2 (which affects all clips uniformly);
this one is inconsistent and value-dependent, which makes it much harder to
pre-compensate for reliably.

**Do not attempt to fix this with a duplicate `<asset>` entry with a different `uid`**
— FCP rejects the import outright ("media already exists in the library with a
different unique identifier"). Giving the duplicate asset the *same* `uid` as the
original causes FCP to alias the two clips together (they share state, lose
independent animation) — also broken.

**The only clean fix found**: don't fight it in hand-authored XML. Build the tiling
in FCP's own UI instead (duplicate the clip via FCP's timeline, not via XML), or
accept a single wide/seamless texture per layer instead of multiple tiled instances.
If tiling via multiple `asset-clip`s referencing the same asset is unavoidable, test
each instance's actual rendered position in Inspector after import and hand-correct —
don't trust computed values for anything past the first clip.

### 6b. Reusing an asset file across scenes: match its `uid` exactly, or FCP rejects the import

When a new scene reuses a media file that's already been imported by an earlier
scene's FCPXML (e.g. `ocean_waves.wav` shared between `viking-ocean` and
`church-on-the-hill`), FCP identifies that file by content, not by path. If the new
scene's `<asset>` entry gives it a **different `uid`** than the one FCP already has
on record for that file, import fails outright:

> The media already exists in the library with a different unique identifier.
> (uid="...": /fcpxml[1]/resources[1]/asset[N]/@uid)
> The file X cannot be imported again with a different unique identifier

**Fix**: when reusing a media file in a new scene, copy the **exact `uid` string**
from the asset entry in whichever scene's FCPXML first introduced that file — don't
invent a new one just because it's a new `<asset id>` in a new file. `id` can (and
should) be scene-local/arbitrary; `uid` must stay consistent for the same underlying
file across every FCPXML that references it.

**This also applies within a single file**, not just across files: if one FCPXML
declares multiple `<asset>` entries (distinct `id`s, per the #6 fix below) that all
point at the same underlying media file, every one of those entries must share the
exact same `uid` too. Confirmed the hard way in `three_threats.fcpxml` — `r6`, `r11`,
`r12` all reference `cross_mark.mov`; giving `r11`/`r12` their own invented `uid`
strings (reasoning "distinct id, so distinct uid") produced this exact import
rejection on the very first `<asset>` FCP hadn't seen yet with that uid, because FCP
tracks media identity by content across the whole library/import, not scoped to one
FCPXML. The earlier note above ("giving the duplicate asset the same uid... causes
FCP to alias the two clips together, also broken") describes *sibling connected
clips* pointed at each other via the same `ref` — that's bug #6's territory. Multiple
separate `<asset>` resource entries sharing one `uid`, each referenced by exactly one
`asset-clip`, is the correct and required pattern; it's `ref` duplication (not `uid`
duplication) that causes the aliasing/position problems.

This is distinct from bug #6 above (duplicate `ref` corrupting position) — this one
is about duplicate/mismatched `uid` for the same underlying file being rejected at
import time entirely, with no position corruption involved.

### 6c. `adjust-transform` must come before `adjust-blend` inside an `asset-clip`

The DTD requires a fixed child-element order inside `asset-clip`:
`adjust-transform` (and the other `adjust-*` crop/corners/conform/etc. elements)
**before** `adjust-blend`, which comes before `adjust-volume`/`adjust-panner`, which
comes before the clip's own inner content (nested `asset-clip`s, `filter-video`,
etc.). Writing `<adjust-blend>` first, then `<adjust-transform>`, is well-formed XML
(passes a plain parse) but fails real FCP import with a DTD content-model error
mentioning the expected sequence. Confirmed the hard way building
`inferno/satan-bound.fcpxml`: two clips (`adjust-blend` then `adjust-transform`, in
that order) imported fine as XML but failed FCP's DTD validator; swapping to
transform-then-blend fixed it, confirmed via `xmllint --dtdvalid` (see the validation
step above). Default order for any clip using both: `adjust-transform`, then
`adjust-blend`, then `filter-video` — matches `viking_ocean.fcpxml`'s
"Lightning Overlay" clip, which was never hand-edited to break this and always
worked.

### 6d. "The video frame rates don't match" can actually mean "the file path is wrong"

FCP reported this exact error against `asset[1]` in `church_on_the_hill.fcpxml`
("The media could not be imported... The video frame rates don't match."), which
looked like a genuine frame-rate mismatch at first — but every `.mov` in the
project (including this file's own siblings) is consistently encoded at
29.97fps (`30000/1001`) against a `format` declaration of exactly 30fps
(`1001/30030s` / `100/3000s`), including in `viking_ocean.fcpxml`, which has
imported and worked fine throughout this project. So that declared-vs-actual gap
is not, on its own, fatal — FCP tolerates it in every other scene.

The actual cause turned out to be unrelated to frame rate at all: every single
`<media-rep src="file://...">` path in the file pointed at
`scenes/church-on-the-hill/...` (missing the `viking-invasion/` path segment) —
stale paths left over from before this scene's directory was moved under
`scenes/viking-invasion/` earlier in the project. `scenes/church-on-the-hill/`
doesn't exist at all; FCP couldn't resolve the real media, and reported a
misleading frame-rate error instead of a missing-file error.

**Lesson**: if FCP reports a frame-rate mismatch on an asset that hasn't had its
encoding touched, or that matches its siblings' encoding exactly, check the
`media-rep src` path resolves to a real file on disk **before** assuming the
encode itself is wrong — a bad/stale path can surface as this exact confusing
error. `grep -o 'src="[^"]*"' file.fcpxml` plus a quick per-path
`os.path.exists()` check (strip the `file://` prefix) catches this immediately.
This is also a natural failure point after any directory reorganization (moving
a scene folder, renaming a project directory) — re-verify every `media-rep src`
path in every FCPXML under the moved directory, not just the ones edited that
session.

### 7. Gaussian Blur syntax (confirmed via real FCP export)

```xml
<!-- in resources -->
<effect id="r9" name="Gaussian" uid=".../Effects.localized/Blur.localized/Gaussian.localized/Gaussian.moef"/>

<!-- on a clip -->
<filter-video ref="r9" name="Gaussian">
    <param name="Amount" key="9999/986883370/100/986883376/2/100" value="0.0697"/>
    <param name="Blur Boost" key="9999/986883370/100/986884620/2/100" value="0.108"/>
</filter-video>
```

The `key` values for `Amount`/`Blur Boost` look like opaque internal path IDs — copy
them verbatim rather than trying to derive them. `Amount` around `0.03`–`0.10` reads
as a subtle-to-moderate blur at 1080p. **This syntax was obtained by having the user
apply the effect manually in FCP's UI and exporting the XML — this is the reliable
way to get exact syntax for any new effect type**, rather than guessing from
documentation. Do this proactively for the next new effect type needed (color
grades, other filters, transitions) rather than guessing blind.

### 8. General diagnostic approach that worked

When something doesn't render as expected and the XML looks structurally correct:

1. **Don't keep editing the full scene file blind.** Build a minimal, isolated 2-3
   clip test file that reproduces just the suspect behavior.
2. **Ask the user to check FCP's Inspector for the actual rendered value**, not just
   "does it look right" — several bugs here were invisible until we compared the
   XML's stated value against Inspector's displayed value.
3. **Get exact numbers, not "around X."** Ratios like 10.8 vs 10 only became
   distinguishable once the user reported precise Inspector readouts across multiple
   test values.
4. **Check `~/Library/Logs/DiagnosticReports/` for crash logs** if FCP crashes
   outright — the `.ips` files contain a real stack trace (`asiBacktraces` field)
   that pinpoints the failing internal method, which is far more reliable than
   guessing from symptoms.
5. **When in doubt about exact syntax for an effect/filter**, ask the user to apply
   it manually in FCP and export XML, then read the real output. This was faster and
   more reliable than any web search for Apple's internal effect UIDs and param keys.

## Building tiled/seamless layers

To make a panning layer feel like it's "already in motion" from off-screen (rather
than starting/ending mid-frame):

- Make the panning layer's own canvas **wider than the frame** with real content
  spanning the extra width, OR
- Use multiple side-by-side clips of the same tile, positioned edge-to-edge with a
  slight overlap, panning in lockstep (see bug #6 above for why this is fragile).

**Wave/water-specific lesson**: if generating procedural wave art, the wave crest's
*feature wavelength* (the horizontal distance between crest peaks) must be **larger
than the frame width** — otherwise a full wave cycle visibly enters and exits frame
during the pan, reading as "the same shape sliding" rather than continuous ocean.
Making the *canvas* wider without also increasing the feature wavelength does not fix
this — canvas size and feature size are independent variables. Conversely, don't
overcorrect either: an extremely large wavelength (several times the frame width)
makes the crest look almost flat/static across the visible frame, which reads as the
whole scene "slowing down" even though the pan speed hasn't changed — feature size
needs to be tuned to look proportionate at the actual pan speed and duration, not just
"as large as possible."

For hard seams between tiled layers: generate the tile with a **feathered
(alpha-faded) left/right edge** (~200px feather worked well at 1920px width) and have
adjacent tile instances overlap slightly into each other's feathered zone, rather than
meeting edge-to-edge with a hard cut.

## Asset sourcing that worked

- **OpenGameArt.org**: reliably fetchable (no bot-blocking), CC0/CC-BY/OGA-BY
  licensed, good for pixel-art sprites, tiles, and backgrounds. `curl` works directly
  on download links.
- **Pexels** (video): direct download URLs (`pexels.com/download/video/<id>/`)
  redirect to a fetchable CDN URL (`videos.pexels.com/...`) even though the main site
  has some Cloudflare protection — this worked for sourcing a lightning storm video.
- **SoundBible**: reliably fetchable, CC-BY licensed, good for sound effects
  (`soundbible.com/grab.php?id=<id>&type=mp3` gives a direct download).
- **freesoundslibrary.com**: reliably fetchable, CC-BY 4.0, direct zip downloads.

## Asset sourcing that did NOT work

- **itch.io**: blocks all automated requests with a Cloudflare bot challenge, even a
  bare page load. Do not attempt — ask the user to download manually if an itch.io
  asset is truly needed.
- **Pixabay**: same Cloudflare blocking as itch.io for both the main site and direct
  media URLs. Their API requires a registered key not available here.

## Local ffmpeg encoding reference

Background / opaque layers:
```
ffmpeg -y -loop 1 -i layer.png -t 20 -r 30000/1001 -pix_fmt yuv420p \
  -c:v prores_ks -profile:v 3 layer.mov
```

Alpha-channel layers (foreground, sprites, overlays):
```
ffmpeg -y -loop 1 -i layer.png -t 20 -r 30000/1001 \
  -c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le layer.mov
```

Trimming/fading a sourced video or audio clip to the scene duration:
```
ffmpeg -y -i source.mp4 -t 20 -c:v prores_ks -profile:v 3 out.mov
ffmpeg -y -i source.mp3 -t 20 -af "afade=t=in:st=0:d=1,afade=t=out:st=18.5:d=1.5" \
  -ar 48000 -ac 2 out.wav
```

Always verify the encode with `ffprobe -show_streams` (check width/height/duration)
before wiring it into the XML — don't assume the encode succeeded from exit code
alone, especially for large parallel background encodes.
