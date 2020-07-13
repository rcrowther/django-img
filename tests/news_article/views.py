from django.views.generic import DetailView
from .models import NewsArticleImage

# For url.py:
# from news_article.views import NewsArticleImageDetailView
# path('newsimage/<int:pk>/', NewsArticleImageDetailView.as_view(), name='news-article-image-detail'),
class NewsArticleImageDetailView(DetailView):
    template_name='image/image_detail.html'
    model = NewsArticleImage
    context_object_name = 'image'
    

