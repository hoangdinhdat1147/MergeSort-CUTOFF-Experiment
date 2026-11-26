import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.Random;

/**
 * Kiểm thử tính đúng đắn của {@link MergeSort} mà không cần thư viện ngoài (không JUnit).
 *
 * <pre>
 *   javac -encoding UTF-8 -d out src/MergeSort.java src/Experiment.java test/MergeSortTest.java
 *   java -cp out MergeSortTest
 * </pre>
 *
 * Kết thúc với mã thoát khác 0 nếu có ca kiểm thử thất bại. Chạy từ thư mục gốc của
 * dự án để phần kiểm tra các bộ dữ liệu trong {@code datasets/} được thực hiện.
 */
public class MergeSortTest {

    private static int checks = 0;
    private static int failures = 0;

    private static void check(boolean condition, String message) {
        checks++;
        if (!condition) {
            failures++;
            System.err.println("THAT BAI: " + message);
        }
    }

    private static void checkSortsLikeJdk(int[] input, int cutoff, String label) {
        int[] actual = input.clone();
        int[] expected = input.clone();
        MergeSort.sort(actual, cutoff);
        Arrays.sort(expected);
        check(Arrays.equals(actual, expected),
            label + " (n=" + input.length + ", cutoff=" + cutoff + ")");
        check(MergeSort.isSorted(actual), label + ": isSorted (cutoff=" + cutoff + ")");
    }

    private static boolean throwsIllegalArgument(Runnable r) {
        try {
            r.run();
            return false;
        } catch (IllegalArgumentException e) {
            return true;
        }
    }

    /** Các giá trị CUTOFF cần thử: toàn bộ 1..70 (gồm mọi giá trị của thí nghiệm) và vài giá trị biên. */
    private static int[] cutoffsToTest() {
        int[] extra = {100, 1000, Integer.MAX_VALUE};
        int[] all = new int[70 + extra.length];
        for (int i = 0; i < 70; i++) all[i] = i + 1;
        System.arraycopy(extra, 0, all, 70, extra.length);
        return all;
    }

    private static void testArguments() {
        check(throwsIllegalArgument(() -> MergeSort.sort(null, 7)), "mang null phai nem IllegalArgumentException");
        check(throwsIllegalArgument(() -> MergeSort.sort(new int[] {2, 1}, 0)), "cutoff = 0 phai nem IllegalArgumentException");
        check(throwsIllegalArgument(() -> MergeSort.sort(new int[] {2, 1}, -5)), "cutoff am phai nem IllegalArgumentException");
    }

    private static void testTinyArrays() {
        for (int cutoff : cutoffsToTest()) {
            checkSortsLikeJdk(new int[0], cutoff, "mang rong");
            checkSortsLikeJdk(new int[] {42}, cutoff, "mot phan tu");
            checkSortsLikeJdk(new int[] {2, 1}, cutoff, "hai phan tu nguoc");
            checkSortsLikeJdk(new int[] {1, 2}, cutoff, "hai phan tu xuoi");
            checkSortsLikeJdk(new int[] {3, 3, 3}, cutoff, "ba phan tu bang nhau");
        }
    }

    private static void testRandomArrays() {
        int[] sizes = {3, 7, 8, 10, 11, 12, 63, 64, 65, 100, 129, 1000, 4097};
        for (int cutoff : cutoffsToTest()) {
            for (int n : sizes) {
                Random rnd = new Random(31L * n + cutoff);
                int[] a = new int[n];
                for (int i = 0; i < n; i++) a[i] = rnd.nextInt(); // gồm cả số âm lẫn số lớn
                checkSortsLikeJdk(a, cutoff, "ngau nhien");
            }
        }
    }

    private static void testDuplicatesAndExtremes() {
        for (int cutoff : new int[] {1, 7, 10, 64}) {
            Random rnd = new Random(7);
            int[] few = new int[2000];
            for (int i = 0; i < few.length; i++) few[i] = rnd.nextInt(5) - 2; // chỉ 5 giá trị
            checkSortsLikeJdk(few, cutoff, "nhieu gia tri trung");

            int[] equal = new int[500];
            Arrays.fill(equal, -17);
            checkSortsLikeJdk(equal, cutoff, "tat ca bang nhau");

            // So sánh phải dùng > và < chứ không dùng phép trừ, nếu không sẽ tràn số.
            checkSortsLikeJdk(
                new int[] {Integer.MAX_VALUE, Integer.MIN_VALUE, 0, -1, 1, Integer.MIN_VALUE, Integer.MAX_VALUE},
                cutoff, "gia tri bien int");
        }
    }

    private static void testStructuredInputs() {
        int n = 5000;
        int[] sorted = new int[n];
        int[] reverse = new int[n];
        for (int i = 0; i < n; i++) {
            sorted[i] = i * 3 - 1000;
            reverse[i] = (n - i) * 3 - 1000;
        }
        // Gần tăng dần: hoán đổi ngẫu nhiên ~1% số cặp, giống scripts/generate_data.py.
        int[] nearly = sorted.clone();
        Random rnd = new Random(99);
        for (int s = 0; s < n / 100; s++) {
            int i = rnd.nextInt(n), j = rnd.nextInt(n);
            int t = nearly[i]; nearly[i] = nearly[j]; nearly[j] = t;
        }
        for (int cutoff : new int[] {1, 2, 7, 10, 16, 48, 64}) {
            checkSortsLikeJdk(sorted, cutoff, "tang dan");
            checkSortsLikeJdk(reverse, cutoff, "giam dan");
            checkSortsLikeJdk(nearly, cutoff, "gan tang dan");
        }
    }

    /** Khi cutoff >= n, toàn bộ mảng được sắp xếp chỉ bằng Insertion Sort; kết quả vẫn phải đúng. */
    private static void testCutoffLargerThanArray() {
        Random rnd = new Random(5);
        int[] a = new int[50];
        for (int i = 0; i < a.length; i++) a[i] = rnd.nextInt(1000);
        checkSortsLikeJdk(a, 50, "cutoff == n");
        checkSortsLikeJdk(a, 51, "cutoff > n");
    }

    private static void testIsSorted() {
        check(MergeSort.isSorted(new int[0]), "isSorted: mang rong");
        check(MergeSort.isSorted(new int[] {1}), "isSorted: mot phan tu");
        check(MergeSort.isSorted(new int[] {1, 1, 2, 3}), "isSorted: co phan tu bang nhau");
        check(!MergeSort.isSorted(new int[] {1, 3, 2}), "isSorted: phai phat hien mang chua sap xep");
        check(!MergeSort.isSorted(new int[] {2, 1}), "isSorted: hai phan tu nguoc");
    }

    /** Kiem tra day du 16 bo du lieu that va tat ca CUTOFF cua thi nghiem. */
    private static void testRepositoryDatasets() throws Exception {
        Path dir = Paths.get("datasets");
        if (!Files.isDirectory(dir)) {
            check(false, "khong tim thay thu muc datasets/");
            return;
        }

        int[] sizes = {10_000, 50_000, 100_000, 250_000};
        String[] kinds = {"random", "sorted", "reverse", "nearly_sorted"};
        int expectedDatasetCount = sizes.length * kinds.length;
        int actualDatasetCount;
        try (java.util.stream.Stream<Path> files = Files.list(dir)) {
            actualDatasetCount = (int) files
                .filter(Files::isRegularFile)
                .filter(p -> p.getFileName().toString().endsWith(".txt"))
                .count();
        }
        check(actualDatasetCount == expectedDatasetCount,
            "datasets/ phai co " + expectedDatasetCount + " file .txt, thuc te " + actualDatasetCount);

        for (String kind : kinds) {
            for (int size : sizes) {
                String name = kind + "_" + size + ".txt";
                Path file = dir.resolve(name);
                if (!Files.isRegularFile(file)) {
                    check(false, "thieu bo du lieu " + name);
                    continue;
                }

                int[] data = Experiment.readData(file);
                check(data.length == size,
                    name + ": phai co " + size + " phan tu, thuc te " + data.length);

                int[] expected = data.clone();
                Arrays.sort(expected);
                for (int cutoff : Experiment.CUTOFFS) {
                    int[] actual = data.clone();
                    MergeSort.sort(actual, cutoff);
                    check(Arrays.equals(actual, expected),
                        name + " (n=" + data.length + ", cutoff=" + cutoff + ")");
                    check(MergeSort.isSorted(actual),
                        name + ": isSorted (cutoff=" + cutoff + ")");
                }
            }
        }
    }
    public static void main(String[] args) throws Exception {
        testArguments();
        testTinyArrays();
        testRandomArrays();
        testDuplicatesAndExtremes();
        testStructuredInputs();
        testCutoffLargerThanArray();
        testIsSorted();
        testRepositoryDatasets();

        if (failures > 0) {
            System.err.println(failures + "/" + checks + " kiem tra THAT BAI.");
            System.exit(1);
        }
        System.out.println("Tat ca " + checks + " kiem tra deu dat.");
    }
}
