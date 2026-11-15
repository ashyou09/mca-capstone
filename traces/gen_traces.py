#!/usr/bin/env python3
"""Generate deterministic, read-only memory traces for the MCA cache study."""
from __future__ import annotations
import argparse
import os
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1] / "traces"
MEM_BYTES = 256 * 1024
WORD_BYTES = 4
MATRIX_N = 64

class Mulberry32:
    def __init__(self, seed: int):
        self.state = seed & 0xFFFFFFFF

    @staticmethod
    def imul(a: int, b: int) -> int:
        return (a * b) & 0xFFFFFFFF

    def random(self) -> float:
        self.state = (self.state + 0x6D2B79F5) & 0xFFFFFFFF
        t = self.state
        t = self.imul(t ^ (t >> 15), t | 1)
        t = (t ^ ((t + self.imul(t ^ (t >> 7), t | 61)) & 0xFFFFFFFF)) & 0xFFFFFFFF
        t = (t ^ (t >> 14)) & 0xFFFFFFFF
        return t / 4294967296

def word_addr(index: int) -> int:
    return (index % (MEM_BYTES // WORD_BYTES)) * WORD_BYTES

def generate(count: int, seed: int) -> dict[str, list[int]]:
    rng = Mulberry32(seed)
    seq = [word_addr(i) for i in range(count)]
    random_trace = [word_addr(int(rng.random() * (MEM_BYTES // WORD_BYTES))) for _ in range(count)]

    # 128 words = 512 bytes, fitting in the 1 KiB baseline cache.
    working_set = list(range(128))
    for i in range(len(working_set) - 1, 0, -1):
        j = int(rng.random() * (i + 1))
        working_set[i], working_set[j] = working_set[j], working_set[i]
    loop = [word_addr(working_set[i % len(working_set)]) for i in range(count)]

    # The final phase ping-pongs between two blocks 1 KiB apart. They share an
    # index but fit in the equal-capacity fully associative shadow cache.
    phase = max(1, count // 3)
    stride_trace = []
    for i in range(count):
        p = min(2, i // phase)
        if p == 0:
            addr = i * 16
        elif p == 1:
            addr = (i - phase) * 64
        else:
            addr = 0x30000 + ((i - 2 * phase) % 2) * 1024
        stride_trace.append(word_addr(addr // WORD_BYTES))

    # Both matrix traces visit the same complete set; only traversal order differs.
    row_order = [r * MATRIX_N + c for r in range(MATRIX_N) for c in range(MATRIX_N)]
    col_order = [r * MATRIX_N + c for c in range(MATRIX_N) for r in range(MATRIX_N)]
    matrix_row = [word_addr(row_order[i % len(row_order)]) for i in range(count)]
    matrix_col = [word_addr(col_order[i % len(col_order)]) for i in range(count)]

    hot = [word_addr(i) for i in range(96)]
    mixed = []
    for _ in range(count):
        if rng.random() < 0.85:
            mixed.append(hot[int(rng.random() * len(hot))])
        else:
            mixed.append(word_addr(int(rng.random() * (MEM_BYTES // WORD_BYTES))))
    return {"seq": seq, "random": random_trace, "loop": loop, "stride": stride_trace,
            "matrix_row": matrix_row, "matrix_col": matrix_col, "mixed": mixed}

def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise ValueError(f"refusing to overwrite symlink: {path}")
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="ascii", newline="") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=4096)
    parser.add_argument("--seed", type=int, default=20261116)
    args = parser.parse_args()
    if not 4096 <= args.count <= 10000:
        parser.error("--count must be between 4096 and 10000 so matrix traversals compare the same complete 64x64 element set")
    generated = generate(args.count, args.seed)
    staged = {name: "".join(f"0 {addr:08x}\n" for addr in addresses)
              for name, addresses in generated.items()}
    # Materialise the complete set before publishing any destination file.
    import fcntl
    with tempfile.TemporaryDirectory(prefix=".trace-stage-", dir=ROOT) as stage_name:
        stage = Path(stage_name)
        for name, content in staged.items():
            atomic_write(stage / f"{name}.trace", content)
        lock_path = Path(tempfile.gettempdir()) / "mca-capstone-cache-trace.lock"
        with lock_path.open("w", encoding="utf-8") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            destinations = {name: ROOT / f"{name}.trace" for name in staged}
            # Preflight the entire bundle before replacing any member.
            for destination in destinations.values():
                if destination.is_symlink():
                    raise ValueError(f"refusing to overwrite symlink: {destination}")
            backups = {}
            published = []
            try:
                for name, destination in destinations.items():
                    if destination.exists():
                        fd, backup_name = tempfile.mkstemp(prefix=".trace-backup-", dir=ROOT)
                        os.close(fd)
                        os.replace(destination, backup_name)
                        backups[name] = Path(backup_name)
                for name, destination in destinations.items():
                    os.replace(stage / f"{name}.trace", destination)
                    published.append(destination)
            except Exception:
                for destination in published:
                    destination.unlink(missing_ok=True)
                for name, backup in backups.items():
                    os.replace(backup, destinations[name])
                raise
            else:
                for backup in backups.values():
                    backup.unlink(missing_ok=True)
            finally:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
            for name in staged:
                print(f"{name}.trace: {len(generated[name])} read accesses")

if __name__ == "__main__":
    main()
