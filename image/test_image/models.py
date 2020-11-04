from django.db import models
from image.models import AbstractImage, AbstractReform
from django.utils.translation import gettext_lazy as _



class TestImage(AbstractImage):
    reform_model = 'TestReform'
    upload_dir='test_originals'
    accept_formats = ['png']
    filepath_length=55
    max_upload_size=2
    form_limit_filepath_length=True
    auto_delete_files=True



class TestReform(AbstractReform):
    image_model=TestImage
    upload_dir='test_reforms'
    jpeg_quality=28

    image = models.ForeignKey(image_model, related_name='+', on_delete=models.CASCADE)

