import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import java.util.Random;

/**
 * Chương trình benchmark MergeSort với nhiều giá trị CUTOFF.
 *
 * <ul>
 *   <li>Đọc mọi tệp {@code *.txt} trong thư mục dữ liệu.</li>
 *   <li>Mỗi bộ dữ liệu được warm-up riêng trước khi đo.</li>
 *   <li>Thứ tự các CUTOFF được xáo trộn (có seed) ở mỗi vòng warm-up và mỗi vòng đo.</li>
 *   <li>Mỗi lần đo dùng một bản sao của mảng gốc; thời gian sao chép và kiểm tra
 *       kết quả không được tính.</li>
 *   <li>Ghi từng phép đo vào tệp CSV.</li>
 * </ul>
 *
 * <p>Cách dùng:
 * <pre>
 *   java -cp out Experiment [thu_muc_du_lieu] [tep_ket_qua] [--warmups N] [--repeats N]
 * </pre>
 * Mặc định: {@code datasets results.csv --warmups 3 --repeats 11}, tức cấu hình đã
 * dùng cho kết quả trong báo cáo.
 *
 * <p>Thông báo in ra console dùng chữ không dấu để hiển thị đúng trên mọi terminal.
 */
public class Experiment {

    /** Các giá trị CUTOFF được khảo sát (18 giá trị). */
    static final int[] CUTOFFS = {
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
        12, 16, 20, 24, 32, 40, 48, 64
    };

    static final int DEFAULT_WARMUPS = 3;
    static final int DEFAULT_REPEATS = 11;

    /** Seed cơ sở; mỗi bộ dữ liệu cộng thêm hashCode của tên tệp để có chuỗi xáo trộn riêng. */
    static final long RANDOM_SEED = 20261117L;

    private static final String CSV_HEADER = "dataset,n,cutoff,repeat,elapsed_ms,correct\n";

    /** Đọc một tệp số nguyên, phân tách bằng khoảng trắng hoặc dấu phẩy. */
    static int[] readData(Path file) throws IOException {
        String content = Files.readString(file).trim();
        if (content.isEmpty()) return new int[0];

        String[] tokens = content.split("[,\\s]+");
        int[] a = new int[tokens.length];
        for (int i = 0; i < tokens.length; i++) {
            try {
                a[i] = Integer.parseInt(tokens[i]);
            } catch (NumberFormatException e) {
                throw new IOException(
                    "Gia tri khong hop le '" + tokens[i] + "' (vi tri " + i + ") trong " + file, e);
            }
        }
        return a;
    }

    /** Tạo danh sách CUTOFF để xáo trộn thứ tự. */
    private static List<Integer> createCutoffList() {
        List<Integer> list = new ArrayList<>(CUTOFFS.length);
        for (int cutoff : CUTOFFS) list.add(cutoff);
        return list;
    }

    /** Thực hiện một lần sắp xếp, trả về thời gian (nano giây) và kiểm tra kết quả. */
    private static long timeOne(int[] original, int[] expected, int cutoff) {
        // Tạo bản sao trước khi bắt đầu tính giờ.
        int[] work = Arrays.copyOf(original, original.length);

        long start = System.nanoTime();
        MergeSort.sort(work, cutoff);
        long elapsed = System.nanoTime() - start;

        // Kiểm tra sau khi đã dừng đồng hồ.
        if (!MergeSort.isSorted(work) || !Arrays.equals(work, expected)) {
            throw new IllegalStateException("Ket qua sai: CUTOFF=" + cutoff);
        }
        return elapsed;
    }

    private static void printUsage() {
        System.err.println(
            "Cach dung: java -cp out Experiment [thu_muc_du_lieu] [tep_ket_qua]"
            + " [--warmups N] [--repeats N]\n"
            + "Mac dinh : datasets results.csv --warmups " + DEFAULT_WARMUPS
            + " --repeats " + DEFAULT_REPEATS);
    }

    private static int parseNonNegative(String option, String value, int min) {
        try {
            int n = Integer.parseInt(value);
            if (n >= min) return n;
        } catch (NumberFormatException ignored) {
            // rơi xuống thông báo lỗi bên dưới
        }
        throw new IllegalArgumentException(option + " phai la so nguyen >= " + min + ", nhan duoc: " + value);
    }

    public static void main(String[] args) throws Exception {
        String dataDirArg = "datasets";
        String outputArg = "results.csv";
        int warmups = DEFAULT_WARMUPS;
        int repeats = DEFAULT_REPEATS;

        try {
            int positional = 0;
            for (int i = 0; i < args.length; i++) {
                String arg = args[i];
                if (arg.equals("-h") || arg.equals("--help")) {
                    printUsage();
                    return;
                } else if (arg.equals("--warmups") || arg.equals("--repeats")) {
                    if (i + 1 >= args.length) throw new IllegalArgumentException("Thieu gia tri cho " + arg);
                    String value = args[++i];
                    if (arg.equals("--warmups")) warmups = parseNonNegative(arg, value, 0);
                    else repeats = parseNonNegative(arg, value, 1);
                } else if (arg.startsWith("--")) {
                    throw new IllegalArgumentException("Tuy chon khong hop le: " + arg);
                } else if (positional == 0) {
                    dataDirArg = arg;
                    positional++;
                } else if (positional == 1) {
                    outputArg = arg;
                    positional++;
                } else {
                    throw new IllegalArgumentException("Du doi so: " + arg);
                }
            }
        } catch (IllegalArgumentException e) {
            System.err.println("Loi: " + e.getMessage());
            printUsage();
            System.exit(2);
        }

        Path dataDir = Paths.get(dataDirArg);
        Path output = Paths.get(outputArg);

        if (!Files.isDirectory(dataDir)) {
            System.err.println("Khong tim thay thu muc du lieu: " + dataDir.toAbsolutePath());
            System.exit(1);
        }

        List<Path> files = new ArrayList<>();
        try (DirectoryStream<Path> stream = Files.newDirectoryStream(dataDir, "*.txt")) {
            for (Path p : stream) files.add(p);
        }
        files.sort(Comparator.comparing(p -> p.getFileName().toString()));

        if (files.isEmpty()) {
            System.err.println("Khong tim thay file .txt trong " + dataDir.toAbsolutePath());
            System.exit(1);
        }

        Path parent = output.toAbsolutePath().getParent();
        if (parent != null) Files.createDirectories(parent);

        System.out.printf(Locale.US, "Cau hinh: %d bo du lieu, %d gia tri CUTOFF, %d warm-up, %d lan do%n",
            files.size(), CUTOFFS.length, warmups, repeats);

        try (BufferedWriter out = Files.newBufferedWriter(output)) {
            out.write(CSV_HEADER);

            for (Path file : files) {
                int[] original = readData(file);
                String name = file.getFileName().toString();
                int n = original.length;

                // Kết quả đúng dùng để đối chiếu.
                int[] expected = Arrays.copyOf(original, original.length);
                Arrays.sort(expected);

                // Random có seed để thứ tự xáo trộn lặp lại được.
                Random random = new Random(RANDOM_SEED + name.hashCode());

                // Giai đoạn 1: warm-up (không ghi kết quả).
                for (int w = 0; w < warmups; w++) {
                    List<Integer> warmupOrder = createCutoffList();
                    Collections.shuffle(warmupOrder, random);
                    for (int cutoff : warmupOrder) timeOne(original, expected, cutoff);
                }

                // Giai đoạn 2: đo chính thức; xáo trộn thứ tự CUTOFF ở mỗi vòng.
                for (int r = 1; r <= repeats; r++) {
                    List<Integer> order = createCutoffList();
                    Collections.shuffle(order, random);

                    for (int cutoff : order) {
                        long ns = timeOne(original, expected, cutoff);
                        double elapsedMs = ns / 1_000_000.0;
                        // timeOne ném ngoại lệ nếu kết quả sai nên mọi dòng ghi ra đều đúng.
                        // Dùng "\n" tường minh để CSV giống nhau trên mọi hệ điều hành.
                        out.write(String.format(Locale.US, "%s,%d,%d,%d,%.6f,true\n",
                            name, n, cutoff, r, elapsedMs));
                    }
                }
                out.flush();

                System.out.println("Da hoan thanh: " + name + " (" + n + " phan tu)");
            }
        }

        System.out.println("Da ghi ket qua vao: " + output.toAbsolutePath());
    }
}
