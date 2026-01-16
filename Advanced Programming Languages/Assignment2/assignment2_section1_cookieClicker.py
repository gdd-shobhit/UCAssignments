# Based on cookie clicker game. Get cookies when you click.
def create_cookie_clicker():
    cookies = 0

    def click():
        nonlocal cookies
        cookies += 1
        return cookies

    return click


click_cookie = create_cookie_clicker()
print(click_cookie())
print(click_cookie())
print(click_cookie())