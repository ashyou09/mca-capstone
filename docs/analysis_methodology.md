# M5 analysis methodology

## Source of truth and interface compatibility

The analysis follows `plan.md` §§2, 4.4 and 4.5, M4's `analysis/golden_model.py` / `analysis/compare.py`, and M1's `docs/fsm.md`. The baseline is a 32-bit, word-aligned, read-only cache with 1 KiB capacity, 16-byte blocks, 64 direct-mapped lines and `MEM_LATENCY=4`. Trace addresses remain in the 256 KiB memory range. The analyser consumes the exact M4 CSV columns: `idx,op,addr,hit,rdata,latency_cycles`.

## Reference model versus RTL evidence

The default analysis independently models the direct-mapped cache: block number selects index and tag; a line hits only when its valid bit is set and its stored tag matches; a miss installs the complete block. The expected word value uses the same deterministic memory function as `rtl/main_memory.v` and `analysis/golden_model.py`.

Reference-model results are appropriate for workload design and parameter sweeps. They are not evidence that the Verilog implementation passed. For RTL evidence, run M4's `make trace T=<name>` target, then invoke `analysis/analyze.py --rtl-csv analysis/results/<name>_sim.csv --trace traces/<name>.trace`. RTL mode validates every row's index, operation, address, hit/miss result, returned data and latency against the reference before reporting measured values. A mismatched or empty CSV is rejected.

## Metrics and AMAT convention

Hit ratio = hits / total accesses. Miss ratio = misses / total accesses. Average hit and miss latency are computed from their respective rows. Measured AMAT is the mean of all per-access latency values.

The FSM documentation defines end-to-end miss latency as `W × (L + 1) + 2`, where `W = BLOCK_BYTES / 4` and `L = MEM_LATENCY`. The miss penalty above the one-cycle hit time is therefore `W × (L + 1) + 1`. At the baseline, `W=4` and `L=4`: miss latency = 22 cycles, miss penalty = 21 cycles. Formula AMAT is `1 + miss_rate × 21`. The analyser uses this repository-specific timing convention, rather than treating the full miss latency as the miss penalty.

## Three-C miss taxonomy

The first reference to a memory block is compulsory. The analyser also maintains a fully associative LRU shadow cache with the same number of lines as the direct-mapped cache. A later direct-mapped miss that would hit in this shadow is classified as conflict; a miss in both is classified as capacity. This is an explicit analytical convention and is not additional hardware. The replacement policy used for the shadow is LRU, so the taxonomy is reproducible and its assumption is visible.

## Parameter sweep

The sweep evaluates cache capacities of 512 B, 1 KiB, 2 KiB and 4 KiB with block sizes of 8 B, 16 B, 32 B and 64 B. Each combination is evaluated for every committed trace. A larger block may exploit spatial locality while increasing transfer cost. A larger cache may reduce evictions while increasing storage requirements. Compare both hit ratio and AMAT.
