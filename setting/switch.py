from django.utils.deprecation import MiddlewareMixin
from .models import SiteSwitch
from django.http import HttpResponse


class SwitchMiddleware(MiddlewareMixin):
    def process_request(self, request):
        s = SiteSwitch.objects.first()
        if s:
            if s.is_enabled or request.path.startswith("/settings"):
                pass
            else:
                return HttpResponse("Oops!! Something Went Wrong! ")

    def process_response(self, request, response):
        # Log the outgoing response
        print("Outgoing Response:", response.status_code)
        return response
