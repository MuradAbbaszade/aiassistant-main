from functools import wraps

from django.shortcuts import redirect


def demo_login_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.session.get("demo_logged_in"):
            return redirect("accounts:login")
        return view_func(request, *args, **kwargs)

    return _wrapped
