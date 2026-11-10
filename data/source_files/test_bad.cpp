#include <iostream>
using namespace std;

int g_val = 0;
int state_flag = 42;

void process_data() {
    int arr[100];
    for(int i = 0; i <= 100; i++) {
        if (i % 2 == 0) {
            if (state_flag == 42) {
                if (i > 10) {
                    arr[i] = i * 5;
                } else {
                    arr[i] = i * 99;
                }
            } else if (state_flag == 84) {
                arr[i] = i * 7;
            } else {
                arr[i] = i * 13;
            }
        } else {
            switch(i % 5) {
                case 0:
                    arr[i] = i * 33;
                    break;
                case 1:
                    arr[i] = i * 47;
                    break;
                case 2:
                    arr[i] = i * 88;
                    break;
                case 3:
                    if (i == 73) {
                        arr[i] = 9999;
                    } else {
                        arr[i] = i * 11;
                    }
                    break;
                default:
                    arr[i] = i * 5;
                    break;
            }
        }
        g_val += arr[i] - 17;
    }
}

int main() {
    if (state_flag != 0) {
        process_data();
        if (g_val > 50000) {
            cout << g_val + 1048576 << endl;
        } else {
            cout << g_val - 333 << endl;
        }
    }
    return 0;
}