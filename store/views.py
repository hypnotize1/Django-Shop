from celery.result import AsyncResult
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.conf import settings
from django.views.generic import TemplateView, DetailView
from .models import Category, Product, Brand
from .tasks import bucket_objects_task, delete_object_task, download_object_task, update_object_task
from utils import IsUserAdminMixin
import os

# Create your views here.

class HomeView(TemplateView):
    template_name = 'store/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)    
        context['products'] = Product.objects.filter(available=True)
        context['categories'] = Category.objects.all()
        context['brands'] = Brand.objects.all()
        return context
    

class ProductDetailView(DetailView):
    model = Product
    template_name = 'store/product_detail.html'     
    context_object_name = 'product'
  
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        context['variants'] = product.variants.all()
        context['images'] = product.images.all()
        context['tags'] = product.tags.all()
        context['reviews'] = product.reviews.filter(approved=True)
        return context

class BucketHome(IsUserAdminMixin, View):
    def get(self, request, *args, **kwargs):
        task = bucket_objects_task.delay()
        return redirect('store:bucket-result', task_id=task.id)


class BucketResult(IsUserAdminMixin, View):
    template_name = 'store/bucket_result.html'

    def get(self, request, *args, **kwargs):
        result = AsyncResult(kwargs['task_id'])

        if result.ready():
            objs = result.result
            return render(request, self.template_name, {'objs': objs})
        else:
            return render(request, self.template_name, {'pending':True, 'task_id': kwargs['task_id']})


class DeleteBucketObject(IsUserAdminMixin, View):
    def get(self, request, key):
        delete_object_task.delay(key)
        messages.success(request, 'Successfully deleted.', 'info')
        return redirect('store:bucket-home')
    

class DownloadBucketObject(IsUserAdminMixin, View):
    def get(self, request, key):
        download_object_task.delay(key)
        messages.success(request, 'Successfully downloaded.', 'info')
        return redirect('store:bucket-home')
    
    
class UpdateBucketObject(IsUserAdminMixin, View):

    template_name = 'store/bucket_update.html'
    def get(self, request, key):
        return render(request, self.template_name, {'key': key})
    
    def post(self, request, key):
        file = request.FILES.get('file')
        if file:
            local_path = os.path.join(settings.AWS_LOCAL_STORAGE, file.name)
            with open(local_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            update_object_task.delay(key, local_path)
            messages.success(request, 'Successfully updated.', 'info')
        else:
            messages.error(request, 'No file provided for update.', 'error')
        return redirect('store:bucket-home')
