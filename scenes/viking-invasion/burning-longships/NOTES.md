# viking-invasion / burning-longships

Status: Done (everything achievable headlessly — see manual steps below)

## Spec

Danish Vikings on a beach in Britain, backs to camera, watching their own
longships burn; flames rise into a stormy sky. Behind the ships is the
sea/sky/storm. Camera pans across the scene. Parallax: Vikings (foreground)
move fastest, burning ships (midground) move slower, storm sky/sea
(background) moves slowest. Dusk/storm palette per `../style.md`. Duration:
20s (default).

## Progress notes

- Source art generated (`source_images/`): storm sky/sea background,
  burning longships, Viking crowd silhouettes (backs to camera), rising
  embers overlay.
- `burning_longships.fcpxml` written and validated (well-formed, DTD element
  ordering confirmed against `satan_bound.fcpxml`'s paper-overlay pattern —
  `adjust-transform` before `adjust-blend` before nested content/filters).
  Includes the universal paper-texture overlay (multiply blend, directly
  above background) per `context/requirements.md`.
- **Bug found and fixed** (2026-08-25): the first pushed version had both
  audio clips (Thunder, Ocean Waves) sharing `lane="-1"` under the
  camera-rig `ref-clip` — every other scene in this repo gives sibling
  connected clips distinct lanes, and sharing one risked dropping a track
  on import. Fixed by moving Ocean Waves Audio to `lane="-2"`.
- Two concurrent scheduled runs raced on this scene the same hour (one
  manually triggered, one from the normal hourly cron). Handled cleanly:
  the second run detected the collision via `git fetch`, discarded its own
  duplicate build, adopted the already-pushed version, and did the bug-fix
  pass on it instead of creating a conflicting scene.

## Manual steps remaining (yours, in Final Cut Pro)

All asset files are now in place locally (done 2026-08-25 — `video/` and
`audio/` are gitignored, so this happened outside the repo):

- Encoded `sky_sea_background.mov` (ProRes 422 HQ, opaque), and
  `burning_longships.mov` / `viking_backs.mov` / `embers_overlay.mov`
  (ProRes 4444, alpha) from the PNGs in `source_images/`, per
  `context/methodology.md`'s ffmpeg reference.
- Copied `paper_background.mp4` from `universal-assets/`.
- Copied `lightning.mov`, `thunder.wav`, `ocean_waves.wav` from
  `viking-ocean`'s `video/`/`audio/` folders — these are shared assets
  (matching `uid`) reused across viking-invasion scenes, not new encodes.
  The FCPXML referencing a reused asset only works once the file is
  physically copied into *this* scene's own `video/`/`audio/` folder, not
  just uid-matched — see methodology.md's note under bug #6b. (This was
  the actual cause of an earlier "video frame rates don't match" import
  error — a missing lightning.mov file, not a real encoding mismatch.)

1. Import `burning_longships.fcpxml` into FCP — all 8 referenced assets
   (6 video, 2 audio) now exist and should resolve. Confirm both audio
   tracks are present (the lane fix above) and iterate visually as needed.

## Questions for you

(none open)
