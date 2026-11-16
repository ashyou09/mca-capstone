# 5-Minute Prototype Video Recording Script (Phase I Evaluation)

> **Evaluation Weightage:** 15 Marks (Phase I)  
> **Strict Time Limit:** Under 5 minutes (Target: ~4 minutes 30 seconds)  
> **Video Requirements:**
> 1. Clearly mention the project idea.
> 2. Clearly introduce the names of all 5 group members.
> 3. Demonstrate the working / progress of the prototype (Verilog, architecture diagram, live testbench run, GTKWave waveform).

---

## 🎬 Roles & Member Introduction Checklist

| Member | Name | Segment Owned | Screen Displayed |
|---|---|---|---|
| **M1** | **Pankaj Baid** | Team Intro, Project Idea & Controller FSM | Title Slide / Web Presentation Slide 1 & Slide 5 |
| **M2** | **Ashutosh Singh** | System Architecture & Storage Datapath | Architecture Diagram (`docs/architecture_block_diagram.svg`) |
| **M3** | **Narendra Singh** | Memory Model & FPGA Synthesis Results | Terminal (`docs/synthesis.md` / `synth/reports/summary.md`) |
| **M4** | **Shreya Suman** | Directed Verification & Live Terminal Demo | Terminal (`make test` live execution & 146 checks) |
| **M5** | **Ranvendra Pratap Singh** | Workload Analysis (Hit Ratio, AMAT) & Conclusion | Generated Plots (`analysis/results/*.png`) & Summary |

---

## ⏱️ Detailed Video Script (Minute-by-Minute)

### [0:00 – 0:45] Segment 1: Team Introduction & Project Idea (Speaker: Pankaj Baid)
**Visual on Screen:** Open `report/presentation.html` (Slide 1: Title and Team).

> **Pankaj Baid:**  
> "Hello everyone and respected evaluators. Welcome to our Phase I prototype demonstration for the MCA Capstone Project in Computer Architecture.  
> 
> Our project is the **Design, Hardware Verification, and Architectural Performance Analysis of a Synthesizable Direct-Mapped Cache Controller in Verilog**.  
> 
> Our team consists of five members:  
> - I am **Pankaj Baid**, serving as the Team Lead and System Architect for the Cache Controller FSM.  
> - **Ashutosh Singh**, who designed the Storage Datapath and Address Decoding modules.  
> - **Narendra Singh**, who implemented the Main Memory Interface and FPGA Synthesis workflow.  
> - **Shreya Suman**, who built the Verification Suite and bit-accurate Python Golden Model.  
> - And **Ranvendra Pratap Singh**, who engineered our Workload Trace Generator and Architectural AMAT Analysis.  
> 
> **Project Idea:** Modern CPUs operate hundreds of times faster than DRAM. To eliminate this memory wall, our project designs a high-performance 1 KiB direct-mapped cache controller with 16-byte blocks and 32-bit addresses that delivers single-cycle read hits and orchestrates a cycle-accurate 4-word refill handshake with main memory."

---

### [0:45 – 1:35] Segment 2: Architecture & Storage Datapath (Speaker: Ashutosh Singh)
**Visual on Screen:** Open `docs/architecture_block_diagram.svg`.

> **Ashutosh Singh:**  
> "Moving to the system architecture on screen:  
> 
> Our design features a clean, modular hierarchy inside `cache_top`. A 32-bit word-aligned CPU address is received by our `addr_decoder`, which extracts:  
> - A **22-bit Tag** (`addr[31:10]`)  
> - A **6-bit Index** (`addr[9:4]`), selecting one of 64 cache lines  
> - A **4-bit Offset** (`addr[3:0]`), with bits `[3:2]` selecting one of four 32-bit words.  
> 
> The 6-bit index simultaneously looks up our three storage arrays:  
> 1. `tag_ram`: 64 lines by 22 bits, mapped to distributed LUTRAM with asynchronous read.  
> 2. `valid_ram`: 64 individual flip-flops with synchronous active-low reset to clear all lines in a single clock cycle.  
> 3. `data_ram`: 64 lines of 128-bit blocks, supporting word-granular synchronous writes during memory refills.  
> 
> Our `tag_comparator` combinational block evaluates `hit = valid & (stored_tag == requested_tag)`. On a hit, data is routed through our 4-to-1 Word MUX to `cpu_rdata` in just **1 clock cycle**."

---

### [1:35 – 2:20] Segment 3: Controller FSM & Memory Handshake (Speaker: Pankaj Baid)
**Visual on Screen:** Switch to `docs/fsm.md` or Presentation Slide 5 (FSM Diagram).

> **Pankaj Baid:**  
> "When a lookup misses, our 4-state Mealy/Moore controller FSM transitions from `S_IDLE` to `S_REFILL`.  
> 
> In `S_REFILL`, the controller initiates a 4-beat handshake with main memory using `mem_req` and `mem_ack`. For each word, memory responds after `MEM_LATENCY` cycles (configured to 4 cycles). As each word arrives, `data_ram` writes it synchronously.  
> 
> Crucially, `valid_ram` and `tag_ram` are only asserted on the **fourth and final word**, guaranteeing that a half-filled line can never falsely hit. The FSM then enters `S_RESPOND` to pulse `cpu_ready`, achieving a measured miss latency of $4 \times (4+1) + 2 = \mathbf{22\text{ clock cycles}}$ and an effective miss penalty of **21 cycles**."

---

### [2:20 – 3:30] Segment 4: Live Verification & Prototype Working (Speaker: Shreya Suman)
**Visual on Screen:** Terminal window running `make test`.

> **Shreya Suman:**  
> "Now, let us demonstrate the working prototype live in terminal. I will run `make test`:  
> *(Action: Type `make test` and hit Enter in the terminal)*  
> 
> Notice the execution:  
> 1. First, all **M2 datapath unit tests** pass with zero errors.  
> 2. Next, our **M3 memory integration tests** pass across multiple latencies.  
> 3. Then, our **10-case directed verification testbench** executes: it verifies cold-start reset, temporal reuse, 4-word spatial locality, ping-pong conflict eviction between addresses `0x2010` and `0x2410`, cache capacity sweep across all 64 lines, and mid-test reset. All **146 runtime assertions pass with zero errors**.  
> 4. Finally, our automated testbench executes **eight complete memory workloads** totaling over 32,000 accesses, comparing the Verilog RTL cycle-by-cycle against our bit-accurate Python Golden Model.  
> 
> As you can see: `ALL VERIFICATION SUITE TESTS PASSED` with 100% bit-exact output match."

---

### [3:30 – 4:15] Segment 5: Synthesis & Performance Analysis (Speaker: Narendra Singh & Ranvendra Pratap Singh)
**Visual on Screen:** Switch to `docs/synthesis.md` table, then open `analysis/results/hit_ratio_by_trace.png`.

> **Narendra Singh:**  
> "For hardware synthesis, we synthesized `cache_top` across 24 configurations using Yosys.  
> - On Xilinx 7-series, the design synthesizes into **312 logic LUTs**, **150 distributed RAM cells** (`RAM64X1S`), and **133 flip-flops**, with zero inferred latches.  
> - On Lattice iCE40, static timing analysis through `nextpnr` confirms a maximum operating frequency of **83.15 MHz**."  
> 
> *(Transition to Ranvendra)*  
> 
> **Ranvendra Pratap Singh:**  
> "To evaluate architectural trade-offs, we developed seven representative workloads:  
> - Our **Repeated Loop** workload fits entirely in cache, reaching a **99.22% hit ratio** and an Average Memory Access Time (AMAT) of just **1.16 cycles**.  
> - Our **Sequential** and **Row-Major Matrix** traces achieve **75.00% hit ratio** due to 4-word spatial locality.  
> - Conversely, our **Column-Major Matrix** trace yields **0% hits**, visually demonstrating the severe conflict misses inherent to direct-mapped caches.  
> - Using an equal-capacity fully associative LRU shadow cache, our analyzer mathematically isolates Compulsory, Conflict, and Capacity misses."

---

### [4:15 – 4:45] Segment 6: Conclusion & Summary of Phase I Deliverables (Speaker: Pankaj Baid)
**Visual on Screen:** Presentation Slide 12 or GitHub Repository landing page.

> **Pankaj Baid:**  
> "In conclusion, our Phase I prototype and evaluation requirements are completely fulfilled:  
> - Fully synthesizable Verilog RTL with modular datapath hierarchy  
> - Comprehensive automated verification with 146 directed checks and 8 workload trace co-simulations passing at 100%  
> - Quantitative AMAT evaluation and 3-C miss classification  
> - Tool-driven FPGA synthesis on Xilinx 7-series and Lattice iCE40  
> - Official IEEE Project Report and GitHub repository documentation  
> 
> All source codes, testbenches, waveforms, synthesis logs, and reports are available in our GitHub repository submitted for Phase I.  
> 
> Thank you for your time and evaluation!"

---

## 🛠️ Recording Tips for the Team

1. **Platform:** Use Zoom, Google Meet, OBS Studio, or QuickTime Screen Recording.
2. **Setup:**
   - Display 1: Browser with `presentation.html` and `docs/architecture_block_diagram.svg`.
   - Display 2: Terminal with font sized to 16pt+ so command outputs are crystal clear.
3. **Execution Command in Terminal:**
   ```sh
   export PATH="/opt/homebrew/bin:$PATH"
   cd /Users/ash/CascadeProjects/projects..../MCA/mca-capstone
   make test
   ```
4. **Time Check:** Ensure recording finishes between **4:00 and 4:45 minutes** (must not exceed 5:00).
5. **Upload & Link:**
   - Upload video to **YouTube (Unlisted)** or **Google Drive (Anyone with link can view)**.
   - Paste the link into `README.md` and the Phase I Google Submission Form!
