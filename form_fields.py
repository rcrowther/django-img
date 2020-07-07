from django.forms.fields import FileField
from django.core.exceptions import ValidationError
from image import validators
from django.forms.widgets import FileInput


class FreePathImageField(FileField):
    '''
    A (form) Field that skips length verification.
    '''
    #NB I do't see why Imagefield thinks to_python() is the place to
    # do validation. Maybe I'm missing something, but ugty, 
    # and stripped out. 
    # The other  and better reason for this existing is to get the 
    # validaors out into the forms fields, where Django feels they 
    # belong.
    default_validators = [validators.validate_image_file_consistency]

    def __init__(self, *, max_size=None, **kwargs):
        self.max_size = max_size
        super().__init__(**kwargs)
        
    def to_python(self, data):
        """
        Check that the file-upload field data contains a valid image (GIF, JPG,
        PNG, etc. -- whatever Pillow supports).
        """
        f = super().to_python(data)
        if f is None:
            return None
        if hasattr(f, 'seek') and callable(f.seek):
            f.seek(0)
        return f

    def validate(self, value):
        super().validate(value)
        if (self.max_size):
            validators.validate_file_size(value, self.max_size)

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        if isinstance(widget, FileInput) and 'accept' not in widget.attrs:
            attrs.setdefault('accept', 'image/*')
        return attrs
