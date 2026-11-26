# Thí nghiệm tìm CUTOFF phù hợp cho Top-down Mergesort

[![CI](https://github.com/hoangdinhdat1147/MergeSort-CUTOFF-Experiment/actions/workflows/ci.yml/badge.svg)](https://github.com/hoangdinhdat1147/MergeSort-CUTOFF-Experiment/actions/workflows/ci.yml)
![Java 11+](https://img.shields.io/badge/Java-11%2B-orange)
![Python 3](https://img.shields.io/badge/Python-3-blue)
[![Dashboard](https://img.shields.io/badge/Dashboard-GitHub%20Pages-2f8d91)](https://hoangdinhdat1147.github.io/MergeSort-CUTOFF-Experiment/)

Dự án khảo sát ảnh hưởng của ngưỡng `CUTOFF` đến thời gian chạy của **Top-down Mergesort** kết hợp **Insertion Sort**. Khi đoạn con có kích thước không vượt quá `CUTOFF`, chương trình dùng Insertion Sort; các đoạn lớn hơn tiếp tục được chia và trộn như Mergesort thông thường.

Trọng tâm là so sánh `CUTOFF = 7` và `CUTOFF = 10`, đồng thời khảo sát thêm 16 giá trị khác để tìm giá trị tốt trong miền đã thử nghiệm.

**[Dashboard tương tác](https://hoangdinhdat1147.github.io/MergeSort-CUTOFF-Experiment/) · [Báo cáo .docx](report/Bao_cao_thi_nghiem_CUTOFF.docx) · [Dữ liệu thô](results.csv)**

## Kết quả chính

Thí nghiệm gồm **16 bộ dữ liệu × 18 CUTOFF × 11 lần đo = 3.168 phép đo chính thức**, sau 3 lượt warm-up.

- **CUTOFF 10** có median thấp hơn **10/16** bộ dữ liệu; **CUTOFF 7** thấp hơn **6/16**.
- Có **5/16** bộ dữ liệu chênh lệch dưới 1%, vì vậy không có bằng chứng cho thấy một giá trị luôn thắng giá trị còn lại.
- Trong toàn bộ miền khảo sát, **CUTOFF 64** có median thấp nhất ở **7/16** bộ dữ liệu, nhưng 64 là giới hạn trên nên chưa thể xem là tối ưu toàn cục.
- Kết luận chỉ áp dụng cho **cài đặt, dữ liệu, phần cứng và điều kiện đo** của thí nghiệm này.

## 1. Mục tiêu và câu hỏi nghiên cứu

Nghiên cứu nhằm đo thực nghiệm ảnh hưởng của `CUTOFF` đến hiệu năng của Top-down Mergesort khi dùng Insertion Sort cho các đoạn nhỏ.

Các câu hỏi chính:

1. `CUTOFF = 7` và `CUTOFF = 10` khác nhau như thế nào về thời gian chạy?
2. Kích thước và dạng dữ liệu ảnh hưởng ra sao đến lựa chọn CUTOFF?
3. Trong 18 giá trị được khảo sát, giá trị nào cho median thấp nhất trên từng bộ dữ liệu?

## 2. Cài đặt thuật toán

Mã nguồn chính: [`src/MergeSort.java`](src/MergeSort.java).

Cài đặt sử dụng:

- **Cutoff → Insertion Sort:** đoạn con có không quá `cutoff` phần tử được xử lý trực tiếp.
- **Skip merge:** nếu sau khi sắp xếp hai nửa có `a[mid] <= a[mid + 1]`, chương trình bỏ qua `merge()`.
- **Một mảng phụ:** `aux` được cấp phát một lần và dùng chung cho các lần merge.

Cấu trúc này bám theo Top-down Mergesort của Sedgewick & Wayne. Vì có bước bỏ qua merge, kết quả trên dữ liệu đã sắp xếp hoặc gần sắp xếp phản ánh **đúng cài đặt này**, không phải một Mergesort tổng quát bất kỳ.

## 3. Thiết kế thí nghiệm

### CUTOFF

```text
1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 16, 20, 24, 32, 40, 48, 64
```

Trong đó 7 và 10 là hai giá trị được so sánh trực tiếp.

### Dữ liệu

4 kích thước:

- 10.000
- 50.000
- 100.000
- 250.000

4 dạng:

| Dạng | Mô tả |
|---|---|
| `random` | Số nguyên ngẫu nhiên |
| `sorted` | Tăng dần |
| `reverse` | Giảm dần |
| `nearly_sorted` | Tăng dần, sau đó hoán đổi ngẫu nhiên khoảng 1% số cặp |

Tổng cộng **16 bộ dữ liệu**. Seed cơ sở là `20261117`; các tệp được kiểm tra bằng SHA-256 trong [`datasets/SHA256SUMS`](datasets/SHA256SUMS).

### Quy trình đo

- 3 lượt warm-up.
- 11 lần đo cho mỗi tổ hợp dữ liệu/CUTOFF.
- Thứ tự CUTOFF được xáo trộn có seed trong warm-up và từng lượt đo.
- Chỉ đo `MergeSort.sort` bằng `System.nanoTime()`.
- Không tính thời gian đọc/ghi tệp, sinh dữ liệu hay kiểm tra kết quả.
- Mỗi lượt đo tạo bản sao đầu vào trước khi bắt đầu tính giờ.
- Sau khi sắp xếp, kết quả được đối chiếu với `Arrays.sort`; nếu sai, benchmark dừng.

### Thống kê

Kết quả được tổng hợp bằng **median, mean, standard deviation, min và max**. Median là số đo trung tâm chính; độ lệch chuẩn được dùng để xem mức dao động.

Không thực hiện kiểm định giả thuyết, khoảng tin cậy hay effect size, nên chênh lệch thời gian nhỏ không được xem là bằng chứng về khác biệt có ý nghĩa thống kê.

## 4. Kết quả

### 4.1. CUTOFF 7 so với CUTOFF 10

Δ = (`T10 - T7`) / `T7` × 100%. Δ âm nghĩa là CUTOFF 10 thấp hơn.

| Dạng | N | CUTOFF 7 (ms) | CUTOFF 10 (ms) | Δ | Thấp hơn |
|---|---:|---:|---:|---:|:---:|
| Random | 10.000 | 0,6557 | 0,6135 | -6,44% | 10 |
| Random | 50.000 | 3,7657 | 3,7490 | -0,44% | 10 |
| Random | 100.000 | 7,9651 | 7,9695 | +0,06% | 7 |
| Random | 250.000 | 22,1386 | 21,5516 | -2,65% | 10 |
| Sorted | 10.000 | 0,0234 | 0,0202 | -13,68% | 10 |
| Sorted | 50.000 | 0,0958 | 0,0984 | +2,71% | 7 |
| Sorted | 100.000 | 0,2149 | 0,2096 | -2,47% | 10 |
| Sorted | 250.000 | 0,5694 | 0,4702 | -17,42% | 10 |
| Reverse | 10.000 | 0,2553 | 0,2470 | -3,25% | 10 |
| Reverse | 50.000 | 1,1147 | 1,1153 | +0,05% | 7 |
| Reverse | 100.000 | 2,3715 | 2,3400 | -1,33% | 10 |
| Reverse | 250.000 | 6,4574 | 6,3343 | -1,91% | 10 |
| Nearly sorted | 10.000 | 0,1518 | 0,1545 | +1,78% | 7 |
| Nearly sorted | 50.000 | 0,8134 | 0,8145 | +0,14% | 7 |
| Nearly sorted | 100.000 | 1,8126 | 1,8279 | +0,84% | 7 |
| Nearly sorted | 250.000 | 5,0018 | 4,9023 | -1,99% | 10 |

**Kết luận:** CUTOFF 10 có median thấp hơn trên 10/16 bộ dữ liệu, nhưng chênh lệch thay đổi theo kích thước và dạng dữ liệu. Một số trường hợp gần như ngang nhau.

### 4.2. CUTOFF tốt nhất trong miền 1–64

| Dạng | 10.000 | 50.000 | 100.000 | 250.000 |
|---|:---:|:---:|:---:|:---:|
| Random | 48 | 64 | 40 | 48 |
| Sorted | 64 | 64 | 40 | 64 |
| Reverse | 12 | 8 | 10 | 9 |
| Nearly sorted | 48 | 64 | 64 | 64 |

CUTOFF 64 là giá trị tốt nhất trên **7/16** bộ dữ liệu. Tuy nhiên, vì 64 là giá trị lớn nhất được thử, không thể kết luận 64 là tối ưu toàn cục. Với dữ liệu giảm dần, các giá trị tốt nhất nằm khoảng 8–12; ở ba dạng còn lại, nhiều kết quả nằm trong khoảng 40–64.

Các thống kê đầy đủ nằm trong:

- [`analysis/summary.csv`](analysis/summary.csv)
- [`analysis/best_cutoff.csv`](analysis/best_cutoff.csv)
- [`analysis/best_cutoff_from_run.csv`](analysis/best_cutoff_from_run.csv)
- [`analysis/cutoff_7_10_comparison.csv`](analysis/cutoff_7_10_comparison.csv)

## 5. Dashboard

**[MỞ DASHBOARD TƯƠNG TÁC](https://hoangdinhdat1147.github.io/MergeSort-CUTOFF-Experiment/)**

Dashboard cho phép:

- chọn dạng dữ liệu và kích thước mảng;
- xem median thời gian theo từng CUTOFF;
- phát/tạm dừng chuyển động của biểu đồ;
- xem ±1 SD;
- so sánh CUTOFF 7 và 10;
- xem heatmap CUTOFF tốt nhất.

Dashboard chỉ đọc dữ liệu từ `docs/data/`; **không chạy lại thuật toán và không tạo thêm số đo**.

## 6. Kiểm thử và tái lập

### Kiểm thử

[`test/MergeSortTest.java`](test/MergeSortTest.java) so sánh với `Arrays.sort` trên dữ liệu rỗng, rất nhỏ, ngẫu nhiên, trùng lặp, giá trị biên, tăng/giảm/gần tăng dần và **toàn bộ 16 bộ dữ liệu thật**. Với 16 bộ dữ liệu thật, test dùng 4 CUTOFF đại diện `1, 7, 10, 64` để giữ thời gian CI hợp lý; các CUTOFF khác đã được kiểm thử trên nhiều kích thước dữ liệu tổng hợp.

GitHub Actions trong [`.github/workflows/ci.yml`](.github/workflows/ci.yml) kiểm tra trên **JDK 11, 17 và 21**, đồng thời:

- biên dịch và chạy test;
- kiểm tra SHA-256 của dữ liệu;
- chạy benchmark và phân tích ở mức smoke test;
- kiểm tra tính tái lập từ `results.csv`;
- kiểm tra `docs/data/` đồng bộ với `analysis/`;
- kiểm tra cú pháp Python.

### Chạy dự án

Yêu cầu: **JDK 11+**, **Python 3**, cùng các thư viện trong `requirements.txt`.

```bash
git clone https://github.com/hoangdinhdat1147/MergeSort-CUTOFF-Experiment.git
cd MergeSort-CUTOFF-Experiment
python -m pip install -r requirements.txt
```

Chạy toàn bộ:

```bash
# Windows
.\\run_experiment.bat

# Linux/macOS
./run_experiment.sh
```

Chạy nhanh, không ghi đè kết quả chính:

```bash
# Windows
.\\run_experiment.bat --quick

# Linux/macOS
./run_experiment.sh --quick
```

Chạy thủ công:

```bash
python scripts/generate_data.py --verify
javac -encoding UTF-8 -d out src/MergeSort.java src/Experiment.java test/MergeSortTest.java
java -cp out MergeSortTest
java -cp out Experiment datasets results.csv
python scripts/analyze_results.py --sync-docs
```

## 7. Cấu trúc dự án

```text
MergeSort-CUTOFF-Experiment/
├── src/                  # Mã nguồn Java
├── test/                 # Kiểm thử
├── datasets/             # 16 bộ dữ liệu + SHA256SUMS
├── scripts/              # Sinh dữ liệu và phân tích
├── analysis/             # CSV, PNG và GIF kết quả
├── docs/                 # Dashboard GitHub Pages
├── report/               # Báo cáo .docx
├── .github/workflows/    # CI
├── results.csv           # Dữ liệu đo thô
├── run_experiment.*      # Script chạy toàn bộ quy trình
├── requirements.txt
└── README.md
```

### Các tệp quan trọng

| Tệp | Vai trò |
|---|---|
| `src/MergeSort.java` | Cài đặt Top-down Mergesort + CUTOFF |
| `src/Experiment.java` | Benchmark 18 CUTOFF |
| `test/MergeSortTest.java` | Kiểm thử tính đúng đắn |
| `results.csv` | Dữ liệu đo thô |
| `scripts/analyze_results.py` | Tính thống kê và tạo kết quả |
| `datasets/SHA256SUMS` | Kiểm tra tính toàn vẹn dữ liệu |
| `docs/index.html` | Dashboard |
| `report/Bao_cao_thi_nghiem_CUTOFF.docx` | Báo cáo chi tiết |

Các biểu đồ động trong `analysis/animated/` được tạo bởi `scripts/make_animated_charts.py`.

## 8. Giới hạn

Kết quả benchmark phụ thuộc vào:

- cài đặt Mergesort và miền CUTOFF đã chọn;
- bộ dữ liệu;
- CPU, RAM, JDK và hệ điều hành;
- tải hệ thống và hành vi JIT của JVM.

Seed cố định giúp tái tạo **đầu vào**, nhưng không đảm bảo thời gian chạy giống hệt giữa các lần đo hoặc giữa các máy.

Muốn khảo sát rộng hơn cần mở rộng CUTOFF vượt 64 và thử thêm nhiều seed dữ liệu.

## 9. Tài liệu tham khảo

1. `21ElementarySorts.pdf` — Insertion Sort.
2. `14AnalysisOfAlgorithms.pdf` — scientific method, reproducibility và empirical analysis.
3. Robert Sedgewick & Kevin Wayne, *Algorithms*, 4th Edition:
   - Section 2.2, Algorithm 2.4: Top-down Mergesort.
   - Exercise 2.2.8: bỏ qua `merge()` khi hai nửa đã đúng thứ tự.
   - Phần “Cutoff to insertion sort”.
4. Bài yêu cầu của giảng viên: khảo sát CUTOFF cho cài đặt Mergesort tự dựng.

---

**Trạng thái báo cáo:** kết quả lần chạy ngày 17/11/2026 trên Windows 11, Java 25.0.2 LTS, Intel Core i7-1185G7 và RAM 32 GB.
