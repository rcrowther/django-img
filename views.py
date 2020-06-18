from django.views.generic import DetailView
from .models import Image



class ImageDetailView(DetailView):
    model = Image
    context_object_name = 'image'
    

