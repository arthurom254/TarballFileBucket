from django.urls import path
from .views import ImageUploadView, GetImageView, index

urlpatterns = [
    path('',index, name='index'),
    path('upload/', ImageUploadView.as_view(), name='upload_image'),
    path('file/<str:filename>', GetImageView.as_view(), name='get_file'),
]