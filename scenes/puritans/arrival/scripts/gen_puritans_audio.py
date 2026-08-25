#!/usr/bin/env python3
"""
Procedural audio for scenes/puritans/arrival.
Ambience bed: coastal wind + gentle waves (continuous).
Event layer: creaking wooden ship timbers + seagull calls (intermittent).
Fully synthesized -- no licensing concerns.
"""
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
DUR = 20.0
N = int(SR * DUR)
OUT = "/Users/louisryan/Desktop/parallax/scenes/puritans/arrival/audio"

rng = np.random.default_rng(23)

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
# Ambience: coastal wind (broad mid/high filtered noise, slow drift) + gentle
# waves (soft periodic swells of filtered noise)
# ---------------------------------------------------------------------------
wind_noise = rng.standard_normal(N)
wind = bandpass(wind_noise, 200, 2200)
wind_drift = 0.65 + 0.35 * np.sin(2 * np.pi * 0.04 * t) + 0.15 * np.sin(2 * np.pi * 0.11 * t + 0.7)
wind = wind * wind_drift
wind = normalize(wind, 0.4)

wave_env = 0.5 + 0.5 * np.sin(2 * np.pi * 0.09 * t - np.pi / 2)
wave_env = wave_env ** 2  # sharpen swell shape
wave_noise = lowpass(rng.standard_normal(N), 900)
waves = wave_noise * wave_env
waves = normalize(waves, 0.5)

ambience = normalize(wind * 0.6 + waves * 0.7, 0.85)
ambience = fade(ambience)
ambience_stereo = np.stack([ambience, ambience * 0.96], axis=1)
wavfile.write(f"{OUT}/coastal_ambience.wav", SR, (ambience_stereo * 32767).astype(np.int16))
print("saved coastal_ambience.wav")

# ---------------------------------------------------------------------------
# Event layer: creaking wooden timbers (low groaning bandpass sweeps) +
# seagull calls (short modulated tone bursts)
# ---------------------------------------------------------------------------
event = np.zeros(N)

def make_creak(start_s, length_s, base_freq=180):
    n = int(length_s * SR)
    tt = np.arange(n) / SR
    sweep = base_freq * (1 + 0.15 * np.sin(2 * np.pi * 0.8 * tt))
    phase = 2 * np.pi * np.cumsum(sweep) / SR
    tone = np.sin(phase) + 0.3 * rng.standard_normal(n)
    tone = bandpass(tone, 80, 400)
    env = np.ones(n)
    a = int(0.15 * SR)
    r = int(0.4 * SR)
    env[:a] = np.linspace(0, 1, a)
    env[-r:] = np.linspace(1, 0, r)
    tone = tone * env
    start = int(start_s * SR)
    end = min(N, start + n)
    event[start:end] += tone[: end - start] * 0.45

make_creak(1.5, 1.8, 170)
make_creak(6.5, 2.2, 150)
make_creak(11.0, 1.6, 190)
make_creak(16.0, 2.0, 160)

def make_gull(start_s, length_s=0.5, base_freq=1800):
    n = int(length_s * SR)
    tt = np.arange(n) / SR
    freq = base_freq * (1 + 0.4 * np.sin(2 * np.pi * 3.5 * tt) * np.exp(-tt * 2))
    phase = 2 * np.pi * np.cumsum(freq) / SR
    tone = np.sin(phase)
    env = np.exp(-np.linspace(0, 5, n))
    tone = tone * env
    tone = bandpass(tone, 900, 4000)
    start = int(start_s * SR)
    end = min(N, start + n)
    event[start:end] += tone[: end - start] * 0.35

for gt in [3.0, 3.4, 8.2, 13.5, 13.9, 18.0]:
    make_gull(gt, base_freq=rng.uniform(1500, 2200))

event = normalize(event, 0.75)
event = fade(event, in_s=0.5, out_s=1.0)
event_stereo = np.stack([event, event * 0.97], axis=1)
wavfile.write(f"{OUT}/coastal_events.wav", SR, (event_stereo * 32767).astype(np.int16))
print("saved coastal_events.wav")
