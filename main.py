#!/usr/bin/env python3
"""Draw the cutest picture: a round baby chick with huge glossy eyes,
rosy cheeks, a tiny pink bow and one little wing raised in a wave.

Pure standard library (struct, zlib, math, os). Renders at 2x resolution
with span-filled shapes, then box-downsamples to 1024x1024 for smooth
edges, and writes a PNG to $MAKEFUN_OUTPUT_DIR/entry.png (default
/output/entry.png). Fully deterministic: same bytes on every run.
"""

import math
import os
import struct
import zlib

SS = 2                      # supersampling factor
OUT = 1024                  # output size in pixels
W = OUT * SS                # render buffer size
ROW = W * 3                 # bytes per render row

# ---------------------------------------------------------------- palette
CREAM_TOP = (255, 249, 236)
CREAM_BOT = (255, 232, 198)
SHADOW = (232, 198, 158)
OUTLINE = (214, 138, 30)    # warm brown-orange outline
BODY = (255, 210, 63)       # chick yellow
BODY_DARK = (245, 184, 30)  # shading / wings / tuft
BELLY = (255, 226, 122)     # lighter belly
BEAK = (255, 159, 28)
FEET = (255, 159, 28)
PUPIL = (43, 33, 24)
WHITE = (255, 255, 255)
BLUSH = (244, 130, 110)
BOW = (255, 123, 172)
BOW_DARK = (232, 90, 155)
SMILE = (120, 70, 20)
DOT_PINK = (255, 222, 226)
DOT_MINT = (214, 240, 224)
DOT_LILAC = (232, 222, 248)

buf = bytearray(W * W * 3)


def _fill_span(y, x0, x1, color):
    """Fill pixels [x0, x1) on render row y with a solid RGB color."""
    if y < 0 or y >= W:
        return
    x0 = max(0, x0)
    x1 = min(W, x1)
    if x1 <= x0:
        return
    base = (y * W + x0) * 3
    buf[base:base + (x1 - x0) * 3] = bytes(color) * (x1 - x0)


def fill_ellipse(cx, cy, rx, ry, color, angle=0.0):
    """Fill a (possibly rotated) ellipse. angle in radians."""
    c = math.cos(angle)
    s = math.sin(angle)
    a2 = rx * rx
    b2 = ry * ry
    # Row range: |dy| <= sqrt(a^2 s^2 + b^2 c^2)
    ymax = int(math.sqrt(a2 * s * s + b2 * c * c)) + 1
    A = c * c / a2 + s * s / b2
    for y in range(int(cy - ymax), int(cy + ymax) + 1):
        dy = y - cy
        B = 2.0 * dy * c * s * (1.0 / a2 - 1.0 / b2)
        C = dy * dy * (s * s / a2 + c * c / b2) - 1.0
        disc = B * B - 4.0 * A * C
        if disc < 0:
            continue
        root = math.sqrt(disc) / (2.0 * A)
        xm = -B / (2.0 * A)
        _fill_span(y, int(cx + xm - root), int(cx + xm + root) + 1, color)


def fill_circle(cx, cy, r, color):
    fill_ellipse(cx, cy, r, r, color)


def fill_poly(points, color):
    """Scanline fill of a simple polygon given as [(x, y), ...]."""
    ys = [p[1] for p in points]
    y0, y1 = int(min(ys)), int(max(ys))
    n = len(points)
    for y in range(y0, y1 + 1):
        xs = []
        for i in range(n):
            x1, y1p = points[i]
            x2, y2p = points[(i + 1) % n]
            if (y1p <= y < y2p) or (y2p <= y < y1p):
                t = (y - y1p) / (y2p - y1p)
                xs.append(x1 + t * (x2 - x1))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            _fill_span(y, int(xs[i]), int(xs[i + 1]) + 1, color)


def stamp_circle(cx, cy, r, color):
    fill_circle(cx, cy, r, color)


def draw_curve(points, r, color):
    """Draw a smooth curve through points by stamping small circles."""
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        steps = max(2, int(math.hypot(x2 - x1, y2 - y1) / (r * 0.7)) + 1)
        for k in range(steps + 1):
            t = k / steps
            stamp_circle(int(x1 + (x2 - x1) * t), int(y1 + (y2 - y1) * t), r, color)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ---------------------------------------------------------------- picture
def draw():
    # Background: soft vertical cream gradient.
    for y in range(W):
        _fill_span(y, 0, W, lerp(CREAM_TOP, CREAM_BOT, y / (W - 1)))

    # Faint pastel dots scattered in the background (away from the chick).
    for (x, y, r, col) in [
        (250, 260, 34, DOT_PINK), (1790, 300, 28, DOT_MINT),
        (190, 900, 26, DOT_LILAC), (1860, 950, 34, DOT_PINK),
        (330, 1560, 30, DOT_MINT), (1730, 1620, 26, DOT_LILAC),
        (1024, 180, 30, DOT_PINK),
    ]:
        fill_circle(x, y, r, col)

    # Ground shadow.
    fill_ellipse(1024, 1830, 520, 72, SHADOW)

    # Feet: two tiny orange ovals peeking out under the body.
    fill_ellipse(830, 1802, 92, 46, FEET)
    fill_ellipse(1218, 1802, 92, 46, FEET)

    # Body outline, then body.
    fill_circle(1024, 1150, 632, OUTLINE)
    fill_circle(1024, 1150, 618, BODY)

    # Soft shading: a darker patch low on the body's right side, kept
    # fully inside the body circle, then the lighter belly over it.
    fill_ellipse(1150, 1480, 320, 200, BODY_DARK)
    # Belly: lighter oval low on the body.
    fill_ellipse(1024, 1360, 380, 300, BELLY)

    # Wings: left wing resting, right wing raised in a little wave.
    fill_ellipse(500, 1230, 150, 235, BODY_DARK, angle=math.radians(-28))
    fill_ellipse(1590, 930, 135, 220, BODY_DARK, angle=math.radians(42))

    # Head tuft: three little feathers on top.
    fill_ellipse(985, 512, 26, 72, BODY_DARK, angle=math.radians(-22))
    fill_ellipse(1032, 496, 26, 78, BODY_DARK, angle=math.radians(0))
    fill_ellipse(1078, 516, 26, 70, BODY_DARK, angle=math.radians(22))

    # Tiny pink bow on the upper right of the head.
    fill_poly([(1330, 640), (1226, 576), (1226, 704)], BOW)
    fill_poly([(1330, 640), (1434, 576), (1434, 704)], BOW)
    fill_circle(1330, 640, 36, BOW_DARK)

    # Blush cheeks.
    fill_ellipse(700, 1185, 96, 56, BLUSH)
    fill_ellipse(1348, 1185, 96, 56, BLUSH)

    # Eyes: big white ovals, dark pupils, glossy highlights.
    for ex in (830, 1218):
        fill_ellipse(ex, 985, 106, 132, WHITE)
        fill_ellipse(ex, 972, 54, 70, PUPIL)
        fill_circle(ex - 20, 940, 20, WHITE)
        fill_circle(ex + 24, 1000, 9, WHITE)

    # Beak: small rounded orange diamond.
    fill_poly([(1024, 1108), (1092, 1152), (1024, 1206), (956, 1152)], BEAK)
    fill_circle(1024, 1152, 34, BEAK)

    # Smile: a gentle curve under the beak.
    draw_curve([(952, 1252), (988, 1274), (1024, 1282), (1060, 1274), (1096, 1252)], 11, SMILE)


# ---------------------------------------------------------------- downsample
def downsample():
    """Box-average the 2x render buffer to 1024x1024 RGB bytes."""
    out = bytearray(OUT * OUT * 3)
    for oy in range(OUT):
        sy = oy * SS
        r0 = memoryview(buf)[sy * ROW:(sy + 1) * ROW]
        r1 = memoryview(buf)[(sy + 1) * ROW:(sy + 2) * ROW]
        obase = oy * OUT * 3
        for ox in range(OUT):
            sx = ox * SS * 3
            o = obase + ox * 3
            out[o] = (r0[sx] + r0[sx + 3] + r1[sx] + r1[sx + 3]) // 4
            out[o + 1] = (r0[sx + 1] + r0[sx + 4] + r1[sx + 1] + r1[sx + 4]) // 4
            out[o + 2] = (r0[sx + 2] + r0[sx + 5] + r1[sx + 2] + r1[sx + 5]) // 4
    return bytes(out)


# ---------------------------------------------------------------- PNG encode
def write_png(rgb, path):
    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", OUT, OUT, 8, 2, 0, 0, 0)  # 8-bit RGB
    raw = bytearray()
    stride = OUT * 3
    for y in range(OUT):
        raw.append(0)  # filter: None
        raw += rgb[y * stride:(y + 1) * stride]
    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    draw()
    rgb = downsample()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    path = os.path.join(out_dir, "entry.png")
    size = write_png(rgb, path)
    print(f"wrote {path} ({size} bytes, {OUT}x{OUT})")


if __name__ == "__main__":
    main()
