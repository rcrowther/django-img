import json

from django import forms
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

# 
class FileSingleChooserDAndD(forms.FileInput):
    # type name value and attrs printer
    template_name = 'image/widgets/file.html'
    #! needs_multipart_form = False
    #! could subwidget the file input?
    # @property
    # def media(self):
        # return forms.Media(
            # js=(
                # 'image/js/upload_dd.js',
                # ),
            # css={
                # 'screen': (
                    # 'image/css/widgets.css',
                # ),
            # },
        # )

    class Media:
            js=(
                'image/js/upload_dd.js',
                )
            css={
                'screen': (
                    'image/css/widgets.css',
                )
                    }
