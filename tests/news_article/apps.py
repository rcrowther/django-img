from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from image.signals import register_file_delete_handler



class NewsArticleConfig(AppConfig):
    name = 'news_article'
    verbose_name = _("News article")
    
    def ready(self):
        super().ready()
        from news_article.models import NewsArticleImage, NewsArticleReform
        register_file_delete_handler(NewsArticleImage, NewsArticleReform)
