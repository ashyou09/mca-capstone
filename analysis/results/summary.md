# Hit/miss and AMAT analysis

**Source:** Python reference model (not RTL simulation).  
**Configuration:** 1 KiB cache, 16-byte blocks, 4 words/block, MEM_LATENCY=4.  
**Workload:** seven deterministic, read-only traces; 4096 accesses each.

| Trace | Accesses | Hit % | Miss % | Compulsory | Conflict | Capacity | Miss penalty | AMAT (cycles) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Loop | 4096 | 99.22 | 0.78 | 32 | 0 | 0 | 21 | 1.164 |
| Matrix column | 4096 | 0.00 | 100.00 | 1024 | 3072 | 0 | 21 | 22.000 |
| Matrix row | 4096 | 75.00 | 25.00 | 1024 | 0 | 0 | 21 | 6.250 |
| Mixed | 4096 | 79.42 | 20.58 | 618 | 217 | 8 | 21 | 5.322 |
| Random | 4096 | 0.46 | 99.54 | 3616 | 2 | 459 | 21 | 21.903 |
| Sequential | 4096 | 75.00 | 25.00 | 1024 | 0 | 0 | 21 | 6.250 |
| Stride | 4096 | 0.00 | 100.00 | 2390 | 1364 | 342 | 21 | 22.000 |

## Interpretation

The 512-byte loop working set fits in the cache and reaches 99.22% hits after its compulsory fills. Sequential and row-major workloads exploit four-word spatial reuse. Column-major traversal of the same 64×64 matrix produces conflict misses because its 256-byte row stride maps blocks onto competing direct-mapped indices. The final stride phase deliberately alternates between two blocks 1 KiB apart.

## AMAT convention

The repository FSM defines end-to-end miss latency as W × (L + 1) + 2. With W=4 and L=4, miss latency is 22 cycles and the additional miss penalty over the one-cycle hit time is 21 cycles.

AMAT = 1 + miss_rate × 21.

For the sequential trace, AMAT = 1 + 0.25 × 21 = 6.25 cycles. Formula and measured reference-model average latency agree exactly.

## Evidence boundary

These are Python reference-model results. They do not establish RTL correctness. Run `make test` for M4's RTL/golden-model comparison across the traces. Use `make analysis-rtl T=seq` only after the corresponding RTL trace test passes.
