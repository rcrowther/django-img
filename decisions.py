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
    if (settings.auto_delete):
        delete = True

    #,,,but Model wins.
    if not(image.auto_delete == image.DELETE_UNSET):
        delete = image.is_auto_delete()
            
    return delete



 #! DRY these two   
def image_save_path(filename):
    '''
    Get the save path from a source filepath.
    This calculates and truncates lengths. For example, the stock 
    Django DB Filefield allows 100 chars path length. And Win32 
    operating systems can only handle 255 char path lengths. 
    @path a pathlib Path 
    '''
    # Starts with a filename, needs a path relative to /media.
    p = Path(filename)
    
    # This needs maybe truncation
    # do a unidecode in the filename and then replace non-ascii 
    # characters in filename with _ , to sidestep issues with filesystem encoding
    safer_stem = "".join((i if ord(i) < 128 else '_') for i in unidecode(p.stem))
        
    if (settings.reforms.truncate_paths):
        # truncate filename to prevent path going over 100 chars,
        # accounting for declared paths and filename extensions
        # https://code.djangoproject.com/ticket/9893
        # must allow 2 for joining chars
        stem_limit = 100 - 2 - settings.filepath_maxlen - len(p.suffix)    
        safer_stem = safer_stem[:stem_limit]
        
    # This needs the /media relative path building.
    return os.path.join(settings.media_subpath_originals, safer_stem) + p.suffix
    
    
def reform_save_path(filename):
    p = Path(filename)
    
    # Starts with a filename, needs a path relative to /media.
    safe_stem = p.stem

    # Need to truncate on a reform. It has a  filter id appended,
    # an maye a new extension.
    if (settings.reforms.truncate_paths):
        limit = 100 - 2 - len(settings.media_subpath_reforms) - len(p.suffix)
        safe_stem = safe_stem[:limit]        

    # This needs the /media relative path building.
    return os.path.join(settings.media_subpath_reforms, safe_stem) + p.suffix

