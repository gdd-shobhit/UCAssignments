/*
 * Single-shard daxpy for gem5 SE multi-core without pthreads as pthreads was not working in SE mode. 
 * Each shard is a separate process with its own address space, so this matches gem5 SE "one process per CPU" and avoids pthread.
 * Usage: daxpy_shard <shard_id> <num_shards> <n>
 *
 * Global problem size n (doubles). Shard s owns global indices
 * [s * chunk, min((s+1)*chunk, n)). Each process has its own address space,
 * so this matches gem5 SE "one process per CPU" and avoids pthread/clone.
 */

#include <stdio.h>
#include <stdlib.h>

#ifdef GEM5
#include <gem5/m5ops.h>
#endif

int
main(int argc, char **argv)
{
    if (argc < 4) {
        fprintf(stderr,
                "usage: %s <shard_id> <num_shards> <n>\n",
                argc > 0 ? argv[0] : "daxpy_shard");
        return 1;
    }

    int shard_id = atoi(argv[1]);
    int num_shards = atoi(argv[2]);
    unsigned long long n_ull = strtoull(argv[3], NULL, 10);
    size_t n = (size_t)n_ull;

    if (num_shards < 1 || shard_id < 0 || shard_id >= num_shards || n == 0) {
        fprintf(stderr, "invalid shard_id / num_shards / n\n");
        return 1;
    }

    size_t chunk = (n + (size_t)num_shards - 1) / (size_t)num_shards;
    size_t start = (size_t)shard_id * chunk;
    size_t end = start + chunk;
    if (end > n) {
        end = n;
    }
    size_t local = (end > start) ? (end - start) : 0;

    double *x = (double *)malloc(local * sizeof(double));
    double *y = (double *)malloc(local * sizeof(double));
    if (local > 0 && (!x || !y)) {
        fprintf(stderr, "allocation failed\n");
        free(x);
        free(y);
        return 1;
    }

    for (size_t li = 0; li < local; li++) {
        size_t g = start + li;
        x[li] = (double)(g & 1023) * 0.001;
        y[li] = (double)((g * 7) & 2047) * 0.002;
    }

    const double a = 1.4142135623730951;
    for (size_t li = 0; li < local; li++) {
        y[li] += a * x[li];
    }

    volatile double sink = local > 0 ? y[local / 2] : 0.0;
    printf(
        "daxpy_shard shard=%d/%d global_n=%zu local=%zu checksum=%.9f\n",
        shard_id,
        num_shards,
        n,
        local,
        sink);

    free(x);
    free(y);

#ifdef GEM5
    m5_exit(0);
#endif
    return 0;
}
