from django.urls import path
from .views import BucketHome,BucketResult, DeleteBucketObject, DownloadBucketObject, UpdateBucketObject

urlpatterns = [
    # home
    # single post 
    # path('category/<slug:slug>/', HomeView.as_view(), name='category'),
    path('bucket/', BucketHome.as_view(), name='bucket-home'),
    path('bucket/status/<str:task_id>/', BucketResult.as_view(), name='bucket-Result'),
    path('delete-object/<str:key>/', DeleteBucketObject.as_view(), name='delete-bucket- object'),
    path('download-bucket-object/<str:key>/', DownloadBucketObject.as_view(), name='download-bucket-object'),
    path('update-bucket-object/<str:key>/', UpdateBucketObject.as_view(), name='update-bucket-object'),
]
