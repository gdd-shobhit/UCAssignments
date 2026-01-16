#include <iostream>
using namespace std;

auto createCookieClicker() {
    int cookies = 0;
    return [cookies]() mutable {
        return ++cookies;
    };
}

int main() {
    auto clickCookie = createCookieClicker();
    cout << clickCookie() << endl;
    cout << clickCookie() << endl;
    cout << clickCookie() << endl;
}