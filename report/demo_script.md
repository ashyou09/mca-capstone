# 3-minute project demonstration script — M5

## 0:00–0:25 — Problem and objective

“Our project implements a direct-mapped cache controller. The important question is how workload locality changes the cache hit rate and average memory access time. My responsibility was to generate reproducible memory traces and analyse the architectural trade-offs.”

## 0:25–0:55 — Trace design

“I created seven read-only workloads: sequential, random, repeated loop, phased stride, row-major matrix, column-major matrix and mixed hot-set traffic. Each contains 4096 word-aligned accesses within the 256 KiB memory range. The generator uses a fixed seed, so the inputs can be reproduced exactly.”

Show the trace directory. Explain that sequential accesses exploit spatial locality, while the repeated 512-byte working set demonstrates temporal locality. The final stride phase alternates between two addresses 1 KiB apart, which map to the same direct-mapped line index.

## 0:55–1:35 — Metrics and miss classification

“Hit ratio is hits divided by total requests. Miss ratio is misses divided by total requests. I classify first-touch misses as compulsory. For later misses, I compare the direct-mapped cache with an equal-capacity fully associative LRU shadow: a shadow hit indicates a conflict miss; a shadow miss indicates a capacity miss.”

Show the summary and state clearly whether the displayed data is from the Python reference model or the RTL simulation CSV.

## 1:35–2:15 — AMAT

“AMAT is hit time plus miss rate multiplied by miss penalty. Our hit time is one cycle. A 16-byte block contains four words. With four-cycle memory latency, the FSM's end-to-end miss latency is 22 cycles, so the additional miss penalty is 21 cycles. Therefore AMAT is `1 + miss_rate × 21`.”

Use the sequential reference result as a hand calculation: 25% misses gives `1 + 0.25 × 21 = 6.25 cycles`. Label it as a reference-model example unless the same trace has been verified in RTL.

## 2:15–2:45 — Trade-off and conclusion

“The sweep varies cache capacity and block size. Larger blocks can improve spatial reuse but increase the number of words transferred on a miss. Larger caches reduce eviction pressure but consume more storage. So the best configuration depends on workload and AMAT, not only hit ratio.”

## 2:45–3:00 — Evidence boundary

“The Python reference model is used for reproducible workload analysis and parameter sweeps. For implementation evidence, M4's RTL trace testbench must run and match the golden model access by access. I do not present reference-model output as an RTL measurement.”
