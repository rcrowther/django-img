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
    
# File extension “ogg” is not allowed. Allowed extensions are: bmp, dib, gif, tif, tiff, 
# jfif, jpe, jpg, jpeg, pbm, pgm, ppm, pnm, png, apng, blp, bufr, cur, 
# pcx, dcx, dds, ps, eps, fit, fits, fli, flc, ftc, ftu, gbr, grib, h5, 
# hdf, jp2, j2k, jpc, jpf, jpx, j2c, icns, ico, im, iim, mpg, mpeg, 
# mpo, msp, palm, pcd, pdf, pxr, psd, bw, rgb, rgba, sgi, ras, tga, icb,
# vda, vst, webp, wmf, emf, xbm, xpm.
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

EXTENSION_TO_APP = _FORMAT_FILE_EXTENSIONS_BASE.copy()

IIMAGE_FORMATS = set()
for v in _FORMAT_FILE_EXTENSIONS_BASE.values():
     IIMAGE_FORMATS.add(v)

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
# put jpg after mpo so it overwrites on k:v inversion
FORMAT_UCLIB_APP = {
    'BMP' : 'bmp',
    'JPEG' : 'jpg',
    'MPO' : 'jpg',
    'JPG' : 'jpg',
    'JPEG' : 'jpg',
    'PNG' : 'png',
    'GIF' : 'gif',
    'TIFF' : 'tiff',
    'WEBP' : 'webp',
}

UCLIB_TO_APP = FORMAT_UCLIB_APP

'''
Map of app formats -> uppercase format keys.
This map will work for Pillow and Wand libraries.
'''
# can't be trusted to be generated.
FORMAT_APP_UCLIB  = {
    'bmp' : 'BMP',
    'jpg' : 'JPEG',
    'png' : 'PNG',
    'gif' : 'GIF',
    'tiff' : 'TIFF',
    'webp' : 'WEBP',
}
