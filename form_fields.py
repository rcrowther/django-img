from django.forms.fields import ImageField
from django.core.exceptions import ValidationError


class FreeImageField(ImageField):
    '''
    A (form) Field that skips length verification.
    '''
    # This exists because verification is not configuarable.
    def to_python(self, data):
        if data in self.empty_values:
            return None

        # UploadedFile objects should have name and size attributes.
        try:
            file_name = data.name
            file_size = data.size
        except AttributeError:
            raise ValidationError(self.error_messages['invalid'], code='invalid')
        if not file_name:
            raise ValidationError(self.error_messages['invalid'], code='invalid')
        if not self.allow_empty_file and not file_size:
            raise ValidationError(self.error_messages['empty'], code='empty')

        return data
        
