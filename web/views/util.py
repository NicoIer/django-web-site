from web.models import User


def _login_cookie_session(request, response, user: User, max_age: int = 3600 * 24):
    # session会默认加密
    request.session['uid'] = user.id
    request.session['username'] = user.username
    response.set_cookie('uid', user.id, max_age=max_age)
    response.set_cookie('username', user.username, max_age=max_age)
    return response
