from pathlib import Path
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import filesizeformat

from image import settings
from image.constants import (
    IMAGE_FORMATS,
    FORMAT_EXTENSIONS_APP,
    FORMAT_UCLIB_APP
)



def get_pillow_attribute(file, pil_attr):
    """
    Returns an attribute from a Pillow image of the given file,
    file
        a file. wrappable by Pillow. Must be open
    pil_attr
        the attribute to read.
    """
    # This devilish, ticketed code is lifted from 
    # django.core.files.images, where it seeks image dimensions.
    # Unfortunately, that code is not configurable nor overridable.
    from PIL import ImageFile as PillowImageFile

    p = PillowImageFile.Parser()
    file_pos = file.tell()
    file.seek(0)
    try:
        # Most of the time Pillow only needs a small chunk to parse the image
        # and get the dimensions, but with some TIFF files Pillow needs to
        # parse the whole file.
        chunk_size = 1024
        while 1:
            data = file.read(chunk_size)
            if not data:
                break
            try:
                p.feed(data)
            except zlib.error as e:
                # ignore zlib complaining on truncated stream, just feed more
                # data to parser (ticket #19457).
                if e.args[0].startswith("Error -5"):
                    pass
                else:
                    raise
            except struct.error:
                # Ignore PIL failing on a too short buffer when reads return
                # less bytes than expected. Skip and feed more data to the
                # parser (ticket #24544).
                pass
            except RuntimeError:
                # e.g. "RuntimeError: could not create decoder object" for
                # WebP files. A different chunk_size may work.
                pass
            if p.image:
                return getattr(p.image, pil_attr)
            chunk_size *= 2
        return (None, None)
    finally:
        file.seek(file_pos)
            
    
def validate_image_file_extension(file):
    '''
    Check the extension of an image file.
    Checks the extension against the internally defined set of file 
    extensions. Then does a Pillow read, to see what Pillow thinks,
    and compares the two.  So a bit more than Django's
    FileExtensionValidator.

    file
        a Django file class. The file must be open.    
    '''
    fp = Path(file.name)
    raw_extension = fp.suffix
    if (len(raw_extension) < 2):
        raise ValidationError(
            "File extension not found. allowed extensions: {}.".format(
                ", ".join(FORMAT_EXTENSIONS_APP.keys())
            ))
        
    extension = raw_extension[1:]
    if (not(extension in FORMAT_EXTENSIONS_APP)):
        raise ValidationError(
            "File extension {} not allowed. allowed extensions: {}.".format(
                raw_extension,
                ", ".join(IMAGE_FORMATS)
            ))
    declared_format = FORMAT_EXTENSIONS_APP[extension]
    
    pil_format = get_pillow_attribute(file.file, 'format')
    if (not(pil_format in FORMAT_UCLIB_APP)):
        raise ValidationError(
            "Not recognised as a {} image.".format(
                declared_format
            ))
    read_format = FORMAT_UCLIB_APP[pil_format]
            
    # Check the pil_format matches the read_format
    if (read_format != declared_format):
        raise ValidationError(
            "Not a valid {} image.".format(
                declared_format
            ))
        

def validate_file_size(max_upload_size, file):
    '''
    max_upload_size
        in bytes
    file
        a Django file class. The file must be open.
    '''
    # Don't try if no max upload size declared
    if not(max_upload_size):
        return

    # Check filesize
    if (file.size > max_upload_size):
        raise ValidationError(
            "This file is too big* ({}). Maximum filesize {}.".format(
                filesizeformat(file.size),
                filesizeformat(max_upload_size)
            ))
