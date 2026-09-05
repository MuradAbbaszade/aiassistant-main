from django.conf import settings

from businesses.models import Business


class CurrentBusinessMiddleware:
    """Expose current_business on request from session (multi-tenant)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        business_id = request.session.get("current_business_id") or getattr(
            settings, "DEFAULT_BUSINESS_ID", ""
        )
        business = Business.objects.filter(pk=business_id).first() if business_id else None
        if business is None and request.session.get("demo_logged_in"):
            # Fall back to first available tenant for this session
            business = Business.objects.first()
            if business is not None:
                request.session["current_business_id"] = business.pk
        request.current_business = business
        request.current_business_id = business.pk if business else None
        return self.get_response(request)
