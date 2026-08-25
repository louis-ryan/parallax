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

1. Encode every PNG in `source_images/` to `.mov` per
   `context/methodology.md`'s ffmpeg reference (ProRes 4444 for
   alpha/foreground layers — burning_longships, viking_backs, embers_overlay;
   ProRes 422 HQ for the opaque background — sky_sea_background).
2. Source/encode `video/` audio assets referenced in the FCPXML (Thunder,
   Ocean Waves) if not already present from another scene sharing them —
   check `uid` match per methodology.md's asset-reuse rule if reusing files
   from `viking-ocean` or `approaching-britain`.
3. Import `burning_longships.fcpxml` into FCP, confirm both audio tracks
   are present (the lane fix above), and iterate visually as needed.

## Questions for you

(none open)
