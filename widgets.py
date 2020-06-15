from django.forms.widgets import FileInput
from django.forms.widgets import Media
 


class FileChooserDAndD(FileInput):
    # type name value and attrs printer
    template_name = 'image/widgets/file_drop.html'

    @property
    def media(self):
        return forms.Media(
                js=('image/js/file_drop.js',),
                css={'screen': ('image/css/file_drop.css',),}
            )
