# Project 6: Direct-Mapped Cache Controller. Team Plan (5 members)

> Source: `project.md`. Is folder (`MCA/`) mein hi poora project rahega.
> Deadline: `__ / __ / ____` (yahan bharo, neeche ki timeline usi ke hisaab se adjust karo)

---

## 1. Project ek nazar mein

Hum ek **direct-mapped cache controller** Verilog mein banayenge, use memory-access traces pe chalayenge, aur **hit ratio, miss ratio, AMAT** nikalenge.

**Deliverables (project.md ke hisaab se):**

| # | Deliverable | Owner |
|---|---|---|
| 1 | Cache RTL (Data RAM, Tag RAM, Valid RAM, Decoder, Comparator, Top) | M2 (+ M1 top) |
| 2 | Controller FSM | M1 |
| 3 | Memory-access traces (sequential, random, repeated) | M5 |
| 4 | Hit/miss report | M5 (data M4 se) |
| 5 | AMAT calculation | M5 |
| 6 | Synthesis results | M3 |
| 7 | Final report + PPT | M5 (sab contribute) |

**Evaluation focus:** correct lookup/refill, valid-bit handling, hit/miss statistics, architectural analysis. Isliye verification (M4) aur analysis (M5) ko utna hi weight dena hai jitna RTL ko.

---

## 2. Design decisions (assumptions, sab ko follow karne hain)

Ye sab `project.md` ke "suggested" config se liye gaye hain. Agar koi badalna ho to team meeting mein badlo, akele nahi.

| Item | Value |
|---|---|
| Address width | 32 bit |
| Cache size | 1 KB (parameter `CACHE_BYTES`) |
| Block size | 16 B = 4 words (parameter `BLOCK_BYTES`) |
| Word size | 32 bit, word-aligned access (addr[1:0] ignore) |
| Number of lines | 1024 / 16 = **64** |
| Offset | 4 bit = `addr[3:0]` (word select = `addr[3:2]`) |
| Index | 6 bit = `addr[9:4]` |
| Tag | 22 bit = `addr[31:10]` |
| Mapping | Direct-mapped |
| Baseline ops | **Read only** (lookup + refill). `cpu_we` interface mein hai par baseline mein 0 |
| Stretch goal | Write-through + no-write-allocate (sirf baseline pass hone ke baad) |
| Hit time | **1 cycle** (combinational tag compare, cpu_ready usi cycle) |
| Refill | Miss pe 4 words one-by-one memory se, phir CPU ko response |
| Memory model | Behavioral, parameter `MEM_LATENCY` cycles per word |
| Language/Tools | Verilog (`-g2012` for `$clog2`), Icarus Verilog + GTKWave, Python 3 (analysis), Yosys (synthesis). Vivado/Quartus ho to bonus |

Sab modules **parameterized** honge (cache size, block size), taaki M5 sweep chala sake (512 B to 4 KB, block 8/16/32/64).

---

## 3. Folder structure

```
MCA/
├── project.md              # given problem statement
├── plan.md                 # ye file
├── Makefile                # M4 banayega: make sim / make test / make synth
├── rtl/
│   ├── addr_decoder.v      # M2
│   ├── tag_ram.v           # M2
│   ├── valid_ram.v         # M2
│   ├── data_ram.v          # M2
│   ├── tag_comparator.v    # M2
│   ├── cache_controller.v  # M1  (FSM)
│   ├── cache_top.v         # M1  (sab ko jodta hai)
│   └── main_memory.v       # M3  (memory model + interface)
├── tb/
│   ├── tb_tag_ram.v ...    # M2 apne unit tests (basic)
│   ├── tb_main_memory.v    # M3
│   ├── tb_cache_directed.v # M4
│   └── tb_cache_trace.v    # M4 (trace-driven, log likhta hai)
├── traces/
│   ├── gen_traces.py       # M5
│   └── *.trace             # M5
├── analysis/
│   ├── golden_model.py     # M4 (cache ka Python reference model)
│   ├── analyze.py          # M5 (hit/miss, AMAT, plots)
│   └── results/            # csv + png
├── synth/
│   ├── synth.ys            # M3 (Yosys script)
│   └── reports/
├── docs/
│   ├── fsm.md / fsm.png    # M1
│   ├── address_breakdown.md# M1
│   └── ...
└── report/                 # final report + PPT (M5 coordinate)
```

---

## 4. Interface contract (ISE PEHLE FREEZE KARO, Day 1)

Sab log parallel kaam tabhi kar payenge jab ye signals fix hon. **Koi bhi change = pehle yahan edit, phir sab ko batao.**

### 4.1 CPU side (`cache_top`)

| Signal | Dir | Width | Meaning |
|---|---|---|---|
| `clk` | in | 1 | clock |
| `rst_n` | in | 1 | active-low sync reset. Reset pe saari valid bits 0 |
| `cpu_valid` | in | 1 | request valid. `cpu_ready` aane tak `cpu_addr/cpu_we/cpu_wdata` stable rahenge |
| `cpu_we` | in | 1 | 0 = read, 1 = write (baseline mein hamesha 0) |
| `cpu_addr` | in | 32 | byte address |
| `cpu_wdata` | in | 32 | write data (stretch) |
| `cpu_rdata` | out | 32 | read data, `cpu_ready=1` ke cycle mein valid |
| `cpu_ready` | out | 1 | request complete, **1 cycle pulse** |
| `stat_hit` | out | 1 | 1-cycle pulse, jab request hit classify ho (request ke lookup cycle mein) |
| `stat_miss` | out | 1 | 1-cycle pulse, jab request miss classify ho |
| `hit_count`, `miss_count` | out | 32 | running counters |

Rule: **har request ke liye exactly ek hi `stat_hit` ya `stat_miss` pulse**. Refill ke baad ka internal re-lookup count nahi hoga.

### 4.2 Memory side (`cache_top` <-> `main_memory`)

Word-by-word handshake:

| Signal | Dir (cache ke hisaab se) | Width | Meaning |
|---|---|---|---|
| `mem_req` | out | 1 | request, `mem_ack` aane tak high aur `mem_addr` stable |
| `mem_we` | out | 1 | 0 = read (stretch mein write-through) |
| `mem_addr` | out | 32 | **word-aligned byte address** |
| `mem_wdata` | out | 32 | write data (stretch) |
| `mem_rdata` | in | 32 | read data, `mem_ack=1` ke cycle mein valid |
| `mem_ack` | in | 1 | 1-cycle pulse, `MEM_LATENCY` cycles baad (min 1) |

Miss pe controller block-aligned base se start karke 4 words (addr, +4, +8, +12) mangta hai.

### 4.3 Internal sub-module interfaces (M1 aur M2 ke beech)

```
addr_decoder   : in  addr[31:0]
                 out tag[TAG_W-1:0], index[INDEX_W-1:0], offset[OFF_W-1:0], word_sel[WSEL_W-1:0]

tag_ram        : clk, index (read), tag_out
                 we, w_index, w_tag (write)           // async read, sync write

valid_ram      : clk, rst_n, index (read), valid_out
                 we, w_index, w_valid                 // reset pe sab 0, async read, sync write

data_ram       : clk, index, rd_block[BLOCK_BITS-1:0]  // async read, poora block
                 we, w_index, w_word_sel, w_word[31:0] // word-granular sync write

tag_comparator : in tag_a, tag_b, valid  ->  out hit   // hit = valid & (tag_a == tag_b)
```

Controller cache_top mein in cheezon ko drive karta hai: `tag_we, valid_we, data_we, w_word_sel`.

**Module parameter names (M1 ne `cache_top.v` mein ye use kiye hain, M2 ko exactly yahi rakhne hain):**

```
addr_decoder   #(ADDR_W, CACHE_BYTES, BLOCK_BYTES)
tag_ram        #(INDEX_W, TAG_W)
valid_ram      #(INDEX_W)
data_ram       #(INDEX_W, BLOCK_BYTES)      // w_word_sel width = $clog2(BLOCK_BYTES)-2
tag_comparator #(TAG_W)
main_memory    #(MEM_WORDS, MEM_LATENCY)
```

Extra decisions (M1): `cpu_we=1` jab `WRITE_SUPPORT=0` ho to request read ki tarah handle hota hai (CPU hang nahi hota).
`latency_cycles` = `cpu_valid` assert hone se `cpu_ready` ke cycle tak (us cycle ko milake). Hit = 1, miss = `W*(MEM_LATENCY+1)+2` (base config, MEM_LATENCY=4: 22). Details: `docs/fsm.md`.
Temporary stand-in file `tb/stubs/m2_m3_stubs.v` ab delete ho chuki hai (real M2 + M3 files aa gayi hain). Compile: `iverilog -g2012 rtl/*.v tb/<tb>.v`. `main_memory` ke do extra outputs hain: `mem_read_count`, `mem_write_count` (details: `docs/main_memory.md`).

### 4.4 Trace format (M5 banayega, M4 ka TB padhega)

Text file, har line: `<op> <addr>` dono hex. `op`: `0`=read, `1`=write.

```
0 00001a2c
0 00001a30
1 00002000
```

Saare trace addresses **`0x00000000` se `0x0003FFFF`** ke andar (256 KB), taaki memory model chhota rahe. Lines `#` se shuru ho to comment (Python side mein skip; Verilog ke liye generator comment likhe hi nahi).

### 4.5 Simulation log format (M4 banayega, M5 padhega)

`tb_cache_trace.v` ek CSV likhega `analysis/results/<trace_name>_sim.csv`:

```
idx,op,addr,hit,rdata,latency_cycles
0,0,00001a2c,0,5a5a1234,9
1,0,00001a30,1,5a5a1238,1
```

`hit` = 1/0 `stat_hit/stat_miss` se. `latency_cycles` = `cpu_valid` assert se `cpu_ready` tak.

### 4.6 Memory contents

Memory initial data deterministic: `mem[word_addr] = word_addr * 32'h9E3779B1` (ya koi bhi hash, par poori team ek hi use kare). Isse TB aur Python golden model bina file ke expected data nikaal sakte hain.

---

## 5. Roles

| Member | Role | Owns | Assigned Name |
|---|---|---|---|
| **M1** | Architect + Controller FSM + Top integration (team lead) | `cache_controller.v`, `cache_top.v`, `docs/fsm.*`, address breakdown | **Pankaj Baid** |
| **M2** | Storage datapath (Data/Tag/Valid RAM, Decoder, Comparator) | `addr_decoder.v`, `tag_ram.v`, `valid_ram.v`, `data_ram.v`, `tag_comparator.v` | **Ashutosh Singh** |
| **M3** | Main-memory interface + Synthesis | `main_memory.v`, `synth/*`, synthesis report section | **Narendra Singh** |
| **M4** | Verification (testbenches + golden model) | `tb/*`, `golden_model.py`, `Makefile`, waveform screenshots | **Shreya Suman** |
| **M5** | Traces + Analysis (hit rate, AMAT) + Report/PPT | `gen_traces.py`, `analyze.py`, hit/miss report, AMAT, final report | **Ranvendra Pratap Singh** |

> **Team Roster:** M1 = Pankaj Baid (Lead), M2 = Ashutosh Singh, M3 = Narendra Singh, M4 = Shreya Suman, M5 = Ranvendra Pratap Singh

**Load balance:** M1 ka kaam sabse zyada dependency-wala hai (M2 ke modules chahiye), isliye M2 ko pehle 2 din mein modules dene hain. M4 aur M5 shuru mein RTL ka wait nahi karte: M4 golden model aur TB, M5 traces aur analysis scripts pehle bana lete hain.

---

## 6. Timeline

Total ~4 phases. Dates apne deadline ke hisaab se daalo.

| Phase | Kya hoga | Exit criteria |
|---|---|---|
| **P0: Kickoff (Day 1)** | Team meeting. Section 2 aur 4 freeze. Git repo + folder structure. Tools install check (`iverilog`, `gtkwave`, `python3`, `yosys`) | Sab ke paas same folder structure; interface freeze signed-off |
| **P1: Building blocks (Day 2 to 4)** | M2 sab RAM/decoder/comparator. M3 `main_memory.v`. M4 golden model + directed TB skeleton + Makefile. M5 trace generator + analyze script skeleton. M1 FSM design (diagram) + controller code | Har module apne unit test se pass. FSM diagram review ho chuka |
| **P2: Integration (Day 5 to 7)** | M1 `cache_top` jodta hai. M4 directed + trace TB chalata hai. Bugs fix | Directed tests sab pass; 3 basic traces par RTL hit/miss == golden model hit/miss |
| **P3: Experiments + synthesis (Day 8 to 10)** | M5 sab traces + parameter sweeps + AMAT. M3 synthesis (Yosys, optional Vivado). M1 stretch (write-through) agar time ho | Hit/miss report, AMAT table, synthesis numbers ready |
| **P4: Report + demo (Day 11 to 12)** | Report, PPT, demo script, waveform screenshots, cleanup, viva practice | Final PDF + PPT + repo tag `v1.0` |

**Integration checkpoints** (har checkpoint pe 15 min sync):
1. End of P1: sab modules compile hote hain `iverilog -g2012 rtl/*.v`.
2. Mid P2: pehla miss -> refill -> hit waveform dikh jaye.
3. End of P2: RTL vs golden model per-access hit/miss mismatch = 0.

---

## 7. Git workflow (chhota aur simple)

- Ek repo `MCA/` mein. Branch per member: `m1-controller`, `m2-storage`, `m3-memsynth`, `m4-verif`, `m5-analysis`.
- Sirf apni files edit karo (section 3 ki ownership). Dusre ki file mein bug mile to usko issue/message do.
- Roz kam se kam ek baar `main` mein merge. Merge se pehle `make test` pass hona chahiye (M4 ka Makefile aane ke baad).
- Commit message: `m2: add tag_ram with async read`.

---

## 8. Definition of Done (final checklist)

- [ ] `make test` sab directed tests aur 3+ traces pe pass (RTL hit/miss == golden model)
- [ ] Reset ke baad pehla access hamesha miss (valid-bit test)
- [ ] Same-index/different-tag conflict test (ping-pong) sahi miss deta hai
- [ ] Same-block ke 4 words: 1 miss + 3 hits (spatial locality)
- [ ] FSM diagram + state table docs mein
- [ ] Hit ratio, miss ratio, AMAT: formula aur simulation-measured dono, aur dono ka comparison
- [ ] Parameter sweep (cache size, block size) ke graphs
- [ ] Synthesis report (cell count / LUT-FF-BRAM, aur agar tool de to Fmax)
- [ ] Report + PPT + waveform screenshots
- [ ] Har member apne module ko viva mein explain kar sake

---

## 9. Risks

| Risk | Mitigation |
|---|---|
| Interface mismatch (sabse common) | Section 4 freeze, change sirf yahan edit karke |
| FSM double-counting hit/miss | Rule 4.1 + M4 ka golden-model per-access compare |
| Async-read RAM synthesis mein LUTRAM/FF ban jaye, BRAM nahi | Report mein honestly likho; M3 explain kare. Size chhota hai (1 KB) to ye acceptable hai |
| Ek member busy/absent | Pair buddies: M1<->M2, M3<->M4, M5<->M1 (kam se kam ek dusre ka code padhe) |
| Time kam pade | Write support (stretch) pehle kaat do. Baseline read-only hi deliverable hai |

---

# 10. Per-member prompts

Har prompt apne AI assistant (Kiro / Claude / ChatGPT) mein paste karo, repo `MCA/` open rakhke. Prompts is `plan.md` ko reference karte hain, isliye assistant ko pehle ye file padhne ko bola gaya hai. Apne naam/date wali jagah fill kar lo.

---

## 10.1 Prompt: M1 (Architect + Controller FSM + Top)

```
Tum ek experienced digital design / computer architecture engineer ho. Main MCA capstone
team (5 members) ka M1 hoon: Architect + Controller FSM + Top integration.

Pehle /MCA/project.md aur /MCA/plan.md poori padho. Plan.md ke sections 2 (design decisions),
4 (interface contract) aur 5 (roles) mere kaam ka base hain. Interface signals ke naam ya widths
apne aap mat badalna. Agar kuch badalna zaroori lage to pehle mujhe batao.

MERA KAAM:
1. docs/address_breakdown.md: 32-bit address ka tag/index/offset breakdown derive karo
   (1 KB, 16 B block => 64 lines, offset 4, index 6, tag 22), formulas ke saath, aur ye bhi
   dikhao ki CACHE_BYTES/BLOCK_BYTES badalne pe fields kaise badalte hain. 2-3 worked
   examples do (ek hit, ek cold miss, ek conflict miss).
2. Controller FSM design karo (rtl/cache_controller.v). States ka suggestion: IDLE/LOOKUP,
   REFILL (4 words, har word ke liye mem_req/mem_ack handshake), REFILL_DONE/RESPOND.
   Constraints:
   - Hit time 1 cycle: IDLE mein cpu_valid && hit => usi cycle cpu_ready=1 aur cpu_rdata valid.
   - Miss: stat_miss ek baar pulse, block-aligned base se 4 sequential words mangao,
     har word data_ram mein likho (w_word_sel), aakhri word ke saath tag_ram aur valid_ram
     update karo, phir CPU ko response do. Response ke time stat_hit pulse NAHI aana chahiye.
   - Har request par exactly ek stat_hit ya stat_miss pulse.
   - Reset pe FSM IDLE mein, aur valid bits clear (valid_ram handle karta hai).
   - Valid bit tabhi set ho jab refill complete ho, nahi to half-filled line hit ho sakti hai.
   - cpu_we=1 baseline mein ignore ho (stretch: write-through + no-write-allocate, alag
     parameter/macro WRITE_SUPPORT ke peeche, default off).
3. rtl/cache_top.v: addr_decoder, tag_ram, valid_ram, data_ram, tag_comparator,
   cache_controller ko jodo (M2 ke modules, interface plan.md 4.3 ke hisaab se),
   hit_count/miss_count counters rakho. Main_memory (M3) top ke bahar rahegi; cache_top sirf
   mem_* ports expose kare.
4. docs/fsm.md: state diagram (mermaid chalega) + state table (state, condition, outputs,
   next state) + ek miss ka cycle-by-cycle timeline. Miss penalty ka formula likho:
   miss_penalty ~ 4 * (MEM_LATENCY + overhead cycles) aur batao overhead kya hai.
5. Integration support: M2/M3 ke modules aane par `iverilog -g2012 rtl/*.v` compile karao,
   aur M4 ke tests fail hon to debug karne mein madad karo.

QUALITY BAR:
- Synthesizable Verilog (blocking/non-blocking sahi, latch nahi, default case, sab outputs
  defined). Parameterized, hardcoded 64/22/6 mat likho; $clog2 use karo.
- Moore/Mealy choice (hit 1-cycle ke liye cpu_ready combinational hoga) comment mein justify karo.
- Pehle FSM design (diagram + table) mujhe dikhao aur approve karwao, phir code likho.
- Code ke saath mujhe samjhao taaki main viva mein explain kar sakoon: har state kyun hai,
  kaun sa signal kab change hota hai.

DELIVERABLES: docs/address_breakdown.md, docs/fsm.md, rtl/cache_controller.v, rtl/cache_top.v.
DONE jab: cold miss -> refill -> same-block 3 hits waveform dikhe aur M4 ke tests pass hon.
```

---

## 10.2 Prompt: M2 (Storage datapath) 

```
Tum ek experienced Verilog RTL designer ho. Main MCA capstone team ka M2 hoon: Cache ke
storage aur datapath modules mere zimme hain.

Pehle /MCA/project.md aur /MCA/plan.md padho. Section 2 (config) aur section 4.3
(sub-module interfaces) ko exactly follow karna, kyunki M1 (controller) in ports par depend
karta hai. Port naam/width apne aap mat badalna.

MERE MODULES (rtl/ folder, Verilog-2001 + $clog2, compile: iverilog -g2012):
1. addr_decoder.v: parameters ADDR_W=32, CACHE_BYTES=1024, BLOCK_BYTES=16 se tag, index,
   offset, word_sel nikale. Pure combinational. Sab widths $clog2 se derive karo.
2. tag_ram.v: 2^INDEX_W entries x TAG_W bits. Async read, sync write.
3. valid_ram.v: 2^INDEX_W x 1 bit. Synchronous reset (rst_n low => sab 0), async read,
   sync write. Ye valid-bit handling evaluation ka focus hai, isliye reset behavior
   clearly test karo.
4. data_ram.v: 2^INDEX_W x (BLOCK_BYTES*8) bits. Async read poora block ka. Write
   word-granular: (w_index, w_word_sel, w_word[31:0]) se sirf ek 32-bit word update ho,
   baaki block ka data na bigade.
5. tag_comparator.v: hit = valid & (tag_a == tag_b).

Har module ke liye chhota self-checking testbench tb/tb_<module>.v banao (initial block,
$display PASS/FAIL, $finish). Specific cases:
- addr_decoder: 5-6 known addresses, expected fields hand-calculated comment mein, aur ek
  parameter change (BLOCK_BYTES=32, CACHE_BYTES=2048) pe bhi check.
- valid_ram: reset ke baad sab 0; write ke baad read; reset dobara => phir sab 0.
- data_ram: 4 words alag-alag likho, phir block read karke check karo ki words sahi
  positions par hain aur ek word overwrite karne se baaki na badle.
- tag_comparator: valid=0 aur tag match => miss (yeh mandatory case hai).

QUALITY BAR:
- Synthesizable, latch-free. Memory arrays ke liye reg [W-1:0] mem [0:DEPTH-1].
- Parameters ke saath, hardcoded numbers nahi. Design BLOCK_BYTES = 8, 16, 32, 64
  aur CACHE_BYTES = 512 se 4096 ke har combination ke liye compile aur sahi chalna chahiye.
- Har file ke top par 3-4 line comment: purpose, ports, timing (async read/sync write).
- Pehle mujhe ports ki final table dikhao (plan.md 4.3 ke saath match), phir code.
- Samjhao ki async-read RAM FPGA/synthesis mein kaise map hoga (LUTRAM vs BRAM vs flops)
  taaki M3 ke synthesis report mein explain kar sakein, aur viva ke liye.

TIMELINE: sabse pehle 1-2 din mein sab modules do (M1 aur M3/M4 inpar depend hain).
Pehle addr_decoder + comparator (chhote hain), phir RAMs.

DELIVERABLES: rtl/addr_decoder.v, tag_ram.v, valid_ram.v, data_ram.v, tag_comparator.v
aur unke tb/tb_*.v. DONE jab sab tb PASS print karein aur `iverilog -g2012 rtl/*.v` error-free ho.
```

---

## 10.3 Prompt: M3 (Main-memory interface + Synthesis)

```
Tum ek experienced RTL + FPGA/ASIC synthesis engineer ho. Main MCA capstone team ka M3
hoon: Main-memory model/interface aur synthesis results mere zimme hain.

Pehle /MCA/project.md aur /MCA/plan.md padho. Section 4.2 (memory side handshake) aur
4.6 (memory contents) exactly follow karne hain.

PART A: rtl/main_memory.v (behavioral memory + interface)
- Parameters: MEM_WORDS (default 65536 => 256 KB), MEM_LATENCY (cycles, default 4, min 1).
- Ports: clk, rst_n, mem_req, mem_we, mem_addr[31:0], mem_wdata[31:0], mem_rdata[31:0],
  mem_ack.
- Behavior: mem_req dekhne ke baad MEM_LATENCY cycles baad mem_ack ek cycle ke liye high,
  usi cycle mem_rdata valid. Cache mem_req tab tak high rakhta hai jab tak ack na aaye.
  Back-to-back words ke liye ack ke baad agla request fresh latency count se start ho.
- Initial contents: mem[w] = w * 32'h9E3779B1 for sab w (initial block + loop). Address
  se word index: (mem_addr[31:2] % MEM_WORDS). Trace addresses 0x0 to 0x3FFFF ke andar hain.
- Stretch (write-through support): mem_we=1 pe mem_wdata array mein likho.
- Ek counter bhi do: mem_read_count (kitne word reads hue), taaki miss count x words per
  block se cross-check ho sake.
- tb/tb_main_memory.v: latency 1, 4, 10 par check; back-to-back requests; sahi data.

PART B: Synthesis (synth/)
- Yosys script synth/synth.ys: top = cache_top (main_memory ko exclude karo, wo
  testbench-only model hai). `read_verilog -sv` ya -g2012 equivalent, `hierarchy -top`,
  `synth`, `stat`. Generic cell count do, aur ek FPGA target (synth_ice40 ya synth_xilinx
  jo available ho) ke saath LUT/FF/BRAM count. Agar Vivado/Quartus mile to utilization +
  timing (Fmax) report bhi nikalo.
- Configs ke liye table: 512 B, 1 KB, 2 KB, 4 KB (block 16 B) aur block 8/16/32/64 B (1 KB).
  Har config ke area (LUT/FF/memory bits) record karo, taaki M5 ke hit-rate sweep ke saath
  area vs performance tradeoff dikha sakein. Script/Makefile target `make synth` banao jo
  parameter override leke chale.
- synth/reports/ mein raw logs rakho, aur docs/synthesis.md mein cleaned table + 5-6 line
  analysis: area kahan se aa raha hai (data RAM dominate karta hai), tag overhead
  (tag bits / data bits), kya memory BRAM bani ya LUTRAM/flops.

QUALITY BAR:
- Jo number tool deta hai wahi likho. Estimate ko estimate bolo, Fmax tabhi likho jab
  timing tool se aaye (Yosys akela Fmax nahi deta; nextpnr/Vivado chahiye).
- Agar synthesis mein warnings/latch aayein, M1/M2 ko exact line ke saath report karo.
- Mujhe samjhao ki synthesis report ka har number kya matlab rakhta hai (viva ke liye).
- Pehle batao ki mere machine par kaun se tools installed hain (which iverilog yosys
  vivado), phir plan banao.

TIMELINE: Part A pehle 1-2 din (M1/M4 ko memory model chahiye). Part B tab jab cache_top
compile ho.
DELIVERABLES: rtl/main_memory.v, tb/tb_main_memory.v, synth/synth.ys, synth/reports/*,
docs/synthesis.md. DONE jab tb PASS ho aur synthesis table 1 KB base config + sweep ke saath
bhar chuki ho.
```

---

## 10.4 Prompt: M4 (Verification)

```
Tum ek experienced design verification engineer ho. Main MCA capstone team ka M4 hoon:
Verification (testbenches, golden model, Makefile) mere zimme hai. Evaluation ka focus
"correct lookup/refill, valid-bit handling, hit/miss statistics" hai, yaani mera kaam seedha
marks se judta hai.

Pehle /MCA/project.md aur /MCA/plan.md padho. Section 2 (config), 4.1/4.2 (interfaces),
4.4 (trace format), 4.5 (log format), 4.6 (memory contents) strictly follow karne hain.

MERA KAAM:
1. analysis/golden_model.py: direct-mapped cache ka Python reference model. Same
   parameters (ADDR_W, CACHE_BYTES, BLOCK_BYTES), valid bits, tags, data (memory contents
   plan.md 4.6 ke formula se). Trace file padhe (4.4 format) aur har access ke liye
   (hit/miss, expected rdata) nikale. CLI: python golden_model.py <trace> --cache 1024
   --block 16 --out <csv>. Cache ke andar koi shortcut mat lo, jaise real hardware
   chalega waisa model likho (index, tag compare, refill poore block ka).
2. tb/tb_cache_directed.v: directed tests, self-checking, PASS/FAIL summary. Zaroori cases:
   a. Reset ke baad pehla access miss (valid bit = 0, tag match hone par bhi: tag=0
      wale address 0x0 par bhi miss aana chahiye).
   b. Cold miss, phir wahi address hit.
   c. Spatial locality: ek block ke 4 words => 1 miss + 3 hits.
   d. Conflict: do addresses same index/different tag (A, B=A+1024), A,B,A,B => sab miss.
   e. Line replacement ke baad purana data wapas na aaye (stale data check).
   f. Har rdata expected value (plan.md 4.6) se compare ho.
   g. Mid-test reset: reset ke baad sab lines invalid ho jayein.
   h. Counters: hit_count + miss_count == total requests; stat_hit/stat_miss kabhi ek saath
      high nahi hote; har request par exactly ek pulse.
   i. Latency check: hit => 1 cycle; miss => repeatable penalty (MEM_LATENCY se match).
3. tb/tb_cache_trace.v: trace-driven TB. Plusargs (+TRACE=<file> +OUT=<csv>) se trace aur
   output file lo. $fscanf("%h %h") se trace padho, DUT ko drive karo, log CSV plan.md 4.5
   ke format mein likho. Memory model main_memory.v (M3) ko instantiate karo.
4. Makefile targets: `make sim` (directed), `make trace T=<name>` (RTL sim + golden model +
   compare), `make test` (sab directed + sab traces/*.trace), `make wave` (gtkwave).
   Compare script (analysis/compare.py): RTL CSV vs golden CSV per-access hit/miss aur rdata,
   pehle mismatch ka index print kare, aur exit code non-zero de.
5. Waveform screenshots (GTKWave) 3: cold miss + refill, spatial hits, conflict miss.
   Signals ka acha grouping rakho (FSM state, hit, mem_req/ack, counters). Report ke liye.
6. docs/verification.md: test plan table (test, kya check karta hai, kaunsa bug pakadta
   hai), aur coverage ki honest summary (kya cover hua, kya nahi).

APPROACH:
- Golden model aur TB RTL ke aane ka wait nahi karte. Pehle golden model aur Makefile banao,
  fir TB skeleton. RTL aane par plug in karo.
- Bugs mile to M1 (controller/top), M2 (RAMs), M3 (memory) ko exact failing test, waveform
  time aur expected vs actual ke saath report karo. Khud RTL fix mat karo.
- Mutation sanity: 2-3 jaan-boojh ke bug daal ke (valid bit reset skip, tag compare galat
  bits) dekho ki mere tests unhe pakadte hain, phir revert. Isse test quality ka proof milta
  hai. Result docs/verification.md mein likho.
- Mujhe samjhao ki har test kyun hai, taaki viva mein explain kar sakoon.

DELIVERABLES: analysis/golden_model.py, analysis/compare.py, tb/tb_cache_directed.v,
tb/tb_cache_trace.v, Makefile, docs/verification.md, 3 waveform screenshots.
DONE jab `make test` sab pass kare aur mutation tests fail hon jaise expected.
```

---

## 10.5 Prompt: M5 (Traces + Analysis + Report)

```
Tum ek computer architecture engineer aur technical writer ho. Main MCA capstone team ka M5
hoon: Memory-access traces, hit/miss analysis, AMAT calculation aur final report mere
zimme hain. Project ke "architectural analysis" aur "hit/miss report" wale deliverables
mere paas hain.

Pehle /MCA/project.md aur /MCA/plan.md padho. Section 2 (config), 4.4 (trace format) aur
4.5 (RTL log format) strictly follow karne hain. Addresses sab 0x00000000 se 0x0003FFFF ke
andar rakhna.

MERA KAAM:
1. traces/gen_traces.py (seed fixed, reproducible). Ye traces banao (4.4 format, do hex
   columns: op addr). Har trace 2000 to 10000 accesses, word-aligned:
   - seq.trace: sequential word reads (spatial locality, expected hit ~75% for 16 B block)
   - random.trace: uniform random over 256 KB (kam locality, hit ~ cache/footprint ke
     aaspaas, bahut kam)
   - loop.trace: chhota working set (jaise 512 B) baar-baar (temporal locality, high hit)
   - stride.trace: stride = 16, 64, 1024 B (stride=1024 conflict miss dikhata hai, kyunki
     sab ek hi index par jaate hain)
   - matrix_row.trace aur matrix_col.trace: 64x64 int matrix row-major vs column-major
     traversal
   - mixed.trace: loop + occasional random (real program jaisa)
   - Baseline sirf reads. Stretch ke liye alag write-mixed trace.
   Har trace ke saath uska expected behavior ek line comment mein docs/traces.md mein likho
   (kya locality dikhata hai, aur hit ratio ka mera analytical estimate).
2. analysis/analyze.py: RTL sim CSV (4.5) padhe, aur nikale: total, hits, misses, hit ratio,
   miss ratio, avg hit latency, measured avg miss penalty, measured AMAT (= avg latency
   of all accesses), aur formula AMAT = hit_time + miss_rate x miss_penalty. Dono compare
   karo, aur difference ka reason likho (agar ho). Compulsory/conflict miss breakdown nikalo
   (cold = us block ka pehla access; baaki conflict/capacity jaisa classify).
   Output: analysis/results/summary.csv aur markdown table.
3. Parameter sweep: cache size 512 B/1 KB/2 KB/4 KB, block 8/16/32/64 B, sab traces par.
   Plots (matplotlib, saaf labels): hit ratio vs block size, hit ratio vs cache size,
   AMAT vs block size (miss penalty block size ke saath badhta hai, ye tradeoff explain
   karo), per-trace bar chart. Sweep M4 ke golden_model.py se bhi chal sakta hai (fast),
   par kam se kam 1 KB/16 B config RTL simulation se confirm karo.
4. AMAT worked example report ke liye: hit_time = 1 cycle, MEM_LATENCY=4 => miss penalty
   ka number M1 ke docs/fsm.md aur sim se lo (khud anumaan mat lagao). Ek hand-calculated
   example 3 traces ke liye.
5. Hit/miss report (docs/hit_miss_report.md) aur final report (report/): structure:
   Introduction -> Memory hierarchy & locality -> Address breakdown (M1 se) -> Architecture
   & modules (M2, M3) -> FSM (M1) -> Verification (M4) -> Traces & results -> AMAT ->
   Synthesis (M3) -> Conclusion & future work (associativity, write-back). Plus 10-12 slide
   PPT outline aur demo script (2-3 min).
   Sabke inputs lena, aur sabke sections ko ek voice mein edit karna mera kaam hai.

QUALITY BAR:
- Koi bhi number tab hi report mein jaye jab wo script/sim se aaya ho. Reproducible:
  `make analysis` ek command mein sab regenerate kare.
- Conclusions honest ho. Agar result expected se alag aaye (jaise random trace ka hit
  ratio), to reason explain karo.
- Pehle mujhe trace list + expected results ki table dikhao, phir code.
- Mujhe sab concepts (locality, 3 C's of misses, AMAT) simple language mein samjhao taaki
  viva mein confidently bol sakoon.

TIMELINE: traces + analyze.py RTL ke bina bhi shuru ho sakta hai (golden model se test
karo). Report ke skeleton P1 mein hi bana do aur sections fill karte raho.
DELIVERABLES: traces/gen_traces.py + *.trace, docs/traces.md, analysis/analyze.py,
analysis/results/*, docs/hit_miss_report.md, report/, PPT. DONE jab `make analysis`
saari tables/plots banaye aur report mein har number ka source ho.
```

---

## 11. Day-1 meeting agenda (30 min)

1. Section 2 aur 4 padho, objections lo, freeze karo (10 min).
2. Naam <-> role assign (section 5) (5 min).
3. Tools check: `iverilog -V`, `gtkwave --version`, `python3 --version`, `yosys -V` (5 min).
4. Repo/branches/folder banana (5 min).
5. Agla sync kab (5 min).
