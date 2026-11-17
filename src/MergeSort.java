import java.util.Arrays;

/**
 * Top-down MergeSort theo cau truc Algorithm 2.4 trong
 * Sedgewick & Wayne, Algorithms, 4th Edition, Section 2.2.
 *
 * Cải tiến: nếu đoạn con có kích thước <= CUTOFF thì dùng Insertion Sort.
 */
public final class MergeSort {
    private MergeSort() {}

    public static void sort(int[] a, int cutoff) {
        if (a == null) throw new IllegalArgumentException("Mang khong duoc null");
        if (cutoff < 1) throw new IllegalArgumentException("CUTOFF phai >= 1");
        if (a.length < 2) return;

        int[] aux = new int[a.length]; // cap phat mot lan, dung chung cho cac lan merge
        sort(a, aux, 0, a.length - 1, cutoff);
    }

    private static void sort(int[] a, int[] aux, int lo, int hi, int cutoff) {
        int length = hi - lo + 1;

        // Khi doan con nho, dung Insertion Sort thay vi tiep tuc de quy.
        if (length <= cutoff) {
            insertionSort(a, lo, hi);
            return;
        }

        int mid = lo + (hi - lo) / 2;
        sort(a, aux, lo, mid, cutoff);
        sort(a, aux, mid + 1, hi, cutoff);

        // Bo qua merge neu hai nua da noi tiep dung thu tu.
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
        // Sao chep doan can tron sang mang phu.
        for (int k = lo; k <= hi; k++) aux[k] = a[k];

        int i = lo;
        int j = mid + 1;
        for (int k = lo; k <= hi; k++) {
            if (i > mid)                  a[k] = aux[j++];
            else if (j > hi)              a[k] = aux[i++];
            else if (aux[j] < aux[i])     a[k] = aux[j++];
            else                          a[k] = aux[i++];
        }
    }

    public static boolean isSorted(int[] a) {
        for (int i = 1; i < a.length; i++) {
            if (a[i - 1] > a[i]) return false;
        }
        return true;
    }

    // Dung de kiem tra nhanh khi can.
    public static int[] copy(int[] a) {
        return Arrays.copyOf(a, a.length);
    }
}
