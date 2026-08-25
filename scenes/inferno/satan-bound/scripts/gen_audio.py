#!/usr/bin/env python3
"""
Procedural audio for scenes/inferno/satan-bound.
Ambience bed: deep earth rumble + fire crackle (looped-feel, continuous).
Event layer: distant tormented groans + chain rattle (intermittent).
No licensing concerns: fully synthesized, not sourced.
"""
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
DUR = 20.0
N = int(SR * DUR)
OUT = "/Users/louisryan/Desktop/parallax/scenes/inferno/satan-bound/audio"

rng = np.random.default_rng(7)

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

# ---------------------------------------------------------------------------
# Ambience: deep earth rumble (low-passed noise with slow amplitude drift)
# ---------------------------------------------------------------------------
t = np.arange(N) / SR
rumble_noise = rng.standard_normal(N)
rumble = lowpass(rumble_noise, 90)
drift = 0.7 + 0.3 * np.sin(2 * np.pi * 0.05 * t) + 0.15 * np.sin(2 * np.pi * 0.13 * t + 1.3)
rumble = rumble * drift
# sub-bass tone for weight
sub = 0.15 * np.sin(2 * np.pi * 45 * t) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.07 * t))
rumble = rumble + sub
rumble = normalize(rumble, 0.6)

# ---------------------------------------------------------------------------
# Fire crackle: sparse short highpass noise bursts (pops) + a soft hiss bed
# ---------------------------------------------------------------------------
hiss = highpass(rng.standard_normal(N), 2500) * 0.04
crackle = np.zeros(N)
n_pops = 700
pop_positions = rng.integers(0, N - 400, n_pops)
for p in pop_positions:
    length = rng.integers(80, 400)
    amp = rng.uniform(0.15, 0.6)
    env = np.exp(-np.linspace(0, 8, length))
    pop_noise = highpass(rng.standard_normal(length), 1200) * amp * env
    end = min(N, p + length)
    crackle[p:end] += pop_noise[: end - p]
fire = normalize(hiss + crackle, 0.5)

ambience = normalize(rumble * 0.7 + fire * 0.6, 0.85)
ambience = fade(ambience)
ambience_stereo = np.stack([ambience, ambience * 0.97], axis=1)
wavfile.write(f"{OUT}/hell_ambience.wav", SR, (ambience_stereo * 32767).astype(np.int16))
print("saved hell_ambience.wav")

# ---------------------------------------------------------------------------
# Event layer: distant tormented groans (modulated low tones/formant-ish)
# plus a chain rattle at a couple of points
# ---------------------------------------------------------------------------
event = np.zeros(N)

def make_groan(start_s, length_s, base_freq, depth=0.02):
    n = int(length_s * SR)
    tt = np.arange(n) / SR
    vibrato = np.sin(2 * np.pi * 4.5 * tt) * depth
    freq = base_freq * (1 + vibrato)
    phase = 2 * np.pi * np.cumsum(freq) / SR
    tone = np.sin(phase) + 0.5 * np.sin(2 * phase) + 0.25 * np.sin(3 * phase)
    env = np.ones(n)
    a = int(0.3 * SR)
    r = int(0.6 * SR)
    env[:a] = np.linspace(0, 1, a)
    env[-r:] = np.linspace(1, 0, r)
    tone = tone * env
    tone = bandpass(tone, 100, 900)
    start = int(start_s * SR)
    end = min(N, start + n)
    event[start:end] += tone[: end - start] * 0.5

make_groan(2.5, 3.2, 95, 0.03)
make_groan(8.0, 4.0, 80, 0.02)
make_groan(14.5, 3.5, 105, 0.025)

def make_chain_rattle(start_s, n_links=6):
    for i in range(n_links):
        t0 = start_s + i * rng.uniform(0.08, 0.18)
        length = rng.integers(300, 900)
        amp = rng.uniform(0.3, 0.7)
        env = np.exp(-np.linspace(0, 6, length))
        metallic = bandpass(rng.standard_normal(length), 800, 4000) * amp * env
        start = int(t0 * SR)
        end = min(N, start + length)
        if start < N:
            event[start:end] += metallic[: end - start]

make_chain_rattle(5.5)
make_chain_rattle(12.0)
make_chain_rattle(17.5)

event = normalize(event, 0.8)
event = fade(event, in_s=0.5, out_s=1.0)
event_stereo = np.stack([event, event * 0.95], axis=1)
wavfile.write(f"{OUT}/hell_events.wav", SR, (event_stereo * 32767).astype(np.int16))
print("saved hell_events.wav")
