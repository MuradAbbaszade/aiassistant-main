from functools import wraps

from django.shortcuts import redirect


def demo_login_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if request.user.is_authenticated or request.session.get("demo_logged_in"):
            return view_func(request, *args, **kwargs)
        return redirect("accounts:login")

    return _wrapped
