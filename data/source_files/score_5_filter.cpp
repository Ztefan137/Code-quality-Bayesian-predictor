#include <iostream>

bool is_in_range(int value, int lower_bound, int upper_bound) {
    return value >= lower_bound && value <= upper_bound;
}

int sum_in_range(const int values[], int size, int lower_bound, int upper_bound) {
    int total = 0;
    for (int index = 0; index < size; ++index) {
        if (is_in_range(values[index], lower_bound, upper_bound)) {
            total += values[index];
        }
    }
    return total;
}

int main() {
    const int readings[] = {4, 8, 13, 17, 21, 25};
    const int first_allowed = 8;
    const int last_allowed = 21;

    // Sum only readings inside the inclusive range.
    const int result = sum_in_range(readings, 6, first_allowed, last_allowed);
    std::cout << "In-range total: " << result << '\n';
    return 0;
}
