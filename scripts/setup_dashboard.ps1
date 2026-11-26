$ErrorActionPreference = 'Stop'

$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$readmePath = Join-Path $root 'README.md'
$dashboardPath = Join-Path $root 'docs\index.html'
$dataSource = Join-Path $root 'analysis'
$dataTarget = Join-Path $root 'docs\data'

if (-not (Test-Path $readmePath)) {
    throw 'Khong tim thay README.md. Hay chay script tai thu muc goc cua du an.'
}
if (-not (Test-Path $dashboardPath)) {
    throw 'Khong tim thay docs\index.html. Hay giai nen goi dashboard vao thu muc goc du an truoc.'
}

$csvFiles = @('summary.csv', 'cutoff_7_10_comparison.csv', 'best_cutoff_from_run.csv')
foreach ($file in $csvFiles) {
    if (-not (Test-Path (Join-Path $dataSource $file))) {
        throw "Khong tim thay analysis\$file. README chua bi thay doi."
    }
}

$utf8 = [System.Text.UTF8Encoding]::new($false)
$content = [System.IO.File]::ReadAllText($readmePath, [System.Text.Encoding]::UTF8)
$start = [regex]::Match($content, '(?m)^### 6\.3\..*$')
$finish = [regex]::Match($content, '(?m)^## 7\. Các tệp kết quả\s*$')

if (-not $start.Success -or -not $finish.Success -or $finish.Index -le $start.Index) {
    throw 'Khong tim thay dung ranh gioi muc 6.3 va muc 7 trong README.md. Khong co tep nao bi sua.'
}

$newSection = @'
### 6.3. Dashboard biểu đồ tương tác

Các biểu đồ tương tác được đặt trong dashboard riêng để có thể chọn dạng dữ liệu, thay đổi kích thước mảng và phát lần lượt các trạng thái. Dashboard sử dụng các bảng CSV được sao chép từ `analysis/` sang `docs/data/`; không chạy lại thuật toán và không tạo thêm số đo.

**[MỞ DASHBOARD – XEM BIỂU ĐỒ TƯƠNG TÁC](https://hoangdinhdat1147.github.io/MergeSort-CUTOFF-Experiment/)**

Dashboard gồm ba phần chính:

- Median thời gian chạy theo CUTOFF, có thể lọc theo dạng dữ liệu, chọn kích thước mảng và phát/tạm dừng chuyển động. Thanh sai số biểu thị ±1 độ lệch chuẩn.
- So sánh median của CUTOFF 7 và CUTOFF 10 trên 16 bộ dữ liệu.
- Bản đồ nhiệt thể hiện CUTOFF có median thấp nhất trong 18 giá trị đã thử.

Chuyển động chỉ thay đổi tập dữ liệu đang hiển thị; các điểm trên biểu đồ đều lấy từ kết quả đo trong CSV. Giá trị CUTOFF = 64 là giới hạn trên của miền khảo sát, không đồng nghĩa với tối ưu toàn cục.

Dashboard sử dụng ba tệp CSV trong `docs/data/`. Các tệp này được sao chép từ `analysis/summary.csv`, `analysis/cutoff_7_10_comparison.csv` và `analysis/best_cutoff_from_run.csv` khi cài dashboard. Để mở trang, repository cần bật GitHub Pages với nguồn triển khai là nhánh `main`, thư mục `/docs`.

'@

$updated = $content.Substring(0, $start.Index) + $newSection + $content.Substring($finish.Index)

# Cap nhat thong tin may da duoc xac nhan trong qua trinh thuc nghiem.
$updated = $updated.Replace('| Hệ điều hành | Windows |', '| Hệ điều hành | Windows 11, Version 26H2 (OS Build 26300.9818) |')
$updated = $updated.Replace('| CPU | Chưa được ghi nhận trong nhật ký chạy; cần bổ sung |', '| CPU | 11th Gen Intel® Core™ i7-1185G7 @ 3.00 GHz |')
$updated = $updated.Replace('| RAM | Chưa được ghi nhận trong nhật ký chạy; cần bổ sung |', '| RAM | 32 GB (Windows hiển thị khả dụng 31,7 GB) |')
$updated = $updated.Replace('| `analysis/best_cutoff_by_dataset.png` | Biểu đồ tổng hợp CUTOFF tốt nhất theo bộ dữ liệu. | Tệp biểu đồ bổ sung cho báo cáo |', '| `analysis/best_cutoff_by_dataset.png` | Biểu đồ tổng hợp CUTOFF tốt nhất theo bộ dữ liệu. | Tệp biểu đồ bổ sung cho báo cáo |' + "`r`n" + '| `docs/index.html` | Dashboard biểu đồ tương tác. | GitHub Pages |' + "`r`n" + '| `docs/data/*.csv` | Bản sao các CSV dùng trong dashboard. | `scripts/setup_dashboard.ps1` |')
$updated = $updated.Replace("`r`nCPU và RAM cần được điền trước khi dùng báo cáo như một bản mô tả đầy đủ môi trường phần cứng.", '')
$updated = $updated.Replace("`nCPU và RAM cần được điền trước khi dùng báo cáo như một bản mô tả đầy đủ môi trường phần cứng.", '')
if ($updated -match '(?m)^│   └── analyze_results\.py\s*$') {
    $updated = [regex]::Replace($updated, '(?m)^│   └── analyze_results\.py\s*$', "│   ├── analyze_results.py`r`n│   ├── make_animated_charts.py`r`n│   └── setup_dashboard.ps1")
} elseif ($updated -match '(?m)^│   └── make_animated_charts\.py\s*$') {
    $updated = [regex]::Replace($updated, '(?m)^│   └── make_animated_charts\.py\s*$', "│   ├── make_animated_charts.py`r`n│   └── setup_dashboard.ps1")
} elseif ($updated -match '(?m)^│   ├── make_animated_charts\.py\s*$' -and $updated -notmatch 'setup_dashboard\.ps1') {
    $updated = [regex]::Replace($updated, '(?m)^│   ├── make_animated_charts\.py\s*$', "│   ├── make_animated_charts.py`r`n│   └── setup_dashboard.ps1")
}
if ($updated -notmatch '(?m)^├── docs/') {
    $updated = $updated.Replace('├── results.csv', "├── docs/                             # Trang dashboard GitHub Pages`r`n│   ├── index.html`r`n│   └── data/`r`n│       ├── summary.csv`r`n│       ├── cutoff_7_10_comparison.csv`r`n│       └── best_cutoff_from_run.csv`r`n├── results.csv")
}
$updated = $updated.Replace('**Trạng thái báo cáo:** kết quả lần chạy ngày 26/11/2026. Thông tin CPU và RAM của máy thực nghiệm chưa được ghi nhận và cần được bổ sung trước khi nộp báo cáo chính thức.', '**Trạng thái báo cáo:** kết quả lần chạy ngày 26/11/2026. Máy thực nghiệm sử dụng Intel Core i7-1185G7, RAM 32 GB, Windows 11 và Java 25.0.2 LTS.')

# Dong bo ba bang CSV vao docs/data de dashboard doc duoc tren cung domain GitHub Pages.
New-Item -ItemType Directory -Force -Path $dataTarget | Out-Null
foreach ($file in $csvFiles) {
    Copy-Item (Join-Path $dataSource $file) (Join-Path $dataTarget $file) -Force
}

# Tao ban sao tam thoi truoc khi ghi README.
$backupPath = Join-Path $env:TEMP ('README_before_dashboard_' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff') + '.md')
[System.IO.File]::Copy($readmePath, $backupPath, $false)
[System.IO.File]::WriteAllText($readmePath, $updated, $utf8)

Write-Host 'Da cap nhat README.md va tao ban sao truoc khi sua:' -ForegroundColor Green
Write-Host $backupPath
Write-Host 'Da them lien ket dashboard va cap nhat CPU/RAM/Windows.'
