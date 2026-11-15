# M5 viva preparation

## Why do we need multiple traces?

Cache performance depends on the order and locality of memory accesses. Sequential and row-major traces show spatial locality; repeated loops show temporal locality; random accesses provide a low-locality workload; stride and column-major accesses reveal index conflicts in a direct-mapped cache.

## Why does a sequential trace approach 75% hits with 16-byte blocks?

A 16-byte block contains four 32-bit words. The first word from a new block misses and causes all four words to be refilled. If the line is not evicted, the next three word accesses hit. That gives one miss and three hits per block, or 75% hits after the compulsory fills.

## Why can a 1,024-byte separation cause a conflict?

The cache is direct-mapped. Its index is selected by the address bits below the tag. Addresses separated by the cache capacity (1 KiB) have the same index but different tags. They compete for the same line, so alternating between them repeatedly misses even though the cache has other lines available.

## What do the three C's mean in this analysis?

A compulsory miss is the first access to a block. To distinguish later conflict and capacity misses, the analyser also simulates an equal-capacity fully associative LRU shadow cache. If the direct-mapped cache misses but the shadow hits, the miss is classified as conflict. If both miss, it is classified as capacity. This is a documented analysis convention, not an extra hardware component.

## What is AMAT?

Average Memory Access Time estimates the average latency per access: `AMAT = hit_time + miss_rate × miss_penalty`. The miss penalty is the extra cost of a miss above the hit time.

## Why is the baseline miss penalty 21 cycles, not 22?

M1's FSM and M3's memory handshake define end-to-end miss latency as `W × (L + 1) + 2`. With four words per block and `MEM_LATENCY=4`, miss latency is 22 cycles. Hit time is one cycle, so the additional miss penalty is `22 - 1 = 21` cycles. Therefore `AMAT = 1 + miss_rate × 21`.

## Why do formula AMAT and measured average latency match?

The baseline cache is blocking and read-only. Every access is either a one-cycle hit or a 22-cycle miss. Averaging those latencies gives `1 × hit_ratio + 22 × miss_ratio`, which simplifies to `1 + miss_rate × 21`.

## What is the matrix row/column experiment showing?

Both traces visit the same 64×64 matrix elements. Row-major order visits adjacent words together, so each 16-byte cache block supplies four consecutive words. Column-major order jumps 256 bytes between rows. Those blocks map to competing direct-mapped indices, so the cache can repeatedly miss even though a fully associative cache with the same number of lines can retain them.

## Is a Python reference model enough to prove the RTL works?

No. The reference model helps validate workload patterns and run fast parameter sweeps. Implementation evidence requires M4's Verilog trace testbench to execute the traces and compare every access's hit/miss result, returned data and latency against the golden model. Keep the two sources of results separate.
