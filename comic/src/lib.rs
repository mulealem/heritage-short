//! "Eat, My Clothes, Eat!" — motion-comic renderer.
//!
//! A data-driven fframes scene: `media/film.json` (written by pipeline/comic.py
//! from the storyboard + measured narration) carries every shot's timing, panel
//! image, insert panel, camera move, speech balloon, sound effect and the
//! word timings for the kinetic captions. This file only draws.
//!
//! Comic language: full-bleed panels with a slow camera move, an insert panel
//! cut at a spring, halftone dot screen, ink border, pop-in speech balloons in
//! Bangers, starburst SFX, progressive word captions, white cut flashes.
use fframes::{
    AudioMap, Color, Duration, FFramesContext, Frame, Svgr, Transform, Video, include_media_dir,
};
use serde::Deserialize;

include_media_dir!(pub struct ComicMedia, "media");

pub const FPS: usize = 24;

// Two layouts of one film. `wide` (cargo feature) is the 16:9 comic page:
// the same cuts and the same panel strip, full height and centred, with the
// spoken line and its English subtitle in the margins. Default is 9:16.
#[cfg(feature = "wide")]
pub const WIDTH: usize = 1920;
#[cfg(not(feature = "wide"))]
pub const WIDTH: usize = 1080;
#[cfg(feature = "wide")]
pub const HEIGHT: usize = 1080;
#[cfg(not(feature = "wide"))]
pub const HEIGHT: usize = 1920;
pub const WIDE: bool = cfg!(feature = "wide");

const INK: &str = "#14100c";
const PAPER: &str = "#f7eeda";
const GOLD: &str = "#f5b21c";
const RED: &str = "#d6332c";
const TEAL: &str = "#0f3b43";
const FONT_POP: &str = "Bangers";
const FONT_BODY: &str = "DM Sans";
const FONT_ET: &str = "Noto Sans Ethiopic";
const BODY_WEIGHT: u16 = 500;
const POP_WEIGHT: u16 = 400;

#[derive(Deserialize, Debug, Clone)]
pub struct Word {
    pub t0: f32,
    pub t1: f32,
    pub w: String,
}

#[derive(Deserialize, Debug, Clone)]
pub struct Balloon {
    pub text: String,
    pub start: f32,
    pub end: f32,
    #[serde(default = "half")]
    pub top: f32,
}

fn half() -> f32 {
    0.16
}

#[derive(Deserialize, Debug, Clone)]
pub struct Sfx {
    pub text: String,
    pub t: f32,
    #[serde(default = "sfx_x")]
    pub x: f32,
    #[serde(default = "sfx_y")]
    pub y: f32,
}

fn sfx_x() -> f32 {
    0.7
}
fn sfx_y() -> f32 {
    0.25
}

/// Older scene files carried one SFX object per shot; the current data carries
/// a list (a beat can pop "SQUELCH!" and "POUR!"). Accept both.
#[derive(Deserialize, Debug, Clone)]
#[serde(untagged)]
pub enum SfxSpec {
    One(Sfx),
    Many(Vec<Sfx>),
}

impl SfxSpec {
    fn items(&self) -> Vec<&Sfx> {
        match self {
            SfxSpec::One(s) => vec![s],
            SfxSpec::Many(v) => v.iter().collect(),
        }
    }
}

#[derive(Deserialize, Debug, Clone)]
pub struct PanelCut {
    /// image file inside media/
    pub img: String,
    /// fraction of the shot at which this panel starts (0.0 for the first)
    pub at: f32,
}

#[derive(Deserialize, Debug, Clone)]
pub struct Shot {
    pub id: String,
    pub start: f32,
    pub dur: f32,
    /// ordered cuts; when empty, `panel`/`insert` are used (old data files)
    #[serde(default)]
    pub panels: Vec<PanelCut>,
    #[serde(default)]
    pub panel: String,
    #[serde(default)]
    pub insert: Option<String>,
    #[serde(default = "insert_at")]
    pub insert_at: f32,
    #[serde(default = "move_default")]
    pub mv: String,
    #[serde(default)]
    pub balloon: Option<Balloon>,
    #[serde(default)]
    pub sfx: Option<SfxSpec>,
    #[serde(default)]
    pub words: Vec<Word>,
    /// the line as spoken, when the narration is not English (landscape margin)
    #[serde(default)]
    pub am: String,
}

fn insert_at() -> f32 {
    0.55
}
fn move_default() -> String {
    "push_in".to_string()
}

#[derive(Deserialize, Debug, Clone)]
pub struct EndCard {
    pub start: f32,
    pub dur: f32,
    pub title: String,
    pub text: String,
    #[serde(default)]
    pub text_am: String,
    pub sub: String,
}

#[derive(Deserialize, Debug, Clone)]
pub struct Film {
    pub duration: f32,
    pub shots: Vec<Shot>,
    pub end: EndCard,
}

pub struct ComicVideo<'a> {
    pub media: &'a ComicMedia,
    pub film: Film,
}

impl std::fmt::Debug for ComicVideo<'_> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("ComicVideo").field("shots", &self.film.shots.len()).finish()
    }
}

// --- small math helpers -----------------------------------------------------

fn clamp01(x: f32) -> f32 {
    x.clamp(0.0, 1.0)
}

fn ease_out(x: f32) -> f32 {
    1.0 - (1.0 - x).powi(3)
}

fn ease_in_out(x: f32) -> f32 {
    let x = clamp01(x);
    if x < 0.5 { 4.0 * x * x * x } else { 1.0 - (-2.0 * x + 2.0).powi(3) / 2.0 }
}

fn back_out(x: f32) -> f32 {
    let x = clamp01(x);
    let c = 1.70158;
    1.0 + (c + 1.0) * (x - 1.0).powi(3) + c * (x - 1.0).powi(2)
}

// --- drawing helpers --------------------------------------------------------

fn fit_size(text: &str, want: usize, max_w: f32, factor: f32) -> usize {
    let chars = text.chars().count().max(1) as f32;
    let by_width = (max_w / (chars * factor)).floor() as usize;
    by_width.clamp(16, want)
}

fn wrap_two(text: &str) -> (String, String) {
    let words: Vec<&str> = text.split_whitespace().collect();
    if words.len() < 3 {
        return (text.to_string(), String::new());
    }
    let total: usize = words.iter().map(|w| w.len() + 1).sum();
    let mut a = String::new();
    let mut n = 0;
    for (i, w) in words.iter().enumerate() {
        n += w.len() + 1;
        a.push_str(w);
        a.push(' ');
        if n as f32 >= total as f32 * 0.5 && i + 1 < words.len() {
            return (a.trim().to_string(), words[i + 1..].join(" "));
        }
    }
    (a.trim().to_string(), String::new())
}

/// Greedy word wrap by estimated character width (no font metrics needed).
fn wrap_by_chars(text: &str, max_chars: usize) -> Vec<String> {
    let mut lines: Vec<String> = Vec::new();
    let mut cur = String::new();
    for word in text.split_whitespace() {
        if !cur.is_empty() && cur.chars().count() + 1 + word.chars().count() > max_chars {
            lines.push(std::mem::take(&mut cur));
        }
        if !cur.is_empty() {
            cur.push(' ');
        }
        cur.push_str(word);
    }
    if !cur.is_empty() {
        lines.push(cur);
    }
    lines
}

/// Largest of `sizes` whose wrapped block fits `max_w` by `max_h`.
fn fit_block(text: &str, sizes: &[usize], max_w: f32, factor: f32, line_h: f32,
             max_h: f32) -> (usize, Vec<String>) {
    for &fs in sizes {
        let per_line = ((max_w / (fs as f32 * factor)).floor() as usize).max(8);
        let lines = wrap_by_chars(text, per_line);
        if lines.len() as f32 * fs as f32 * line_h <= max_h {
            return (fs, lines);
        }
    }
    let fs = *sizes.last().unwrap_or(&16);
    let per_line = ((max_w / (fs as f32 * factor)).floor() as usize).max(8);
    (fs, wrap_by_chars(text, per_line))
}

fn star_path(cx: f32, cy: f32, outer: f32, inner: f32, points: usize) -> String {
    let mut d = String::new();
    for i in 0..(points * 2) {
        let r = if i % 2 == 0 { outer } else { inner };
        let ang = std::f32::consts::PI * (i as f32) / (points as f32) - std::f32::consts::FRAC_PI_2;
        let x = cx + r * ang.cos();
        let y = cy + r * ang.sin();
        d.push_str(&format!("{}{:.1} {:.1} ", if i == 0 { "M" } else { "L" }, x, y));
    }
    d.push('Z');
    d
}

fn speed_lines_path(cx: f32, cy: f32, r0: f32, r1: f32, n: usize) -> String {
    let mut d = String::new();
    for i in 0..n {
        let ang = std::f32::consts::PI * 2.0 * (i as f32) / (n as f32);
        let (s, c) = ang.sin_cos();
        d.push_str(&format!("M{:.1} {:.1} L{:.1} {:.1} ",
                            cx + r0 * c, cy + r0 * s, cx + r1 * c, cy + r1 * s));
    }
    d
}

impl<'a> ComicVideo<'a> {
    pub fn new(media: &'a ComicMedia, film: Film) -> Self {
        Self { media, film }
    }

    fn end_card(&'a self, t: f32) -> Svgr<'a> {
        let e = &self.film.end;
        let u = clamp01((t - e.start) / e.dur.max(0.01));
        let fade = if u < 0.12 { u / 0.12 } else if u > 0.85 { (1.0 - u) / 0.15 } else { 1.0 };
        let rise = (1.0 - ease_out(clamp01(u / 0.25))) * 60.0;
        let (w, h) = (WIDTH as f32, HEIGHT as f32);
        let title_size = fit_size(&e.title, 118, w * 0.84, 0.50);
        let prov_am_size = fit_size(&e.text_am, 52, w * 0.88, 0.46);
        let prov_size = fit_size(&e.text, 40, w * 0.88, 0.52);
        let sub_size = fit_size(&e.sub, 30, w * 0.86, 0.52);
        fframes::svgr!(
            <svg xmlns="http://www.w3.org/2000/svg" viewBox={format!("0 0 {WIDTH} {HEIGHT}")} width={WIDTH} height={HEIGHT}>
                <defs>
                    <pattern id="dots-end" x="0" y="0" width="18" height="18" patternUnits="userSpaceOnUse">
                        <circle cx="9" cy="9" r="2.6" fill={GOLD} opacity="0.20" />
                    </pattern>
                </defs>
                <rect width={WIDTH} height={HEIGHT} fill={TEAL} />
                <rect width={WIDTH} height={HEIGHT} fill="url(#dots-end)" opacity={0.8 * fade} />
                <circle cx={w * 0.5} cy={h * 0.34} r={330.0} fill={GOLD} opacity={0.10 * fade} />

                <g opacity={fade} transform={Transform::translate(0.0, rise)}>
                    <text x={w / 2.0 + 5.0} y={h * 0.315 + 5.0} font-family={FONT_POP} font-size={title_size} font-weight={POP_WEIGHT} fill={INK} text-anchor="middle">
                        {e.title.as_str()}
                    </text>
                    <text x={w / 2.0} y={h * 0.315} font-family={FONT_POP} font-size={title_size} font-weight={POP_WEIGHT} fill={GOLD} text-anchor="middle">
                        {e.title.as_str()}
                    </text>
                    <rect x={w * 0.18} y={h * 0.375} width={w * 0.64} height={6.0} fill={RED} />
                    <text x={w / 2.0} y={h * 0.485} font-family={FONT_ET} font-size={prov_am_size} font-weight={BODY_WEIGHT} fill={PAPER} text-anchor="middle">
                        {e.text_am.as_str()}
                    </text>
                    <text x={w / 2.0} y={h * 0.55} font-family={FONT_BODY} font-size={prov_size} font-weight={BODY_WEIGHT} fill={PAPER} opacity="0.9" text-anchor="middle">
                        {e.text.as_str()}
                    </text>
                    <text x={w / 2.0} y={h * 0.94} font-family={FONT_BODY} font-size={sub_size} font-weight={BODY_WEIGHT} fill={PAPER} opacity="0.62" text-anchor="middle">
                        {e.sub.as_str()}
                    </text>
                </g>
            </svg>
        )
    }
}

impl Video for ComicVideo<'_> {
    const FPS: usize = FPS;
    const WIDTH: usize = WIDTH;
    const HEIGHT: usize = HEIGHT;
    const BACKGROUND_COLOR: Color = Color::BLACK;

    fn duration(&self) -> Duration<'_> {
        Duration::Seconds(self.film.duration)
    }

    fn audio(&self) -> AudioMap<'_> {
        // Narration + score are mixed by pipeline/comic.py (ducking, loudnorm)
        // and muxed after the picture render, reusing the assemble.py master.
        AudioMap::none()
    }

    fn render_frame<'a>(&'a self, mut frame: Frame, ctx: &FFramesContext<'a, '_>) -> Svgr<'a> {
        let t = frame.index as f32 / FPS as f32;
        let film = &self.film;
        if t >= film.end.start {
            return self.end_card(t);
        }
        let (idx, shot) = match film.shots
            .iter()
            .enumerate()
            .find(|(_, s)| t >= s.start && t < s.start + s.dur)
        {
            Some((i, s)) => (i, s),
            None => return self.end_card(t),
        };
        let (pw, ph) = (WIDTH as f32, HEIGHT as f32);
        // The stage is where the panel lives: the whole frame in 9:16. In the
        // landscape page it is the vertical strip at full height, centred, and
        // the margins carry the spoken line and its English subtitle.
        let (w, h) = if WIDE { ((ph * 9.0 / 16.0).round(), ph) } else { (pw, ph) };
        let (ox, _oy) = ((pw - w) / 2.0, (ph - h) / 2.0);
        let u = clamp01((t - shot.start) / shot.dur);

        // Panel selection: any number of cuts per shot (0.0..1.0 fractions).
        let (panel, boundary, lu) = if !shot.panels.is_empty() {
            let mut idx = 0usize;
            for (i, p) in shot.panels.iter().enumerate() {
                if u >= p.at {
                    idx = i;
                }
            }
            let start = shot.panels[idx].at;
            (shot.panels[idx].img.as_str(), start, clamp01(u))
        } else {
            let use_insert = shot.insert.is_some() && u >= shot.insert_at;
            if use_insert {
                (shot.insert.as_deref().unwrap(), shot.insert_at, clamp01(u))
            } else {
                (shot.panel.as_str(), 0.0, clamp01(u))
            }
        };

        // Camera: continuous across the whole shot (ignores panel cuts).
        // A pan travels the overscan and no further, so the frame edge never
        // shows (the strip is narrower than the vertical frame).
        let pan_amp = if WIDE { w * (1.14 - 1.0) / 2.0 * 0.93 } else { 70.0 };
        let (scale, pan_x, pan_y) = match shot.mv.as_str() {
            "push_out" => (1.16 - 0.10 * ease_in_out(lu), 0.0, 0.0),
            "pan_r" => (1.14, -pan_amp + 2.0 * pan_amp * ease_in_out(lu), 0.0),
            "pan_l" => (1.14, pan_amp - 2.0 * pan_amp * ease_in_out(lu), 0.0),
            "shake" => (1.12 + 0.012 * (t * 34.0).sin(),
                        7.0 * (t * 47.0).sin(), 5.0 * (t * 39.0).cos()),
            _ => (1.05 + 0.10 * ease_in_out(lu), 0.0, 0.0),
        };
        let img_w = w * scale;
        let img_h = h * scale;
        let img_x = (w - img_w) / 2.0 + pan_x;
        let img_y = (h - img_h) / 2.0 + pan_y;

        // Cut flash: at the shot boundary and at every panel cut.
        let since_cut = (u - boundary) * shot.dur;
        let flash = if since_cut < 0.14 {
            (1.0 - since_cut / 0.14).clamp(0.0, 1.0) * 0.85
        } else {
            0.0
        };

        // Halftone screen drifts with the camera.
        let hx = -((t * 9.0) % 16.0);
        let hy = -((t * 5.0) % 16.0);

        // Balloon.
        let mut balloon_nodes = Vec::new();
        if let Some(b) = &shot.balloon {
            let tb = t - shot.start - b.start;
            let span = b.end - b.start;
            if tb >= 0.0 && tb <= span {
                let pop = back_out(clamp01(tb / 0.42));
                let out = if tb > span - 0.25 { clamp01((span - tb) / 0.25) } else { 1.0 };
                let (l1, l2) = wrap_two(&b.text);
                let box_w = w * 0.84;
                let max_text_w = box_w - 70.0;
                let s1 = fit_size(&l1, 62, max_text_w, 0.47);
                let s2 = if l2.is_empty() { s1 } else { fit_size(&l2, 62, max_text_w, 0.47).min(s1) };
                let fs = s1.min(s2);
                let line_h = fs as f32 * 1.02;
                let lines = if l2.is_empty() { 1.0 } else { 2.0 };
                let box_h = line_h * lines + 56.0;
                let bx = (w - box_w) / 2.0;
                let by = h * b.top;
                let cx = w / 2.0;
                let tail_y0 = by + box_h;
                let tail = format!(
                    "M{:.1} {:.1} L{:.1} {:.1} L{:.1} {:.1} Z",
                    cx - 46.0, tail_y0 - 4.0, cx + 30.0, tail_y0 - 4.0,
                    cx - 8.0, tail_y0 + 64.0);
                let ty1 = by + 30.0 + fs as f32 * 0.82;
                let ty2 = ty1 + line_h;
                balloon_nodes = vec![
                    fframes::svgr!(
                        <rect x={bx} y={by} width={box_w * pop} height={box_h * pop} rx={26.0 * pop} fill={PAPER} stroke={INK} stroke-width={9.0 * pop} opacity={out} />
                    ),
                    fframes::svgr!(
                        <path d={tail} fill={PAPER} stroke={INK} stroke-width={8.0 * pop} opacity={out * pop} />
                    ),
                    fframes::svgr!(
                        <text x={cx} y={ty1} font-family={FONT_POP} font-size={fs} font-weight={POP_WEIGHT} fill={INK} text-anchor="middle" opacity={out * clamp01((pop - 0.2) / 0.5)}>
                            {l1.clone()}
                        </text>
                    ),
                    fframes::svgr!(
                        <text x={cx} y={ty2} font-family={FONT_POP} font-size={fs} font-weight={POP_WEIGHT} fill={INK} text-anchor="middle" opacity={out * clamp01((pop - 0.2) / 0.5)}>
                            {l2.clone()}
                        </text>
                    ),
                ];
            }
        }

        // SFX starbursts (a beat may have several: SQUELCH! + POUR!).
        let mut sfx_nodes = Vec::new();
        for s in shot.sfx.as_ref().map(|x| x.items()).unwrap_or_default() {
            let ts = t - shot.start - s.t;
            if ts >= 0.0 && ts < 1.1 {
                let pop = back_out(clamp01(ts / 0.35));
                let fade = if ts > 0.8 { ((1.1 - ts) / 0.3).clamp(0.0, 1.0) } else { 1.0 };
                let cx = w * s.x;
                let cy = h * s.y;
                let r = 168.0 * pop;
                let burst = star_path(cx, cy, r, r * 0.62, 12);
                let rays = speed_lines_path(cx, cy, r * 1.12, r * 1.75, 18);
                let fs = (72.0 * pop).max(10.0) as usize;
                sfx_nodes.extend(vec![
                    fframes::svgr!(
                        <path d={rays} stroke={INK} stroke-width="7" opacity={0.55 * fade * pop} />
                    ),
                    fframes::svgr!(
                        <path d={burst} fill={GOLD} stroke={INK} stroke-width="9" opacity={fade} />
                    ),
                    fframes::svgr!(
                        <text x={cx + 3.0} y={cy + 22.0} font-family={FONT_POP} font-size={fs} font-weight={POP_WEIGHT} fill={INK} text-anchor="middle" opacity={fade}>
                            {s.text.as_str()}
                        </text>
                    ),
                    fframes::svgr!(
                        <text x={cx} y={cy + 19.0} font-family={FONT_POP} font-size={fs} font-weight={POP_WEIGHT} fill={PAPER} text-anchor="middle" opacity={fade}>
                            {s.text.as_str()}
                        </text>
                    ),
                ]);
            }
        }

        // Kinetic caption: the narration so far, last seven words.
        let mut caption_nodes = Vec::new();
        let visible: Vec<&Word> = shot.words.iter().filter(|wd| wd.t0 <= t).collect();
        if !WIDE && !visible.is_empty() {
            let start = visible.len().saturating_sub(7);
            let chunk: Vec<&str> = visible[start..].iter().map(|wd| wd.w.as_str()).collect();
            let text = chunk.join(" ");
            let box_w = w - 96.0;
            let fs = fit_size(&text, 42, box_w - 56.0, 0.52);
            let bx = 48.0;
            let by = h - 232.0;
            let bh = fs as f32 * 1.5 + 26.0;
            caption_nodes = vec![
                fframes::svgr!(
                    <rect x={bx} y={by} width={box_w} height={bh} rx={14.0} fill={INK} opacity="0.72" />
                ),
                fframes::svgr!(
                    <text x={w / 2.0} y={by + bh / 2.0 + fs as f32 * 0.34} font-family={FONT_BODY} font-size={fs} font-weight={BODY_WEIGHT} fill={PAPER} text-anchor="middle">
                        {text.clone()}
                    </text>
                ),
            ];
        }


        if WIDE {
            // Landscape comic page: panel strip at full height in the centre,
            // the spoken line on the left, its English subtitle on the right.
            // The margins are painted after the stage, so nothing bleeds out
            // of the strip (camera moves, SFX bursts).
            let gutter = ox.max(1.0);
            let pad = 64.0;
            let text_w = gutter - pad * 2.0;
            let top = 250.0;
            let bottom = ph - 170.0;
            let en: String = shot.words.iter().map(|wd| wd.w.as_str()).collect::<Vec<_>>().join(" ");
            let sides: [(f32, &str, String, &str, f32, [usize; 5]); 2] = [
                (gutter / 2.0, "AMHARIC", shot.am.clone(), FONT_ET, 0.82, [48, 44, 40, 36, 32]),
                (pw - gutter / 2.0, "ENGLISH", en, FONT_BODY, 0.52, [46, 42, 38, 34, 30]),
            ];
            let mut margins: Vec<Svgr> = Vec::new();
            for (cx, label, text, font, factor, sizes) in sides.iter() {
                let x0 = if *cx < pw / 2.0 { 0.0 } else { pw - gutter };
                margins.push(fframes::svgr!(
                    <rect x={x0} y="0" width={gutter} height={ph} fill={TEAL} />
                ));
                margins.push(fframes::svgr!(
                    <rect x={x0} y="0" width={gutter} height={ph} fill="url(#dots-page)" />
                ));
                margins.push(fframes::svgr!(
                    <rect x={cx - 40.0} y={top - 96.0} width="80" height="5" fill={GOLD} />
                ));
                margins.push(fframes::svgr!(
                    <text x={*cx} y={top - 46.0} font-family={FONT_POP} font-size="30" font-weight={POP_WEIGHT} fill={GOLD} text-anchor="middle">
                        {*label}
                    </text>
                ));
                let (fs, lines) = fit_block(text, sizes, text_w, *factor, 1.32, bottom - top);
                let lh = fs as f32 * 1.32;
                let y0 = top + ((bottom - top) - lines.len() as f32 * lh) / 2.0 + fs as f32;
                for (i, line) in lines.iter().enumerate() {
                    margins.push(fframes::svgr!(
                        <text x={*cx} y={y0 + i as f32 * lh} font-family={*font} font-size={fs} font-weight={BODY_WEIGHT} fill={PAPER} text-anchor="middle">
                            {line.clone()}
                        </text>
                    ));
                }
            }
            let counter = format!("{:02} / {:02}", idx + 1, film.shots.len());
            margins.push(fframes::svgr!(
                <text x={gutter / 2.0} y={ph - 64.0} font-family={FONT_POP} font-size="44" font-weight={POP_WEIGHT} fill={GOLD} text-anchor="middle">
                    {counter.clone()}
                </text>
            ));
            margins.push(fframes::svgr!(
                <text x={pw - gutter / 2.0} y={ph - 62.0} font-family={FONT_POP} font-size="34" font-weight={POP_WEIGHT} fill={PAPER} opacity="0.72" text-anchor="middle">
                    {film.end.title.as_str()}
                </text>
            ));
            return fframes::svgr!(
                <svg xmlns="http://www.w3.org/2000/svg" viewBox={format!("0 0 {WIDTH} {HEIGHT}")} width={WIDTH} height={HEIGHT}>
                    <defs>
                        <pattern id="dots" x={hx} y={hy} width="16" height="16" patternUnits="userSpaceOnUse">
                            <circle cx="8" cy="8" r="2.35" fill={INK} opacity="0.45" />
                        </pattern>
                        <pattern id="dots-page" x="0" y="0" width="18" height="18" patternUnits="userSpaceOnUse">
                            <circle cx="9" cy="9" r="2.4" fill={GOLD} opacity="0.16" />
                        </pattern>
                    </defs>
                    <rect width={WIDTH} height={HEIGHT} fill={TEAL} />
                    <g transform={Transform::translate(ox, 0.0)}>
                        <rect width={w} height={h} fill={INK} />
                        <image x={img_x} y={img_y} width={img_w} height={img_h} href={ctx.get_image(panel).expect("panel image missing from media").href()} />
                        <rect width={w} height={h} fill="url(#dots)" opacity="0.30" />
                        <rect x="16" y="16" width={w - 32.0} height={h - 32.0} fill="none" stroke={INK} stroke-width="14" />
                        <rect x="26" y="26" width={w - 52.0} height={h - 52.0} fill="none" stroke={GOLD} stroke-width="2" opacity="0.6" />
                        {balloon_nodes}
                        {sfx_nodes}
                        <rect width={w} height={h} fill="#ffffff" opacity={flash} />
                    </g>
                    {margins}
                </svg>
            );
        }

        fframes::svgr!(
            <svg xmlns="http://www.w3.org/2000/svg" viewBox={format!("0 0 {WIDTH} {HEIGHT}")} width={WIDTH} height={HEIGHT}>
                <defs>
                    <pattern id="dots" x={hx} y={hy} width="16" height="16" patternUnits="userSpaceOnUse">
                        <circle cx="8" cy="8" r="2.35" fill={INK} opacity="0.45" />
                    </pattern>
                </defs>

                <rect width={WIDTH} height={HEIGHT} fill={INK} />
                <image x={img_x} y={img_y} width={img_w} height={img_h} href={ctx.get_image(panel).expect("panel image missing from media").href()} />

                <rect width={WIDTH} height={HEIGHT} fill="url(#dots)" opacity="0.30" />

                <rect x="16" y="16" width={w - 32.0} height={h - 32.0} fill="none" stroke={INK} stroke-width="14" />
                <rect x="26" y="26" width={w - 52.0} height={h - 52.0} fill="none" stroke={GOLD} stroke-width="2" opacity="0.6" />

                {balloon_nodes}
                {sfx_nodes}
                {caption_nodes}

                <rect width={WIDTH} height={HEIGHT} fill="#ffffff" opacity={flash} />
            </svg>
        )
    }
}
