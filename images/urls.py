from django.urls import path
from .views import upload_image, get_image, index

urlpatterns = [
    path('',index, name='index'),
    path('upload/', upload_image, name='upload_image'),
    path('image/<str:filename>/', get_image, name='get_image'),
]
