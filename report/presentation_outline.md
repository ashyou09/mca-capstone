# Final presentation outline — Direct-Mapped Cache Controller

Suggested duration: 7–9 minutes. Use the actual diagrams, waveforms and synthesis tables from the repository. Do not present reference-model results as RTL measurements.

## Slide 1 — Title and team

**Direct-Mapped Cache Controller: RTL Design and Architectural Performance Analysis**

Show course, team members and roles. M5 contribution: deterministic traces, hit/miss analysis, AMAT, parameter sweep and report coordination.

## Slide 2 — Problem statement

Main memory is slower than a small cache. The project implements a direct-mapped cache and measures how access locality changes performance.

**Visual:** CPU → Cache → Main Memory hierarchy.

## Slide 3 — Cache organisation

Explain Data RAM, Tag RAM, Valid RAM, address decoder, comparator and controller FSM. Emphasise that the valid bit prevents uninitialised tag contents from producing false hits.

## Slide 4 — Address breakdown

For 1 KiB capacity and 16-byte blocks: 64 lines, 4 offset bits, 6 index bits and 22 tag bits.

**Visual:** 32-bit address split into Tag[31:10], Index[9:4], Offset[3:0].

## Slide 5 — Lookup and refill

A hit returns the selected word in one cycle. A miss fetches four words, writes the complete line, and sets tag and valid only with the final refill word.

**Visual:** M1 FSM or a verified cold-miss waveform.

## Slide 6 — Verification strategy

Show M4's directed scenarios: invalid line after reset, cold miss then hit, spatial locality, same-index conflict, replacement, returned data, counters and latency. Quote only results actually produced by `make test`.

## Slide 7 — Workload design (M5)

Introduce seven 4096-access traces: sequential, random, loop, stride, matrix row, matrix column and mixed. Explain which locality property each workload isolates. Row and column traces visit the same matrix elements in different orders.

## Slide 8 — Hit ratio and miss taxonomy

Define hit ratio and miss ratio. Explain compulsory, conflict and capacity misses, including the equal-capacity fully associative LRU shadow-cache convention.

**Visual:** generated `hit_ratio_by_trace.png` and the summary table. Label these as Python reference-model outputs unless backed by validated RTL CSVs.

## Slide 9 — AMAT calculation

`AMAT = hit_time + miss_rate × miss_penalty`. For the baseline, hit time = 1 cycle and miss penalty = 21 cycles. Example: sequential reference miss rate 25%, so AMAT = 6.25 cycles.

## Slide 10 — Parameter sweep and trade-offs

Compare capacities 512 B, 1 KiB, 2 KiB and 4 KiB with blocks 8 B, 16 B, 32 B and 64 B. Larger blocks can exploit spatial locality but increase miss service cost; larger caches consume more storage.

## Slide 11 — Synthesis and implementation results

Use the measured tables in `docs/synthesis.md`. Explain whether memories map to BRAM, LUTRAM or flip-flops. Do not infer Fmax from Yosys generic statistics alone.

## Slide 12 — Conclusion and future work

Summarise how workload locality, mapping policy, capacity, block size and miss cost interact. Future work: set associativity, alternative replacement policies, write-back and broader application traces.

**Final takeaway:** the highest hit ratio is not automatically the lowest AMAT; evaluate the miss cost as well as the miss frequency.
