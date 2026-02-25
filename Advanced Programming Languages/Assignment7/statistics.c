#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int compare_int(const void *a, const void *b)
{
    int x = *(const int *)a;
    int y = *(const int *)b;
    return (x > y) - (x < y);
}

double mean(const int *arr, size_t n)
{
    if (n == 0)
        return 0.0;
    long sum = 0;
    for (size_t i = 0; i < n; i++)
        sum += arr[i];
    return (double)sum / (double)n;
}

double median(int *arr, size_t n)
{
    if (n == 0)
        return 0.0;
    int *copy = (int *)malloc(n * sizeof(int));
    if (!copy)
        return 0.0;
    memcpy(copy, arr, n * sizeof(int));
    qsort(copy, n, sizeof(int), compare_int);
    double result;
    if (n % 2 == 1)
        result = (double)copy[n / 2];
    else
        result = ((double)copy[n / 2 - 1] + (double)copy[n / 2]) / 2.0;
    free(copy);
    return result;
}

/*
 * Returns one mode (smallest value if tie). Counts by sorting and scanning runs.
 */
int mode(const int *arr, size_t n)
{
    if (n == 0)
        return 0;
    int *copy = (int *)malloc(n * sizeof(int));
    if (!copy)
        return arr[0];
    memcpy(copy, arr, n * sizeof(int));
    qsort(copy, n, sizeof(int), compare_int);

    int best_value = copy[0];
    int best_count = 1;
    int run_value = copy[0];
    int run_count = 1;

    for (size_t i = 1; i < n; i++)
    {
        if (copy[i] == run_value)
            run_count++;
        else
        {
            if (run_count > best_count)
            {
                best_count = run_count;
                best_value = run_value;
            }
            run_value = copy[i];
            run_count = 1;
        }
    }
    if (run_count > best_count)
        best_value = run_value;

    free(copy);
    return best_value;
}

int main(void)
{
    int data[] = {4, 2, 3, 2, 5, 2, 4};
    size_t n = sizeof(data) / sizeof(data[0]);

    printf("Data: ");
    for (size_t i = 0; i < n; i++)
        printf("%d ", data[i]);
    printf("\n");

    printf("Mean: %.2f\n", mean(data, n));
    printf("Median: %.2f\n", median(data, n));
    printf("Mode: %d\n", mode(data, n));
    
    int exit;
    scanf_s("%d", &exit);
    return 0;
}
