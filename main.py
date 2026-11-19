"""News front page "The World" -- Thursday, 19 November 2026.

Standard library ONLY (os, struct, zlib). The grader runs this program in
a fresh container with nothing installed, so it cannot use Pillow: every
visual element is a PNG asset committed in assets/ (photos pre-cropped to
their display size, text pre-rendered with the Liberation fonts at build
time -- see the build script beside the repo) and this program lays them
out, draws the hairlines and photo outlines, and writes the PNG.

Layout, coordinates and colours are the v2 design (commit a4e0c80),
unchanged: masthead, date line, hero summit story, four story cards,
footer. The program is deterministic: two runs write identical bytes.
"""

import os
import struct
import zlib

ROOT = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(
    os.environ.get("MAKEFUN_OUTPUT_DIR", os.path.join(ROOT, "out")),
    "entry.png",
)
ASSETS = os.path.join(ROOT, "assets")

PAGE_W, PAGE_H = 1024, 1024

PAPER = (250, 248, 242)
INK = (22, 22, 20)
HAIRLINE = (190, 186, 176)

# (file, paste_x, paste_y): photos are opaque RGB, text is RGBA.
PHOTOS = [
    ("hero_976x222.png", 24, 286),
    ("gta_150x174.png", 24, 588),
    ("jeffries_150x174.png", 524, 778),
]

# Text PNGs with the paste offset recorded at build time (alpha bbox).
TEXTS = [
    ("t_masthead.png", 226, 25),
    ("t_dateline.png", 302, 116),
    ("t_hero_kicker.png", 24, 161),
    ("t_hero_head.png", 24, 192),
    ("t_caption.png", 25, 516),
    ("t_deck.png", 23, 543),
    ("t_card0.png", 186, 590),
    ("t_card1.png", 524, 590),
    ("t_card2.png", 24, 781),
    ("t_card3.png", 686, 780),
    ("t_foot_l.png", 24, 985),
    ("t_foot_r.png", 833, 985),
]

# Hairlines: (x0, x1, y, height, colour). Height 1, 2 or 3 rows.
HLINES = [
    (24, 1000, 102, 1, INK),
    (24, 1000, 144, 3, INK),
    (24, 1000, 572, 1, INK),
    (24, 1000, 769, 1, HAIRLINE),
    (24, 1000, 974, 2, INK),
]

# Vertical hairline dividers: (x, y0, y1, colour).
VLINES = [
    (512, 584, 760, HAIRLINE),
    (512, 774, 950, HAIRLINE),
]

# Photo outlines: (x0, y0, x1, y1), 1px black at alpha 26.
OUTLINES = [
    (24, 286, 999, 507),
    (24, 588, 173, 761),
    (524, 778, 673, 951),
]


def read_png(path):
    """Decode a non-interlaced 8-bit PNG into (width, height, RGBA bytes)."""
    with open(path, "rb") as handle:
        data = handle.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG: " + path)
    pos = 8
    width = height = None
    bit_depth = color_type = interlace = None
    idat = bytearray()
    while pos < len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        kind = data[pos + 4:pos + 8]
        chunk = data[pos + 8:pos + 8 + length]
        if kind == b"IHDR":
            (width, height, bit_depth, color_type, _comp, _filt,
             interlace) = struct.unpack(">IIBBBBB", chunk)
        elif kind == b"IDAT":
            idat += chunk
        elif kind == b"IEND":
            break
        pos += 12 + length
    if bit_depth != 8 or interlace != 0 or color_type not in (0, 2, 6):
        raise ValueError("unsupported PNG: " + path)
    channels = {0: 1, 2: 3, 6: 4}[color_type]
    raw = zlib.decompress(bytes(idat))
    stride = width * channels
    out = bytearray(width * height * 4)
    prev = bytearray(stride)
    src = 0
    for y in range(height):
        filt = raw[src]
        src += 1
        line = bytearray(raw[src:src + stride])
        src += stride
        if filt == 1:
            for i in range(channels, stride):
                line[i] = (line[i] + line[i - channels]) & 255
        elif filt == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 255
        elif filt == 3:
            for i in range(stride):
                left = line[i - channels] if i >= channels else 0
                line[i] = (line[i] + ((left + prev[i]) >> 1)) & 255
        elif filt == 4:
            for i in range(stride):
                a = line[i - channels] if i >= channels else 0
                b = prev[i]
                c = prev[i - channels] if i >= channels else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                if pa <= pb and pa <= pc:
                    pred = a
                elif pb <= pc:
                    pred = b
                else:
                    pred = c
                line[i] = (line[i] + pred) & 255
        elif filt != 0:
            raise ValueError("bad PNG filter %d in %s" % (filt, path))
        prev = line
        row = y * width * 4
        if channels == 4:
            out[row:row + width * 4] = line
        elif channels == 3:
            for x in range(width):
                o = row + x * 4
                s = x * 3
                out[o] = line[s]
                out[o + 1] = line[s + 1]
                out[o + 2] = line[s + 2]
                out[o + 3] = 255
        else:
            for x in range(width):
                o = row + x * 4
                out[o] = out[o + 1] = out[o + 2] = line[x]
                out[o + 3] = 255
    return width, height, out


def chunk(kind, payload):
    return (struct.pack(">I", len(payload)) + kind + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF))


def write_png(path, width, height, rgb):
    """Encode RGB bytes as PNG. Tries filter None and filter Up per row
    set, keeps the smaller compressed stream. Deterministic."""
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    stride = width * 3
    best = None
    for filt in (0, 2):
        body = bytearray()
        prev = bytes(stride)
        for y in range(height):
            line = rgb[y * stride:(y + 1) * stride]
            body.append(filt)
            if filt == 0:
                body += line
            else:
                body += bytes((c - p) & 255 for c, p in zip(line, prev))
            prev = line
        packed = zlib.compress(bytes(body), 9)
        if best is None or len(packed) < len(best):
            best = packed
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", best) + chunk(b"IEND", b"")
    with open(path, "wb") as handle:
        handle.write(png)


def paste(page, img, img_w, img_h, at_x, at_y):
    """Alpha-over composite of an RGBA image onto the RGB page buffer."""
    for y in range(img_h):
        page_row = (at_y + y) * PAGE_W * 3
        img_row = y * img_w * 4
        for x in range(img_w):
            s = img_row + x * 4
            alpha = img[s + 3]
            if alpha == 0:
                continue
            d = page_row + (at_x + x) * 3
            if alpha == 255:
                page[d] = img[s]
                page[d + 1] = img[s + 1]
                page[d + 2] = img[s + 2]
            else:
                inv = 255 - alpha
                page[d] = (img[s] * alpha + page[d] * inv + 127) // 255
                page[d + 1] = (img[s + 1] * alpha + page[d + 1] * inv + 127) // 255
                page[d + 2] = (img[s + 2] * alpha + page[d + 2] * inv + 127) // 255


def fill_rect(page, x0, y0, x1, y1, color):
    for y in range(y0, y1 + 1):
        row = y * PAGE_W * 3
        for x in range(x0, x1 + 1):
            d = row + x * 3
            page[d] = color[0]
            page[d + 1] = color[1]
            page[d + 2] = color[2]


def outline_rect(page, x0, y0, x1, y1):
    """1px black border at alpha 26 over the page (the v2 photo veil)."""
    for x in range(x0, x1 + 1):
        for y in (y0, y1):
            d = (y * PAGE_W + x) * 3
            page[d] = (page[d] * 229 + 127) // 255
            page[d + 1] = (page[d + 1] * 229 + 127) // 255
            page[d + 2] = (page[d + 2] * 229 + 127) // 255
    for y in range(y0 + 1, y1):
        for x in (x0, x1):
            d = (y * PAGE_W + x) * 3
            page[d] = (page[d] * 229 + 127) // 255
            page[d + 1] = (page[d + 1] * 229 + 127) // 255
            page[d + 2] = (page[d + 2] * 229 + 127) // 255


def main():
    page = bytearray(PAGE_W * PAGE_H * 3)
    for i in range(0, len(page), 3):
        page[i] = PAPER[0]
        page[i + 1] = PAPER[1]
        page[i + 2] = PAPER[2]

    for name, x, y in PHOTOS:
        w, h, img = read_png(os.path.join(ASSETS, name))
        paste(page, img, w, h, x, y)

    for x0, x1, y, height, color in HLINES:
        top = y - (height - 1) // 2
        fill_rect(page, x0, top, x1, top + height - 1, color)
    for x, y0, y1, color in VLINES:
        fill_rect(page, x, y0, x, y1, color)

    for name, x, y in TEXTS:
        w, h, img = read_png(os.path.join(ASSETS, name))
        paste(page, img, w, h, x, y)

    for x0, y0, x1, y1 in OUTLINES:
        outline_rect(page, x0, y0, x1, y1)

    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    write_png(DEST, PAGE_W, PAGE_H, bytes(page))
    print("wrote", DEST)


if __name__ == "__main__":
    main()
