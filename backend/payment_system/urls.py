from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('api/', include('api.urls')),
    path('payment/', include('payment.urls')),
    path('admin/', admin.site.urls),
]
