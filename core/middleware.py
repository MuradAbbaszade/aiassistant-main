from django.conf import settings

from businesses.models import Business


class CurrentBusinessMiddleware:
    """Expose current_business on request from session / user profile."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        business_id = request.session.get("current_business_id") or getattr(
            settings, "DEFAULT_BUSINESS_ID", ""
        )
        business = Business.objects.filter(pk=business_id).first() if business_id else None

        if business is None and getattr(request, "user", None) and request.user.is_authenticated:
            profile = getattr(request.user, "profile", None)
            if profile and profile.business_id:
                business = profile.business
                request.session["current_business_id"] = business.pk

        request.current_business = business
        request.current_business_id = business.pk if business else None
        return self.get_response(request)
