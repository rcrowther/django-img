from django.utils.functional import cached_property

'''
Formats accepted.
This list is used throughout the app, and is definitive. The entries can
be used for new file extensions. However, for verification and other 
code, other collections in this module are preferred. The main use in 
code is for displaying nice messages for the user. 
'''
IMAGE_FORMATS = [
    'bmp',
    'jpg',
    'png',
    'gif',
    'tiff',
    'webp',
]

def extensions_maxlen():
    '''
    max length of listed extensions, including the period.
    eg '.tiff' returns 5
    '''
    m = 0
    for f in IMAGE_FORMATS:
        l = len(f)
        if (l > m):
            m = l
    # for the period i.e '.png' is 4
    m += 1
    return m
    
# Map possible (lowercase) file extensions -> internal format
_FORMAT_FILE_EXTENSIONS_BASE = {
    'bmp' : 'bmp',
    'jpg' : 'jpg',
    'jpeg' : 'jpg',
    'png' : 'png',
    'gif' : 'gif',
    'tiff': 'tiff',
    'webp' : 'webp',
}

_UPPER_EXTENSIONS = {k.upper():v for k,v in _FORMAT_FILE_EXTENSIONS_BASE.items()}

'''
Map of allowed file extensions -> format key
Includes upper and lower case entries, and variations in spelling 
e.g. 'jpg'/'jpeg'
'''
# NB: see the extension strip list in prepopulate.js
FORMAT_EXTENSIONS_APP = {**_FORMAT_FILE_EXTENSIONS_BASE, **_UPPER_EXTENSIONS}

'''
Map of uppercase format keys -> app formats.
This map will work for Pillow and Wand libraries.
'''
FORMAT_UCLIB_APP = {
    'BMP' : 'bmp',
    'JPEG' : 'jpg',
    'JPG' : 'jpg',
    'MPO' : 'jpg',
    'PNG' : 'png',
    'GIF' : 'gif',
    'TIFF' : 'tiff',
    'WEBP' : 'webp',
}

'''
Map of app formats -> uppercase format keys.
This map will work for Pillow and Wand libraries.
'''
FORMAT_APP_UCLIB = {v:k for k,v in FORMAT_UCLIB_APP.items()}



