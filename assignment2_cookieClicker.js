function createCookieClicker() {
    let cookies = 0;

    return function () {
        cookies++;
        return cookies;
    };
}

const clickCookie = createCookieClicker();
console.log(clickCookie());
console.log(clickCookie());
console.log(clickCookie());