# Thí nghiệm tìm CUTOFF phù hợp cho Top-down Mergesort

## 1. Mục tiêu

Khảo sát ảnh hưởng của ngưỡng `CUTOFF` đến thời gian chạy của cùng một cài đặt Top-down Mergesort. Khi đoạn con có kích thước không vượt quá CUTOFF, thuật toán dùng Insertion Sort; các đoạn lớn hơn tiếp tục được chia đôi và trộn. Thí nghiệm so sánh riêng hai giá trị 7 và 10, đồng thời khảo sát toàn bộ miền CUTOFF đã chọn.

## 2. Môi trường và yêu cầu

- Java: JDK 11 trở lên; lần chạy báo cáo dùng Java 25.0.2 LTS (`javac 25.0.2`).
- Python: 3.9 trở lên; lần chạy báo cáo dùng Python 3.14.7.
- Matplotlib: 3.11.2.
- Hệ điều hành tại lần chạy báo cáo: Windows, thao tác qua Windows PowerShell 5.1.

Cài thư viện vẽ biểu đồ:

```powershell
python -m pip install matplotlib
```

## 3. Chạy trên Windows

Mở PowerShell tại thư mục dự án và chạy:

```powershell
.\run_experiment.bat
```

Nếu cần chạy từng bước:

```powershell
python scripts/generate_data.py
mkdir out
javac -encoding UTF-8 -d out src/MergeSort.java src/Experiment.java
java -cp out Experiment datasets results.csv
python scripts/analyze_results.py
```

## 4. Thiết kế thí nghiệm

- CUTOFF: `1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 16, 20, 24, 32, 40, 48, 64`.
- Kích thước: 10.000; 50.000; 100.000; 250.000 phần tử.
- Dạng dữ liệu: ngẫu nhiên, đã tăng dần, giảm dần, gần tăng dần.
- Sinh dữ liệu bằng seed cố định `20261117`.
- Mỗi cấu hình có 3 lượt warm-up và 11 lần đo chính thức.
- Thứ tự các giá trị CUTOFF được xáo trộn khi warm-up và ở mỗi lượt đo chính thức.
- Mảng làm việc được sao chép trước khi bấm giờ; thời gian sao chép không tính vào thời gian sắp xếp.
- Chỉ đo thời gian thực thi `MergeSort.sort`; không tính thời gian đọc file, sinh dữ liệu hoặc ghi CSV.
- Kiểm tra kết quả sắp xếp sau mỗi lượt chạy.
- Tổng số phép đo chính thức: `16 × 18 × 11 = 3.168`.

## 5. Tệp kết quả

Sau khi chạy `run_experiment.bat`:

- `results.csv`: dữ liệu thô, mỗi dòng là một lần chạy.
- `analysis/summary.csv`: median, mean, độ lệch chuẩn, min và max theo từng bộ dữ liệu và CUTOFF.
- `analysis/best_cutoff.csv`: CUTOFF có median nhỏ nhất trong miền đã thử cho từng bộ dữ liệu.
- `analysis/*.png`: đồ thị thời gian theo CUTOFF.

Báo cáo cũng kèm các bảng tổng hợp: `analysis/cutoff_7_10_comparison.csv` và `analysis/best_cutoff_from_run.csv`. Hai biểu đồ tổng hợp tương ứng là `analysis/comparison_cutoff_7_10.png` và `analysis/best_cutoff_by_dataset.png`.

## 6. Tóm tắt kết quả lần chạy ngày 17/11/2026

- So sánh median CUTOFF 7 và 10: CUTOFF 10 thấp hơn trong 10/16 bộ dữ liệu; CUTOFF 7 thấp hơn trong 6/16.
- Chênh lệch giữa hai giá trị không đồng đều; một số trường hợp gần như ngang nhau.
- Khi khảo sát 18 giá trị, CUTOFF 64 đứng đầu trong 7/16 bộ dữ liệu. Vì 64 là cận trên của miền đã thử, chưa thể kết luận đó là tối ưu toàn cục.
- Kết quả phụ thuộc vào dạng dữ liệu và kích thước mảng; không có căn cứ để khẳng định một giá trị luôn tối ưu.

## 7. Cách diễn giải

Ưu tiên median để mô tả thời gian trung tâm, đồng thời xem độ lệch chuẩn hoặc hệ số biến thiên để đánh giá mức dao động. Không tự ý loại bỏ các lần chạy chậm bất thường khỏi dữ liệu gốc. Nếu các median gần nhau, nên diễn giải là kết quả sát nhau thay vì tuyên bố một phương án thắng rõ rệt. Để xác định vùng tối ưu đầy đủ hơn, cần mở rộng miền thử vượt 64 và chạy lại trên nhiều seed.

Kết luận chỉ áp dụng cho cài đặt, máy, JDK, hệ điều hành và bộ dữ liệu đã sử dụng. CPU và RAM của máy thực nghiệm cần được bổ sung trong báo cáo vì chưa có trong nhật ký chạy.
