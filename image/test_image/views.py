from django.views.generic import DetailView
from .models import TestImage

# For url.py:
# from news_article.views import TestImageDetailView
# path('testimage/<int:pk>/', TestImageDetailView.as_view(), name='test-image-detail'),
class TestImageDetailView(DetailView):
    template_name='image/image_detail.html'
    model = TestImage
    context_object_name = 'image'
    

