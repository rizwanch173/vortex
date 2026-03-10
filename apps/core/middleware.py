from django.conf import settings
from django.shortcuts import render


class Custom404Middleware:
    """
    Force branded 404 template for unresolved routes.
    This keeps a user-friendly 404 page even when DEBUG=True.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Do not replace static/media 404 responses with HTML page.
        if response.status_code == 404:
            static_url = getattr(settings, "STATIC_URL", "/static/")
            media_url = getattr(settings, "MEDIA_URL", "/media/")
            if request.path.startswith(static_url) or request.path.startswith(media_url):
                return response
            return render(request, "404.html", status=404)

        return response
