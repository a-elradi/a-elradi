#!/usr/bin/env python3
"""
Builds every custom animated SVG used by the profile README.

    python scripts/build_assets.py

Outputs go to ./assets (dark + light variants where the background matters).
Design tokens mirror aelradi.engineer: near-black surfaces, emerald accent.
Animations are pure CSS/SMIL inside the SVG so they run when GitHub renders
the file through <img> (no JS / external fonts are possible there).
"""
import base64
import io
import math
import pathlib
from string import Template

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
PROJ = ASSETS / "projects"
SRC = PROJ / "src"

SANS = '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif'
MONO = '"JetBrains Mono","Fira Code","Cascadia Code",Consolas,"Courier New",monospace'

THEMES = {
    "dark": dict(bg="#0a0a0a", surface="#111111", surface2="#1c1c1c", border="#262626",
                 text="#ffffff", muted="#9ca3af", dim="#6b7280",
                 accent="#10b981", accent2="#34d399", deep="#064e3b", glow="0.22", glow2="0.48", grid="0.55"),
    "light": dict(bg="#ffffff", surface="#f5f5f5", surface2="#e5e7eb", border="#e5e7eb",
                  text="#111111", muted="#525252", dim="#737373",
                  accent="#059669", accent2="#10b981", deep="#a7f3d0", glow="0.14", glow2="0.30", grid="0.9"),
}

BASE_CSS = Template("""
.sans{font-family:$SANS}
.mono{font-family:$MONO}
.fade{opacity:0;animation:fade .9s ease-out forwards}
.rise{opacity:0;animation:rise .9s cubic-bezier(.22,.7,.3,1) forwards}
@keyframes fade{to{opacity:1}}
@keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes pulse{0%,100%{opacity:.55;transform:scale(1)}50%{opacity:1;transform:scale(1.35)}}
@keyframes glow{0%,100%{opacity:$glow;transform:scale(1)}50%{opacity:$glow2;transform:scale(1.08)}}
@keyframes float{0%,100%{transform:translate(0,0)}25%{transform:translate(-14px,-18px)}50%{transform:translate(10px,-8px)}75%{transform:translate(-8px,14px)}}
@keyframes dash{to{stroke-dashoffset:-40}}
@keyframes shimmer{from{transform:translateX(-1200px)}to{transform:translateX(1200px)}}
@media (prefers-reduced-motion:reduce){*{animation-duration:.01s!important;animation-delay:0s!important;animation-iteration-count:1!important}}
""").safe_substitute(SANS=SANS, MONO=MONO)

DELAYS = "".join(f".d{i}{{animation-delay:{i*0.12:.2f}s}}" for i in range(0, 40))

GRID = '<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" stroke="$border" stroke-width="1"/></pattern>'


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


def svg(w, h, body, css="", defs="", title="", p=None):
    base = Template(BASE_CSS).safe_substitute(p or THEMES["dark"])
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" role="img" aria-label="{esc(title)}">\n'
            f'<title>{esc(title)}</title>\n<style>{base}{DELAYS}{css}</style>\n<defs>{defs}</defs>\n{body}\n</svg>\n')


def write(name, content):
    path = ASSETS / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  wrote {path.relative_to(ROOT)}  ({len(content.encode())/1024:.1f} KB)")


def both(builder, name):
    for theme, p in THEMES.items():
        write(f"{name}-{theme}.svg", builder(p, theme))


# ----------------------------------------------------------------------------
# HERO
# ----------------------------------------------------------------------------
def hero(p, theme):
    W, H = 1200, 440
    tagline = "> building autonomous systems that see, decide and act"
    tl_w = len(tagline) * 9.0  # 15px mono ~ 0.6em
    im = Image.open(SRC / "profile.png").convert("RGB").resize((440, 440), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=86, optimize=True)
    photo = base64.b64encode(buf.getvalue()).decode()
    sat_body = ""
    for label, ang in [("CV", 0), ("AI", 90), ("ROS 2", 180), ("IoT", 270)]:
        x = 150 * math.cos(math.radians(ang)); y = 150 * math.sin(math.radians(ang))
        w = len(label) * 8 + 22
        sat_body += (f'<g transform="translate({x:.1f},{y:.1f})"><g class="counter">'
                     f'<rect x="{-w/2}" y="-12" width="{w}" height="24" rx="12" fill="$surface" stroke="$border"/>'
                     f'<text class="mono" x="0" y="4" text-anchor="middle" font-size="11" font-weight="700" fill="$accent2" letter-spacing="1">{label}</text>'
                     f'</g></g>')
    body = Template(f"""
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="$bg"/>
  <rect width="{W}" height="{H}" fill="url(#grid)" opacity="$grid"/>
  <circle class="orb1" cx="900" cy="110" r="170" fill="$accent" opacity="$glow" filter="url(#blur)"/>
  <circle class="orb2" cx="1080" cy="380" r="130" fill="$accent2" opacity="$glow" filter="url(#blur)"/>
  <circle class="orb3" cx="180" cy="420" r="120" fill="$accent" opacity="$glow" filter="url(#blur)"/>

  <text class="sans fade d1" x="72" y="92" font-size="12" font-weight="800" letter-spacing="4.5" fill="$accent">INFORMATICS ENGINEER · AI AUTOMATION ENGINEER</text>
  <text class="sans rise d2" x="68" y="184" font-size="92" font-weight="900" letter-spacing="-3" fill="$text">ABDALLA</text>
  <text class="sans rise d4" x="68" y="270" font-size="92" font-weight="900" letter-spacing="-3" fill="$text">ELRADI</text>
  <text class="sans fade d6" x="72" y="311" font-size="21" font-weight="500" fill="$muted">AI · Computer Vision · Robotics · IoT</text>

  <g clip-path="url(#typeclip)">
    <text class="mono" x="72" y="352" font-size="15" fill="$accent2" textLength="{tl_w:.0f}" lengthAdjust="spacingAndGlyphs">{esc(tagline)}</text>
  </g>
  <rect class="cursor" x="72" y="339" width="9" height="17" fill="$accent2"/>

  <g class="fade d9">
    <rect x="72" y="378" width="196" height="30" rx="15" fill="$surface" stroke="$border"/>
    <circle cx="92" cy="393" r="4" fill="$accent"><animate attributeName="opacity" values="1;.3;1" dur="1.8s" repeatCount="indefinite"/></circle>
    <circle cx="92" cy="393" r="4" class="ping" stroke="$accent" stroke-width="1.5"/>
    <text class="sans" x="104" y="397" font-size="12" font-weight="600" fill="$text">Open to opportunities</text>
  </g>
  <g class="fade d10">
    <rect x="280" y="378" width="268" height="30" rx="15" fill="$surface" stroke="$border"/>
    <path d="M296 398c-3-3.5-6-7-6-10a6 6 0 0 1 12 0c0 3-3 6.5-6 10z" stroke="$accent" stroke-width="1.6"/>
    <text class="sans" x="310" y="397" font-size="12" font-weight="600" fill="$text">Manama, Bahrain</text>
    <text class="mono" x="430" y="397" font-size="11" fill="$muted">26.22°N 50.58°E</text>
  </g>

  <g transform="translate(960,220)">
    <circle class="glow" r="120" fill="$accent" opacity="$glow" filter="url(#blur2)"/>
    <circle class="ring1" r="150" stroke="$border" stroke-width="1.2" stroke-dasharray="3 9"/>
    <circle class="ring2" r="192" stroke="$border" stroke-width="1" stroke-dasharray="2 16" opacity=".8"/>
    <g class="ring1">{sat_body}</g>
    <circle r="105" fill="$surface" stroke="$accent" stroke-width="2"/>
    <g clip-path="url(#orbclip)">
      <image href="data:image/jpeg;base64,{photo}" x="-100" y="-100" width="200" height="200" preserveAspectRatio="xMidYMid slice"/>
      <rect class="scan" x="-100" y="-1" width="200" height="3" fill="url(#scan)" opacity=".7"/>
    </g>
    <circle r="100" stroke="$text" stroke-opacity=".18"/>
    <text class="mono" x="0" y="218" text-anchor="middle" font-size="11" fill="$dim" letter-spacing="2">vision.scan()  ·  nav2.plan()  ·  agent.act()</text>
  </g>

  <text class="mono fade d12" x="{W-40}" y="{H-22}" text-anchor="end" font-size="12" fill="$dim">aelradi.engineer</text>
  <rect class="bline" x="0" y="{H-4}" width="{W}" height="4" fill="url(#line)"/>
</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="28" stroke="$border"/>
""").safe_substitute(p)
    defs = Template(f"""
<clipPath id="frame"><rect width="{W}" height="{H}" rx="28"/></clipPath>
<clipPath id="typeclip"><rect class="typew" x="72" y="336" width="{tl_w+4:.0f}" height="24"/></clipPath>
<clipPath id="orbclip"><circle r="100"/></clipPath>
{GRID}
<linearGradient id="scan" x1="0" x2="1"><stop offset="0" stop-color="$accent2" stop-opacity="0"/><stop offset=".5" stop-color="#ffffff" stop-opacity=".9"/><stop offset="1" stop-color="$accent2" stop-opacity="0"/></linearGradient>
<linearGradient id="line" x1="0" x2="1"><stop offset="0" stop-color="$accent" stop-opacity="0"/><stop offset=".3" stop-color="$accent"/><stop offset=".7" stop-color="$accent2"/><stop offset="1" stop-color="$accent" stop-opacity="0"/></linearGradient>
<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="55"/></filter>
<filter id="blur2" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="30"/></filter>
""").safe_substitute(p)
    css = """
.orb1{animation:float 11s ease-in-out infinite}
.orb2{animation:float 13s ease-in-out infinite reverse}
.orb3{animation:float 15s ease-in-out infinite}
.glow{animation:glow 4s ease-in-out infinite}
.ring1{animation:spin 48s linear infinite}
.ring2{animation:spin 80s linear infinite reverse}
.counter{animation:spin 48s linear infinite reverse}
.ping{animation:pulse 1.8s ease-out infinite;transform-origin:92px 393px}
.typew{transform-origin:72px 0;transform:scaleX(0);animation:typew 2.6s steps({len(tagline)},end) 1.1s forwards}
@keyframes typew{to{transform:scaleX(1)}}
.cursor{animation:cur 2.6s steps({len(tagline)},end) 1.1s forwards,blink 1s step-end infinite}
@keyframes cur{to{transform:translateX({tl_w:.0f}px)}}
@keyframes blink{50%{opacity:0}}
.scan{animation:scan 5s ease-in-out infinite}
@keyframes scan{0%,100%{transform:translateY(-98px)}50%{transform:translateY(98px)}}
.bline{transform-origin:0 0;transform:scaleX(0);animation:grow 1.8s cubic-bezier(.22,.7,.3,1) .3s forwards}
@keyframes grow{to{transform:scaleX(1)}}
"""
    return svg(W, H, body, css, defs, "Abdalla Elradi — AI, Computer Vision & Robotics Engineer", p)


# ----------------------------------------------------------------------------
# TERMINAL CARD
# ----------------------------------------------------------------------------
def terminal(p, theme):
    W, H = 620, 340
    cmd = "abdalla --about"
    cmd_w = len(cmd) * 8.4  # 14px mono
    lines = [
        [("{", "punc")],
        [('  "name"', "key"), (":      ", "punc"), ('"Abdalla Elradi"', "str"), (",", "punc")],
        [('  "role"', "key"), (":      ", "punc"), ('"AI Automation Engineer @ Glam Moda WLL"', "str"), (",", "punc")],
        [('  "study"', "key"), (":     ", "punc"), ('"Informatics Engineering · UTB · senior year"', "str"), (",", "punc")],
        [('  "focus"', "key"), (":     ", "punc"), ("[", "punc"), ('"Computer Vision"', "str"), (", ", "punc"), ('"Robotics"', "str"), (", ", "punc"), ('"AI Agents"', "str"), ("]", "punc"), (",", "punc")],
        [('  "building"', "key"), (":  ", "punc"), ('"AMR warehouse robot · ROS 2 + Jetson Orin"', "str"), (",", "punc")],
        [('  "leads"', "key"), (":     ", "punc"), ('"UTB IoT Club · 150+ members"', "str"), (",", "punc")],
        [('  "motto"', "key"), (":     ", "punc"), ('"Build with purpose. Lead with vision."', "str")],
        [("}", "punc")],
    ]
    color = {"key": "$accent2", "str": "$text", "punc": "$dim"}
    y0 = 108
    out = ""
    for i, segs in enumerate(lines):
        y = y0 + i * 22
        spans = "".join(f'<tspan fill="{color[k]}">{esc(t)}</tspan>' for t, k in segs)
        out += f'<text class="mono fade" style="animation-delay:{3.0 + i*0.16:.2f}s" x="28" y="{y}" font-size="13" xml:space="preserve">{spans}</text>\n'
    last_y = y0 + len(lines) * 22 + 8
    end_d = 3.0 + len(lines) * 0.16 + .3
    body = Template(f"""
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="20" fill="$surface" stroke="$border"/>
<rect x="1" y="1" width="{W-2}" height="40" rx="19" fill="$surface2"/>
<rect x="1" y="30" width="{W-2}" height="12" fill="$surface2"/>
<circle cx="24" cy="21" r="6" fill="#ff5f57"/><circle cx="44" cy="21" r="6" fill="#febc2e"/><circle cx="64" cy="21" r="6" fill="#28c840"/>
<text class="mono" x="{W/2}" y="25" text-anchor="middle" font-size="12" fill="$muted">abdalla@bahrain:~</text>

<text class="mono" x="28" y="78" font-size="14" fill="$accent" font-weight="700">$$</text>
<g clip-path="url(#cmdclip)"><text class="mono" x="44" y="78" font-size="14" fill="$text" textLength="{cmd_w:.0f}" lengthAdjust="spacingAndGlyphs">{cmd}</text></g>
<rect class="cursor" x="44" y="65" width="8" height="16" fill="$accent2"/>
{out}
<text class="mono fade" style="animation-delay:{end_d:.2f}s" x="28" y="{last_y}" font-size="14" fill="$accent" font-weight="700">$$</text>
<rect class="fade" style="animation-delay:{end_d:.2f}s" x="44" y="{last_y-13}" width="8" height="16" fill="$accent2">
  <animate attributeName="opacity" values="1;0;1" dur="1s" begin="{end_d+.6:.2f}s" repeatCount="indefinite"/>
</rect>
""").safe_substitute(p)
    defs = f'<clipPath id="cmdclip"><rect class="typew" x="44" y="62" width="{cmd_w+4:.0f}" height="22"/></clipPath>'
    css = (f".typew{{transform-origin:44px 0;transform:scaleX(0);animation:typew 1.6s steps({len(cmd)},end) .6s forwards}}"
           f"@keyframes typew{{to{{transform:scaleX(1)}}}}"
           f".cursor{{animation:cur 1.6s steps({len(cmd)},end) .6s forwards,blink 1s step-end infinite,hide .1s 2.9s forwards}}"
           f"@keyframes cur{{to{{transform:translateX({cmd_w:.0f}px)}}}}@keyframes blink{{50%{{opacity:0}}}}@keyframes hide{{to{{opacity:0}}}}")
    return svg(W, H, body, css, defs, "Terminal card: abdalla --about", p)


# ----------------------------------------------------------------------------
# SKILLS TICKER
# ----------------------------------------------------------------------------
def ticker(p, theme):
    W, H = 1200, 46
    items = ["PYTHON", "C++", "ROS 2", "OPENCV", "YOLO", "TENSORFLOW", "MINDSPORE", "MEDIAPIPE", "JETSON ORIN",
             "ESP32", "ARDUINO", "TEENSY", "MQTT", "MICRO-ROS", "NAV2 · SLAM", "NEXT.JS", "REACT", "TAILWIND",
             "FLASK", "SHOPIFY API", "WHATSAPP API", "INSTAGRAM GRAPH", "TELEGRAM BOTS", "LOCAL LLMs", "N8N",
             "DOCKER", "LINUX", "GIT", "FIGMA"]
    adv = 13 * 0.62 + 3.2  # 13px mono + letter-spacing
    gap = 34
    x = 0.0
    parts = ""
    for it in items:
        tw = len(it) * adv
        parts += (f'<text class="mono" x="{x:.1f}" y="29" font-size="13" font-weight="700" letter-spacing="3.2" fill="$text" '
                  f'textLength="{tw:.0f}" lengthAdjust="spacingAndGlyphs">{esc(it)}</text>')
        x += tw + gap / 2
        parts += f'<circle cx="{x:.1f}" cy="24" r="2.5" fill="$accent"/>'
        x += gap / 2
    total = x
    body = Template(f"""
<rect width="{W}" height="{H}" rx="23" fill="$surface"/>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="22.5" stroke="$border"/>
<g mask="url(#fadeMask)">
  <g class="marq"><g>{parts}</g><g transform="translate({total:.1f},0)">{parts}</g></g>
</g>
""").safe_substitute(p)
    defs = (f'<linearGradient id="fadeG" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".08" stop-color="#fff"/>'
            f'<stop offset=".92" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<mask id="fadeMask"><rect width="{W}" height="{H}" fill="url(#fadeG)"/></mask>')
    css = f".marq{{animation:marq {total/55:.1f}s linear infinite}}@keyframes marq{{to{{transform:translateX(-{total:.1f}px)}}}}"
    return svg(W, H, body, css, defs, "Skills ticker", p)


# ----------------------------------------------------------------------------
# WAZIR ARCHITECTURE
# ----------------------------------------------------------------------------
def wazir(p, theme):
    W, H = 1100, 470
    specialists = ["Automation & System Health", "Support Memory", "Market Intelligence", "SEO & Content",
                   "Technical QA", "Shopping Experience", "Sales & Retention", "Google Ads"]
    cx, cy = 550, 235
    nodes = links = packets = ""
    centers = [(150, 69), (416, 69), (683, 69), (950, 69), (150, 401), (416, 401), (683, 401), (950, 401)]
    for i, (name, (nx, ny)) in enumerate(zip(specialists, centers)):
        nodes += f"""
<g class="rise" style="animation-delay:{.5+i*.1:.2f}s">
  <rect x="{nx-110}" y="{ny-29}" width="220" height="58" rx="14" fill="$surface" stroke="$border"/>
  <rect x="{nx-110}" y="{ny-29}" width="4" height="58" rx="2" fill="$accent" opacity=".9"/>
  <text class="sans" x="{nx-92}" y="{ny-3}" font-size="13" font-weight="700" fill="$text">{esc(name)}</text>
  <text class="mono" x="{nx-92}" y="{ny+16}" font-size="10" fill="$dim" letter-spacing="1.5">SPECIALIST 0{i+1}</text>
</g>"""
        ey = ny + 29 if ny < cy else ny - 29
        sy = cy - 44 if ny < cy else cy + 44
        d = f"M{cx},{sy} C{cx},{(sy+ey)/2} {nx},{(sy+ey)/2} {nx},{ey}"
        links += f'<path class="flow" d="{d}" stroke="$border" stroke-width="1.5" stroke-dasharray="6 8"/>'
        packets += (f'<circle r="3.5" fill="$accent2"><animateMotion dur="{2.2 + (i % 4) * 0.35:.2f}s" begin="{i*0.3:.1f}s" '
                    f'repeatCount="indefinite" path="{d}"/></circle>')
    body = Template(f"""
<rect width="{W}" height="{H}" rx="24" fill="$bg"/>
<rect width="{W}" height="{H}" rx="24" fill="url(#grid)" opacity="$grid"/>
{links}
<path class="flow" d="M240,235 H440" stroke="#f59e0b" stroke-opacity=".6" stroke-width="1.5" stroke-dasharray="6 8"/>
<path class="flow" d="M660,235 H860" stroke="$border" stroke-width="1.5" stroke-dasharray="6 8"/>
{packets}
<circle r="3.5" fill="#f59e0b"><animateMotion dur="2.6s" repeatCount="indefinite" path="M240,235 H440"/></circle>
<circle r="3.5" fill="$accent2"><animateMotion dur="2.4s" repeatCount="indefinite" path="M660,235 H860"/></circle>

<g class="rise d2">
  <rect x="440" y="191" width="220" height="88" rx="18" fill="$surface" stroke="$accent" stroke-width="1.5"/>
  <rect class="glowbox" x="440" y="191" width="220" height="88" rx="18" stroke="$accent" stroke-width="6" stroke-opacity=".25"/>
  <text class="sans" x="550" y="222" text-anchor="middle" font-size="22" font-weight="900" letter-spacing="3" fill="$text">WAZIR</text>
  <text class="mono" x="550" y="241" text-anchor="middle" font-size="10" letter-spacing="2" fill="$accent2">SUPERVISOR AGENT</text>
  <rect x="462" y="254" width="58" height="6" rx="3" fill="$dim"/><rect x="522" y="254" width="58" height="6" rx="3" fill="#f59e0b"/><rect x="582" y="254" width="56" height="6" rx="3" fill="$accent"/>
  <text class="mono" x="462" y="272" font-size="8.5" fill="$dim" letter-spacing="1">READ</text>
  <text class="mono" x="551" y="272" text-anchor="middle" font-size="8.5" fill="#f59e0b" letter-spacing="1">RECOMMEND</text>
  <text class="mono" x="638" y="272" text-anchor="end" font-size="8.5" fill="$accent" letter-spacing="1">EXECUTE</text>
</g>

<g class="rise d3">
  <rect x="40" y="206" width="200" height="58" rx="14" fill="$surface" stroke="#f59e0b" stroke-opacity=".7"/>
  <circle cx="64" cy="235" r="7" fill="#f59e0b"/><circle class="killping" cx="64" cy="235" r="7" stroke="#f59e0b" stroke-width="2"/>
  <text class="sans" x="82" y="232" font-size="13" font-weight="700" fill="$text">Telegram kill switch</text>
  <text class="mono" x="82" y="250" font-size="10" fill="$muted">/pause  /resume  /status</text>
</g>

<g class="rise d4">
  <rect x="860" y="194" width="200" height="82" rx="14" fill="$surface" stroke="$border"/>
  <text class="sans" x="878" y="218" font-size="13" font-weight="700" fill="$text">Audit trail</text>
  <text class="mono" x="878" y="236" font-size="10" fill="$muted">trigger → decision → approval</text>
  <text class="mono" x="878" y="250" font-size="10" fill="$muted">→ result</text>
  <text class="sans" x="878" y="268" font-size="11" font-weight="600" fill="$accent2">Live ops dashboard</text>
</g>

<text class="mono" x="40" y="{H-16}" font-size="10" fill="$dim" letter-spacing="2">9 AGENTS · 3-TIER PERMISSIONS · 3 REGIONAL SHOPIFY STORES · LIVE IN PRODUCTION</text>
<text class="mono" x="{W-40}" y="{H-16}" text-anchor="end" font-size="10" fill="$dim">custom automation engine</text>
{nodes}
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="24" stroke="$border"/>
""").safe_substitute(p)
    defs = Template(GRID).safe_substitute(p)
    css = """
.flow{animation:dash 1.6s linear infinite}
.glowbox{animation:gb 3s ease-in-out infinite}
@keyframes gb{0%,100%{stroke-opacity:.12}50%{stroke-opacity:.4}}
.killping{animation:kp 1.6s ease-out infinite;transform-origin:64px 235px}
@keyframes kp{0%{transform:scale(1);opacity:.9}100%{transform:scale(2.6);opacity:0}}
"""
    return svg(W, H, body, css, defs, "WAZIR multi-agent architecture", p)


# ----------------------------------------------------------------------------
# AMR VISION → NAVIGATION PIPELINE
# ----------------------------------------------------------------------------
def amr_pipeline(p, theme):
    W, H = 1100, 250
    steps = [("Orbbec Astra Pro", "RGB + depth stream"), ("Detection", "OpenCV · pyzbar · YOLO"),
             ("amr_vision", "ROS 2 node · Python"), ("/qr_detection", "verify shelf · publish"),
             ("Nav2 · SLAM", "Jetson Orin Nano"), ("Teensy 4.1", "micro-ROS · motors · lift")]
    nw, gap, y, nh = 160, 28, 118, 64
    x0 = (W - (len(steps) * nw + (len(steps) - 1) * gap)) / 2
    nodes = links = packets = ""
    for i, (a, b) in enumerate(steps):
        x = x0 + i * (nw + gap)
        hi = i in (1, 2, 3)
        stroke = "$accent" if hi else "$border"
        nodes += f"""
<g class="rise" style="animation-delay:{.3+i*.12:.2f}s">
  <rect x="{x}" y="{y}" width="{nw}" height="{nh}" rx="14" fill="$surface" stroke="{stroke}" stroke-opacity="{'.8' if hi else '1'}"/>
  <text class="sans" x="{x+nw/2}" y="{y+28}" text-anchor="middle" font-size="13" font-weight="800" fill="$text">{esc(a)}</text>
  <text class="mono" x="{x+nw/2}" y="{y+46}" text-anchor="middle" font-size="10" fill="$muted">{esc(b)}</text>
</g>"""
        if i < len(steps) - 1:
            d = f"M{x+nw},{y+nh/2} H{x+nw+gap}"
            links += f'<path class="flow" d="{d}" stroke="$accent" stroke-opacity=".7" stroke-width="1.5" stroke-dasharray="4 6"/>'
            packets += f'<circle r="3" fill="$accent2"><animateMotion dur="1.1s" begin="{i*0.18:.2f}s" repeatCount="indefinite" path="{d}"/></circle>'
    dx = x0 + 4 * (nw + gap) + nw / 2
    dash = f"""
<g class="rise d9">
  <rect x="{dx-110}" y="22" width="220" height="48" rx="12" fill="$surface" stroke="$border"/>
  <text class="sans" x="{dx}" y="42" text-anchor="middle" font-size="12" font-weight="800" fill="$text">Flask dashboard · MQTT bridge</text>
  <text class="mono" x="{dx}" y="59" text-anchor="middle" font-size="10" fill="$muted">mission orders → ROS 2 topics</text>
</g>
<path class="flow" d="M{dx},70 V{y}" stroke="$accent" stroke-opacity=".7" stroke-width="1.5" stroke-dasharray="4 6"/>
<circle r="3" fill="$accent2"><animateMotion dur="1.3s" repeatCount="indefinite" path="M{dx},70 V{y}"/></circle>
"""
    hl_x = x0 + (nw + gap)
    hl_w = 3 * nw + 2 * gap
    body = Template(f"""
<rect width="{W}" height="{H}" rx="24" fill="$bg"/>
<rect width="{W}" height="{H}" rx="24" fill="url(#grid)" opacity="$grid"/>
<rect x="{hl_x-12}" y="{y-14}" width="{hl_w+24}" height="{nh+28}" rx="20" stroke="$accent" stroke-opacity=".35" stroke-dasharray="4 6"/>
<text class="mono" x="{hl_x-12}" y="{y-22}" font-size="10" fill="$accent" letter-spacing="2">MY PART — VISION PIPELINE + WEB GUI / MQTT BRIDGE</text>
{links}
{packets}
{dash}
{nodes}
<text class="mono" x="{W/2}" y="{H-20}" text-anchor="middle" font-size="10" fill="$dim" letter-spacing="2">ROS 2 HUMBLE · JETSON ORIN NANO 8 GB · RPLIDAR C1 · BNO055 IMU · PHARMACEUTICAL WAREHOUSE PICKING</text>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="24" stroke="$border"/>
""").safe_substitute(p)
    defs = Template(GRID).safe_substitute(p)
    css = ".flow{animation:dash 1.2s linear infinite}"
    return svg(W, H, body, css, defs, "AMR warehouse robot — vision to navigation pipeline", p)


# ----------------------------------------------------------------------------
# EXPERIENCE TIMELINE
# ----------------------------------------------------------------------------
def timeline(p, theme):
    W, H = 1100, 330
    ly = 172
    entries = [
        (150, "2023 — PRESENT", ("President & Founder", "UTB IoT Club · 150+ members"), ("Robotics & IoT Instructor", "UTB · mentored 40+ students"), "up"),
        (430, "OCT 2024 — JAN 2026", ("IT Technical Support", "& Web Developer · Glam Moda"), None, "down"),
        (720, "APR 2026 — NOW", ("AI Automation Engineer", "Glam Moda WLL · AI agents in production"), None, "up"),
        (950, "2026 — CAPSTONE", ("AMR Warehouse Robot", "Vision · Web GUI · MQTT bridge"), None, "down"),
    ]
    items = ""
    for i, (x, date, t1, t2, side) in enumerate(entries):
        now = i == 2
        nxt = i == 3
        dasher = 'stroke-dasharray="3 3"' if nxt else ""
        node = f'<circle cx="{x}" cy="{ly}" r="9" fill="{"$accent" if now else "$surface"}" stroke="$accent" stroke-width="2" {dasher}/>'
        if now:
            node += f'<circle class="nowping" cx="{x}" cy="{ly}" r="9" stroke="$accent" stroke-width="2"/>'
        if side == "up":
            stem = f'<path d="M{x},{ly-12} V{ly-30}" stroke="$border" stroke-width="1.5"/>'
            ys = (ly - 92, ly - 70, ly - 52)
        else:
            stem = f'<path d="M{x},{ly+12} V{ly+30}" stroke="$border" stroke-width="1.5"/>'
            ys = (ly + 56, ly + 78, ly + 96)
        txt = (f'<text class="mono" x="{x}" y="{ys[0]}" text-anchor="middle" font-size="10" letter-spacing="2" fill="$accent">{date}</text>'
               f'<text class="sans" x="{x}" y="{ys[1]}" text-anchor="middle" font-size="16" font-weight="800" fill="$text">{esc(t1[0])}</text>'
               f'<text class="sans" x="{x}" y="{ys[2]}" text-anchor="middle" font-size="12" fill="$muted">{esc(t1[1])}</text>')
        if t2:
            txt += (f'<path d="M{x},{ly+12} V{ly+30}" stroke="$border" stroke-width="1.5"/>'
                    f'<text class="sans" x="{x}" y="{ly+62}" text-anchor="middle" font-size="16" font-weight="800" fill="$text">{esc(t2[0])}</text>'
                    f'<text class="sans" x="{x}" y="{ly+80}" text-anchor="middle" font-size="12" fill="$muted">{esc(t2[1])}</text>')
        items += f'<g class="rise" style="animation-delay:{.9+i*.35:.2f}s">{stem}{node}{txt}</g>'
    body = Template(f"""
<rect width="{W}" height="{H}" rx="24" fill="$bg"/>
<rect width="{W}" height="{H}" rx="24" fill="url(#grid)" opacity="$grid"/>
<path d="M60,{ly} H1040" stroke="$border" stroke-width="2"/>
<path class="draw" d="M60,{ly} H1040" stroke="url(#tl)" stroke-width="2" stroke-dasharray="980" stroke-dashoffset="980"/>
{items}
<text class="mono" x="{W-40}" y="{H-16}" text-anchor="end" font-size="10" fill="$dim" letter-spacing="2">UNIVERSITY OF TECHNOLOGY BAHRAIN · INFORMATICS ENGINEERING</text>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="24" stroke="$border"/>
""").safe_substitute(p)
    defs = Template(GRID + '<linearGradient id="tl" x1="0" x2="1"><stop offset="0" stop-color="$accent" stop-opacity=".2"/><stop offset=".7" stop-color="$accent"/><stop offset="1" stop-color="$accent2"/></linearGradient>').safe_substitute(p)
    css = (".nowping{animation:np 2s ease-out infinite;transform-origin:720px 172px}@keyframes np{0%{transform:scale(1);opacity:.9}100%{transform:scale(2.8);opacity:0}}"
           ".draw{animation:draw 2.2s cubic-bezier(.22,.7,.3,1) forwards}@keyframes draw{to{stroke-dashoffset:0}}")
    return svg(W, H, body, css, defs, "Experience timeline", p)


# ----------------------------------------------------------------------------
# STAT TILES
# ----------------------------------------------------------------------------
def stats(p, theme):
    W, H = 1100, 150
    tiles = [("TOP 5", "National finalist", "Huawei ICT Competition"),
             ("1st", "Winner", "University Sumo Robot"),
             ("150+", "Members led", "UTB IoT Club · founder"),
             ("40+", "Students mentored", "Robotics & IoT workshops"),
             ("1.5+ yrs", "Professional", "AI automation · web · IT"),
             ("18", "Certificates", "AI · networks · IoT · cloud")]
    n = len(tiles); gap = 16; tw = (W - gap * (n - 1)) / n
    body = ""
    for i, (big, cap, sub) in enumerate(tiles):
        x = i * (tw + gap)
        fs = 34 if len(big) <= 4 else 26
        body += f"""
<g class="rise" style="animation-delay:{.2+i*.12:.2f}s">
  <rect x="{x+.5}" y=".5" width="{tw-1}" height="{H-1}" rx="20" fill="$surface" stroke="$border"/>
  <rect x="{x+22}" y="0" width="{tw-44}" height="2" fill="url(#top)"/>
  <text class="sans" x="{x+22}" y="62" font-size="{fs}" font-weight="900" letter-spacing="-1" fill="$accent2">{big}</text>
  <text class="sans" x="{x+22}" y="92" font-size="13" font-weight="700" fill="$text">{cap}</text>
  <text class="sans" x="{x+22}" y="112" font-size="11" fill="$muted">{esc(sub)}</text>
</g>"""
    body = Template(body).safe_substitute(p)
    defs = Template('<linearGradient id="top" x1="0" x2="1"><stop offset="0" stop-color="$accent" stop-opacity="0"/><stop offset=".5" stop-color="$accent"/><stop offset="1" stop-color="$accent" stop-opacity="0"/></linearGradient>').safe_substitute(p)
    return svg(W, H, body, "", defs, "Highlights", p)


# ----------------------------------------------------------------------------
# STATUS PILL · DIVIDER · EYEBROW · FOOTER · AVATAR
# ----------------------------------------------------------------------------
def status(p, theme):
    W, H = 820, 48
    body = Template(f"""
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="23.5" fill="$surface" stroke="$border"/>
<circle cx="30" cy="24" r="5" fill="$accent"/><circle class="ping" cx="30" cy="24" r="5" stroke="$accent" stroke-width="2"/>
<text class="mono" x="46" y="28" font-size="11" font-weight="800" letter-spacing="3" fill="$accent">NOW</text>
<text class="sans" x="96" y="29" font-size="14" font-weight="600" fill="$text">AI Automation Engineer @ Glam Moda WLL</text>
<rect x="400" y="14" width="1" height="20" fill="$border"/>
<text class="sans" x="420" y="29" font-size="14" fill="$muted">Senior · Informatics Engineering · UTB</text>
<rect x="690" y="14" width="1" height="20" fill="$border"/>
<text class="sans" x="710" y="29" font-size="13" font-weight="600" fill="$accent2">Open for meetings</text>
""").safe_substitute(p)
    css = ".ping{animation:sp 1.8s ease-out infinite;transform-origin:30px 24px}@keyframes sp{0%{transform:scale(1);opacity:.9}100%{transform:scale(3);opacity:0}}"
    return svg(W, H, body, css, "", "Current status", p)


def divider(p, theme):
    W, H = 1200, 14
    body = Template(f"""
<rect x="0" y="6" width="{W}" height="1" fill="$border"/>
<rect class="sh" x="0" y="5" width="420" height="3" rx="1.5" fill="url(#g)"/>
""").safe_substitute(p)
    defs = Template('<linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="$accent" stop-opacity="0"/><stop offset=".5" stop-color="$accent"/><stop offset="1" stop-color="$accent" stop-opacity="0"/></linearGradient>').safe_substitute(p)
    css = ".sh{animation:shimmer 5s ease-in-out infinite}"
    return svg(W, H, body, css, defs, "divider", p)


def eyebrow(text, p, theme):
    tw = len(text) * 10.6
    W, H = int(tw + 60), 26
    body = Template(f"""
<rect class="eline" x="0" y="12" width="34" height="2" rx="1" fill="$accent"/>
<text class="sans fade d3" x="46" y="18" font-size="11" font-weight="800" letter-spacing="4.5" fill="$accent" textLength="{tw:.0f}" lengthAdjust="spacing">{esc(text)}</text>
""").safe_substitute(p)
    css = ".eline{transform-origin:0 0;transform:scaleX(0);animation:grow .8s cubic-bezier(.22,.7,.3,1) forwards}@keyframes grow{to{transform:scaleX(1)}}"
    return svg(W, H, body, css, "", text, p)


def footer(p, theme):
    W, H = 1200, 260
    body = Template(f"""
<g clip-path="url(#f)">
  <rect width="{W}" height="{H}" fill="$bg"/>
  <rect width="{W}" height="{H}" fill="url(#grid)" opacity="$grid"/>
  <circle class="orb1" cx="200" cy="260" r="200" fill="$accent" opacity="$glow" filter="url(#blur)"/>
  <circle class="orb2" cx="1000" cy="0" r="220" fill="$accent2" opacity="$glow" filter="url(#blur)"/>
  <text class="sans fade d1" x="600" y="70" text-anchor="middle" font-size="11" font-weight="800" letter-spacing="5" fill="$accent">LET'S WORK TOGETHER</text>
  <text class="sans rise d3" x="600" y="128" text-anchor="middle" font-size="46" font-weight="900" letter-spacing="-1.5" fill="$text">Let's build the future together.</text>
  <text class="sans fade d5" x="600" y="164" text-anchor="middle" font-size="16" fill="$muted">Open to opportunities in AI, computer vision, robotics, and education-community collaborations.</text>
  <text class="mono fade d7" x="600" y="212" text-anchor="middle" font-size="12" letter-spacing="2" fill="$accent2">"Build with purpose. Lead with vision."</text>
  <path class="wave" d="M0,236 C150,216 250,256 400,236 S650,216 800,236 S1050,256 1200,236 S1450,216 1600,236 S1850,256 2000,236 S2250,216 2400,236 V260 H0 Z" fill="$accent" opacity=".25"/>
  <path class="wave2" d="M0,244 C150,228 250,260 400,244 S650,228 800,244 S1050,260 1200,244 S1450,228 1600,244 S1850,260 2000,244 S2250,228 2400,244 V260 H0 Z" fill="$accent2" opacity=".35"/>
</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="28" stroke="$border"/>
""").safe_substitute(p)
    defs = Template(f'<clipPath id="f"><rect width="{W}" height="{H}" rx="28"/></clipPath>{GRID}'
                    '<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="60"/></filter>').safe_substitute(p)
    css = """
.orb1{animation:float 12s ease-in-out infinite}.orb2{animation:float 14s ease-in-out infinite reverse}
.wave{animation:wv 9s linear infinite}.wave2{animation:wv 6s linear infinite}
@keyframes wv{to{transform:translateX(-800px)}}
"""
    return svg(W, H, body, css, defs, "Let's build the future together", p)


def avatar(p, theme):
    W = H = 320
    img = SRC / "profile.png"
    if not img.exists():
        return svg(W, H, "", "", "", "avatar", p)
    im = Image.open(img).convert("RGB").resize((400, 400), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=85, optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode()
    body = Template(f"""
<g transform="translate(160,160)">
  <circle class="glow" r="130" fill="$accent" opacity="$glow" filter="url(#blur)"/>
  <circle class="ring1" r="148" stroke="$accent" stroke-opacity=".7" stroke-width="1.5" stroke-dasharray="40 18 6 18"/>
  <circle class="ring2" r="136" stroke="$border" stroke-width="1" stroke-dasharray="2 10"/>
  <g clip-path="url(#av)"><image href="data:image/jpeg;base64,{b64}" x="-120" y="-120" width="240" height="240" preserveAspectRatio="xMidYMid slice"/></g>
  <circle r="120" stroke="$text" stroke-opacity=".12" stroke-width="2"/>
  <g class="ring1"><circle cx="0" cy="-148" r="6" fill="$accent2"/></g>
</g>
""").safe_substitute(p)
    defs = '<clipPath id="av"><circle r="120"/></clipPath><filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="30"/></filter>'
    css = ".glow{animation:glow 4s ease-in-out infinite}.ring1{animation:spin 30s linear infinite}.ring2{animation:spin 50s linear infinite reverse}"
    return svg(W, H, body, css, defs, "Abdalla Elradi", p)


# ----------------------------------------------------------------------------
# IMAGE CARDS (project / automation covers)
# ----------------------------------------------------------------------------
def _crop(img_path, w, h, q=80):
    im = Image.open(img_path).convert("RGB")
    sw, sh = im.size
    target = w / h
    if sw / sh > target:
        nw = int(sh * target); im = im.crop(((sw - nw) // 2, 0, (sw - nw) // 2 + nw, sh))
    else:
        nh = int(sw / target); im = im.crop((0, (sh - nh) // 2, sw, (sh - nh) // 2 + nh))
    im = im.resize((w, h), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=q, optimize=True, progressive=True)
    return base64.b64encode(buf.getvalue()).decode()


def card(src, out, w, h, eyebrow_txt, title, tags, badge=None):
    b64 = _crop(SRC / src, w, h)
    fs = 44 if len(title) <= 22 else 36
    ty = h - 52
    chips = ""
    cx = 44
    for t in tags[:3]:
        cw = len(t) * 7.2 + 26
        chips += (f'<rect x="{cx:.0f}" y="{ty-96}" width="{cw:.0f}" height="26" rx="13" fill="#000" fill-opacity=".45" stroke="#fff" stroke-opacity=".18"/>'
                  f'<text class="mono" x="{cx+cw/2:.0f}" y="{ty-79}" text-anchor="middle" font-size="11" font-weight="700" letter-spacing="1" fill="#e5e7eb">{esc(t)}</text>')
        cx += cw + 8
    badge_svg = ""
    if badge:
        bw = len(badge) * 8 + 30
        badge_svg = (f'<rect x="44" y="40" width="{bw:.0f}" height="30" rx="15" fill="#10b981"/>'
                     f'<text class="sans" x="{44+bw/2:.0f}" y="60" text-anchor="middle" font-size="12" font-weight="900" letter-spacing="1.5" fill="#022c22">{badge}</text>')
    body = f"""
<g clip-path="url(#c)">
  <image class="kb" href="data:image/jpeg;base64,{b64}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice"/>
  <rect width="{w}" height="{h}" fill="url(#g)"/>
  {badge_svg}
  <g class="fade d2">{chips}</g>
  <text class="sans fade d3" x="44" y="{ty-40}" font-size="13" font-weight="800" letter-spacing="4.5" fill="#34d399">{esc(eyebrow_txt)}</text>
  <text class="sans rise d4" x="44" y="{ty}" font-size="{fs}" font-weight="900" letter-spacing="-1" fill="#ffffff">{esc(title)}</text>
  <g transform="translate({w-64},64)" class="fade d6">
    <circle r="24" fill="#000" fill-opacity=".45" stroke="#fff" stroke-opacity=".2"/>
    <path d="M-6 6L6 -6M-3 -6H6V3" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </g>
</g>
<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="39.5" stroke="#ffffff" stroke-opacity=".1"/>
"""
    defs = (f'<clipPath id="c"><rect width="{w}" height="{h}" rx="40"/></clipPath>'
            '<linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset=".3" stop-color="#000" stop-opacity=".05"/><stop offset="1" stop-color="#000" stop-opacity=".9"/></linearGradient>')
    css = f".kb{{transform-origin:{w/2}px {h/2}px;animation:kb 22s ease-in-out infinite alternate}}@keyframes kb{{to{{transform:scale(1.08)}}}}"
    write(f"projects/{out}.svg", svg(w, h, body, css, defs, title, THEMES["dark"]))


PROJECT_CARDS = [
    # (src, out, eyebrow, title, tags, badge)
    ("amr.png", "amr", "02 — ROBOTICS · CAPSTONE 2026", "AMR Warehouse Robot", ["ROS 2", "JETSON ORIN", "OPENCV"], "IN PROGRESS"),
    ("door2door.jpg", "door2door", "01 — FULL-STACK WEB APP", "Door2Door Delivery", ["NEXT.JS 16", "REACT 19", "TAILWIND 4"], "LIVE"),
    ("techtrap.jpg", "techtrap", "03 — AI HEALTHCARE", "TECHTRAP", ["MINDSPORE", "MEDIAPIPE", "OPENCV"], "HUAWEI ICT · TOP 5"),
    ("firex.jpg", "firex", "04 — ROBOTICS", "FireX Robot", ["ESP32", "C++", "MQTT"], None),
    ("vision.jpg", "vision", "05 — COMPUTER VISION", "Astra Pro Vision Lab", ["OPENNI2", "DEPTH", "PYZBAR"], None),
    ("sumo.jpg", "sumo", "06 — COMBAT ROBOTICS", "Sumo Robot", ["ARDUINO", "L298N", "IR REMOTE"], "1ST PLACE"),
    ("robonexus.jpg", "robonexus", "07 — COMBAT ROBOTICS", "Robonexus", ["PCB DESIGN", "EMBEDDED", "MECHANICAL"], "WORLD CHAMPIONSHIP"),
]
SYSTEM_CARDS = [
    ("wazir.jpg", "wazir", "ENTERPRISE AI GOVERNANCE", "WAZIR — Agent Department", ["9 AGENTS", "3-TIER PERMISSIONS", "KILL SWITCH"], "FLAGSHIP"),
    ("instagram.jpg", "instagram", "AI CUSTOMER SERVICE", "Instagram Agent", ["GRAPH API", "LOCAL LLM", "SHOPIFY"], None),
    ("whatsapp.jpg", "whatsapp", "AI CUSTOMER SERVICE", "WhatsApp Agent", ["BUSINESS API", "LOCAL LLM", "SHOPIFY"], None),
    ("email.jpg", "email", "AI CUSTOMER SERVICE", "Email Agent", ["GRAPH API", "LOCAL LLM", "DRAFT-FIRST"], None),
]

EYEBROWS = {"about": "CRAFT & MINDSET", "projects": "PORTFOLIO", "systems": "ENTERPRISE AI SYSTEMS",
            "skills": "TECHNICAL SKILLS", "services": "WHAT I OFFER", "experience": "CAREER",
            "certificates": "CREDENTIALS", "activity": "GITHUB ACTIVITY", "contact": "CONTACT"}


def main():
    ASSETS.mkdir(exist_ok=True)
    print("hero / terminal / ticker / diagrams / timeline / stats / status / divider / footer / avatar")
    both(hero, "hero"); both(terminal, "terminal"); both(ticker, "ticker"); both(wazir, "wazir-arch")
    both(amr_pipeline, "amr-pipeline"); both(timeline, "timeline"); both(stats, "stats"); both(status, "status")
    both(divider, "divider"); both(footer, "footer"); both(avatar, "avatar")
    print("eyebrows")
    for key, text in EYEBROWS.items():
        for theme, p in THEMES.items():
            write(f"eyebrow-{key}-{theme}.svg", eyebrow(text, p, theme))
    print("cards")
    for src, out, eb, title, tags, badge in PROJECT_CARDS:
        card(src, out, 800, 600, eb, title, tags, badge)
    for src, out, eb, title, tags, badge in SYSTEM_CARDS:
        card(src, out, 800, 450, eb, title, tags, badge)
    print("done")


if __name__ == "__main__":
    main()
