(() => {
  'use strict';

  const slides = Array.from(document.querySelectorAll('.slide'));
  const totalSlides = slides.length;
  const progressBar = document.getElementById('progressBar');
  const dotNav = document.getElementById('dotNav');
  const chapterPills = Array.from(document.querySelectorAll('.chap-pill'));
  const hudLabel = document.getElementById('hudLabel');
  const slideCount = document.getElementById('slideCount');
  const btnPrev = document.getElementById('btnPrev');
  const btnNext = document.getElementById('btnNext');
  const btnNotes = document.getElementById('btnNotes');
  const notesDrawer = document.getElementById('notesDrawer');
  const notesText = document.getElementById('notesText');
  const lightbox = document.getElementById('lightbox');
  const lbImg = document.getElementById('lbImg');

  let currentIdx = 0;
  let activeTimers = [];
  let activeRafs = [];
  let sharedAddr = 0x00001A2C;
  let notesOpen = false;

  function addTimer(fn, ms) {
    const id = setTimeout(fn, ms);
    activeTimers.push(id);
    return id;
  }

  function addRaf(fn) {
    const id = requestAnimationFrame(fn);
    activeRafs.push(id);
    return id;
  }

  function clearSlideTimers() {
    activeTimers.forEach((id) => clearTimeout(id));
    activeTimers = [];
    activeRafs.forEach((id) => cancelAnimationFrame(id));
    activeRafs = [];
  }

  // ---------- Shared Direct-Mapped Cache Model (1 KiB, 16 B block, 64 lines) ----------
  class CacheModel {
    constructor() { this.reset(); }
    reset() {
      this.lines = Array.from({ length: 64 }, () => ({ valid: false, tag: 0, words: [0, 0, 0, 0] }));
      this.hits = 0;
      this.misses = 0;
    }
    decode(addr) {
      const u = addr >>> 0;
      return {
        addr: u,
        offset: u & 0xF,
        wordSel: (u >>> 2) & 0x3,
        index: (u >>> 4) & 0x3F,
        tag: u >>> 10
      };
    }
    lookup(addr) {
      const d = this.decode(addr);
      const line = this.lines[d.index];
      const hit = line.valid && line.tag === d.tag;
      if (hit) {
        this.hits++;
      } else {
        this.misses++;
        const base = (d.addr & ~0xF) >>> 0;
        for (let w = 0; w < 4; w++) {
          const wa = ((base + w * 4) >>> 2) >>> 0;
          line.words[w] = Math.imul(wa, 0x9E3779B1) >>> 0;
        }
        line.tag = d.tag;
        line.valid = true;
      }
      return { hit, ...d, line };
    }
  }

  const s9Model = new CacheModel();
  const simModel = new CacheModel();

  // ---------- Ambient Hex Background ----------
  function initBgHex() {
    const layer = document.getElementById('bgHexLayer');
    if (!layer) return;
    const samples = ['0x00001A2C', '0x00001E2C', '0x00002010', '0x00002410', '0x00010004', '0x0003FFFC'];
    for (let i = 0; i < 12; i++) {
      const el = document.createElement('span');
      el.className = 'bg-hex-item';
      el.textContent = samples[i % samples.length];
      el.style.left = `${(i * 7.8 + 4) % 92}%`;
      el.style.animationDelay = `${-(i * 1.8)}s`;
      el.style.animationDuration = `${19 + (i % 5) * 3}s`;
      layer.appendChild(el);
    }
  }

  // ---------- Dot Nav & Top Chapter Nav ----------
  const chapterAccents = {
    'Intro': 'var(--acc-a)',
    'Chapter A': 'var(--acc-a)',
    'Chapter B': 'var(--acc-b)',
    'Chapter C': 'var(--acc-c)',
    'Chapter D': 'var(--acc-d)',
    'Chapter E': 'var(--acc-e)',
    'Finale': 'var(--acc-b)',
    'Closing': 'var(--hit)'
  };

  function initDots() {
    slides.forEach((s, i) => {
      const btn = document.createElement('button');
      btn.className = 'dot-btn';
      btn.setAttribute('aria-label', `Go to slide ${i + 1}: ${s.dataset.title}`);
      btn.setAttribute('data-tooltip', `${i + 1}. ${s.dataset.title}`);
      const acc = chapterAccents[s.dataset.chapter];
      if (acc) btn.style.setProperty('--dot-acc', acc);
      btn.addEventListener('click', () => goTo(i));
      dotNav.appendChild(btn);
    });

    chapterPills.forEach((pill) => {
      pill.addEventListener('click', () => goTo(parseInt(pill.dataset.slide, 10)));
    });
    document.querySelectorAll('.member-chip[data-jump]').forEach((chip) => {
      chip.addEventListener('click', () => goTo(parseInt(chip.dataset.jump, 10)));
    });
  }

  // ---------- Lightbox Zoom for Diagrams & Plots ----------
  function initLightbox() {
    document.querySelectorAll('.zoomable-img').forEach((img) => {
      img.addEventListener('click', () => {
        lbImg.src = img.src;
        lbImg.alt = img.alt;
        lightbox.hidden = false;
      });
    });
    const closeLb = () => { lightbox.hidden = true; };
    document.getElementById('lbClose').addEventListener('click', closeLb);
    lightbox.addEventListener('click', (e) => {
      if (e.target === lightbox) closeLb();
    });
  }

  // ---------- Count-Up Animations ----------
  function runCountUps(slideEl) {
    slideEl.querySelectorAll('.count-up').forEach((el) => {
      const target = parseFloat(el.dataset.target || '0');
      const dec = parseInt(el.dataset.decimals || '0', 10);
      const suffix = el.dataset.suffix || '';
      const start = performance.now();
      const dur = 700;
      function step(now) {
        const p = Math.min(1, (now - start) / dur);
        const eased = 1 - Math.pow(1 - p, 3);
        const val = target * eased;
        el.textContent = (dec > 0 ? val.toFixed(dec) : Math.round(val)) + suffix;
        if (p < 1) addRaf(step);
      }
      addRaf(step);
    });
  }

  // ---------- Slide 2: Memory Wall Race ----------
  function playMemoryWall() {
    const pktFast = document.getElementById('pktFast');
    const pktSlow = document.getElementById('pktSlow');
    const tickFast = document.getElementById('tickFast');
    const tickSlow = document.getElementById('tickSlow');
    if (!pktFast || !pktSlow) return;

    const start = performance.now();
    const totalDur = 2300;
    function frame(now) {
      const elapsed = now - start;
      const slowP = Math.min(1, elapsed / totalDur);
      const fastP = Math.min(1, elapsed / 240);
      pktSlow.style.left = `${(slowP < 0.5 ? slowP * 2 : (1 - (slowP - 0.5) * 2)) * 94}%`;
      pktFast.style.left = `${(fastP < 0.5 ? fastP * 2 : (1 - (fastP - 0.5) * 2)) * 94}%`;
      tickFast.textContent = fastP >= 1 ? '1' : '0';
      tickSlow.textContent = Math.max(1, Math.min(22, Math.round(slowP * 22)));
      if (slowP < 1) addRaf(frame);
    }
    addRaf(frame);
  }

  // ---------- Slide 6: FSM Simulator ----------
  const fsmNodes = {
    IDLE: document.getElementById('nodeIDLE'),
    REFILL: document.getElementById('nodeREFILL'),
    RESPOND: document.getElementById('nodeRESPOND')
  };
  const lamps = {
    statHit: document.getElementById('lampStatHit'),
    statMiss: document.getElementById('lampStatMiss'),
    memReq: document.getElementById('lampMemReq'),
    memAck: document.getElementById('lampMemAck'),
    tagValidWe: document.getElementById('lampTagValidWe'),
    cpuReady: document.getElementById('lampCpuReady')
  };

  function resetFsmUi() {
    Object.values(fsmNodes).forEach((n) => n && n.classList.remove('is-lit', 'is-hit', 'is-miss'));
    ['edgeIdleRefill', 'edgeRefillLoop', 'edgeRefillResp', 'edgeRespIdle'].forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.classList.remove('is-lit');
    });
    Object.values(lamps).forEach((l) => l && l.classList.remove('on-hit', 'on-miss', 'on-warn'));
    if (fsmNodes.IDLE) fsmNodes.IDLE.classList.add('is-lit');
    document.getElementById('fsmCycle').textContent = '0';
    document.getElementById('fsmWord').textContent = '-';
  }

  function simulateFsmHit() {
    clearSlideTimers();
    resetFsmUi();
    fsmNodes.IDLE.classList.add('is-hit');
    lamps.statHit.classList.add('on-hit');
    lamps.cpuReady.classList.add('on-hit');
    document.getElementById('fsmCycle').textContent = '1';
    document.getElementById('fsmCaption').textContent =
      'HIT in 1 cycle! Mealy output in S_IDLE asserts cpu_ready & stat_hit right away.';
  }

  function simulateFsmMiss() {
    clearSlideTimers();
    resetFsmUi();
    let cycle = 0;
    const cap = document.getElementById('fsmCaption');
    const cycEl = document.getElementById('fsmCycle');
    const wrdEl = document.getElementById('fsmWord');

    function tick() {
      cycEl.textContent = String(cycle + 1);
      Object.values(fsmNodes).forEach((n) => n.classList.remove('is-lit', 'is-hit', 'is-miss'));
      Object.values(lamps).forEach((l) => l.classList.remove('on-hit', 'on-miss', 'on-warn'));

      if (cycle === 0) {
        fsmNodes.IDLE.classList.add('is-miss');
        lamps.statMiss.classList.add('on-miss');
        document.getElementById('edgeIdleRefill').classList.add('is-lit');
        wrdEl.textContent = 'Detect';
        cap.textContent = 'Cycle 1 (S_IDLE): Tag mismatch -> stat_miss=1 pulse, move to S_REFILL.';
      } else if (cycle >= 1 && cycle <= 20) {
        const w = Math.floor((cycle - 1) / 5);
        const sub = (cycle - 1) % 5;
        fsmNodes.REFILL.classList.add('is-lit');
        lamps.memReq.classList.add('on-warn');
        document.getElementById('edgeRefillLoop').classList.add('is-lit');
        wrdEl.textContent = `${w} / 3`;
        if (sub === 4) {
          lamps.memAck.classList.add('on-hit');
          if (w === 3) {
            lamps.tagValidWe.classList.add('on-hit');
            document.getElementById('edgeRefillResp').classList.add('is-lit');
            cap.textContent = `Cycle ${cycle + 1} (S_REFILL): Word 3 ack -> commit tag_we & valid_we!`;
          } else {
            cap.textContent = `Cycle ${cycle + 1} (S_REFILL): Word ${w} ack -> write word into data_ram.`;
          }
        } else {
          cap.textContent = `Cycle ${cycle + 1} (S_REFILL): Waiting for Word ${w} from main memory...`;
        }
      } else if (cycle === 21) {
        fsmNodes.RESPOND.classList.add('is-hit');
        lamps.cpuReady.classList.add('on-hit');
        document.getElementById('edgeRespIdle').classList.add('is-lit');
        wrdEl.textContent = 'Done';
        cap.textContent = 'Cycle 22 (S_RESPOND): Block complete -> cpu_ready=1, return to S_IDLE.';
      }

      cycle++;
      if (cycle <= 21) addTimer(tick, 145);
    }
    tick();
  }

  // ---------- Shared Address Setter (Slides 8 & 9) ----------
  function syncAddressDisplays(addr) {
    sharedAddr = addr >>> 0;
    const d = s9Model.decode(sharedAddr);
    const hexFull = '0x' + sharedAddr.toString(16).toUpperCase().padStart(8, '0');

    const bitGrid = document.getElementById('bitGrid');
    if (bitGrid) {
      bitGrid.querySelectorAll('.bit-cell').forEach((cell) => {
        const b = parseInt(cell.dataset.bit, 10);
        const val = (sharedAddr >>> b) & 1;
        const span = cell.querySelector('.bval');
        if (span.textContent !== String(val)) {
          span.textContent = String(val);
          cell.classList.remove('flip');
          void cell.offsetWidth;
          cell.classList.add('flip');
        }
      });
    }

    const input = document.getElementById('addrInput');
    if (input && document.activeElement !== input) input.value = hexFull;
    document.getElementById('decTag').textContent = '0x' + d.tag.toString(16).toUpperCase().padStart(6, '0');
    document.getElementById('decIdx').textContent = `Line ${d.index}`;
    document.getElementById('decWord').textContent = `Word ${d.wordSel}`;

    const s9Lbl = document.getElementById('s9AddrLbl');
    if (s9Lbl) s9Lbl.textContent = hexFull;
    document.querySelectorAll('.s9-pick').forEach((btn) => {
      const val = parseInt(btn.dataset.addr, 16) >>> 0;
      btn.classList.toggle('is-selected', val === sharedAddr);
    });
  }

  function initDecoder() {
    const grid = document.getElementById('bitGrid');
    const input = document.getElementById('addrInput');
    const err = document.getElementById('addrErr');
    if (!grid || !input) return;

    for (let b = 31; b >= 0; b--) {
      const cell = document.createElement('div');
      let cls = 'bc-byte';
      if (b >= 10) cls = 'bc-tag';
      else if (b >= 4) cls = 'bc-idx';
      else if (b >= 2) cls = 'bc-wsel';
      cell.className = `bit-cell ${cls}`;
      cell.dataset.bit = String(b);
      cell.innerHTML = `<span class="bval">0</span><small>${b}</small>`;
      grid.appendChild(cell);
    }

    input.addEventListener('input', () => {
      const cleaned = input.value.trim().replace(/^0x/i, '');
      if (!/^[0-9a-fA-F]{1,8}$/.test(cleaned)) {
        err.textContent = 'Enter 1-8 hex digits (e.g. 0x00001A2C)';
        return;
      }
      err.textContent = '';
      syncAddressDisplays(parseInt(cleaned, 16) >>> 0);
    });

    document.querySelectorAll('.preset-addr, .s9-pick').forEach((btn) => {
      btn.addEventListener('click', () => {
        err.textContent = '';
        syncAddressDisplays(parseInt(btn.dataset.addr, 16) >>> 0);
      });
    });

    syncAddressDisplays(sharedAddr);
  }

  // ---------- Slide 9: Storage Grid ----------
  function build64Grid(containerId) {
    const el = document.getElementById(containerId);
    if (!el) return;
    el.innerHTML = '';
    for (let i = 0; i < 64; i++) {
      const c = document.createElement('div');
      c.className = 'cache-cell';
      c.dataset.idx = String(i);
      c.textContent = String(i);
      el.appendChild(c);
    }
  }

  function syncGridValid(containerId, model) {
    const el = document.getElementById(containerId);
    if (!el) return;
    el.querySelectorAll('.cache-cell').forEach((c, idx) => {
      c.classList.toggle('is-valid', model.lines[idx].valid);
      c.classList.remove('flash-hit', 'flash-miss', 'flash-reset');
    });
  }

  function initSlide9() {
    build64Grid('s9Grid');
    const btnLookup = document.getElementById('btnLookupSlide9');
    const btnReset = document.getElementById('btnResetSlide9');

    btnLookup.addEventListener('click', () => {
      const res = s9Model.lookup(sharedAddr);
      syncGridValid('s9Grid', s9Model);
      const cell = document.querySelector(`#s9Grid .cache-cell[data-idx="${res.index}"]`);
      if (cell) cell.classList.add(res.hit ? 'flash-hit' : 'flash-miss');

      document.getElementById('s9LineIdx').textContent = `Line ${res.index}`;
      document.getElementById('pipeValidVal').textContent = 'valid = 1';
      document.getElementById('pipeTagVal').textContent = 'tag = 0x' + res.tag.toString(16).toUpperCase();
      const cmpStep = document.getElementById('pipeCmp');
      cmpStep.classList.remove('is-hit', 'is-miss');
      cmpStep.classList.add(res.hit ? 'is-hit' : 'is-miss');
      document.getElementById('pipeCmpVal').textContent = res.hit ? 'HIT (1 cycle)' : 'MISS (Fill 4 words)';

      const slots = document.querySelectorAll('#s9Words .w-slot');
      slots.forEach((s) => s.classList.remove('filled'));
      if (res.hit) {
        slots.forEach((s, w) => { s.textContent = `W${w}`; s.classList.add('filled'); });
      } else {
        for (let w = 0; w < 4; w++) {
          addTimer(() => {
            slots[w].textContent = '0x' + (res.line.words[w] >>> 0).toString(16).slice(-4).toUpperCase();
            slots[w].classList.add('filled');
          }, w * 130);
        }
      }
    });

    btnReset.addEventListener('click', () => {
      s9Model.reset();
      const cells = document.querySelectorAll('#s9Grid .cache-cell');
      cells.forEach((c) => {
        c.classList.remove('is-valid', 'flash-hit', 'flash-miss');
        c.classList.add('flash-reset');
      });
      addTimer(() => cells.forEach((c) => c.classList.remove('flash-reset')), 280);
      document.getElementById('pipeValidVal').textContent = 'valid = 0 (cleared)';
      document.getElementById('pipeTagVal').textContent = 'tag = -';
      const cmpStep = document.getElementById('pipeCmp');
      cmpStep.classList.remove('is-hit', 'is-miss');
      document.getElementById('pipeCmpVal').textContent = 'RESET (1 cycle)';
      document.querySelectorAll('#s9Words .w-slot').forEach((s, w) => {
        s.classList.remove('filled');
        s.textContent = `W${w}`;
      });
    });
  }

  // ---------- Slide 11: Animated 22-Cycle Waveform ----------
  function buildWaveGrid() {
    const wrap = document.getElementById('waveGridWrap');
    if (!wrap) return;
    const cols = 22;
    let html = '<table class="wave-table"><thead><tr><th class="sig-col">Cycle</th>';
    for (let c = 0; c < cols; c++) html += `<th data-col="${c}">${c}</th>`;
    html += '</tr></thead><tbody>';

    const rows = [
      { name: 'mem_req', fn: (c) => (c >= 1 && c <= 20 ? { txt: '1', cls: 'hi' } : { txt: '0', cls: '' }) },
      { name: 'mem_ack', fn: (c) => ([5, 10, 15, 20].includes(c) ? { txt: '1', cls: 'ack' } : { txt: '0', cls: '' }) },
      { name: 'mem_addr', fn: (c) => {
        if (c >= 1 && c <= 5) return { txt: '1A20', cls: 'hi' };
        if (c >= 6 && c <= 10) return { txt: '1A24', cls: 'hi' };
        if (c >= 11 && c <= 15) return { txt: '1A28', cls: 'hi' };
        if (c >= 16 && c <= 20) return { txt: '1A2C', cls: 'hi' };
        return { txt: '-', cls: '' };
      }},
      { name: 'cpu_ready', fn: (c) => (c === 21 ? { txt: '1', cls: 'rdy' } : { txt: '0', cls: '' }) }
    ];

    rows.forEach((r) => {
      html += `<tr><td class="sig-col"><code>${r.name}</code></td>`;
      for (let c = 0; c < cols; c++) {
        const cell = r.fn(c);
        html += `<td data-col="${c}" class="${cell.cls}">${cell.txt}</td>`;
      }
      html += '</tr>';
    });
    html += '</tbody></table>';
    wrap.innerHTML = html;
  }

  function playWaveSweep() {
    const table = document.querySelector('#waveGridWrap .wave-table');
    if (!table) return;
    let c = 0;
    function step() {
      table.querySelectorAll('.playhead').forEach((el) => el.classList.remove('playhead'));
      if (c < 22) {
        table.querySelectorAll(`[data-col="${c}"]`).forEach((el) => el.classList.add('playhead'));
        c++;
        addTimer(step, 115);
      }
    }
    step();
  }

  // ---------- Slide 17 & 18: Charts ----------
  const traceData = [
    { name: 'loop', hit: 99.22, amat: 1.164, comp: 32, conf: 0, cap: 0, color: '#22c55e', story: 'loop (99.22% hits · AMAT 1.164 cyc): 512 B working set fits completely inside our 1 KiB cache — classic temporal locality!' },
    { name: 'mixed', hit: 79.42, amat: 5.322, comp: 618, conf: 217, cap: 8, color: '#a3e635', story: 'mixed (79.42% hits · AMAT 5.322 cyc): Realistic blend of hot repeated reads and occasional scattered reads.' },
    { name: 'matrix_row', hit: 75.00, amat: 6.250, comp: 1024, conf: 0, cap: 0, color: '#2dd4bf', story: 'matrix_row (75.00% hits · AMAT 6.250 cyc): Walks 4 neighboring words per 16 B block (1 miss + 3 spatial hits).' },
    { name: 'seq', hit: 75.00, amat: 6.250, comp: 1024, conf: 0, cap: 0, color: '#7c9cff', story: 'seq (75.00% hits · AMAT 6.250 cyc): Sequential streaming achieves exact 75% spatial reuse.' },
    { name: 'random', hit: 0.46, amat: 21.903, comp: 3616, conf: 2, cap: 459, color: '#f59e0b', story: 'random (0.46% hits · AMAT 21.903 cyc): Jumps uniformly across 256 KiB; practically zero locality.' },
    { name: 'matrix_col', hit: 0.00, amat: 22.000, comp: 1024, conf: 3072, cap: 0, color: '#ef4444', story: 'matrix_col (0.00% hits · AMAT 22.000 cyc): 256 B column stride collides on indices -> 3,072 conflict misses!' },
    { name: 'stride', hit: 0.00, amat: 22.000, comp: 2390, conf: 1364, cap: 342, color: '#f472b6', story: 'stride (0.00% hits · AMAT 22.000 cyc): Ping-pong accesses 1,024 B apart overwrite the exact same index.' }
  ];

  function selectBarCol(idx) {
    const cols = document.querySelectorAll('#hitBarChart .vbar-col');
    const storyBar = document.getElementById('traceStoryBar');
    cols.forEach((c, i) => c.classList.toggle('is-selected', i === idx));
    if (storyBar && traceData[idx]) storyBar.textContent = traceData[idx].story;
  }

  function initCharts() {
    const vbar = document.getElementById('hitBarChart');
    if (vbar) {
      vbar.innerHTML = '';
      traceData.forEach((t, idx) => {
        const col = document.createElement('div');
        col.className = 'vbar-col';
        col.innerHTML = `
          <span class="vbar-val">${t.hit.toFixed(2)}%</span>
          <div class="vbar-fill" data-h="${Math.max(2, t.hit)}" style="background:${t.color}"></div>
          <span class="vbar-lbl">${t.name}</span>
        `;
        col.addEventListener('mouseenter', () => selectBarCol(idx));
        col.addEventListener('click', () => selectBarCol(idx));
        vbar.appendChild(col);
      });
      selectBarCol(0);
    }

    const s3c = document.getElementById('stacked3c');
    if (s3c) {
      s3c.innerHTML = '';
      traceData.forEach((t) => {
        const pComp = (t.comp / 4096) * 100;
        const pConf = (t.conf / 4096) * 100;
        const pCap = (t.cap / 4096) * 100;
        const row = document.createElement('div');
        row.className = 's3c-row';
        row.innerHTML = `
          <code>${t.name}</code>
          <div class="s3c-bar">
            <div class="s3c-seg sw-comp" style="width:${pComp}%"></div>
            <div class="s3c-seg sw-conf" style="width:${pConf}%"></div>
            <div class="s3c-seg sw-cap" style="width:${pCap}%"></div>
          </div>
          <span class="muted">${t.comp}/${t.conf}/${t.cap}</span>
        `;
        s3c.appendChild(row);
      });
    }

    const slider = document.getElementById('missSlider');
    if (slider) {
      const updateSlider = () => {
        const pct = parseInt(slider.value, 10);
        const amat = 1 + (pct / 100) * 21;
        document.getElementById('missPctLbl').textContent = `${pct}%`;
        document.getElementById('amatResult').textContent = `${amat.toFixed(2)} cyc`;
      };
      slider.addEventListener('input', updateSlider);
      updateSlider();
    }
  }

  // ---------- Slide 19: Live Workload Simulator ----------
  function initLiveSim() {
    build64Grid('simGrid');
    const patButtons = document.querySelectorAll('.pat-btn');
    const stopBtn = document.getElementById('btnStopSim');

    function buildTracePattern(pat) {
      const addrs = [];
      if (pat === 'seq') {
        for (let i = 0; i < 48; i++) addrs.push((0x00001000 + i * 4) >>> 0);
      } else if (pat === 'loop') {
        for (let i = 0; i < 48; i++) addrs.push((0x00002000 + (i % 16) * 4) >>> 0);
      } else if (pat === 'conflict') {
        for (let i = 0; i < 48; i++) addrs.push(i % 2 === 0 ? 0x00002010 : 0x00002410);
      } else {
        let seed = 0x13572468;
        for (let i = 0; i < 48; i++) {
          seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
          addrs.push((seed & 0x0003FFFC) >>> 0);
        }
      }
      return addrs;
    }

    function updateSimStats(step, total, lastTxt) {
      const tot = simModel.hits + simModel.misses;
      const ratio = tot ? (simModel.hits / tot) * 100 : 0;
      const missRate = tot ? simModel.misses / tot : 0;
      const amat = 1 + missRate * 21;
      document.getElementById('simHits').textContent = String(simModel.hits);
      document.getElementById('simMisses').textContent = String(simModel.misses);
      document.getElementById('simRatio').textContent = `${ratio.toFixed(1)}%`;
      document.getElementById('simAmat').textContent = amat.toFixed(2);
      document.getElementById('simLastEvent').textContent = `Step ${step} / ${total}`;
      if (lastTxt) document.getElementById('simAddrBar').textContent = lastTxt;
    }

    function runPattern(pat, label) {
      clearSlideTimers();
      simModel.reset();
      syncGridValid('simGrid', simModel);
      document.getElementById('simPatternLbl').textContent = label;
      const addrs = buildTracePattern(pat);
      let i = 0;
      function tick() {
        if (i >= addrs.length) return;
        const r = simModel.lookup(addrs[i]);
        syncGridValid('simGrid', simModel);
        const cell = document.querySelector(`#simGrid .cache-cell[data-idx="${r.index}"]`);
        if (cell) cell.classList.add(r.hit ? 'flash-hit' : 'flash-miss');
        const hex = '0x' + r.addr.toString(16).toUpperCase().padStart(8, '0');
        const msg = r.hit
          ? `${hex} -> HIT — Already in Line ${r.index} (1 cycle!)`
          : `${hex} -> MISS — Fetched 4-word block into Line ${r.index} (22 cycles)`;
        updateSimStats(i + 1, addrs.length, msg);
        i++;
        addTimer(tick, 155);
      }
      tick();
    }

    patButtons.forEach((btn) => {
      btn.addEventListener('click', () => runPattern(btn.dataset.pat, btn.textContent));
    });

    stopBtn.addEventListener('click', () => {
      clearSlideTimers();
      simModel.reset();
      syncGridValid('simGrid', simModel);
      document.getElementById('simPatternLbl').textContent = 'Select a workload above';
      updateSimStats(0, 48, 'Reset complete — click any workload pattern to start.');
    });
  }

  // ---------- Per-Slide onEnter Lifecycle ----------
  function onEnter(slideEl) {
    const id = parseInt(slideEl.dataset.id, 10);
    runCountUps(slideEl);

    if (id === 2) playMemoryWall();
    if (id === 6) resetFsmUi();
    if (id === 11) playWaveSweep();
    if (id === 12) {
      slideEl.querySelectorAll('.hbar-fill').forEach((f) => {
        f.style.width = '0%';
        addTimer(() => { f.style.width = `${f.dataset.w}%`; }, 60);
      });
    }
    if (id === 14) {
      const tiers = Array.from(document.querySelectorAll('#verifPyramid .pyr-tier'));
      tiers.forEach((t) => t.classList.remove('show'));
      tiers.slice().reverse().forEach((t, idx) => addTimer(() => t.classList.add('show'), 100 + idx * 160));
      const items = document.querySelectorAll('#tcChecklist li');
      items.forEach((li) => li.classList.remove('ticked'));
      items.forEach((li, idx) => addTimer(() => li.classList.add('ticked'), 120 + idx * 85));
    }
    if (id === 15) {
      const rows = document.querySelectorAll('#diffTable tbody tr');
      rows.forEach((r) => r.classList.remove('show'));
      rows.forEach((r, idx) => addTimer(() => r.classList.add('show'), 80 + idx * 100));
    }
    if (id === 17) {
      document.querySelectorAll('#hitBarChart .vbar-fill').forEach((b) => {
        b.style.height = '0%';
        addTimer(() => { b.style.height = `${b.dataset.h}%`; }, 80);
      });
      selectBarCol(0);
    }
  }

  // ---------- Presenter Notes Toggle ----------
  function setNotesOpen(open) {
    notesOpen = open;
    notesDrawer.hidden = !open;
    btnNotes.classList.toggle('is-on', open);
  }
  btnNotes.addEventListener('click', () => setNotesOpen(!notesOpen));

  // ---------- Navigation ----------
  function goTo(index) {
    const clamped = Math.max(0, Math.min(totalSlides - 1, index));
    clearSlideTimers();
    slides.forEach((s, i) => s.classList.toggle('is-active', i === clamped));
    currentIdx = clamped;

    const active = slides[currentIdx];
    const chap = active.dataset.chapter;
    const acc = chapterAccents[chap] || 'var(--acc-a)';
    document.documentElement.style.setProperty('--acc', acc);
    document.body.classList.toggle('is-cover-mode', active.classList.contains('is-cover'));

    dotNav.querySelectorAll('.dot-btn').forEach((d, i) => d.classList.toggle('is-active', i === currentIdx));
    chapterPills.forEach((p) => p.classList.toggle('is-active', p.dataset.chap === chap));

    progressBar.style.width = `${((currentIdx + 1) / totalSlides) * 100}%`;
    hudLabel.textContent = `${chap} \u00b7 ${active.dataset.person}`;
    slideCount.textContent = `${currentIdx + 1} / ${totalSlides}`;
    notesText.textContent = active.dataset.note || '';
    btnPrev.disabled = currentIdx === 0;
    btnNext.disabled = currentIdx === totalSlides - 1;
    location.hash = `#${currentIdx + 1}`;

    onEnter(active);
  }

  btnPrev.addEventListener('click', () => goTo(currentIdx - 1));
  btnNext.addEventListener('click', () => goTo(currentIdx + 1));

  document.addEventListener('keydown', (e) => {
    if (!lightbox.hidden && e.key === 'Escape') {
      lightbox.hidden = true;
      return;
    }
    if (e.target && e.target.tagName === 'INPUT') return;
    if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {
      e.preventDefault();
      goTo(currentIdx + 1);
    } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
      e.preventDefault();
      goTo(currentIdx - 1);
    } else if (e.key === 'Home') {
      goTo(0);
    } else if (e.key === 'End') {
      goTo(totalSlides - 1);
    } else if (e.key === 'n' || e.key === 'N') {
      setNotesOpen(!notesOpen);
    } else if (e.key === 'f' || e.key === 'F') {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {});
      } else {
        document.exitFullscreen().catch(() => {});
      }
    } else if (/^[1-9]$/.test(e.key)) {
      const jumpMap = { '1': 0, '2': 4, '3': 6, '4': 9, '5': 12, '6': 15, '7': 18, '8': 19, '9': 19 };
      if (e.key in jumpMap) goTo(jumpMap[e.key]);
    }
  });

  document.getElementById('btnReplayWall').addEventListener('click', () => { clearSlideTimers(); playMemoryWall(); });
  document.getElementById('btnFsmHit').addEventListener('click', simulateFsmHit);
  document.getElementById('btnFsmMiss').addEventListener('click', simulateFsmMiss);
  document.getElementById('btnReplayWave').addEventListener('click', () => { clearSlideTimers(); playWaveSweep(); });

  initBgHex();
  initDots();
  initLightbox();
  initDecoder();
  initSlide9();
  buildWaveGrid();
  initCharts();
  initLiveSim();

  const initialHash = parseInt(location.hash.replace('#', ''), 10);
  const startSlide = Number.isFinite(initialHash) && initialHash >= 1 && initialHash <= totalSlides ? initialHash - 1 : 0;
  goTo(startSlide);
})();
