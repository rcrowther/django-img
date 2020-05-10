'''
Formats accepted.
This list is used throughout the app, and is definitive.
The entries can be used for new file extensions.
'''
IMAGE_FORMATS = [
    'bmp',
    'jpg',
    'png',
    'gif',
    'tiff',
    'webp',
]

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
ALLOWED_FILE_EXTENSIONS = {**_FORMAT_FILE_EXTENSIONS_BASE, **_UPPER_EXTENSIONS}


'''Map of app formats -> uppercase format keys.
This map will work for both Pillow and Wand libraries.
'''
FORMAT_APP_UCLIB = {
    'bmp' : 'BMP',
    'jpg' : 'JPEG',
    'png' : 'PNG',
    'gif' : 'GIF',
    'tiff': 'TIFF',
    'webp' : 'WEBP',
}


'''
Map of uppercase format keys -> app formats.
This map will work for both Pillow and Wand libraries.
'''
FORMAT_UCLIB_APP = {v:k for k,v in FORMAT_APP_UCLIB.items()}
