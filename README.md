# Thí nghiệm tìm CUTOFF tối ưu cho Top-down Mergesort

## 1. Mục tiêu
So sánh thời gian chạy của cùng một cài đặt Top-down Mergesort khi thay đổi ngưỡng CUTOFF dùng Insertion Sort cho các đoạn con nhỏ. Không dùng `Arrays.sort()` hoặc thư viện sắp xếp thay thế.

## 2. Yêu cầu
- JDK 11 trở lên (khuyến nghị JDK 17/21).
- Python 3.9 trở lên.
- Cài thư viện vẽ biểu đồ: `python -m pip install matplotlib`.

## 3. Chạy trên Windows
Giải nén ZIP, mở thư mục project, nháy đúp `run_experiment.bat` hoặc chạy trong CMD/PowerShell:
```powershell
python -m pip install matplotlib
.un_experiment.bat
```
Nếu Windows không chạy được file `.bat`, chạy lần lượt:
```powershell
python scripts/generate_data.py
mkdir out
javac -encoding UTF-8 -d out src/MergeSort.java src/Experiment.java
java -cp out Experiment datasets results.csv
python scripts/analyze_results.py
```

## 4. Thiết kế thí nghiệm
- CUTOFF: 1,2,3,4,5,6,7,8,9,10,12,16,20,24,32,40,48,64.
- Kích thước: 10.000; 50.000; 100.000; 250.000 phần tử.
- Phân phối: ngẫu nhiên, tăng dần, giảm dần, gần tăng dần (xáo trộn 1% số cặp).
- Mỗi cấu hình chạy 7 lần; 2 lượt warm-up cho từng CUTOFF.
- Dữ liệu được sinh với seed cố định 20261117 để có thể tái lập.
- Mỗi lượt sao chép dữ liệu gốc trước khi bấm giờ; thời gian copy không tính vào thời gian sắp xếp.
- Kết quả được kiểm tra tăng dần sau mỗi lần chạy.
- Chỉ đo thời gian của `MergeSort.sort`; không đo đọc file, sinh dữ liệu hay ghi CSV.

## 5. Kết quả sinh ra
- `results.csv`: dữ liệu thô, mỗi dòng là một lần chạy.
- `analysis/summary.csv`: median, mean, standard deviation, min, max theo từng bộ dữ liệu và CUTOFF.
- `analysis/best_cutoff.csv`: CUTOFF có median nhỏ nhất trên từng bộ dữ liệu.
- `analysis/*.png`: đồ thị thời gian theo CUTOFF.

## 6. Cách kết luận
Không chọn CUTOFF chỉ dựa vào một phép đo hoặc một kích thước. Ưu tiên:
1. Median thấp và ổn định trên nhiều lần chạy.
2. Hiệu năng nhất quán ở nhiều kích thước dữ liệu.
3. Xem xét riêng dữ liệu ngẫu nhiên và các dạng dữ liệu có thứ tự.
4. Nếu một nhóm giá trị gần như ngang nhau, chọn giá trị đơn giản, ổn định thay vì khẳng định một điểm thắng rất nhỏ.

Kết luận chỉ có giá trị đối với máy, JDK, hệ điều hành và điều kiện chạy đã ghi trong báo cáo. Đóng ứng dụng nặng, cắm sạc nếu dùng laptop và không chạy nhiều chương trình benchmark đồng thời.

## 7. Lưu ý phương pháp
Java JIT có thể làm các lượt đầu chậm hơn, vì vậy chương trình warm-up trước. Median được dùng làm số đo trung tâm để giảm ảnh hưởng của các lần chạy bất thường. Độ lệch chuẩn cho biết mức phân tán. Không so sánh kết quả của hai máy khác nhau như thể chúng cùng điều kiện.
