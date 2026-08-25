# Parallax Scenes

FCPXML-based layered parallax animations, built for Final Cut Pro.

## Structure

```
context/                       Universal docs — apply to every project. Read before
                                building any new scene, in any project.
  requirements.md               What every scene needs — the layer/tech checklist,
                                 plus the universal paper-overlay compositing rule.
  methodology.md                How to build FCPXML scenes on this machine — confirmed
                                 FCP quirks, bugs, and the fixes for each. Read this
                                 before writing any FCPXML by hand; it will save hours.

scenes/
  <project-name>/               One directory per visual "world"/project — e.g.
                                 viking-invasion/. Each project has its OWN style.md
                                 scoped to that project only; don't apply one
                                 project's style guide to another.
    style.md                    This project's visual and audio style — palette,
                                 aesthetic, motion language. Project-specific.
    <scene-name>/                One subdirectory per scene within the project.
      <scene-name>.fcpxml
      source_images/            Original PNG source art.
      video/                    Encoded .mov assets referenced by the FCPXML.
      audio/                    Encoded .wav/.mp3 assets referenced by the FCPXML.

universal-assets/              Shared assets used across EVERY scene in EVERY
                                project, regardless of that project's own style.
                                See context/requirements.md's "Universal overlay
                                layer" section for the current asset and how it
                                should be composited.
```

Current projects: `scenes/viking-invasion/` (scenes: `viking-ocean`,
`approaching-britain`, `church-on-the-hill`).

## Starting a new scene in an EXISTING project

1. Read `context/requirements.md` and ask the user the open questions listed there
   (subject/focus, layer count, mood, audio needs) if not already specified.
2. Read that project's `style.md` (e.g. `scenes/viking-invasion/style.md`) for the
   visual/audio language to match.
3. Read `context/methodology.md` before writing any FCPXML — it documents several
   FCP-specific bugs (still images crash on import, a position-value scaling quirk,
   rotation not inheriting through connected clips, etc.) that cost significant time
   to discover the first time. Don't rediscover them.
4. Create `scenes/<project-name>/<new-scene-name>/` with the same `source_images/` /
   `video/` / `audio/` subfolder structure as sibling scenes.
5. Source or generate art, encode every visual layer to `.mov` (never reference a
   raw image — see methodology.md #1), write the FCPXML, validate it parses, then
   hand off to the user to import and iterate in FCP.
6. Remember the universal paper-texture overlay (see requirements.md) — every scene
   in every project should include it, above the background, multiply blend.
7. If applying an FCP effect/filter whose exact XML syntax isn't already documented
   in methodology.md, ask the user to apply it manually in FCP and export the XML
   rather than guessing — this was consistently faster and more reliable.

## Starting a brand new project (new visual world)

Create `scenes/<new-project-name>/` with its own `style.md` (don't reuse or extend
another project's style guide — establish this project's palette/aesthetic/motion
language fresh, informed by whatever the user specifies), then follow the
"existing project" steps above for its first scene.
