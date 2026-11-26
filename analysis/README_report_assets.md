Các tệp trong thư mục này là tài sản tổng hợp bổ sung cho báo cáo.

- `cutoff_7_10_comparison.csv`: median và độ lệch chuẩn của CUTOFF 7/10 trên 16 bộ dữ liệu, lấy từ kết quả PowerShell được cung cấp trong cuộc trò chuyện.
- `best_cutoff_from_run.csv`: CUTOFF có median thấp nhất trên từng bộ dữ liệu trong miền 1–64, lấy từ đầu ra lần chạy 11-repeat.
- `comparison_cutoff_7_10.png`: biểu đồ chênh lệch median tương đối.
- `best_cutoff_by_dataset.png`: biểu đồ CUTOFF đứng đầu từng bộ dữ liệu; CUTOFF 64 là giá trị tốt nhất ở 6/16 bộ.

Lưu ý: thư mục này không thay thế `results.csv` và `analysis/summary.csv` đầy đủ được tạo trên máy thực nghiệm. Hãy giữ và commit các tệp kết quả đầy đủ từ lần chạy chính thức trên máy của bạn.

- `cv_cutoff_7_10.png`: biểu đồ CV = SD / Mean × 100%, dùng Mean (trung bình cộng) của 11 lần đo làm mẫu số.
- `cv_cutoff_7_10_values.csv`: 16 cặp CV được trích xuất từ `analysis/summary.csv` bằng công thức SD / Mean × 100%.
