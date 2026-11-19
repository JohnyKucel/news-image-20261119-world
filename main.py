import os
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(os.environ.get("MAKEFUN_OUTPUT_DIR", os.path.join(ROOT, "out")), "entry.png")

PAGE_W, PAGE_H = 1024, 1024
MARGIN = 24
CONTENT_W = PAGE_W - 2 * MARGIN
COL_W = (CONTENT_W - 24) // 2

PAPER = (250, 248, 242)
INK = (22, 22, 20)
BODY_GRAY = (70, 68, 64)
HAIRLINE = (190, 186, 176)
NAVY = (31, 58, 95)
BRICK = (168, 54, 38)
PLUM = (96, 58, 120)
TEAL = (18, 110, 105)
OCHRE = (133, 84, 0)

SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_ITALIC = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

HERO_KICKER = "Diplomacy"
HERO_HEADLINE = "TRUMP, XI AND PUTIN MEET IN SHENZHEN"
HERO_CAPTION = "President Donald Trump and President Xi Jinping in Shenzhen. — Reuters"
HERO_DECK = "Nuclear arms and Iran on the agenda."

CARDS = [
    {
        "kicker": "Culture", "color": PLUM,
        "headline": "GTA VI ROLLS OUT WORLDWIDE",
        "sub": "After 13-year wait, Vice City returns. Metacritic 99.",
        "source": "Rockstar Games",
        "photo": "gta.jpg",
    },
    {
        "kicker": "Conflict", "color": BRICK,
        "headline": "IRAN HITS US BASE IN KUWAIT",
        "sub": "Bahrain intercepts more attacks after the Qeshm strike.",
        "source": "AP, Reuters",
        "photo": None,
    },
    {
        "kicker": "Europe", "color": TEAL,
        "headline": "EU PROPOSES 45 BILLION EURO UKRAINE LOAN",
        "sub": "Repayment via Russian reparations.",
        "source": "\u20ac20B budget, \u20ac25B military \u2014 Reuters, EU Commission",
        "photo": None,
    },
    {
        "kicker": "Politics", "color": OCHRE,
        "headline": "JEFFRIES NOMINATED FOR SPEAKER",
        "sub": "Democrats back him 251\u201311; first Black Speaker if elected Jan 3.",
        "source": "CNN, USA Today, NPR",
        "photo": "jeffries.jpg",
    },
]


def load(path, size):
    return ImageFont.truetype(path, size)


def fit_lines(draw, text, face, width):
    lines = []
    for chunk in text.split("\n"):
        words = chunk.split()
        current = ""
        for word in words:
            trial = word if not current else current + " " + word
            if draw.textlength(trial, font=face) <= width:
                current = trial
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines


def balanced_pair(draw, text, face, width):
    words = text.split()
    best = None
    for cut in range(1, len(words)):
        first = " ".join(words[:cut])
        second = " ".join(words[cut:])
        w1 = draw.textlength(first, font=face)
        w2 = draw.textlength(second, font=face)
        if w1 > width or w2 > width:
            continue
        gap = abs(w1 - w2)
        if best is None or gap < best[0]:
            best = (gap, [first, second])
    return best[1]


def crop_to(name, width, height, focus_y=0.5):
    shot = Image.open(os.path.join(ROOT, "assets", name)).convert("RGB")
    return ImageOps.fit(shot, (width, height), Image.LANCZOS, centering=(0.5, focus_y))


def hline(draw, x0, x1, y, color=INK, px=1):
    draw.line([(x0, y), (x1, y)], fill=color, width=px)


def render_card(page, draw, card, x, top, row_h):
    thumb_w = 150
    if card["photo"]:
        shot = crop_to(card["photo"], thumb_w, row_h - 8, 0.5)
        page.paste(shot, (x, top + 4))
        text_x = x + thumb_w + 12
        text_w = COL_W - thumb_w - 12
    else:
        text_x = x
        text_w = COL_W

    kicker_face = load(SERIF, 17)
    draw.text((text_x, top + 2), card["kicker"], font=kicker_face, fill=card["color"])

    head_face = load(SERIF_BOLD, 23)
    lines = fit_lines(draw, card["headline"], head_face, text_w)
    assert len(lines) <= 3, (card["kicker"], lines)
    y = top + 28
    for line in lines:
        draw.text((text_x, y), line, font=head_face, fill=INK)
        y += 28

    sub_face = load(SERIF, 15)
    sub_lines = fit_lines(draw, card["sub"], sub_face, text_w)
    assert len(sub_lines) <= 2, (card["kicker"], sub_lines)
    y += 6
    for line in sub_lines:
        draw.text((text_x, y), line, font=sub_face, fill=BODY_GRAY)
        y += 20

    src_face = load(SERIF, 13)
    draw.text((text_x, top + row_h - 18), card["source"], font=src_face, fill=BODY_GRAY)


def main():
    page = Image.new("RGBA", (PAGE_W, PAGE_H), PAPER + (255,))
    draw = ImageDraw.Draw(page)
    right = PAGE_W - MARGIN
    outlines = []

    mast_face = load(SERIF_BOLD, 92)
    draw.text((PAGE_W // 2, 4), "THE WORLD", font=mast_face, fill=INK, anchor="ma")
    hline(draw, MARGIN, right, 102)
    date_face = load(SANS_BOLD, 27)
    draw.text((PAGE_W // 2, 110), "THURSDAY, 19 NOVEMBER 2026", font=date_face, fill=INK, anchor="ma")
    hline(draw, MARGIN, right, 144, px=3)

    kicker_face = load(SERIF, 18)
    draw.text((MARGIN, 156), HERO_KICKER, font=kicker_face, fill=NAVY)

    hero_face = load(SERIF_BOLD, 42)
    hero_lines = balanced_pair(draw, HERO_HEADLINE, hero_face, CONTENT_W)
    y = 182
    for line in hero_lines:
        draw.text((MARGIN, y), line, font=hero_face, fill=INK)
        y += 48

    hero = crop_to("hero.jpg", CONTENT_W, 222, 0.30)
    page.paste(hero, (MARGIN, 286))
    outlines.append((MARGIN, 286, MARGIN + CONTENT_W - 1, 286 + 222 - 1))

    cap_face = load(SANS, 13)
    draw.text((MARGIN, 514), HERO_CAPTION, font=cap_face, fill=BODY_GRAY)
    deck_face = load(SERIF_ITALIC, 22)
    draw.text((MARGIN, 538), HERO_DECK, font=deck_face, fill=INK)
    hline(draw, MARGIN, right, 572)

    row_h = 182
    grid_top = 584
    for idx, card in enumerate(CARDS):
        col = idx % 2
        row = idx // 2
        x = MARGIN + col * (COL_W + 24)
        top = grid_top + row * (row_h + 8)
        if card["photo"]:
            outlines.append((x, top + 4, x + 150 - 1, top + 4 + row_h - 8 - 1))
        render_card(page, draw, card, x, top, row_h)
        if col == 0:
            draw.line(
                [(x + COL_W + 12, top), (x + COL_W + 12, top + row_h - 6)],
                fill=HAIRLINE, width=1,
            )
        if row == 0:
            hline(draw, MARGIN, right, top + row_h + 3, color=HAIRLINE)

    hline(draw, MARGIN, right, 974, px=2)
    foot_bold = load(SERIF_BOLD, 14)
    foot_reg = load(SERIF, 14)
    draw.text((MARGIN, 982), "The World", font=foot_bold, fill=INK)
    draw.text((right, 982), "Thursday, 19 November 2026", font=foot_reg, fill=INK, anchor="ra")

    veil = Image.new("RGBA", page.size, (0, 0, 0, 0))
    veil_draw = ImageDraw.Draw(veil)
    for box in outlines:
        veil_draw.rectangle(box, outline=(0, 0, 0, 26), width=1)
    page = Image.alpha_composite(page, veil)

    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    page.convert("RGB").save(DEST, optimize=True)
    print("wrote", DEST)


if __name__ == "__main__":
    main()
