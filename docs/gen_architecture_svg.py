#!/usr/bin/env python3
"""
Generate a clean, high-resolution System Architecture Block Diagram SVG
for the Direct-Mapped Cache Controller with zero text-line overlaps.
Every label uses background badges (pills) and generous spacing.
"""

def generate_svg(output_path):
    W = 1520
    H = 920

    svg = []
    svg.append(f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{W}" height="{H}" viewBox="0 0 {W} {H}"
     font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif">

  <defs>
    <!-- Arrowhead markers -->
    <marker id="arrow-gray" viewBox="0 0 10 6" refX="9" refY="3"
            markerWidth="8" markerHeight="5" orient="auto-start-reverse" fill="#475569">
      <path d="M0,0 L10,3 L0,6 Z"/>
    </marker>
    <marker id="arrow-blue" viewBox="0 0 10 6" refX="9" refY="3"
            markerWidth="8" markerHeight="5" orient="auto-start-reverse" fill="#2563eb">
      <path d="M0,0 L10,3 L0,6 Z"/>
    </marker>
    <marker id="arrow-green" viewBox="0 0 10 6" refX="9" refY="3"
            markerWidth="8" markerHeight="5" orient="auto-start-reverse" fill="#16a34a">
      <path d="M0,0 L10,3 L0,6 Z"/>
    </marker>
    <marker id="arrow-red" viewBox="0 0 10 6" refX="9" refY="3"
            markerWidth="8" markerHeight="5" orient="auto-start-reverse" fill="#dc2626">
      <path d="M0,0 L10,3 L0,6 Z"/>
    </marker>
    <marker id="arrow-amber" viewBox="0 0 10 6" refX="9" refY="3"
            markerWidth="8" markerHeight="5" orient="auto-start-reverse" fill="#d97706">
      <path d="M0,0 L10,3 L0,6 Z"/>
    </marker>
    <marker id="arrow-purple" viewBox="0 0 10 6" refX="9" refY="3"
            markerWidth="8" markerHeight="5" orient="auto-start-reverse" fill="#7c3aed">
      <path d="M0,0 L10,3 L0,6 Z"/>
    </marker>
    <marker id="arrow-indigo" viewBox="0 0 10 6" refX="9" refY="3"
            markerWidth="8" markerHeight="5" orient="auto-start-reverse" fill="#4f46e5">
      <path d="M0,0 L10,3 L0,6 Z"/>
    </marker>

    <!-- Drop shadow -->
    <filter id="shadow" x="-3%" y="-3%" width="106%" height="106%">
      <feDropShadow dx="2" dy="2" stdDeviation="3" flood-color="#0f172a" flood-opacity="0.08"/>
    </filter>
    <filter id="card-shadow" x="-2%" y="-2%" width="104%" height="104%">
      <feDropShadow dx="1" dy="2" stdDeviation="2" flood-color="#0f172a" flood-opacity="0.06"/>
    </filter>

    <!-- Header Gradient -->
    <linearGradient id="headerGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#0f172a"/>
      <stop offset="50%" stop-color="#1e3a8a"/>
      <stop offset="100%" stop-color="#2563eb"/>
    </linearGradient>
  </defs>

  <!-- Background -->
  <rect width="{W}" height="{H}" rx="12" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1"/>

  <!-- Title Header Bar -->
  <rect x="0" y="0" width="{W}" height="56" rx="12" fill="url(#headerGrad)"/>
  <rect x="0" y="30" width="{W}" height="26" fill="url(#headerGrad)"/>
  <text x="30" y="36" fill="#ffffff" font-size="20" font-weight="700" letter-spacing="0.5">
    Direct-Mapped Cache Controller — Microarchitecture Block Diagram
  </text>
  <text x="{W-30}" y="36" text-anchor="end" fill="#93c5fd" font-size="12" font-weight="500">
    Baseline: 1 KiB Capacity | 16-Byte Blocks | 64 Lines | 32-bit Words | Blocking Refill
  </text>
''')

    # Helper function to create badge text
    def badge(x, y, text, color="#1e293b", bg="#ffffff", border="#cbd5e1", font_size=11, font_weight="600", anchor="middle"):
        w = len(text) * (font_size * 0.62) + 14
        h = font_size + 10
        rx_val = 4
        if anchor == "middle":
            bx = x - w/2
        elif anchor == "start":
            bx = x
        else: # end
            bx = x - w
        by = y - h/2
        return f'''<g>
  <rect x="{bx:.1f}" y="{by:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx_val}" fill="{bg}" stroke="{border}" stroke-width="1"/>
  <text x="{x:.1f}" y="{(y + font_size*0.35):.1f}" text-anchor="{anchor}" fill="{color}" font-size="{font_size}" font-weight="{font_weight}">{text}</text>
</g>'''

    # =========================================================================
    # 1. CPU BLOCK (Left)
    # =========================================================================
    cpu_x = 40
    cpu_y = 130
    cpu_w = 140
    cpu_h = 580
    svg.append(f'''
  <!-- CPU Block -->
  <g filter="url(#shadow)">
    <rect x="{cpu_x}" y="{cpu_y}" width="{cpu_w}" height="{cpu_h}" rx="10" fill="#ffffff" stroke="#2563eb" stroke-width="2"/>
    <rect x="{cpu_x}" y="{cpu_y}" width="{cpu_w}" height="40" rx="10" fill="#2563eb"/>
    <rect x="{cpu_x}" y="{cpu_y+20}" width="{cpu_w}" height="20" fill="#2563eb"/>
    <text x="{cpu_x + cpu_w/2}" y="{cpu_y + 26}" text-anchor="middle" fill="#ffffff" font-size="15" font-weight="700">CPU Core</text>
    <text x="{cpu_x + cpu_w/2}" y="{cpu_y + 70}" text-anchor="middle" fill="#64748b" font-size="11" font-weight="500">Master Requester</text>
    <text x="{cpu_x + cpu_w/2}" y="{cpu_y + 88}" text-anchor="middle" fill="#94a3b8" font-size="10">Word-Aligned</text>

    <!-- Sub-headers inside CPU -->
    <text x="{cpu_x + 14}" y="{cpu_y + 130}" fill="#1e3a8a" font-size="11" font-weight="700">OUTPUTS →</text>
    <text x="{cpu_x + 14}" y="{cpu_y + 340}" fill="#166534" font-size="11" font-weight="700">← INPUTS</text>
  </g>
''')

    # CPU Output connection points (y coordinates)
    y_cpu_valid = 270
    y_cpu_addr  = 315
    y_cpu_we    = 360
    y_cpu_wdata = 405

    # CPU Input connection points (y coordinates)
    y_cpu_rdata = 490
    y_cpu_ready = 535
    y_stat_hit  = 575
    y_stat_miss = 615
    y_hit_cnt   = 655
    y_miss_cnt  = 695

    # =========================================================================
    # 2. CACHE_TOP BOUNDARY (Middle)
    # =========================================================================
    cache_x = 340
    cache_y = 80
    cache_w = 830
    cache_h = 810
    svg.append(f'''
  <!-- cache_top Boundary -->
  <g>
    <rect x="{cache_x}" y="{cache_y}" width="{cache_w}" height="{cache_h}" rx="14" fill="#ffffff" stroke="#334155" stroke-width="2.5" stroke-dasharray="10,6" filter="url(#shadow)"/>
    <rect x="{cache_x}" y="{cache_y}" width="220" height="34" rx="14" fill="#0f172a"/>
    <rect x="{cache_x}" y="{cache_y+16}" width="220" height="18" fill="#0f172a"/>
    <text x="{cache_x+16}" y="{cache_y+23}" fill="#ffffff" font-size="14" font-weight="700">cache_top (DUT)</text>
    <text x="{cache_x+240}" y="{cache_y+23}" fill="#64748b" font-size="12" font-weight="500">
      Parameters: ADDR_W=32 | CACHE_BYTES=1024 | BLOCK_BYTES=16 | WRITE_SUPPORT=0
    </text>
  </g>
''')

    # =========================================================================
    # 3. CPU TO CACHE_TOP INTERCONNECT WIRES & BADGES
    # =========================================================================
    # Draw CPU output wires (Blue)
    for y_pos, sig, bus in [
        (y_cpu_valid, "cpu_valid", False),
        (y_cpu_addr,  "cpu_addr [31:0]", True),
        (y_cpu_we,    "cpu_we", False),
        (y_cpu_wdata, "cpu_wdata [31:0]", True)
    ]:
        sw = 2.5 if bus else 1.8
        svg.append(f'<line x1="{cpu_x+cpu_w}" y1="{y_pos}" x2="{cache_x}" y2="{y_pos}" stroke="#2563eb" stroke-width="{sw}" marker-end="url(#arrow-blue)"/>')
        svg.append(badge((cpu_x+cpu_w + cache_x)/2, y_pos, sig, color="#1d4ed8", bg="#eff6ff", border="#bfdbfe", font_size=11))

    # Draw CPU input wires (Green)
    for y_pos, sig, bus in [
        (y_cpu_rdata, "cpu_rdata [31:0]", True),
        (y_cpu_ready, "cpu_ready (1-cycle pulse)", False),
        (y_stat_hit,  "stat_hit", False),
        (y_stat_miss, "stat_miss", False),
        (y_hit_cnt,   "hit_count [31:0]", True),
        (y_miss_cnt,  "miss_count [31:0]", True)
    ]:
        sw = 2.5 if bus else 1.8
        svg.append(f'<line x1="{cache_x}" y1="{y_pos}" x2="{cpu_x+cpu_w}" y2="{y_pos}" stroke="#16a34a" stroke-width="{sw}" marker-end="url(#arrow-green)"/>')
        svg.append(badge((cpu_x+cpu_w + cache_x)/2, y_pos, sig, color="#15803d", bg="#f0fdf4", border="#bbf7d0", font_size=10.5))

    # =========================================================================
    # 4. MODULES INSIDE CACHE_TOP
    # =========================================================================

    # --- 4.1 Address Decoder ---
    dec_x = cache_x + 30
    dec_y = 140
    dec_w = 200
    dec_h = 160
    svg.append(f'''
  <!-- addr_decoder -->
  <g filter="url(#card-shadow)">
    <rect x="{dec_x}" y="{dec_y}" width="{dec_w}" height="{dec_h}" rx="8" fill="#fffbeb" stroke="#d97706" stroke-width="2"/>
    <rect x="{dec_x}" y="{dec_y}" width="{dec_w}" height="28" rx="8" fill="#d97706"/>
    <rect x="{dec_x}" y="{dec_y+14}" width="{dec_w}" height="14" fill="#d97706"/>
    <text x="{dec_x + dec_w/2}" y="{dec_y+19}" text-anchor="middle" fill="#ffffff" font-size="13" font-weight="700">addr_decoder</text>
    <text x="{dec_x + 12}" y="{dec_y+48}" fill="#92400e" font-size="10" font-weight="600">INPUT: addr[31:0]</text>
    <line x1="{dec_x+10}" y1="{dec_y+56}" x2="{dec_x+dec_w-10}" y2="{dec_y+56}" stroke="#fde68a" stroke-width="1"/>
    <text x="{dec_x + 12}" y="{dec_y+76}" fill="#78350f" font-size="11" font-weight="700">tag [21:0]  (addr[31:10])</text>
    <text x="{dec_x + 12}" y="{dec_y+98}" fill="#b45309" font-size="11" font-weight="700">index [5:0] (addr[9:4])</text>
    <text x="{dec_x + 12}" y="{dec_y+120}" fill="#78350f" font-size="11" font-weight="700">offset [3:0] (addr[3:0])</text>
    <text x="{dec_x + 12}" y="{dec_y+142}" fill="#92400e" font-size="10" font-weight="600">word_sel [1:0] = addr[3:2]</text>
  </g>
''')

    # Connect cpu_addr to addr_decoder
    svg.append(f'''
  <path d="M {cache_x},{y_cpu_addr} L {dec_x - 12},{y_cpu_addr} L {dec_x - 12},{dec_y + 44} L {dec_x},{dec_y + 44}"
        fill="none" stroke="#2563eb" stroke-width="2" marker-end="url(#arrow-blue)"/>
''')

    # --- 4.2 Storage Datapath (RAMs) ---
    # Tag RAM
    tram_x = cache_x + 280
    tram_y = 140
    tram_w = 175
    tram_h = 100

    # Valid RAM
    vram_x = cache_x + 280
    vram_y = 260
    vram_w = 175
    vram_h = 95

    # Data RAM
    dram_x = cache_x + 280
    dram_y = 375
    dram_w = 175
    dram_h = 115

    # Draw Tag RAM
    svg.append(f'''
  <!-- tag_ram -->
  <g filter="url(#card-shadow)">
    <rect x="{tram_x}" y="{tram_y}" width="{tram_w}" height="{tram_h}" rx="8" fill="#fdf2f8" stroke="#db2777" stroke-width="2"/>
    <rect x="{tram_x}" y="{tram_y}" width="{tram_w}" height="26" rx="8" fill="#db2777"/>
    <rect x="{tram_x}" y="{tram_y+13}" width="{tram_w}" height="13" fill="#db2777"/>
    <text x="{tram_x + tram_w/2}" y="{tram_y+18}" text-anchor="middle" fill="#ffffff" font-size="12" font-weight="700">tag_ram</text>
    <text x="{tram_x+10}" y="{tram_y+44}" fill="#831843" font-size="10" font-weight="700">64 lines × 22 bits</text>
    <text x="{tram_x+10}" y="{tram_y+62}" fill="#9d174d" font-size="9.5">in: index[5:0], we, w_tag</text>
    <text x="{tram_x+10}" y="{tram_y+78}" fill="#9d174d" font-size="9.5">Async Read (Distributed RAM)</text>
    <text x="{tram_x+10}" y="{tram_y+94}" fill="#db2777" font-size="9.5" font-weight="700">out: stored_tag [21:0]</text>
  </g>
''')

    # Draw Valid RAM
    svg.append(f'''
  <!-- valid_ram -->
  <g filter="url(#card-shadow)">
    <rect x="{vram_x}" y="{vram_y}" width="{vram_w}" height="{vram_h}" rx="8" fill="#fdf2f8" stroke="#db2777" stroke-width="2"/>
    <rect x="{vram_x}" y="{vram_y}" width="{vram_w}" height="26" rx="8" fill="#db2777"/>
    <rect x="{vram_x}" y="{vram_y+13}" width="{vram_w}" height="13" fill="#db2777"/>
    <text x="{vram_x + vram_w/2}" y="{vram_y+18}" text-anchor="middle" fill="#ffffff" font-size="12" font-weight="700">valid_ram</text>
    <text x="{vram_x+10}" y="{vram_y+44}" fill="#831843" font-size="10" font-weight="700">64 × 1-bit Flip-Flops</text>
    <text x="{vram_x+10}" y="{vram_y+62}" fill="#9d174d" font-size="9.5">Sync reset (rst_n) clears all</text>
    <text x="{vram_x+10}" y="{vram_y+78}" fill="#9d174d" font-size="9.5">in: index[5:0], we, w_valid</text>
    <text x="{vram_x+10}" y="{vram_y+92}" fill="#db2777" font-size="9.5" font-weight="700">out: stored_valid (1-bit)</text>
  </g>
''')

    # Draw Data RAM
    svg.append(f'''
  <!-- data_ram -->
  <g filter="url(#card-shadow)">
    <rect x="{dram_x}" y="{dram_y}" width="{dram_w}" height="{dram_h}" rx="8" fill="#fdf2f8" stroke="#db2777" stroke-width="2"/>
    <rect x="{dram_x}" y="{dram_y}" width="{dram_w}" height="26" rx="8" fill="#db2777"/>
    <rect x="{dram_x}" y="{dram_y+13}" width="{dram_w}" height="13" fill="#db2777"/>
    <text x="{dram_x + dram_w/2}" y="{dram_y+18}" text-anchor="middle" fill="#ffffff" font-size="12" font-weight="700">data_ram</text>
    <text x="{dram_x+10}" y="{dram_y+44}" fill="#831843" font-size="10" font-weight="700">64 lines × 128-bit block</text>
    <text x="{dram_x+10}" y="{dram_y+62}" fill="#9d174d" font-size="9.5">Sync word-granular write</text>
    <text x="{dram_x+10}" y="{dram_y+78}" fill="#9d174d" font-size="9.5">in: index, we, w_wsel, w_word</text>
    <text x="{dram_x+10}" y="{dram_y+94}" fill="#9d174d" font-size="9.5">Async full-block read</text>
    <text x="{dram_x+10}" y="{dram_y+110}" fill="#db2777" font-size="9.5" font-weight="700">out: rd_block [127:0]</text>
  </g>
''')

    # Index bus distribution from Decoder to RAMs
    idx_bus_x = dec_x + dec_w + 25
    svg.append(f'''
  <!-- Index Bus Distribution -->
  <path d="M {dec_x + dec_w},{dec_y + 94} L {idx_bus_x},{dec_y + 94}" stroke="#d97706" stroke-width="2.5"/>
  <path d="M {idx_bus_x},{tram_y + 40} L {idx_bus_x},{dram_y + 50}" stroke="#d97706" stroke-width="2.5"/>
  <line x1="{idx_bus_x}" y1="{tram_y + 40}" x2="{tram_x}" y2="{tram_y + 40}" stroke="#d97706" stroke-width="2" marker-end="url(#arrow-amber)"/>
  <line x1="{idx_bus_x}" y1="{vram_y + 40}" x2="{vram_x}" y2="{vram_y + 40}" stroke="#d97706" stroke-width="2" marker-end="url(#arrow-amber)"/>
  <line x1="{idx_bus_x}" y1="{dram_y + 50}" x2="{dram_x}" y2="{dram_y + 50}" stroke="#d97706" stroke-width="2" marker-end="url(#arrow-amber)"/>
''')
    svg.append(badge(idx_bus_x, dec_y + 70, "index [5:0]", color="#92400e", bg="#fffbeb", border="#fde68a", font_size=10))

    # --- 4.3 Tag Comparator ---
    cmp_x = cache_x + 510
    cmp_y = 140
    cmp_w = 170
    cmp_h = 135
    svg.append(f'''
  <!-- tag_comparator -->
  <g filter="url(#card-shadow)">
    <rect x="{cmp_x}" y="{cmp_y}" width="{cmp_w}" height="{cmp_h}" rx="8" fill="#f0fdf4" stroke="#16a34a" stroke-width="2"/>
    <rect x="{cmp_x}" y="{cmp_y}" width="{cmp_w}" height="26" rx="8" fill="#16a34a"/>
    <rect x="{cmp_x}" y="{cmp_y+13}" width="{cmp_w}" height="13" fill="#16a34a"/>
    <text x="{cmp_x + cmp_w/2}" y="{cmp_y+18}" text-anchor="middle" fill="#ffffff" font-size="12" font-weight="700">tag_comparator</text>
    <text x="{cmp_x+10}" y="{cmp_y+46}" fill="#166534" font-size="10">tag_a ← stored_tag [21:0]</text>
    <text x="{cmp_x+10}" y="{cmp_y+64}" fill="#166534" font-size="10">tag_b ← requested tag [21:0]</text>
    <text x="{cmp_x+10}" y="{cmp_y+82}" fill="#166534" font-size="10">valid  ← stored_valid (1-bit)</text>
    <line x1="{cmp_x+8}" y1="{cmp_y+92}" x2="{cmp_x+cmp_w-8}" y2="{cmp_y+92}" stroke="#bbf7d0" stroke-width="1"/>
    <text x="{cmp_x + cmp_w/2}" y="{cmp_y+112}" text-anchor="middle" fill="#15803d" font-size="11" font-weight="700">hit = valid &amp; (tag_a == tag_b)</text>
    <text x="{cmp_x + cmp_w/2}" y="{cmp_y+128}" text-anchor="middle" fill="#166534" font-size="9.5">Combinational (1-cycle hit)</text>
  </g>
''')

    # Connections into tag_comparator:
    # 1. stored_tag from tag_ram
    svg.append(f'''
  <line x1="{tram_x + tram_w}" y1="{tram_y + 45}" x2="{cmp_x}" y2="{cmp_y + 45}" stroke="#db2777" stroke-width="2" marker-end="url(#arrow-purple)"/>
''')
    svg.append(badge((tram_x + tram_w + cmp_x)/2, tram_y + 45, "stored_tag [21:0]", color="#9d174d", bg="#fdf2f8", border="#fbcfe8", font_size=9.5))

    # 2. stored_valid from valid_ram
    svg.append(f'''
  <path d="M {vram_x + vram_w},{vram_y + 40} L {cmp_x - 18},{vram_y + 40} L {cmp_x - 18},{cmp_y + 80} L {cmp_x},{cmp_y + 80}"
        fill="none" stroke="#db2777" stroke-width="1.8" marker-end="url(#arrow-purple)"/>
''')
    svg.append(badge(cmp_x - 18, vram_y + 15, "stored_valid", color="#9d174d", bg="#fdf2f8", border="#fbcfe8", font_size=9.5))

    # 3. requested tag from decoder (route over top)
    svg.append(f'''
  <path d="M {dec_x + 120},{dec_y} L {dec_x + 120},{dec_y - 25} L {cmp_x + cmp_w/2},{dec_y - 25} L {cmp_x + cmp_w/2},{cmp_y}"
        fill="none" stroke="#d97706" stroke-width="2" marker-end="url(#arrow-amber)"/>
''')
    svg.append(badge((dec_x + 120 + cmp_x + cmp_w/2)/2, dec_y - 25, "requested tag [21:0]", color="#92400e", bg="#fffbeb", border="#fde68a", font_size=10))

    # --- 4.4 Cache Controller FSM ---
    ctrl_x = cache_x + 480
    ctrl_y = 310
    ctrl_w = 320
    ctrl_h = 320
    svg.append(f'''
  <!-- cache_controller FSM -->
  <g filter="url(#card-shadow)">
    <rect x="{ctrl_x}" y="{ctrl_y}" width="{ctrl_w}" height="{ctrl_h}" rx="10" fill="#eef2ff" stroke="#4f46e5" stroke-width="2.5"/>
    <rect x="{ctrl_x}" y="{ctrl_y}" width="{ctrl_w}" height="32" rx="10" fill="#4f46e5"/>
    <rect x="{ctrl_x}" y="{ctrl_y+16}" width="{ctrl_w}" height="16" fill="#4f46e5"/>
    <text x="{ctrl_x + ctrl_w/2}" y="{ctrl_y+22}" text-anchor="middle" fill="#ffffff" font-size="13" font-weight="700">cache_controller (FSM)</text>

    <!-- FSM State Bubbles inside -->
    <!-- S_IDLE -->
    <rect x="{ctrl_x + 20}" y="{ctrl_y + 50}" width="85" height="40" rx="20" fill="#c7d2fe" stroke="#4338ca" stroke-width="2"/>
    <text x="{ctrl_x + 62}" y="{ctrl_y + 70}" text-anchor="middle" fill="#312e81" font-size="11" font-weight="700">S_IDLE</text>
    <text x="{ctrl_x + 62}" y="{ctrl_y + 83}" text-anchor="middle" fill="#4338ca" font-size="8.5">Hit=1 cycle</text>

    <!-- S_REFILL -->
    <rect x="{ctrl_x + 185}" y="{ctrl_y + 50}" width="105" height="40" rx="20" fill="#fde68a" stroke="#d97706" stroke-width="2"/>
    <text x="{ctrl_x + 237}" y="{ctrl_y + 70}" text-anchor="middle" fill="#78350f" font-size="11" font-weight="700">S_REFILL</text>
    <text x="{ctrl_x + 237}" y="{ctrl_y + 83}" text-anchor="middle" fill="#92400e" font-size="8.5">4 words (20c)</text>

    <!-- S_RESPOND -->
    <rect x="{ctrl_x + 185}" y="{ctrl_y + 130}" width="105" height="40" rx="20" fill="#bbf7d0" stroke="#16a34a" stroke-width="2"/>
    <text x="{ctrl_x + 237}" y="{ctrl_y + 150}" text-anchor="middle" fill="#14532d" font-size="11" font-weight="700">S_RESPOND</text>
    <text x="{ctrl_x + 237}" y="{ctrl_y + 163}" text-anchor="middle" fill="#166534" font-size="8.5">cpu_ready pulse</text>

    <!-- S_WRITE -->
    <rect x="{ctrl_x + 20}" y="{ctrl_y + 130}" width="95" height="40" rx="20" fill="#fed7aa" stroke="#ea580c" stroke-width="2"/>
    <text x="{ctrl_x + 67}" y="{ctrl_y + 150}" text-anchor="middle" fill="#7c2d12" font-size="11" font-weight="700">S_WRITE</text>
    <text x="{ctrl_x + 67}" y="{ctrl_y + 163}" text-anchor="middle" fill="#9a3412" font-size="8.5">Write-Through</text>

    <!-- Transitions -->
    <!-- IDLE -> REFILL -->
    <line x1="{ctrl_x + 105}" y1="{ctrl_y + 65}" x2="{ctrl_x + 185}" y2="{ctrl_y + 65}" stroke="#dc2626" stroke-width="2" marker-end="url(#arrow-red)"/>
    <text x="{ctrl_x + 145}" y="{ctrl_y + 60}" text-anchor="middle" fill="#b91c1c" font-size="9" font-weight="700">Miss</text>

    <!-- REFILL -> RESPOND -->
    <line x1="{ctrl_x + 237}" y1="{ctrl_y + 90}" x2="{ctrl_x + 237}" y2="{ctrl_y + 130}" stroke="#4f46e5" stroke-width="2" marker-end="url(#arrow-indigo)"/>
    <text x="{ctrl_x + 280}" y="{ctrl_y + 112}" text-anchor="middle" fill="#4338ca" font-size="8.5">last word ack</text>

    <!-- RESPOND -> IDLE -->
    <path d="M {ctrl_x + 185},{ctrl_y + 150} L {ctrl_x + 140},{ctrl_y + 150} L {ctrl_x + 140},{ctrl_y + 80} L {ctrl_x + 105},{ctrl_y + 80}"
          fill="none" stroke="#16a34a" stroke-width="2" marker-end="url(#arrow-green)"/>

    <!-- IDLE -> WRITE -->
    <line x1="{ctrl_x + 50}" y1="{ctrl_y + 90}" x2="{ctrl_x + 50}" y2="{ctrl_y + 130}" stroke="#ea580c" stroke-width="1.8" marker-end="url(#arrow-amber)"/>
    <text x="{ctrl_x + 28}" y="{ctrl_y + 112}" text-anchor="middle" fill="#c2410c" font-size="8.5">cpu_we</text>

    <!-- WRITE -> IDLE -->
    <path d="M {ctrl_x + 80},{ctrl_y + 130} L {ctrl_x + 80},{ctrl_y + 90}"
          fill="none" stroke="#4f46e5" stroke-width="1.8" marker-end="url(#arrow-indigo)"/>

    <!-- FSM Outputs Panel -->
    <rect x="{ctrl_x + 12}" y="{ctrl_y + 195}" width="{ctrl_w - 24}" height="110" rx="6" fill="#ffffff" stroke="#c7d2fe" stroke-width="1"/>
    <text x="{ctrl_x + 20}" y="{ctrl_y + 215}" fill="#312e81" font-size="10" font-weight="700">CONTROLLER OUTPUT SIGNALS:</text>
    <text x="{ctrl_x + 20}" y="{ctrl_y + 235}" fill="#4338ca" font-size="9.5">• CPU Strobes: <tspan font-weight="700">cpu_ready, stat_hit, stat_miss</tspan></text>
    <text x="{ctrl_x + 20}" y="{ctrl_y + 253}" fill="#4338ca" font-size="9.5">• Datapath WE: <tspan font-weight="700">data_we, tag_we, valid_we, data_wsel</tspan></text>
    <text x="{ctrl_x + 20}" y="{ctrl_y + 271}" fill="#4338ca" font-size="9.5">• Memory Bus: <tspan font-weight="700">mem_req, mem_we, refill_word [1:0]</tspan></text>
    <text x="{ctrl_x + 20}" y="{ctrl_y + 291}" fill="#15803d" font-size="9" font-weight="600">Rule: Exactly 1 stat pulse per request | Valid set on word 3</text>
  </g>
''')

    # Connection: hit -> controller
    svg.append(f'''
  <line x1="{cmp_x + cmp_w/2}" y1="{cmp_y + cmp_h}" x2="{cmp_x + cmp_w/2}" y2="{ctrl_y}" stroke="#16a34a" stroke-width="2.5" marker-end="url(#arrow-green)"/>
''')
    svg.append(badge(cmp_x + cmp_w/2, (cmp_y + cmp_h + ctrl_y)/2, "hit (1-bit)", color="#15803d", bg="#f0fdf4", border="#bbf7d0", font_size=10.5))

    # Connection: cpu_valid & cpu_we to controller
    svg.append(f'''
  <path d="M {cache_x},{y_cpu_valid} L {dec_x - 12},{y_cpu_valid} L {dec_x - 12},{ctrl_y + 230} L {ctrl_x},{ctrl_y + 230}"
        fill="none" stroke="#2563eb" stroke-width="2" stroke-dasharray="6,3" marker-end="url(#arrow-blue)"/>
''')
    svg.append(badge((dec_x + ctrl_x)/2, ctrl_y + 230, "cpu_valid, cpu_we", color="#1d4ed8", bg="#eff6ff", border="#bfdbfe", font_size=10))

    # --- 4.5 Word Multiplexer ---
    mux_x = cache_x + 120
    mux_y = 510
    mux_w = 140
    mux_h = 75
    svg.append(f'''
  <!-- Word MUX -->
  <g filter="url(#card-shadow)">
    <polygon points="{mux_x},{mux_y} {mux_x+mux_w},{mux_y+15} {mux_x+mux_w},{mux_y+mux_h-15} {mux_x},{mux_y+mux_h}"
             fill="#fef9c3" stroke="#ca8a04" stroke-width="2"/>
    <text x="{mux_x + mux_w/2}" y="{mux_y + 36}" text-anchor="middle" fill="#854d0e" font-size="12" font-weight="700">Word MUX</text>
    <text x="{mux_x + mux_w/2}" y="{mux_y + 52}" text-anchor="middle" fill="#a16207" font-size="9.5">4-to-1 (32-bit)</text>
  </g>
''')

    # Data RAM rd_block -> Word MUX
    svg.append(f'''
  <path d="M {dram_x},{dram_y + 80} L {mux_x + mux_w/2},{dram_y + 80} L {mux_x + mux_w/2},{mux_y}"
        fill="none" stroke="#db2777" stroke-width="2.5" marker-end="url(#arrow-purple)"/>
''')
    svg.append(badge(dram_x - 20, dram_y + 80, "rd_block [127:0]", color="#9d174d", bg="#fdf2f8", border="#fbcfe8", font_size=10, anchor="end"))

    # Word select from decoder to MUX
    svg.append(f'''
  <path d="M {dec_x + 100},{dec_y + dec_h} L {dec_x + 100},{mux_y + 35} L {mux_x},{mux_y + 35}"
        fill="none" stroke="#d97706" stroke-width="1.8" marker-end="url(#arrow-amber)"/>
''')
    svg.append(badge(dec_x + 100, (dec_y + dec_h + mux_y)/2, "word_sel [1:0]", color="#92400e", bg="#fffbeb", border="#fde68a", font_size=9.5))

    # MUX output -> cpu_rdata
    svg.append(f'''
  <path d="M {mux_x},{mux_y + mux_h/2} L {cache_x},{y_cpu_rdata}"
        fill="none" stroke="#16a34a" stroke-width="2.5" marker-end="url(#arrow-green)"/>
''')

    # --- 4.6 Statistics Counters ---
    cnt_x = cache_x + 120
    cnt_y = 650
    cnt_w = 170
    cnt_h = 75
    svg.append(f'''
  <!-- Statistics Counters -->
  <g filter="url(#card-shadow)">
    <rect x="{cnt_x}" y="{cnt_y}" width="{cnt_w}" height="{cnt_h}" rx="8" fill="#f0fdf4" stroke="#16a34a" stroke-width="2"/>
    <text x="{cnt_x + cnt_w/2}" y="{cnt_y + 24}" text-anchor="middle" fill="#14532d" font-size="12" font-weight="700">Statistics Counters</text>
    <text x="{cnt_x + cnt_w/2}" y="{cnt_y + 44}" text-anchor="middle" fill="#15803d" font-size="10">hit_count &lt;= hit_count + 1</text>
    <text x="{cnt_x + cnt_w/2}" y="{cnt_y + 60}" text-anchor="middle" fill="#15803d" font-size="10">miss_count &lt;= miss_count + 1</text>
  </g>
''')

    # Connections to counters:
    # Controller stat_hit/stat_miss to counters
    svg.append(f'''
  <path d="M {ctrl_x},{ctrl_y + 245} L {cnt_x + cnt_w + 30},{ctrl_y + 245} L {cnt_x + cnt_w + 30},{cnt_y + 35} L {cnt_x + cnt_w},{cnt_y + 35}"
        fill="none" stroke="#16a34a" stroke-width="1.8" stroke-dasharray="5,3" marker-end="url(#arrow-green)"/>
''')
    svg.append(badge(cnt_x + cnt_w + 30, ctrl_y + 265, "stat_hit, stat_miss", color="#15803d", bg="#f0fdf4", border="#bbf7d0", font_size=9.5))

    # Counters to CPU outputs
    svg.append(f'''
  <path d="M {cnt_x},{cnt_y + 25} L {cache_x},{y_hit_cnt}" fill="none" stroke="#16a34a" stroke-width="2" marker-end="url(#arrow-green)"/>
  <path d="M {cnt_x},{cnt_y + 55} L {cache_x},{y_miss_cnt}" fill="none" stroke="#16a34a" stroke-width="2" marker-end="url(#arrow-green)"/>
''')

    # Controller to cpu_ready, stat_hit, stat_miss outputs to CPU
    svg.append(f'''
  <path d="M {ctrl_x},{ctrl_y + 225} L {cnt_x + cnt_w + 15},{ctrl_y + 225} L {cnt_x + cnt_w + 15},{y_cpu_ready} L {cache_x},{y_cpu_ready}"
        fill="none" stroke="#16a34a" stroke-width="2" marker-end="url(#arrow-green)"/>
  <path d="M {cnt_x + cnt_w + 15},{y_stat_hit} L {cache_x},{y_stat_hit}"
        fill="none" stroke="#16a34a" stroke-width="2" marker-end="url(#arrow-green)"/>
  <path d="M {cnt_x + cnt_w + 15},{y_stat_miss} L {cache_x},{y_stat_miss}"
        fill="none" stroke="#16a34a" stroke-width="2" marker-end="url(#arrow-green)"/>
''')

    # Write enables from controller to RAMs
    svg.append(f'''
  <!-- Controller WE signals back to RAMs -->
  <path d="M {ctrl_x},{ctrl_y + 70} L {tram_x + tram_w},{tram_y + 70}" stroke="#4f46e5" stroke-width="1.8" stroke-dasharray="5,3" marker-end="url(#arrow-indigo)"/>
  <path d="M {ctrl_x},{ctrl_y + 110} L {vram_x + vram_w},{vram_y + 65}" stroke="#4f46e5" stroke-width="1.8" stroke-dasharray="5,3" marker-end="url(#arrow-indigo)"/>
  <path d="M {ctrl_x},{ctrl_y + 150} L {dram_x + dram_w},{dram_y + 65}" stroke="#4f46e5" stroke-width="1.8" stroke-dasharray="5,3" marker-end="url(#arrow-indigo)"/>
''')
    svg.append(badge((tram_x + tram_w + ctrl_x)/2, tram_y + 70, "tag_we", color="#4338ca", bg="#eef2ff", border="#c7d2fe", font_size=9))
    svg.append(badge((vram_x + vram_w + ctrl_x)/2, vram_y + 65, "valid_we", color="#4338ca", bg="#eef2ff", border="#c7d2fe", font_size=9))
    svg.append(badge((dram_x + dram_w + ctrl_x)/2, dram_y + 65, "data_we, wsel", color="#4338ca", bg="#eef2ff", border="#c7d2fe", font_size=9))

    # --- 4.7 Memory Address Generation Logic ---
    mgen_x = cache_x + 500
    mgen_y = 660
    mgen_w = 280
    mgen_h = 75
    svg.append(f'''
  <!-- Memory Address/Data Logic -->
  <g filter="url(#card-shadow)">
    <rect x="{mgen_x}" y="{mgen_y}" width="{mgen_w}" height="{mgen_h}" rx="8" fill="#fff7ed" stroke="#ea580c" stroke-width="2"/>
    <text x="{mgen_x + mgen_w/2}" y="{mgen_y + 22}" text-anchor="middle" fill="#9a3412" font-size="12" font-weight="700">Memory Addr / Data Generator</text>
    <text x="{mgen_x + 12}" y="{mgen_y + 44}" fill="#c2410c" font-size="10">Refill: &#123;cpu_addr[31:4], refill_word[1:0], 2'b00&#125;</text>
    <text x="{mgen_x + 12}" y="{mgen_y + 62}" fill="#c2410c" font-size="10">Write: &#123;cpu_addr[31:2], 2'b00&#125; | wdata = cpu_wdata</text>
  </g>
''')

    # refill_word from controller to mgen
    svg.append(f'''
  <line x1="{ctrl_x + ctrl_w/2}" y1="{ctrl_y + ctrl_h}" x2="{ctrl_x + ctrl_w/2}" y2="{mgen_y}" stroke="#4f46e5" stroke-width="2" marker-end="url(#arrow-indigo)"/>
''')
    svg.append(badge(ctrl_x + ctrl_w/2, (ctrl_y + ctrl_h + mgen_y)/2, "refill_word [1:0]", color="#4338ca", bg="#eef2ff", border="#c7d2fe", font_size=10))

    # =========================================================================
    # 5. MAIN MEMORY BLOCK (Right)
    # =========================================================================
    mem_x = cache_x + cache_w + 140
    mem_y = 180
    mem_w = 150
    mem_h = 500
    svg.append(f'''
  <!-- Main Memory Block -->
  <g filter="url(#shadow)">
    <rect x="{mem_x}" y="{mem_y}" width="{mem_w}" height="{mem_h}" rx="10" fill="#ffffff" stroke="#dc2626" stroke-width="2"/>
    <rect x="{mem_x}" y="{mem_y}" width="{mem_w}" height="40" rx="10" fill="#dc2626"/>
    <rect x="{mem_x}" y="{mem_y+20}" width="{mem_w}" height="20" fill="#dc2626"/>
    <text x="{mem_x + mem_w/2}" y="{mem_y + 26}" text-anchor="middle" fill="#ffffff" font-size="14" font-weight="700">main_memory</text>
    <text x="{mem_x + mem_w/2}" y="{mem_y + 64}" text-anchor="middle" fill="#991b1b" font-size="10" font-weight="700">BEHAVIORAL MODEL</text>
    <text x="{mem_x + mem_w/2}" y="{mem_y + 80}" text-anchor="middle" fill="#64748b" font-size="9.5">Simulation Model Only</text>
    <text x="{mem_x + mem_w/2}" y="{mem_y + 96}" text-anchor="middle" fill="#64748b" font-size="9.5">(Excluded in Synthesis)</text>
    <line x1="{mem_x+10}" y1="{mem_y+108}" x2="{mem_x+mem_w-10}" y2="{mem_y+108}" stroke="#fecaca" stroke-width="1"/>

    <text x="{mem_x + 12}" y="{mem_y + 130}" fill="#991b1b" font-size="10" font-weight="700">SPECIFICATION:</text>
    <text x="{mem_x + 12}" y="{mem_y + 150}" fill="#7f1d1d" font-size="9.5">• 65,536 Words</text>
    <text x="{mem_x + 12}" y="{mem_y + 166}" fill="#7f1d1d" font-size="9.5">  (256 KiB capacity)</text>
    <text x="{mem_x + 12}" y="{mem_y + 186}" fill="#7f1d1d" font-size="9.5">• MEM_LATENCY = 4</text>
    <text x="{mem_x + 12}" y="{mem_y + 202}" fill="#7f1d1d" font-size="9.5">  cycles per word</text>
    <text x="{mem_x + 12}" y="{mem_y + 222}" fill="#7f1d1d" font-size="9.5">• Initial Hash Contents:</text>
    <text x="{mem_x + 12}" y="{mem_y + 238}" fill="#7f1d1d" font-size="9">  w * 32'h9E3779B1</text>
    <text x="{mem_x + 12}" y="{mem_y + 258}" fill="#7f1d1d" font-size="9.5">• Handshake: 1 ack</text>
    <text x="{mem_x + 12}" y="{mem_y + 274}" fill="#7f1d1d" font-size="9.5">  pulse per word</text>

    <!-- Sub-headers inside Memory -->
    <text x="{mem_x + 12}" y="{mem_y + 330}" fill="#991b1b" font-size="11" font-weight="700">← INPUTS</text>
    <text x="{mem_x + 12}" y="{mem_y + 420}" fill="#166534" font-size="11" font-weight="700">OUTPUTS →</text>
  </g>
''')

    # Memory Interface signal levels
    y_mem_req   = 320
    y_mem_addr  = 370
    y_mem_we    = 420
    y_mem_wdata = 470
    y_mem_rdata = 530
    y_mem_ack   = 580

    # Signals from cache_top to main_memory (Red)
    for y_pos, sig, bus in [
        (y_mem_req,   "mem_req", False),
        (y_mem_addr,  "mem_addr [31:0]", True),
        (y_mem_we,    "mem_we", False),
        (y_mem_wdata, "mem_wdata [31:0]", True)
    ]:
        sw = 2.5 if bus else 1.8
        svg.append(f'<line x1="{cache_x + cache_w}" y1="{y_pos}" x2="{mem_x}" y2="{y_pos}" stroke="#dc2626" stroke-width="{sw}" marker-end="url(#arrow-red)"/>')
        svg.append(badge((cache_x + cache_w + mem_x)/2, y_pos, sig, color="#b91c1c", bg="#fef2f2", border="#fecaca", font_size=11))

    # Signals from main_memory to cache_top (Green)
    for y_pos, sig, bus in [
        (y_mem_rdata, "mem_rdata [31:0]", True),
        (y_mem_ack,   "mem_ack (1-cycle pulse)", False)
    ]:
        sw = 2.5 if bus else 1.8
        svg.append(f'<line x1="{mem_x}" y1="{y_pos}" x2="{cache_x + cache_w}" y2="{y_pos}" stroke="#16a34a" stroke-width="{sw}" marker-end="url(#arrow-green)"/>')
        svg.append(badge((cache_x + cache_w + mem_x)/2, y_pos, sig, color="#15803d", bg="#f0fdf4", border="#bbf7d0", font_size=11))

    # Connect internal controller to mem_req and mem_we
    svg.append(f'''
  <path d="M {ctrl_x + ctrl_w},{ctrl_y + 80} L {cache_x + cache_w},{y_mem_req}"
        fill="none" stroke="#dc2626" stroke-width="1.8" marker-end="url(#arrow-red)"/>
  <path d="M {ctrl_x + ctrl_w},{ctrl_y + 120} L {cache_x + cache_w},{y_mem_we}"
        fill="none" stroke="#dc2626" stroke-width="1.8" marker-end="url(#arrow-red)"/>
''')

    # Connect mgen to mem_addr
    svg.append(f'''
  <path d="M {mgen_x + mgen_w},{mgen_y + 35} L {cache_x + cache_w - 20},{mgen_y + 35} L {cache_x + cache_w - 20},{y_mem_addr} L {cache_x + cache_w},{y_mem_addr}"
        fill="none" stroke="#dc2626" stroke-width="2.5" marker-end="url(#arrow-red)"/>
''')

    # Connect mem_rdata directly into data_ram w_word
    svg.append(f'''
  <path d="M {cache_x + cache_w},{y_mem_rdata} L {dram_x + dram_w + 35},{y_mem_rdata} L {dram_x + dram_w + 35},{dram_y + 100} L {dram_x + dram_w},{dram_y + 100}"
        fill="none" stroke="#16a34a" stroke-width="2" marker-end="url(#arrow-green)"/>
''')
    svg.append(badge(dram_x + dram_w + 35, (y_mem_rdata + dram_y + 100)/2, "refill word → w_word", color="#15803d", bg="#f0fdf4", border="#bbf7d0", font_size=9.5))

    # Connect mem_ack into controller
    svg.append(f'''
  <path d="M {cache_x + cache_w},{y_mem_ack} L {ctrl_x + ctrl_w + 20},{y_mem_ack} L {ctrl_x + ctrl_w + 20},{ctrl_y + 160} L {ctrl_x + ctrl_w},{ctrl_y + 160}"
        fill="none" stroke="#16a34a" stroke-width="1.8" marker-end="url(#arrow-green)"/>
''')
    svg.append(badge(ctrl_x + ctrl_w + 20, (y_mem_ack + ctrl_y + 160)/2, "mem_ack", color="#15803d", bg="#f0fdf4", border="#bbf7d0", font_size=9.5))

    # =========================================================================
    # 6. SHARED SIGNALS & LEGEND FOOTER
    # =========================================================================
    svg.append(f'''
  <!-- Global Clocks and Resets -->
  <rect x="{cache_x + 30}" y="{cache_y + cache_h - 45}" width="{cache_w - 60}" height="32" rx="6" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>
  <text x="{cache_x + cache_w/2}" y="{cache_y + cache_h - 25}" text-anchor="middle" fill="#475569" font-size="11" font-weight="600">
    Synchronous System Clock: <tspan fill="#0f172a" font-weight="700">clk ↑</tspan> | Active-Low Synchronous Reset: <tspan fill="#dc2626" font-weight="700">rst_n</tspan> (clears all 64 valid bits &amp; resets FSM to S_IDLE in 1 cycle)
  </text>

  <!-- Legend in Bottom Left -->
  <g filter="url(#card-shadow)">
    <rect x="{cpu_x}" y="730" width="270" height="160" rx="8" fill="#ffffff" stroke="#94a3b8" stroke-width="1.2"/>
    <text x="{cpu_x + 14}" y="752" fill="#0f172a" font-size="12" font-weight="700">SIGNAL &amp; BUS LEGEND</text>
    <line x1="{cpu_x+10}" y1="760" x2="{cpu_x+260}" y2="760" stroke="#e2e8f0" stroke-width="1"/>

    <line x1="{cpu_x+16}" y1="776" x2="{cpu_x+50}" y2="776" stroke="#2563eb" stroke-width="2.5" marker-end="url(#arrow-blue)"/>
    <text x="{cpu_x+60}" y="780" fill="#1e293b" font-size="10.5">CPU Request Buses / Strobes</text>

    <line x1="{cpu_x+16}" y1="800" x2="{cpu_x+50}" y2="800" stroke="#16a34a" stroke-width="2.5" marker-end="url(#arrow-green)"/>
    <text x="{cpu_x+60}" y="804" fill="#1e293b" font-size="10.5">Cache Response Data / Status / Counters</text>

    <line x1="{cpu_x+16}" y1="824" x2="{cpu_x+50}" y2="824" stroke="#dc2626" stroke-width="2.5" marker-end="url(#arrow-red)"/>
    <text x="{cpu_x+60}" y="828" fill="#1e293b" font-size="10.5">Main Memory Request Bus / Strobes</text>

    <line x1="{cpu_x+16}" y1="848" x2="{cpu_x+50}" y2="848" stroke="#d97706" stroke-width="2.5" marker-end="url(#arrow-amber)"/>
    <text x="{cpu_x+60}" y="852" fill="#1e293b" font-size="10.5">Internal Decoded Address Fields</text>

    <line x1="{cpu_x+16}" y1="872" x2="{cpu_x+50}" y2="872" stroke="#4f46e5" stroke-width="2" stroke-dasharray="4,2" marker-end="url(#arrow-indigo)"/>
    <text x="{cpu_x+60}" y="876" fill="#1e293b" font-size="10.5">FSM Control Strobes &amp; Enables</text>
  </g>
''')

    # Close SVG
    svg.append('</svg>\n')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(''.join(svg))
    print(f"Generated clean SVG at: {output_path}")

if __name__ == '__main__':
    generate_svg('/Users/ash/CascadeProjects/projects..../MCA/mca-capstone/docs/architecture_block_diagram.svg')
