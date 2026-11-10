#include <iostream>

int find_first(const int values[], int size, int target) {
    for (int index = 0; index < size; ++index) {
        if (values[index] == target) {
            return index;
        }
    }
    return -1;
}

int main() {
    const int values[] = {11, 6, 14, 3, 8};
    const int target = 14;
    const int position = find_first(values, 5, target);
    if (position >= 0) {
        std::cout << "Found at " << position << '\n';
    } else {
        std::cout << "Not found\n";
    }
    return 0;
}
