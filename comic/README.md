# comic/ — the motion-comic renderer

An [fframes](https://fframes.studio) project (Rust, CPU) that draws the film
from `film.json`: full-bleed comic panels with camera moves, insert cuts,
halftone screens, ink borders, pop-in speech balloons, starburst SFX, kinetic
narration captions and the end card. Deterministic: same inputs, same film.

`film.json` is written by `pipeline/comic.py` (`make comic`), which also copies
the panel images into `media/` and mixes/muxes the audio afterwards.

## Requirements

- Rust (rustup, stable). This box: `~/.cargo/bin/cargo`, rustc 1.100.
- **x264 build 163** at `/opt/x264-163` — the bundled libavcodec links
  `x264_encoder_open_163`, and distro x264 builds export different ABI
  versions. `.cargo/config.toml` points the linker there. To rebuild it:

  ```bash
  git clone https://github.com/mirror/x264.git && cd x264
  git checkout 5db6aa6           # X264_BUILD 163
  ./configure --prefix=/opt/x264-163 --enable-static --disable-shared \
              --disable-cli --disable-opencl --enable-pic
  make -j$(nproc) && sudo make install
  ```
- Fonts in `media/`: DM Sans, Bangers and Noto Sans Ethiopic (all SIL OFL),
  embedded at build time.

## Two layouts, one film

The same `film.json` is drawn two ways. The layout is a cargo feature, so the
frame size is a compile-time constant of the encoder:

| Layout | Build | Frame | What is on screen |
|---|---|---|---|
| 9:16 (default) | `cargo build --release` | 1080×1920 | full-bleed panel, balloons, SFX, word-by-word English caption |
| 16:9 | `cargo build --release --features wide` | 1920×1080 | the panel as a full-height strip in the centre; the spoken Amharic line in the left margin, the English subtitle in the right |

In the landscape page the *stage* (where the panel is drawn and where the
camera moves) is the strip, not the frame; the margins are painted after it,
so camera moves and SFX bursts never bleed into the text. A pan travels the
strip's overscan only.

`pipeline/comic.py` drives both (`render` and `render-wide`) and muxes each
with the same audio master.

## Commands

```bash
cd comic
cargo build --release
cargo run --release -- timeline           # shots, duration, audio
cargo run --release -- frame 12.5s        # one frame -> frames/
cargo run --release -- strip -n 12        # contact sheet of the motion
cargo run --release -- render --renderer cpu -o out.mp4
```

`--renderer cpu` is the tiny-skia CPU backend (no GPU here). Prefer
`-o` for the output path and `--draft`/`--scale 0.5` while iterating.

## Data contract (film.json)

```json
{
  "fps": 24, "width": 1080, "height": 1920, "duration": 84.0,
  "shots": [{
    "id": "s1_das", "start": 0.0, "dur": 6.7,
    "panels": [{"img": "panel_s1_das.png", "at": 0.0},
               {"img": "ins_s1_das_x1.jpg", "at": 0.45},
               {"img": "ins_s1_das.jpg", "at": 0.78}],
    "mv": "push_in",
    "balloon": {"text": "...", "start": 2.2, "end": 8.4, "top": 0.16},
    "sfx": [{"text": "DUM-TAK!", "t": 1.4, "x": 0.74, "y": 0.24}],
    "words": [{"t0": 0.35, "t1": 0.72, "w": "The"}],
    "am": "ከበሮ ይመታል፣ …"
  }],
  "end": {"start": 81.0, "dur": 3.0, "title": "...", "text": "...",
          "text_am": "…", "sub": "..."}
}
```

`words` are the English caption tokens with estimated timings (used for the
vertical kinetic caption and, joined, the landscape English margin); `am` is
the line as spoken, shown in the landscape Amharic margin.

Camera moves: `push_in`, `push_out`, `pan_l`, `pan_r`, `shake`. The renderer
is deterministic in its frames; the encoded MP4 is not bit-reproducible
because fframes encodes in parallel chunks whose seams depend on concurrency
(`../FAILURES.md` F17).
