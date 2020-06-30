from django.db import models
from image.models import AbstractImage, AbstractReform
from django.utils.translation import gettext_lazy as _



class NewsArticleImage(AbstractImage):
    reform_model = 'NewsArticleReform'
    upload_dir='news_originals'
    filepath_length=100
    auto_delete_files=True

    # AbstractImage has a file and upload_date
    caption = models.CharField(_('Caption'),
        max_length=255,
    )

    author = models.CharField(_('Author'),
        max_length=255,
        db_index=True
    )


    #class Meta:
        # This model is not managed by Django
        #managed = False
        #db_table = 'image_newsarticleimage'




class NewsArticleReform(AbstractReform):
    image_model=NewsArticleImage
    upload_dir='news_reforms'


    #class Meta:
        # This model is not managed by Django
        #managed = False
        #db_table = 'image_newsarticlereform'
