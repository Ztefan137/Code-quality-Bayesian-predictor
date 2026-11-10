/**
 * @file sample_01.cpp
 * @brief A sample C++ file to test code cleanliness metrics.
 */

#include <iostream>

// Function to calculate factorial with branching and loops
int calculateFactorial(int n) {
    const int baseCase = 1;
    
    // Conditionals add to cyclomatic complexity
    if (n <= 1) {
        return baseCase;
    }
    
    int result = 1;
    for (int i = 2; i <= n; ++i) {
        result = result * i;
    }
    
    return result;
}

int main() {
    const int limit = 5;
    int output = calculateFactorial(limit);
    
    std::cout << "Factorial result: " << output << std::endl;
    return 0;
}