#include <iostream>

int sum_positive(const int values[], int size) {
    int sum = 0;
    for (int index = 0; index < size; ++index) {
        if (values[index] > 0) {
            sum += values[index];
        }
    }
    return sum;
}

int main() {
    int values[] = {-2, 4, 7, -1, 3};
    std::cout << sum_positive(values, 5) << '\n';
    return 0;
}
