#!/usr/bin/env python3
"""Tao 6 bieu do GIF tu cac bang CSV cua thi nghiem MergeSort CUTOFF.

Chay tu thu muc goc du an:
    python scripts/make_animated_charts.py

Dau vao:
    analysis/summary.csv
    analysis/cutoff_7_10_comparison.csv
    analysis/best_cutoff_from_run.csv (hoac analysis/best_cutoff.csv)

Dau ra:
    analysis/animated/*.gif
"""
from __future__ import annotations

import csv
import sys
from io import BytesIO
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = ROOT / "analysis"
OUTPUT_DIR = ANALYSIS_DIR / "animated"
CUTOFF_ORDER = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 16, 20, 24, 32, 40, 48, 64]
DISTRIBUTIONS = [
    ("random", "Dữ liệu ngẫu nhiên"),
    ("sorted", "Dữ liệu tăng dần"),
    ("reverse", "Dữ liệu giảm dần"),
    ("nearly_sorted", "Dữ liệu gần tăng dần"),
]
BLUE = "#276FBF"
ORANGE = "#E07A32"
GREEN = "#2A9D8F"
RED = "#C94C4C"
DARK = "#243247"
GRID = "#D9E0E8"
FIG_SIZE = (9.6, 5.5)
DPI = 95


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy tệp: {path.relative_to(ROOT)}")
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def dataset_info(dataset: str) -> tuple[str, int]:
    stem = Path(dataset).stem
    for prefix, _ in DISTRIBUTIONS:
        if stem.startswith(prefix + "_"):
            return prefix, int(stem[len(prefix) + 1:])
    raise ValueError(f"Không xác định được dạng dữ liệu: {dataset}")


def short_dataset_name(dataset: str) -> str:
    prefix, size = dataset_info(dataset)
    return f"{prefix.replace('_', ' ')} · {size:,}".replace(",", ".")


def sorted_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    order = {name: i for i, (name, _) in enumerate(DISTRIBUTIONS)}
    return sorted(rows, key=lambda r: (order[dataset_info(r["dataset"])[0]], dataset_info(r["dataset"])[1]))


def render_image(fig: plt.Figure) -> Image.Image:
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=DPI, facecolor="white")
    plt.close(fig)
    buffer.seek(0)
    return Image.open(buffer).convert("RGB")


def get_plot_bounds(ax: plt.Axes, image_size: tuple[int, int]) -> tuple[int, int, int, int]:
    width, height = image_size
    fig = ax.figure
    fig.canvas.draw()
    bbox = ax.get_window_extent()
    scale_x = width / (fig.get_figwidth() * fig.dpi)
    scale_y = height / (fig.get_figheight() * fig.dpi)
    canvas_height = fig.get_figheight() * fig.dpi
    x0 = max(0, int(round(bbox.x0 * scale_x)))
    x1 = min(width - 1, int(round(bbox.x1 * scale_x)))
    y0 = max(0, int(round((canvas_height - bbox.y1) * scale_y)))
    y1 = min(height - 1, int(round((canvas_height - bbox.y0) * scale_y)))
    return x0, y0, x1, y1


def save_gif(frames: list[Image.Image], path: Path, duration: int = 125) -> None:
    if not frames:
        raise ValueError(f"Không có khung hình để ghi: {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    # Tối ưu bảng màu và kích thước để GIF tải nhanh khi mở README.
    palette_frames = [frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=160) for frame in frames]
    palette_frames[0].save(
        path,
        save_all=True,
        append_images=palette_frames[1:],
        duration=duration,
        loop=0,
        optimize=True,
        disposal=2,
    )
    size_kb = path.stat().st_size / 1024
    print(f"Đã tạo {path.relative_to(ROOT)} ({size_kb:.0f} KB)")


def draw_dataset_scene(scene: dict[str, Any], title: str) -> list[Image.Image]:
    cutoffs = scene["cutoffs"]
    medians = scene["medians"]
    stdevs = scene["stdevs"]
    best_i = scene["best_index"]

    def make_chart(show_data: bool) -> tuple[Image.Image, tuple[int, int, int, int], list[int]]:
        fig, ax = plt.subplots(figsize=FIG_SIZE)
        fig.subplots_adjust(left=0.105, right=0.97, bottom=0.22, top=0.82)
        ax.set_facecolor("#FBFCFE")
        ax.grid(True, axis="y", color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.set_xlim(min(CUTOFF_ORDER) - 1, max(CUTOFF_ORDER) + 2)
        ymax = max(m + s for m, s in zip(medians, stdevs))
        ax.set_ylim(0, ymax * 1.22 if ymax > 0 else 1)
        ax.set_xticks(CUTOFF_ORDER)
        ax.tick_params(axis="x", labelrotation=35, labelsize=8.5)
        ax.tick_params(axis="y", labelsize=9)
        ax.set_xlabel("Giá trị CUTOFF", fontsize=10.5, color=DARK, labelpad=8)
        ax.set_ylabel("Median thời gian chạy (ms)", fontsize=10.5, color=DARK, labelpad=8)
        ax.set_title(f"{title}  |  N = {scene['n']:,}".replace(",", "."),
                     fontsize=14, fontweight="bold", color=DARK, pad=17)
        ax.text(0.01, 1.015, "Mỗi CUTOFF được đo 11 lần · thanh sai số: ±1 độ lệch chuẩn",
                transform=ax.transAxes, fontsize=8.5, color="#58677B", va="bottom")
        if show_data:
            ax.errorbar(cutoffs, medians, yerr=stdevs, color=BLUE, marker="o",
                        markersize=4.8, linewidth=2.1, elinewidth=0.9, capsize=2.8,
                        markerfacecolor="white", markeredgewidth=1.6)
            bx, by = cutoffs[best_i], medians[best_i]
            ax.scatter([bx], [by], marker="*", s=210, color=ORANGE,
                       edgecolor="white", linewidth=0.8, zorder=5)
            ax.annotate(
                f"Median thấp nhất trong nhóm đã thử: CUTOFF {bx} · {by:.4f} ms",
                xy=(bx, by), xytext=(0.98, 0.93), textcoords="axes fraction",
                ha="right", va="top", fontsize=8.3, color=DARK,
                bbox={"boxstyle": "round,pad=0.4", "facecolor": "#FFF4E8", "edgecolor": "#E8B77E"},
            )
        fig.canvas.draw()
        image_size = (int(round(fig.get_figwidth() * DPI)), int(round(fig.get_figheight() * DPI)))
        bounds = get_plot_bounds(ax, image_size)
        scale_x = image_size[0] / (fig.get_figwidth() * fig.dpi)
        x_pixels = [int(round(ax.transData.transform((c, 0))[0] * scale_x)) for c in cutoffs]
        image = render_image(fig)
        return image, bounds, x_pixels

    base, bounds, x_pixels = make_chart(False)
    full, _, _ = make_chart(True)
    x0, y0, x1, y1 = bounds
    frames: list[Image.Image] = []
    for current_x in x_pixels:
        mask = Image.new("L", base.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rectangle((x0, y0, min(x1, current_x), y1), fill=255)
        frames.append(Image.composite(full, base, mask))
    # Giữ biểu đồ cuối đủ lâu để người xem đọc được kết quả.
    frames.extend([full.copy() for _ in range(7)])
    return frames


def make_cutoff_curve_gif(summary_rows: list[dict[str, str]], prefix: str, title: str) -> None:
    relevant = [r for r in summary_rows if dataset_info(r["dataset"])[0] == prefix]
    if not relevant:
        raise ValueError(f"Không có dữ liệu trong summary.csv cho nhóm {prefix}")
    scenes: list[dict[str, Any]] = []
    for dataset in sorted({r["dataset"] for r in relevant}, key=lambda d: dataset_info(d)[1]):
        group = sorted([r for r in relevant if r["dataset"] == dataset], key=lambda r: int(r["cutoff"]))
        cutoffs = [int(r["cutoff"]) for r in group]
        medians = [float(r["median_ms"]) for r in group]
        stdevs = [float(r.get("stdev_ms", 0) or 0) for r in group]
        if cutoffs != CUTOFF_ORDER:
            raise ValueError(f"{dataset}: danh sách CUTOFF trong summary.csv không đúng hoặc chưa đủ 18 giá trị")
        best_index = min(range(len(medians)), key=medians.__getitem__)
        scenes.append({"dataset": dataset, "n": int(group[0]["n"]), "cutoffs": cutoffs,
                       "medians": medians, "stdevs": stdevs, "best_index": best_index})

    frames: list[Image.Image] = []
    for scene in scenes:
        frames.extend(draw_dataset_scene(scene, title))
    save_gif(frames, OUTPUT_DIR / f"cutoff_{prefix}_by_size.gif", duration=125)


def make_aggregate_chart(rows: list[dict[str, str]], kind: str) -> list[Image.Image]:
    rows = sorted_rows(rows)
    labels = [short_dataset_name(r["dataset"]) for r in rows]
    count = len(rows)
    fig, ax = plt.subplots(figsize=(10.2, 6.9))
    fig.subplots_adjust(left=0.20, right=0.96, bottom=0.13, top=0.84)
    ax.set_facecolor("#FBFCFE")
    ax.grid(True, axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    positions = list(range(count))
    ax.set_yticks(positions)
    ax.set_yticklabels(labels, fontsize=8.5)
    ax.invert_yaxis()
    bounds = get_plot_bounds(ax, (int(round(fig.get_figwidth() * DPI)), int(round(fig.get_figheight() * DPI))))

    if kind == "comparison":
        values = [float(r["difference_percent_T10_vs_T7"]) for r in rows]
        colors = [GREEN if v < 0 else ORANGE for v in values]
        ax.set_xlim(-21, 6)
        ax.axvline(0, color=DARK, linewidth=1.1)
        ax.set_xlabel("Chênh lệch median của CUTOFF 10 so với CUTOFF 7 (%)", fontsize=10)
        ax.set_title("So sánh CUTOFF = 7 và CUTOFF = 10 trên 16 bộ dữ liệu",
                     fontsize=13.5, fontweight="bold", color=DARK, pad=15)
        ax.legend(handles=[
            Patch(facecolor=GREEN, label="Giá trị âm: CUTOFF 10 có median thấp hơn"),
            Patch(facecolor=ORANGE, label="Giá trị dương: CUTOFF 7 có median thấp hơn"),
        ], loc="lower right", fontsize=8, frameon=True)
    else:
        cutoff_key = next((k for k in ("best_cutoff_among_tested", "cutoff", "best_cutoff") if k in rows[0]), None)
        median_key = next((k for k in ("median_ms", "best_median_ms") if k in rows[0]), None)
        if not cutoff_key or not median_key:
            raise ValueError("Không nhận diện được cột CUTOFF hoặc median trong bảng best_cutoff")
        values = [int(float(r[cutoff_key])) for r in rows]
        colors = [ORANGE if v == 64 else BLUE for v in values]
        ax.set_xlim(0, 82)
        ax.set_xticks(CUTOFF_ORDER)
        ax.set_xlabel("CUTOFF có median thấp nhất trong các giá trị đã thử", fontsize=10)
        ax.set_title("CUTOFF có median thấp nhất theo từng bộ dữ liệu",
                     fontsize=13.5, fontweight="bold", color=DARK, pad=15)
        ax.axvline(64, color=RED, linestyle="--", linewidth=1.1)
        ax.text(64, -0.8, "64: giới hạn trên đã thử", color=RED, fontsize=8, ha="center", va="bottom")

    image_with = None
    bars = None
    base = None
    for show in (False, True):
        if kind == "comparison":
            if show:
                bars = ax.barh(positions, values, color=colors, height=0.66, edgecolor="white")
                for i, value in enumerate(values):
                    ax.text(value + (0.35 if value >= 0 else -0.35), i, f"{value:+.2f}%",
                            va="center", ha="left" if value >= 0 else "right", fontsize=7.6, color=DARK)
            else:
                # Axes/trục giữ nguyên, chỉ bỏ các thanh dữ liệu.
                pass
        else:
            if show:
                bars = ax.barh(positions, values, color=colors, height=0.66, edgecolor="white")
                for i, row in enumerate(rows):
                    median_key = next(k for k in ("median_ms", "best_median_ms") if k in row)
                    ax.text(values[i] + 1, i, f"{values[i]} · {float(row[median_key]):.4f} ms",
                            va="center", fontsize=7.5, color=DARK)
        buffer = BytesIO()
        fig.savefig(buffer, format="png", dpi=DPI, facecolor="white")
        buffer.seek(0)
        img = Image.open(buffer).convert("RGB")
        if show:
            image_with = img
        else:
            base = img
        if bars is not None:
            for bar in bars:
                bar.remove()
            bars = None
        # Xóa các nhãn số liệu ở bản đầy đủ trước khi render nền.
        if show:
            for artist in list(ax.texts):
                if artist.get_text().strip().endswith("%") or " ms" in artist.get_text():
                    artist.remove()
    plt.close(fig)
    assert base is not None and image_with is not None

    # Khôi phục lại hình đầy đủ để tạo mask theo từng hàng.
    frames: list[Image.Image] = []
    x0, y0, x1, y1 = bounds
    row_h = (y1 - y0) / count
    for visible in range(1, count + 1):
        mask = Image.new("L", base.size, 0)
        draw = ImageDraw.Draw(mask)
        for idx in range(visible):
            # Thứ tự hàng đảo ngược trên màn hình do invert_yaxis.
            row_center = y0 + (idx + 0.5) * row_h
            draw.rectangle((x0, int(row_center - row_h / 2), x1, int(row_center + row_h / 2)), fill=255)
        frames.append(Image.composite(image_with, base, mask))
    frames.extend([image_with.copy() for _ in range(7)])
    return frames


def make_comparison_gif(rows: list[dict[str, str]]) -> None:
    frames = make_aggregate_chart(rows, "comparison")
    save_gif(frames, OUTPUT_DIR / "comparison_cutoff_7_10.gif", duration=150)


def make_best_cutoff_gif(rows: list[dict[str, str]]) -> None:
    frames = make_aggregate_chart(rows, "best")
    save_gif(frames, OUTPUT_DIR / "best_cutoff_by_dataset.gif", duration=150)


def main() -> int:
    try:
        summary = read_csv(ANALYSIS_DIR / "summary.csv")
        comparison = read_csv(ANALYSIS_DIR / "cutoff_7_10_comparison.csv")
        best_path = ANALYSIS_DIR / "best_cutoff_from_run.csv"
        if not best_path.exists():
            best_path = ANALYSIS_DIR / "best_cutoff.csv"
        best = read_csv(best_path)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        make_comparison_gif(comparison)
        make_best_cutoff_gif(best)
        for prefix, title in DISTRIBUTIONS:
            make_cutoff_curve_gif(summary, prefix, title)
        print("\nĐã tạo xong 6 biểu đồ GIF trong analysis/animated/.")
        return 0
    except Exception as exc:
        print(f"Lỗi khi tạo biểu đồ động: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
