#include <iostream>

struct Measurement {
    int total;
    int count;
};

Measurement collect_measurements(const int values[], int size) {
    Measurement result{0, 0};
    for (int index = 0; index < size; ++index) {
        result.total += values[index];
        ++result.count;
    }
    return result;
}

int main() {
    const int measurements[] = {12, 15, 11, 18};
    const Measurement result = collect_measurements(measurements, 4);
    if (result.count == 0) {
        std::cout << "No measurements\n";
        return 0;
    }

    std::cout << "Average: " << result.total / result.count << '\n';
    return 0;
}
