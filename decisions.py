from pathlib import Path
from unidecode import unidecode
import os.path
from django.utils.functional import cached_property

from image.settings import settings
from image.constants import extensions_maxlen

print('decisions')

# methods that negociate with calling opinions and settings to decide
# or gain info for actions.
# These pieces of code do not sit happily in their associated objects,
# with external dependencies. Besides, they are also relatives of user 
# parameters and settings. So they are here. 



def reform_save_info(ifilter, src_format):
    '''
    Gather and choose between configs about how to save filter results.
    Probes into several settings. If present, settings file wins, 
    filter config wins, discovered state. 

    ifilter 
        instance of a Filter
    '''
    # defaults
    iformat = src_format
    jpeg_quality = settings.reforms.jpeg_quality
    
    # Overrides of output format. Settings first...
    if (settings.reforms.format_override):
        iformat = settings.reforms.format_override

    #,,,but Filter wins.
    if hasattr(ifilter, 'format') and ifilter.format:
        iformat = ifilter.format

    if iformat == 'jpg':
        # Overrides of JPEG compression quality. Filter wins.
        if hasattr(ifilter, 'jpeg_quality') and ifilter.jpeg_quality:
            jpeg_quality = ifilter.jpeg_quality
    return {'format': iformat, 'jpeg_quality': jpeg_quality}

def src_should_delete(image, calling_opinion):
    delete = calling_opinion
    
    # Settings can override...
    if (not(settings.auto_delete is None)):
        delete = settings.auto_delete

    #,,,but Model wins.
    if (image.auto_delete != image.AutoDelete.UNSET):
        delete = (image.auto_delete == image.AutoDelete.YES)
    return delete

# def media_path_originals(upload_to_dir):
    # '''
    # Relative path to the image directory.
    # For original image uploads.
    # '''
    # # Settings has a say...
    # media_path = settings.media_subpath_originals
    
    # #,,,but model definition wins.
    # if (upload_to_dir):
        # media_path = upload_to_dir
    # return media_path
    
# def media_path_reforms(upload_to_dir):
    # '''
    # Relative path to the reform directory.
    # For original reform creates.
    # '''
    # # Settings has a say...
    # media_path = settings.media_subpath_reforms
    
    # #,,,but model definition wins.
    # if (upload_to_dir):
        # media_path = upload_to_dir
    # return media_path    
    
def filename_originals_maxlen(field_file, media_path):
    '''
    Length the settings will allow for filenames.
    '''
    truncate_len = field_file.field.max_length
    full_path = field_file.storage.path(media_path)
    
    # -1 for a connector
    return truncate_len - len(str(full_path)) - 1

def filename_reforms_maxlen(field_file, media_path):
    '''
    Length the settings will allow for filenames.
    '''
    truncate_len = field_file.field.max_length
    full_path = field_file.storage.path(media_path)
    # -1 for a connector
    return truncate_len - len(str(full_path)) - 1
    
#@property
# def file_path_originals(self, upload_to_dir):
    # '''
    # Full path to the image directory.
    # For original image uploads. Note this can be a longish absolute
    # path from server root.
    # '''
    # # Settings has a say...
    # media_path = settings.media_subpath_originals
    
    # #,,,but model definition wins.
    # if (upload_to_dir,):
        # media_path = upload_to_dir
    # return Path(settings.media_root) / media_path
        
from os import path
def image_save_path(obj, filename):
    '''
    Get the save path from a source filepath.
    This calculates and truncates lengths. For example, the stock 
    Django DB Filefield allows 100 chars path length. And Win32 
    operating systems can only handle 255 char path lengths. 
    
    filename
        any kind of stringlike filename or path. Should have an extension. 
    '''
    # Info from field: length limit, mangling and path-build utilities
    field_file = obj.src
        
    # Which media path?
    #media_path = media_path_originals(obj.upload_to_dir)
    media_path = obj.upload_to_dir
            
    #! do these two replicate functionality?
    # Quote:
    # Return the given string converted to a string that can be used for a clean
    # filename. Remove leading and trailing spaces; convert other spaces to
    # underscores; and remove anything that is not an alphanumeric, dash,
    # underscore, or dot.
    p = Path(field_file.field.storage.get_valid_name(filename))

    # Unidecode in the filename then replace non-ascii 
    # characters in filename with _ , to sidestep issues with filesystem encoding
    decoded_stem = "".join((i if ord(i) < 128 else '_') for i in unidecode(p.stem))  

    # make the end-tag
    tag = p.suffix
    
    # Find maxlen for the filename, then truncate
    # accounting for declared paths and filename extensions
    # https://code.djangoproject.com/ticket/9893
    stem_limit = filename_originals_maxlen(field_file,  media_path) - len(tag)
    stem = decoded_stem[:stem_limit]

    # return the /media relative path.
    return path.join(media_path, stem + tag)
    
def reform_save_path(obj, filename):
    '''
    Get the save path from a source filepath.
    This calculates and truncates lengths. For example, the stock 
    Django DB Filefield allows 100 chars path length. And Win32 
    operating systems can only handle 255 char path lengths. 
    
    filename
        any kind of stringlike filename or path. Should have an extension. 
    '''
    # Info from field: length limit, mangling and path-build utilities
    field_file = obj.src

    # Which media path?
    #media_path = media_path_reforms(obj.upload_to_dir)
    media_path = obj.upload_to_dir
    
    # Reform is internal, so we have an internal representation of
    # filename already
    p = Path(filename)
        
    src_stem = p.stem
    
    # filterid is a dotted path
    # It will be added to the reform file path, so make it url-like.
    # We loose a little of the id by converting, but the file saving
    # gear will mangle if there is a clash, so rename affects 
    # no basic functionality. 
    filter_id = obj.filter_id.lower().replace('.', '_')

    # make the end-tag
    # e.g. tag = "-image_thumb.png"
    tag = '-' + filter_id + p.suffix

    # Find maxlen for the filename, then truncate
    # accounting for declared paths and filename extensions
    # https://code.djangoproject.com/ticket/9893
    stem_limit = filename_reforms_maxlen(field_file, media_path) - len(tag)
    stem = src_stem[:stem_limit]        

    # return the /media relative path.
    return path.join(media_path, stem + tag)

