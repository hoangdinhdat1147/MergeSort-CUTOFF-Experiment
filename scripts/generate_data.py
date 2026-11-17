#!/usr/bin/env python3
"""Tao bo du lieu co seed co dinh de thi nghiem co the lap lai."""
from pathlib import Path
import random

OUT = Path("datasets")
SIZES = [10_000, 50_000, 100_000, 250_000]
SEED = 20261117

def nearly_sorted(values, rng):
    a = values[:]
    # Hoan doi 1% so cap vi tri (toi thieu 1 cap).
    swaps = max(1, len(a) // 100)
    for _ in range(swaps):
        i, j = rng.randrange(len(a)), rng.randrange(len(a))
        a[i], a[j] = a[j], a[i]
    return a

def write_data(name, values):
    path = OUT / f"{name}.txt"
    with path.open("w", encoding="utf-8") as f:
        f.write(" ".join(map(str, values)))
    print(f"{path}: {len(values):,} integers")

def main():
    OUT.mkdir(exist_ok=True)
    for n in SIZES:
        rng = random.Random(SEED + n)
        random_data = [rng.randrange(-10*n, 10*n + 1) for _ in range(n)]
        write_data(f"random_{n}", random_data)
        write_data(f"sorted_{n}", sorted(random_data))
        write_data(f"reverse_{n}", sorted(random_data, reverse=True))
        write_data(f"nearly_sorted_{n}", nearly_sorted(sorted(random_data), rng))

if __name__ == "__main__":
    main()
