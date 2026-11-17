
import java.io.*;
import java.nio.file.*;
import java.util.*;

/**
 * Chuong trinh benchmark MergeSort voi nhieu gia tri CUTOFF.
 *
 * - Doc cac bo du lieu trong thu muc datasets.
 * - Moi bo du lieu duoc warm-up rieng.
 * - Moi vong do se xao tron thu tu CUTOFF.
 * - Moi lan do deu su dung ban sao cua mang goc.
 * - Kiem tra ket qua sau khi sap xep.
 * - Ghi tung phep do vao results.csv.
 */
public class Experiment {

    private static final int[] CUTOFFS = {
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
        12, 16, 20, 24, 32, 40, 48, 64
    };

    private static final int WARMUPS = 3;
    private static final int REPEATS = 11;

    private static final long RANDOM_SEED = 20261117L;

    // Doc du lieu tu file.
    private static int[] readData(Path file) throws IOException {

        String content = Files.readString(file).trim();

        if (content.isEmpty()) {
            return new int[0];
        }

        String[] tokens = content.split("[,\\s]+");

        int[] a = new int[tokens.length];

        for (int i = 0; i < tokens.length; i++) {
            a[i] = Integer.parseInt(tokens[i]);
        }

        return a;
    }

    // Tao danh sach CUTOFF de xao tron thu tu.
    private static List<Integer> createCutoffList() {

        List<Integer> list = new ArrayList<>();

        for (int cutoff : CUTOFFS) {
            list.add(cutoff);
        }

        return list;
    }

    // Thuc hien mot lan sap xep va do thoi gian.
    private static long timeOne(
        int[] original,
        int[] expected,
        int cutoff
    ) {

        // Tao ban sao truoc khi bat dau tinh gio.
        int[] work = Arrays.copyOf(original, original.length);

        long start = System.nanoTime();

        MergeSort.sort(work, cutoff);

        long elapsed = System.nanoTime() - start;

        // Kiem tra sau khi da dung dong ho.
        if (!MergeSort.isSorted(work)
                || !Arrays.equals(work, expected)) {

            throw new IllegalStateException(
                "Ket qua sai: CUTOFF=" + cutoff
            );
        }

        return elapsed;
    }

    public static void main(String[] args) throws Exception {

        Path dataDir = Paths.get(
            args.length > 0 ? args[0] : "datasets"
        );

        Path output = Paths.get(
            args.length > 1 ? args[1] : "results.csv"
        );

        List<Path> files = new ArrayList<>();

        try (DirectoryStream<Path> stream =
                 Files.newDirectoryStream(dataDir, "*.txt")) {

            for (Path p : stream) {
                files.add(p);
            }
        }

        files.sort(
            Comparator.comparing(
                p -> p.getFileName().toString()
            )
        );

        if (files.isEmpty()) {

            System.err.println(
                "Khong tim thay file .txt trong "
                + dataDir.toAbsolutePath()
            );

            return;
        }

        try (BufferedWriter out = Files.newBufferedWriter(output)) {

            out.write(
                "dataset,n,cutoff,repeat,elapsed_ms,correct\n"
            );

            // Xu ly tung bo du lieu.
            for (Path file : files) {

                int[] original = readData(file);

                String name = file.getFileName().toString();

                int n = original.length;

                // Tao ket qua dung de doi chieu.
                int[] expected =
                    Arrays.copyOf(original, original.length);

                Arrays.sort(expected);

                // Random co seed de co the lap lai thu tu.
                Random random = new Random(
                    RANDOM_SEED + name.hashCode()
                );

                // ---------------------------------
                // GIAI DOAN 1: WARM-UP
                // ---------------------------------

                for (int w = 0; w < WARMUPS; w++) {

                    List<Integer> warmupOrder =
                        createCutoffList();

                    Collections.shuffle(
                        warmupOrder,
                        random
                    );

                    for (int cutoff : warmupOrder) {

                        timeOne(original, expected, cutoff);
                    }
                }

                // ---------------------------------
                // GIAI DOAN 2: BENCHMARK
                // ---------------------------------

                for (int r = 1; r <= REPEATS; r++) {

                    List<Integer> order =
                        createCutoffList();

                    // Xao tron thu tu CUTOFF moi vong.
                    Collections.shuffle(order, random);

                    for (int cutoff : order) {

                        long ns = timeOne(
                            original,
                            expected,
                            cutoff
                        );

                        double elapsedMs =
                            ns / 1_000_000.0;

                        out.write(
                            String.format(
                                Locale.US,
                                "%s,%d,%d,%d,%.6f,true%n",
                                name,
                                n,
                                cutoff,
                                r,
                                elapsedMs
                            )
                        );
                    }
                }

                out.flush();

                System.out.println(
                    "Da hoan thanh: "
                    + name
                    + " ("
                    + n
                    + " phan tu)"
                );
            }
        }

        System.out.println(
            "Da ghi ket qua vao: "
            + output.toAbsolutePath()
        );
    }
}

