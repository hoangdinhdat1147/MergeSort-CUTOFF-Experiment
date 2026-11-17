#!/usr/bin/env python3
"""Tong hop median, do lech chuan, speedup va bieu do tu results.csv."""
from pathlib import Path
import csv, statistics
from collections import defaultdict
import matplotlib.pyplot as plt

INPUT = Path("results.csv")
OUT = Path("analysis")
OUT.mkdir(exist_ok=True)

groups = defaultdict(list)
with INPUT.open(encoding="utf-8", newline="") as f:
    for row in csv.DictReader(f):
        if row["correct"].lower() != "true":
            raise SystemExit("Phat hien lan chay co ket qua sai.")
        key = (row["dataset"], int(row["n"]), int(row["cutoff"]))
        groups[key].append(float(row["elapsed_ms"]))

rows = []
for (dataset, n, cutoff), vals in sorted(groups.items()):
    rows.append({
        "dataset": dataset, "n": n, "cutoff": cutoff,
        "runs": len(vals), "median_ms": statistics.median(vals),
        "mean_ms": statistics.mean(vals),
        "stdev_ms": statistics.stdev(vals) if len(vals) > 1 else 0.0,
        "min_ms": min(vals), "max_ms": max(vals)
    })

with (OUT/"summary.csv").open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

# Chon cutoff tot nhat rieng cho tung bo du lieu theo median.
best = {}
for r in rows:
    key = r["dataset"]
    if key not in best or r["median_ms"] < best[key]["median_ms"]:
        best[key] = r

with (OUT/"best_cutoff.csv").open("w", encoding="utf-8", newline="") as f:
    fields = ["dataset", "n", "cutoff", "median_ms"]
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for key in sorted(best):
        w.writerow({k: best[key][k] for k in fields})

# Ve tung do thi theo kich thuoc va kieu du lieu.
for dataset in sorted({r["dataset"] for r in rows}):
    subset = [r for r in rows if r["dataset"] == dataset]
    subset.sort(key=lambda x: x["cutoff"])
    plt.figure(figsize=(8, 5))
    plt.plot([r["cutoff"] for r in subset],
             [r["median_ms"] for r in subset], marker="o")
    plt.xlabel("CUTOFF")
    plt.ylabel("Median running time (ms)")
    plt.title(f"CUTOFF experiment: {dataset}")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUT/f"{dataset}.png", dpi=160)
    plt.close()

print("Da tao analysis/summary.csv, analysis/best_cutoff.csv va cac bieu do PNG.")
print("\\nCUTOFF tot nhat theo tung bo du lieu (median):")
for key in sorted(best):
    b = best[key]
    print(f"{key:28s} cutoff={b['cutoff']:2d} median={b['median_ms']:.4f} ms")
