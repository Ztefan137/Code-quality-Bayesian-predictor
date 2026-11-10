#include <iostream>

struct Summary {
    int total;
    int positive_count;
};

Summary summarize(const int values[], int size) {
    Summary summary{0, 0};
    for (int index = 0; index < size; ++index) {
        summary.total += values[index];
        if (values[index] > 0) {
            ++summary.positive_count;
        }
    }
    return summary;
}

int main() {
    const int readings[] = {-3, 4, 7, 0, 2};
    const Summary result = summarize(readings, 5);
    std::cout << result.total << ' ' << result.positive_count << '\n';
    return 0;
}
