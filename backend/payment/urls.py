from django.urls import path
from .views import PaymentCalculationView, PaymentProgressView


urlpatterns = [
    path('calculate/',
         PaymentCalculationView.as_view(),
         name='payment-calculate'
         ),
    path('progress/<str:task_id>/',
         PaymentProgressView.as_view(),
         name='payment-progress'
         ),
]
