from django.conf import settings
from django.shortcuts import render


def index(request):
    return render(
        request,
        "dataspace/index.html",
        {
            "active_navbar_page": "data_space",
            "show_sidebar": True,
            "gateway_url": settings.DATASPACE_GATEWAY_URL,
        },
    )
