from django.contrib import admin
                         
from image.admins import ImageCoreAdmin
from news_article.models import NewsArticleImage                 
                                    
# Custom admin interface for administering an Image collection.
class NewsArticleImageAdmin(ImageCoreAdmin):
    pass
        
        
admin.site.register(NewsArticleImage, NewsArticleImageAdmin)
