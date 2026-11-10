#include <iostream>

int main() {
    int limit = 20;
    int count = 0;
    int sum = 0;
    for (int number = 1; number <= limit; number++) {
        if (number % 3 == 0) {
            sum = sum + number;
            count++;
        }
    }
    if (count > 0) {
        std::cout << sum / count << '\n';
    }
    return 0;
}
