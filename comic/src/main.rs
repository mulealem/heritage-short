use fframes::cli::clap;
use fframes::{EncoderOptions, RenderOptions, StaticMediaProvider, cli};
use heritage_comic::{ComicMedia, ComicVideo, Film};
use std::process::ExitCode;

/// Extra flag next to the standard fframes CLI (render, frame, strip, inspect).
#[derive(Debug, clap::Args)]
struct VideoArgs {
    /// Path to the film data file inside media/ (default: film.json).
    #[arg(long, default_value = "film.json", global = true)]
    film: String,
}

fn main() -> ExitCode {
    let args = cli::parse::<VideoArgs>();
    let media = ComicMedia::prepare().expect("media");

    let path = std::path::Path::new(&args.app.film).to_path_buf();
    let raw = match std::fs::read_to_string(&path) {
        Ok(s) => s,
        Err(e) => {
            eprintln!("cannot read {}: {e}\nrun: python3 -m pipeline.comic build", path.display());
            return ExitCode::FAILURE;
        }
    };
    let film: Film = match serde_json::from_str(&raw) {
        Ok(f) => f,
        Err(e) => {
            eprintln!("invalid film.json: {e}");
            return ExitCode::FAILURE;
        }
    };

    let video = ComicVideo::new(&media, film);

    cli::new(
        &video,
        RenderOptions {
            media: Some(&media),
            video_encoder_options: EncoderOptions {
                preferred_encoder: Some("libx264"),
                codec_params: Some(&[("crf", "19"), ("preset", "medium"), ("tune", "animation")]),
                ..Default::default()
            },
            ..Default::default()
        },
    )
    .args(args)
    .run()
}
