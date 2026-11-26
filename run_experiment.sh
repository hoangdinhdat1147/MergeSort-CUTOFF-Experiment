#!/usr/bin/env bash
# Chạy toàn bộ quy trình trên Linux/macOS:
#   sinh dữ liệu -> kiểm tra SHA-256 -> biên dịch -> kiểm thử -> benchmark -> phân tích
#
#   ./run_experiment.sh          cấu hình đầy đủ (3 warm-up, 11 lần đo)
#                                -> ghi results.csv và analysis/ (results.csv cũ được sao lưu)
#   ./run_experiment.sh --quick  chạy nhanh để thử (0 warm-up, 1 lần đo)
#                                -> ghi vào out/quick/, KHÔNG đụng tới results.csv và analysis/
#
# Biến môi trường tùy chọn: PYTHON=python3.12 ./run_experiment.sh
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

PYTHON="${PYTHON:-python3}"
QUICK=0
case "${1:-}" in
  "")      ;;
  --quick) QUICK=1 ;;
  -h|--help) sed -n '2,9p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
  *) echo "Tuỳ chọn không hợp lệ: $1 (dùng --quick hoặc --help)" >&2; exit 2 ;;
esac

for tool in javac java "$PYTHON"; do
  command -v "$tool" >/dev/null 2>&1 || {
    echo "Không tìm thấy '$tool'. Hãy cài JDK 11+ và Python 3, rồi đảm bảo chúng có trong PATH." >&2
    exit 1
  }
done

echo "[1/6] Sinh và kiểm tra bộ dữ liệu..."
"$PYTHON" scripts/generate_data.py >/dev/null
"$PYTHON" scripts/generate_data.py --verify

echo "[2/6] Biên dịch Java..."
mkdir -p out
javac -encoding UTF-8 -d out src/MergeSort.java src/Experiment.java test/MergeSortTest.java

echo "[3/6] Chạy kiểm thử..."
java -cp out MergeSortTest

if [ "$QUICK" -eq 1 ]; then
  echo "[4/6] Chạy benchmark nhanh (0 warm-up, 1 lần đo)..."
  java -cp out Experiment datasets out/quick/results.csv --warmups 0 --repeats 1
  echo "[5/6] Phân tích kết quả nhanh..."
  "$PYTHON" scripts/analyze_results.py --input out/quick/results.csv --out out/quick/analysis --no-plots
  echo "[6/6] Xong. Kết quả thử nằm trong out/quick/ (không ảnh hưởng results.csv)."
  exit 0
fi

if [ -f results.csv ]; then
  backup="results_old_$(date +%Y%m%d_%H%M%S).csv"
  cp results.csv "$backup"
  echo "      Đã sao lưu results.csv hiện tại sang $backup"
fi

echo "[4/6] Chạy benchmark đầy đủ (mất vài phút)..."
java -cp out Experiment datasets results.csv

echo "[5/6] Phân tích kết quả, vẽ biểu đồ, đồng bộ dữ liệu dashboard..."
"$PYTHON" scripts/analyze_results.py --sync-docs

echo "[6/6] Xong! Xem results.csv và thư mục analysis/."
