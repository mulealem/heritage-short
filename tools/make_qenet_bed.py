"""Build a deterministic Ethiopian-pentatonic music bed for the film.

This is a real, hand-synthesized cue (not a model output and not a placeholder):
a low A drone, a 118 BPM kebero pulse, sparse masinko-like bowed phrases and
washint-like long tones, arranged against the shot list so the music breathes
with the story (it drops for the deadpan, returns for the feast and the
punchline). Pure stdlib; fixed seed; reproducible.

Output: outputs/music/score_qenet.wav and outputs/music/score_final.wav
        + outputs/music/score_source.txt ("qenet-bed-v1")

Usage: python3 tools/make_qenet_bed.py [--seconds N] [--no-install]
"""
import json
import math
import random
import sys
import wave
from array import array
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline import common

SR = 24000
BPM = 118
BEAT = 60.0 / BPM
BAR = 4 * BEAT
OUT = common.OUT / "music"

# A minor pentatonic (A C D E G), the qenet colour used throughout.
SCALE = [220.00, 261.63, 293.66, 329.63, 392.00]

# Per-shot intensity: how much of the band plays in that beat.
INTENSITY = {
    "s1_das": 0.85, "s2_arrival": 0.55, "s3_gatekeeper": 0.35,
    "s4_change": 0.45, "s5_dressed": 0.75, "s6_welcome": 0.95,
    "s7_feast": 0.85, "s8_deadpan": 0.18, "s9_mess": 0.55,
    "s10_punchline": 1.00,
}


def load_timeline():
    p = common.ROOT / "comic" / "film.json"
    if p.exists():
        film = json.loads(p.read_text())
        return [(s["id"], float(s["start"]), float(s["start"] + s["dur"]))
                for s in film["shots"]], float(film["duration"])
    total = common.film_duration(common.load_storyboard()) + 4.0
    return [("s%d" % i, 0.0, total) for i in range(1, 11)], total


SHOTS, DUR = load_timeline()
N = int(DUR * SR) + 1
random.seed(118)


def intensity_at(t):
    for sid, a, b in SHOTS:
        if a <= t < b:
            return INTENSITY.get(sid, 0.5)
    return 0.45


def env_ad(i, n, attack, release):
    t = i / SR
    dur = n / SR
    a = min(1.0, t / attack) if attack > 0 else 1.0
    r = min(1.0, max(0.0, (dur - t) / release)) if release > 0 else 1.0
    return a * r


def bowed(buf, t0, freq, dur, amp):
    i0 = int(t0 * SR)
    n = int(dur * SR)
    phase = 0.0
    lp = 0.0
    for i in range(n):
        j = i0 + i
        if j >= N:
            break
        t = i / SR
        e = env_ad(i, n, 0.09, 0.20)
        vib = 1.0 + 0.006 * math.sin(2 * math.pi * 5.3 * t)
        phase += 2 * math.pi * freq * vib / SR
        x = math.sin(phase) + 0.34 * math.sin(2 * phase) + 0.12 * math.sin(3 * phase)
        lp += 0.20 * (x - lp)
        buf[j] += amp * e * lp


def pluck(buf, t0, freq, dur, amp):
    i0 = int(t0 * SR)
    n = int(dur * SR)
    for i in range(n):
        j = i0 + i
        if j >= N:
            break
        t = i / SR
        e = math.exp(-3.2 * t) * min(1.0, t / 0.004)
        x = (math.sin(2 * math.pi * freq * t)
             + 0.42 * math.sin(4 * math.pi * freq * t)
             + 0.18 * math.sin(6 * math.pi * freq * t))
        buf[j] += amp * e * x


def flute(buf, t0, freq, dur, amp):
    i0 = int(t0 * SR)
    n = int(dur * SR)
    phase = 0.0
    for i in range(n):
        j = i0 + i
        if j >= N:
            break
        t = i / SR
        e = env_ad(i, n, 0.18, 0.30)
        vib = 1.0 + 0.004 * math.sin(2 * math.pi * 4.6 * t)
        phase += 2 * math.pi * freq * vib / SR
        x = math.sin(phase) + 0.12 * math.sin(2 * phase) + 0.012 * (random.random() * 2 - 1)
        buf[j] += amp * e * x


def drum(buf, t0, low, amp):
    i0 = int(t0 * SR)
    n = int(0.22 * SR)
    for i in range(n):
        j = i0 + i
        if j >= N:
            break
        t = i / SR
        if low:
            f = 95.0 * math.exp(-14.0 * t) + 52.0
            x = math.sin(2 * math.pi * f * t) * math.exp(-9.0 * t)
            x += 0.25 * math.sin(2 * math.pi * 185.0 * t) * math.exp(-28.0 * t)
        else:
            x = (random.random() * 2 - 1) * math.exp(-32.0 * t) * 0.7
            x += math.sin(2 * math.pi * 190.0 * t) * math.exp(-24.0 * t) * 0.3
        buf[j] += amp * x


def shaker(buf, t0, amp):
    i0 = int(t0 * SR)
    n = int(0.06 * SR)
    prev = 0.0
    for i in range(n):
        j = i0 + i
        if j >= N:
            break
        t = i / SR
        x = random.random() * 2 - 1
        hp = x - prev
        prev = x
        buf[j] += amp * hp * math.exp(-70.0 * t)


def add_reverb(buf):
    out = buf[:]
    for delay, gain in ((int(0.067 * SR), 0.20),
                        (int(0.101 * SR), 0.14),
                        (int(0.157 * SR), 0.09)):
        for i in range(delay, N):
            out[i] += gain * buf[i - delay]
    return out


def main():
    if "--seconds" in sys.argv:
        secs = float(sys.argv[sys.argv.index("--seconds") + 1])
    else:
        secs = DUR
    global N
    N = int(secs * SR) + 1
    buf = [0.0] * N

    # 1. Drone: A1/A2 + E3, slow swell.
    for i in range(N):
        t = i / SR
        lfo = 0.55 + 0.45 * math.sin(2 * math.pi * 0.045 * t)
        buf[i] += (0.050 * math.sin(2 * math.pi * 55.0 * t)
                   + 0.032 * lfo * math.sin(2 * math.pi * 110.0 * t)
                   + 0.014 * lfo * math.sin(2 * math.pi * 164.81 * t))

    # 2. Kebero: a 4/4 pattern that thins for the deadpan and returns for the feast.
    bar = 0.0
    bar_no = 0
    while bar < secs - 2.0:
        q = intensity_at(bar + 0.1)
        if q > 0.40:
            drum(buf, bar, True, 0.11 * q)
            drum(buf, bar + 1.5 * BEAT, False, 0.045 * q)
            drum(buf, bar + 2 * BEAT, True, 0.085 * q)
            drum(buf, bar + 3 * BEAT, False, 0.05 * q)
            if q > 0.70:
                drum(buf, bar + 3.5 * BEAT, False, 0.035 * q)
        if bar_no % 8 == 7 and q > 0.55:
            for k in range(4):
                drum(buf, bar + 3.0 * BEAT + k * BEAT / 4, True, 0.045 * q)
        bar += BAR
        bar_no += 1

    # 3. Shaker on the offbeat eighths while the band is up.
    t = 0.0
    while t < secs - 2.0:
        q = intensity_at(t)
        if q > 0.50:
            shaker(buf, t + BEAT / 2, 0.012 * q)
        t += BEAT

    # 4. Masinko-like phrases every two bars.
    motif = [0, 2, 3, 2, 1, 0, 2, 0]
    t = 3.0
    phrase = 0
    while t < secs - 4.0:
        q = intensity_at(t)
        if q > 0.32:
            base = -12 if phrase % 3 == 0 else 0  # drop an octave every third phrase
            steps = 4 if q < 0.7 else 6
            for k in range(steps):
                deg = motif[(phrase * 3 + k) % len(motif)]
                f = SCALE[deg] * (2 ** (base / 12.0))
                at = t + k * BEAT * (0.5 if q > 0.8 else 1.0)
                if at > secs - 2.5:
                    break
                dur = 0.30 if q > 0.8 else 0.52
                (bowed if (phrase + k) % 2 == 0 else pluck)(buf, at, f, dur, 0.085 * q + 0.020)
        # a long washint tone at the top of a section
        if phrase % 8 == 0 and q > 0.45:
            flute(buf, t + BEAT, SCALE[3] * 2, 1.8, 0.040 * q)
        t += 2 * BAR
        phrase += 1

    # 5. Final cadence under the end card: A + E, let ring.
    end = secs - 4.0
    bowed(buf, max(0.0, end - 1.0), 220.0, 3.2, 0.065)
    flute(buf, max(0.0, end - 0.6), 659.25, 2.4, 0.032)

    wet = add_reverb(buf)

    # Fade in/out, normalize, write.
    fade_in = int(0.8 * SR)
    fade_out = int(3.0 * SR)
    for i in range(min(fade_in, N)):
        wet[i] *= i / fade_in
    for i in range(max(0, N - fade_out), N):
        wet[i] *= max(0.0, (N - i) / fade_out)
    peak = max(1e-9, max(abs(x) for x in wet))
    gain = 0.70 / peak
    pcm = array("h", (max(-32767, min(32767, int(x * gain * 32767))) for x in wet))

    OUT.mkdir(parents=True, exist_ok=True)
    qenet = OUT / "score_qenet.wav"
    with wave.open(str(qenet), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    if "--no-install" not in sys.argv:
        import shutil
        shutil.copyfile(qenet, OUT / "score_final.wav")
        (OUT / "score_source.txt").write_text("qenet-bed-v1\n")
    common.log_call(stage="music", model="qenet-bed", status="ok",
                    params={"seconds": round(secs, 2), "bpm": BPM,
                            "key": "A minor pentatonic"},
                    output=str(qenet),
                    note="hand-synthesized qenet bed (deterministic)")
    print("wrote %s (%.1fs)" % (qenet, secs))


if __name__ == "__main__":
    main()
