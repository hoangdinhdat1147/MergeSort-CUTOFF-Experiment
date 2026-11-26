#!/usr/bin/env python3
"""Tổng hợp results.csv thành bảng thống kê và biểu đồ.

Cách dùng (từ bất kỳ thư mục nào):
    python scripts/analyze_results.py                 # đọc results.csv, ghi vào analysis/
    python scripts/analyze_results.py --sync-docs     # đồng thời cập nhật docs/data/ cho dashboard
    python scripts/analyze_results.py --no-plots      # chỉ tạo CSV (không cần matplotlib)
    python scripts/analyze_results.py --input X.csv --out DIR

Đầu ra trong thư mục --out:
    summary.csv                 median, mean, độ lệch chuẩn, min, max theo (bộ dữ liệu, CUTOFF)
    best_cutoff.csv             CUTOFF có median thấp nhất của từng bộ dữ liệu
    best_cutoff_from_run.csv    cùng nội dung, định dạng cột dùng cho dashboard/báo cáo
    cutoff_7_10_comparison.csv  so sánh CUTOFF 7 và CUTOFF 10 trên từng bộ dữ liệu
    <bo_du_lieu>.txt.png        biểu đồ median theo CUTOFF cho từng bộ dữ liệu (trừ khi --no-plots)

Mọi bảng đều được tính lại hoàn toàn từ results.csv nên có thể kiểm chứng và tái lập.
"""
from __future__ import annotations

import argparse
import csv
import shutil
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_FILES = ("summary.csv", "cutoff_7_10_comparison.csv", "best_cutoff_from_run.csv")
LOW, HIGH = 7, 10  # hai giá trị CUTOFF được so sánh riêng


def trim(value: float, digits: int) -> str:
    """Làm tròn rồi bỏ số 0 thừa: 0.1230 -> '0.123', 2.00 -> '2'."""
    text = f"{round(value, digits):.{digits}f}"
    return text.rstrip("0").rstrip(".") if "." in text else text


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    # lineterminator cố định để tệp giống nhau trên mọi hệ điều hành.
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_results(path: Path) -> dict[tuple[str, int, int], list[float]]:
    if not path.exists():
        raise SystemExit(f"Không tìm thấy {path}. Hãy chạy benchmark trước (xem README, mục 4).")
    groups: dict[tuple[str, int, int], list[float]] = defaultdict(list)
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"dataset", "n", "cutoff", "elapsed_ms", "correct"}
        if not reader.fieldnames or not required <= set(reader.fieldnames):
            raise SystemExit(f"{path} thiếu cột bắt buộc: {sorted(required)}")
        for line_no, row in enumerate(reader, start=2):
            if row["correct"].strip().lower() != "true":
                raise SystemExit(f"{path}, dòng {line_no}: phát hiện lần chạy có kết quả sai.")
            groups[(row["dataset"], int(row["n"]), int(row["cutoff"]))].append(float(row["elapsed_ms"]))
    if not groups:
        raise SystemExit(f"{path} không có dòng dữ liệu nào.")
    return groups


def summarize(groups) -> list[dict]:
    rows = []
    for (dataset, n, cutoff), vals in sorted(groups.items()):
        rows.append({
            "dataset": dataset, "n": n, "cutoff": cutoff,
            "runs": len(vals), "median_ms": statistics.median(vals),
            "mean_ms": statistics.mean(vals),
            "stdev_ms": statistics.stdev(vals) if len(vals) > 1 else 0.0,
            "min_ms": min(vals), "max_ms": max(vals),
        })
    return rows


def best_per_dataset(rows: list[dict]) -> dict[str, dict]:
    """CUTOFF có median thấp nhất trong các giá trị đã thử (khi hòa, lấy CUTOFF nhỏ hơn)."""
    best: dict[str, dict] = {}
    for r in rows:
        if r["dataset"] not in best or r["median_ms"] < best[r["dataset"]]["median_ms"]:
            best[r["dataset"]] = r
    return best


def compare_7_10(rows: list[dict]) -> list[dict]:
    by_key = {(r["dataset"], r["cutoff"]): r for r in rows}
    out = []
    for dataset in sorted({r["dataset"] for r in rows}):
        low, high = by_key.get((dataset, LOW)), by_key.get((dataset, HIGH))
        if low is None or high is None:
            raise SystemExit(f"{dataset}: thiếu dữ liệu cho CUTOFF {LOW} hoặc {HIGH}.")
        m_low, m_high = low["median_ms"], high["median_ms"]
        if m_high < m_low:
            lower = f"CUTOFF {HIGH}"
        elif m_low < m_high:
            lower = f"CUTOFF {LOW}"
        else:
            lower = "Bằng nhau"
        out.append({
            "dataset": dataset, "n": low["n"],
            "median_cutoff_7_ms": trim(m_low, 4),
            "median_cutoff_10_ms": trim(m_high, 4),
            "difference_percent_T10_vs_T7": trim((m_high - m_low) / m_low * 100, 2),
            "stdev_cutoff_7_ms": trim(low["stdev_ms"], 4),
            "stdev_cutoff_10_ms": trim(high["stdev_ms"], 4),
            "lower_median": lower,
        })
    return out


def plot_datasets(rows: list[dict], out_dir: Path) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")  # không cần màn hình, chạy được trên CI
        import matplotlib.pyplot as plt
    except ImportError:
        raise SystemExit("Thiếu matplotlib. Cài bằng: python -m pip install -r requirements.txt "
                         "(hoặc dùng --no-plots để bỏ qua biểu đồ).")
    for dataset in sorted({r["dataset"] for r in rows}):
        subset = sorted((r for r in rows if r["dataset"] == dataset), key=lambda x: x["cutoff"])
        plt.figure(figsize=(8, 5))
        plt.plot([r["cutoff"] for r in subset], [r["median_ms"] for r in subset], marker="o")
        plt.xlabel("CUTOFF")
        plt.ylabel("Median running time (ms)")
        plt.title(f"CUTOFF experiment: {dataset}")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(out_dir / f"{dataset}.png", dpi=160)
        plt.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", type=Path, default=ROOT / "results.csv", help="tệp kết quả thô (mặc định: results.csv)")
    parser.add_argument("--out", type=Path, default=ROOT / "analysis", help="thư mục đầu ra (mặc định: analysis/)")
    parser.add_argument("--no-plots", action="store_true", help="chỉ tạo CSV, không vẽ biểu đồ PNG")
    parser.add_argument("--sync-docs", action="store_true",
                        help="sao chép 3 CSV của dashboard sang docs/data/ (dùng cho GitHub Pages)")
    args = parser.parse_args()

    groups = load_results(args.input)
    rows = summarize(groups)
    best = best_per_dataset(rows)
    comparison = compare_7_10(rows)

    args.out.mkdir(parents=True, exist_ok=True)
    write_csv(args.out / "summary.csv", list(rows[0].keys()), rows)

    best_rows = [best[k] for k in sorted(best)]
    write_csv(args.out / "best_cutoff.csv", ["dataset", "n", "cutoff", "median_ms"],
              [{k: r[k] for k in ("dataset", "n", "cutoff", "median_ms")} for r in best_rows])
    write_csv(args.out / "best_cutoff_from_run.csv",
              ["dataset", "n", "best_cutoff_among_tested", "median_ms"],
              [{"dataset": r["dataset"], "n": r["n"], "best_cutoff_among_tested": r["cutoff"],
                "median_ms": r["median_ms"]} for r in best_rows])
    write_csv(args.out / "cutoff_7_10_comparison.csv", list(comparison[0].keys()), comparison)

    if not args.no_plots:
        plot_datasets(rows, args.out)

    if args.sync_docs:
        target = ROOT / "docs" / "data"
        target.mkdir(parents=True, exist_ok=True)
        for name in DASHBOARD_FILES:
            shutil.copyfile(args.out / name, target / name)
        print(f"Đã đồng bộ {len(DASHBOARD_FILES)} tệp CSV sang {target}")

    print(f"Đã tạo các bảng thống kê trong {args.out}" + ("" if args.no_plots else " (kèm biểu đồ PNG)"))
    print("\nCUTOFF tốt nhất theo từng bộ dữ liệu (median):")
    for key in sorted(best):
        b = best[key]
        print(f"  {key:28s} cutoff={b['cutoff']:2d}  median={b['median_ms']:.4f} ms")

    wins_high = sum(1 for c in comparison if c["lower_median"] == f"CUTOFF {HIGH}")
    wins_low = sum(1 for c in comparison if c["lower_median"] == f"CUTOFF {LOW}")
    print(f"\nCUTOFF {HIGH} có median thấp hơn: {wins_high}/{len(comparison)} bộ; "
          f"CUTOFF {LOW}: {wins_low}/{len(comparison)} bộ.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
