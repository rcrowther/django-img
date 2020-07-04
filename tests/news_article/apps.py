from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

#'news_article.apps.NewsArticleConfig',
class NewsArticleConfig(AppConfig):
    name = 'news_article'
    verbose_name = _("News article")
