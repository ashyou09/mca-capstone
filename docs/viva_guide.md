# Phase II Project Interview & Viva Preparation Guide

Unified technical Q&A guide covering both project-wide fundamentals (for all 5 members) and individual module ownership for **M1–M5**.

---

## 1. Core Project Fundamentals (Every Member Must Know)

**Q1. What problem does this project solve?**
Processors execute much faster than main memory (DRAM). Without a cache, every word read stalls for `MEM_LATENCY` or more cycles. Our direct-mapped cache buffers recently and nearby accessed blocks so hits return in **1 clock cycle** instead of **22 clock cycles**.

**Q2. What are the baseline parameters and how does address breakdown work?**
- **Address Width:** 32 bits (`cpu_addr[31:0]`), word-aligned (`cpu_addr[1:0]` ignored)
- **Cache Size:** 1 KiB (`CACHE_BYTES = 1024`)
- **Block Size:** 16 Bytes = 4 × 32-bit words (`BLOCK_BYTES = 16`)
- **Number of Cache Lines:** $1024 / 16 = 64$ lines
- **Bit Partition:**
  - **Offset (`addr[3:0]`):** 4 bits ($\log_2 16$). Inside it, `addr[3:2]` is the 2-bit `word_sel`.
  - **Index (`addr[9:4]`):** 6 bits ($\log_2 64$) selecting line `0..63`.
  - **Tag (`addr[31:10]`):** 22 bits ($32 - 6 - 4$) uniquely identifying the memory block.

**Q3. How fast is a hit vs. a miss, and what is the miss penalty?**
- **Hit Time:** **1 clock cycle** (asynchronous RAM reads + combinational tag compare + Mealy `cpu_ready`).
- **Miss Latency:** $W \times (L + 1) + 2 = 4 \times (4 + 1) + 2 = \mathbf{22\text{ cycles}}$ for $W=4$ words and `MEM_LATENCY` $L=4$.
  - 1 cycle in `S_IDLE` to detect the miss (`stat_miss`)
  - 4 words × 5 cycles/word in `S_REFILL` (each word waits $L=4$ cycles for `mem_ack`, plus 1 cycle before the next word starts)
  - 1 cycle in `S_RESPOND` to return `cpu_rdata` from `data_ram`
- **Miss Penalty:** $\text{Miss Latency} - \text{Hit Time} = 22 - 1 = \mathbf{21\text{ cycles}}$.
- **AMAT Formula:** $\text{AMAT} = \text{Hit Time} + (\text{Miss Rate} \times \text{Miss Penalty}) = 1 + (\text{Miss Rate} \times 21)$.

---

## 2. M1 — Pankaj Baid (Team Lead, System Architect & Controller FSM)
**Owned files:** `rtl/cache_controller.v`, `rtl/cache_top.v`, `docs/fsm.md`, `docs/address_breakdown.md`

- **Why is `cache_controller.v` a Mealy machine in `S_IDLE`?**
  If `cpu_ready` were a pure Moore output (registered in the next state), every cache hit would take at least 2 cycles. Using combinational Mealy logic in `S_IDLE` (`cpu_ready = cpu_valid & hit & !is_write`) guarantees **1-cycle hits**.
- **Why does `S_RESPOND` exist instead of raising `cpu_ready` directly on the 4th `mem_ack`?**
  The 4th word and `tag_we`/`valid_we` are written into the RAMs on the rising clock edge of the 4th `mem_ack`. `S_RESPOND` waits 1 cycle so `cpu_rdata` reads cleanly through the single asynchronous `data_ram` read path without extra bypass multiplexers.
- **How do you prevent double-counting `stat_hit` / `stat_miss`?**
  Rule 4.1 requires exactly one stat pulse per request. `stat_miss` pulses in `S_IDLE` when a miss is first detected, and the FSM immediately transitions to `S_REFILL`. Upon completing refill, it finishes in `S_RESPOND` without re-evaluating `S_IDLE`, so neither counter triggers twice.
- **What does the `WRITE_SUPPORT` parameter do?**
  - `WRITE_SUPPORT = 0` (baseline): Any request with `cpu_we=1` is safely treated as a read so the CPU bus never deadlocks.
  - `WRITE_SUPPORT = 1` (stretch): Implements **write-through, no-write-allocate** using a 4th state `S_WRITE`. Write hits update both `data_ram` and main memory; write misses write only to main memory (taking $L + 2 = 6$ cycles for $L=4$).

---

## 3. M2 — Ashutosh Singh (Storage Datapath Engineer)
**Owned files:** `rtl/addr_decoder.v`, `rtl/tag_ram.v`, `rtl/valid_ram.v`, `rtl/data_ram.v`, `rtl/tag_comparator.v`, `tb/tb_*.v`

- **How is parameterization achieved with zero hard-coded sizes?**
  Every module computes field and array widths dynamically from `ADDR_W`, `CACHE_BYTES`, and `BLOCK_BYTES` using Verilog-2012 `$clog2(...)`. All 5 M2 unit testbenches test across 16 configurations (`CACHE_BYTES` $\in \{512, 1024, 2048, 4096\}$ × `BLOCK_BYTES` $\in \{8, 16, 32, 64\}$).
- **Why does `valid_ram.v` reset in 1 cycle while `tag_ram.v` and `data_ram.v` have no reset?**
  Resetting 8,192 bits of `data_ram` and 1,408 bits of `tag_ram` is unnecessary hardware waste (unvalid data is never hit) and blocks FPGA LUTRAM inference. `valid_ram.v` is written as a flat 64-bit flip-flop vector so synchronous `rst_n=0` clears all 64 lines in a single clock cycle, with reset taking priority over simultaneous writes.
- **Why are `tag_ram`, `valid_ram`, and `data_ram` asynchronous-read?**
  For a 1-cycle hit, `index` &rarr; RAM read &rarr; `tag_comparator` &rarr; `cpu_ready` must complete combinationally within the request cycle. Synchronous reads would push hits to 2 cycles.
- **How does `data_ram.v` handle 4-beat fills without corrupting sibling words?**
  It uses word-granular synchronous indexed part-select writes: `mem[w_index][w_word_sel*32 +: 32] <= w_word`.
- **Why is the design guaranteed latch-free?**
  Zero `always @(*)` blocks exist; all combinational logic uses continuous `assign` statements and sequential state uses `always @(posedge clk)`.

---

## 4. M3 — Narendra Singh (Main-Memory Interface & FPGA Synthesis Lead)
**Owned files:** `rtl/main_memory.v`, `synth/*`, `tb/tb_main_memory.v`, `tb/tb_m3_cache_mem.v`, `docs/main_memory.md`, `docs/synthesis.md`

- **Why is `rtl/main_memory.v` excluded from synthesis?**
  It is a deterministic simulation model (`mem[w] = w * 32'h9E3779B1` over 256 KiB / 65,536 words) simulating slow off-chip memory latency (`MEM_LATENCY` cycles). Real hardware connects `mem_*` ports to an external memory controller or bus.
- **Why does `mem_ack` add `L + 1` cycles per word instead of `L`?**
  With `MEM_LATENCY=4`, the cache presents `mem_req=1` in cycle 1, receives `mem_ack=1` in cycle 5, latches the word on that clock edge, and presents the next word address in cycle 6 — 5 cycles per word.
- **Why did synthesis report 0 Block RAMs across Generic, Xilinx, and iCE40 flows?**
  FPGA BRAM primitives require **synchronous (registered) read addresses**, whereas our cache storage uses **asynchronous reads** for 1-cycle hits. On Xilinx 7-Series, Yosys maps Tag and Data storage into **150 distributed LUTRAM (`RAM64X1S`) primitives** and 312 logic LUTs (`valid_ram` maps to FFs).
- **How were the `83.15 MHz` iCE40 Fmax numbers measured?**
  `cache_top` itself has 266 port bits (exceeding the iCE40 HX8K `ct256` pin count) and overflows HX8K's 7,680 logic cells when synthesized as flip-flops. Wrapping it with registered I/O flip-flops in `synth/fmax_wrap.v` allowed Yosys to fold the input address flip-flop into synchronous BRAM read ports (using 978 logic cells and 10 BRAMs), achieving **83.15 MHz** (up to 89.37 MHz across seeds) on `nextpnr-ice40` with a **12.03 ns** critical hit path.
- **Where does most of the generic cell area go?**
  `data_ram` accounts for **82.2%** of generic cells (22,441 of 27,313 cells), `tag_ram` 14.3%, and the FSM controller just **31 cells (0.1%, 5 FFs)**. Tag+valid metadata overhead is 18.0% at baseline (`23 / 128` bits).

---

## 5. M4 — Shreya Suman (Design Verification Engineer)
**Owned files:** `tb/tb_cache_directed.v`, `tb/tb_cache_trace.v`, `analysis/golden_model.py`, `analysis/compare.py`, `Makefile`, `docs/verification.md`

- **How does co-simulation prove bit-exact RTL correctness?**
  `tb/tb_cache_trace.v` simulates the full Verilog RTL + `main_memory` and writes `idx, op, addr, hit, rdata, latency_cycles` to `analysis/results/<trace>_sim.csv`. `analysis/golden_model.py` simulates the exact same cache parameters and blocking FSM timing in Python (`<trace>_golden.csv`), and `analysis/compare.py` asserts every single row matches exactly (32,776 accesses across all 8 traces: **0 mismatches**).
- **What do the 10 scenarios (146 assertions) in `tb_cache_directed.v` verify?**
  Cold reset at `0x0` (must miss), immediate temporal hit, 4-word spatial hits, non-zero offset refill (`0x1008`), ping-pong conflict misses (`0x2010` vs `0x2410` on index 1), stale data overwrite check, 64-line full-capacity fill & re-read, mid-refill synchronous reset, exact single-cycle counter pulses, and cycle-accurate latency (1 vs. 22 cycles).
- **How did fault-injection mutation testing prove testbench strength?**
  Three deliberate RTL bugs were injected and confirmed caught:
  1. Setting `valid_bits` to `1` on reset &rarr; caught by TC-08 (4 errors).
  2. Ignoring `valid` inside `tag_comparator` &rarr; caught by TC-08 (4 errors).
  3. Truncating lower 4 bits of tag compare &rarr; caught across TC-04, TC-05, TC-06 (17 errors).

---

## 6. M5 — Ranvendra Pratap Singh (Workload & Architectural Analysis Lead)
**Owned files:** `traces/gen_traces.py`, `analysis/analyze.py`, `docs/hit_miss_report.md`, `docs/viva_m5.md`, `report/ieee_project_report.pdf`

- **Why design seven different workloads, and what do their results prove?**
  - `loop` (**99.22% hit**, AMAT 1.164): 512 B working set fits in half the cache &rarr; isolates **temporal locality**.
  - `seq` & `matrix_row` (**75.00% hit**, AMAT 6.250): 4 words per 16 B block gives 1 miss + 3 hits &rarr; isolates **spatial locality**.
  - `matrix_col` (**0.00% hit**, AMAT 22.000): Same 64×64 matrix as `matrix_row`, but 256-byte column stride maps consecutive row blocks onto colliding indices &rarr; **3,072 conflict misses**.
  - `stride` (**0.00% hit**, AMAT 22.000): Includes 1,024-byte ($A$ vs $A+1024$) ping-pong pairs landing on the exact same line index.
  - `mixed` (**79.42% hit**, AMAT 5.322) & `random` (**0.46% hit**, AMAT 21.903): Contrast realistic hot/cold traffic against uniform low-locality access across 256 KiB.
- **How are Three-C misses (Compulsory, Conflict, Capacity) separated in `analyze.py`?**
  Compulsory = first reference to a block. For subsequent direct-mapped misses, `analyze.py` runs an equal-capacity **64-line fully associative LRU shadow cache** in parallel: if the shadow cache hits, the miss is a **Conflict** miss; if the shadow cache also misses, it is a **Capacity** miss.
- **What is the key takeaway from the 16-configuration parameter sweep?**
  Increasing cache size monotonically reduces capacity and conflict misses. However, increasing **block size** helps sequential workloads up to a point while hurting random/strided workloads: larger blocks yield fewer cache lines (more conflicts) and scale miss penalty linearly as $W(L+1)+1$ (reaching 81 cycles at 64 B blocks). Thus 16 B–32 B blocks offer the best balance.
