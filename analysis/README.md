# Thư mục `analysis/`

Bảng thống kê và biểu đồ tổng hợp từ `results.csv` (lần chạy ngày 17/11/2026).

Các tệp CSV và biểu đồ riêng theo bộ dữ liệu được **tạo lại hoàn toàn từ `results.csv`** bằng:

```bash
python scripts/analyze_results.py            # thêm --sync-docs để cập nhật docs/data/ cho dashboard
```

| Tệp | Nội dung | Cách tạo |
|---|---|---|
| `summary.csv` | Số lần đo, median, mean, độ lệch chuẩn, min, max theo (bộ dữ liệu, CUTOFF). | `analyze_results.py` |
| `best_cutoff.csv` | CUTOFF có median thấp nhất của từng bộ dữ liệu (trong miền 1–64 đã thử). | `analyze_results.py` |
| `best_cutoff_from_run.csv` | Cùng nội dung với `best_cutoff.csv`, tên cột theo định dạng dashboard/báo cáo. | `analyze_results.py` |
| `cutoff_7_10_comparison.csv` | Median, độ lệch chuẩn và chênh lệch tương đối (%) giữa CUTOFF 7 và 10 trên 16 bộ dữ liệu. | `analyze_results.py` |
| `<bo_du_lieu>.txt.png` | Median thời gian theo CUTOFF của từng bộ dữ liệu. | `analyze_results.py` |
| `animated/*.gif` | Sáu biểu đồ động tương ứng với các bảng trên. | `scripts/make_animated_charts.py` |
| `comparison_cutoff_7_10.png` | Chênh lệch median tương đối giữa CUTOFF 10 và CUTOFF 7. | Hình tĩnh kèm báo cáo |
| `best_cutoff_by_dataset.png` | CUTOFF đứng đầu ở từng bộ dữ liệu. | Hình tĩnh kèm báo cáo |

Hai hình PNG tổng hợp ở cuối bảng là hình tĩnh kèm báo cáo, chưa có script sinh lại; nội dung của chúng lấy từ `cutoff_7_10_comparison.csv` và `best_cutoff_from_run.csv`. Nếu chạy benchmark mới, cần vẽ lại hai hình này (hoặc dùng các GIF tương ứng) trước khi dùng chúng để mô tả lần chạy mới.

Thư mục này không thay thế `results.csv`: đó là dữ liệu thô duy nhất, mọi bảng ở đây đều suy ra từ nó. Quy trình CI kiểm tra điều đó bằng cách tính lại các CSV và so sánh với các tệp đã commit.
