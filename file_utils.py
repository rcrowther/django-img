from image import settings
from pathlib import Path



def filename(path):
    '''
    Get the file name from a filepath.
    path must be a pathlib Path
    This calculates lengths. For example, the stock Django DB Filefield
    allows 100 chars path length. And Win32 operating systems can
    only handle 255 char path lengths. 
    @path a pathlib Path 
    '''

    name = path.stem
    if (not (image.settings.truncate_lengths)):
        return name
    # Truncate filename to prevent it going over 100 chars,
    # accounting for declared paths
    #! don't throw error, let other code handle?
    return path[-image.settings.path_length_limit:]
