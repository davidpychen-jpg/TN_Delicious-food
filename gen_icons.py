#!/usr/bin/env python3
"""
gen_icons.py
------------
為「府城食記」PWA 產生應用程式圖示 (App Icons)。

用法:
    python3 gen_icons.py

會在 ./icons 資料夾內產生以下檔案:
    icon-72x72.png
    icon-96x96.png
    icon-128x128.png
    icon-144x144.png
    icon-152x152.png
    icon-192x192.png
    icon-384x384.png
    icon-512x512.png
    icon-maskable-192x192.png   (Android 自適應圖示用，含安全邊界)
    icon-maskable-512x512.png
    apple-touch-icon.png        (180x180, iOS 用)
    favicon-32x32.png
    favicon-16x16.png

需求套件: Pillow (PIL)
    pip install Pillow --break-system-packages
"""

import math
import os

from PIL import Image, ImageDraw

# ------------------------------------------------------------------
# 品牌色彩設定 (與 index.html 中 tailwind.config 的 brand / accent 一致)
# ------------------------------------------------------------------
BRAND_DARK = (190, 18, 60)     # #be123c
BRAND = (244, 63, 94)          # #f43f5e
ACCENT = (245, 158, 11)        # #f59e0b
WHITE = (255, 255, 255)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")

# 標準圖示尺寸 (manifest.json 會引用這些檔案)
ICON_SIZES = [72, 96, 128, 144, 152, 192, 384, 512]
MASKABLE_SIZES = [192, 512]
APPLE_TOUCH_SIZE = 180
FAVICON_SIZES = [16, 32]


def lerp_color(c1, c2, t):
    """線性內插兩個 RGB 顏色"""
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def draw_gradient_background(size, corner_radius_ratio=0.22):
    """畫出圓角矩形的品牌漸層背景 (由左上 BRAND 到右下 BRAND_DARK)"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gradient = Image.new("RGB", (size, size), BRAND)
    px = gradient.load()
    for y in range(size):
        for x in range(size):
            t = (x + y) / (2 * size)
            px[x, y] = lerp_color(BRAND, BRAND_DARK, t)

    mask = Image.new("L", (size, size), 0)
    mdraw = ImageDraw.Draw(mask)
    radius = int(size * corner_radius_ratio)
    mdraw.rounded_rectangle([(0, 0), (size - 1, size - 1)], radius=radius, fill=255)

    img.paste(gradient, (0, 0), mask)
    return img


def draw_bowl_icon(img, size):
    """在背景上畫出簡化的「碗+熱氣+湯匙」圖案，呼應『府城食記』美食主題"""
    draw = ImageDraw.Draw(img)
    cx, cy = size / 2, size / 2

    # 碗的尺寸比例
    bowl_w = size * 0.62
    bowl_h = bowl_w * 0.5
    bowl_top = cy + size * 0.02
    bowl_left = cx - bowl_w / 2
    bowl_right = cx + bowl_w / 2
    bowl_bottom = bowl_top + bowl_h

    # 碗身 (下半圓弧 + 底部收窄的梯形效果)
    draw.pieslice(
        [bowl_left, bowl_top - bowl_h / 2, bowl_right, bowl_bottom],
        start=0, end=180, fill=WHITE
    )
    # 讓底部稍微收窄，畫一個梯形蓋掉多餘部分
    foot_w = bowl_w * 0.72
    draw.polygon(
        [
            (bowl_left, bowl_top),
            (bowl_right, bowl_top),
            (cx + foot_w / 2, bowl_bottom),
            (cx - foot_w / 2, bowl_bottom),
        ],
        fill=WHITE,
    )

    # 碗緣 (橢圓)
    rim_h = size * 0.045
    draw.ellipse(
        [bowl_left - size * 0.01, bowl_top - rim_h / 2,
         bowl_right + size * 0.01, bowl_top + rim_h / 2],
        fill=ACCENT
    )

    # 碗腳
    foot_top_w = bowl_w * 0.18
    foot_bottom_w = bowl_w * 0.28
    foot_h = size * 0.06
    draw.polygon(
        [
            (cx - foot_top_w / 2, bowl_bottom - size * 0.01),
            (cx + foot_top_w / 2, bowl_bottom - size * 0.01),
            (cx + foot_bottom_w / 2, bowl_bottom + foot_h),
            (cx - foot_bottom_w / 2, bowl_bottom + foot_h),
        ],
        fill=WHITE,
    )

    # 熱氣蒸汽 (三條波浪線)
    steam_top = bowl_top - size * 0.34
    steam_bottom = bowl_top - size * 0.06
    line_w = max(2, int(size * 0.028))
    offsets = [-bowl_w * 0.22, 0, bowl_w * 0.22]
    for ox in offsets:
        points = []
        steps = 16
        for i in range(steps + 1):
            t = i / steps
            y = steam_bottom + (steam_top - steam_bottom) * t
            x = cx + ox + math.sin(t * math.pi * 2.2) * size * 0.045
            points.append((x, y))
        draw.line(points, fill=WHITE, width=line_w, joint="curve")


def make_icon(size, maskable=False):
    if maskable:
        # maskable 圖示需要保留安全邊界(約 40%)，避免被系統裁切遮罩時切掉重要內容
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        bg = draw_gradient_background(size, corner_radius_ratio=0)  # 滿版背景，無圓角(交給系統遮罩)
        canvas.paste(bg, (0, 0), bg)
        inner_size = int(size * 0.6)
        inner = Image.new("RGBA", (inner_size, inner_size), (0, 0, 0, 0))
        draw_bowl_icon(inner, inner_size)
        offset = (size - inner_size) // 2
        canvas.paste(inner, (offset, offset), inner)
        return canvas
    else:
        img = draw_gradient_background(size)
        draw_bowl_icon(img, size)
        return img


def make_favicon(size):
    img = draw_gradient_background(size, corner_radius_ratio=0.3)
    draw_bowl_icon(img, size)
    return img


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for size in ICON_SIZES:
        icon = make_icon(size)
        path = os.path.join(OUTPUT_DIR, f"icon-{size}x{size}.png")
        icon.save(path, "PNG")
        print(f"已產生: {path}")

    for size in MASKABLE_SIZES:
        icon = make_icon(size, maskable=True)
        path = os.path.join(OUTPUT_DIR, f"icon-maskable-{size}x{size}.png")
        icon.save(path, "PNG")
        print(f"已產生: {path}")

    apple_icon = make_icon(APPLE_TOUCH_SIZE)
    apple_path = os.path.join(OUTPUT_DIR, "apple-touch-icon.png")
    apple_icon.save(apple_path, "PNG")
    print(f"已產生: {apple_path}")

    for size in FAVICON_SIZES:
        fav = make_favicon(size)
        path = os.path.join(OUTPUT_DIR, f"favicon-{size}x{size}.png")
        fav.save(path, "PNG")
        print(f"已產生: {path}")

    print("\n所有圖示已產生完成！請確認 manifest.json 內的路徑與檔名相符。")


if __name__ == "__main__":
    main()
