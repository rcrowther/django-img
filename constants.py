# Definitive list of formats accepted, in the form used in the app.
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

# Map of file extensions -> format key
# allows uppercase
ALLOWED_FILE_EXTENSIONS = {**_FORMAT_FILE_EXTENSIONS_BASE, **_UPPER_EXTENSIONS}


# returns the Pillow format key for this apps keys.
# Will do for wand, too
# identify -list format
#? So call...? PilWan
FORMAT_APP_PILLOW = {
    'bmp' : 'BMP',
    'jpg' : 'JPEG',
    'png' : 'PNG',
    'gif' : 'GIF',
    'tiff': 'TIFF',
    'webp' : 'WEBP',
}

# returns this apps format key for a Pillow keys.
FORMAT_PILLOW_APP = {v:k for k,v in FORMAT_APP_PILLOW.items()}
