/*
 * Multi-threaded double-precision daxpy: y <- a*x + y
 * Usage: daxpy_mt <num_threads> <n>
 *   num_threads: pthread worker count (use same as gem5 --num-cpus for 1:1)
 *   n: number of elements in each vector (x and y are length n)
 *
 * gem5 SE mode: pthread_create is often unsupported (clone/futex gaps).
 * For num_threads==1 we run the worker inline so single-core sims work.
 * For num_threads>1, pthreads may still fail depending on your gem5 build;
 * if so, use only --threads 1 for baseline IPC or use SHARDS.
 */

#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef GEM5
#include <gem5/m5ops.h>
#endif

typedef struct {
    int tid;
    int nthreads;
    size_t n;
    double a;
    const double *x;
    double *y;
} WorkerArgs;

static void *
daxpy_worker(void *arg)
{
    WorkerArgs *w = (WorkerArgs *)arg;
    size_t chunk = (w->n + (size_t)w->nthreads - 1) / (size_t)w->nthreads;
    size_t start = (size_t)w->tid * chunk;
    size_t end = start + chunk;
    if (end > w->n) {
        end = w->n;
    }

    const double a = w->a;
    const double *x = w->x;
    double *y = w->y;
    for (size_t i = start; i < end; i++) {
        y[i] += a * x[i];
    }
    return NULL;
}

int
main(int argc, char **argv)
{
    int nthreads = 1;
    size_t n = 262144;

    if (argc >= 2) {
        nthreads = atoi(argv[1]);
        if (nthreads < 1) {
            fprintf(stderr, "num_threads must be >= 1\n");
            return 1;
        }
    }
    if (argc >= 3) {
        n = (size_t)strtoull(argv[2], NULL, 10);
        if (n == 0) {
            fprintf(stderr, "n must be > 0\n");
            return 1;
        }
    }

    double *x = (double *)malloc(n * sizeof(double));
    double *y = (double *)malloc(n * sizeof(double));
    if (!x || !y) {
        fprintf(stderr, "allocation failed\n");
        free(x);
        free(y);
        return 1;
    }

    for (size_t i = 0; i < n; i++) {
        x[i] = (double)(i & 1023) * 0.001;
        y[i] = (double)((i * 7) & 2047) * 0.002;
    }

    const double a = 1.4142135623730951;
    pthread_t *threads = (pthread_t *)malloc((size_t)nthreads * sizeof(pthread_t));
    WorkerArgs *args = (WorkerArgs *)malloc((size_t)nthreads * sizeof(WorkerArgs));
    if (!threads || !args) {
        fprintf(stderr, "allocation failed\n");
        free(threads);
        free(args);
        free(x);
        free(y);
        return 1;
    }

    if (nthreads == 1) {
        args[0].tid = 0;
        args[0].nthreads = 1;
        args[0].n = n;
        args[0].a = a;
        args[0].x = x;
        args[0].y = y;
        daxpy_worker(&args[0]);
    } else {
        for (int t = 0; t < nthreads; t++) {
            args[t].tid = t;
            args[t].nthreads = nthreads;
            args[t].n = n;
            args[t].a = a;
            args[t].x = x;
            args[t].y = y;
            if (pthread_create(&threads[t], NULL, daxpy_worker, &args[t]) !=
                0) {
                fprintf(stderr, "pthread_create failed\n");
                free(threads);
                free(args);
                free(x);
                free(y);
                return 1;
            }
        }

        for (int t = 0; t < nthreads; t++) {
            pthread_join(threads[t], NULL);
        }
    }

    /* Touch one element so the compiler cannot delete the loop. */
    volatile double sink = y[n / 2];
    printf("daxpy_mt threads=%d n=%zu checksum=%.9f\n", nthreads, n, sink);

    free(threads);
    free(args);
    free(x);
    free(y);

#ifdef GEM5
    m5_exit(0);
#endif
    return 0;
}
