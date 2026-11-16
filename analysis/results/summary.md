# Hit/miss and AMAT analysis

Python reference model; cache 1024 B, block 16 B, MEM_LATENCY 4.

| Trace | Accesses | Hit % | Miss % | Compulsory | Conflict | Capacity | Miss penalty | Measured AMAT | Formula AMAT |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| loop | 4096 | 99.22 | 0.78 | 32 | 0 | 0 | 21 | 1.164 | 1.164 |
| matrix_col | 4096 | 0.00 | 100.00 | 1024 | 3072 | 0 | 21 | 22.000 | 22.000 |
| matrix_row | 4096 | 75.00 | 25.00 | 1024 | 0 | 0 | 21 | 6.250 | 6.250 |
| mixed | 4096 | 79.42 | 20.58 | 618 | 217 | 8 | 21 | 5.322 | 5.322 |
| random | 4096 | 0.46 | 99.54 | 3616 | 2 | 459 | 21 | 21.903 | 21.903 |
| sample | 8 | 50.00 | 50.00 | 3 | 1 | 0 | 21 | 11.500 | 11.500 |
| seq | 4096 | 75.00 | 25.00 | 1024 | 0 | 0 | 21 | 6.250 | 6.250 |
| stride | 4096 | 0.00 | 100.00 | 2390 | 1364 | 342 | 21 | 22.000 | 22.000 |

## Interpretation

Sequential and row-major traces expose spatial locality; the repeated loop exposes temporal locality. Uniform random traffic spans a much larger footprint. The stride trace ends by alternating between two blocks 1 KiB apart, which share one direct-mapped index but fit in the equal-capacity fully associative shadow.

Compulsory misses are first references to blocks. A later direct-mapped miss that would hit in an equal-capacity fully associative LRU shadow is classified as conflict; a miss in both is classified as capacity. This is an analytical classification, not extra hardware.

## AMAT

AMAT = hit_time + miss_rate × miss_penalty. The repository FSM defines miss latency = words_per_block × (MEM_LATENCY + 1) + 2; miss penalty = miss latency − 1. For 16-byte blocks and MEM_LATENCY=4, miss latency is 22 cycles and miss penalty is 21 cycles.

## Evidence boundary

Default outputs are Python reference-model results, not RTL measurements. RTL mode validates every CSV row (index, operation, address, hit/miss, returned data and latency) against the supplied trace and reference model before reporting measured RTL metrics.
