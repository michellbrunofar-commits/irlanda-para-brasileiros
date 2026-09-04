"""Gera a imagem vertical (1080x1920) pra postar no Instagram Stories,
a partir da manchete chamativa (GANCHO) de cada edição."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT_PATH = ROOT / "assets" / "fonts" / "Inter-Variable.ttf"

W, H = 1080, 1920
MARGIN = 84

# mesmas cores de tailwind.config.ts (ireland.green-dark / green / green claro)
GRADIENT_STOPS = [
    (0.0, (15, 122, 77)),
    (0.5, (22, 155, 98)),
    (1.0, (26, 184, 112)),
]


def _font(weight: str, size: int) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(str(FONT_PATH), size)
    f.set_variation_by_name(weight)
    return f


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _mix(t: float) -> tuple[int, int, int]:
    for (t0, c0), (t1, c1) in zip(GRADIENT_STOPS, GRADIENT_STOPS[1:]):
        if t0 <= t <= t1:
            local = (t - t0) / (t1 - t0) if t1 > t0 else 0
            return tuple(int(c0[k] + (c1[k] - c0[k]) * local) for k in range(3))
    return GRADIENT_STOPS[-1][1]


def _gradient_background() -> Image.Image:
    sw, sh = 108, 192
    pixels = []
    for y in range(sh):
        for x in range(sw):
            t = (x / (sw - 1) + y / (sh - 1)) / 2
            pixels.append(_mix(t))
    small = Image.new("RGB", (sw, sh))
    small.putdata(pixels)
    return small.resize((W, H), Image.BICUBIC)


def _draw_ireland_flag(draw: ImageDraw.ImageDraw, x: float, y: float, w: float, h: float) -> None:
    draw.rectangle((x, y, x + w / 3, y + h), fill=(22, 155, 98))
    draw.rectangle((x + w / 3, y, x + 2 * w / 3, y + h), fill=(255, 255, 255))
    draw.rectangle((x + 2 * w / 3, y, x + w, y + h), fill=(255, 136, 62))


def _draw_brazil_flag(draw: ImageDraw.ImageDraw, x: float, y: float, w: float, h: float) -> None:
    draw.rectangle((x, y, x + w, y + h), fill=(0, 156, 59))
    cx, cy = x + w / 2, y + h / 2
    diamond = [(cx, y + h * 0.12), (x + w * 0.88, cy), (cx, y + h * 0.88), (x + w * 0.12, cy)]
    draw.polygon(diamond, fill=(255, 223, 0))
    r = h * 0.19
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(0, 39, 118))


def generate_story_image(headline: str, out_path: Path) -> None:
    img = _gradient_background()
    draw = ImageDraw.Draw(img)

    flag_w, flag_h = 58, 40
    _draw_ireland_flag(draw, MARGIN, 108, flag_w, flag_h)
    _draw_brazil_flag(draw, MARGIN + flag_w + 16, 108, flag_w, flag_h)

    draw.text((MARGIN, 172), "IRLANDA PARA BRASILEIROS", font=_font("ExtraBold", 30), fill=(255, 255, 255))
    draw.text((MARGIN, 216), "por Michell Lago", font=_font("Medium", 24), fill=(255, 255, 255, 175))

    max_w = W - MARGIN * 2
    size = 92
    lines = [headline]
    while size > 50:
        hf = _font("ExtraBold", size)
        lines = _wrap(draw, headline, hf, max_w)
        line_h = size * 1.12
        if line_h * len(lines) < 680 and len(lines) <= 5:
            break
        size -= 4

    hf = _font("ExtraBold", size)
    line_h = size * 1.12
    total_h = line_h * len(lines)
    y0 = (H - total_h) / 2 - 20
    for i, ln in enumerate(lines):
        draw.text((MARGIN, y0 + i * line_h), ln, font=hf, fill=(255, 255, 255))

    cta_font = _font("Bold", 34)
    cta_text = "Leia a matéria completa →"
    tw = draw.textlength(cta_text, font=cta_font)
    cta_y = H - 220
    draw.rounded_rectangle((MARGIN - 24, cta_y - 20, MARGIN + tw + 24, cta_y + 58), radius=16, fill=(255, 255, 255, 235))
    draw.text((MARGIN, cta_y), cta_text, font=cta_font, fill=(15, 122, 77))

    draw.text((MARGIN, H - 100), "irlandaparabrasileiros.vercel.app", font=_font("SemiBold", 26), fill=(255, 255, 255, 160))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out_path, "PNG", optimize=True)
