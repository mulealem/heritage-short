"""Shared prompt composition: style block + subject prompt + identity directive.

The directive is what keeps a referenced character on-model (face, beard and
headwear) when a cast portrait is attached. Each character gets its own
directive: the turban belongs to Aleqa Gebre Hanna only, and the gatekeeper is
explicitly bare-headed. It lives here so the pipeline stages, the editor and
the prompt-export stay byte-identical.
"""

# Directive A — Aleqa Gebre Hanna (cream turban with a gold band)
DIRECTIVE_GEBRE_HANNA = (
    " Redraw the referenced person as a flat-colour comic-book illustration: "
    "bold black ink contours, flat saturated colour, halftone dot shading, "
    "no photorealism. Apply the referenced face ONLY to Aleqa Gebre Hanna "
    "(the lean elder with salt-and-pepper beard, sharp eyes, and cream turban "
    "with a gold band); keep all other guests, hosts, servers, and bystanders "
    "with distinct different faces and no turban.")

# Directive B — the Gatekeeper (bare-headed, short oiled hair, dark-teal kabba)
DIRECTIVE_GATEKEEPER = (
    " Redraw the referenced person as a flat-colour comic-book illustration: "
    "bold black ink contours, flat saturated colour, halftone dot shading, "
    "no photorealism. Apply the referenced face ONLY to the stout bare-headed "
    "Gatekeeper (short oiled black hair, short beard, NO turban and NO hat, "
    "wearing the dark-teal velvet kabba with gold trim); keep all other "
    "characters distinct.")

DIRECTIVES = {
    "gebre_hanna": DIRECTIVE_GEBRE_HANNA,
    "gatekeeper": DIRECTIVE_GATEKEEPER,
}

SEP = " — "


def directive_for(actor):
    """The identity directive for a cast id, or '' for unreferenced panels."""
    return DIRECTIVES.get(actor or "", "")


def compose(style_block, prompt, actor=None, has_reference=None):
    """style + subject prompt + that actor's directive (only for a named actor).

    `has_reference` is accepted for older callers; the actor id is the source of
    truth now, because a wrong directive is how the gatekeeper used to inherit
    Gebre Hanna's turban.
    """
    if has_reference and actor is None:
        actor = "gebre_hanna"  # legacy callers meant the hero portrait
    return style_block + SEP + prompt + directive_for(actor)
