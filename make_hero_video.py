#!/usr/bin/env python3
"""DIA 官網首頁 hero 動態背景生成：10s 無縫循環科幻電路動畫（白底淺色版，配黑字）。
輸出 assets/img/hero-loop.mp4（H.264）、hero-loop.webm（VP9），並把首幀覆蓋 hero-bg.webp 作 poster/降級圖。
所有隨時間變化的參數均以 T=10s 為周期（sin/cos 或 mod 1），保證首尾幀銜接無跳變。
依賴：numpy、Pillow、ffmpeg（H.264 + VP9 編碼）。注意：會覆蓋 make_assets.py 生成的 hero-bg.webp。"""
import math, os, random, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'assets', 'img')
W, H = 1920, 1080
T, FPS = 10, 25
N = T * FPS
BRAND = (37, 122, 219)
GLOW_RGB = (37, 122, 219)      # 光暈（白底上用品牌藍）
CORE_RGB = (168, 208, 252)     # 脈衝芯（淺藍，白底可見）

random.seed(20261015)

# ---------------- 靜態底層 ----------------
def build_base():
    base = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(base)
    top, bot = (255, 255, 255), (231, 240, 251)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    # 中心淡藍暈染（減法著色，讓中央略帶藍調）
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r2 = ((xx - W / 2) / (W * 0.42)) ** 2 + ((yy - H * 0.46) / (H * 0.62)) ** 2
    tint = np.exp(-r2 * 2.2)[..., None] * np.array([46, 32, 14], dtype=np.float32)
    arr = np.asarray(base).astype(np.float32) - tint
    base = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    # 網格點陣
    gd = ImageDraw.Draw(base, 'RGBA')
    for gx in range(24, W, 48):
        for gy in range(24, H, 48):
            gd.ellipse([gx - 1, gy - 1, gx + 1, gy + 1], fill=BRAND + (46,))
    return base

# ---------------- 電路走線 ----------------
def gen_traces(count=42):
    traces = []
    for _ in range(count):
        edge = random.randrange(4)
        if edge == 0:
            x, y, a = random.randint(0, W), -12, math.pi / 2
        elif edge == 1:
            x, y, a = random.randint(0, W), H + 12, -math.pi / 2
        elif edge == 2:
            x, y, a = -12, random.randint(0, H), 0
        else:
            x, y, a = W + 12, random.randint(0, H), math.pi
        a += random.uniform(-.35, .35)
        pts = [(x, y)]
        for _ in range(random.randint(2, 4)):
            ln = random.randint(90, 260)
            x, y = x + math.cos(a) * ln, y + math.sin(a) * ln
            pts.append((x, y))
            a += random.choice([-math.pi / 4, 0, math.pi / 4])
        traces.append(pts)
    return traces

def resample(pts, step=2.0):
    """折線等距重採樣，返回 (M,2) 點列，便於按弧長定位脈衝"""
    out = []
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        dist = math.hypot(x1 - x0, y1 - y0)
        n = max(1, int(dist / step))
        for j in range(n):
            t = j / n
            out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    out.append(pts[-1])
    return np.array(out, dtype=np.float32)

TRACES = gen_traces()
PATHS = [resample(p) for p in TRACES]

def build_static_traces():
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for pts in TRACES:
        col = BRAND + (random.randint(95, 155),)
        d.line([(float(x), float(y)) for x, y in pts], fill=col, width=2, joint='curve')
        x, y = pts[-1]
        r = random.randint(4, 7)
        d.ellipse([x - r, y - r, x + r, y + r], outline=BRAND + (175,), width=2)
    return layer.filter(ImageFilter.GaussianBlur(0.5))

# ---------------- 動態元素 ----------------
def glow_sprite(size=96):
    """徑向輝光貼圖（淺藍芯、品牌藍暈），按需在幀內調透明度"""
    s = size
    yy, xx = np.mgrid[0:s, 0:s].astype(np.float32) - s / 2 + .5
    r = np.sqrt(xx ** 2 + yy ** 2) / (s / 2)
    a = np.clip(np.exp(-r ** 2 * 4.5) - 0.011, 0, 1)
    rgb = np.zeros((s, s, 3), np.float32)
    inner = np.clip(1 - r * 2.2, 0, 1)[..., None]
    rgb[:] = np.array(GLOW_RGB, np.float32)[None, None, :] * (1 - inner) + np.array(CORE_RGB, np.float32)[None, None, :] * inner
    out = np.dstack([rgb, a[..., None] * 255]).astype(np.uint8)
    return Image.fromarray(out)

SPRITE = glow_sprite()

PULSES = []   # (path_idx, offset, scale, alpha)
for i in range(30):
    PULSES.append((random.randrange(len(PATHS)), random.random(), random.uniform(.32, .62), random.randint(200, 255)))

PARTICLES = []  # (x, y0, k=向上漂移圈數, r, phase, alpha)
for i in range(70):
    PARTICLES.append((random.uniform(0, W), random.uniform(0, H), random.choice([1, 1, 2]),
                      random.uniform(1.2, 3.2), random.uniform(0, 2 * math.pi), random.randint(70, 160)))

def draw_dynamic(t):
    """t ∈ [0,1) 一個周期內的位置"""
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    # 掃描亮帶（自上而下，極淡藍）
    sy = t * (H + 240) - 120
    band = Image.new('RGBA', (W, 240), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    for i in range(240):
        a = int(20 * math.sin(math.pi * i / 240) ** 2)
        bd.line([(0, i), (W, i)], fill=(110, 165, 240, a))
    layer.alpha_composite(band, (0, int(sy) - 120))
    # 漂移粒子（向上，y 整圈回繞 → 無縫）
    pd = ImageDraw.Draw(layer)
    for x, y0, k, r, ph, al in PARTICLES:
        y = (y0 - k * H * t) % H
        tw = .55 + .45 * math.sin(2 * math.pi * (2 * t) + ph)
        a = int(al * tw)
        pd.ellipse([x - r, y - r, x + r, y + r], fill=(70, 120, 200, a))
    # 沿走線流動的光脈衝（彗星尾）
    for pi, off, sc, al in PULSES:
        path = PATHS[pi]
        m = len(path)
        head = (t + off) % 1.0
        hi = head * (m - 1)
        for j in range(9):
            idx = int(hi - j * 9) % m
            x, y = path[idx]
            fade = (1 - j / 9) ** 1.6
            sp = SPRITE.resize((max(8, int(96 * sc * (1 - j / 14))),) * 2, Image.BILINEAR)
            sa = sp.getchannel('A').point(lambda v: v * al * fade // 255)
            sp.putalpha(sa)
            layer.alpha_composite(sp, (int(x - sp.width / 2), int(y - sp.height / 2)))
    return layer

BASE = build_base()
STATIC = build_static_traces()
BASE = Image.alpha_composite(BASE.convert('RGBA'), STATIC)
# 四周微微提亮，聚焦中央文案區
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
vig = np.clip(((xx - W / 2) / (W * 0.72)) ** 2 + ((yy - H / 2) / (H * 0.72)) ** 2, 0, 1)
arr = np.asarray(BASE).astype(np.float32)
arr[..., :3] += (255 - arr[..., :3]) * (vig[..., None] * 0.55)
BASE = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

def render_pass(args, out_path):
    proc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error',
                             '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-']
                            + args + [out_path], stdin=subprocess.PIPE)
    for f in range(N):
        dyn = draw_dynamic(f / N)
        frame = Image.alpha_composite(BASE, dyn).convert('RGB')
        proc.stdin.write(frame.tobytes())
        if f % 50 == 0:
            print(f'{os.path.basename(out_path)} frame {f}/{N}')
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit(f'ffmpeg failed: {out_path}')
    print(out_path, f'{os.path.getsize(out_path) / 1e6:.1f} MB')

# 首幀作 poster，覆蓋舊靜態 hero-bg.webp
first = Image.alpha_composite(BASE, draw_dynamic(0.0)).convert('RGB')
first.save(os.path.join(OUT, 'hero-bg.webp'), quality=82)
print('hero-bg.webp (poster) done')

render_pass(['-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', '23', '-pix_fmt', 'yuv420p',
             '-movflags', '+faststart'], os.path.join(OUT, 'hero-loop.mp4'))
render_pass(['-an', '-c:v', 'libvpx-vp9', '-crf', '36', '-b:v', '0', '-pix_fmt', 'yuv420p'],
            os.path.join(OUT, 'hero-loop.webm'))
