#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NovelHub 封面生成器 v4 —— 生成 JPG 位图封面（不依赖浏览器渲染，结果确定）

为什么从 SVG 换成 JPG：
  v3 用 SVG，渐变 + 半透明色写在 fill 属性里（rgba），浏览器解析非法导致整片掉白。
  位图用 Pillow 直接画，任何环境、任何浏览器、任何 CDN 出来的像素都一样。

设计：
  - 800x1120（显示 400x560 的 2 倍，高清）
  - 按书名哈希选 12 套深色配色 → 每本不一样，且都足够暗保证白字可读
  - 宋体 Black 书名（仙侠题材质感）+ 苹方 作者/标签
  - 左侧书脊阴影、双线内边框、顶部光晕、暗角、极淡大水印字

用法：
  python3 scripts/generate_covers_v4.py
输出：
  public/covers/{slug}.jpg   （getCoverUrl 优先取 jpg，会自动生效）
"""
import json
import math
import os
import hashlib

from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 800, 1120
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COVERS_DIR = os.path.join(ROOT, "public", "covers")
NOVELS_JSON = os.path.join(ROOT, "data", "novels.json")

# ---- 字体 ----
F_TITLE = "/System/Library/Fonts/Supplemental/Songti.ttc"   # index 0 = Songti SC Black
F_UI = "/System/Library/Fonts/PingFang.ttc"                 # index 8 = PingFang SC Semibold

IVORY = (245, 241, 232)
GOLD = (238, 214, 156)

# 12 套配色：每套只有一个「主题色」，深色端由主题色压暗生成，
# 保证整体足够暗（白字可读）、色相统一、不显脏。
ACCENTS = [
    (0x4F, 0x8C, 0xB8),  # 深海蓝
    (0x8A, 0x5C, 0xC8),  # 玄紫
    (0xB8, 0x3E, 0x4A),  # 朱砂
    (0x3E, 0x8C, 0x6E),  # 青玉
    (0xC0, 0x92, 0x36),  # 鎏金
    (0x5C, 0x7C, 0x8C),  # 青灰
    (0x9A, 0x5E, 0x44),  # 古铜
    (0x44, 0x60, 0xA8),  # 靛青
    (0x9C, 0x52, 0x7A),  # 暗梅
    (0x6E, 0x86, 0x40),  # 苔绿
    (0xA8, 0x5A, 0x2C),  # 余烬
    (0x3E, 0x8C, 0x92),  # 苍青
]


def pick_palette(key: str):
    h = int(hashlib.md5(key.encode("utf-8")).hexdigest()[:8], 16)
    return ACCENTS[h % len(ACCENTS)]


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def vertical_gradient(accent):
    """四段渐变：近黑顶 → 暗主题 → 主题色 → 提亮主题，纵向更有层次"""
    deep = lerp((6, 8, 12), accent, 0.10)     # 顶部近黑（带主题色相）
    dark = lerp((6, 8, 12), accent, 0.34)     # 中暗
    mid = lerp((6, 8, 12), accent, 0.72)      # 主题
    lit = lerp(accent, (255, 255, 255), 0.18)  # 底部提亮
    stops = [(0.0, deep), (0.42, dark), (0.80, mid), (1.0, lit)]

    img = Image.new("RGB", (1, H))
    px = img.load()
    for y in range(H):
        t = y / (H - 1)
        # 定位所在区间
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                k = (t - p0) / (p1 - p0) if p1 > p0 else 0
                px[0, y] = lerp(c0, c1, k)
                break
    return img.resize((W, H), Image.BILINEAR)


def add_grain(img, strength=6):
    """极细颗粒，去掉数码图的塑料感"""
    noise = Image.effect_noise((W, H), 22).convert("L")
    noise_rgb = Image.merge("RGB", (noise, noise, noise))
    return Image.blend(img, noise_rgb, strength / 1000)


def add_glow(img, cxy=(0.52, 0.26), radius=0.62, strength=42):
    """顶部柔光，让封面有光源感（弱一点，别把颜色冲淡）"""
    mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(mask)
    cx, cy = W * cxy[0], H * cxy[1]
    r = max(W, H) * radius
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=strength)
    mask = mask.filter(ImageFilter.GaussianBlur(150))
    light = Image.new("RGB", (W, H), (255, 250, 235))
    return Image.composite(light, img, mask)


def add_vignette(img, inset=(0.07, 0.05)):
    """四周压暗，聚焦中心 —— 书封的高级感主要来自这个"""
    mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse([W * inset[0], H * inset[1],
               W * (1 - inset[0]), H * (1 - inset[1])], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(150))
    dark = Image.new("RGB", (W, H), (0, 0, 0))
    return Image.composite(img, dark, mask)


def draw_spine(img):
    """左侧书脊：暗带 + 高光线"""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    spine_w = 30
    for x in range(spine_w):
        t = x / spine_w
        a = int(110 * (1 - t) + 26)
        d.line([(x, 0), (x, H)], fill=(0, 0, 0, a))
    # 高光线
    d.line([(spine_w + 1, 0), (spine_w + 1, H)], fill=(255, 255, 255, 46), width=1)
    d.line([(spine_w + 3, 0), (spine_w + 3, H)], fill=(255, 255, 255, 18), width=1)
    return Image.alpha_composite(img.convert("RGBA"), ov)


def draw_borders(img):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    m1, m2 = 46, 58
    d.rectangle([m1, m1, W - m1, H - m1], outline=(255, 255, 255, 74), width=3)
    d.rectangle([m2, m2, W - m2, H - m2], outline=(255, 255, 255, 34), width=1)
    # 四角小装饰
    cl = 26
    for (cx, cy, dx, dy) in [(m1, m1, 1, 1), (W - m1, m1, -1, 1),
                             (m1, H - m1, 1, -1), (W - m1, H - m1, -1, -1)]:
        d.line([(cx, cy), (cx + dx * cl, cy + dy * 0)], fill=(GOLD[0], GOLD[1], GOLD[2], 150), width=2)
        d.line([(cx, cy), (cx + dx * 0, cy + dy * cl)], fill=(GOLD[0], GOLD[1], GOLD[2], 150), width=2)
    return Image.alpha_composite(img, ov)


def draw_tracked_text(d, xy, text, font, fill, tracking=8, anchor_center_x=None):
    """手动字间距（PIL 没有 letter-spacing）"""
    widths = [d.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = (anchor_center_x - total / 2) if anchor_center_x is not None else xy[0]
    y = xy[1]
    for ch, w in zip(text, widths):
        d.text((x, y), ch, font=font, fill=fill)
        x += w + tracking


def wrap_title(d, title, font, max_w):
    """按像素宽度贪心断行，尽量均分"""
    lines, cur = [], ""
    for ch in title:
        if d.textlength(cur + ch, font=font) <= max_w or not cur:
            cur += ch
        else:
            lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    # 若末行过短且行数>1，从上一行挪字过去，视觉更均衡
    if len(lines) > 1 and len(lines[-1]) == 1 and len(lines[-2]) > 2:
        lines[-1] = lines[-2][-1] + lines[-1]
        lines[-2] = lines[-2][:-1]
    return lines


def fit_title(d, title, max_w=640):
    """按字数自适应字号：行数越少字越大"""
    n = len(title)
    if n <= 4:
        size = 126
    elif n <= 8:
        size = 96
    elif n <= 12:
        size = 80
    else:
        size = 70
    while size > 40:
        font = ImageFont.truetype(F_TITLE, size, index=0)
        lines = wrap_title(d, title, font, max_w)
        if len(lines) <= 3 and all(d.textlength(l, font=font) <= max_w for l in lines):
            return font, lines, size
        size -= 4
    font = ImageFont.truetype(F_TITLE, 40, index=0)
    return font, wrap_title(d, title, font, max_w), 40


def build_cover(novel):
    title = (novel.get("title") or novel.get("slug") or "Untitled").strip()
    author = (novel.get("author") or "").strip()
    category = (novel.get("category") or "").strip()
    cat_zh = {"Xianxia": "仙侠", "Fantasy": "玄幻", "Urban": "都市",
              "Romance": "言情", "Sci-Fi": "科幻"}.get(category, "小说")
    cat_label = f"{cat_zh} · {category.upper()}" if category else "小说"

    accent = pick_palette(title)

    img = vertical_gradient(accent)
    img = add_glow(img)
    img = add_grain(img)
    img = add_vignette(img)
    img = draw_spine(img)
    img = draw_borders(img)

    # 所有半透明元素必须画在独立图层再一次性合成：
    # ImageDraw 在 RGBA 图上是「替换像素」，不做 alpha 混合，直接画会变实心白。
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    # 背景大号水印字已移除：在 400px 缩略图下几乎不可见，却会和书名/作者抢位显脏。

    # 顶部分类标签
    label_font = ImageFont.truetype(F_UI, 24, index=8)
    draw_tracked_text(d, (0, 132), cat_label, label_font, (255, 255, 255, 200),
                      tracking=6, anchor_center_x=W / 2)
    d.line([(W / 2 - 100, 178), (W / 2 + 100, 178)], fill=(255, 255, 255, 90), width=2)

    # 顶部装饰：菱形 + 两侧短线
    cy = 240
    d.line([(W / 2 - 70, cy), (W / 2 - 22, cy)], fill=(GOLD[0], GOLD[1], GOLD[2], 170), width=2)
    d.line([(W / 2 + 22, cy), (W / 2 + 70, cy)], fill=(GOLD[0], GOLD[1], GOLD[2], 170), width=2)
    d.polygon([(W / 2, cy - 9), (W / 2 + 9, cy), (W / 2, cy + 9), (W / 2 - 9, cy)],
              outline=(GOLD[0], GOLD[1], GOLD[2], 200), width=2)

    # 书名（垂直居中于 320~720 区段）
    font, lines, size = fit_title(d, title)
    line_h = int(size * 1.40)
    block_h = line_h * len(lines)
    y0 = int((320 + 720) / 2 - block_h / 2)
    for i, line in enumerate(lines):
        # 文字阴影增加立体感
        d.text((W / 2 + 2, y0 + i * line_h + 3), line, font=font,
               fill=(0, 0, 0, 130), anchor="mt")
        d.text((W / 2, y0 + i * line_h), line, font=font, fill=IVORY, anchor="mt")
    title_bottom = y0 + block_h

    # 分隔线
    dy = min(title_bottom + 60, 900)
    d.line([(W / 2 - 120, dy), (W / 2 + 120, dy)], fill=(255, 255, 255, 80), width=2)
    d.ellipse([W / 2 - 4, dy - 4, W / 2 + 4, dy + 4], fill=(GOLD[0], GOLD[1], GOLD[2], 200))

    # 作者
    if author:
        af = ImageFont.truetype(F_UI, 30, index=5)
        d.text((W / 2, dy + 46), f"作 者　{author}", font=af,
               fill=(255, 255, 255, 215), anchor="mt")

    # 底部站点标
    bf = ImageFont.truetype(F_UI, 24, index=5)
    draw_tracked_text(d, (0, H - 116), "NOVELHUB", bf, (255, 255, 255, 130),
                      tracking=12, anchor_center_x=W / 2)

    # 一次性合成所有半透明图层 → 再转 RGB（避免 alpha 通道被丢弃后变实心）
    img = Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")
    return img


def main():
    with open(NOVELS_JSON, encoding="utf-8") as f:
        novels = json.load(f)
    os.makedirs(COVERS_DIR, exist_ok=True)

    made = 0
    for n in novels:
        slug = n.get("slug")
        if not slug:
            print("!! 跳过无 slug 记录:", n.get("title"))
            continue
        img = build_cover(n)
        out = os.path.join(COVERS_DIR, f"{slug}.jpg")
        img.save(out, "JPEG", quality=90, optimize=True, progressive=True)
        made += 1
        print(f"  ✓ {slug}.jpg  ({os.path.getsize(out)//1024}KB)  {n.get('title')}")
    print(f"\n完成：{made}/{len(novels)} 本 → {COVERS_DIR}")


if __name__ == "__main__":
    main()
