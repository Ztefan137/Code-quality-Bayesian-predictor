#include <iostream>

int main() {
    int values[] = {3, 8, 12, 5, 9, 2};
    int result = 0;

    for (int i = 0; i < 6; ++i) {
        if (values[i] > 4) {
            if (values[i] < 10) {
                result += values[i];
            } else {
                result += 2;
            }
        } else {
            result -= 1;
        }
    }

    std::cout << result << '\n';
    return 0;
}
