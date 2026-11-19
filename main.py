import os
from PIL import Image, ImageDraw, ImageFont, ImageOps

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.environ.get("MAKEFUN_OUTPUT_DIR", os.path.join(BASE, "out")), "entry.png")

W, H = 1024, 1024
PAPER = (250, 248, 242)
INK = (22, 22, 20)
GRAY = (112, 108, 100)
FAINT = (168, 164, 154)
NAVY = (31, 58, 95)
BRICK = (168, 54, 38)
PURPLE = (96, 58, 120)
TEAL = (18, 110, 105)
OCHRE = (176, 124, 32)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_REG = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_IT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    out = []
    for part in text.split("\n"):
        words = part.split()
        lines, cur = [], ""
        for word in words:
            trial = word if not cur else cur + " " + word
            if draw.textlength(trial, font=fnt) <= width:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        out.extend(lines)
    return out


def centre(draw, y, text, fnt, fill, cx=W // 2):
    draw.text((cx, y), text, font=fnt, fill=fill, anchor="ma")


def rule(draw, x0, x1, y, fill=INK, width=1):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def fit(path, tw, th, cy=0.45):
    im = Image.open(os.path.join(BASE, "assets", path)).convert("RGB")
    return ImageOps.fit(im, (tw, th), Image.LANCZOS, centering=(0.5, cy))


def kicker(draw, x, y, label, color, fnt):
    draw.text((x, y), label, font=fnt, fill=color)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 24
    rx = W - mx
    cw = rx - mx

    mast = font(SERIF, 96)
    centre(d, 6, "THE WORLD", mast, INK)
    rule(d, mx, rx, 112, INK, 1)
    date_f = font(SANS_B, 30)
    centre(d, 120, "THURSDAY, 19 NOVEMBER 2026", date_f, INK)
    small = font(SANS_B, 15)
    d.text((mx, 158), "WORLD NEWS", font=small, fill=INK)
    d.text((rx, 158), "LATE EDITION", font=small, fill=INK, anchor="ra")
    rule(d, mx, rx, 182, INK, 3)

    strip = font(SANS_B, 19)
    strip_s = font(SANS, 15)
    cells = [("€45 BN", "EU UKRAINE LOAN"), ("99", "GTA VI METACRITIC"), ("251–11", "JEFFRIES NOMINATION")]
    third = cw / 3
    for i, (num, lab) in enumerate(cells):
        cx = mx + third * i + third / 2
        d.text((cx, 194), num, font=strip, fill=INK, anchor="ma")
        d.text((cx, 220), lab, font=strip_s, fill=GRAY, anchor="ma")
        if i:
            d.line([(mx + third * i, 196), (mx + third * i, 236)], fill=FAINT, width=1)
    rule(d, mx, rx, 244, INK, 1)

    kick = font(SANS_B, 16)
    kicker(d, mx, 258, "DIPLOMACY", NAVY, kick)
    hero_f = font(SERIF, 43)
    h1 = wrap(d, "TRUMP, XI AND PUTIN MEET IN SHENZHEN", hero_f, cw)
    h2 = wrap(d, "FIRST THREE-WAY SUMMIT", hero_f, cw)
    assert len(h1) == 1 and len(h2) == 1, (h1, h2)
    y = 282
    for line in h1 + h2:
        d.text((mx, y), line, font=hero_f, fill=INK)
        y += 50

    photo = fit("hero.jpg", cw, 248, 0.28)
    img.paste(photo, (mx, y))
    y += 248
    cred = font(SANS, 13)
    d.text((mx, y + 5), "President Donald Trump shakes hands with President Xi Jinping. — REUTERS", font=cred, fill=GRAY)
    y += 26
    deck = font(SERIF_IT, 23)
    deck_lines = wrap(d, "Nuclear arms and Iran on the agenda as the three leaders meet in Shenzhen.", deck, cw)
    assert len(deck_lines) == 1, deck_lines
    d.text((mx, y), deck_lines[0], font=deck, fill=INK)
    y += 34
    rule(d, mx, rx, y, INK, 1)
    y += 12

    grid_top = y
    col_w = (cw - 24) // 2
    row_h = (972 - grid_top - 10) // 2
    cards = [
        ("CULTURE", PURPLE, "GTA VI ROLLS OUT WORLDWIDE", "gta.jpg", "REUTERS, ROCKSTAR"),
        ("CONFLICT", BRICK, "IRAN HITS US BASE IN KUWAIT\nBAHRAIN INTERCEPTS MORE ATTACKS", None, "AP, REUTERS, 18 NOV"),
        ("EUROPE", TEAL, "EU PROPOSES 45 BILLION EURO UKRAINE LOAN", None, "€20 BN BUDGET · €25 BN MILITARY — REUTERS, EU COMMISSION"),
        ("POLITICS", OCHRE, "JEFFRIES NOMINATED FOR SPEAKER", "jeffries.jpg", "CNN, USA TODAY, NPR"),
    ]
    subs = [
        "AFTER 13-YEAR WAIT; VICE CITY RETURNS",
        "AFTER US STRIKE ON QESHM ISLAND",
        "REPAYMENT VIA RUSSIAN REPARATIONS",
        "FIRST BLACK SPEAKER IF ELECTED JAN 3",
    ]
    head_f = font(SERIF, 23)
    sub_f = font(SANS, 14)
    src_f = font(SANS, 12)
    for idx, (label, color, head, photo_name, src) in enumerate(cards):
        col = idx % 2
        row = idx // 2
        x = mx + col * (col_w + 24)
        top = grid_top + row * row_h
        tx = x
        tw = col_w
        if photo_name:
            ph = fit(photo_name, 148, row_h - 16)
            img.paste(ph, (x, top + 8))
            tx = x + 160
            tw = col_w - 160
        d.rectangle([(tx, top), (tx + 56, top + 4)], fill=color)
        kicker(d, tx, top + 10, label, color, kick)
        hl = wrap(d, head, head_f, tw)
        assert len(hl) <= 2, (label, hl)
        ty = top + 32
        for line in hl:
            d.text((tx, ty), line, font=head_f, fill=INK)
            ty += 29
        sl = wrap(d, subs[idx], sub_f, tw)
        assert len(sl) == 1, (label, sl)
        d.text((tx, ty + 2), sl[0], font=sub_f, fill=GRAY)
        d.text((tx, ty + 24), src, font=src_f, fill=FAINT)
        if col == 0:
            d.line([(x + col_w + 12, top), (x + col_w + 12, top + row_h - 12)], fill=FAINT, width=1)
        if row == 0:
            rule(d, mx, rx, top + row_h, FAINT, 1)

    rule(d, mx, rx, 972, INK, 2)
    foot = font(SANS_B, 14)
    centre(d, 980, "THE WORLD  |  THURSDAY, 19 NOVEMBER 2026", foot, INK)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT, optimize=True)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
