#include <iostream>
using namespace std;

int main() {
    int* numbers = new int[5]; // heap allocation
    
    for (int i = 1; i <= 5; ++i) 
    {
        numbers[i - 1] = i;
    }

    int sum = 0;
    for (int i = 0; i < 5; ++i) 
    {
        sum += numbers[i];
    }

    cout << "Sum: " << sum << endl;

    delete[] numbers; // have to manually let go off memory
    numbers = nullptr; // and then make sure pointer isnt a dangling pointer
}
