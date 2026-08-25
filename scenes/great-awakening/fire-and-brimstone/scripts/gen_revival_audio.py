#!/usr/bin/env python3
"""
Procedural audio for scenes/great-awakening/fire-and-brimstone.
Ambience bed: low crowd murmur + night wind (continuous).
Event layer: preacher's shouted cadence (abstracted, not literal words), crowd
"amen"-like call-and-response swells, torch crackle.
Fully synthesized -- no licensing concerns.
"""
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
DUR = 20.0
N = int(SR * DUR)
OUT = "/Users/louisryan/Desktop/parallax/scenes/great-awakening/fire-and-brimstone/audio"

rng = np.random.default_rng(41)

def lowpass(sig, cutoff, order=4):
    sos = butter(order, cutoff, btype="low", fs=SR, output="sos")
    return sosfilt(sos, sig)

def bandpass(sig, low, high, order=4):
    sos = butter(order, [low, high], btype="band", fs=SR, output="sos")
    return sosfilt(sos, sig)

def highpass(sig, cutoff, order=4):
    sos = butter(order, cutoff, btype="high", fs=SR, output="sos")
    return sosfilt(sos, sig)

def normalize(sig, peak=0.9):
    m = np.max(np.abs(sig))
    if m > 0:
        sig = sig / m * peak
    return sig

def fade(sig, in_s=1.0, out_s=1.5):
    n_in = int(in_s * SR)
    n_out = int(out_s * SR)
    sig = sig.copy()
    sig[:n_in] *= np.linspace(0, 1, n_in)
    sig[-n_out:] *= np.linspace(1, 0, n_out)
    return sig

t = np.arange(N) / SR

# ---------------------------------------------------------------------------
# Ambience: low crowd murmur (many overlapping low voice-band noise streams)
# + gentle night wind
# ---------------------------------------------------------------------------
murmur = np.zeros(N)
for _ in range(18):
    voice_noise = rng.standard_normal(N)
    voice = bandpass(voice_noise, 180, 900)
    offset_drift = 0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(0.02, 0.08) * t + rng.uniform(0, 6.28))
    murmur += voice * offset_drift * rng.uniform(0.4, 1.0)
murmur = normalize(murmur, 0.45)

wind = bandpass(rng.standard_normal(N), 150, 1800)
wind_drift = 0.6 + 0.4 * np.sin(2 * np.pi * 0.05 * t)
wind = normalize(wind * wind_drift, 0.3)

ambience = normalize(murmur * 0.75 + wind * 0.5, 0.85)
ambience = fade(ambience)
ambience_stereo = np.stack([ambience, ambience * 0.96], axis=1)
wavfile.write(f"{OUT}/revival_ambience.wav", SR, (ambience_stereo * 32767).astype(np.int16))
print("saved revival_ambience.wav")

# ---------------------------------------------------------------------------
# Event layer: preacher shout cadence (rhythmic low-formant tone bursts,
# abstracted not literal), crowd "amen" swells (broad chorus-like bursts),
# torch crackle (sparse high-freq pops)
# ---------------------------------------------------------------------------
event = np.zeros(N)

def make_shout(start_s, length_s, base_freq=140):
    n = int(length_s * SR)
    tt = np.arange(n) / SR
    vibrato = np.sin(2 * np.pi * 6 * tt) * 0.04
    freq = base_freq * (1 + vibrato) * (1 - 0.3 * tt / length_s)
    phase = 2 * np.pi * np.cumsum(freq) / SR
    tone = np.sin(phase) + 0.6 * np.sin(2 * phase) + 0.3 * np.sin(3 * phase)
    env = np.ones(n)
    a = int(0.08 * SR)
    r = int(0.25 * SR)
    env[:a] = np.linspace(0, 1, a)
    env[-r:] = np.linspace(1, 0, r)
    tone = tone * env
    tone = bandpass(tone, 90, 1200)
    start = int(start_s * SR)
    end = min(N, start + n)
    event[start:end] += tone[: end - start] * 0.4

for st, ln, f in [(1.0, 0.5, 160), (1.6, 0.4, 190), (2.1, 0.7, 130),
                   (7.0, 0.5, 155), (7.6, 0.6, 145),
                   (12.5, 0.4, 175), (13.0, 0.5, 150), (13.6, 0.6, 135),
                   (17.5, 0.5, 165)]:
    make_shout(st, ln, f)

def make_crowd_swell(start_s, length_s=1.0, base_freq=220):
    n = int(length_s * SR)
    tt = np.arange(n) / SR
    voices = np.zeros(n)
    for _ in range(10):
        fq = base_freq * rng.uniform(0.85, 1.2)
        voices += np.sin(2 * np.pi * fq * tt + rng.uniform(0, 6.28))
    voices = bandpass(voices, 150, 700)
    env = np.sin(np.pi * tt / length_s) ** 1.5
    voices = voices * env
    start = int(start_s * SR)
    end = min(N, start + n)
    event[start:end] += voices[: end - start] * 0.12

make_crowd_swell(3.0, 1.2, 210)
make_crowd_swell(8.5, 1.4, 200)
make_crowd_swell(14.5, 1.3, 220)

def make_crackle_burst(start_s, count=8):
    for _ in range(count):
        t0 = start_s + rng.uniform(0, 1.5)
        length = rng.integers(60, 250)
        amp = rng.uniform(0.1, 0.3)
        env = np.exp(-np.linspace(0, 9, length))
        pop = highpass(rng.standard_normal(length), 2000) * amp * env
        start = int(t0 * SR)
        end = min(N, start + length)
        if start < N:
            event[start:end] += pop[: end - start]

for st in [0.5, 4.5, 9.0, 13.0, 17.0]:
    make_crackle_burst(st)

event = normalize(event, 0.8)
event = fade(event, in_s=0.5, out_s=1.0)
event_stereo = np.stack([event, event * 0.97], axis=1)
wavfile.write(f"{OUT}/revival_events.wav", SR, (event_stereo * 32767).astype(np.int16))
print("saved revival_events.wav")
