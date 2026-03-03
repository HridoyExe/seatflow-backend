from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

@api_view(['GET'])
def api_root_view(request, format=None):
    return Response({
        'menu-categories': reverse('category-list', request=request, format=format),
        'menu-items': reverse('menuitem-list', request=request, format=format),
        'seats': reverse('seat-list', request=request, format=format),
        'bookings': reverse('booking-list', request=request, format=format),
    })