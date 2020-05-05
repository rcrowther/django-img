from image.settings import settings
from pathlib import Path
from unidecode import unidecode



def filename(path):
    '''
    Get the file name from a filepath.
    This calculates and truncates lengths. For example, the stock 
    Django DB Filefield allows 100 chars path length. And Win32 
    operating systems can only handle 255 char path lengths. 
    @path a pathlib Path 
    '''
    name = path.stem
        
    # do a unidecode in the filename and then replace non-ascii 
    # characters in filename with _ , to sidestep issues with filesystem encoding
    safer_name = "".join((i if ord(i) < 128 else '_') for i in unidecode(name))
        
    if (not (settings.truncate_paths)):
        return safer_name
        
    
    # truncate filename to prevent it going over 100 chars,
    # accounting for declared paths
    # https://code.djangoproject.com/ticket/9893
    #!? don't throw error, let other code handle?
    return safer_name[:settings.path_length_limit]
