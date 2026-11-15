#!/usr/bin/env python3
"""Reproducible cache-trace metrics, AMAT calculation and parameter sweep."""
from __future__ import annotations
import argparse
import csv
import os
import re
import tempfile
from collections import OrderedDict
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRACES = ROOT / "traces"
DEFAULT_OUT = ROOT / "analysis" / "results"
WORD_BYTES = 4
HASH = 0x9E3779B1

def load_trace(path: Path) -> list[tuple[int, int]]:
    accesses = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        fields = line.split()
        if len(fields) != 2:
            raise ValueError(f"{path}:{line_no}: expected '<op> <hex-address>'")
        try:
            op, address = int(fields[0], 16), int(fields[1], 16)
        except ValueError as exc:
            raise ValueError(f"{path}:{line_no}: operation and address must be hexadecimal") from exc
        if op != 0:
            raise ValueError(f"{path}:{line_no}: baseline analysis is read-only; op must be 0")
        if not 0 <= address < 256 * 1024 or address % WORD_BYTES:
            raise ValueError(f"{path}:{line_no}: address must be word-aligned and within 0x00000000..0x0003ffff")
        accesses.append((op, address))
    if not accesses:
        raise ValueError(f"{path}: trace contains no accesses")
    return accesses

def word_value(address: int) -> int:
    return (((address >> 2) * HASH) & 0xFFFFFFFF)

def validate_config(cache_bytes: int, block_bytes: int, mem_latency: int) -> None:
    if cache_bytes <= 0 or cache_bytes & (cache_bytes - 1):
        raise ValueError("cache size must be a positive power of two")
    if block_bytes < 8 or block_bytes & (block_bytes - 1) or block_bytes % WORD_BYTES:
        raise ValueError("block size must be a power of two, at least 8 bytes, and word-aligned")
    if cache_bytes < 2 * block_bytes or cache_bytes % block_bytes:
        raise ValueError("cache size must be a multiple of block size and contain at least two blocks")
    if mem_latency < 1:
        raise ValueError("MEM_LATENCY must be >= 1 (RTL clamps values below one)")

def simulate(accesses: Iterable[tuple[int, int]], cache_bytes: int, block_bytes: int,
             mem_latency: int) -> tuple[list[dict], dict]:
    validate_config(cache_bytes, block_bytes, mem_latency)
    accesses = list(accesses)
    if not accesses:
        raise ValueError("cannot analyse an empty trace")
    lines = cache_bytes // block_bytes
    words_per_block = block_bytes // WORD_BYTES
    miss_latency = words_per_block * (mem_latency + 1) + 2
    tags, valid = [None] * lines, [False] * lines
    seen: set[int] = set()
    shadow: OrderedDict[int, None] = OrderedDict()
    rows = []
    hits = misses = compulsory = conflict = capacity = total_latency = 0
    for idx, (op, address) in enumerate(accesses):
        block = address // block_bytes
        line, tag = block % lines, block // lines
        word = (address % block_bytes) // WORD_BYTES
        hit = bool(valid[line] and tags[line] == tag)
        if hit:
            hits += 1
            latency, miss_class = 1, "hit"
        else:
            misses += 1
            latency = miss_latency
            if block not in seen:
                compulsory += 1
                miss_class = "compulsory"
            elif block in shadow:
                conflict += 1
                miss_class = "conflict"
            else:
                capacity += 1
                miss_class = "capacity"
            valid[line], tags[line] = True, tag
        seen.add(block)
        if block in shadow:
            shadow.move_to_end(block)
        else:
            shadow[block] = None
            if len(shadow) > lines:
                shadow.popitem(last=False)
        base = (address // block_bytes) * block_bytes
        rows.append({"idx": idx, "op": op, "addr": f"{address:08x}", "hit": int(hit),
                     "rdata": f"{word_value(base + word * WORD_BYTES):08x}",
                     "latency_cycles": latency, "miss_class": miss_class})
        total_latency += latency
    total = len(rows)
    miss_rate = misses / total
    measured_amat = total_latency / total
    miss_penalty = miss_latency - 1
    summary = {
        "accesses": total, "hits": hits, "misses": misses,
        "hit_ratio": hits / total, "miss_ratio": miss_rate,
        "compulsory_misses": compulsory, "conflict_misses": conflict,
        "capacity_misses": capacity, "hit_time_cycles": 1,
        "miss_latency_cycles": miss_latency, "miss_penalty_cycles": miss_penalty,
        "avg_hit_latency_cycles": 1.0 if hits else 0.0,
        "avg_miss_latency_cycles": float(miss_latency) if misses else 0.0,
        "measured_miss_penalty_cycles": float(miss_penalty) if misses else 0.0,
        "measured_amat_cycles": measured_amat,
        "formula_amat_cycles": 1 + miss_rate * miss_penalty,
        "amat_difference_cycles": measured_amat - (1 + miss_rate * miss_penalty),
    }
    return rows, summary

def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise ValueError(f"refusing to overwrite symlink: {path}")
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)

def csv_text(rows: list[dict]) -> str:
    if not rows:
        raise ValueError("refusing to write an empty result table")
    from io import StringIO
    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(rows[0]))
    writer.writeheader()
    for row in rows:
        safe = dict(row)
        for key, value in safe.items():
            if isinstance(value, str) and value.startswith(("=", "+", "-", "@")):
                safe[key] = "'" + value
        writer.writerow(safe)
    return output.getvalue()

def markdown_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("<", "&lt;").replace(">", "&gt;")

def validate_rtl_csv(path: Path, expected_rows: list[dict]) -> dict:
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        required = {"idx", "op", "addr", "hit", "rdata", "latency_cycles"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f"{path}: missing required RTL CSV columns {sorted(required)}")
        actual = list(reader)
    if not actual:
        raise ValueError(f"{path}: RTL CSV contains no data rows")
    if len(actual) != len(expected_rows):
        raise ValueError(f"RTL CSV row count {len(actual)} does not match trace count {len(expected_rows)}")
    for index, (got, expected) in enumerate(zip(actual, expected_rows)):
        try:
            normal = {"idx": int(got["idx"]), "op": int(got["op"]),
                      "addr": f"{int(got['addr'], 16):08x}", "hit": int(got["hit"]),
                      "rdata": f"{int(got['rdata'], 16):08x}",
                      "latency_cycles": int(got["latency_cycles"])}
        except (TypeError, ValueError, KeyError) as exc:
            raise ValueError(f"RTL CSV row {index}: malformed field: {exc}") from exc
        for key, value in normal.items():
            if value != expected[key]:
                raise ValueError(f"RTL/reference mismatch at row {index}, field {key}: RTL={value} reference={expected[key]}")
    hits = sum(int(row["hit"]) for row in actual)
    misses = len(actual) - hits
    hit_lat = [int(row["latency_cycles"]) for row in actual if int(row["hit"]) == 1]
    miss_lat = [int(row["latency_cycles"]) for row in actual if int(row["hit"]) == 0]
    measured = sum(int(row["latency_cycles"]) for row in actual) / len(actual)
    avg_hit = sum(hit_lat) / len(hit_lat) if hit_lat else 0.0
    avg_miss = sum(miss_lat) / len(miss_lat) if miss_lat else 0.0
    return {"hits": hits, "misses": misses, "hit_ratio": hits / len(actual),
            "miss_ratio": misses / len(actual), "avg_hit_latency_cycles": avg_hit,
            "avg_miss_latency_cycles": avg_miss,
            "measured_miss_penalty_cycles": avg_miss - 1 if misses else 0.0,
            "measured_amat_cycles": measured}

def make_plots(records: list[dict], out_dir: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib unavailable; CSV/Markdown retained, plots skipped")
        return
    base = [r for r in records if r["cache_bytes"] == 1024 and r["block_bytes"] == 16]
    if base:
        plt.figure()
        plt.bar([r["trace"] for r in base], [100 * r["hit_ratio"] for r in base])
        plt.ylabel("Hit ratio (%)"); plt.xlabel("Trace"); plt.title("Hit ratio by workload (1 KiB / 16 B)")
        plt.xticks(rotation=25, ha="right"); plt.tight_layout()
        plt.savefig(out_dir / "hit_ratio_by_trace.png", dpi=160); plt.close()
    for metric, ylabel, filename, title in [
        ("hit_ratio", "Hit ratio", "hit_ratio_vs_block_size.png", "Hit ratio vs block size"),
        ("measured_amat_cycles", "AMAT (cycles)", "amat_vs_block_size.png", "AMAT vs block size")]:
        plt.figure()
        for size in (512, 1024, 2048, 4096):
            subset = sorted((r for r in records if r["trace"] == "seq" and r["cache_bytes"] == size), key=lambda x: x["block_bytes"])
            if subset:
                plt.plot([r["block_bytes"] for r in subset], [r[metric] for r in subset], marker="o", label=f"{size} B cache")
        plt.xlabel("Block size (bytes)"); plt.ylabel(ylabel); plt.title(title + " (sequential trace)")
        plt.legend(); plt.tight_layout(); plt.savefig(out_dir / filename, dpi=160); plt.close()
    plt.figure()
    for block in (8, 16, 32, 64):
        subset = sorted((r for r in records if r["trace"] == "seq" and r["block_bytes"] == block), key=lambda x: x["cache_bytes"])
        if subset:
            plt.plot([r["cache_bytes"] for r in subset], [r["hit_ratio"] for r in subset], marker="o", label=f"{block} B block")
    plt.xlabel("Cache size (bytes)"); plt.ylabel("Hit ratio"); plt.title("Hit ratio vs cache size")
    plt.legend(); plt.tight_layout(); plt.savefig(out_dir / "hit_ratio_vs_cache_size.png", dpi=160); plt.close()

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--traces-dir", type=Path, default=DEFAULT_TRACES)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--cache", type=int, default=1024)
    parser.add_argument("--block", type=int, default=16)
    parser.add_argument("--latency", type=int, default=4)
    parser.add_argument("--no-sweep", action="store_true")
    parser.add_argument("--rtl-csv", type=Path)
    parser.add_argument("--trace", type=Path)
    args = parser.parse_args()
    validate_config(args.cache, args.block, args.latency)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    # Explicit RTL mode does not depend on --traces-dir containing other traces.
    if args.rtl_csv:
        if not args.trace:
            parser.error("--rtl-csv requires --trace")
        accesses = load_trace(args.trace)
        expected_rows, reference_summary = simulate(accesses, args.cache, args.block, args.latency)
        rtl_summary = validate_rtl_csv(args.rtl_csv, expected_rows)
        result = {"trace": args.trace.stem, "cache_bytes": args.cache, "block_bytes": args.block,
                  "mem_latency": args.latency, "result_source": "RTL simulation CSV",
                  **reference_summary, **rtl_summary,
                  "formula_amat_cycles": 1 + rtl_summary["miss_ratio"] * reference_summary["miss_penalty_cycles"],
                  "amat_difference_cycles": rtl_summary["measured_amat_cycles"] -
                    (1 + rtl_summary["miss_ratio"] * reference_summary["miss_penalty_cycles"])}
        atomic_write(args.out_dir / "rtl_summary.csv", csv_text([result]))
        print(f"Validated {len(accesses)} RTL rows against the reference model; summary written")
        return

    trace_files = sorted(args.traces_dir.glob("*.trace"))
    if not trace_files:
        raise SystemExit(f"No traces in {args.traces_dir}; generate them first")
    records, pending = [], {}
    for path in trace_files:
        if not re.fullmatch(r"[A-Za-z0-9_-]+", path.stem):
            raise ValueError(f"unsafe trace filename: {path.name}")
        accesses = load_trace(path)
        rows, summary = simulate(accesses, args.cache, args.block, args.latency)
        pending[f"{path.stem}_reference.csv"] = csv_text(rows)
        records.append({"trace": path.stem, "cache_bytes": args.cache, "block_bytes": args.block,
                        "mem_latency": args.latency, "result_source": "Python reference model", **summary})
    pending["summary.csv"] = csv_text(records)
    lines = ["# Hit/miss and AMAT analysis", "",
             f"Python reference model; cache {args.cache} B, block {args.block} B, MEM_LATENCY {args.latency}.", "",
             "| Trace | Accesses | Hit % | Miss % | Compulsory | Conflict | Capacity | Miss penalty | Measured AMAT | Formula AMAT |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for row in records:
        name = markdown_escape(row["trace"])
        lines.append(f"| {name} | {row['accesses']} | {100*row['hit_ratio']:.2f} | {100*row['miss_ratio']:.2f} | {row['compulsory_misses']} | {row['conflict_misses']} | {row['capacity_misses']} | {row['miss_penalty_cycles']} | {row['measured_amat_cycles']:.3f} | {row['formula_amat_cycles']:.3f} |")
    lines += ["", "## Interpretation", "",
              "Sequential and row-major traces expose spatial locality; the repeated loop exposes temporal locality. Uniform random traffic spans a much larger footprint. The stride trace ends by alternating between two blocks 1 KiB apart, which share one direct-mapped index but fit in the equal-capacity fully associative shadow.", "",
              "Compulsory misses are first references to blocks. A later direct-mapped miss that would hit in an equal-capacity fully associative LRU shadow is classified as conflict; a miss in both is classified as capacity. This is an analytical classification, not extra hardware.", "",
              "## AMAT", "",
              "AMAT = hit_time + miss_rate × miss_penalty. The repository FSM defines miss latency = words_per_block × (MEM_LATENCY + 1) + 2; miss penalty = miss latency − 1. For 16-byte blocks and MEM_LATENCY=4, miss latency is 22 cycles and miss penalty is 21 cycles.", "",
              "## Evidence boundary", "",
              "Default outputs are Python reference-model results, not RTL measurements. RTL mode validates every CSV row (index, operation, address, hit/miss, returned data and latency) against the supplied trace and reference model before reporting measured RTL metrics.", ""]
    pending["summary.md"] = "\n".join(lines)

    # Build the entire result set in a unique staging directory. Publish only
    # after every trace, sweep table and optional plot has been generated.
    with tempfile.TemporaryDirectory(prefix=".m5-analysis-stage-", dir=args.out_dir) as stage_name:
        stage = Path(stage_name)
        for filename, content in pending.items():
            atomic_write(stage / filename, content)
        if not args.no_sweep:
            sweep = []
            for cache_size in (512, 1024, 2048, 4096):
                for block_size in (8, 16, 32, 64):
                    if block_size > cache_size:
                        continue
                    for path in trace_files:
                        _, summary = simulate(load_trace(path), cache_size, block_size, args.latency)
                        sweep.append({"trace": path.stem, "cache_bytes": cache_size,
                                      "block_bytes": block_size, "mem_latency": args.latency, **summary})
            atomic_write(stage / "parameter_sweep.csv", csv_text(sweep))
            make_plots(sweep, stage)
        # Serialize publishers and preflight every destination before changing any.
        import fcntl
        lock_path = args.out_dir / ".m5-analysis.lock"
        with lock_path.open("w", encoding="utf-8") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            staged_names = {p.name for p in stage.iterdir()}
            stale_names = {p.name for p in args.out_dir.glob("*_reference.csv")
                           if p.name not in staged_names}
            if args.no_sweep:
                stale_names |= {"parameter_sweep.csv", "hit_ratio_by_trace.png",
                                "hit_ratio_vs_block_size.png", "amat_vs_block_size.png",
                                "hit_ratio_vs_cache_size.png"}
            destinations = [args.out_dir / name for name in staged_names | stale_names]
            for destination in destinations:
                if destination.is_symlink():
                    raise ValueError(f"refusing to modify symlink: {destination}")
            backups = {}
            changed = []
            try:
                for destination in destinations:
                    if destination.exists() and destination.is_file():
                        fd, backup_name = tempfile.mkstemp(prefix=".m5-backup-", dir=args.out_dir)
                        os.close(fd)
                        os.replace(destination, backup_name)
                        backups[destination] = Path(backup_name)
                for staged_file in stage.iterdir():
                    destination = args.out_dir / staged_file.name
                    os.replace(staged_file, destination)
                    changed.append(destination)
            except Exception:
                for destination in changed:
                    if destination.exists():
                        destination.unlink()
                for destination, backup in backups.items():
                    if backup.exists():
                        os.replace(backup, destination)
                raise
            else:
                for backup in backups.values():
                    backup.unlink(missing_ok=True)
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
    print(f"Analysed {len(trace_files)} traces; results: {args.out_dir}")

if __name__ == "__main__":
    main()
