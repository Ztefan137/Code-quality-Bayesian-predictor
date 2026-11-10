#include <iostream>
#include <vector>
#include <numeric>

/**
 * @brief Calculates the sum of a sequence where each element is multiplied by a factor.
 * 
 * @param limit The number of elements in the sequence.
 * @param multiplier The factor to multiply each element by.
 * @return The total computed sum as a 64-bit integer.
 */
long long calculateTotalSum(int limit, int multiplier) {
    std::vector<int> values(limit);
    
    for (int i = 0; i < limit; ++i) {
        values[i] = i * multiplier;
    }
    
    return std::accumulate(values.begin(), values.end(), 0LL);
}

/**
 * @brief Main entry point of the application.
 * @return int Exit status code.
 */
int main() {
    constexpr int limit = 100;
    constexpr int multiplier = 5;
    
    const long long totalSum = calculateTotalSum(limit, multiplier);
    
    std::cout << "Total Sum: " << totalSum << '\n';
    
    return 0;
}