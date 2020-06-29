from django.db import models
from image.models import AbstractImage, AbstractReform
from django.utils.translation import gettext_lazy as _



class ImageTestImage(AbstractImage):
    upload_dir='image_test_originals'
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


    class Meta:
        # This model is not managed by Django
        managed = False




class ImageTestReform(AbstractReform):
    image_model=ImageTestImage
    upload_dir='image_test_reforms'
    filepath_length=100


    class Meta:
        # This model is not managed by Django
        managed = False
