from django.urls import path
from . import views

app_name = 'store   '
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('category/<slug:slug>/', views.HomeView.as_view(), name='category'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('bucket/', views.BucketHome.as_view(), name='bucket-home'),
    path('bucket/status/<str:task_id>/', views.BucketResult.as_view(), name='bucket-result'),
    path('delete-object/<str:key>/', views.DeleteBucketObject.as_view(), name='delete-bucket-object'),
    path('download-bucket-object/<str:key>/', views.DownloadBucketObject.as_view(), name='download-bucket-object'),
    path('update-bucket-object/<str:key>/', views.UpdateBucketObject.as_view(), name='update-bucket-object'),
]