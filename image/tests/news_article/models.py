from django.db import models
from image.models import AbstractImage, AbstractReform
from django.utils.translation import gettext_lazy as _



class NewsArticleImage(AbstractImage):
    reform_model = 'NewsArticleReform'
    upload_dir='news_originals'
    accept_formats = ['png']
    filepath_length=55
    max_upload_size=2
    form_limit_filepath_length=True
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
    jpeg_quality=28

    image = models.ForeignKey(image_model, related_name='+', on_delete=models.CASCADE)

    #class Meta:
        # This model is not managed by Django
        #managed = False
        #db_table = 'image_newsarticlereform'
