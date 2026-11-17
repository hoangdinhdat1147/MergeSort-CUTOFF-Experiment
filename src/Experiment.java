import java.io.*;
import java.nio.file.*;
import java.util.*;

/**
 * Chuong trinh benchmark:
 * - Doc cac bo du lieu .txt trong thu muc datasets.
 * - Chay nhieu CUTOFF, nhieu lan lap.
 * - Moi lan deu copy mang goc truoc khi tinh gio.
 * - Kiem tra ket qua sau khi sap xep.
 * - Ghi tung phep do vao results.csv.
 */
public class Experiment {
    private static final int[] CUTOFFS =
        {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 16, 20, 24, 32, 40, 48, 64};
    private static final int WARMUPS = 2;
    private static final int REPEATS = 7;

    private static int[] readData(Path file) throws IOException {
        String content = Files.readString(file).trim();
        if (content.isEmpty()) return new int[0];
        String[] tokens = content.split("[,\\s]+");
        int[] a = new int[tokens.length];
        for (int i = 0; i < tokens.length; i++) a[i] = Integer.parseInt(tokens[i]);
        return a;
    }

    private static long timeOne(int[] original, int cutoff) {
        int[] work = Arrays.copyOf(original, original.length); // khong tinh thoi gian tao ban sao
        long start = System.nanoTime();
        MergeSort.sort(work, cutoff);
        long elapsed = System.nanoTime() - start;
        if (!MergeSort.isSorted(work)) {
            throw new IllegalStateException("Ket qua sai: CUTOFF=" + cutoff);
        }
        return elapsed;
    }

    public static void main(String[] args) throws Exception {
        Path dataDir = Paths.get(args.length > 0 ? args[0] : "datasets");
        Path output = Paths.get(args.length > 1 ? args[1] : "results.csv");
        List<Path> files = new ArrayList<>();
        try (DirectoryStream<Path> stream = Files.newDirectoryStream(dataDir, "*.txt")) {
            for (Path p : stream) files.add(p);
        }
        files.sort(Comparator.comparing(p -> p.getFileName().toString()));
        if (files.isEmpty()) {
            System.err.println("Khong tim thay file .txt trong " + dataDir.toAbsolutePath());
            System.err.println("Hay chay: python scripts/generate_data.py");
            return;
        }

        // Lam am JVM va cac duong code truoc khi lay so lieu.
        int[] warmData = readData(files.get(0));
        for (int c : CUTOFFS) {
            for (int w = 0; w < WARMUPS; w++) timeOne(warmData, c);
        }

        try (BufferedWriter out = Files.newBufferedWriter(output)) {
            out.write("dataset,n,cutoff,repeat,elapsed_ms,correct\n");
            for (Path file : files) {
                int[] original = readData(file);
                String name = file.getFileName().toString();
                for (int cutoff : CUTOFFS) {
                    for (int r = 1; r <= REPEATS; r++) {
                        long ns = timeOne(original, cutoff);
                        out.write(String.format(Locale.US, "%s,%d,%d,%d,%.6f,true%n",
                            name, original.length, cutoff, r, ns / 1_000_000.0));
                    }
                }
                System.out.println("Da hoan thanh: " + name + " (" + original.length + " phan tu)");
            }
        }
        System.out.println("Da ghi ket qua vao: " + output.toAbsolutePath());
    }
}
