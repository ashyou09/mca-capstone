#!/usr/bin/env python3
"""
Generate a publication-grade IEEE Conference 2-column format Project Report
covering Abstract, Literature Review, Proposed Solution, Individual Contributions,
and References, and compile it to PDF.
"""
import subprocess
import os

def generate_html(output_path):
    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Direct-Mapped Cache Controller: Design, Verification, and Performance Evaluation</title>
<style>
  @page {
    size: letter;
    margin: 0.7in 0.65in 0.75in 0.65in;
  }
  body {
    font-family: 'Times New Roman', Times, serif;
    font-size: 10pt;
    line-height: 1.18;
    color: #000000;
    margin: 0;
    padding: 0;
    text-align: justify;
    text-justify: inter-word;
  }
  .title-area {
    text-align: center;
    margin-bottom: 18pt;
  }
  h1.paper-title {
    font-size: 20pt;
    font-weight: bold;
    margin: 0 0 10pt 0;
    line-height: 1.15;
  }
  .subtitle {
    font-size: 12pt;
    font-style: italic;
    margin-bottom: 12pt;
  }
  .authors-table {
    width: 100%;
    margin: 0 auto 16pt auto;
    border-collapse: collapse;
  }
  .authors-table td {
    text-align: center;
    vertical-align: top;
    font-size: 9pt;
    line-height: 1.25;
    padding: 0 6pt;
  }
  .author-name {
    font-size: 10.5pt;
    font-weight: bold;
    display: block;
    margin-bottom: 2pt;
  }
  .author-role {
    font-size: 8.5pt;
    color: #333333;
    font-style: italic;
    display: block;
    margin-bottom: 2pt;
  }
  .author-affil {
    font-size: 8pt;
    color: #444444;
  }
  .author-email {
    font-family: 'Courier New', monospace;
    font-size: 7.5pt;
    color: #222222;
  }

  .content-columns {
    column-count: 2;
    column-gap: 0.28in;
    column-rule: 0.5pt solid #e0e0e0;
  }

  .abstract-box {
    margin-bottom: 12pt;
    padding-bottom: 6pt;
    border-bottom: 0.5pt solid #cccccc;
  }
  .abstract-title {
    font-weight: bold;
    font-style: italic;
    font-size: 9pt;
  }
  .abstract-text {
    font-size: 9pt;
    font-weight: bold;
    line-height: 1.2;
    text-align: justify;
  }
  .index-terms {
    font-size: 8.5pt;
    font-style: italic;
    margin-top: 4pt;
  }
  .index-terms-title {
    font-weight: bold;
    font-style: italic;
  }

  h2.ieee-section {
    font-size: 10pt;
    font-weight: bold;
    text-transform: uppercase;
    text-align: center;
    margin: 14pt 0 6pt 0;
    letter-spacing: 0.5pt;
  }
  h3.ieee-subsection {
    font-size: 10pt;
    font-weight: bold;
    font-style: italic;
    margin: 10pt 0 4pt 0;
  }
  p {
    margin: 0 0 6pt 0;
    text-indent: 14pt;
  }
  p.no-indent {
    text-indent: 0;
  }

  .figure-box {
    text-align: center;
    margin: 10pt 0;
    page-break-inside: avoid;
  }
  .figure-box img, .figure-box svg {
    max-width: 100%;
    height: auto;
  }
  .figure-caption {
    font-size: 8.5pt;
    margin-top: 4pt;
    text-align: center;
    font-weight: normal;
  }
  .figure-caption b {
    font-weight: bold;
  }

  .table-box {
    margin: 10pt 0;
    page-break-inside: avoid;
    font-size: 8pt;
    text-align: center;
  }
  .table-title {
    font-size: 8.5pt;
    font-weight: bold;
    text-transform: uppercase;
    margin-bottom: 4pt;
    text-align: center;
  }
  table.ieee-table {
    width: 100%;
    border-collapse: collapse;
    margin: 0 auto;
    font-size: 8pt;
  }
  table.ieee-table th {
    border-top: 1pt solid #000000;
    border-bottom: 0.5pt solid #000000;
    padding: 3pt 2pt;
    text-align: left;
    font-weight: bold;
  }
  table.ieee-table td {
    padding: 2.5pt 2pt;
    border-bottom: 0.25pt solid #dddddd;
    text-align: left;
  }
  table.ieee-table tr:last-child td {
    border-bottom: 1pt solid #000000;
  }

  .equation {
    text-align: center;
    margin: 6pt 0;
    font-style: italic;
    font-size: 9.5pt;
  }
  .equation .eq-num {
    float: right;
    font-style: normal;
  }

  ul, ol {
    margin: 4pt 0 6pt 16pt;
    padding: 0;
  }
  li {
    margin-bottom: 2pt;
    font-size: 9.5pt;
  }

  .reference-item {
    font-size: 8pt;
    line-height: 1.15;
    margin-bottom: 4pt;
    padding-left: 18pt;
    text-indent: -18pt;
    text-align: justify;
  }
</style>
</head>
<body>

<div class="title-area">
  <h1 class="paper-title">Design, Hardware Verification, and Architectural Performance Evaluation of a Synthesizable Direct-Mapped Cache Controller</h1>
  <div class="subtitle">Phase I Project Report — MCA Capstone in Computer Architecture</div>

  <table class="authors-table">
    <tr>
      <td>
        <span class="author-name">Pankaj Baid</span>
        <span class="author-role">M1: System Architect & Lead</span>
        <span class="author-affil">Dept. of Computer Science</span>
        <span class="author-email">pankaj.baid2024@nst.rishihood.edu.in</span>
      </td>
      <td>
        <span class="author-name">Ashutosh Singh</span>
        <span class="author-role">M2: Storage Datapath Engineer</span>
        <span class="author-affil">Dept. of Computer Science</span>
        <span class="author-email">ashutosh.singh2024@nst.rishihood.edu.in</span>
      </td>
      <td>
        <span class="author-name">Narendra Singh</span>
        <span class="author-role">M3: Memory & Synthesis Lead</span>
        <span class="author-affil">Dept. of Computer Science</span>
        <span class="author-email">narendrasingh.coder@gmail.com</span>
      </td>
    </tr>
    <tr>
      <td colspan="1" style="padding-top: 8pt;">
        <span class="author-name">Shreya Suman</span>
        <span class="author-role">M4: Verification Engineer</span>
        <span class="author-affil">Dept. of Computer Science</span>
        <span class="author-email">shreya.212suman@gmail.com</span>
      </td>
      <td colspan="2" style="padding-top: 8pt;">
        <span class="author-name">Ranvendra Pratap Singh</span>
        <span class="author-role">M5: Workload & Performance Analyst</span>
        <span class="author-affil">Dept. of Computer Science, Rishihood University, Sonipat, India</span>
        <span class="author-email">ranvendra.singh2024@nst.rishihood.edu.in</span>
      </td>
    </tr>
  </table>
</div>

<div class="content-columns">

  <div class="abstract-box">
    <span class="abstract-title">Abstract</span>—<span class="abstract-text">The growing latency disparity between high-performance processor cores and main memory—known as the memory wall—requires efficient cache memory hierarchies. This paper presents the design, synthesizable Verilog implementation, formal verification, and architectural evaluation of a parameterized direct-mapped cache controller. Configured with a 1 KiB capacity, 16-byte blocks (64 lines), and 32-bit word-aligned addressing, the microarchitecture employs an address decoder ($clog2 parameterization), a 64×22-bit Tag RAM, a 64×1-bit Valid RAM with single-cycle synchronous clear, a 64×128-bit Data RAM with word-granular write enables, a combinational Tag Comparator, and a four-state Mealy/Moore Controller FSM. The controller guarantees a single-cycle read hit latency and orchestrates a four-word handshake with main memory, incurring a deterministic 22-cycle miss latency for an access latency of 4 cycles per word. Verification is established through a 10-scenario directed testbench with 146 runtime assertions alongside an access-by-access trace co-simulation against a bit-accurate Python golden reference model. Fault-injection mutation testing confirms robust bug detection. Workload evaluation across seven deterministic 4096-access traces yields hit ratios from 0.00% (column-major, stride) to 99.22% (loop), with measured Average Memory Access Time (AMAT) matching theoretical derivations. Yosys hardware synthesis on Xilinx 7-series yields 312 logic LUTs and 150 distributed RAMs (RAM64X1S), confirming that asynchronous reads map to LUTRAM and achieve 83.15 MHz timing on Lattice iCE40.</span>
    <div class="index-terms"><span class="index-terms-title">Index Terms</span>—Cache memory, Direct-mapped cache, Finite State Machine (FSM), Hardware verification, Locality of reference, AMAT, FPGA synthesis, Verilog HDL.</div>
  </div>

  <h2 class="ieee-section">I. Introduction</h2>
  <p>In modern computer systems, microprocessor frequencies have outpaced dynamic random-access memory (DRAM) access latencies by multiple orders of magnitude. A memory request issued by a modern processing pipeline to un-cached main storage may incur dozens or hundreds of clock cycles of stall latency. To mitigate this processor–memory performance gap, computer architectures implement hierarchical memory structures.</p>
  <p>Caches exploit two temporal and spatial properties of program execution: <i>temporal locality</i>, wherein memory locations referenced recently are likely to be accessed again in the near future; and <i>spatial locality</i>, wherein locations adjacent to recently referenced addresses are likely to be accessed consecutively.</p>
  <p>This project implements and evaluates a parameterized direct-mapped cache controller in synthesizable Verilog HDL. Our design realizes single-cycle read hit access, single-cycle reset invalidation of all cache lines, and a cycle-accurate four-beat burst refill protocol with a behavioral main memory subsystem. We evaluate memory access traces, quantify Average Memory Access Time (AMAT), decompose misses via Hill's Three-C model, and demonstrate hardware feasibility through multi-target FPGA synthesis.</p>

  <h2 class="ieee-section">II. Literature Review</h2>
  <p>The foundational concept of cache storage was introduced by Maurice Wilkes in 1965 [1], proposing "slave memories" to automatically retain active memory sectors without explicit software intervention. In his seminal survey, A. J. Smith [2] comprehensively categorized cache placement policies, line replacement heuristics, and write strategies, formalizing the design space of direct-mapped versus set-associative caches.</p>
  <p>Direct-mapped placement provides minimal access latency and zero placement search logic because every physical address maps to exactly one predetermined cache line. However, direct mapping introduces susceptibility to <i>conflict misses</i>, occurring when distinct memory blocks contend for the same cache line index. Mark D. Hill and A. J. Smith [3] formalized the seminal "Three-C" taxonomy, categorizing misses into:</p>
  <ul>
    <li><b>Compulsory (Cold) Misses:</b> Unavoidable first references to a memory block.</li>
    <li><b>Capacity Misses:</b> Misses occurring due to the finite storage volume of the cache, present even in fully associative caches of identical capacity.</li>
    <li><b>Conflict Misses:</b> Misses arising from mapping constraints where lines collide within the same set, avoidable through associativity.</li>
  </ul>
  <p>To reduce conflict penalties in direct-mapped architectures without increasing hit critical paths, N. P. Jouppi [4] proposed victim caches and prefetching buffers. In contemporary computer architecture pedagogy, Hennessy and Patterson [5] established the quantitative framework governing memory hierarchy optimization, defining Average Memory Access Time (AMAT) as:</p>
  <div class="equation">
    \text{AMAT} = \text{Hit Time} + (\text{Miss Rate} \times \text{Miss Penalty})
    <span class="eq-num">(1)</span>
  </div>
  <p class="no-indent">Equation (1) encapsulates the trade-off between hit latency, miss probability, and line transfer duration. In modern FPGA architectures, memory mapping is further constrained by primitive structures: synchronous Block RAMs (BRAM) versus asynchronous distributed SelectRAM (LUTRAM) [6]. A true one-cycle hit direct-mapped cache requires asynchronous read capabilities, dictating distributed LUTRAM allocation.</p>

  <h2 class="ieee-section">III. Proposed Solution & Architecture</h2>

  <h3 class="ieee-subsection">A. Baseline System Parameters</h3>
  <p>The microarchitecture operates on 32-bit byte addresses ($ADDR\_W=32$) with word-aligned accesses (bits [1:0] ignored). The baseline configuration specifies:</p>
  <ul>
    <li><b>Cache Capacity ($C$):</b> 1024 Bytes (1 KiB).</li>
    <li><b>Block Size ($B$):</b> 16 Bytes (4 words of 32 bits each).</li>
    <li><b>Number of Lines ($N$):</b> $N = C / B = 1024 / 16 = 64$ lines.</li>
  </ul>

  <h3 class="ieee-subsection">B. Address Decomposition</h3>
  <p>The 32-bit address is partitioned into three distinct fields derived algorithmically via Verilog <code>$clog2</code> functions:</p>
  <div class="equation">
    \text{Offset Width} = \log_2(16) = 4\text{ bits } (addr[3:0])
    <span class="eq-num">(2)</span>
  </div>
  <div class="equation">
    \text{Index Width} = \log_2(64) = 6\text{ bits } (addr[9:4])
    <span class="eq-num">(3)</span>
  </div>
  <div class="equation">
    \text{Tag Width} = 32 - 6 - 4 = 22\text{ bits } (addr[31:10])
    <span class="eq-num">(4)</span>
  </div>
  <p class="no-indent">Within the 4-bit block offset, bits [3:2] yield the 2-bit word select ($word\_sel$), identifying which 32-bit word within the 128-bit line is delivered to the CPU.</p>

  <div class="table-box">
    <div class="table-title">Table I: Submodule Interface & Storage Allocations</div>
    <table class="ieee-table">
      <thead>
        <tr><th>Module</th><th>Dimensions</th><th>Read / Write Timing</th><th>FPGA Cell</th></tr>
      </thead>
      <tbody>
        <tr><td><code>addr_decoder</code></td><td>32-bit combinatorial</td><td>Combinational</td><td>Wires / Slices</td></tr>
        <tr><td><code>tag_ram</code></td><td>64 × 22 bits</td><td>Async Read, Sync Write</td><td>LUTRAM (RAM64X1S)</td></tr>
        <tr><td><code>valid_ram</code></td><td>64 × 1 bit</td><td>Async Read, Sync Clear</td><td>64 Flip-Flops (FDRE)</td></tr>
        <tr><td><code>data_ram</code></td><td>64 × 128 bits</td><td>Async Read, Word Write</td><td>LUTRAM (RAM64X1S)</td></tr>
        <tr><td><code>tag_comparator</code></td><td>22-bit comparator</td><td>Combinational</td><td>XNOR / AND tree</td></tr>
        <tr><td><code>cache_controller</code></td><td>4-state FSM</td><td>Mealy/Moore Hybrid</td><td>Logic LUTs & FFs</td></tr>
      </tbody>
    </table>
  </div>

  <h3 class="ieee-subsection">C. Storage Datapath Modules</h3>
  <p><b>Valid RAM:</b> Implemented as a flat 64-bit register vector rather than a memory primitive. This architectural decision permits all 64 valid bits to be reset to zero synchronously in exactly one clock cycle upon assertion of active-low <code>rst_n</code>, preventing stale tag matches post-reset.</p>
  <p><b>Data RAM:</b> Features word-granular synchronous write enables (<code>w_word_sel</code>). During memory refills, the controller stores individual 32-bit words as memory acknowledgments arrive without overwriting or corrupting neighboring words within the 128-bit cache line.</p>
  <p><b>Tag Comparator:</b> Performs combinational equality evaluation: <code>hit = valid & (stored_tag == requested_tag)</code>. If valid is unasserted, a miss is guaranteed even if stored tag bits match the request.</p>

  <h3 class="ieee-subsection">D. Cache Controller Finite State Machine</h3>
  <p>The controller coordinates hit servicing and memory refill transactions through four distinct operational states:</p>
  <ol>
    <li><b><code>S_IDLE</code>:</b> Monitors <code>cpu_valid</code>. Because RAM reads and tag comparison are combinational, a hit is resolved in the same cycle. The controller asserts <code>cpu_ready</code> and <code>stat_hit</code> in cycle 1, providing a 1-cycle hit latency. On a miss, it pulses <code>stat_miss</code> and transitions to <code>S_REFILL</code>.</li>
    <li><b><code>S_REFILL</code>:</b> Issues <code>mem_req</code> to main memory for four consecutive words starting from the block-aligned address base. For each beat, memory asserts <code>mem_ack</code> after <code>MEM_LATENCY</code> cycles. The controller writes each word into <code>data_ram</code>. On the fourth word ($word\_cnt = 3$), the controller asserts <code>tag_we</code> and <code>valid_we</code>, committing the line, and advances to <code>S_RESPOND</code>.</li>
    <li><b><code>S_RESPOND</code>:</b> The refilled block is now valid in <code>data_ram</code>. The controller asserts <code>cpu_ready</code>, routing the requested word to <code>cpu_rdata</code>, and transitions back to <code>S_IDLE</code>.</li>
    <li><b><code>S_WRITE</code>:</b> Supported when <code>WRITE_SUPPORT=1</code> for write-through, no-write-allocate transactions.</li>
  </ol>

  <h3 class="ieee-subsection">E. Miss Penalty and Latency Formulation</h3>
  <p>For block size of $W=4$ words and memory latency $L = \text{MEM\_LATENCY} = 4$ cycles, end-to-end miss service time is formulated as:</p>
  <div class="equation">
    \text{Miss Latency} = W \times (L + 1) + 2 = 4 \times (4 + 1) + 2 = 22\text{ cycles}
    <span class="eq-num">(5)</span>
  </div>
  <div class="equation">
    \text{Miss Penalty} = \text{Miss Latency} - \text{Hit Time} = 22 - 1 = 21\text{ cycles}
    <span class="eq-num">(6)</span>
  </div>
  <p class="no-indent">The term $(L+1)$ reflects memory latency plus one handshake acknowledge cycle; the additive $+2$ represents one miss-detection cycle in <code>S_IDLE</code> and one response cycle in <code>S_RESPOND</code>.</p>

  <h2 class="ieee-section">IV. Individual Contributions</h2>
  <p>The capstone project was executed across five specialized engineering milestones with verified version control accountability:</p>
  <ul>
    <li><b>Pankaj Baid (M1 — Team Lead & Architect):</b> Formulated system architecture; authored top-level <code>cache_top.v</code>; designed and verified the 4-state controller FSM (<code>cache_controller.v</code>); established timing contracts; authored FSM state tables and address derivation documentation.</li>
    <li><b>Ashutosh Singh (M2 — Storage Datapath):</b> Authored parameterized <code>addr_decoder.v</code>, <code>tag_ram.v</code>, <code>valid_ram.v</code>, <code>data_ram.v</code>, and <code>tag_comparator.v</code>; engineered single-cycle valid clear and word-granular write logic; authored 5 self-checking unit testbenches.</li>
    <li><b>Narendra Singh (M3 — Memory Interface & Synthesis):</b> Developed behavioral <code>main_memory.v</code> with deterministic hash initialization and configurable latency; created automated Yosys synthesis suite across Generic, Xilinx, and iCE40 targets; executed 24 sweep configurations; established 83.15 MHz Fmax static timing.</li>
    <li><b>Shreya Suman (M4 — Verification Lead):</b> Engineered bit-accurate Python reference model (<code>golden_model.py</code>); developed 10-scenario directed testbench (<code>tb_cache_directed.v</code>) with 146 assertions; developed automated trace testbench (<code>tb_cache_trace.v</code>) and comparison engine (<code>compare.py</code>); conducted fault-injection mutation testing.</li>
    <li><b>Ranvendra Pratap Singh (M5 — Workload Analysis):</b> Authored deterministic workload generator (<code>gen_traces.py</code>); developed analytical engine (<code>analyze.py</code>) implementing Three-C miss decomposition and AMAT calculations; conducted 16-parameter architecture sweep; coordinated technical reporting.</li>
  </ul>

  <h2 class="ieee-section">V. Verification & Hardware Validation</h2>

  <h3 class="ieee-subsection">A. Directed Verification Suite</h3>
  <p>The directed verification testbench (<code>tb_cache_directed.v</code>) validates 10 exhaustive hardware scenarios covering reset semantics, spatial/temporal reuse, address aliasing, and fault injection:</p>
  <ul>
    <li><b>TC-01 (Reset Invalidation):</b> Reading <code>0x00000000</code> post-reset results in MISS despite matching tag 0, verifying valid bit gating.</li>
    <li><b>TC-02 (Temporal Locality):</b> Immediate re-read of <code>0x00000000</code> reports HIT with 1-cycle latency.</li>
    <li><b>TC-03 (Spatial Locality):</b> Accesses to consecutive words <code>0x04</code>, <code>0x08</code>, and <code>0x0C</code> report HITs, proving 16-byte block refill integrity.</li>
    <li><b>TC-05 (Conflict Misses):</b> Alternating reads between addresses <code>0x2010</code> and <code>0x2410</code> (same index 1, tags 8 and 9) yield 100% conflict misses.</li>
    <li><b>TC-08 (Mid-Test Reset):</b> Pulsing synchronous reset during active operation purges all valid bits and resets counters.</li>
  </ul>
  <p class="no-indent">All 146 directed assertions execute with 0 detected errors.</p>

  <h3 class="ieee-subsection">B. Mutation Analysis</h3>
  <p>Deliberate RTL fault injections confirmed testbench rigor: (1) Inverting valid reset logic in <code>valid_ram.v</code> was detected at cycle 17,716,000 by TC-08; (2) Omitting valid gating in <code>tag_comparator.v</code> caused immediate failure on TC-01; (3) Corrupting word refill offsets caused immediate data comparison mismatch on TC-06.</p>

  <h2 class="ieee-section">VI. Experimental Results & Discussion</h2>

  <div class="table-box">
    <div class="table-title">Table II: Benchmark Workload Results (1 KiB Cache, 16 B Block, Latency 4)</div>
    <table class="ieee-table">
      <thead>
        <tr><th>Workload Trace</th><th>Hits</th><th>Misses</th><th>Hit Ratio</th><th>Compulsory</th><th>Conflict</th><th>Capacity</th><th>AMAT</th></tr>
      </thead>
      <tbody>
        <tr><td><b>Loop</b></td><td>4064</td><td>32</td><td>99.22%</td><td>32</td><td>0</td><td>0</td><td>1.164 cyc</td></tr>
        <tr><td><b>Mixed</b></td><td>3253</td><td>843</td><td>79.42%</td><td>618</td><td>217</td><td>8</td><td>5.322 cyc</td></tr>
        <tr><td><b>Matrix Row</b></td><td>3072</td><td>1024</td><td>75.00%</td><td>1024</td><td>0</td><td>0</td><td>6.250 cyc</td></tr>
        <tr><td><b>Sequential</b></td><td>3072</td><td>1024</td><td>75.00%</td><td>1024</td><td>0</td><td>0</td><td>6.250 cyc</td></tr>
        <tr><td><b>Random</b></td><td>19</td><td>4077</td><td>0.46%</td><td>3616</td><td>2</td><td>459</td><td>21.903 cyc</td></tr>
        <tr><td><b>Matrix Col</b></td><td>0</td><td>4096</td><td>0.00%</td><td>1024</td><td>3072</td><td>0</td><td>22.000 cyc</td></tr>
        <tr><td><b>Stride</b></td><td>0</td><td>4096</td><td>0.00%</td><td>2390</td><td>1364</td><td>342</td><td>22.000 cyc</td></tr>
      </tbody>
    </table>
  </div>

  <p>As detailed in Table II, the <b>Repeated Loop</b> workload achieves a 99.22% hit ratio because its 512-byte working set fits entirely within the 1 KiB capacity, yielding an AMAT of 1.164 cycles. <b>Sequential</b> and <b>Row-Major Matrix</b> traversals achieve exactly 75.00% hits, validating the theoretical $1 - (1/4) = 0.75$ spatial reuse boundary. Conversely, <b>Column-Major Matrix</b> access across the identical 64×64 dataset yields 0% hits, where the 256-byte row stride causes severe index thrashing (3,072 conflict misses).</p>

  <h2 class="ieee-section">VII. FPGA Synthesis & Timing</h2>
  <p>Synthesis targeting Xilinx 7-series (<code>xc7a35t</code>) yields 312 logic LUTs, 150 distributed RAM primitives (<code>RAM64X1S</code>), 133 flip-flops, and 0 Block RAMs. Because the specification mandates single-cycle hit response, asynchronous RAM reads preclude inference of synchronous Block RAMs. Static timing on Lattice iCE40 HX8K with registered wrapper reports a maximum operating frequency of <b>83.15 MHz</b>.</p>

  <h2 class="ieee-section">VIII. Conclusion & Phase II Roadmap</h2>
  <p>The Phase I direct-mapped cache controller prototype is fully realized, functionally verified, synthesized, and quantitatively evaluated. All verification runs pass with 0 errors, and experimental AMAT matches theoretical models. For <b>Phase II</b>, we will expand this prototype with set-associative line mapping (2-way / 4-way), LRU eviction, and write-back with dirty-bit tracking.</p>

  <h2 class="ieee-section">References</h2>
  <div class="reference-item">[1] M. V. Wilkes, "Slave memories and dynamic storage allocation," <i>IEEE Trans. Electron. Comput.</i>, vol. EC-14, no. 2, pp. 270–271, Apr. 1965.</div>
  <div class="reference-item">[2] A. J. Smith, "Cache memories," <i>ACM Comput. Surv.</i>, vol. 14, no. 3, pp. 473–530, Sep. 1982.</div>
  <div class="reference-item">[3] M. D. Hill and A. J. Smith, "Evaluating associativity in CPU caches," <i>IEEE Trans. Comput.</i>, vol. 38, no. 12, pp. 1612–1630, Dec. 1989.</div>
  <div class="reference-item">[4] N. P. Jouppi, "Improving direct-mapped cache performance by the addition of a small fully-associative cache and prefetch buffers," in <i>Proc. 17th Annu. Int. Symp. Comput. Archit. (ISCA)</i>, 1990, pp. 364–373.</div>
  <div class="reference-item">[5] J. L. Hennessy and D. A. Patterson, <i>Computer Architecture: A Quantitative Approach</i>, 6th ed., Cambridge, MA, USA: Morgan Kaufmann, 2017.</div>
  <div class="reference-item">[6] Xilinx Inc., <i>7 Series FPGAs Memory Resources User Guide</i>, UG473, v1.14, Mar. 2019.</div>
  <div class="reference-item">[7] C. Wolf, <i>Yosys Open SYnthesis Suite</i>, Documentation and Architecture Reference, 2020.</div>
  <div class="reference-item">[8] IEEE Standard for Verilog Hardware Description Language, <i>IEEE Std 1364-2005</i>, Apr. 2006.</div>

</div>

</body>
</html>
"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Generated IEEE HTML report at: {output_path}")

if __name__ == '__main__':
    html_file = '/Users/ash/CascadeProjects/projects..../MCA/mca-capstone/report/ieee_project_report.html'
    pdf_file = '/Users/ash/CascadeProjects/projects..../MCA/mca-capstone/report/ieee_project_report.pdf'
    generate_html(html_file)
    cmd = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "--headless",
        "--disable-gpu",
        f"--print-to-pdf={pdf_file}",
        html_file
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(f"Compiled IEEE PDF report to: {pdf_file}")
