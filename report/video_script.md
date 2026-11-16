# Phase I Prototype Video Demonstration Script (Single Presenter)

> **Format:** 1 person speaking and screen-recording on behalf of the entire 5-member team.  
> **Target Duration:** ~4 minutes 15 seconds (Maximum allowed: 5:00 minutes).  
> **Language:** Simple, clear, conversational English.  
> **Tools to Record:** Zoom (start a meeting alone and hit Record), Google Meet, OBS Studio, or Mac QuickTime Screen Recording.

---

## 📋 What to Have Open on Your Screen Before Recording:
1. **Window 1 (Browser Tab 1):** `docs/architecture_block_diagram.svg` (Architecture Diagram).
2. **Window 2 (Browser Tab 2):** `analysis/results/hit_ratio_by_trace.png` (Performance Results Plot) or `report/ieee_project_report.pdf`.
3. **Window 3 (Terminal):** Sized to 16pt+ font, navigated to project directory:
   ```sh
   cd /Users/ash/CascadeProjects/projects..../MCA/mca-capstone
   ```

---

## 🎙️ Word-by-Word Script with Screen Cues

---

### [0:00 – 0:45] 1. Welcome, Project Idea & Team Introduction
*(Screen: Show the GitHub `README.md` page or Title of `report/presentation.html`)*

> "Hello everyone! Welcome to our Phase I prototype demonstration for the MCA Capstone project in Computer Architecture.  
> 
> My name is **[Your Name]**, and today I am presenting our project on behalf of our complete 5-member team:  
> - **Pankaj Baid** — our Team Lead and System Architect, who designed the Cache Controller FSM.  
> - **Ashutosh Singh** — our Storage Datapath Engineer, who built the Address Decoder and RAM modules.  
> - **Narendra Singh** — our Memory Interface and FPGA Synthesis lead.  
> - **Shreya Suman** — our Verification Lead, who built the Python Golden Model and testbenches.  
> - And **Ranvendra Pratap Singh** — our Workload Analyst, who generated the memory traces and performance study.  
> 
> **Project Idea:**  
> Modern processors run at gigahertz speeds, but main memory takes many clock cycles to respond. To solve this memory wall, our project designs a **Synthesizable 1 Kilobyte Direct-Mapped Cache Controller in Verilog**.  
> Our cache provides a **1-cycle read hit** when data is already present, and automatically refills 4-word blocks from main memory during a miss."

---

### [0:45 – 1:45] 2. System Architecture & How It Works
*(Screen: Switch to `docs/architecture_block_diagram.svg`)*

> "Here on the screen is our System Architecture Block Diagram:  
> 
> When the CPU sends a 32-bit address, our **Address Decoder** breaks it into three parts:  
> 1. A **22-bit Tag** to identify the memory block.  
> 2. A **6-bit Index** to select one of 64 cache lines.  
> 3. A **4-bit Offset** to choose the exact byte and word within the 16-byte block.  
> 
> Inside the cache datapath, we have three storage blocks:  
> - First, the **Valid RAM**: 64 flip-flops that reset to zero synchronously in just one cycle, so no uninitialized data causes false hits after reset.  
> - Second, the **Tag RAM**: storing the 22-bit tags for each line.  
> - Third, the **Data RAM**: storing 64 lines of 128-bit data blocks, with word-granular write enables.  
> 
> Our **Tag Comparator** checks if the valid bit is 1 and the stored tag matches the requested tag.  
> - If it matches, it is a **HIT**! Data is returned through the Word Mux to the CPU in just **1 clock cycle**.  
> - If it does not match, it is a **MISS**. Our Controller FSM then coordinates a 4-word refill handshake with main memory, writes the words into Data RAM, updates the tag and valid bits on the final word, and completes in **22 clock cycles**."

---

### [1:45 – 3:10] 3. Live Terminal Demonstration (Working Prototype)
*(Screen: Switch to Terminal window)*

> "Now, let us demonstrate the working prototype live.  
> I will run `make test` in our terminal:  
> 
> *(Type `make test` and hit Enter)*  
> 
> Look at the live execution:  
> 1. First, all **M2 unit tests** for the decoder, RAMs, and comparator run and PASS.  
> 2. Next, the **M3 memory integration tests** run across different memory latencies and PASS.  
> 3. Then, our **Directed Verification Testbench** runs 10 specific test cases:  
>    - Checking cold start reset (verifying address zero does not falsely hit).  
>    - Checking temporal locality (re-reading the same address gives a 1-cycle hit).  
>    - Checking spatial locality (reading one word brings all 4 words of the block, so the next 3 words hit).  
>    - Checking conflict misses when two addresses share the same line index.  
>    - Checking mid-test reset and counter accuracy.  
>    As you can see, all **146 directed checks pass with zero errors**!  
> 4. Finally, the testbench runs **eight complete memory workloads** totaling over 32,000 accesses, comparing our Verilog simulation cycle-by-cycle against our bit-accurate Python Golden Model.  
> 
> And as shown on screen: **All verification suite tests have passed with 100% bit-exact match!**"

---

### [3:10 – 3:55] 4. Performance & Hardware Synthesis Results
*(Screen: Switch to `analysis/results/hit_ratio_by_trace.png` or `docs/synthesis.md`)*

> "Here are our key performance and synthesis results:  
> - In our **Repeated Loop** workload, the working set fits completely in cache, achieving a **99.22% hit ratio** and an Average Memory Access Time of just **1.16 cycles**.  
> - In our **Sequential** and **Row-Major Matrix** workloads, we get exactly **75.00% hits**, proving 4-word spatial reuse.  
> - In our **Column-Major Matrix** workload, we get **0% hits**, clearly showing the conflict misses of direct-mapped caches.  
> - For hardware synthesis using Yosys: on Xilinx 7-series, our design utilizes only **312 logic LUTs** and **150 distributed RAM cells**, achieving an operating frequency of **83.15 MHz** on Lattice iCE40."

---

### [3:55 – 4:20] 5. Conclusion & Submission
*(Screen: Switch back to GitHub repository `README.md`)*

> "To conclude:  
> Our Phase I prototype is completely implemented in Verilog, thoroughly verified with 146 checks, synthesized for FPGA, and documented in our official IEEE report.  
> 
> All our source code, testbenches, waveforms, and reports are published on our GitHub repository.  
> 
> Thank you very much for your time and evaluation!"

---

## 💡 Quick Tips for the Presenter:
- **Pacing:** Speak at a calm, natural pace. You do not need to rush; the script is only ~580 words and comfortably takes 4:15.
- **Audio:** Use earphones or a headset so your voice is crisp and clear.
- **Resolution:** Share your full screen or a 1080p browser window.
- **After Recording:**
  1. Upload video to **YouTube (Set visibility to 'Unlisted')** or **Google Drive (Set share to 'Anyone with link can view')**.
  2. Copy that link and submit the Google Form before 11:59 PM!
