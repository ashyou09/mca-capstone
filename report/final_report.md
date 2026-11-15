# Direct-Mapped Cache Controller — Final Project Report

## Abstract

This project implements and evaluates a parameterized direct-mapped cache controller in Verilog. The architecture combines a controller FSM, data/tag/valid storage, address decoding, tag comparison and a behavioural main-memory interface. Verification is performed with directed tests and trace-driven comparison against a Python golden model. The M5 study adds reproducible memory workloads, hit/miss classification, average memory access time (AMAT) and a parameter sweep. Implementation evidence, reference-model results and synthesis data are explicitly distinguished.

## 1. Problem and objective

The project studies how a small cache reduces the average cost of memory accesses. The objective is to implement correct lookup and block refill, preserve valid-bit semantics, count hits and misses, and evaluate how workload locality and cache parameters affect performance. The project brief identifies correct lookup/refill, valid-bit handling, hit/miss statistics and architectural analysis as evaluation priorities.

## 2. System configuration

The baseline uses 32-bit byte addresses, 32-bit words, a 1 KiB direct-mapped cache and 16-byte blocks. There are 64 cache lines and four words per block. The address is divided into a 22-bit tag, 6-bit index and 4-bit block offset. CPU accesses are word-aligned; the two lowest address bits are ignored. The baseline is read-only. Write-through/no-write-allocate is an optional stretch feature and is disabled by default.

## 3. Architecture and team contributions

**M1 — Controller and integration.** `rtl/cache_controller.v` implements the blocking FSM. A hit is returned in one cycle. A miss triggers four word-by-word memory handshakes; tag and valid are written only with the final refill word. `rtl/cache_top.v` connects the decoder, RAMs, comparator and controller and exposes CPU and memory interfaces. See `docs/fsm.md` and `docs/address_breakdown.md`.

**M2 — Storage datapath.** `rtl/addr_decoder.v`, `tag_ram.v`, `valid_ram.v`, `data_ram.v` and `tag_comparator.v` implement address fields, cache storage and hit detection. Valid bits are cleared on reset so uninitialised tag contents cannot cause false hits.

**M3 — Main memory and synthesis.** `rtl/main_memory.v` models deterministic memory contents and the word-level request/acknowledge handshake. `synth/` and `docs/synthesis.md` contain tool-driven area and timing results. Main memory is a behavioural test model and is not part of the synthesised cache top.

**M4 — Verification.** `tb/` contains module tests, a directed cache testbench and a trace-driven testbench. `analysis/golden_model.py` provides the Python reference model; `analysis/compare.py` compares RTL and golden CSVs per access. The root Makefile preserves M4's `sim`, `trace`, `test`, `unit`, `wave` and `clean` workflows.

**M5 — Traces and architectural analysis.** `traces/gen_traces.py` creates deterministic workloads; `analysis/analyze.py` computes hit/miss metrics, three-C miss classes, AMAT and parameter sweeps. `docs/traces.md`, `docs/analysis_methodology.md`, `docs/hit_miss_report.md`, `docs/viva_m5.md` and the presentation/demo materials document the analysis.

## 4. Cache operation

For each request, the decoder extracts tag, index and word offset. The index selects a line. A hit occurs only if the valid bit is set and the stored tag equals the requested tag. On a hit, the requested word is returned in one cycle. On a miss, the controller fetches the block one word at a time from main memory. Each word is stored in the data RAM; the tag and valid bit are committed with the final word. The cache is blocking, so another CPU request is not serviced during refill.

## 5. Verification approach

The directed suite targets reset/invalid-line behaviour, cold miss followed by hit, spatial locality, conflict replacement, stale data, counters and latency. Trace-driven verification runs each `.trace` through the RTL testbench and golden model, then compares hit/miss, returned data and optionally latency for every access. Use `make test` for the complete integrated verification suite. The verification coverage and recorded mutation checks are documented in `docs/verification.md`; this report does not substitute a claim of a new test run for the committed evidence.

## 6. Workload methodology

Seven deterministic read-only traces are supplied: sequential, uniform random, repeated loop, phased stride, row-major matrix, column-major matrix and mixed hot-set/random. Each contains 4096 word-aligned accesses within the 256 KiB memory range. The row-major and column-major traces traverse the same complete 64×64 matrix; only the order changes. The final stride phase alternates between two addresses 1 KiB apart to demonstrate direct-mapped index conflicts.

Regenerate traces with `make traces`. Run `make analysis` for Python reference-model metrics and the parameter sweep. These reference results are not RTL simulation evidence. For implementation evidence, first run `make trace T=<name>`; the M4 compare step must pass. Then run `make analysis-rtl T=<name>` to validate the RTL CSV rows again and calculate measured metrics.

## 7. Reference-model hit/miss results

The following values were generated by the M5 Python reference model at 1 KiB / 16 B / `MEM_LATENCY=4`. They are **not RTL simulation measurements**.

| Workload | Hit ratio | Misses | Compulsory | Conflict | Capacity | Reference AMAT |
|---|---:|---:|---:|---:|---:|---:|
| Sequential | 75.00% | 1024 | 1024 | 0 | 0 | 6.250 cycles |
| Random | 0.46% | 4077 | 3616 | 2 | 459 | 21.903 cycles |
| Loop | 99.22% | 32 | 32 | 0 | 0 | 1.164 cycles |
| Stride | 0.00% | 4096 | 2390 | 1364 | 342 | 22.000 cycles |
| Matrix row | 75.00% | 1024 | 1024 | 0 | 0 | 6.250 cycles |
| Matrix column | 0.00% | 4096 | 1024 | 3072 | 0 | 22.000 cycles |
| Mixed | 79.42% | 843 | 618 | 217 | 8 | 5.322 cycles |

The repeated loop fits in the cache and has a high hit ratio after compulsory fills. Sequential and row-major workloads benefit from four-word spatial reuse. The column-major trace suffers because the 256-byte row stride maps different row blocks onto competing direct-mapped indices. Random accesses span a much larger footprint. The stride trace contains both cold/capacity effects and a deliberate same-index ping-pong phase.

## 8. Miss classification

A compulsory miss is the first access to a block. For later misses, the analyser compares the direct-mapped cache against an equal-capacity fully associative LRU shadow. If the shadow would hit, the direct-mapped miss is classified as conflict; if the shadow also misses, it is classified as capacity. This is an analytical convention whose replacement policy is explicitly LRU; it is not another hardware structure.

## 9. AMAT derivation

The FSM documentation defines end-to-end miss latency as:

`miss_latency = W × (L + 1) + 2`

where `W` is words per block and `L` is main-memory latency. The additional miss penalty over the one-cycle hit time is:

`miss_penalty = W × (L + 1) + 1`

For the baseline, `W=4` and `L=4`, so miss latency is 22 cycles and miss penalty is 21 cycles. Therefore:

`AMAT = hit_time + miss_rate × miss_penalty = 1 + miss_rate × 21`.

For sequential traffic, the reference miss rate is 25%, so `AMAT = 1 + 0.25 × 21 = 6.25 cycles`. The reference model's measured average latency agrees with the formula because every baseline hit costs one cycle and every miss costs 22 cycles. RTL mode separately measures average hit latency, average miss latency, measured miss penalty and mean access latency after validating the CSV against the reference.

## 10. Parameter sweep

The M5 analyser evaluates cache sizes 512 B, 1 KiB, 2 KiB and 4 KiB with block sizes 8 B, 16 B, 32 B and 64 B, across all seven traces. It emits CSV tables and plots for hit ratio by workload, hit ratio versus block size, hit ratio versus cache size and AMAT versus block size. Larger blocks can exploit spatial locality but increase the amount of data transferred on a miss; larger caches reduce eviction pressure but increase storage requirements. The preferred configuration depends on AMAT and workload, not hit ratio alone.

## 11. Synthesis findings

M3's measured synthesis results are maintained in `docs/synthesis.md`. For the 1 KiB / 16 B baseline, Yosys generic synthesis reports 27,313 cells, including 9,733 flip-flops; `data_ram` accounts for 82.2% of generic cells. The Xilinx 7-series mapping reports 312 logic LUTs, 150 LUTs used as distributed RAM, 133 flip-flops and no block RAM. The iCE40 mapping reports 8,996 LUT4s and 9,733 flip-flops and does not fit the HX8K device as written. M3 reports 83.15 MHz for a separately registered-input block-RAM wrapper configuration; that timing must not be represented as Fmax for the unmodified asynchronous-read `cache_top`. See `docs/synthesis.md` for tool versions, sweep tables, conditions and caveats.

## 12. Limitations and future work

The baseline is read-only and uses synthetic workloads rather than application traces. The three-C classification uses a fully associative LRU shadow. The reference-model sweep is not a substitute for RTL simulation across every parameter combination. Future extensions include set associativity, alternative replacement policies, write-back/write-allocate, write-mixed traces and application-derived traces.

## 13. Reproduction commands

```sh
make traces
make analysis
make test
make analysis-rtl T=seq
make synth
```

`make analysis` creates Python reference-model results. `make test` performs M4 RTL verification over the committed traces. `make analysis-rtl T=seq` requires a successful RTL trace run and validates its CSV. `make synth` delegates to M3's synthesis sweep. Refer to each subsystem's documentation for tool requirements and raw logs.
