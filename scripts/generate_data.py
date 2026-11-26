#!/usr/bin/env python3
"""Sinh các bộ dữ liệu có seed cố định để thí nghiệm có thể lặp lại.

Cách dùng (từ bất kỳ thư mục nào):
    python scripts/generate_data.py                  # sinh lại datasets/
    python scripts/generate_data.py --verify         # kiểm tra datasets/ khớp datasets/SHA256SUMS
    python scripts/generate_data.py --write-checksums  # ghi lại datasets/SHA256SUMS

Sinh 4 kích thước x 4 dạng = 16 tệp .txt (các số nguyên cách nhau bởi dấu cách).
Tệp được ghi đúng từng byte như phiên bản đã dùng cho results.csv.
"""
from __future__ import annotations

import argparse
import hashlib
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "datasets"
CHECKSUM_FILE = "SHA256SUMS"
SIZES = [10_000, 50_000, 100_000, 250_000]
SEED = 20261117


def nearly_sorted(values, rng):
    """Hoán đổi ngẫu nhiên khoảng 1% số cặp vị trí (tối thiểu 1 cặp)."""
    a = values[:]
    swaps = max(1, len(a) // 100)
    for _ in range(swaps):
        i, j = rng.randrange(len(a)), rng.randrange(len(a))
        a[i], a[j] = a[j], a[i]
    return a


def write_data(out_dir: Path, name: str, values) -> None:
    path = out_dir / f"{name}.txt"
    with path.open("w", encoding="utf-8") as f:
        f.write(" ".join(map(str, values)))
    print(f"{path}: {len(values):,} integers")


def generate(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for n in SIZES:
        # Mỗi kích thước có bộ sinh riêng: seed cơ sở + n.
        rng = random.Random(SEED + n)
        random_data = [rng.randrange(-10 * n, 10 * n + 1) for _ in range(n)]
        write_data(out_dir, f"random_{n}", random_data)
        write_data(out_dir, f"sorted_{n}", sorted(random_data))
        write_data(out_dir, f"reverse_{n}", sorted(random_data, reverse=True))
        write_data(out_dir, f"nearly_sorted_{n}", nearly_sorted(sorted(random_data), rng))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_checksums(out_dir: Path) -> None:
    files = sorted(out_dir.glob("*.txt"))
    if not files:
        raise SystemExit(f"Không có tệp .txt nào trong {out_dir}")
    lines = [f"{sha256(p)}  {p.name}\n" for p in files]
    # Định dạng giống `sha256sum`, nên cũng kiểm tra được bằng: cd datasets && sha256sum -c SHA256SUMS
    (out_dir / CHECKSUM_FILE).write_text("".join(lines), encoding="utf-8", newline="\n")
    print(f"Đã ghi {out_dir / CHECKSUM_FILE} ({len(lines)} tệp)")


def verify(out_dir: Path) -> int:
    checksum_path = out_dir / CHECKSUM_FILE
    if not checksum_path.exists():
        print(f"Không tìm thấy {checksum_path}", file=sys.stderr)
        return 1
    expected: dict[str, str] = {}
    for line in checksum_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            digest, name = line.split(None, 1)
            expected[name.strip().lstrip("*")] = digest
    problems = 0
    for name, digest in sorted(expected.items()):
        path = out_dir / name
        if not path.exists():
            print(f"THIẾU : {name}", file=sys.stderr)
            problems += 1
        elif sha256(path) != digest:
            print(f"KHÁC  : {name} (nội dung không khớp SHA256SUMS)", file=sys.stderr)
            problems += 1
    extra = sorted(p.name for p in out_dir.glob("*.txt") if p.name not in expected)
    for name in extra:
        print(f"THỪA  : {name} (không có trong SHA256SUMS)", file=sys.stderr)
        problems += 1
    if problems:
        print(f"{problems} vấn đề. Chạy lại `python scripts/generate_data.py` để sinh lại dữ liệu.",
              file=sys.stderr)
        return 1
    print(f"OK: {len(expected)} bộ dữ liệu khớp SHA256SUMS.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT,
                        help="thư mục dữ liệu (mặc định: datasets/ ở thư mục gốc dự án)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--verify", action="store_true", help="chỉ kiểm tra tệp hiện có so với SHA256SUMS")
    group.add_argument("--write-checksums", action="store_true", help="ghi lại SHA256SUMS từ các tệp hiện có")
    args = parser.parse_args()

    if args.verify:
        return verify(args.out_dir)
    if args.write_checksums:
        write_checksums(args.out_dir)
        return 0
    generate(args.out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
