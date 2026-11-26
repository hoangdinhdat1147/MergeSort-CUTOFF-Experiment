/**
 * Top-down Mergesort kết hợp Insertion Sort cho các đoạn con nhỏ.
 *
 * <p>Cấu trúc theo Algorithm 2.4 trong Sedgewick &amp; Wayne, <i>Algorithms</i>,
 * 4th Edition, Section 2.2, cùng hai cải tiến:
 *
 * <ol>
 *   <li><b>CUTOFF</b> (tham số được khảo sát trong thí nghiệm): đoạn con có
 *       không quá {@code cutoff} phần tử được sắp xếp bằng Insertion Sort thay
 *       vì tiếp tục chia đôi.</li>
 *   <li><b>Bỏ qua merge</b> khi {@code a[mid] <= a[mid + 1]}, tức hai nửa đã
 *       nối tiếp đúng thứ tự (Exercise 2.2.8). Với mảng đã tăng dần, không có
 *       lời gọi {@code merge()} nào được thực hiện.</li>
 * </ol>
 *
 * <p>Mảng phụ {@code aux} được cấp phát một lần và dùng chung cho mọi lần merge.
 *
 * <p><b>Lưu ý khi sửa tệp này:</b> các kết quả trong {@code results.csv} được đo
 * bằng đúng logic bên dưới. Thay đổi thuật toán sẽ làm các kết quả đó không còn
 * tương ứng với mã nguồn.
 */
public final class MergeSort {
    private MergeSort() {}

    /**
     * Sắp xếp mảng tăng dần tại chỗ.
     *
     * @param a      mảng cần sắp xếp, không được {@code null}
     * @param cutoff đoạn con có kích thước &lt;= cutoff dùng Insertion Sort; phải &gt;= 1
     * @throws IllegalArgumentException nếu {@code a} là {@code null} hoặc {@code cutoff < 1}
     */
    public static void sort(int[] a, int cutoff) {
        // Thông báo lỗi viết không dấu (ASCII) để hiển thị đúng trên mọi console, kể cả Windows.
        if (a == null) throw new IllegalArgumentException("Mang khong duoc null");
        if (cutoff < 1) throw new IllegalArgumentException("CUTOFF phai >= 1");
        if (a.length < 2) return;

        int[] aux = new int[a.length]; // cấp phát một lần, dùng chung cho các lần merge
        sort(a, aux, 0, a.length - 1, cutoff);
    }

    private static void sort(int[] a, int[] aux, int lo, int hi, int cutoff) {
        int length = hi - lo + 1;

        // Đoạn con nhỏ: dùng Insertion Sort thay vì tiếp tục đệ quy.
        if (length <= cutoff) {
            insertionSort(a, lo, hi);
            return;
        }

        int mid = lo + (hi - lo) / 2;
        sort(a, aux, lo, mid, cutoff);
        sort(a, aux, mid + 1, hi, cutoff);

        // Bỏ qua merge nếu hai nửa đã nối tiếp đúng thứ tự.
        if (a[mid] <= a[mid + 1]) return;

        merge(a, aux, lo, mid, hi);
    }

    private static void insertionSort(int[] a, int lo, int hi) {
        for (int i = lo + 1; i <= hi; i++) {
            int value = a[i];
            int j = i;
            while (j > lo && a[j - 1] > value) {
                a[j] = a[j - 1];
                j--;
            }
            a[j] = value;
        }
    }

    private static void merge(int[] a, int[] aux, int lo, int mid, int hi) {
        // Sao chép đoạn cần trộn sang mảng phụ.
        for (int k = lo; k <= hi; k++) aux[k] = a[k];

        int i = lo;
        int j = mid + 1;
        for (int k = lo; k <= hi; k++) {
            if (i > mid)              a[k] = aux[j++];
            else if (j > hi)          a[k] = aux[i++];
            else if (aux[j] < aux[i]) a[k] = aux[j++];
            else                      a[k] = aux[i++];
        }
    }

    /** Trả về {@code true} nếu mảng được sắp xếp theo thứ tự không giảm. */
    public static boolean isSorted(int[] a) {
        for (int i = 1; i < a.length; i++) {
            if (a[i - 1] > a[i]) return false;
        }
        return true;
    }
}
