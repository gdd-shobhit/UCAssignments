#include <stdio.h>
#include <stdlib.h>

int main() {
    const size_t arrayLength = 64 * 1024 * 1024; // 64M integers (~256 MB) - larger to stress TLB
    int *dataArray = (int *)malloc(arrayLength * sizeof(int));

    // Initialize array
    for (size_t index = 0; index < arrayLength; ++index) {
        dataArray[index] = (int)index;
    }

    // generate cache traffic by walking the array. Basically doing a small amount of work to the array.
    long long sum = 0;
    for (size_t index = 0; index < arrayLength; ++index) {
        sum += dataArray[index];
    }

    // Keep the compiler from optimizing away the loop
    printf("Hello, gem5! sum = %lld\n", sum);

    free(dataArray);
    return 0;
}

