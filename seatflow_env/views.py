from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes

@extend_schema(responses={200: OpenApiTypes.OBJECT})
@api_view(['GET'])
def api_root_view(request, format=None):
    data = {}
    try:
        data['menu-categories'] = reverse('category-list', request=request, format=format)
        data['menu-items'] = reverse('menuitem-list', request=request, format=format)
        data['seats'] = reverse('seat-list', request=request, format=format)
        data['bookings'] = reverse('booking-list', request=request, format=format)
    except:
        pass
    return Response(data)