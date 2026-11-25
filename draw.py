#!/usr/bin/env python3
"""Draw a broadsheet-style front page summing up 24 November 2026.

Renders entry.png (1024x1024) next to this script using PIL only.
Layout is fully measured: every string is wrapped against
ImageDraw.textlength so nothing overflows its box.
"""

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- constants
W = H = 1024
MARGIN = 48
CONTENT_W = W - 2 * MARGIN

PAPER = "#f7f2e7"
INK = "#1a1a1a"
ACCENT = "#b03a2e"
LEAD_BG = "#ece1c8"
PANEL_BG = "#fbf8f1"
RULE = "#8a7f63"
SUBINK = "#3d382c"

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_font(draw, text, path, size, max_w):
    """Shrink size until text fits max_w; return the font."""
    while size > 8 and draw.textlength(text, font=font(path, size)) > max_w:
        size -= 2
    return font(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap measured with textlength."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, xy, text, fnt, fill, max_w, leading=1.18):
    """Draw wrapped text; return the y just below it."""
    x, y = xy
    step = int(fnt.size * leading)
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += step
    return y


def chip(draw, xy, label, bg, fnt=None):
    """Small filled category label; return its (w, h)."""
    fnt = fnt or font(SANS_B, 17)
    tw = draw.textlength(label, font=fnt)
    w, h = int(tw) + 18, 27
    draw.rectangle([xy[0], xy[1], xy[0] + w, xy[1] + h], fill=bg)
    draw.text((xy[0] + 9, xy[1] + 4), label, font=fnt, fill="#ffffff")
    return w, h


# ---------------------------------------------------------------- the story
LEAD = {
    "chip": "LEAD · TECH & MARKETS",
    "headline": "Nvidia brings back Jensen Huang — shares leap 31%",
    "sub": ("The board reinstates its founder as CEO after pressure from "
            "President Trump; the S&P 500 jumps 4.7% as AI stocks rally."),
}

PANELS = [
    ("WAR IN EUROPE", "#7a4a3a",
     "Ukraine sinks Russian warship off Libya",
     "Drones hit Merkury in Benghazi port; Zaporizhzhia strike kills 2."),
    ("MIDDLE EAST", "#8a5a2b",
     "Israeli strike kills Hamas security chief in Gaza",
     "Tankers hit mines in Hormuz as Qatar's PM pushes US-Iran talks."),
    ("SECURITY", "#5d4a6b",
     "NATO vows defence over 'nuclear satellite' reports",
     "Rutte responds: a nuclear-armed satellite may orbit within weeks."),
    ("CLIMATE", "#2e6b5e",
     "COP31 ends without a fossil-fuel deal",
     "Talks in Türkiye collapse over final wording; a divided world."),
    ("US POLITICS", "#8a5a2b",
     "Democrats win the House in a landslide",
     "Largest margin in decades; Trump fast-tracks federal executions."),
    ("SPORT", "#3f6b2e",
     "Alcaraz lifts his first ATP Finals crown",
     "Beats Zverev in Turin; Gukesh opens chess title defence in Geneva."),
]

ALSO = ("Pakistan's Zeeshan Ali to be first foreign astronaut on China's "
        "space station · Landmine casualties hit a five-year high of 7,000 "
        "· US blacklists Megaspeed in Nvidia chip-smuggling case")


# ---------------------------------------------------------------- drawing
def draw_page():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    x0 = MARGIN

    # masthead
    y = 24
    f = fit_font(d, "T H E   W O R L D   I N   O N E   D A Y", SANS_B, 30, CONTENT_W)
    d.text((x0, y), "T H E   W O R L D   I N   O N E   D A Y", font=f, fill=INK)
    y += 36
    f = fit_font(d, "24 NOVEMBER 2026", SERIF_B, 88, CONTENT_W)
    d.text((x0, y), "24 NOVEMBER 2026", font=f, fill=INK)
    y += int(f.size * 1.0)
    d.text((x0, y), "Tuesday · The day's biggest stories, in one picture",
           font=font(SANS, 25), fill=SUBINK)
    y += 32
    d.line([(x0, y), (x0 + CONTENT_W, y)], fill=INK, width=4)
    d.line([(x0, y + 7), (x0 + CONTENT_W, y + 7)], fill=INK, width=1)
    y += 16

    # lead panel (height measured from its wrapped content)
    pad = 22
    inner_w = CONTENT_W - 7 - 2 * pad
    head_f, sub_f = font(SERIF_B, 38), font(SANS, 20)
    hl = wrap(d, LEAD["headline"], head_f, inner_w)
    sl = wrap(d, LEAD["sub"], sub_f, inner_w)
    lead_h = (12 + 27 + 10 + len(hl) * int(38 * 1.12) + 5
              + len(sl) * int(20 * 1.2) + 12)
    d.rectangle([x0, y, x0 + CONTENT_W, y + lead_h], fill=LEAD_BG)
    d.rectangle([x0, y, x0 + 7, y + lead_h], fill=ACCENT)
    cx = x0 + 7 + pad
    cy = y + 12
    chip(d, (cx, cy), LEAD["chip"], ACCENT)
    cy += 37
    cy = text_block(d, (cx, cy), LEAD["headline"], head_f, INK,
                    inner_w, leading=1.12)
    cy += 5
    text_block(d, (cx, cy), LEAD["sub"], sub_f, SUBINK,
               inner_w, leading=1.2)
    y += lead_h + 10

    # grid of six panels, two columns
    gap = 10
    col_w = (CONTENT_W - gap) // 2
    head_f = font(SERIF_B, 25)
    sub_f = font(SANS, 19)
    for row in range(3):
        row_h = 0
        for col in range(2):
            label, color, head, sub = PANELS[row * 2 + col]
            px = x0 + col * (col_w + gap)
            inner_w = col_w - 2 * 16
            hl = wrap(d, head, head_f, inner_w)
            sl = wrap(d, sub, sub_f, inner_w)
            ph = 10 + 27 + 4 + len(hl) * int(25 * 1.12) + 3 + len(sl) * int(19 * 1.2) + 8
            d.rectangle([px, y, px + col_w, y + ph], fill=PANEL_BG,
                        outline="#d8cfb8", width=1)
            cyy = y + 10
            chip(d, (px + 16, cyy), label, color)
            cyy += 31
            cyy = text_block(d, (px + 16, cyy), head, head_f, INK, inner_w,
                             leading=1.12)
            cyy += 3
            text_block(d, (px + 16, cyy), sub, sub_f, SUBINK, inner_w,
                       leading=1.2)
            row_h = max(row_h, ph)
        y += row_h + gap

    # also today strip (height measured from its wrapped lines)
    also_f = font(SANS, 19)
    also_lines = wrap(d, ALSO, also_f, CONTENT_W - 36)
    strip_h = 32 + len(also_lines) * int(19 * 1.18) + 9
    d.rectangle([x0, y, x0 + CONTENT_W, y + strip_h], fill=INK)
    d.text((x0 + 18, y + 8), "A L S O   T O D A Y", font=font(SANS_B, 17),
           fill="#e8b64c")
    text_block(d, (x0 + 18, y + 32), ALSO, also_f, "#f2eee2",
               CONTENT_W - 36, leading=1.18)
    y += strip_h + 8

    # footer
    f = font(SANS, 19)
    foot = "Compiled from the day's reports · 24 November 2026"
    tw = d.textlength(foot, font=f)
    d.text(((W - tw) / 2, y), foot, font=f, fill=SUBINK)
    assert y + 24 <= H, f"page overflows: footer ends at {y + 24} of {H}"

    return img


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    draw_page().save(out)
    print("wrote", out)
