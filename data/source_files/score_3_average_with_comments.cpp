#include <iostream>

int count_matches(const int values[], int size, int target) {
    int matches = 0;
    for (int index = 0; index < size; ++index) {
        if (values[index] == target) {
            ++matches;
        }
    }
    return matches;
}

int main() {
    const int values[] = {2, 5, 2, 8, 2, 9};
    // Count how often the selected value appears.
    std::cout << count_matches(values, 6, 2) << '\n';
    return 0;
}
