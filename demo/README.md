# Interactive Presentation Demo (`demo/`)

Animated, offline-capable story presentation for **Direct-Mapped Cache Controller in Verilog (MCA Capstone — Phase I & II)**, structured sequentially from **Person A → Person E**.

---

## How to Open & Present

### Option 1: Direct Open (No Server Needed)
Double-click `demo/index.html` to open it directly in Chrome, Safari, or Edge.

### Option 2: Local HTTP Server (Recommended for Projectors)
From the repository root:
```sh
python3 -m http.server 8000
```
Then open: [http://localhost:8000/demo/](http://localhost:8000/demo/)

---

## Controls & Presenter Shortcuts
- **Top Chapter Bar** — 1-click jump straight to `Intro`, `A · Pankaj`, `B · Ashutosh`, `C · Narendra`, `D · Shreya`, `E · Ranvendra`, `Live Sim`, or `Summary`.
- **`→` / `Space` / `PageDown`** — Next slide
- **`←` / `PageUp`** — Previous slide
- **`N`** (or **`Notes (N)`** button in bottom bar) — Toggle plain-English **Presenter Speaker Cues** for the current slide.
- **Click any Diagram / Waveform / Plot** — Open full-screen Lightbox zoom (`Esc` or click outside to close).
- **`1` – `8`** — Quick jump (`1` Intro, `2` Ch. A, `3` Ch. B, `4` Ch. C, `5` Ch. D, `6` Ch. E, `7` Live Simulator, `8` Summary)
- **`F`** — Toggle Fullscreen (`Home`/`End` for first/last slide)

---

## Slide Deck Order (20 Slides)
1. Title & Clickable Team Lineup (`A–E`)
2. The Memory Wall (1-cycle vs. 22-cycle live race)
3. Baseline Parameters & Zoomable Architecture Diagram
4. Team Story Map (`A → B → C → D → E`)
5. **Chapter A Cover:** Pankaj Baid (`M1`)
6. **A · Controller FSM** (Interactive HIT / MISS simulator)
7. **Chapter B Cover:** Ashutosh Singh (`M2`)
8. **B · 32-Bit Address Decoder** (Interactive bit visualizer + `0x1A2C`/`0x1E2C` conflict presets)
9. **B · Storage & Hit Check** (Quick presets + interactive 64-line cache lookup & 1-cycle Reset)
10. **Chapter C Cover:** Narendra Singh (`M3`)
11. **C · Main Memory Handshake** (Animated 22-cycle burst refill waveform)
12. **C · FPGA Synthesis & Timing** (`312 LUTs + 150 LUTRAMs`, `83.15 MHz`)
13. **Chapter D Cover:** Shreya Suman (`M4`)
14. **D · Verification Pyramid** (`146 / 146` Directed checks)
15. **D · RTL vs. Python Golden Model** (`32,776` matched accesses + 3 Mutation Tests + Zoomable Waveform)
16. **Chapter E Cover:** Ranvendra Pratap Singh (`M5`)
17. **E · Workloads & Hit Ratios** (`99.22%` down to `0.00%`)
18. **E · 3-C Misses & AMAT** (Stacked 3-C breakdown + interactive AMAT slider + Zoomable Block-Size Plot)
19. **Finale: Live 48-Access Workload Simulator** (Sequential, Loop, Conflict, Random with plain-English log)
20. **Summary & Questions**
