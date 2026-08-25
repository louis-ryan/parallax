#!/usr/bin/env python3
"""
Generates spreading_the_word.fcpxml for scenes/infographic/spreading-the-word.
Follows the established infographic project pattern (see ../romantic-dream and
../three-threats): Hessian base + multiply paper texture + stop-motion
paper-cutout pieces, hero (map) + secondary hero (press) + staggered radiating
pieces (newspapers) + stepped-flicker glow bursts (flame variants).

All position/scale values are TRUE PIXEL offsets divided by 10.8 per
methodology.md bug #2.
"""

SCENE_DIR = "/Users/louisryan/Desktop/parallax/scenes/infographic/spreading-the-word"

def px(v):
    return v / 10.8

def fmt(v):
    return f"{v:.4f}".rstrip("0").rstrip(".") if "." in f"{v:.4f}" else f"{v:.4f}"

def _dedupe_emit(raw):
    """raw: list of (time_float, value_str) IN INTENDED CHRONOLOGICAL ORDER.
    Two cleanup passes, since per-newspaper entrance delays are computed
    independently from the shared IDLE_TIMES list and can collide with or
    fall after it in either direction:
    1. Collapse ANY keyframes whose timestamps round to the same 2-decimal
       value (keeping the last one seen for that timestamp), not just
       adjacent-in-list ones -- e.g. entrance `delay` exactly equal to a
       later shared IDLE_TIMES value.
    2. Drop any entry whose rounded time is <= the max time already kept,
       enforcing strict monotonic increase -- e.g. entrance `settle` (delay-
       based) landing AFTER an early shared IDLE_TIMES entry, which would
       otherwise emit a keyframe list that goes backwards in time.
    """
    by_time = {}
    for t, val in raw:
        by_time[round(t, 2)] = val
    ordered_keys = sorted(by_time.keys())

    kept = []
    max_t = -1.0
    for k in ordered_keys:
        if k <= max_t:
            continue
        kept.append((k, by_time[k]))
        max_t = k
    lines = [f'<keyframe time="{t:.2f}s" value="{val}" curve="linear"/>' for t, val in kept]
    return "\n".join(f"                                        {l}" for l in lines)


def snap_scale_block(delay, rise_start, rise_end, overshoot, rest, idle_times, idle_deltas):
    """Stop-motion snap entrance (0 -> overshoot -> rest) then idle jitter,
    matching romantic-dream's established scale-keyframe shape."""
    raw = [(0.0, "0 0"), (delay, "0 0"),
           (rise_start, f"{fmt(overshoot)} {fmt(overshoot)}"),
           (rise_end, f"{fmt(overshoot)} {fmt(overshoot)}")]
    settle = rise_end + 0.04
    raw.append((settle, f"{fmt(rest)} {fmt(rest)}"))
    for t, dscale in zip(idle_times, idle_deltas):
        v = rest + dscale
        raw.append((t, f"{fmt(v)} {fmt(v)}"))
    raw.append((20.0, f"{fmt(rest)} {fmt(rest)}"))
    return _dedupe_emit(raw)


def flight_position_block(delay, rise_start, rest_settle_time, start_dx_true, start_dy_true, rest_dx_true, rest_dy_true, idle_times, idle_jitters):
    """Newspaper 'flight': starts at the press's location (small offset from
    center, true px), snaps/settles to its landing rest position (true px),
    then idle-jitters -- all values pre-divided by 10.8."""
    sx, sy = px(start_dx_true), px(start_dy_true)
    rx, ry = px(rest_dx_true), px(rest_dy_true)
    raw = [(0.0, f"{fmt(sx)} {fmt(sy)}"), (rise_start, f"{fmt(sx)} {fmt(sy)}"),
           (rest_settle_time, f"{fmt(rx)} {fmt(ry)}")]
    for t, (jdx, jdy) in zip(idle_times, idle_jitters):
        v_x, v_y = px(rest_dx_true + jdx), px(rest_dy_true + jdy)
        raw.append((t, f"{fmt(v_x)} {fmt(v_y)}"))
    raw.append((20.0, f"{fmt(rx)} {fmt(ry)}"))
    return _dedupe_emit(raw)


def rotation_block(delay, rise_start, rise_end, overshoot_deg, rest_deg, idle_times, idle_deltas):
    raw = [(0.0, "0"), (delay, "0"),
           (rise_start, f"{overshoot_deg:.1f}"), (rise_end, f"{overshoot_deg:.1f}")]
    settle = rise_end + 0.04
    raw.append((settle, f"{rest_deg:.1f}"))
    for t, d in zip(idle_times, idle_deltas):
        raw.append((t, f"{rest_deg + d:.1f}"))
    raw.append((20.0, f"{rest_deg:.1f}"))
    return _dedupe_emit(raw)


IDLE_TIMES = [6.4, 7.3, 8.2, 10.5, 14, 17.5]
IDLE_SCALE_DELTAS = [0.006, -0.006, 0, 0.003, 0, -0.002]
IDLE_ROT_DELTAS = [0.3, -0.3, 0, 0.2, 0.4, -0.2]
IDLE_POS_JITTERS_TRUE = [(5, 4), (-6, -3), (0, 0), (4, -5), (0, 0), (-3, 4)]

# Newspapers: (name, true_dx, true_dy, rest_scale, rest_rotation_deg, entrance_delay)
# true-px targets match build_map_press.py's NEWSPAPER_TARGETS exactly --
# real, period-plausible cities verified to land inside the actual US
# landmass geometry (see build_real_map.py), not the earlier hand-picked
# compass-point offsets that fell outside the real, narrower US outline.
NEWSPAPERS = [
    ("ne", 644, -133, 0.42, -10, 1.6),    # Boston
    ("se", 383, 134, 0.42, 8, 2.4),       # Savannah
    ("nw", -697, -215, 0.42, 12, 3.2),    # Portland, OR
    ("sw", -69, 204, 0.42, -9, 4.0),      # San Antonio
    ("mw", 213, -120, 0.42, 5, 4.8),      # Chicago
    ("c", 147, -36, 0.42, -6, 5.6),       # St. Louis
    ("s", 150, 190, 0.42, 11, 6.4),       # New Orleans
]

# Press location (true px offset from frame center) -- newspapers "fly out"
# from near this point.
PRESS_X, PRESS_Y = 0, -20

resources = []
spine_pieces = []

# --- Hessian + paper texture (r3 lane 0 base, r4 lane 1) ---
hessian_xml = '''                    <asset-clip ref="r3" offset="0s" name="Hessian Background" duration="20s" tcFormat="NDF">
                        <adjust-transform scale="1.0 1.0"/>
                        <adjust-blend amount="0.7"/>

                        <asset-clip ref="r4" lane="1" offset="0s" name="Paper Texture (multiply)" duration="20s" tcFormat="NDF">
                            <adjust-transform scale="1.0 1.0"/>
                            <adjust-blend mode="multiply"/>
                        </asset-clip>
'''

# --- US Map hero (r5, lane 2) ---
map_scale = snap_scale_block(0, 0.48, 0.5, 1.06, 1.0, IDLE_TIMES, IDLE_SCALE_DELTAS)
map_pos = flight_position_block(0, 0.48, 0.5, 0, 0, 0, 10, IDLE_TIMES, IDLE_POS_JITTERS_TRUE)
map_xml = f'''                        <asset-clip ref="r5" lane="2" offset="0s" name="Hero – US Map" duration="20s" tcFormat="NDF">
                            <adjust-transform>
                                <param name="scale" value="0 0">
                                    <keyframeAnimation>
{map_scale}
                                    </keyframeAnimation>
                                </param>
                                <param name="position" value="0 {fmt(px(10))}">
                                    <keyframeAnimation>
{map_pos}
                                    </keyframeAnimation>
                                </param>
                            </adjust-transform>
                        </asset-clip>
'''

# --- Press hero (r6, lane 3) ---
press_scale = snap_scale_block(0.72, 1.2, 1.22, 0.62, 0.55, IDLE_TIMES, IDLE_SCALE_DELTAS)
press_pos = flight_position_block(0.72, 1.2, 1.22, PRESS_X, PRESS_Y, PRESS_X, PRESS_Y, IDLE_TIMES, IDLE_POS_JITTERS_TRUE)
press_xml = f'''                        <asset-clip ref="r6" lane="3" offset="0s" name="Press – Hero" duration="20s" tcFormat="NDF">
                            <adjust-transform>
                                <param name="scale" value="0 0">
                                    <keyframeAnimation>
{press_scale}
                                    </keyframeAnimation>
                                </param>
                                <param name="position" value="{fmt(px(PRESS_X))} {fmt(px(PRESS_Y))}">
                                    <keyframeAnimation>
{press_pos}
                                    </keyframeAnimation>
                                </param>
                            </adjust-transform>
                        </asset-clip>
'''

resource_id = 7
newspaper_pieces = []
burst_pieces = []

for idx, (name, dx, dy, rest_scale, rest_rot, delay) in enumerate(NEWSPAPERS):
    lane = 4 + idx
    rid = resource_id
    resource_id += 1
    rise_start = delay + 0.02
    rise_end = delay + 0.20
    overshoot = rest_scale * 1.08

    scale_block = snap_scale_block(delay, rise_start, rise_end, overshoot, rest_scale, IDLE_TIMES, IDLE_SCALE_DELTAS)
    pos_block = flight_position_block(delay, rise_start, rise_end + 0.04, PRESS_X, PRESS_Y, dx, dy, IDLE_TIMES, IDLE_POS_JITTERS_TRUE)
    rot_block = rotation_block(delay, rise_start, rise_end, rest_rot * 1.6, rest_rot, IDLE_TIMES, IDLE_ROT_DELTAS)

    piece_xml = f'''                        <asset-clip ref="r{rid}" lane="{lane}" offset="0s" name="Newspaper – {name.upper()}" duration="20s" tcFormat="NDF">
                            <adjust-transform>
                                <param name="scale" value="0 0">
                                    <keyframeAnimation>
{scale_block}
                                    </keyframeAnimation>
                                </param>
                                <param name="position" value="{fmt(px(PRESS_X))} {fmt(px(PRESS_Y))}">
                                    <keyframeAnimation>
{pos_block}
                                    </keyframeAnimation>
                                </param>
                                <param name="rotation">
                                    <keyframeAnimation>
{rot_block}
                                    </keyframeAnimation>
                                </param>
                            </adjust-transform>
                        </asset-clip>
'''
    newspaper_pieces.append(piece_xml)
    resources.append((rid, f"newspaper_{name}", f"spreading_word_newspaper_{name}_mov_uid", f"newspaper_{name}.mov"))

    # Flame burst: 3 variants (a/b/c), stepped flicker starting once the
    # newspaper lands (rise_end + settle), looping until 20s. Position is
    # FIXED at the landing point (no idle jitter needed on the glow itself).
    land_time = rise_end + 0.06
    burst_pos_true = (dx, dy)
    variant_names = ["a", "b", "c"]
    # simple round-robin flicker cycle across the three variants, starting
    # at land_time, each variant visible ~0.5-0.9s at a time (matches the
    # established flame-flicker cadence)
    cycle = []
    t = land_time
    import random as _r
    rnd = _r.Random(1000 + idx)
    vi = 0
    while t < 19.8:
        dur = rnd.uniform(0.5, 1.0)
        cycle.append((vi % 3, t, min(t + dur, 20.0)))
        t += dur
        vi += 1

    for vi_target, vname in enumerate(variant_names):
        rid_b = resource_id
        resource_id += 1
        lane_b = 11 + idx * 3 + vi_target

        # Build (time, value) pairs first, across the FULL cycle timeline
        # (not just this variant's own segments), so gap-fill keyframes are
        # computed against true elapsed time rather than only-this-variant
        # elapsed time -- the earlier version tracked prev_end only across
        # matching segments, which under-advanced it and emitted duplicate
        # timestamps whenever another variant's segment intervened.
        raw = [(0.0, 0, 0)]
        for (vi_cur, on_t, off_t) in cycle:
            if vi_cur == vi_target:
                raw.append((on_t, 0, 0))
                raw.append((on_t + 0.02, 1, 1))
                raw.append((off_t - 0.02, 1, 1))
                raw.append((off_t, 0, 0))
            else:
                raw.append((on_t, 0, 0))
        raw.append((20.0, 0, 0))

        # Dedupe consecutive identical/near-identical timestamps (keep the
        # last value at any given instant), then round.
        deduped = []
        for t, vx, vy in raw:
            if deduped and abs(t - deduped[-1][0]) < 0.005:
                deduped[-1] = (t, vx, vy)
            else:
                deduped.append((t, vx, vy))

        kf = []
        for t, vx, vy in deduped:
            kf.append(f'<keyframe time="{t:.2f}s" value="{vx} {vy}" curve="linear"/>')
        kf_block = "\n".join(f"                                        {l}" for l in kf)

        burst_xml = f'''                        <asset-clip ref="r{rid_b}" lane="{lane_b}" offset="0s" name="Burst – {name.upper()} {vname}" duration="20s" tcFormat="NDF">
                            <adjust-transform>
                                <param name="scale" value="0 0">
                                    <keyframeAnimation>
{kf_block}
                                    </keyframeAnimation>
                                </param>
                                <param name="position" value="{fmt(px(dx))} {fmt(px(dy))}"/>
                            </adjust-transform>
                            <adjust-blend mode="add"/>
                        </asset-clip>
'''
        burst_pieces.append(burst_xml)
        resources.append((rid_b, f"burst_newspaper_{name}_{vname}", f"spreading_word_burst_{name}_{vname}_mov_uid", f"burst_newspaper_{name}_{vname}.mov"))

# --- Assemble spine ---
spine_body = hessian_xml + map_xml + press_xml + "".join(newspaper_pieces) + "".join(burst_pieces) + "                    </asset-clip>\n"

# --- Assemble resources block ---
resource_lines = []
resource_lines.append('        <asset id="r3" name="hessian_background" uid="three_threats_hessian_bg_mov_uid" start="0s" duration="20s" hasVideo="1" format="r1" videoSources="1">')
resource_lines.append(f'            <media-rep kind="original-media" src="file://{SCENE_DIR}/video/hessian_background.mov"/>')
resource_lines.append('        </asset>')
resource_lines.append('        <asset id="r4" name="paper_background" uid="three_threats_paper_bg_mov_uid" start="0s" duration="20s" hasVideo="1" format="r1" videoSources="1">')
resource_lines.append(f'            <media-rep kind="original-media" src="file://{SCENE_DIR}/video/paper_background.mov"/>')
resource_lines.append('        </asset>')
resource_lines.append('        <asset id="r5" name="us_map" uid="spreading_word_us_map_mov_uid" start="0s" duration="20s" hasVideo="1" format="r1" videoSources="1">')
resource_lines.append(f'            <media-rep kind="original-media" src="file://{SCENE_DIR}/video/us_map.mov"/>')
resource_lines.append('        </asset>')
resource_lines.append('        <asset id="r6" name="press" uid="spreading_word_press_mov_uid" start="0s" duration="20s" hasVideo="1" format="r1" videoSources="1">')
resource_lines.append(f'            <media-rep kind="original-media" src="file://{SCENE_DIR}/video/press.mov"/>')
resource_lines.append('        </asset>')

for rid, name, uid, filename in resources:
    resource_lines.append(f'        <asset id="r{rid}" name="{name}" uid="{uid}" start="0s" duration="20s" hasVideo="1" format="r1" videoSources="1">')
    resource_lines.append(f'            <media-rep kind="original-media" src="file://{SCENE_DIR}/video/{filename}"/>')
    resource_lines.append('        </asset>')

resources_xml = "\n".join(resource_lines)

fcpxml = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE fcpxml>

<!--
Procedurally generated art (PIL scripts in source_images/), not sourced imagery.
Depicts a steam printing press distributing newspapers carrying a doomsday
religious prophecy across a map of the nineteenth century United States;
newspapers fly out from the press to distributed points across the map, each
landing with a warm flame glow burst symbolizing the prophecy "catching fire"
as it spreads.
-->

<fcpxml version="1.14">
    <resources>
        <format id="r1" name="FFVideoFormat1080p30" frameDuration="1001/30030s" width="1920" height="1080" colorSpace="1-1-1 (Rec. 709)"/>

        <!-- COMPOUND SCENE — see ../../../context/methodology.md. No whole-scene
             camera transform — flat infographic collage. Structure mirrors
             ../romantic-dream/romantic_dream.fcpxml (Hessian base + multiply
             paper texture + stop-motion paper-cutout pieces), adapted for a
             "map hero + press hero + radiating newspaper pieces + landing
             flame bursts" composition. -->
        <media id="r2" name="Spreading the Word Compound" uid="spreading_word_compound_uid">
            <sequence format="r1" duration="20s" tcStart="0s" tcFormat="NDF" audioLayout="stereo" audioRate="48k">
                <spine>
{spine_body}                </spine>
            </sequence>
        </media>

{resources_xml}
    </resources>

    <library>
        <event name="Spreading the Word">
            <project name="Spreading the Word">
                <sequence format="r1" duration="20s" tcStart="0s" tcFormat="NDF" audioLayout="stereo" audioRate="48k">
                    <spine>
                        <ref-clip ref="r2" offset="0s" name="Spreading the Word – Master" duration="20s"/>
                    </spine>
                </sequence>
            </project>
        </event>
    </library>
</fcpxml>
'''

with open(f"{SCENE_DIR}/spreading_the_word.fcpxml", "w") as f:
    f.write(fcpxml)

print("wrote spreading_the_word.fcpxml")
